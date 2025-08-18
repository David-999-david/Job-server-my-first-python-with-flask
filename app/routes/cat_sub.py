from flask import request, jsonify, Blueprint
from app.schema.cat_sub import (
    bulk_items_schema,
    category_schema,
    sub_category_schema,
    ProjectSchema
)
from app.services.cat_sub import (
    category_service, sub_category_service,
    ProjectService
    )
from werkzeug.datastructures import FileStorage
from app.serializers import serizliDict
from app.security.permission import require_permission
from flask_jwt_extended import jwt_required, get_jwt_identity

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


@cat_bp.route('', defaults={"id": None}, methods=['GET'])
@cat_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
@require_permission('worker:read:all')
def get(id):
    query = request.args.get('q', '').strip()
    if id:
        results = category_service().get_id(id)
        categories = [
            serizliDict(dict(r)) for r in results
        ]
        return jsonify({
            "error": False,
            "success": True,
            "data": categories,
            "counts": len(categories)
        })
    elif query:
        results = category_service().get_query(query)
        categories = [
            serizliDict(dict(r)) for r in results
        ]
        return jsonify({
            "error": False,
            "success": True,
            "data": categories,
            "count": len(categories)
        })
    else:
        results = category_service().get()
        categories = [
            serizliDict(dict(r)) for r in results
        ]
        return jsonify({
            "error": False,
            "success": True,
            "data": categories,
            "count": len(categories)
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


@sub_bp.route('', defaults={"id": None}, methods=['GET'])
@sub_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
@require_permission('worker:read:all')
def get_sub(id):
    query = request.args.get('q', '').strip()
    if id:
        results = sub_category_service().get_id(id)
        sub_categories = [
            serizliDict(dict(r)) for r in results
        ]
        return jsonify({
            "error": False,
            "success": True,
            "data": sub_categories,
            "counts": len(sub_categories)
        })
    elif query:
        results = sub_category_service().get_query(query)
        sub_categories = [
            serizliDict(dict(r)) for r in results
        ]
        return jsonify({
            "error": False,
            "success": True,
            "data": sub_categories,
            "count": len(sub_categories)
        })
    else:
        results = sub_category_service().get()
        sub_categories = [
            serizliDict(dict(r)) for r in results
        ]
        return jsonify({
            "error": False,
            "success": True,
            "data": sub_categories,
            "count": len(sub_categories)
        })


project_bp = Blueprint('project', __name__, url_prefix='/project')


@project_bp.route('', methods=['POST'])
@jwt_required()
def insert():
    userId = get_jwt_identity()
    data = {
        "title": request.form.get('title'),
        "description": request.form.get('description'),
        "sub_id": request.form.get('sub_id')
    }
    payload = ProjectSchema().load(data)

    file: FileStorage | None = request.files.get('file')

    if file and file.filename:

        mime = (file.mimetype or '').lower()

        file_data = file.read()

        result = ProjectService().insert_with_image(
            userId, payload, file_data, mime)
        project = serizliDict(dict(result))

    else:
        result = ProjectService().insert(payload)

        project = serizliDict(dict(result))

    return jsonify({
            "error": False,
            "success": True,
            "data": project
    }), 201
