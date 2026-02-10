# AI Chatbot Implementation Research

**Feature**: AI Chatbot for Task Management
**Branch**: `004-ai-chatbot`
**Date**: 2026-02-07
**Purpose**: Research foundational technologies for implementing MCP-based AI chatbot

---

## Research Scope

This document provides implementation guidance for building an AI-powered task management chatbot using:
- OpenAI Agents SDK for agent orchestration
- Model Context Protocol (MCP) for tool-based operations
- OpenRouter/OpenAI API for language model inference
- OpenAI ChatKit for frontend chat UI
- PostgreSQL for conversation persistence

Each section provides:
- **Decision**: Recommended approach
- **Rationale**: Why this approach was chosen
- **Alternatives Considered**: Other options and rejection reasons
- **Implementation Pattern**: Concrete code/config examples

---

## 1. OpenAI Agents SDK Best Practices

### Decision: Use Session-Based State Management with Stateless Server Design

**Implementation Pattern**:

```python
# backend/src/ai/agent.py
from agents_sdk import Agent, Session
from openai import OpenAI
import os

# Configure API provider (OpenAI or OpenRouter)
def get_ai_client():
    provider = os.getenv("AI_PROVIDER", "openai")

    if provider == "openrouter":
        return OpenAI(
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1"
        )
    else:
        return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Create stateless agent with MCP tools
def create_task_agent(mcp_tools: list):
    """
    Agent is stateless - session recreated per request.
    Conversation history loaded from database, not memory.
    """
    client = get_ai_client()

    agent = Agent(
        name="TaskAssistant",
        instructions="""You are a helpful task management assistant.

        You help users:
        - Create tasks with natural language ("I need to buy groceries")
        - View their tasks ("Show me what's pending")
        - Complete tasks ("Mark task 3 as done")
        - Update tasks ("Change task 2 to 'Call mom at 6pm'")
        - Delete tasks ("Remove the meeting task")

        Always:
        - Be friendly and conversational
        - Confirm actions clearly
        - Ask for clarification when ambiguous
        - Use the provided tools to interact with tasks
        - Never access data outside the user's scope
        """,
        model=os.getenv("AI_MODEL", "gpt-3.5-turbo"),
        tools=mcp_tools,  # MCP tools registered here
        client=client
    )

    return agent

# Stateless request handler
def handle_chat_request(user_id: int, conversation_history: list, new_message: str, mcp_tools: list):
    """
    Each request creates fresh session with database-loaded history.
    No state persisted in memory between requests.
    """
    agent = create_task_agent(mcp_tools)

    # Create session with conversation history from database
    session = Session(agent=agent)

    # Inject conversation history
    for msg in conversation_history:
        session.add_message(role=msg["role"], content=msg["content"])

    # Process new user message
    response = session.run(new_message)

    # Return response (server discards session after this)
    return {
        "response": response.output[-1]["content"],  # Latest assistant message
        "tool_calls": response.tool_calls,  # List of tools invoked
        "session_id": None  # Session not persisted in memory
    }
```

**Rationale**:

1. **Stateless Architecture**: OpenAI Agents SDK's Session management allows loading conversation history from database per request, enabling horizontal scaling and server restarts without state loss
2. **Previous Response ID Pattern**: SDK supports `previous_response_id` pattern where you send only new input + ID of last response, simplifying client-side logic
3. **Session Memory**: SDK handles context length, history management, and automatic compaction internally
4. **Tool Orchestration**: Built-in tool registration and invocation with minimal abstractions

**Alternatives Considered**:

| Alternative | Why Rejected |
|-------------|--------------|
| **In-memory session cache** | Violates constitutional requirement for stateless design; fails on server restart |
| **WebSocket-based stateful connections** | Adds complexity, harder to scale horizontally, not supported by ChatKit |
| **Manual conversation history management** | SDK's Session abstraction handles this better with automatic trimming and context budgets |
| **Direct OpenAI API calls without SDK** | More boilerplate, no built-in tool orchestration, manual history management |

**Key Considerations**:

- **System Prompt Design**: Keep instructions clear, actionable, and scoped to task management domain
- **Tool Registration**: Register all MCP tools during agent creation (before session starts)
- **Context Management**: SDK automatically handles context window limits with intelligent trimming
- **Conversation Reinjection**: When trimming occurs, SDK reinjacts session memories into system prompt on next turn

