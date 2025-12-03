from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from app.database import SessionLocal
from app.models.models import User, ProjectType, Role, TaskType, Status
from passlib.context import CryptContext
import os

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

JWT_REFRESH_SECRET = os.getenv("JWT_REFRESH_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
REFRESH_EXPIRE_SECONDS = os.getenv("REFRESH_TOKEN_EXPIRE", 86400)


class AuthService:
    def create_user(self, name, surname, email, password, img_url=None):
        db = SessionLocal()
        try:
            hashed_password = pwd_context.hash(password)
            user = User(
                name=name,
                surname=surname,
                email=email,
                password=hashed_password,
                img_url=img_url
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            return user
        except IntegrityError:
            db.rollback()
            return None
        finally:
            db.close()

    def login_user(self, email, password):
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.email == email).first()
            if user and pwd_context.verify(password, user.password):
                return user
            return None
        finally:
            db.close()

    def get_user_by_id(self, user_id):
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            return user
        finally:
            db.close()

    def get_user_by_email(self, email):
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.email == email).first()
            return user
        finally:
            db.close()

    def update_user(self, name, surname, email, password):
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.email == email).first()
            if not user:
                return None

            hashed_password = pwd_context.hash(password)

            user.name = name
            user.surname = surname
            user.password = hashed_password

            db.commit()
            db.refresh(user)
            return user
        finally:
            db.close()

    def update_user_img_url(self, email, img_url):
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.email == email).first()
            if not user:
                return None

            user.img_url = img_url

            db.commit()
            db.refresh(user)
            return user
        finally:
            db.close()

    def delete_user(self, email):
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.email == email).first()
            if not user:
                return None

            db.delete(user)
            db.commit()
            return True
        finally:
            db.close()

    def search_users(self, substr):
        db = SessionLocal()
        try:
            pattern = f"%{substr}%"
            full_name = func.concat(User.name, ' ', User.surname)
            q = db.query(User).filter(full_name.ilike(pattern)).limit(20)
            return q.all()
        finally:
            db.close()

    def init_db(self):
        db = SessionLocal()
        try:
            project_types = ['pet-project', 'software', 'bugtracking',
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

            statuses = ["to do", "in progress", "done"]

            types = [
                "design",
                "bug",
                "feature",
                "docs",
                "refactor",
                "improvement",
                "user story",
            ]

            for status in statuses:
                status_model = Status(name=status)
                db.add(status_model)
                db.commit()

            for type_item in types:
                type_model = TaskType(name=type_item)
                db.add(type_model)
                db.commit()
        finally:
            db.close()

