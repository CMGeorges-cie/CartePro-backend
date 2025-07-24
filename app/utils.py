from flask import request

def paginate_query(query, serializer=lambda x: x.serialize() if hasattr(x, 'serialize') else x, default_per_page=10):
    """Paginate a SQLAlchemy query based on request args."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', default_per_page, type=int)
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return {
        'items': [serializer(item) for item in pagination.items],
        'page': page,
        'per_page': per_page,
        'total': pagination.total
    }

def paginate_list(items, serializer=lambda x: x, default_per_page=10):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', default_per_page, type=int)
    total = len(items)
    start = (page - 1) * per_page
    end = start + per_page
    return {
        'items': [serializer(item) for item in items[start:end]],
        'page': page,
        'per_page': per_page,
        'total': total
    }