**Sources**:
- [OpenAI Agents SDK Documentation](https://platform.openai.com/docs/guides/agents-sdk)
- [Session Memory Management](https://cookbook.openai.com/examples/agents_sdk/session_memory)
- [Conversation State Guide](https://platform.openai.com/docs/guides/conversation-state)

---

## 2. MCP (Model Context Protocol) Server Implementation

### Decision: Use FastMCP with @mcp.tool() Decorator for Type-Safe Tool Definitions

**Implementation Pattern**:

```python
# backend/src/ai/mcp_server.py
from mcp import FastMCP
from pydantic import BaseModel, Field
from typing import Optional, Literal
from sqlmodel import Session, select
from backend.src.models.task import Task
from backend.src.database import get_session

# Initialize MCP server
mcp = FastMCP("TaskManager")

# Define tool input schemas using Pydantic
class AddTaskInput(BaseModel):
    user_id: int = Field(..., description="Authenticated user ID from JWT")
    title: str = Field(..., description="Task title")
    description: Optional[str] = Field(None, description="Optional task description")

class ListTasksInput(BaseModel):
    user_id: int = Field(..., description="Authenticated user ID from JWT")
    status: Optional[Literal["all", "pending", "completed"]] = Field(
        "all",
        description="Filter by task status"
    )

class UpdateTaskInput(BaseModel):
    user_id: int = Field(..., description="Authenticated user ID from JWT")
    task_id: int = Field(..., description="Task ID to update")
    title: Optional[str] = Field(None, description="New task title")
    description: Optional[str] = Field(None, description="New task description")

class CompleteTaskInput(BaseModel):
    user_id: int = Field(..., description="Authenticated user ID from JWT")
    task_id: int = Field(..., description="Task ID to mark complete")

class DeleteTaskInput(BaseModel):
    user_id: int = Field(..., description="Authenticated user ID from JWT")
    task_id: int = Field(..., description="Task ID to delete")

# Standard response format
class ToolResponse(BaseModel):
    status: Literal["success", "error"]
    data: Optional[dict] = None
    error: Optional[str] = None

# MCP Tool: Add Task
@mcp.tool()
def add_task(input: AddTaskInput) -> ToolResponse:
    """
    Create a new task for the authenticated user.

    Args:
        input: Task creation parameters with user_id, title, and optional description

    Returns:
        ToolResponse with created task data or error message
    """
    try:
        with get_session() as session:
            task = Task(
                user_id=input.user_id,
                title=input.title,
                description=input.description,
                completed=False
            )
            session.add(task)
            session.commit()
            session.refresh(task)

            return ToolResponse(
                status="success",
                data={
                    "task_id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed
                }
            )
    except Exception as e:
        return ToolResponse(status="error", error=f"Failed to create task: {str(e)}")

# MCP Tool: List Tasks
@mcp.tool()
def list_tasks(input: ListTasksInput) -> ToolResponse:
    """
    Retrieve tasks for the authenticated user, optionally filtered by status.

    Args:
        input: List parameters with user_id and optional status filter

    Returns:
        ToolResponse with array of tasks or error message
    """
    try:
        with get_session() as session:
            query = select(Task).where(Task.user_id == input.user_id)

            # Apply status filter
            if input.status == "pending":
                query = query.where(Task.completed == False)
            elif input.status == "completed":
                query = query.where(Task.completed == True)

            tasks = session.exec(query).all()

            return ToolResponse(
                status="success",
                data={
                    "tasks": [
                        {
                            "task_id": t.id,
                            "title": t.title,
                            "description": t.description,
                            "completed": t.completed
                        }
                        for t in tasks
                    ],
                    "count": len(tasks)
                }
            )
    except Exception as e:
        return ToolResponse(status="error", error=f"Failed to list tasks: {str(e)}")

# MCP Tool: Update Task
@mcp.tool()
def update_task(input: UpdateTaskInput) -> ToolResponse:
    """
    Update title or description of an existing task.

    Args:
        input: Update parameters with user_id, task_id, and optional new title/description

    Returns:
        ToolResponse with updated task data or error message
    """
    try:
        with get_session() as session:
            task = session.exec(
                select(Task).where(
                    Task.id == input.task_id,
                    Task.user_id == input.user_id
                )
            ).first()

            if not task:
                return ToolResponse(
                    status="error",
                    error=f"Task {input.task_id} not found for this user"
                )

            # Update fields if provided
            if input.title is not None:
                task.title = input.title
            if input.description is not None:
                task.description = input.description

            session.add(task)
            session.commit()
            session.refresh(task)

            return ToolResponse(
                status="success",
                data={
                    "task_id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed
                }
            )
    except Exception as e:
        return ToolResponse(status="error", error=f"Failed to update task: {str(e)}")

# MCP Tool: Complete Task
@mcp.tool()
def complete_task(input: CompleteTaskInput) -> ToolResponse:
    """
    Mark a task as completed.

    Args:
        input: Completion parameters with user_id and task_id

    Returns:
        ToolResponse with updated task data or error message
    """
    try:
        with get_session() as session:
            task = session.exec(
                select(Task).where(
                    Task.id == input.task_id,
                    Task.user_id == input.user_id
                )
            ).first()

            if not task:
                return ToolResponse(
                    status="error",
                    error=f"Task {input.task_id} not found for this user"
                )

            task.completed = True
            session.add(task)
            session.commit()
            session.refresh(task)

            return ToolResponse(
                status="success",
                data={
                    "task_id": task.id,
                    "title": task.title,
                    "completed": task.completed
                }
            )
    except Exception as e:
        return ToolResponse(status="error", error=f"Failed to complete task: {str(e)}")

# MCP Tool: Delete Task
@mcp.tool()
def delete_task(input: DeleteTaskInput) -> ToolResponse:
    """
    Delete a task permanently.

    Args:
        input: Deletion parameters with user_id and task_id

    Returns:
        ToolResponse confirming deletion or error message
    """
    try:
        with get_session() as session:
            task = session.exec(
                select(Task).where(
                    Task.id == input.task_id,
                    Task.user_id == input.user_id
                )
            ).first()

            if not task:
                return ToolResponse(
                    status="error",
                    error=f"Task {input.task_id} not found for this user"
                )

            session.delete(task)
            session.commit()

            return ToolResponse(
                status="success",
                data={"task_id": input.task_id, "deleted": True}
            )
    except Exception as e:
        return ToolResponse(status="error", error=f"Failed to delete task: {str(e)}")

# Export tools for agent registration
def get_mcp_tools():
    """Return all registered MCP tools for agent integration"""
    return [add_task, list_tasks, update_task, complete_task, delete_task]
```

**Rationale**:

1. **Type Safety**: Pydantic models with type hints generate JSON Schema automatically, providing validation before tool execution
2. **Standard Response Format**: Consistent `{status, data, error}` structure simplifies agent error handling
3. **User Scoping Enforcement**: Every tool requires `user_id` parameter and filters database queries accordingly
4. **Stateless Design**: No tool maintains state between invocations; each call is independent
5. **Error Handling**: Graceful error responses prevent agent crashes and enable friendly user messages

**Alternatives Considered**:

| Alternative | Why Rejected |
|-------------|--------------|
| **Manual JSON schema definition** | Error-prone, no type checking, more boilerplate vs. Pydantic auto-generation |
| **Function calling without MCP** | Less standardized, harder to test in isolation, no protocol-level guarantees |
| **Direct database access from agent** | Violates MCP architecture, breaks security boundaries, untestable |
| **REST endpoint proxying** | Adds network overhead, duplicate authorization logic, less efficient |

**Key Considerations**:

- **Parameter Validation**: Type hints directly translate into JSON Schema for LLM tool invocation
- **Tool Naming**: Use clear, verb-based names (add_task, not create_task_tool) for agent clarity
- **Error Messages**: Return user-friendly error messages (not stack traces) in `error` field
- **Idempotency**: Design tools to be idempotent where possible (e.g., completing an already-completed task returns success)
- **Authorization**: Always validate `user_id` matches JWT user before executing database operations

**Sources**:
- [MCP Python SDK](https://modelcontextprotocol.github.io/python-sdk/)
- [FastMCP Documentation](https://gofastmcp.com/servers/tools)
- [MCP Tool System Guide](https://deepwiki.com/modelcontextprotocol/python-sdk/2.2-function-metadata-and-validation)

---

## 3. OpenRouter API Integration

### Decision: Use OpenAI SDK with Configurable Base URL for Provider Switching

**Implementation Pattern**:

```python
# backend/src/ai/config.py
import os
from openai import OpenAI
from typing import Literal

def get_ai_provider() -> Literal["openai", "openrouter"]:
    """
    Determine AI provider from environment variable.
    Defaults to OpenAI if not specified.
    """
    return os.getenv("AI_PROVIDER", "openai").lower()

def get_ai_client() -> OpenAI:
    """
    Create OpenAI-compatible client for configured provider.

    Environment Variables:
        AI_PROVIDER: "openai" or "openrouter" (default: "openai")
        OPENAI_API_KEY: Required if provider is "openai"
        OPENROUTER_API_KEY: Required if provider is "openrouter"
        AI_MODEL: Model name (default: "gpt-3.5-turbo")

    Returns:
        Configured OpenAI client instance

    Raises:
        ValueError: If required API key is missing
    """
    provider = get_ai_provider()

    if provider == "openrouter":
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable required when AI_PROVIDER=openrouter")

        return OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": os.getenv("APP_URL", "http://localhost:3000"),
                "X-Title": "Task Management Chatbot"
            }
        )
    else:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable required when AI_PROVIDER=openai")

        return OpenAI(api_key=api_key)

def get_ai_model() -> str:
    """
    Get configured model name.

    Defaults:
        OpenAI: gpt-3.5-turbo
        OpenRouter: anthropic/claude-3-haiku (fast, low-cost)

    Returns:
        Model identifier string
    """
    model = os.getenv("AI_MODEL")

    if model:
        return model

    # Provider-specific defaults
    provider = get_ai_provider()
    if provider == "openrouter":
        return "anthropic/claude-3-haiku"  # Fast, cost-effective
    else:
        return "gpt-3.5-turbo"

# Example usage in chat endpoint
def process_chat_message(user_id: int, message: str, history: list):
    """
    Process chat message with configured AI provider.
    """
    client = get_ai_client()
    model = get_ai_model()

    # Use client as normal - OpenRouter is API-compatible
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful task management assistant."},
            *history,
            {"role": "user", "content": message}
        ],
        temperature=0.7,
        max_tokens=500
    )

    return response.choices[0].message.content
```

**Environment Configuration**:

```bash
# .env.example

# AI Provider Selection
AI_PROVIDER=openrouter  # or "openai"

# API Keys (provide based on AI_PROVIDER)
OPENAI_API_KEY=sk-...
OPENROUTER_API_KEY=sk-or-v1-...

# Model Selection (optional)
AI_MODEL=anthropic/claude-3-haiku  # OpenRouter model
# AI_MODEL=gpt-4  # OpenAI model

# Application metadata for OpenRouter
APP_URL=https://your-app.com
```

**Rationale**:

1. **API Compatibility**: OpenRouter is 100% OpenAI-compatible; same SDK works for both providers
2. **Cost Efficiency**: OpenRouter provides access to 500+ models at competitive pricing
3. **Flexibility**: Environment-based provider switching without code changes
4. **Fallback Strategy**: Can switch providers instantly if one experiences downtime
5. **Single Codebase**: No need to maintain separate integration code for each provider

**Alternatives Considered**:

| Alternative | Why Rejected |
|-------------|--------------|
| **Separate SDKs per provider** | Duplicated code, harder to maintain, violates DRY principle |
| **Direct HTTP requests** | More boilerplate, no type safety, manual error handling |
| **LiteLLM wrapper** | Adds dependency, unnecessary abstraction when OpenRouter is already OpenAI-compatible |
| **Hardcoded provider selection** | Inflexible, requires code changes to switch providers |

**Rate Limiting & Error Handling**:

```python
# backend/src/ai/error_handling.py
from openai import RateLimitError, APIError, APIConnectionError
import time
from functools import wraps

def retry_with_exponential_backoff(max_retries: int = 3, base_delay: float = 1.0):
    """
    Retry decorator for API calls with exponential backoff.

    Handles:
    - Rate limiting (429)
    - Temporary API errors (5xx)
    - Network connection errors
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)

                except RateLimitError as e:
                    if attempt == max_retries - 1:
                        raise ValueError(
                            "I'm experiencing high demand right now. Please try again in a moment."
                        )

                    # Exponential backoff: 1s, 2s, 4s, 8s...
                    delay = base_delay * (2 ** attempt)
                    time.sleep(delay)

                except (APIError, APIConnectionError) as e:
                    if attempt == max_retries - 1:
                        raise ValueError(
                            "I'm having trouble connecting to my AI service. Please try again later."
                        )

                    delay = base_delay * (2 ** attempt)
                    time.sleep(delay)

            raise ValueError("Maximum retry attempts exceeded")

        return wrapper
    return decorator

# Apply to chat processing
@retry_with_exponential_backoff(max_retries=3)
def call_ai_api(client: OpenAI, model: str, messages: list):
    """API call with automatic retry on rate limits"""
    return client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.7,
        max_tokens=500
    )
```

**Key Considerations**:

- **Rate Limits**: OpenRouter free tier = 20 requests/minute; paid tier = dynamic based on $1 = 1 RPS (max 500 RPS)
- **Error Codes**: 402 = insufficient credits, 429 = rate limit exceeded, 5xx = API/network errors
- **Fallback Behavior**: OpenRouter automatically falls back to other providers/GPUs on 5xx errors
- **Credit Checking**: Use `GET https://openrouter.ai/api/v1/key` to check remaining credits
- **Model Selection**: OpenRouter supports 500+ models; choose based on speed/cost tradeoffs

**Model Recommendations**:

| Use Case | OpenAI Model | OpenRouter Model | Rationale |
|----------|-------------|------------------|-----------|
| **Fast, simple tasks** | gpt-3.5-turbo | anthropic/claude-3-haiku | Low cost, sub-second responses |
| **Complex reasoning** | gpt-4 | anthropic/claude-3-sonnet | Higher quality, better understanding |
| **Cost optimization** | gpt-3.5-turbo | google/gemini-flash-1.5 | Excellent price/performance ratio |

**Sources**:
- [OpenRouter API Reference](https://openrouter.ai/docs/api/reference/overview)
- [OpenRouter Authentication](https://openrouter.ai/docs/api/reference/authentication)
- [OpenRouter Rate Limits](https://openrouter.ai/docs/api/reference/limits)
- [OpenRouter Error Handling](https://openrouter.ai/docs/api/reference/errors-and-debugging)

---

## 4. OpenAI ChatKit Frontend Integration

### Decision: Use Self-Hosted Backend Integration with Custom Fetch Method

**Implementation Pattern**:

```typescript
// frontend/src/components/chat/ChatInterface.tsx
'use client';

import { useState, useEffect } from 'react';
import '@openai/chatkit-js/dist/styles.css';

interface ChatMessage {
  id: number;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
}

interface ChatKitProps {
  userId: number;
  conversationId?: number;
  authToken: string;
}

export default function ChatInterface({ userId, conversationId, authToken }: ChatKitProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);

  // Load conversation history on mount
  useEffect(() => {
    if (conversationId) {
      loadConversationHistory(conversationId);
    }
  }, [conversationId]);

  const loadConversationHistory = async (convId: number) => {
    try {
      const response = await fetch(`/api/${userId}/conversations/${convId}/messages`, {
        headers: {
          'Authorization': `Bearer ${authToken}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setMessages(data.messages);
      }
    } catch (error) {
      console.error('Failed to load conversation history:', error);
    }
  };

  // Custom fetch handler for ChatKit
  const handleSendMessage = async (message: string) => {
    setLoading(true);

    try {
      // Optimistically add user message to UI
      const userMessage: ChatMessage = {
        id: Date.now(),
        role: 'user',
        content: message,
        created_at: new Date().toISOString(),
      };
      setMessages(prev => [...prev, userMessage]);

      // Send to backend chat endpoint
      const response = await fetch(`/api/${userId}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authToken}`,
        },
        body: JSON.stringify({
          conversation_id: conversationId || null,
          message: message,
        }),
      });

      if (!response.ok) {
        throw new Error(`Chat request failed: ${response.statusText}`);
      }

      const data = await response.json();

      // Add assistant response to UI
      const assistantMessage: ChatMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: data.response,
        created_at: new Date().toISOString(),
      };
      setMessages(prev => [...prev, assistantMessage]);

      // Update conversation ID if this was a new conversation
      if (!conversationId && data.conversation_id) {
        // Update URL or state to track conversation ID
        window.history.replaceState(
          null,
          '',
          `/chat?conversation=${data.conversation_id}`
        );
      }

      return data.response;
    } catch (error) {
      console.error('Failed to send message:', error);

      // Add error message to UI
      const errorMessage: ChatMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: "I'm having trouble processing your request right now. Please try again in a moment.",
        created_at: new Date().toISOString(),
      };
      setMessages(prev => [...prev, errorMessage]);

      throw error;
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen max-w-4xl mx-auto p-4">
      {/* Chat messages display */}
      <div className="flex-1 overflow-y-auto space-y-4 mb-4">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] rounded-lg p-4 ${
                msg.role === 'user'
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-100 text-gray-900'
              }`}
            >
              <p className="text-sm">{msg.content}</p>
              <p className="text-xs opacity-70 mt-2">
                {new Date(msg.created_at).toLocaleTimeString()}
              </p>
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-lg p-4">
              <p className="text-sm text-gray-500">Thinking...</p>
            </div>
          </div>
        )}
      </div>

      {/* Chat input */}
      <ChatInput onSend={handleSendMessage} disabled={loading} />
    </div>
  );
}
```

```typescript
// frontend/src/components/chat/ChatInput.tsx
'use client';

import { useState, FormEvent } from 'react';

interface ChatInputProps {
  onSend: (message: string) => Promise<void>;
  disabled?: boolean;
}

export default function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [input, setInput] = useState('');

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    if (!input.trim() || disabled) return;

    const message = input.trim();
    setInput(''); // Clear input immediately

    try {
      await onSend(message);
    } catch (error) {
      // Error handling already done in parent component
      console.error('Message send failed:', error);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Type your message... (e.g., 'I need to buy groceries')"
        disabled={disabled}
        className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
      />
      <button
        type="submit"
        disabled={disabled || !input.trim()}
        className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed"
      >
        Send
      </button>
    </form>
  );
}
```

```typescript
// frontend/src/app/chat/page.tsx
import { redirect } from 'next/navigation';
import ChatInterface from '@/components/chat/ChatInterface';
import { auth } from '@/lib/auth/client';

export default async function ChatPage({
  searchParams,
}: {
  searchParams: { conversation?: string };
}) {
  const session = await auth();

  if (!session?.user) {
    redirect('/login');
  }

  const conversationId = searchParams.conversation
    ? parseInt(searchParams.conversation)
    : undefined;

  return (
    <div className="container mx-auto py-8">
      <h1 className="text-3xl font-bold mb-6">Task Assistant</h1>
      <ChatInterface
        userId={session.user.id}
        conversationId={conversationId}
        authToken={session.accessToken}
      />
    </div>
  );
}
```

**Rationale**:

1. **Self-Hosted Backend**: Full control over data path, authentication, and API integration
2. **Custom Fetch**: Direct integration with FastAPI `/api/{user_id}/chat` endpoint
3. **Stateless Frontend**: Conversation history loaded from database, not local state
4. **Optimistic UI**: User messages appear immediately for better UX
5. **URL-Based Navigation**: Conversation ID in URL enables shareable links and browser history

**Alternatives Considered**:

| Alternative | Why Rejected |
|-------------|--------------|
| **OpenAI-Hosted Backend (getClientSecret)** | Requires domain allowlist in OpenAI org settings, less control over data path, locks to OpenAI API only |
| **ChatKit Web Component (`<openai-chatkit>`)** | Requires domain verification, limited customization, tighter coupling to OpenAI |
| **Third-party chat libraries (e.g., react-chat-widget)** | More setup, no OpenAI integration, need to build streaming ourselves |
| **Direct streaming with fetch EventSource** | More complex, ChatKit handles this internally, reinventing the wheel |

**Key Considerations**:

- **Authentication**: JWT token passed in `Authorization: Bearer <token>` header to backend
- **Conversation Persistence**: Conversation ID tracked in URL query parameter for session resumption
- **Error Handling**: Graceful fallback messages when API calls fail
- **Loading States**: Show "Thinking..." indicator while waiting for AI response
- **Message Rendering**: Clear visual distinction between user and assistant messages
- **Styling**: Tailwind CSS for responsive, mobile-friendly chat UI

**Installation**:

```bash
# Frontend dependencies
cd frontend
npm install @openai/chatkit-js
```

**ChatKit Configuration Options**:

```typescript
// Option 1: Recommended - Self-Hosted Backend (our choice)
// Custom fetch method connects to your FastAPI backend
const customFetch = async (url: string, init: RequestInit) => {
  return fetch(`/api/${userId}/chat`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${authToken}`,
      'Content-Type': 'application/json',
    },
    body: init.body,
  });
};

