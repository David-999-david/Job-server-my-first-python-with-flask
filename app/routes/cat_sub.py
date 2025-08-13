from flask import request, jsonify, Blueprint
from app.schema.cat_sub import (
    bulk_items_schema,
    category_schema,
    sub_category_schema
)
from app.services.cat_sub import category_service, sub_category_service
from app.serializers import serizliDict
from app.security.permission import require_permission
from flask_jwt_extended import jwt_required

cat_bp = Blueprint('category', __name__, url_prefix='/category')


@cat_bp.route('', methods=['POST'])
@jwt_required()
@require_permission('worker:create:all')
def insert_cat():
    payload = bulk_items_schema(category_schema).load(
        request.get_json() or {}
    )
    results = category_service().insert(payload['items'])
    categories = [
        serizliDict(dict(d)) for d in results
    ]
    return jsonify({
        "error": False,
        "success": True,
        "data": categories
    })


sub_bp = Blueprint('sub_category', __name__, url_prefix='/sub-category')


@sub_bp.route('', methods=['POST'])
def insert_sub():
    payload = bulk_items_schema(sub_category_schema).load(
        request.get_json() or {}
    )
    results = sub_category_service().insert(payload['items'])
    sub_categories = [
        serizliDict(dict(d)) for d in results
    ]
    return jsonify({
        "error": False,
        "success": True,
        "data": sub_categories
    })
