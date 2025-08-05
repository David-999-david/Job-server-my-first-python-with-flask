from flask import request, jsonify, Blueprint, current_app
from sqlalchemy import text
from sqlalchemy.exc import DatabaseError, IntegrityError
from app.extensions import db

job_bp = Blueprint('job', __name__, url_prefix="/jobs")


@job_bp.route('/', methods=['POST'])
def create():
    data = request.get_json()
    name = data.get('name')

    if not name:
        return jsonify({
            "error": "Name is required"
        }), 400

    sql = text(
        """
    insert into job (name)
    values (:name)
    returning *
"""
    )

    try:
        result = db.session.execute(sql, {"name": name})
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({
            'error': "IntergrityError",
            'detail': str(e.orig)
        }), 400
    except DatabaseError as e:
        db.session.rollback()
        current_app.logger.error(f"DB error on insert: {e}")
        return jsonify({
            'error': 'Database Error',
            'detail': str(e.orig)
        }), 500
    row = result.mappings().first()
    newJob = {
        "id": row["id"],
        "name": row["name"],
        "called_at": row["called_at"].isoformat()
    }
    return jsonify({
        "message": "Successfully add Job",
        "data": newJob
        }), 201


@job_bp.route('/', methods=['GET'])
def getAllJob():

    q = request.args.get('q', '').strip()

    if q:
        sql = text("""
select id,name,called_at,updated_at
    from job where name ilike :querry
""")
        pattern = {"querry": f"%{q}%"}
    else:
        sql = text("""
    select id,name,called_at,updated_at
    from job
""")
        pattern = {}

    try:
        rows = db.session.execute(sql, pattern)
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({
            "error": 'Integrity when get all job',
            "detail": f"{str(e.orig)}"
        }), 400
    except DatabaseError as e:
        db.session.rollback()
        current_app.logger.error(f"Error when get all job, {e}")
        return jsonify({
            "error": "Database error",
            "detail": str(e.orig)
        }), 500
    # jobs = [dict(row) for row in rows.mappings().fetchall()]
    jobs = []
    for job in rows.mappings().all():
        jobs.append({
            "id": job['id'],
            "name": job['name'],
            "called_at": job["called_at"].isoformat()
        })

    return jsonify({
        "error": False,
        "success": True,
        "data": jobs
    }), 200


@job_bp.route('/<int:id>', methods=['GET'])
def getJobById(id):

    sql = text(
        """
    select id,name,called_at,updated_at
    from job
    where id=:id
"""
    )

    try:
        job = db.session.execute(sql, {'id': id})

        if not job:
            return jsonify({'error': "Job not found"}), 404

        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({
            "error": "Integrity when get job by id",
            "detail": str(e.orig)
        }), 400
    except DatabaseError as e:
        db.session.rollback()
        current_app.logger.error(f"Database error : {e}")
        return jsonify({
            "error": "Database error",
            "detail": str(e.orig)
        }), 500
    return jsonify(
        {
            "error": False,
            "success": True,
            "data": dict(job.mappings().first())
        }
        ), 200


@job_bp.route('/search', methods=['GET'])
def searchByQuery():

    query = request.args.get('q', '').strip()

    if not query:
        return jsonify({'data': [], 'message': "No query"}), 200

    sql = text(
        """
    select id,name,called_at,updated_at
    from job
    where name ilike :query
"""
    )

    try:
        searchJrowobs = db.session.execute(sql, {"query": f"%{query}%"})
        db.session.commit()

    except IntegrityError as e:
        db.session.rollback()
        return jsonify({
            "error": "Integrity when search job",
            "detail": str(e.orig)
        })
    except DatabaseError as e:
        db.session.rollback()
        current_app.logger.error(f"Error when seach by query for job : {e}")
        return jsonify({
            "error": "Error when search by query for job",
            "detail": str(e.orig)
        })

    # rows = searchJrowobs.mappings().fetchall()

    # if not rows:
    #     return jsonify({"error": "There is no job result"}), 404

    items = [dict(row) for row in searchJrowobs.mappings().fetchall()]

    return jsonify({
        'error': False,
        'success': True,
        "data": items
    }), 200


@job_bp.route('/<int:id>', methods=['PUT'])
def editJob(id):
    data = request.get_json()
    updateName = data.get('name')

    sql = text(
        """
    update job
    set name=:name,
    updated_at = now()
    where id=:id
    returning id,name,called_at,updated_at
"""
    )
    try:
        updatedJob = db.session.execute(
            sql, {"id": id, "name": updateName}
        )
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        current_app.logger.error(f"Intefrity Error : {e}")
        return jsonify({
            'error': "Ingegrity when update job",
            'detail': str(e.orig)
        }), 400
    except DatabaseError as e:
        db.session.rollback()
        current_app.logger.error(f"Database Error : {e}")
        return jsonify({
            'error': "Database Error",
            'detail': str(e.orig)
        }), 500

    if not updatedJob:
        return jsonify({"error": "Failed to update job"}), 400

    returnJob = updatedJob.mappings().first()

    job = {
        "id": returnJob["id"],
        "name": returnJob["name"],
        "called_at": returnJob["called_at"].isoformat(),
        "updated_at": returnJob["updated_at"].isoformat()
    }

    return jsonify({
        "error": False,
        "success": True,
        "data": job
    }), 200


@job_bp.route('/<int:id>', methods=['DELETE'])
def deleteOneJob(id):

    sql = text(
        '''
    delete from job
    where id=:id
'''
    )

    try:
        result = db.session.execute(sql, {"id": id})
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify({
            'error': f'Integrity error when delet job with id={id}',
            'detail': str(e.orig)
        }), 400
    except DatabaseError as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify({
            'error': f'Database error when delet job with id={id}',
            'detail': str(e.orig)
        }), 500

    rowCount = result.rowcount

    if rowCount == 0:
        return jsonify({
            "error": "Nothing delete for job"
        }), 404

    return jsonify({
        "error": False,
        "success": True,
        "data": f"Successfully delete job with id={id}"
    }), 204
