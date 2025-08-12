from flask import request, jsonify, Blueprint
from app.schema.worker_task import worker_task_schema, task_staus_schema
from http import HTTPStatus
from flask_jwt_extended import jwt_required
from app.services.worker_task import worker_task_service
from app.serializers import serizliDict

worker_task_bp = Blueprint('worker_task', __name__, url_prefix='/worker-task')


@worker_task_bp.route('', methods=['POST'])
@jwt_required()
def insert():
    payload = worker_task_schema().load(
        request.get_json() or {}
    )
    result = worker_task_service.insert(
        payload['worker_id'], payload['task_id'])
    return jsonify({
        "error": False,
        "success": True,
        "data": serizliDict(dict(result))
    }), HTTPStatus.CREATED


@worker_task_bp.route('', defaults={"id": None}, methods=['GET'])
@worker_task_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get(id):
    query = request.args.get('q', '').strip()
    if id:
        result = worker_task_service.get_id(id)
        return jsonify({
            "error": False,
            "success": True,
            "data": serizliDict(dict(result))
        })
    if query:
        results = worker_task_service.get_query(query=query)
        dict_result = [serizliDict(dict(r)) for r in results]
        return jsonify({
            "error": False,
            "success": True,
            "data": dict_result,
            "count": len(dict_result)
        })
    else:
        results = worker_task_service.get_all()
        dict_result = [serizliDict(dict(r)) for r in results]
        return jsonify({
            "error": False,
            "success": True,
            "data": dict_result,
            "count": len(dict_result)
        })


@worker_task_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def edit_worker_task_status(id):
    payload = task_staus_schema().load(
        request.get_json() or {}
    )
    result = worker_task_service.edit_worker_task_status(id, payload['status'])
    return jsonify({
        "error": False,
        "success": True,
        "data": serizliDict(dict(result))
    })
