import uuid
from datetime import datetime, date, timezone

from sqlalchemy import (
    Column, String, Text, Date, DateTime, SmallInteger,
    ForeignKey, Table, Boolean
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base, engine


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    surname = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    password = Column(String(255), nullable=False)
    img_url = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).astimezone(), nullable=False)
    updated_at = Column(DateTime, onupdate=lambda: datetime.now(timezone.utc).astimezone())

    assigned_tasks = relationship("Task", back_populates="assignee", cascade="all, delete-orphan")
    project_links = relationship("ProjectUser", back_populates="user", cascade="all, delete-orphan")


class ProjectType(Base):
    __tablename__ = "project_types"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)

    projects = relationship("Project", back_populates="type", cascade="all, delete-orphan", lazy="joined")


class Project(Base):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(String(255))
    color = Column(String(255), nullable=False)
    img_url = Column(String(255))

    type_id = Column(UUID(as_uuid=True), ForeignKey("project_types.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).astimezone(), nullable=False)
    updated_at = Column(DateTime, onupdate=lambda: datetime.now(timezone.utc).astimezone())

    type = relationship("ProjectType", back_populates="projects")
    users = relationship("ProjectUser", back_populates="project", cascade="all, delete-orphan")
    epics = relationship("Epic", back_populates="project", cascade="all, delete-orphan")
    sprints = relationship("Sprint", back_populates="project", cascade="all, delete-orphan")
    pages = relationship("Page", back_populates="project", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="project", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")


class Role(Base):
    __tablename__ = "roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)

    project_users = relationship("ProjectUser", back_populates="role", cascade="all, delete-orphan")


class ProjectUser(Base):
    __tablename__ = "project_users"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True)
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    assigned_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).astimezone(), nullable=False)

    user = relationship("User", back_populates="project_links")
    project = relationship("Project", back_populates="users")
    role = relationship("Role", back_populates="project_users")


class Epic(Base):
    __tablename__ = "epics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(String(255))
    priority = Column(SmallInteger, nullable=False)
    start_date = Column(Date)
    end_date = Column(Date)

    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).astimezone(), nullable=False)
    updated_at = Column(DateTime, onupdate=lambda: datetime.now(timezone.utc).astimezone())

    project = relationship("Project", back_populates="epics")
    tasks = relationship("Task", back_populates="epic", cascade="all, delete-orphan")


class Sprint(Base):
    __tablename__ = "sprints"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(String(255))
    start_date = Column(Date)
    end_date = Column(Date)
    is_started = Column(Boolean, default=False)

    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).astimezone(), nullable=False)
    updated_at = Column(DateTime, onupdate=lambda: datetime.now(timezone.utc).astimezone())

    project = relationship("Project", back_populates="sprints")
    tasks = relationship("Task", back_populates="sprint", cascade="all, delete-orphan")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    description = Column(String(255))
    priority = Column(SmallInteger)

    type_id = Column(UUID(as_uuid=True), ForeignKey("task_types.id", ondelete="CASCADE"), nullable=False)
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    epic_id = Column(UUID(as_uuid=True), ForeignKey("epics.id", ondelete="SET NULL"))
    sprint_id = Column(UUID(as_uuid=True), ForeignKey("sprints.id", ondelete="SET NULL"))
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    status_id = Column(UUID(as_uuid=True), ForeignKey("statuses.id", ondelete="CASCADE"), nullable=False)

    start_date = Column(Date)
    end_date = Column(Date)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).astimezone(), nullable=False)
    updated_at = Column(DateTime, onupdate=lambda: datetime.now(timezone.utc).astimezone())

    project = relationship("Project", back_populates="tasks")
    assignee = relationship("User", back_populates="assigned_tasks")
    epic = relationship("Epic", back_populates="tasks")
    sprint = relationship("Sprint", back_populates="tasks")
    status = relationship("Status", back_populates="tasks")
    type = relationship("TaskType", back_populates="tasks")


class TaskType(Base):
    __tablename__ = "task_types"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True)

    tasks = relationship("Task", back_populates="type", cascade="all, delete-orphan")


class Status(Base):
    __tablename__ = "statuses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True)

    tasks = relationship("Task", back_populates="status", cascade="all, delete-orphan")


class Page(Base):
    __tablename__ = "pages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).astimezone(), nullable=False)
    updated_at = Column(DateTime, onupdate=lambda: datetime.now(timezone.utc).astimezone())

    project = relationship("Project", back_populates="pages")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    date = Column(DateTime, default=lambda: datetime.now(timezone.utc).astimezone(), nullable=False)

    project = relationship("Project", back_populates="notifications")