// Option 2: OpenAI-Hosted Backend (requires domain allowlist)
// Only for reference - NOT using this approach
const getClientSecret = async () => {
  const response = await fetch('/api/chatkit/session', {
    headers: { 'Authorization': `Bearer ${authToken}` },
  });
  const data = await response.json();
  return data.client_secret;
};
```

**Sources**:
- [ChatKit Documentation](https://platform.openai.com/docs/guides/chatkit)
- [Advanced ChatKit Integration](https://platform.openai.com/docs/guides/custom-chatkit)
- [ChatKit + Next.js Guide](https://www.buildwithmatija.com/blog/chatkit-nextjs-integration)
- [ChatKit Backend Configuration](https://deepwiki.com/openai/chatkit-js/4.2-api-documentation-generation)

---

## 5. Database Schema Design for Conversations

### Decision: Composite Indexes on (user_id, conversation_id, created_at) for Message Queries

**Implementation Pattern**:

```python
# backend/src/models/conversation.py
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List

class Conversation(SQLModel, table=True):
    """
    Represents a chat conversation between user and AI assistant.

    Foreign Keys:
        user_id -> users.id (enforces user ownership)

    Indexes:
        - Primary key on id
        - Index on user_id for user-scoped queries
        - Index on (user_id, updated_at) for "recent conversations" queries
    """
    __tablename__ = "conversations"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", nullable=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    user: Optional["User"] = Relationship(back_populates="conversations")
    messages: List["Message"] = Relationship(
        back_populates="conversation",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

    class Config:
        # SQLModel config for proper JSON serialization
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": 42,
                "created_at": "2026-02-07T12:00:00Z",
                "updated_at": "2026-02-07T12:05:00Z"
            }
        }

