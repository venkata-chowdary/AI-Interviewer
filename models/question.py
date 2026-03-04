import uuid
import enum
from sqlmodel import SQLModel, Field
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String, Integer, Enum, DateTime, JSON
import datetime


class DomainEnum(str, enum.Enum):
    backend="backend"
    frontend="frontend"
    fullstack="fullstack"
    system_design="system_design"
    genai="genai"
    database="database"

class CategoryEnum(str, enum.Enum):
    technical="technical"
    conceptual="conceptual"
    coding="coding"
    system_design="system_design"
    behavioral="behavioral"


class Question(SQLModel, table=True):
    __tablename__ = "question"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, sa_column=Column(UUID(as_uuid=True), primary_key=True))

    domain: DomainEnum = Field(sa_column=Column(Enum(DomainEnum), nullable=False))
    category: CategoryEnum = Field(sa_column=Column(Enum(CategoryEnum), nullable=False))

    topic: str=Field(sa_column=Column(String, nullable=False))
    difficulty_level: int = Field(sa_column=Column(Integer, nullable=False))

    primary_skill: str = Field(sa_column=Column(String, nullable=False))
    secondary_skill: list = Field(default_factory=list, sa_column=Column(JSON))

    question_text: str = Field(sa_column=Column(String, nullable=False))

    expected_concepts: list = Field(default_factory=list, sa_column=Column(JSON))
    max_score: int = Field(sa_column=Column(Integer, nullable=False))
    scoring_guidelines: dict = Field(default_factory=dict, sa_column=Column(JSON))

    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow, sa_column=Column(DateTime(timezone=True), server_default=func.now()))

    