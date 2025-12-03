from datetime import date
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.database import SessionLocal
from app.models.models import (
    User, ProjectType, Role, Status, TaskType,
    Project, ProjectUser, Sprint, Epic, Task
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def _fetch_by_name_ci(session: Session, model, name: str):
    obj = session.execute(
        select(model).where(func.lower(model.name) == name.lower())
    ).unique().scalar_one_or_none()
    if not obj:
        raise ValueError(f"{model.__name__} с именем '{name}' не найден в БД.")
    return obj


def _fetch_status(session: Session, name: str) -> Status:
    return _fetch_by_name_ci(session, Status, name)


def _fetch_task_type(session: Session, name: str) -> TaskType:
    return _fetch_by_name_ci(session, TaskType, name)


def _fetch_role(session: Session, name: str) -> Role:
    return _fetch_by_name_ci(session, Role, name)


def _fetch_project_type(session: Session, name: str) -> ProjectType:
    return _fetch_by_name_ci(session, ProjectType, name)

def _ensure_user(session: Session, email: str, name: str, surname: str, password: str) -> User:
    user = session.execute(select(User).where(User.email == email)).unique().scalar_one_or_none()
    if user:
        changed = False
        if user.name != name:
            user.name = name
            changed = True
        if user.surname != surname:
            user.surname = surname
            changed = True
        if changed:
            session.commit()
        return user
    user = User(
        email=email,
        name=name,
        surname=surname,
        password=pwd_context.hash(password),
        img_url=None,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def _ensure_project(session: Session, name: str, color: str, type_pt: ProjectType,
                    description: str = "", img_url: Optional[str] = None) -> Project:
    pr = session.execute(select(Project).where(Project.name == name)).unique().scalar_one_or_none()
    if pr:
        updated = False
        if pr.type_id != type_pt.id:
            pr.type_id = type_pt.id
            updated = True
        if pr.color != color:
            pr.color = color
            updated = True
        if (pr.description or "") != (description or ""):
            pr.description = description
            updated = True
        if (pr.img_url or "") != (img_url or ""):
            pr.img_url = img_url
            updated = True
        if updated:
            session.commit()
        return pr
    pr = Project(
        name=name,
        description=description,
        color=color,
        img_url=img_url,
        type_id=type_pt.id,
    )
    session.add(pr)
    session.commit()
    session.refresh(pr)
    return pr


def _ensure_project_user(session: Session, project: Project, user: User, role: Role) -> ProjectUser:
    link = session.execute(
        select(ProjectUser).where(
            ProjectUser.project_id == project.id,
            ProjectUser.user_id == user.id
        )
    ).unique().scalar_one_or_none()
    if link:
        if link.role_id != role.id:
            link.role_id = role.id
            session.commit()
        return link
    link = ProjectUser(project_id=project.id, user_id=user.id, role_id=role.id)
    session.add(link)
    session.commit()
    return link


def _ensure_sprint(session: Session, project: Project, name: str,
                   start_date: Optional[date], end_date: Optional[date], is_started: bool) -> Sprint:
    sp = session.execute(
        select(Sprint).where(Sprint.project_id == project.id, Sprint.name == name)
    ).unique().scalar_one_or_none()
    if sp:
        changed = False
        if sp.start_date != start_date:
            sp.start_date = start_date; changed = True
        if sp.end_date != end_date:
            sp.end_date = end_date; changed = True
        if sp.is_started != is_started:
            sp.is_started = is_started; changed = True
        if changed:
            session.commit()
        return sp
    sp = Sprint(
        project_id=project.id,
        name=name,
        description=f"Sprint {name}",
        start_date=start_date,
        end_date=end_date,
        is_started=is_started,
    )
    session.add(sp)
    session.commit()
    session.refresh(sp)
    return sp


def _ensure_epic(session: Session, project: Project, name: str,
                 start_date: Optional[date], end_date: Optional[date], priority: int = 1) -> Epic:
    ep = session.execute(
        select(Epic).where(Epic.project_id == project.id, Epic.name == name)
    ).unique().scalar_one_or_none()
    if ep:
        changed = False
        if ep.start_date != start_date:
            ep.start_date = start_date; changed = True
        if ep.end_date != end_date:
            ep.end_date = end_date; changed = True
        if ep.priority != priority:
            ep.priority = priority; changed = True
        if changed:
            session.commit()
        return ep
    ep = Epic(
        project_id=project.id,
        name=name,
        description=f"Epic {name}",
        start_date=start_date,
        end_date=end_date,
        priority=priority
    )
    session.add(ep)
    session.commit()
    session.refresh(ep)
    return ep


def _ensure_task(
    session: Session,
    project: Project,
    sprint: Optional[Sprint],
    epic: Optional[Epic],
    title: str,
    ttype: TaskType,
    status: Status,
    assigned_to: Optional[User],
    start_date: Optional[date],
    end_date: Optional[date],
    priority: int = 2,
) -> Task:
    t = session.execute(
        select(Task).where(Task.project_id == project.id, Task.title == title)
    ).unique().scalar_one_or_none()
    if t:
        changed = False
        if t.type_id != ttype.id:
            t.type_id = ttype.id; changed = True
        if t.status_id != status.id:
            t.status_id = status.id; changed = True
        desired_sprint_id = sprint.id if sprint else None
        if t.sprint_id != desired_sprint_id:
            t.sprint_id = desired_sprint_id; changed = True
        desired_epic_id = epic.id if epic else None
        if t.epic_id != desired_epic_id:
            t.epic_id = desired_epic_id; changed = True
        desired_assignee = assigned_to.id if assigned_to else None
        if t.assigned_to != desired_assignee:
            t.assigned_to = desired_assignee; changed = True
        if t.start_date != start_date:
            t.start_date = start_date; changed = True
        if t.end_date != end_date:
            t.end_date = end_date; changed = True
        if t.priority != priority:
            t.priority = priority; changed = True
        if changed:
            session.commit()
        return t
    t = Task(
        project_id=project.id,
        sprint_id=sprint.id if sprint else None,
        epic_id=epic.id if epic else None,
        type_id=ttype.id,
        status_id=status.id,
        assigned_to=assigned_to.id if assigned_to else None,
        title=title,
        description=f"{title} description",
        start_date=start_date,
        end_date=end_date,
        priority=priority,
    )
    session.add(t)
    session.commit()
    session.refresh(t)
    return t



def seed_demo_data():
    db: Session = SessionLocal()
    try:
        st_todo = _fetch_status(db, "to do")
        st_inp  = _fetch_status(db, "in progress")
        st_done = _fetch_status(db, "done")

        tt_feature     = _fetch_task_type(db, "feature")
        tt_bug         = _fetch_task_type(db, "bug")
        tt_design      = _fetch_task_type(db, "design")
        tt_docs        = _fetch_task_type(db, "docs")
        tt_refactor    = _fetch_task_type(db, "refactor")
        tt_improvement = _fetch_task_type(db, "improvement")

        role_owner    = _fetch_role(db, "owner")
        role_assignee = _fetch_role(db, "assignee")
        role_observer = _fetch_role(db, "observer")

        pt_software = _fetch_project_type(db, "software")
        pt_science  = _fetch_project_type(db, "science")

        jan  = _ensure_user(db, email="jan.kowalski@example.com", name="Jan",  surname="Kowalski", password="JanPass123!")
        anna = _ensure_user(db, email="anna.nowak@example.com",  name="Anna", surname="Nowak",    password="AnnaPass123!")
        ivan = _ensure_user(db, email="ivan.sokolov@example.com", name="Ivan", surname="Sokolov", password="IvanPass123!")

        pr_alpha = _ensure_project(db, name="Project Alpha", color="#4CAF50", type_pt=pt_software, description="Alpha project")
        pr_beta  = _ensure_project(db, name="Project Beta",  color="#3F51B5", type_pt=pt_science,  description="Beta project")

        _ensure_project_user(db, pr_alpha, jan,  role_owner)
        _ensure_project_user(db, pr_alpha, anna, role_assignee)
        _ensure_project_user(db, pr_alpha, ivan, role_assignee)

        _ensure_project_user(db, pr_beta,  anna, role_owner)
        _ensure_project_user(db, pr_beta,  ivan, role_assignee)
        _ensure_project_user(db, pr_beta,  jan,  role_observer)

        sp_alpha_prev = _ensure_sprint(db, pr_alpha, "Alpha Sprint 0", date(2025, 8, 1),  date(2025, 8, 10), is_started=False)
        sp_alpha_now  = _ensure_sprint(db, pr_alpha, "Alpha Sprint 1", date(2025, 8, 12), date(2025, 8, 26), is_started=True)

        sp_beta_prev  = _ensure_sprint(db, pr_beta,  "Beta Sprint A",  date(2025, 8, 5),  date(2025, 8, 12), is_started=False)
        sp_beta_now   = _ensure_sprint(db, pr_beta,  "Beta Sprint B",  date(2025, 8, 14), date(2025, 8, 28), is_started=True)

        ep_alpha_auth = _ensure_epic(db, pr_alpha, "Authentication", date(2025, 8, 12), date(2025, 8, 26), priority=1)
        ep_alpha_ui   = _ensure_epic(db, pr_alpha, "UI/UX",          date(2025, 8, 12), date(2025, 8, 26), priority=2)
        ep_beta_rt    = _ensure_epic(db, pr_beta,  "Realtime",       date(2025, 8, 14), date(2025, 8, 28), priority=1)

        _ensure_task(
            db, pr_alpha, sp_alpha_now, ep_alpha_auth,
            title="Design login page", ttype=tt_design, status=st_done, assigned_to=jan,
            start_date=date(2025, 8, 12), end_date=date(2025, 8, 13), priority=2
        )
        _ensure_task(
            db, pr_alpha, sp_alpha_now, ep_alpha_auth,
            title="Implement auth backend", ttype=tt_feature, status=st_done, assigned_to=anna,
            start_date=date(2025, 8, 12), end_date=date(2025, 8, 15), priority=1
        )
        _ensure_task(
            db, pr_alpha, sp_alpha_now, ep_alpha_ui,
            title="Gantt chart analytics", ttype=tt_improvement, status=st_inp, assigned_to=jan,
            start_date=date(2025, 8, 16), end_date=None, priority=2
        )
        _ensure_task(
            db, pr_alpha, sp_alpha_now, ep_alpha_auth,
            title="Fix bug #123", ttype=tt_bug, status=st_done, assigned_to=jan,
            start_date=date(2025, 8, 17), end_date=date(2025, 8, 20), priority=1
        )
        _ensure_task(
            db, pr_alpha, sp_alpha_now, ep_alpha_ui,
            title="Polish dashboard", ttype=tt_improvement, status=st_todo, assigned_to=ivan,
            start_date=date(2025, 8, 18), end_date=None, priority=3
        )

        _ensure_task(
            db, pr_beta, sp_beta_now, ep_beta_rt,
            title="Landing page polish", ttype=tt_design, status=st_done, assigned_to=anna,
            start_date=date(2025, 8, 15), end_date=date(2025, 8, 18), priority=3
        )
        _ensure_task(
            db, pr_beta, sp_beta_now, ep_beta_rt,
            title="Realtime notifications", ttype=tt_feature, status=st_inp, assigned_to=ivan,
            start_date=date(2025, 8, 16), end_date=None, priority=2
        )
        _ensure_task(
            db, pr_beta, sp_beta_now, ep_beta_rt,
            title="Kafka tuning", ttype=tt_refactor, status=st_todo, assigned_to=ivan,
            start_date=date(2025, 8, 17), end_date=None, priority=2
        )
        _ensure_task(
            db, pr_beta, sp_beta_now, ep_beta_rt,
            title="Fix flaky test #77", ttype=tt_bug, status=st_done, assigned_to=jan,
            start_date=date(2025, 8, 18), end_date=date(2025, 8, 21), priority=1
        )

        _ensure_task(
            db, pr_alpha, sp_alpha_prev, ep_alpha_auth,
            title="Legacy cleanup", ttype=tt_docs, status=st_done, assigned_to=ivan,
            start_date=date(2025, 8, 2), end_date=date(2025, 8, 6), priority=3
        )
        _ensure_task(
            db, pr_beta, sp_beta_prev, ep_beta_rt,
            title="PoC for realtime", ttype=tt_feature, status=st_done, assigned_to=anna,
            start_date=date(2025, 8, 6), end_date=date(2025, 8, 10), priority=2
        )

        print("Demo data seeded successfully with existing vocab.")
    finally:
        db.close()