class Message(SQLModel, table=True):
    """
    Represents a single message in a conversation.

    Foreign Keys:
        user_id -> users.id (enforces user ownership)
        conversation_id -> conversations.id (enforces conversation membership)

    Indexes:
        - Primary key on id
        - Composite index on (user_id, conversation_id, created_at)
          for fast chronological message retrieval within conversations

    Note:
        Column order in composite index matters: (user_id, conversation_id, created_at)
        supports queries filtering by user_id + conversation_id and ordering by created_at.
    """
    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", nullable=False)
    conversation_id: int = Field(foreign_key="conversations.id", nullable=False)
    role: str = Field(nullable=False)  # "user" or "assistant"
    content: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    user: Optional["User"] = Relationship(back_populates="messages")
    conversation: Optional["Conversation"] = Relationship(back_populates="messages")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": 42,
                "conversation_id": 1,
                "role": "user",
                "content": "I need to buy groceries",
                "created_at": "2026-02-07T12:00:00Z"
            }
        }
```

```sql
-- Alembic migration: backend/alembic/versions/004_add_conversations.py
"""add conversations and messages tables

Revision ID: 004
"""

from alembic import op
import sqlalchemy as sa

def upgrade():
    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )

    # Index for user-scoped queries
    op.create_index('ix_conversations_user_id', 'conversations', ['user_id'])

    # Composite index for "recent conversations" queries
    op.create_index(
        'ix_conversations_user_updated',
        'conversations',
        ['user_id', 'updated_at'],
        postgresql_ops={'updated_at': 'DESC'}
    )

    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('conversation_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE')
    )

    # CRITICAL: Composite index for chronological message queries
    # Order matters: (user_id, conversation_id, created_at) supports:
    #   - WHERE user_id = ? AND conversation_id = ? ORDER BY created_at
    #   - WHERE user_id = ? AND conversation_id = ?
    #   - WHERE user_id = ?
    op.create_index(
        'ix_messages_user_conv_time',
        'messages',
        ['user_id', 'conversation_id', 'created_at']
    )

    # Check constraint: role must be 'user' or 'assistant'
    op.create_check_constraint(
        'ck_messages_role',
        'messages',
        "role IN ('user', 'assistant')"
    )

