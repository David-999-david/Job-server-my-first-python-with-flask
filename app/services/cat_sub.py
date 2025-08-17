from sqlalchemy import text
from app.extensions import db
from werkzeug.exceptions import BadRequest
from flask import current_app
from app.supabase import supabase_client
import os


class category_service:
    insert_sql = text(
        """insert into category
            (name)
            values (:name)
            on conflict (name) do nothing
            returning *
        """
    )

    get_sql = text("""select * from category""")

    get_id_sql = text("""select * from category where id =:id""")

    get_query_sql = text("""select * from category where name ilike :query""")

    @staticmethod
    def insert(data: list[dict]) -> list[dict]:
        results = []
        with db.session.begin():
            for item in data:
                result = (
                    db.session.execute(
                        category_service.insert_sql, {"name": item.get("name")}
                    )
                    .mappings()
                    .first()
                )
                if result is None:
                    continue
                results.append(result)
            return results

    @staticmethod
    def get() -> list[dict]:
        with db.session.begin():
            results = db.session.execute(
                category_service.get_sql).mappings().fetchall()
            return results

    @staticmethod
    def get_query(query: str) -> list[dict]:
        with db.session.begin():
            results = (
                db.session.execute(
                    category_service.get_query_sql, {"query": f"%{query}%"}
                )
                .mappings()
                .fetchall()
            )
            return results

    @staticmethod
    def get_id(id: int) -> list[dict]:
        with db.session.begin():
            results = (
                db.session.execute(category_service.get_id_sql, {"id": id})
                .mappings()
                .fetchall()
            )
            return results


class sub_category_service:
    insert_sql = text(
        """insert into sub_category
            (category_id,name)
            values
            (:catId, :name)
            on conflict (name) do nothing
            returning *
        """
    )

    get_sql = text("""select * from sub_category""")

    get_id_sql = text("""select * from sub_category where id =:id""")

    get_query_sql = text(
        """select * from sub_category where name ilike :query""")

    @staticmethod
    def insert(data: list[dict]) -> list[dict]:
        results = []
        with db.session.begin():
            for d in data:
                result = (
                    db.session.execute(
                        sub_category_service.insert_sql,
                        {"catId": d.get("category_id"), "name": d.get("name")},
                    )
                    .mappings()
                    .first()
                )
                if result is None:
                    current_app.logger.warning(f"on conflict {d.get('name')}")
                    continue
                results.append(result)
            return results

    @staticmethod
    def get() -> list[dict]:
        with db.session.begin():
            results = (
                db.session.execute(
                    sub_category_service.get_sql).mappings().fetchall()
            )
            return results

    @staticmethod
    def get_query(query: str) -> list[dict]:
        with db.session.begin():
            results = (
                db.session.execute(
                    sub_category_service.get_query_sql, {"query": f"%{query}%"}
                )
                .mappings()
                .fetchall()
            )
            return results

    @staticmethod
    def get_id(id: int) -> list[dict]:
        with db.session.begin():
            results = (
                db.session.execute(sub_category_service.get_id_sql, {"id": id})
                .mappings()
                .fetchall()
            )
            return results


class ProjectService:

    allow_mime = {"image/jpeg", "image/png", "image/webp"}
    ext_for_mime = {
        "image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}

    sb = supabase_client()

    project_insert = text(
        """insert into project
        (title,description)
        values
        (:title,:description)
        returning *
        """
    )

    sub_insert = text(
        """insert into project_sub
        (project_id,sub_id)
        values
        (:projectId,:subId)
        returning *
        """
    )

    project_image = text(
        """update project
        set image_path=:imagePath,
        image_url=:imageUrl
        where id = :projectId
        returning *
        """
    )

    project_sql = text(
        """select * from project
        where id = :projectId
        """
    )

    def upload_project_image(
            self,
            userId: str, projectId: int, file_data: bytes, mime: str
    ) -> tuple[str, str]:
        bulks = os.getenv('SUPABASE_BUCKET')
        ext = self.ext_for_mime.get(mime, "jpg")
        storage_path = f"users/{userId}/projects/{projectId}.{ext}"

        upload = self.sb.storage.from_(bulks).upload(
            storage_path,
            file_data,
            file_options={"content-type": mime, "upsert": "true"}
        )
        err = None
        if hasattr(upload, "error"):
            err = upload.error
        elif isinstance(upload, dict):
            err = upload.get("error")

        if err:
            raise BadRequest(str(err))

        pub = self.sb.storage.from_(bulks).get_public_url(
            storage_path)
        url: str | None = None

        if isinstance(pub, str):
            url = pub
        elif hasattr(pub, "public_url"):
            url = pub.public_url

        return storage_path, url

    def insert(
            self, userId: str, data: dict,
            file_data: bytes, mime: str) -> dict:
        if mime not in self.allow_mime:
            raise ValueError("unsupport mime type")
        if not file_data:
            raise ValueError("empty file")
        if len(file_data) > 5 * 1024 * 1024:
            raise ValueError("file size is too larger than 5 MB")
        with db.session.begin():
            p_res = (
                db.session.execute(
                    self.project_insert,
                    {
                        "title": data.get("title"),
                        "description": data.get("description"),
                    },
                )
                .mappings()
                .first()
            )
            if p_res is None:
                raise BadRequest("Insert into project is failed")
            projectId = p_res["id"]

            s_res = (
                db.session.execute(
                    self.sub_insert,
                    {"projectId": projectId, "subId": data.get("sub_id")},
                )
            )

            if s_res.rowcount != 1:
                raise BadRequest(
                    f"Failed to make join for projectId={projectId}"
                    f"with sub_categoryId={data.get('sub_id')}"
                )

            image_path, image_url = self.upload_project_image(
                userId, projectId, file_data, mime
            )

            i_res = (
                db.session.execute(
                    self.project_image,
                    {"projectId": projectId,
                     "imagePath": image_path,
                     "imageUrl": image_url},
                )
                .mappings()
                .first()
            )

            if not i_res:
                raise BadRequest(
                    f"Insert imageurl to project with id={projectId} Failed"
                )

            result = db.session.execute(
                self.project_sql, {"projectId": projectId}
            ).mappings().first()
            if not result:
                raise BadRequest(
                    f'Could not re-fetch project with id={projectId}'
                )
            return result
