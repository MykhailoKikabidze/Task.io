import uuid
from sqlalchemy import Column, String, DateTime, Date, SmallInteger, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime, timezone


class Epic(Base):
    __tablename__ = "epics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(String(255))
    priority = Column(SmallInteger, nullable=False)
    start_date = Column(Date)
    end_date = Column(Date)

    project_id = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).astimezone(), nullable=False)
    updated_at = Column(DateTime, onupdate=lambda: datetime.now(timezone.utc).astimezone())