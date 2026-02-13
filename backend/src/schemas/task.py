"""Task request and response schemas."""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, validator


class TaskCreate(BaseModel):
    """
    Request schema for creating a new task.

    Attributes:
        title: Task title (required, max 500 chars)
        description: Task description (optional, max 5000 chars)
        completed: Completion status (optional, default: false)
    """
    title: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Task title",
        example="Buy groceries"
    )
    description: Optional[str] = Field(
        None,
        max_length=5000,
        description="Task description",
        example="Milk, eggs, and bread"
    )
    completed: bool = Field(
        default=False,
        description="Task completion status",
        example=False
    )

    @validator('title')
    def title_not_empty(cls, v):
        """Ensure title is not just whitespace."""
        if not v or not v.strip():
            raise ValueError('Title cannot be empty or whitespace')
        return v.strip()


class TaskUpdate(BaseModel):
    """
    Request schema for full task update (PUT).

    All fields are required for full replacement.

    Attributes:
        title: New task title (required, max 500 chars)
        description: New task description (optional, max 5000 chars)
        completed: New completion status (required)
    """
    title: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Task title",
        example="Buy groceries (updated)"
    )
    description: Optional[str] = Field(
        None,
        max_length=5000,
        description="Task description",
        example="Milk, eggs, bread, and butter"
    )
    completed: bool = Field(
        ...,
        description="Task completion status",
        example=True
    )

    @validator('title')
    def title_not_empty(cls, v):
        """Ensure title is not just whitespace."""
        if not v or not v.strip():
            raise ValueError('Title cannot be empty or whitespace')
        return v.strip()


class TaskPatch(BaseModel):
    """
    Request schema for partial task update (PATCH).

    All fields are optional. Only provided fields will be updated.

    Attributes:
        title: Update task title (optional, max 500 chars)
        description: Update task description (optional, max 5000 chars)
        completed: Update completion status (optional)
    """
    title: Optional[str] = Field(
        None,
        min_length=1,
        max_length=500,
        description="Task title",
        example="Buy groceries (updated)"
    )
    description: Optional[str] = Field(
        None,
        max_length=5000,
        description="Task description",
        example="Milk, eggs, bread, and butter"
    )
    completed: Optional[bool] = Field(
        None,
        description="Task completion status",
        example=True
    )

    @validator('title')
    def title_not_empty(cls, v):
        """Ensure title is not just whitespace if provided."""
        if v is not None and (not v or not v.strip()):
            raise ValueError('Title cannot be empty or whitespace')
        return v.strip() if v else None


class TaskResponse(BaseModel):
    """
    Task response schema.

    Attributes:
        id: Task UUID
        user_id: Owner's user UUID
        title: Task title
        description: Task description (optional)
        completed: Completion status
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """
    id: UUID = Field(
        ...,
        description="Task unique identifier",
        example="550e8400-e29b-41d4-a716-446655440000"
    )
    user_id: UUID = Field(
        ...,
        description="Task owner's user ID",
        example="123e4567-e89b-12d3-a456-426614174000"
    )
    title: str = Field(
        ...,
        description="Task title",
        example="Buy groceries"
    )
    description: Optional[str] = Field(
        None,
        description="Task description",
        example="Milk, eggs, and bread"
    )
    completed: bool = Field(
        ...,
        description="Task completion status",
        example=False
    )
    created_at: datetime = Field(
        ...,
        description="Task creation timestamp",
        example="2026-02-06T10:30:00Z"
    )
    updated_at: datetime = Field(
        ...,
        description="Last update timestamp",
        example="2026-02-06T10:30:00Z"
    )

    class Config:
        """Pydantic configuration."""
        from_attributes = True  # Allow creating from SQLModel objects
