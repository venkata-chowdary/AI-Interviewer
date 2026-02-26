from sqlmodel import SQLModel, Field
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
import uuid
import datetime

class User(SQLModel, table=True):
    __tablename__="user"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, sa_column=Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4))
    email: str = Field(sa_column=Column(String, index=True, unique=True))
    hased_password: str = Field(sa_column=Column(String))
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow, sa_column=Column(DateTime(timezone=True), server_default=func.now()))