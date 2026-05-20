# app/storage.py
#
# Abstraction du stockage de fichiers.
# - Sans S3_BUCKET : stockage local dans UPLOAD_FOLDER
# - Avec S3_BUCKET  : stockage S3 ou S3-compatible (Cloudflare R2, MinIO, etc.)
#
import os
from loguru import logger
from flask import current_app

_MIME_TYPES = {
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'png': 'image/png',
    'webp': 'image/webp',
}


def _s3_client():
    try:
        import boto3
        return boto3.client(
            's3',
            endpoint_url=current_app.config.get('S3_ENDPOINT_URL'),
            aws_access_key_id=current_app.config.get('S3_ACCESS_KEY'),
            aws_secret_access_key=current_app.config.get('S3_SECRET_KEY'),
            region_name=current_app.config.get('S3_REGION', 'us-east-1'),
        )
    except ImportError:
        logger.warning("boto3 non installé — stockage S3 indisponible, fallback local.")
        return None


def save_file(file_obj, filename: str, folder: str = 'photos') -> str:
    """Sauvegarde un fichier. Retourne le filename."""
    bucket = current_app.config.get('S3_BUCKET')
    if bucket:
        client = _s3_client()
        if client:
            key = f"{folder}/{filename}"
            ext = filename.rsplit('.', 1)[-1].lower()
            content_type = _MIME_TYPES.get(ext, 'application/octet-stream')
            try:
                client.upload_fileobj(
                    file_obj,
                    bucket,
                    key,
                    ExtraArgs={'ContentType': content_type, 'ACL': 'public-read'},
                )
                logger.info("Fichier sauvegardé dans S3 : {}/{}", bucket, key)
                return filename
            except Exception:
                logger.exception("Erreur S3 — fallback stockage local pour {}", filename)

    # Stockage local
    upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], folder)
    os.makedirs(upload_folder, exist_ok=True)
    file_obj.save(os.path.join(upload_folder, filename))
    return filename


def delete_file(filename: str, folder: str = 'photos') -> None:
    """Supprime un fichier de S3 ou du disque local."""
    bucket = current_app.config.get('S3_BUCKET')
    if bucket:
        client = _s3_client()
        if client:
            key = f"{folder}/{filename}"
            try:
                client.delete_object(Bucket=bucket, Key=key)
                logger.info("Fichier supprimé de S3 : {}/{}", bucket, key)
                return
            except Exception:
                logger.exception("Erreur lors de la suppression S3 : {}", key)

    # Stockage local
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], folder, filename)
    if os.path.exists(file_path):
        os.remove(file_path)


def get_file_url(filename: str, folder: str = 'photos') -> str:
    """Retourne l'URL publique d'un fichier."""
    bucket = current_app.config.get('S3_BUCKET')
    if bucket:
        endpoint = current_app.config.get('S3_ENDPOINT_URL')
        if endpoint:
            # Cloudflare R2 ou endpoint S3-compatible
            return f"{endpoint.rstrip('/')}/{folder}/{filename}"
        region = current_app.config.get('S3_REGION', 'us-east-1')
        return f"https://{bucket}.s3.{region}.amazonaws.com/{folder}/{filename}"

    # URL locale
    app_url = current_app.config.get('APP_URL', 'http://localhost:5000')
    return f"{app_url.rstrip('/')}/uploads/{folder}/{filename}"
