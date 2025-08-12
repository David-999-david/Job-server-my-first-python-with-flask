from app.extensions import db
from werkzeug.exceptions import NotFound, BadRequest
from sqlalchemy import text
from flask import current_app


class worker_task_service:
    insert_sql = text(
        '''insert into worker_task
            (worker_id,task_id)
            values
            (:workerId,:taskId)
            returning *
        '''
    )

    worker_sql = text(
        '''select 1 from workers
            where id=:id
        '''
    )
    task_sql = text(
        '''select 1 from tasks
            where id=:id
        '''
    )

    @staticmethod
    def insert(wokerId: int, taskId: int) -> dict:
        with db.session.begin():
            worker_check = db.session.execute(
                worker_task_service.worker_sql,
                {"id": wokerId}
            )
            if worker_check.rowcount != 1:
                raise NotFound("Worker not found")
            task_check = db.session.execute(
                worker_task_service.task_sql,
                {"id": taskId}
            )
            if task_check.rowcount != 1:
                raise NotFound("Task not found")
            res = db.session.execute(
                worker_task_service.insert_sql,
                {
                    "workerId": wokerId,
                    "taskId": taskId
                }
            )
            row = res.mappings().first()
            if row is None:
                raise BadRequest('Failed to insert join for worker with task')
            return row
    get_sql = text(
        '''select * from worker_task'''
    )
    get_id_sql = text(
        '''select * from worker_task
            where id=:id
        '''
    )
    get_query_sql = text(
        '''select * from worker_task
            where (status::text) ilike :query
        '''
    )

    @staticmethod
    def get_all() -> list[dict]:
        with db.session.begin():
            result = db.session.execute(worker_task_service.get_sql)
            if result is None:
                raise NotFound("There is no result for get"
                               " all worker with task")
            return result.mappings().fetchall()

    @staticmethod
    def get_query(query: str) -> list[dict]:
        with db.session.begin():
            result = db.session.execute(
                worker_task_service.get_query_sql,
                {"query": f'%{query}%'}
            )
            if result is None:
                raise NotFound("There is no result for get"
                               "all worker with task"
                               f"by search {query}")
            return result.mappings().fetchall()

    @staticmethod
    def get_id(id: int) -> dict:
        with db.session.begin():
            result = db.session.execute(
                worker_task_service.get_id_sql,
                {"id": id}
            )
            if result.rowcount != 1:
                raise NotFound(f"There is no work with task row by id={id}")
            return result.mappings().first()
    pending_sql = text(
        '''update worker_task
            set status = :status
            where id=:id
            returning *
        '''
    )
    processing_sql = text(
        '''update worker_task
            set status = :status,
            start_time = coalesce(start_time, now())
            where id=:id
            returning *
        '''
    )
    completed_sql = text(
        '''update worker_task
            set status = :status,
            end_time = now()
            where id=:id
            returning *
        '''
    )
    canceled_sql = text(
        '''update worker_task
            set status = :status,
            canceled_time = now()
            where id=:id
            returning *
        '''
    )

    @staticmethod
    def edit_worker_task_status(id: int, status: str) -> dict:
        need = {"id": id, "status": status}
        current_app.logger.info(f'need => {need}')
        with db.session.begin():
            if status == 'pending':
                result = db.session.execute(
                    worker_task_service.pending_sql, need
                )
            elif status == 'processing':
                result = db.session.execute(
                    worker_task_service.processing_sql, need
                )
            elif status == 'completed':
                result = db.session.execute(
                    worker_task_service.completed_sql, need
                )
            elif status == 'canceled':
                result = db.session.execute(
                    worker_task_service.canceled_sql, need
                )
            row = result.mappings().first()
            if row is None:
                raise NotFound(f'worker_task with id={id} not found')
            return row
