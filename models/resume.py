import datetime
import uuid
from typing import Optional
from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlmodel import SQLModel, Field

class ResumeMetadata(SQLModel, table=True):
    __tablename__ = "resume_metadata"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, sa_column=Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4))
    user_id: str = Field(sa_column=Column(String, index=True, nullable=False))
    file_name: str = Field(sa_column=Column(String, nullable=False))
    resume_hash: str = Field(sa_column=Column(String, unique=True, index=True, nullable=False))
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow, sa_column=Column(DateTime(timezone=True), server_default=func.now()))
    embeddings_created: bool = Field(default=False, sa_column=Column(Boolean, default=False))
    skills: Optional[str]
    experience_level: Optional[str]
    years_of_experience: Optional[int]
    resume_summary: Optional[str]
    analysis_status: str = "pending"
    
    def __repr__(self):
        return f"<ResumeMetadata(file_name='{self.file_name}', user_id='{self.user_id}')>"
