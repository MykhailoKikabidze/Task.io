from sqlalchemy.exc import IntegrityError
from sqlalchemy import func, select
from app.database import SessionLocal
from app.models.models import Epic, Task, Project
from datetime import date, datetime
from app.clients.redis import redis_client, EPICS_TTL
import uuid
import json


def _to_uuid_or_none(v):
    if v in (None, "", 0):
        return None
    if isinstance(v, uuid.UUID):
        return v
    return uuid.UUID(str(v))


def _fmt_date(d: date | None) -> str:
    return d.strftime("%d.%m.%Y") if d else ""


def _serialize_epic(e: Epic) -> dict:
    return {
        "id": str(e.id),
        "name": e.name,
        "description": e.description,
        "priority": e.priority,
        "start_date": _fmt_date(e.start_date),
        "end_date": _fmt_date(e.end_date),
        "project_id": str(e.project_id)
    }


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


class EpicService:
    def get_epic(self, id):
        db = SessionLocal()
        try:
            epic = db.get(Epic, id)
            if epic is None:
                raise ValueError(f"Epic ({id}) not found")
            return _serialize_epic(epic)
        finally:
            db.close()

    def get_project_epics(self, project_id):
        cache_key = f"project_epics:{project_id}"
        raw = redis_client.get(cache_key)
        if raw:
            return json.loads(raw)

        db = SessionLocal()
        try:
            epics = db.query(Epic).where(Epic.project_id == project_id).all()

            payload = [_serialize_epic(e) for e in epics]
            redis_client.setex(cache_key, EPICS_TTL, json.dumps(payload))
            return payload
        finally:
            db.close()

    def create_epic(self, name, description, priority, start_date, end_date, project_id, tasks):
        db = SessionLocal()
        try:
            sd = _parse_date(start_date)
            ed = _parse_date(end_date)

            if sd and ed and ed < sd:
                raise ValueError("end_date cannot be earlier than start_date")

            project_id = _to_uuid_or_none(project_id)

            if db.get(Project, project_id) is None:
                raise ValueError(f"Project ({project_id}) not found")

            epic = Epic(
                name=name,
                description=description,
                priority=priority,
                start_date=sd,
                end_date=ed,
                project_id=project_id
            )
            db.add(epic)
            db.flush()

            task_ids = {_to_uuid_or_none(tid) for tid in (tasks or [])}
            task_ids.discard(None)

            if task_ids:
                db_tasks = db.execute(
                    select(Task).where(Task.id.in_(task_ids))
                ).scalars().all()

                for t in db_tasks:
                    if t.project_id == project_id and t.epic_id is None:
                        t.epic_id = epic.id

            db.commit()
            db.refresh(epic)

            redis_client.delete(f"project_epics:{project_id}")
            redis_client.delete(f"epic_tasks:{epic.id}")

            return _serialize_epic(epic)
        finally:
            db.close()

    def update_epic(self, id, name, description, priority, start_date, end_date, project_id, tasks):
        db = SessionLocal()
        try:
            epic = db.get(Epic, id)

            if epic is None:
                raise ValueError(f"Epic ({id}) not found")

            sd = _parse_date(start_date)
            ed = _parse_date(end_date)

            if sd and ed and ed < sd:
                raise ValueError("end_date cannot be earlier than start_date")

            project_id = _to_uuid_or_none(project_id)

            if db.get(Project, project_id) is None:
                raise ValueError(f"Project ({project_id}) not found")

            epic.name = name
            epic.description = description
            epic.priority = priority
            epic.start_date = sd
            epic.end_date = ed
            epic.project_id = project_id

            old_tasks = db.execute(
                select(Task).where(Task.epic_id == epic.id)
            ).scalars().all()

            for t in old_tasks:
                t.epic_id = None

            task_ids = {_to_uuid_or_none(tid) for tid in (tasks or [])}
            task_ids.discard(None)

            if task_ids:
                db_tasks = db.execute(
                    select(Task).where(Task.id.in_(task_ids))
                ).scalars().all()

                for t in db_tasks:
                    if t.project_id == project_id and t.epic_id is None:
                        t.epic_id = epic.id

            db.commit()
            db.refresh(epic)

            redis_client.delete(f"project_epics:{project_id}")
            redis_client.delete(f"epic_tasks:{epic.id}")

            return _serialize_epic(epic)
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def delete_epic(self, id):
        db = SessionLocal()
        try:
            epic = db.get(Epic, id)

            if epic is None:
                raise ValueError(f"Epic ({id}) not found")

            project_id = epic.project_id

            db.delete(epic)
            db.commit()

            redis_client.delete(f"project_epics:{project_id}")
            redis_client.delete(f"epic_tasks:{id}")
            redis_client.delete(f"project_tasks:{project_id}")

            return True
        except:
            db.rollback()
            raise
        finally:
            db.close()
