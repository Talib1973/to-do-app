"""Task model for todo items."""
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field


class Task(SQLModel, table=True):
    """
    Task/Todo item model.

    Stores individual task data with user ownership.
    Each task belongs to exactly one user.

    Attributes:
        id: Unique identifier (UUID v4)
        user_id: Foreign key to users table (owner of this task)
        title: Task title/summary (max 500 characters)
        description: Optional detailed description (max 5000 characters)
        completed: Whether task is marked as done (default: False)
        created_at: Timestamp when task was created
        updated_at: Timestamp when task was last modified
    """

    __tablename__ = "tasks"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False,
        description="Unique task identifier"
    )

    user_id: UUID = Field(
        foreign_key="users.id",
        nullable=False,
        index=True,
        description="Task owner (foreign key to users.id)"
    )

    title: str = Field(
        max_length=500,
        nullable=False,
        description="Task title (required, max 500 chars)"
    )

    description: Optional[str] = Field(
        default=None,
        max_length=5000,
        description="Task description (optional, max 5000 chars)"
    )

    completed: bool = Field(
        default=False,
        nullable=False,
        index=True,
        description="Task completion status"
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Task creation timestamp"
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Last update timestamp (auto-updated by trigger)"
    )

    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "title": "Buy groceries",
                "description": "Milk, eggs, and bread",
                "completed": False,
                "created_at": "2026-02-06T10:30:00Z",
                "updated_at": "2026-02-06T10:30:00Z"
            }
        }