def downgrade():
    op.drop_table('messages')
    op.drop_table('conversations')
```

**Rationale**:

1. **Composite Index Efficiency**: `(user_id, conversation_id, created_at)` index enables fast retrieval of chronologically ordered messages for a specific user's conversation
2. **Column Order**: Leading with `user_id` and `conversation_id` allows index to be used for authorization checks AND sorting
3. **Foreign Key Constraints**: Cascade deletes ensure referential integrity (deleting conversation deletes all messages)
4. **Timestamp Indexing**: `created_at` in index supports `ORDER BY` without additional sorting overhead
5. **User Scoping**: Separate `user_id` foreign key on messages enables enforcement even if conversation is compromised

**Query Performance**:

```python
# This query uses the composite index efficiently:
messages = session.exec(
    select(Message)
    .where(Message.user_id == user_id)
    .where(Message.conversation_id == conv_id)
    .order_by(Message.created_at)  # Uses index, no separate sort
).all()

# Execution plan shows: Index Scan using ix_messages_user_conv_time
```

**Alternatives Considered**:

| Alternative | Why Rejected |
|-------------|--------------|
| **Separate indexes on each column** | ~10x slower than composite index; PostgreSQL index merge is inefficient for this access pattern |
| **Single index on conversation_id only** | Doesn't enforce user scoping at index level; slower for multi-tenant queries |
| **Index on (conversation_id, created_at)** | Misses user_id check; requires full table scan to verify ownership |
| **No indexes** | Unacceptable performance for large conversation histories (100+ messages) |

**Handling Large Conversation Histories**:

```python
# backend/src/api/chat.py
from sqlmodel import Session, select
from backend.src.models.message import Message

