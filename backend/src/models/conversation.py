"""Conversation model for AI chatbot feature."""

from sqlmodel import Field, SQLModel, Relationship
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .message import Message
    from .user import User


class Conversation(SQLModel, table=True):
    """
    Represents a chat session between an authenticated user and the AI chatbot.

    Business Rules:
    - Conversations belong to exactly one user
    - Conversations cannot be shared between users
    - Conversations are append-only (no deletion in initial implementation)
    - updated_at timestamp updates whenever a new message is added
    """
    __tablename__ = "conversations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", nullable=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    messages: List["Message"] = Relationship(back_populates="conversation")
    user: Optional["User"] = Relationship(back_populates="conversations")
