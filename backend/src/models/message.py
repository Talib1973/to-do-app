"""Message model for AI chatbot feature."""

from sqlmodel import Field, SQLModel, Relationship
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from pydantic import field_validator

if TYPE_CHECKING:
    from .conversation import Conversation
    from .user import User


class Message(SQLModel, table=True):
    """
    Represents a single message within a conversation (either from user or AI assistant).

    Business Rules:
    - Messages must belong to a valid conversation
    - user_id must match the conversation's user_id (referential integrity)
    - Role must be either 'user' (human) or 'assistant' (AI chatbot)
    - Messages are immutable once created (no editing or deletion)
    - Messages are ordered chronologically by created_at
    """
    __tablename__ = "messages"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", nullable=False)
    user_id: UUID = Field(foreign_key="users.id", nullable=False)
    role: str = Field(nullable=False, max_length=20)  # 'user' or 'assistant'
    content: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    conversation: Optional["Conversation"] = Relationship(back_populates="messages")
    user: Optional["User"] = Relationship(back_populates="messages")

    @field_validator('role')
    @classmethod
    def validate_role(cls, v: str) -> str:
        """Validate that role is either 'user' or 'assistant'."""
        if v not in ('user', 'assistant'):
            raise ValueError('role must be "user" or "assistant"')
        return v

    @field_validator('content')
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Validate that content is not empty."""
        if not v or not v.strip():
            raise ValueError('content cannot be empty')
        return v.strip()
