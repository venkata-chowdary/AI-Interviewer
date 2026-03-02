import datetime
import uuid
from typing import Optional
from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlmodel import SQLModel, Field

class Interview(SQLModel, table=True):
    __tablename__ = "interview"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, sa_column=Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4))
    user_id: str = Field(sa_column=Column(String, index=True, nullable=False))
    resume_id: str = Field(sa_column=Column(String, index=True, nullable=False))
    role: str = Field(sa_column=Column(String, nullable=False))
    difficulty_band: str = Field(sa_column=Column(String, nullable=False))
    total_questions: int = Field(default=5, sa_column=Column(Integer, default=5))
    current_question_index: int = Field(default=0, sa_column=Column(Integer, default=0))
    status: str = Field(default="active", sa_column=Column(String, default="active"))
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow, sa_column=Column(DateTime(timezone=True), server_default=func.now()))
