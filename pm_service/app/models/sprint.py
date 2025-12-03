import uuid
from sqlalchemy import Column, String, DateTime, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime, timezone


class Sprint(Base):
    __tablename__ = "sprints"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(String(255))
    start_date = Column(Date)
    end_date = Column(Date)

    project_id = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).astimezone(), nullable=False)
    updated_at = Column(DateTime, onupdate=lambda: datetime.now(timezone.utc).astimezone())
