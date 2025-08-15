from sqlalchemy import text
from app.extensions import db
# from werkzeug.exceptions import BadRequest
from flask import current_app


class category_service():
    insert_sql = text(
        '''insert into category
            (name)
            values (:name)
            on conflict (name) do nothing
            returning *
        '''
    )

    get_sql = text(
        '''select * from category'''
    )

    get_id_sql = text(
        '''select * from category where id =:id'''
    )

    get_query_sql = text(
        '''select * from category where name ilike :query'''
    )

    @staticmethod
    def insert(data: list[dict]) -> list[dict]:
        results = []
        with db.session.begin():
            for item in data:
                result = db.session.execute(
                    category_service.insert_sql,
                    {"name": item.get('name')}
                ).mappings().first()
                if result is None:
                    continue
                results.append(result)
            return results

    @staticmethod
    def get() -> list[dict]:
        with db.session.begin():
            results = db.session.execute(
                category_service.get_sql
            ).mappings().fetchall()
            return results

    @staticmethod
    def get_query(query: str) -> list[dict]:
        with db.session.begin():
            results = db.session.execute(
                category_service.get_query_sql,
                {"query": f'%{query}%'}
            ).mappings().fetchall()
            return results

    @staticmethod
    def get_id(id: int) -> list[dict]:
        with db.session.begin():
            results = db.session.execute(
                category_service.get_id_sql,
                {"id": id}
            ).mappings().fetchall()
            return results


class sub_category_service():
    insert_sql = text(
        '''insert into sub_category
            (category_id,name)
            values
            (:catId, :name)
            on conflict (name) do nothing
            returning *
        '''
    )

    get_sql = text(
        '''select * from sub_category'''
    )

    get_id_sql = text(
        '''select * from sub_category where id =:id'''
    )

    get_query_sql = text(
        '''select * from sub_category where name ilike :query'''
    )

    @staticmethod
    def insert(data: list[dict]) -> list[dict]:
        results = []
        with db.session.begin():
            for d in data:
                result = db.session.execute(
                    sub_category_service.insert_sql,
                    {
                        "catId": d.get('category_id'),
                        "name": d.get('name')
                    }
                ).mappings().first()
                if result is None:
                    current_app.logger.warning(f"on conflict {d.get('name')}")
                    continue
                results.append(result)
            return results

    @staticmethod
    def get() -> list[dict]:
        with db.session.begin():
            results = db.session.execute(
                sub_category_service.get_sql
            ).mappings().fetchall()
            return results

    @staticmethod
    def get_query(query: str) -> list[dict]:
        with db.session.begin():
            results = db.session.execute(
                sub_category_service.get_query_sql,
                {"query": f'%{query}%'}
            ).mappings().fetchall()
            return results

    @staticmethod
    def get_id(id: int) -> list[dict]:
        with db.session.begin():
            results = db.session.execute(
                sub_category_service.get_id_sql,
                {"id": id}
            ).mappings().fetchall()
            return results
