from flask import request, jsonify, Blueprint, current_app
from app.schema.address_salary import AddressSalarySchema
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError, DatabaseError
from app.services.address_salary_service import AddressSalaryService
from app.serializers import serizliDict

addr_sal_bp = Blueprint("addr_sala", __name__, url_prefix='/jobs')


@addr_sal_bp.route('/adre&sal', methods=['POST'])
def create():
    schema = AddressSalarySchema()

    try:
        payload = schema.load(request.get_json() or {})
    except ValidationError as e:
        current_app.logger.error(e)
        return jsonify({
            "error": True,
            "message": e.messages
        }), 400

    try:
        add_res, sal_res = AddressSalaryService().create(payload)
    except IntegrityError as e:
        return jsonify({
            "error": "Integrity Error when create in address and salary ",
            "detial": str(e.orig)
        }), 400
    except DatabaseError as e:
        current_app.logger.error(e)
        return jsonify({
            "error": "Database Error when create in address and salary ",
            "detail": str(e.orig)
        }), 500

    return jsonify({
        "error": False,
        "success": True,
        "data": {
            "newAddress": {
                "id": add_res["id"],
                "job_id": add_res['job_id'],
                "street": add_res['street'],
                "city": add_res['city'],
                "country": add_res['country']
            },
            "newSalary": {
                "id": sal_res['id'],
                "address_id": sal_res['address_id'],
                "amount": sal_res['amount'],
                "created_at": sal_res['created_at'].isoformat()
            }
        }
    }), 201


@addr_sal_bp.route('/adre&sal', defaults={'jobId': None}, methods=['GET'])
@addr_sal_bp.route('/<int:jobId>/adre&sal', methods=['GET'])
def getAll(jobId):
    query = request.args.get('q', '').strip()

    try:
        if jobId is not None:
            results = AddressSalaryService().getById(jobId=jobId)
        elif query:
            results = AddressSalaryService().search(query=query)
        else:
            results = AddressSalaryService().getAll()
    except IntegrityError as e:
        return jsonify({
            "error": "Integrity Error when get all from "
            "job with address and salary",
            "detail": str(e.orig)
        })
    except DatabaseError as e:
        current_app.logger.error(e)
        return jsonify({
            "error": "Database Error when get all from"
            " job with address and salary",
            "detail": str(e.orig)
        })

    if jobId is None:
        jobs = []

        for item in results:
            jobs.append(serizliDict(item=dict(item)))

        return jsonify({
                "error": False,
                "success": True,
                "data": jobs,
                "total": len(jobs)
                })
    else:
        return jsonify({
            "error": False,
            "success": True,
            "data": dict(results),
            "total": len(dict(results))
        })


@addr_sal_bp.route('/adre&sal/<int:addressId>/<int:salaryId>/',
                   methods=['PUT'])
def update(addressId, salaryId):

    schema = AddressSalarySchema()

    try:
        payload = schema.load(request.get_json() or {}, partial=True)
    except ValidationError as e:
        return jsonify({
            "error": "Schema error when update address and salary",
            "message": e.messages
        }), 400

    try:
        add_res, sal_res = AddressSalaryService().update(
            addressId=addressId,
            salaryId=salaryId,
            data=payload
            )
    except LookupError as e:
        current_app.logger.error(e)
        return jsonify({
            "error": "Not Found!",
            "detail": str(e)
        }), 404
    except IntegrityError as e:
        current_app.logger.error(e._message)
        return jsonify({
            "error": "Integrity when update in address salary",
            "detail": str(e.orig)
        }), 400
    except DatabaseError as e:
        current_app.logger.error(e)
        return jsonify({
            "error": "Database Error when update in address salary",
            "detail": str(e.orig)
        }), 500

    updatedAddress = serizliDict(dict(add_res))
    updatedSalary = serizliDict(dict(sal_res))

    return jsonify({
        "error": False,
        "success": True,
        "data": {
            "updatedAddress": updatedAddress,
            "updatedSalary": updatedSalary
        }
    }), 203
