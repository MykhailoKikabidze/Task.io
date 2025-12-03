import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime, timezone


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


class Role(Base):
    __tablename__ = "roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)

    project_users = relationship("ProjectUser", back_populates="role", cascade="all, delete-orphan")


class ProjectUser(Base):
    __tablename__ = "project_users"

    user_id = Column(UUID(as_uuid=True), primary_key=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True)
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    assigned_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).astimezone(), nullable=False)

    project = relationship("Project", back_populates="users")
    role = relationship("Role", back_populates="project_users")
