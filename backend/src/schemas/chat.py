"""Pydantic schemas for chat API request/response validation."""

from pydantic import BaseModel, Field, field_validator
from uuid import UUID
from typing import Optional, List, Dict, Any
from datetime import datetime


class ChatRequest(BaseModel):
    """
    Request schema for POST /api/{user_id}/chat endpoint.

    Attributes:
        conversation_id: UUID of existing conversation (None for new conversation)
        message: User's message text (1-10000 characters)
    """
    conversation_id: Optional[UUID] = Field(
        None,
        description="Existing conversation ID or null for new conversation"
    )
    message: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="User's message text"
    )

    @field_validator('message')
    @classmethod
    def message_not_empty(cls, v: str) -> str:
        """Ensure message is not just whitespace."""
        if not v or not v.strip():
            raise ValueError('Message cannot be empty or whitespace')
        return v.strip()


class MessageSchema(BaseModel):
    """
    Schema for a single message in conversation.

    Attributes:
        id: Message UUID
        role: "user" or "assistant"
        content: Message text
        created_at: ISO 8601 timestamp
    """
    id: UUID
    role: str
    content: str
    created_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "role": "assistant",
                "content": "I've added 'Buy groceries' to your task list.",
                "created_at": "2026-02-07T14:32:15Z"
            }
        }


class ToolCallSchema(BaseModel):
    """
    Schema for MCP tool invocation (for transparency and debugging).

    Attributes:
        tool: Tool name (e.g., "add_task", "list_tasks")
        parameters: Parameters passed to tool
        result: Tool response data
    """
    tool: str
    parameters: Dict[str, Any]
    result: Dict[str, Any]


class ChatResponse(BaseModel):
    """
    Response schema for POST /api/{user_id}/chat endpoint.

    Attributes:
        conversation_id: UUID of conversation (newly created if was null in request)
        message: AI assistant's response message
        tool_calls: List of MCP tools invoked by agent (for transparency)
    """
    conversation_id: UUID = Field(..., description="Conversation UUID")
    message: MessageSchema = Field(..., description="AI assistant's response")
    tool_calls: List[ToolCallSchema] = Field(
        default_factory=list,
        description="MCP tools invoked during request"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
                "message": {
                    "id": "8d4f8390-3b16-42f3-9c21-5f8e7a6b4c2d",
                    "role": "assistant",
                    "content": "I've added 'Buy groceries' to your task list. Would you like to add any details?",
                    "created_at": "2026-02-07T14:32:15Z"
                },
                "tool_calls": [
                    {
                        "tool": "add_task",
                        "parameters": {
                            "user_id": "550e8400-e29b-41d4-a716-446655440000",
                            "title": "Buy groceries",
                            "description": ""
                        },
                        "result": {
                            "status": "success",
                            "data": {
                                "id": "123",
                                "title": "Buy groceries",
                                "completed": False
                            }
                        }
                    }
                ]
            }
        }
