from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from app.database import SessionLocal
from app.models.models import User, Project, ProjectType, ProjectUser, Role
from sqlalchemy.orm import joinedload
from app.clients.redis import redis_client, PROJECT_TTL, USERS_TTL
import json


class ProjectService:
    def init_types_and_roles(self):
        db = SessionLocal()
        try:
            project_types =['pet-project', 'software', 'bugtracking',
                            'devops', 'project managment', 'marketing',
                            'finance', 'science', 'event organization']
            roles = ['observer', 'assignee', 'manager', 'owner']

            for type in project_types:
                type_model = ProjectType(name=type)
                db.add(type_model)
                db.commit()

            for role in roles:
                role_model = Role(name=role)
                db.add(role_model)
                db.commit()
        finally:
            db.close()

    def get_type(self, type_name):
        db = SessionLocal()
        try:
            type_model = db.query(ProjectType).filter(ProjectType.name == type_name).first()
            return type_model.id
        finally:
            db.close()

    def get_role(self, role_name):
        db = SessionLocal()
        try:
            role = db.query(Role).filter(Role.name == role_name).first()
            return role.id
        finally:
            db.close()

    def write_users_to_project(self, project_id, users):
        db = SessionLocal()
        try:
            for user in users:

                role_id = self.get_role(user.role)

                project_user = ProjectUser(
                    user_id=user.id,
                    project_id=project_id,
                    role_id=role_id
                )

                db.add(project_user)
                db.commit()
        finally:
            db.close()

    def create_project(self, name, description, color, img_url, type_project, users):
        db = SessionLocal()
        try:
            type_model = db.query(ProjectType).filter_by(name=type_project).one()

            project = Project(
                name=name,
                description=description,
                color=color,
                img_url=img_url,
                type_id=type_model.id
            )
            db.add(project)
            db.flush()

            for u in users:
                role = db.query(Role).filter_by(name=u.role).one()
                pu = ProjectUser(
                    user_id=u.id,
                    project_id=project.id,
                    role_id=role.id
                )
                db.add(pu)

            db.commit()
            db.refresh(project)

            project_res = {
                "id": str(project.id),
                "name": project.name,
                "description": project.description,
                "color": project.color,
                "img_url": project.img_url,
                "type": type_model.name,
            }

            return project_res
        except:
            db.rollback()
            raise
        finally:
            db.close()

    def get_project(self, project_id):

        cache_key = f"project:{project_id}"
        raw = redis_client.get(cache_key)
        if raw:
            return json.loads(raw)

        db = SessionLocal()
        try:
            project = db.get(Project, project_id)

            if project is None:
                raise ValueError(f"Project ({project_id}) not found")

            project = (
                db.query(Project)
                .options(
                    joinedload(Project.type)
                )
                .get(project.id)
            )

            project_res = {
                "id": str(project.id),
                "name": project.name,
                "description": project.description,
                "color": project.color,
                "img_url": project.img_url,
                "type": project.type.name,
            }

            redis_client.setex(cache_key, PROJECT_TTL, json.dumps(project_res))

            return project_res
        finally:
            db.close()

    def update_project(self, project_id, name, description, color, type_project):
        db = SessionLocal()
        try:
            project = db.get(Project, project_id)

            if project is None:
                raise ValueError(f"Project ({project_id}) not found")

            project.name = name
            project.description = description
            project.color = color

            type_model = db.query(ProjectType).filter_by(name=type_project).one()

            project.type_id = type_model.id

            db.commit()
            db.refresh(project)

            project_res = {
                "id": str(project.id),
                "name": project.name,
                "description": project.description,
                "color": project.color,
                "img_url": project.img_url,
                "type": type_model.name,
            }

            cache_key = f"project:{project_id}"
            redis_client.setex(cache_key, PROJECT_TTL, json.dumps(project_res))

            return project_res
        except:
            db.rollback()
            raise
        finally:
            db.close()

    def update_project_img(self, project_id, img_url):
        db = SessionLocal()
        try:
            project = db.get(Project, project_id)

            if project is None:
                raise ValueError(f"Project ({project_id}) not found")

            project.img_url = img_url

            db.commit()
            db.refresh(project)

            project = (
                db.query(Project)
                .options(
                    joinedload(Project.type)
                )
                .get(project.id)
            )

            project_res = {
                "id": str(project.id),
                "name": project.name,
                "description": project.description,
                "color": project.color,
                "img_url": project.img_url,
                "type": project.type.name,
            }

            cache_key = f"project:{project_id}"
            redis_client.setex(cache_key, PROJECT_TTL, json.dumps(project_res))

            return project_res
        except:
            db.rollback()
            raise
        finally:
            db.close()

    def update_project_users(self, project_id, users):
        db = SessionLocal()
        try:
            project = db.get(Project, project_id)
            if project is None:
                raise ValueError(f"Project ({project_id}) not found")

            db.query(ProjectUser).filter_by(project_id=project_id).delete()

            if not users:
                db.delete(project)
                db.commit()

                redis_client.delete(f"project:{project_id}")
                redis_client.delete(f"project_users:{project_id}")

                return {
                    "project_id": "",
                    "users": []
                }

            for u in users:
                role = db.query(Role).filter_by(name=u["role"]).one()
                pu = ProjectUser(
                    user_id=u["id"],
                    project_id=project.id,
                    role_id=role.id
                )
                db.add(pu)

            db.commit()

            project = (
                db.query(Project)
                .options(
                    joinedload(Project.users).joinedload(ProjectUser.role),
                    joinedload(Project.users).joinedload(ProjectUser.user)
                )
                .get(project.id)
            )
            db.refresh(project)

            payload = {
                "project_id": str(project.id),
                "users": [
                    {
                        "user_id": str(pu.user_id),
                        "role": pu.role.name
                    }
                    for pu in project.users
                ]
            }

            redis_payload = [
                {
                    "user_id": str(pu.user.id),
                    "email": pu.user.email,
                    "name": pu.user.name,
                    "surname": pu.user.surname,
                    "img_url": pu.user.img_url or "",
                    "role": pu.role.name
                }
                for pu in project.users
            ]

            cache_key = f"project_users:{project_id}"
            redis_client.setex(cache_key, USERS_TTL, json.dumps(redis_payload))
            return payload
        except:
            db.rollback()
            raise
        finally:
            db.close()

    def delete_project(self, project_id):
        db = SessionLocal()
        try:
            project = db.get(Project, project_id)

            if project is None:
                raise ValueError(f"Project ({project_id}) not found")

            db.delete(project)
            db.commit()

            redis_client.delete(f"project:{project_id}")
            redis_client.delete(f"project_users:{project_id}")
            redis_client.delete(f"project_tasks:{project_id}")
            redis_client.delete(f"project_epics:{project_id}")
            redis_client.delete(f"project_sprints:{project_id}")

            return True
        except:
            db.rollback()
            raise
        finally:
            db.close()

    def get_project_users(self, project_id):
        cache_key = f"project_users:{project_id}"
        raw = redis_client.get(cache_key)
        if raw:
            return json.loads(raw)

        db = SessionLocal()
        try:
            pu = db.query(ProjectUser).filter(ProjectUser.project_id == project_id).all()

            if not pu:
                return []

            res = []

            for u in pu:
                user = db.get(User, u.user_id)
                role = db.get(Role, u.role_id)
                item = {
                    "user_id": str(user.id),
                    "email": user.email,
                    "name": user.name,
                    "surname": user.surname,
                    "img_url": user.img_url,
                    "role": role.name
                }

                res.append(item)

            redis_client.setex(cache_key, USERS_TTL, json.dumps(res))

            return res
        finally:
            db.close()

    def get_user_projects(self, user_id):
        db = SessionLocal()
        try:
            projects = (
                db.query(Project)
                .join(ProjectUser, Project.id == ProjectUser.project_id)
                .filter(ProjectUser.user_id == user_id)
                .options(joinedload(Project.type))
                .all()
            )

            return [
                {
                    "id": str(p.id),
                    "name": p.name,
                    "description": p.description,
                    "color": p.color,
                    "img_url": p.img_url,
                    "type": p.type.name
                }
                for p in projects
            ]
        finally:
            db.close()

