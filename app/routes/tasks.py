from flask import request, jsonify, Blueprint
from werkzeug.exceptions import BadRequest, NotFound
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.schema.tasks import bulk_tasks_schema, taskSchema
from app.services.tasks import TaskService
from app.serializers import serizliDict
from http import HTTPStatus

task_bp = Blueprint('task', __name__, url_prefix='/task')


@task_bp.route('', methods=['POST'])
@jwt_required()
def create():
    payload = bulk_tasks_schema(taskSchema).load(
        request.get_json() or {}
    )
    result = TaskService().insert(payload['items'])
    tasks = [serizliDict(dict(k)) for k in result]
    return jsonify({
        "error": False,
        "success": True,
        "data": tasks
    })


@task_bp.route('', defaults={'id': None}, methods=['GET'])
@task_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def getAll(id):
    query = request.args.get('q', '').strip()
    if id is not None:
        result = TaskService().get_id_taks(id)
        return jsonify({
            "error": False,
            "success": True,
            "data": serizliDict(dict(result))
        })
    elif query:
        result = TaskService().get_query(query)
        tasks = [serizliDict(dict(t)) for t in result]
        return jsonify({
            "error": False,
            "success": True,
            "data": tasks
        })
    else:
        result = TaskService().get_all_tasks()
        tasks = [serizliDict(dict(t)) for t in result]
        return jsonify({
            "error": False,
            "success": True,
            "data": tasks
        })


@task_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update(id):
    payload = taskSchema().load(
        request.get_json() or {},
        partial=True
    )
    result = TaskService().update(id, payload)
    return jsonify({
        "error": False,
        "success": True,
        "data": serizliDict(dict(result))
    }), HTTPStatus.OK
