import datetime
import uuid
from typing import Optional, List
from sqlalchemy import Column, String, DateTime, Integer, Float, Text, JSON
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.sql import func
from sqlmodel import SQLModel, Field

class Interview(SQLModel, table=True):
    __tablename__ = "interview"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, sa_column=Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4))
    user_id: str = Field(sa_column=Column(String, index=True, nullable=False))
    resume_id: str = Field(sa_column=Column(String, index=True, nullable=False))
    role: str = Field(sa_column=Column(String, nullable=False))
    difficulty_level: str = Field(sa_column=Column(String, nullable=False))
    duration: Optional[int] = Field(default=None, sa_column=Column(Integer))
    questions: Optional[List[str]] = Field(default=[], sa_column=Column(ARRAY(String)))
    marks: Optional[float] = Field(default=None, sa_column=Column(Float))
    performance_report: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    selected_status: Optional[str] = Field(default=None, sa_column=Column(String))
    time_taken: Optional[int] = Field(default=None, sa_column=Column(Integer))
    status: str = Field(default="active", sa_column=Column(String, default="active"))
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow, sa_column=Column(DateTime(timezone=True), server_default=func.now()))

    evaluation_retry_count: int = Field(default=0, sa_column=Column(Integer, nullable=False, default=0))
    evaluation_last_error: Optional[str] = Field(default=None, sa_column=Column(Text))
    evaluation_failed_at: Optional[datetime.datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    evaluation_lock_until: Optional[datetime.datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True)))

class InterviewQuestionAttempt(SQLModel, table=True):
    __tablename__ = "interview_question_attempt"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, sa_column=Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4))
    session_id: uuid.UUID = Field(sa_column=Column(UUID(as_uuid=True), index=True, nullable=False))
    question_id: str = Field(sa_column=Column(String, index=True, nullable=False))
    question_order: int = Field(sa_column=Column(Integer, nullable=False))
    answer_text: Optional[str] = Field(default=None, sa_column=Column(Text))
    score: Optional[float] = Field(default=None, sa_column=Column(Float))
    feedback: Optional[str] = Field(default=None, sa_column=Column(Text))
    time_taken: Optional[int] = Field(default=None, sa_column=Column(Integer))
    asked_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow, sa_column=Column(DateTime(timezone=True), server_default=func.now()))
