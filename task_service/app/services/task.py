from app.database import SessionLocal
from app.models.models import Task, Status, TaskType
from sqlalchemy.orm import joinedload
from sqlalchemy import select
from datetime import date, datetime
from app.clients.redis import redis_client, TASKS_TTL
import json
import uuid


def _to_uuid_or_none(v):
    if v in (None, "", 0):
        return None
    if isinstance(v, uuid.UUID):
        return v
    return uuid.UUID(str(v))


def _fmt_date(d: date | None) -> str:
    return d.strftime("%d.%m.%Y") if d else ""


def _parse_date(v) -> date | None:
    if not v:
        return None
    if isinstance(v, date):
        return v
    v = str(v).strip()
    for fmt in ("%d.%m.%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(v, fmt).date()
        except ValueError:
            pass
    raise ValueError(f"Incorrect date format: {v}. Waiting for dd.mm.yyyy")


def _serialize_task(t: Task) -> dict:
    return {
        "id": str(t.id),
        "title": t.title,
        "description": t.description,
        "priority": t.priority,
        "type": t.type.name if getattr(t, "type", None) else "",
        "status": t.status.name if getattr(t, "status", None) else "",
        "assigned_to": str(t.assigned_to) if t.assigned_to else "",
        "epic_id": str(t.epic_id) if t.epic_id else "",
        "sprint_id": str(t.sprint_id) if t.sprint_id else "",
        "project_id": str(t.project_id),
        "start_date": _fmt_date(t.start_date),
        "end_date": _fmt_date(t.end_date),
    }


class TaskService:
    def init_statuses_types(self):
        db = SessionLocal()
        try:
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

    def get_task(self, task_id):
        db = SessionLocal()
        try:
            stmt = (
                select(Task)
                .options(
                    joinedload(Task.status),
                    joinedload(Task.type),
                )
                .where(Task.id == task_id)
            )
            task = db.scalars(stmt).first()
            if task is None:
                raise ValueError(f"Task ({task_id}) not found")
            return _serialize_task(task)
        finally:
            db.close()

    def get_project_tasks(self, project_id):
        cache_key = f"project_tasks:{project_id}"
        raw = redis_client.get(cache_key)
        if raw:
            return json.loads(raw)

        db = SessionLocal()
        try:
            stmt = (
                select(Task)
                .options(
                    joinedload(Task.status),
                    joinedload(Task.type),
                )
                .where(Task.project_id == project_id)
            )
            tasks = db.scalars(stmt).all()

            payload = [_serialize_task(t) for t in tasks]
            redis_client.setex(cache_key, TASKS_TTL, json.dumps(payload))
            return payload
        finally:
            db.close()

    def get_sprint_tasks(self, sprint_id):
        cache_key = f"sprint_tasks:{sprint_id}"
        raw = redis_client.get(cache_key)
        if raw:
            return json.loads(raw)

        db = SessionLocal()
        try:
            stmt = (
                select(Task)
                .options(
                    joinedload(Task.status),
                    joinedload(Task.type),
                )
                .where(Task.sprint_id == sprint_id)
            )
            tasks = db.scalars(stmt).all()

            payload = [_serialize_task(t) for t in tasks]
            redis_client.setex(cache_key, TASKS_TTL, json.dumps(payload))
            return payload
        finally:
            db.close()

    def get_epic_tasks(self, epic_id):
        cache_key = f"epic_tasks:{epic_id}"
        raw = redis_client.get(cache_key)
        if raw:
            return json.loads(raw)

        db = SessionLocal()
        try:
            stmt = (
                select(Task)
                .options(
                    joinedload(Task.status),
                    joinedload(Task.type),
                )
                .where(Task.epic_id == epic_id)
            )
            tasks = db.scalars(stmt).all()

            payload = [_serialize_task(t) for t in tasks]
            redis_client.setex(cache_key, TASKS_TTL, json.dumps(payload))
            return payload
        finally:
            db.close()

    def create_task(
        self,
        title,
        description,
        priority,
        type,
        assigned_to,
        epic_id,
        sprint_id,
        project_id,
        start_date,
        end_date,
    ):
        db = SessionLocal()
        try:
            type_model = db.query(TaskType).filter_by(name=type).one()
            status_model = db.query(Status).filter_by(name="to do").one()

            sd = _parse_date(start_date)
            ed = _parse_date(end_date)

            if sd and ed and ed < sd:
                raise ValueError("end_date cannot be earlier than start_date")

            task = Task(
                title=title,
                description=description,
                priority=priority,
                type_id=type_model.id,
                status_id=_to_uuid_or_none(status_model.id),
                assigned_to=_to_uuid_or_none(assigned_to),
                epic_id=_to_uuid_or_none(epic_id),
                sprint_id=_to_uuid_or_none(sprint_id),
                project_id=project_id,
                start_date=sd,
                end_date=ed,
            )

            db.add(task)
            db.commit()
            db.refresh(task)

            stmt = (
                select(Task)
                .options(
                    joinedload(Task.status),
                    joinedload(Task.type),
                )
                .where(Task.id == task.id)
            )
            task = db.scalars(stmt).first()

            redis_client.delete(f"project_tasks:{task.project_id}")
            if task.sprint_id:
                redis_client.delete(f"sprint_tasks:{task.sprint_id}")
            if task.epic_id:
                redis_client.delete(f"epic_tasks:{task.epic_id}")

            return _serialize_task(task)
        finally:
            db.close()

    def update_task(
        self,
        id,
        title,
        description,
        priority,
        type,
        status,
        assigned_to,
        epic_id,
        sprint_id,
        project_id,
        start_date,
        end_date,
    ):
        db = SessionLocal()
        try:
            task = db.get(Task, id)
            if task is None:
                raise ValueError(f"Task ({id}) not found")

            old_sprint_id = task.sprint_id
            old_epic_id = task.epic_id

            task.title = title
            task.description = description
            task.priority = priority

            type_model = db.query(TaskType).filter_by(name=type).one()
            task.type_id = type_model.id

            status_model = db.query(Status).filter_by(name=status).one()
            task.status_id = status_model.id

            task.assigned_to = _to_uuid_or_none(assigned_to)
            task.epic_id = _to_uuid_or_none(epic_id)
            task.sprint_id = _to_uuid_or_none(sprint_id)
            task.project_id = _to_uuid_or_none(project_id)

            task.start_date = _parse_date(start_date)
            if task.start_date and task.end_date and task.end_date < task.start_date:
                raise ValueError("end_date cannot be earlier than start_date")

            if status == "done" and date.today() < task.start_date:
                task.start_date = date.today()
                task.end_date = date.today()
            elif status == "done":
                task.end_date = date.today()
            else:
                task.end_date = _parse_date(end_date)



            db.commit()

            stmt = (
                select(Task)
                .options(
                    joinedload(Task.status),
                    joinedload(Task.type),
                )
                .where(Task.id == task.id)
            )
            task = db.scalars(stmt).first()

            redis_client.delete(f"project_tasks:{task.project_id}")

            if old_sprint_id:
                redis_client.delete(f"sprint_tasks:{old_sprint_id}")
            if task.sprint_id:
                redis_client.delete(f"sprint_tasks:{task.sprint_id}")

            if old_epic_id:
                redis_client.delete(f"epic_tasks:{old_epic_id}")
            if task.epic_id:
                redis_client.delete(f"epic_tasks:{task.epic_id}")

            return _serialize_task(task)
        finally:
            db.close()

    def delete_task(self, task_id):
        db = SessionLocal()
        try:
            task = db.get(Task, task_id)

            if task is None:
                raise ValueError(f"Task ({task_id}) not found")

            project_id = task.project_id
            sprint_id = task.sprint_id
            epic_id = task.epic_id

            db.delete(task)
            db.commit()

            redis_client.delete(f"project_tasks:{project_id}")
            if sprint_id:
                redis_client.delete(f"sprint_tasks:{sprint_id}")
            if epic_id:
                redis_client.delete(f"epic_tasks:{epic_id}")

            return True
        except:
            db.rollback()
            raise
        finally:
            db.close()