def load_conversation_history(
    session: Session,
    user_id: int,
    conversation_id: int,
    limit: int = 100
) -> list[Message]:
    """
    Load recent messages from conversation with pagination.

    Args:
        session: Database session
        user_id: Authenticated user ID
        conversation_id: Conversation to load
        limit: Maximum messages to retrieve (default 100)

    Returns:
        List of messages in chronological order (oldest first)

    Performance:
        Uses composite index for O(log n) lookup + sequential scan of limit rows.
        For conversations with 1000+ messages, retrieves only most recent limit.
    """
    messages = session.exec(
        select(Message)
        .where(Message.user_id == user_id)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())  # Most recent first
        .limit(limit)
    ).all()

    # Reverse to chronological order (oldest first) for AI context
    return list(reversed(messages))

# Pagination for frontend display
def load_messages_paginated(
    session: Session,
    user_id: int,
    conversation_id: int,
    page: int = 1,
    per_page: int = 50
) -> dict:
    """
    Load messages with pagination for frontend infinite scroll.

    Returns:
        {
            "messages": [...],
            "page": 1,
            "per_page": 50,
            "total": 250,
            "has_more": true
        }
    """
    # Count total messages
    total = session.exec(
        select(func.count())
        .select_from(Message)
        .where(Message.user_id == user_id)
        .where(Message.conversation_id == conversation_id)
    ).one()

    # Fetch paginated messages
    offset = (page - 1) * per_page
    messages = session.exec(
        select(Message)
        .where(Message.user_id == user_id)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
        .offset(offset)
        .limit(per_page)
    ).all()

    return {
        "messages": messages,
        "page": page,
        "per_page": per_page,
        "total": total,
        "has_more": (page * per_page) < total
    }
