from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.sql import func
import uuid
import datetime


class User(SQLModel, table=True):
    __tablename__ = "user"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        sa_column=Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    )
    email: str = Field(sa_column=Column(String, index=True, unique=True))
    hased_password: str = Field(sa_column=Column(String))
    created_at: datetime.datetime = Field(
        default_factory=datetime.datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )

    # Public profile fields
    first_name: Optional[str] = Field(
        default=None,
        sa_column=Column(String, nullable=True),
    )
    last_name: Optional[str] = Field(
        default=None,
        sa_column=Column(String, nullable=True),
    )
    bio: Optional[str] = Field(
        default=None,
        sa_column=Column(String, nullable=True),
    )

    # Email verification fields
    is_email_verified: bool = Field(
        default=False,
        sa_column=Column(Boolean, nullable=False, default=False),
    )
    email_verification_otp: Optional[str] = Field(
        default=None,
        sa_column=Column(String, nullable=True),
    )
    email_verification_expires_at: Optional[datetime.datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )