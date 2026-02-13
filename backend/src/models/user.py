"""User model for authentication and ownership."""
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .conversation import Conversation
    from .message import Message


class User(SQLModel, table=True):
    """
    User account model.

    Stores user authentication credentials and metadata.
    Each user can own multiple tasks.

    Attributes:
        id: Unique identifier (UUID v4)
        email: User's email address (unique, case-insensitive)
        password_hash: Bcrypt hashed password (never store plain text)
        created_at: Timestamp when account was created
        updated_at: Timestamp when account was last modified
    """

    __tablename__ = "users"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False,
        description="Unique user identifier"
    )

    name: str = Field(
        max_length=100,
        nullable=False,
        description="User's full name"
    )

    email: str = Field(
        max_length=255,
        nullable=False,
        index=True,
        description="User email address (case-insensitive unique)"
    )

    password_hash: str = Field(
        max_length=255,
        nullable=False,
        description="Bcrypt hashed password"
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Account creation timestamp"
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Last update timestamp (auto-updated by trigger)"
    )

    # Relationships (AI chatbot feature)
    conversations: List["Conversation"] = Relationship(back_populates="user")
    messages: List["Message"] = Relationship(back_populates="user")

    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "user@example.com",
                "created_at": "2026-02-06T10:00:00Z",
                "updated_at": "2026-02-06T10:00:00Z"
            }
        }
