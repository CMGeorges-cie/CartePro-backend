from __future__ import annotations

import os

from flask import current_app, jsonify, render_template, request
from loguru import logger
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from werkzeug.exceptions import HTTPException

from .extensions import db


class APIError(Exception):
    """Application error with an explicit HTTP status code."""

    def __init__(self, message: str, status_code: int = 400, payload: dict | None = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.payload = payload or {}


def wants_json_response() -> bool:
    path = request.path or ""
    accept = request.accept_mimetypes
    return (
        request.is_json
        or path.startswith("/api/")
        or path.startswith("/auth/")
        or accept["application/json"] >= accept["text/html"]
    )


def json_error(message: str, status_code: int, **extra):
    payload = {"error": message}
    if extra:
        payload.update(extra)
    return jsonify(payload), status_code


def commit_session(error_message: str = "Database operation failed."):
    try:
        db.session.commit()
    except IntegrityError as exc:
        db.session.rollback()
        logger.warning("Integrity error during database commit: {}", exc)
        raise APIError(error_message, 409) from exc
    except SQLAlchemyError as exc:
        db.session.rollback()
        logger.exception("Database error during commit")
        raise APIError("Internal database error.", 500) from exc


def get_or_404(model, entity_id):
    entity = db.session.get(model, entity_id)
    if entity is None:
        raise APIError("Resource not found.", 404)
    return entity


def register_error_handlers(app):
    @app.errorhandler(APIError)
    def handle_api_error(error: APIError):
        return json_error(error.message, error.status_code, **error.payload)

    @app.errorhandler(HTTPException)
    def handle_http_exception(error: HTTPException):
        message = error.description or error.name
        if wants_json_response():
            return json_error(message, error.code or 500)
        template_name = os.path.join("errors", f"{error.code}.html")
        if os.path.exists(os.path.join(current_app.template_folder, template_name)):
            return render_template(template_name), error.code
        return render_template("errors/500.html"), error.code

    @app.errorhandler(IntegrityError)
    def handle_integrity_error(error: IntegrityError):
        db.session.rollback()
        logger.warning("Unhandled integrity error: {}", error)
        return json_error("Database constraint violation.", 409)

    @app.errorhandler(SQLAlchemyError)
    def handle_sqlalchemy_error(error: SQLAlchemyError):
        db.session.rollback()
        logger.exception("Unhandled database error")
        if wants_json_response():
            return json_error("Internal database error.", 500)
        return render_template("errors/500.html"), 500

    @app.errorhandler(Exception)
    def handle_unexpected_error(error: Exception):
        logger.exception("Unhandled application error")
        if wants_json_response():
            return json_error("Internal server error.", 500)
        return render_template("errors/500.html"), 500
