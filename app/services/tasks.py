from app.extensions import db
from sqlalchemy import text
from werkzeug.exceptions import BadRequest, NotFound


class TaskService():

    task_insert = text(
        '''insert into tasks
            (title,description,type)
            values
            (:title,:description,:type)
            returning *
        '''
    )

    @staticmethod
    def insert(items: list[dict]) -> tuple[dict]:
        result = []
        with db.session.begin():
            for item in items:
                need = {
                    "title": item['title'],
                    "description": item["description"],
                    "type": item["type"]
                }
                res = db.session.execute(
                    TaskService.task_insert,
                    need
                )
                if res.rowcount != 1:
                    raise BadRequest("Create")
                result.append(res.mappings().first())
            return result

    get_sql = text(
        '''select *
           from tasks
        '''
    )

    @staticmethod
    def get_all_tasks() -> list[dict]:
        with db.session.begin():
            result = db.session.execute(
                TaskService.get_sql
            )
            return result.mappings().fetchall()

    get_id_sql = text(
        '''select * from tasks
            where id = :id
        '''
    )

    @staticmethod
    def get_id_taks(id: int) -> dict:
        with db.session.begin():
            result = db.session.execute(TaskService.get_id_sql,
                                        {"id": id})
            if result.rowcount != 1:
                raise NotFound(f'Can\'t find task with id={id}')
            return result.mappings().first()

    query_sql = text(
        '''select * from tasks
            where title ilike :query or
             description ilike :query or
            (type::text) ilike :query
        '''
    )

    @staticmethod
    def get_query(query: str) -> list[dict]:
        with db.session.begin():
            result = db.session.execute(
                TaskService.query_sql,
                {"query": f'%{query}%'}
            )

            return result.mappings().fetchall()

    update_sql = text(
        '''insert into tasks
            (id,title,description, type)
            values
            (:id,:title,:description, :type)
            on conflict (id)
            do update set
            title = coalesce(excluded.title, tasks.title),
            description = coalesce(excluded.description, tasks.description),
            type = coalesce(excluded.type, tasks.type),
            updated_at = now()
            returning *
        '''
    )

    check_task = text(
        '''select 1 from tasks
            where id=:id
        '''
    )

    @staticmethod
    def update(id: int, data: dict) -> dict:
        with db.session.begin():
            check = db.session.execute(
                TaskService.check_task,
                {"id": id}
            ).scalar()
            if not check:
                raise NotFound(f'Canot found taks with id={id}')
            need = {
                "id": id,
                "title": data.get('title'),
                "description": data.get('description'),
                "type": data.get('type')
            }
            result = db.session.execute(
                TaskService.update_sql,
                need
            )
            return result.mappings().first()
    delete_sql = text(
        '''delete from tasks
           where id=any(:ids)
        '''
    )

    @staticmethod
    def delete_many(ids: list[int]) -> int:
        with db.session.begin():
            res = db.session.execute(
                TaskService.delete_sql,
                {"ids": ids}
            )
            if res.rowcount == 0:
                return BadRequest('There is no row for delete')
            rowcount = res.rowcount
            return rowcount
