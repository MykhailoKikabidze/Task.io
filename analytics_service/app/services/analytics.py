from app.database import SessionLocal
from app.models.models import User, Task, Sprint, ProjectUser, Project, Status
from sqlalchemy.orm import joinedload
from sqlalchemy import select, func, and_
from datetime import date, datetime, timedelta
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


class AnalyticsService:
    def get_timeline_all(self, user_id):
        db = SessionLocal()
        user_id = _to_uuid_or_none(user_id)
        try:
            q = (
                select(
                    Task.title.label("task_name"),
                    Project.name.label("project_name"),
                    Task.start_date.label("start_date"),
                    func.coalesce(Task.end_date, Sprint.end_date).label("end_date"),
                )
                .join(Sprint, Task.sprint_id == Sprint.id)
                .where(Sprint.is_started.is_(True))
                .join(Project, Task.project_id == Project.id)
                .join(
                    ProjectUser,
                    and_(
                        ProjectUser.project_id == Project.id,
                        ProjectUser.user_id == user_id,
                    ),
                )
                .order_by(func.coalesce(Task.start_date, Sprint.start_date),
                          func.coalesce(Task.end_date, Sprint.end_date))
            )

            rows = db.execute(q).all()

            result: list[dict[str, str]] = [
                {
                    "task_name": task_name,
                    "project_name": project_name,
                    "start_date": _fmt_date(start_date),
                    "end_date": _fmt_date(end_date),
                }
                for task_name, project_name, start_date, end_date in rows
            ]

            return result
        finally:
            db.close()

    def get_timeline_project(self, user_id, project_id):
        db = SessionLocal()
        user_id = _to_uuid_or_none(user_id)
        project_id = _to_uuid_or_none(project_id)
        try:
            q = (
                select(
                    Task.title.label("task_name"),
                    Project.name.label("project_name"),
                    Task.start_date.label("start_date"),
                    func.coalesce(Task.end_date, Sprint.end_date).label("end_date"),
                )
                .join(Sprint, Task.sprint_id == Sprint.id)
                .where(Sprint.is_started.is_(True))
                .join(Project, Task.project_id == Project.id)
                .where(Project.id == project_id)
                .join(
                    ProjectUser,
                    and_(
                        ProjectUser.project_id == Project.id,
                        ProjectUser.user_id == user_id,
                    ),
                )
                .order_by(
                    func.coalesce(Task.start_date, Sprint.start_date),
                    func.coalesce(Task.end_date, Sprint.end_date),
                    Task.title,
                )
            )

            rows = db.execute(q).all()

            return [
                {
                    "task_name": task_name,
                    "project_name": project_name,
                    "start_date": _fmt_date(start_date),
                    "end_date": _fmt_date(end_date),
                }
                for task_name, project_name, start_date, end_date in rows
            ]
        finally:
            db.close()

    def get_timeline_all_mine(self, user_id):
        db = SessionLocal()
        user_id = _to_uuid_or_none(user_id)
        try:
            q = (
                select(
                    Task.title.label("task_name"),
                    Project.name.label("project_name"),
                    Task.start_date.label("start_date"),
                    func.coalesce(Task.end_date, Sprint.end_date).label("end_date"),
                )
                .join(Sprint, Task.sprint_id == Sprint.id)
                .where(Sprint.is_started.is_(True))
                .join(Project, Task.project_id == Project.id)
                .join(
                    ProjectUser,
                    and_(
                        ProjectUser.project_id == Project.id,
                        ProjectUser.user_id == user_id,
                    ),
                )
                .where(Task.assigned_to == user_id)
                .order_by(
                    func.coalesce(Task.start_date, Sprint.start_date),
                    func.coalesce(Task.end_date, Sprint.end_date),
                    Task.title,
                )
            )

            rows = db.execute(q).all()

            return [
                {
                    "task_name": task_name,
                    "project_name": project_name,
                    "start_date": _fmt_date(start_date),
                    "end_date": _fmt_date(end_date),
                }
                for task_name, project_name, start_date, end_date in rows
            ]
        finally:
            db.close()

    def get_timeline_project_mine(self, user_id, project_id):
        db = SessionLocal()
        try:
            q = (
                select(
                    Task.title.label("task_name"),
                    Project.name.label("project_name"),
                    Task.start_date.label("start_date"),
                    func.coalesce(Task.end_date, Sprint.end_date).label("end_date"),
                )
                .join(Sprint, Task.sprint_id == Sprint.id)
                .where(Sprint.is_started.is_(True))
                .join(Project, Task.project_id == Project.id)
                .where(Project.id == project_id)
                .join(
                    ProjectUser,
                    and_(
                        ProjectUser.project_id == Project.id,
                        ProjectUser.user_id == user_id,
                    ),
                )
                .where(Task.assigned_to == user_id)
                .order_by(
                    func.coalesce(Task.start_date, Sprint.start_date),
                    func.coalesce(Task.end_date, Sprint.end_date),
                    Task.title,
                )
            )

            rows = db.execute(q).all()

            return [
                {
                    "task_name": task_name,
                    "project_name": project_name,
                    "start_date": _fmt_date(start_date),
                    "end_date": _fmt_date(end_date),
                }
                for task_name, project_name, start_date, end_date in rows
            ]
        finally:
            db.close()

    def get_tasks_completed_by_user(self, project_id):
        db = SessionLocal()
        try:
            users_rows = db.execute(
                select(User.id, User.name, User.surname)
                .join(ProjectUser, ProjectUser.user_id == User.id)
                .where(ProjectUser.project_id == project_id)
                .order_by(User.surname, User.name)
            ).all()

            result_map: dict = {
                uid: {
                    "user_id": str(uid),
                    "full_name": f"{name} {surname}",
                    "completed_tasks": [],
                }
                for uid, name, surname in users_rows
            }

            if not result_map:
                return []

            user_ids = list(result_map.keys())

            done_rows = db.execute(
                select(Task.title, Task.assigned_to)
                .join(Status, Task.status_id == Status.id)
                .where(
                    Task.project_id == project_id,
                    Status.name == "done",
                    Task.assigned_to.in_(user_ids),
                )
                .order_by(Task.title)
            ).all()

            for title, assignee_id in done_rows:
                result_map[assignee_id]["completed_tasks"].append(title)

            return list(result_map.values())

        finally:
            db.close()

    def get_tasks_status_in_sprints(self, project_id):
        db = SessionLocal()
        try:
            sprints = db.execute(
                select(Sprint.id, Sprint.name)
                .where(Sprint.project_id == project_id)
                .order_by(Sprint.start_date, Sprint.created_at, Sprint.name)
            ).all()

            if not sprints:
                return []

            result_map: dict = {
                sid: {
                    "sprint_id": str(sid),
                    "name": name,
                    "completed_tasks": [],
                    "uncompleted_tasks": [],
                }
                for sid, name in sprints
            }
            sprint_ids = list(result_map.keys())

            rows = db.execute(
                select(
                    Task.sprint_id,
                    Task.title,
                    (func.lower(Status.name) == "done").label("is_done"),
                )
                .join(Status, Status.id == Task.status_id)
                .where(
                    Task.project_id == project_id,
                    Task.sprint_id.in_(sprint_ids),
                )
                .order_by(Task.sprint_id, Task.title)
            ).all()

            for sprint_id, title, is_done in rows:
                if is_done:
                    result_map[sprint_id]["completed_tasks"].append(title)
                else:
                    result_map[sprint_id]["uncompleted_tasks"].append(title)

            return list(result_map.values())

        finally:
            db.close()

    def get_tasks_progress_by_day(self, project_id):
        db = SessionLocal()
        try:
            project_start = db.execute(
                select(func.min(Sprint.start_date)).where(
                    Sprint.project_id == project_id,
                    Sprint.start_date.isnot(None),
                )
            ).scalar()

            if project_start is None:
                return []

            today = date.today()
            if project_start > today:
                return []

            rows = db.execute(
                select(Task.title, Task.end_date)
                .join(Status, Status.id == Task.status_id)
                .where(
                    Task.project_id == project_id,
                    func.lower(Status.name) == "done",
                    Task.end_date.isnot(None),
                    Task.end_date >= project_start,
                    Task.end_date <= today,
                )
                .order_by(Task.end_date, Task.title)
            ).all()

            done_by_day: dict[date, list[str]] = {}
            for title, end_dt in rows:
                done_by_day.setdefault(end_dt, []).append(title)

            days_count = (today - project_start).days
            result: list[dict[str, object]] = []
            for i in range(days_count + 1):
                day = project_start + timedelta(days=i)
                result.append({
                    "day": _fmt_date(day),
                    "tasks": done_by_day.get(day, []),
                })

            return result

        finally:
            db.close()
