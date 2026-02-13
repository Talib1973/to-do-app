"""Chat API endpoint for AI chatbot interaction."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from uuid import UUID
from datetime import datetime
from typing import List

from src.database import get_session
from src.auth.jwt import get_current_user
from src.models.user import User
from src.models.conversation import Conversation
from src.models.message import Message
from src.schemas.chat import ChatRequest, ChatResponse, MessageSchema, ToolCallSchema
from src.ai.agent import run_agent

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/{user_id}/chat", response_model=ChatResponse)
async def send_chat_message(
    user_id: UUID,
    request: ChatRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
) -> ChatResponse:
    """
    Send message to AI chatbot and receive conversational response.

    **Authentication**: Requires valid JWT token
    **Authorization**: user_id in route MUST match user_id from JWT

    **Request Lifecycle**:
    1. Validate JWT and verify user_id matches authenticated user
    2. Load or create conversation
    3. Store user message in database
    4. Load conversation history from database
    5. Invoke AI agent with history and MCP tools
    6. Store assistant response in database
    7. Update conversation updated_at timestamp
    8. Return response with conversation_id and tool calls

    Args:
        user_id: User identifier from route (must match JWT user_id)
        request: ChatRequest with optional conversation_id and message
        session: Database session
        current_user: Authenticated user from JWT

    Returns:
        ChatResponse: {conversation_id, message, tool_calls}

    Raises:
        HTTPException 403: user_id in route doesn't match JWT user_id
        HTTPException 404: conversation_id provided but not found or doesn't belong to user
        HTTPException 500: AI agent failure or database error

    Example:
        POST /api/550e8400-e29b-41d4-a716-446655440000/chat
        Headers: Authorization: Bearer {jwt}
        Body: {"conversation_id": null, "message": "I need to buy groceries"}

        Response: {
            "conversation_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
            "message": {
                "id": "...",
                "role": "assistant",
                "content": "I've added 'Buy groceries' to your task list.",
                "created_at": "2026-02-07T14:32:15Z"
            },
            "tool_calls": [{"tool": "add_task", ...}]
        }
    """
    # SECURITY: Verify user_id in route matches authenticated user from JWT
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User ID in route does not match authenticated user"
        )

    try:
        # Step 1: Resolve conversation (load existing or create new)
        conversation: Conversation

        if request.conversation_id:
            # Load existing conversation
            conversation = session.exec(
                select(Conversation).where(
                    Conversation.id == request.conversation_id,
                    Conversation.user_id == current_user.id
                )
            ).first()

            if not conversation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found or does not belong to user"
                )
        else:
            # Create new conversation
            conversation = Conversation(
                user_id=current_user.id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(conversation)
            session.commit()
            session.refresh(conversation)

        # Step 2: Store user message in database BEFORE agent processing
        user_message = Message(
            conversation_id=conversation.id,
            user_id=current_user.id,
            role="user",
            content=request.message,
            created_at=datetime.utcnow()
        )
        session.add(user_message)

        # Step 3: Load conversation history from database
        conversation_messages = session.exec(
            select(Message)
            .where(Message.conversation_id == conversation.id)
            .where(Message.user_id == current_user.id)
            .order_by(Message.created_at.asc())
        ).all()

        # Build conversation history (exclude the message we just added)
        conversation_history = [
            {"role": msg.role, "content": msg.content}
            for msg in conversation_messages
            if msg.id != user_message.id  # Exclude current user message
        ]

        # Save conversation ID BEFORE closing session
        conversation_id = conversation.id

        # CRITICAL: Commit and close session BEFORE calling AI agent
        # This prevents database locks when agent tools try to write
        session.commit()
        session.close()

        # Step 4: Invoke AI agent with conversation history and user message
        agent_response = run_agent(
            user_id=str(current_user.id),
            user_message=request.message,
            conversation_history=conversation_history
        )

        # Reopen session for storing assistant response
        from src.database import engine
        with Session(engine) as new_session:
            # Step 5: Store assistant response in database AFTER agent processing
            assistant_message = Message(
                conversation_id=conversation_id,
                user_id=current_user.id,
                role="assistant",
                content=agent_response["content"],
                created_at=datetime.utcnow()
            )
            new_session.add(assistant_message)

            # Step 6: Update conversation updated_at timestamp
            conv = new_session.get(Conversation, conversation_id)
            if conv:
                conv.updated_at = datetime.utcnow()
                new_session.add(conv)

            # Commit all changes
            new_session.commit()
            new_session.refresh(assistant_message)

            # Get fresh copies for response
            assistant_message_data = {
                "id": assistant_message.id,
                "role": assistant_message.role,
                "content": assistant_message.content,
                "created_at": assistant_message.created_at
            }

        # Step 7: Build and return response
        return ChatResponse(
            conversation_id=conversation_id,
            message=MessageSchema(
                id=assistant_message_data["id"],
                role=assistant_message_data["role"],
                content=assistant_message_data["content"],
                created_at=assistant_message_data["created_at"]
            ),
            tool_calls=[
                ToolCallSchema(
                    tool=tc["tool"],
                    parameters=tc["parameters"],
                    result=tc["result"]
                )
                for tc in agent_response["tool_calls"]
            ]
        )

    except HTTPException:
        # Re-raise HTTP exceptions (403, 404)
        raise

    except Exception as e:
        # Log error for debugging (but don't expose to user)
        print(f"Chat endpoint error: {str(e)}")

        # Return user-friendly error message
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="I'm having trouble processing your request right now. Please try again in a moment."
        )


@router.get("/{user_id}/conversations/{conversation_id}/messages", response_model=List[MessageSchema])
async def get_conversation_messages(
    user_id: UUID,
    conversation_id: UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
) -> List[MessageSchema]:
    """
    Load conversation history (for frontend to display on page load).

    Args:
        user_id: User identifier (must match JWT)
        conversation_id: Conversation UUID
        session: Database session
        current_user: Authenticated user from JWT

    Returns:
        List[MessageSchema]: All messages in chronological order

    Raises:
        HTTPException 403: user_id doesn't match JWT
        HTTPException 404: conversation not found or doesn't belong to user
    """
    # Verify user_id matches authenticated user
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User ID in route does not match authenticated user"
        )

    # Load conversation to verify ownership
    conversation = session.exec(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        )
    ).first()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found or does not belong to user"
        )

    # Load all messages for conversation
    messages = session.exec(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .where(Message.user_id == current_user.id)
        .order_by(Message.created_at.asc())
    ).all()

    return [
        MessageSchema(
            id=msg.id,
            role=msg.role,
            content=msg.content,
            created_at=msg.created_at
        )
        for msg in messages
    ]
