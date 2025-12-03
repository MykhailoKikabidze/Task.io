from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from app.database import SessionLocal
from app.models.models import Sprint, Task, Project
from datetime import date, datetime
from app.clients.redis import redis_client, SPRINTS_TTL
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


def _serialize_sprint(s: Sprint) -> dict:
    return {
        "id": str(s.id),
        "name": s.name,
        "description": s.description,
        "start_date": _fmt_date(s.start_date),
        "end_date": _fmt_date(s.end_date),
        "is_started": s.is_started,
        "project_id": str(s.project_id)
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


class SprintService:
    def get_sprint(self, id):
        db = SessionLocal()
        try:
            sprint = db.get(Sprint, id)
            if sprint is None:
                raise ValueError(f"Sprint ({id}) not found")
            return _serialize_sprint(sprint)
        finally:
            db.close()

    def get_project_sprints(self, project_id):
        cache_key = f"project_sprints:{project_id}"
        raw = redis_client.get(cache_key)
        if raw:
            return json.loads(raw)

        db = SessionLocal()
        try:
            sprints = db.query(Sprint).where(Sprint.project_id == project_id).all()

            payload = [_serialize_sprint(s) for s in sprints]
            redis_client.setex(cache_key, SPRINTS_TTL, json.dumps(payload))
            return payload
        finally:
            db.close()

    def create_sprint(self, name, description, start_date, end_date, is_started, project_id, tasks):
        db = SessionLocal()
        try:
            sd = _parse_date(start_date)
            ed = _parse_date(end_date)

            if sd and ed and ed < sd:
                raise ValueError("end_date cannot be earlier than start_date")

            project_id = _to_uuid_or_none(project_id)

            if db.get(Project, project_id) is None:
                raise ValueError(f"Project ({project_id}) not found")

            sprint = Sprint(
                name=name,
                description=description,
                start_date=sd,
                end_date=ed,
                is_started=is_started,
                project_id=project_id
            )
            db.add(sprint)
            db.flush()

            task_ids = {_to_uuid_or_none(tid) for tid in (tasks or [])}
            task_ids.discard(None)

            if task_ids:
                db_tasks = db.execute(
                    select(Task).where(Task.id.in_(task_ids))
                ).scalars().all()

                for t in db_tasks:
                    if t.project_id == project_id and t.sprint_id is None:
                        t.sprint_id = sprint.id

            db.commit()
            db.refresh(sprint)

            redis_client.delete(f"project_sprints:{project_id}")
            redis_client.delete(f"sprint_tasks:{sprint.id}")

            return _serialize_sprint(sprint)
        finally:
            db.close()

    def update_sprint(self, id, name, description, start_date, end_date, is_started, project_id, tasks):
        db = SessionLocal()
        try:
            sprint = db.get(Sprint, id)

            if sprint is None:
                raise ValueError(f"Sprint ({id}) not found")

            sd = _parse_date(start_date)
            ed = _parse_date(end_date)

            if sd and ed and ed < sd:
                raise ValueError("end_date cannot be earlier than start_date")

            project_id = _to_uuid_or_none(project_id)

            if db.get(Project, project_id) is None:
                raise ValueError(f"Project ({project_id}) not found")

            if bool(is_started):

                if not bool(end_date):
                    raise ValueError(f"Cannot start sprint ({id}). End date is required")

                running_exists = db.execute(
                    select(Sprint.id).where(
                        Sprint.project_id == project_id,
                        Sprint.is_started.is_(True),
                        Sprint.id != sprint.id,
                    ).limit(1)
                ).scalar_one_or_none()
                if running_exists is not None:
                    raise ValueError(
                        f"Cannot start sprint ({id}). Running sprint already exists in project ({project_id})"
                    )

            sprint.name = name
            sprint.description = description
            sprint.start_date = sd
            sprint.end_date = ed
            sprint.is_started = is_started
            sprint.project_id = project_id

            old_tasks = db.execute(
                select(Task).where(Task.sprint_id == sprint.id)
            ).scalars().all()

            for t in old_tasks:
                t.sprint_id = None

            task_ids = {_to_uuid_or_none(tid) for tid in (tasks or [])}
            task_ids.discard(None)

            if task_ids:
                db_tasks = db.execute(
                    select(Task).where(Task.id.in_(task_ids))
                ).scalars().all()

                for t in db_tasks:
                    if t.project_id == project_id and t.sprint_id is None:
                        t.sprint_id = sprint.id

            db.commit()
            db.refresh(sprint)

            redis_client.delete(f"project_sprints:{project_id}")
            redis_client.delete(f"sprint_tasks:{sprint.id}")

            return _serialize_sprint(sprint)
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def delete_sprint(self, id):
        db = SessionLocal()
        try:
            sprint = db.get(Sprint, id)

            if sprint is None:
                raise ValueError(f"Sprint ({id}) not found")

            project_id = sprint.project_id

            db.delete(sprint)
            db.commit()

            redis_client.delete(f"project_sprints:{project_id}")
            redis_client.delete(f"sprint_tasks:{id}")
            redis_client.delete(f"project_tasks:{project_id}")

            return True
        except:
            db.rollback()
            raise
        finally:
            db.close()