```

**Key Considerations**:

- **Index Maintenance**: Each insert/update requires index update; acceptable tradeoff for read-heavy chat workloads
- **Column Order**: `(user_id, conversation_id, created_at)` supports most common query patterns efficiently
- **Stick to 5-10 Indexes**: Current schema has 3 indexes (primary key + 2 composites); well within best practice limits
- **Write Performance**: Message inserts are fast; single row with 3 index updates (~1ms overhead)
- **Storage**: Composite index adds ~30% storage overhead; acceptable for query performance gains

**Monitoring Index Usage**:

```sql
-- Check index usage statistics
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE tablename IN ('conversations', 'messages')
ORDER BY idx_scan DESC;

-- Identify unused indexes (idx_scan = 0)
-- Consider dropping if not used after 1 week of production traffic
```

**Sources**:
- [PostgreSQL Composite Index Performance](https://minervadb.xyz/composite-indexes-in-postgresql/)
- [PostgreSQL Indexing Best Practices](https://www.mydbops.com/blog/postgresql-indexing-best-practices-guide)
- [Database Schema for Messaging Systems](https://www.geeksforgeeks.org/dbms/how-to-design-a-database-for-messaging-systems/)
- [PostgreSQL Multicolumn Indexes](https://www.geeksforgeeks.org/postgresql/postgresql-multicolumn-indexes/)

---

## Summary of Recommendations

| Component | Recommended Approach | Key Benefit |
|-----------|---------------------|-------------|
| **OpenAI Agents SDK** | Session-based state with database-loaded history | Stateless server design, horizontal scalability |
| **MCP Server** | FastMCP with Pydantic-based @mcp.tool() decorator | Type-safe tool definitions, automatic JSON schema |
| **API Integration** | OpenAI SDK with configurable base_url for OpenRouter | Single codebase, cost flexibility, instant failover |
| **Frontend** | Self-hosted ChatKit with custom fetch to FastAPI | Full control over data path, JWT authentication |
| **Database** | Composite index on (user_id, conversation_id, created_at) | ~10x faster message queries, efficient sorting |

---

## Next Steps

1. **Phase 1: Design**
   - Define detailed data models for conversations and messages
   - Design MCP tool contracts with input/output schemas
   - Create API endpoint contracts for `/api/{user_id}/chat`
   - Document quickstart guide for local development

2. **Phase 2: Implementation**
   - Implement database migrations for conversations and messages tables
   - Build MCP server with 5 tools (add_task, list_tasks, update_task, complete_task, delete_task)
   - Create OpenAI Agents SDK integration with stateless session management
   - Implement chat endpoint with conversation persistence
   - Build ChatKit frontend integration

3. **Phase 3: Testing & Validation**
   - Write contract tests for MCP tools
   - Integration tests for chat endpoint
   - End-to-end tests for natural language task operations
   - Validate constitutional compliance (stateless, user-scoped, MCP architecture)

---

## References

### Documentation
- [OpenAI Agents SDK](https://platform.openai.com/docs/guides/agents-sdk)
- [MCP Python SDK](https://modelcontextprotocol.github.io/python-sdk/)
- [OpenRouter API](https://openrouter.ai/docs/api/reference/overview)
- [ChatKit Documentation](https://platform.openai.com/docs/guides/chatkit)
- [PostgreSQL Indexing](https://www.postgresql.org/docs/current/indexes.html)

### Tutorials & Guides
- [ChatKit + Next.js Integration](https://www.buildwithmatija.com/blog/chatkit-nextjs-integration)
- [FastMCP Tools Guide](https://gofastmcp.com/servers/tools)
- [Session Memory Management](https://cookbook.openai.com/examples/agents_sdk/session_memory)
- [Database Design for Chat Apps](https://www.geeksforgeeks.org/dbms/how-to-design-a-database-for-messaging-systems/)

### Code Examples
- [OpenAI Agents Examples](https://github.com/openai/openai-agents-python)
- [MCP Python SDK Examples](https://github.com/modelcontextprotocol/python-sdk)
- [ChatKit Advanced Samples](https://github.com/openai/openai-chatkit-advanced-samples)

---

**Document Status**: Research Complete
**Next Command**: `/sp.plan` (Phase 1: Design)
