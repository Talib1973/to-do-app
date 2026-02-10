"""AI agent handler using OpenAI SDK for natural language task management."""

import os
from typing import List, Dict, Any
from openai import OpenAI
from .tools import add_task, list_tasks, complete_task, update_task, delete_task


# System prompt for task management chatbot
SYSTEM_PROMPT = """You are a helpful task management assistant. Users will ask you to create, view, update, complete, or delete tasks using natural language.

You have 5 tools available:
- add_task: Create a new task (parameters: user_id, title, description)
- list_tasks: View tasks (parameters: user_id, status: "all"|"pending"|"completed")
- update_task: Change a task's title or description (parameters: user_id, task_id, title, description)
- complete_task: Mark a task as done (parameters: user_id, task_id)
- delete_task: Remove a task (parameters: user_id, task_id)

**Examples of natural language commands:**
- "I need to buy groceries" → add_task(user_id, "Buy groceries", "")
- "Show me my tasks" → list_tasks(user_id, "all")
- "What's pending?" → list_tasks(user_id, "pending")
- "Mark task 3 as done" → complete_task(user_id, task_id)
- "I'm done with buying groceries" → list_tasks to find task → complete_task
- "Change task 1 to 'Call mom at 6pm'" → update_task(user_id, task_id, "Call mom at 6pm")
- "Delete the meeting task" → list_tasks to find task → delete_task

**Guidelines:**
1. Interpret user requests naturally - they won't use technical commands
2. If a request is unclear or ambiguous, ask clarifying questions
3. Always confirm task operations with friendly, conversational responses
4. When users reference tasks by description (e.g., "the grocery task"), use list_tasks first to find the matching task ID
5. Only help with task management - politely redirect other requests

**Important:**
- Always use the user_id parameter from the conversation context (never ask users for their ID)
- Format responses conversationally (not as raw JSON)
- Confirm successful operations with friendly messages
"""


def get_openai_client() -> OpenAI:
    """
    Get configured OpenAI client with support for OpenRouter.

    Returns:
        OpenAI: Configured client for OpenAI or OpenRouter API
    """
    ai_provider = os.getenv("AI_PROVIDER", "openrouter").lower()
    api_key = os.getenv("OPENROUTER_API_KEY") if ai_provider == "openrouter" else os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError(f"API key not found for provider: {ai_provider}")

    # Configure client based on provider
    if ai_provider == "openrouter":
        return OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )
    else:
        return OpenAI(api_key=api_key)


def run_agent(
    user_id: str,
    user_message: str,
    conversation_history: List[Dict[str, str]]
) -> Dict[str, Any]:
    """
    Run AI agent to process user message and execute MCP tools.

    This is a stateless agent - conversation history is loaded from database per request.
    Agent interprets natural language and calls appropriate MCP tools.

    Args:
        user_id: UUID of authenticated user (for tool authorization)
        user_message: Latest message from user
        conversation_history: List of prior messages [{role: "user"|"assistant", content: "..."}]

    Returns:
        dict: {
            "content": str (assistant's response),
            "tool_calls": List[dict] (tools invoked with parameters and results)
        }

    Example:
        >>> run_agent(
        ...     user_id="123e4567-e89b-12d3-a456-426614174000",
        ...     user_message="I need to buy groceries",
        ...     conversation_history=[]
        ... )
        {
            "content": "I've added 'Buy groceries' to your task list. Would you like to add any details?",
            "tool_calls": [{
                "tool": "add_task",
                "parameters": {"user_id": "...", "title": "Buy groceries", "description": ""},
                "result": {"status": "success", "data": {...}}
            }]
        }
    """
    try:
        # Get OpenAI client (supports OpenRouter)
        client = get_openai_client()
        model = os.getenv("AI_MODEL", "anthropic/claude-3.5-haiku")

        # Build messages array
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        # Add conversation history
        messages.extend(conversation_history)

        # Add current user message
        messages.append({"role": "user", "content": user_message})

        # Define tools in OpenAI function calling format
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "add_task",
                    "description": "Create a new task for the user",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Task title"
                            },
                            "description": {
                                "type": "string",
                                "description": "Task description (optional)"
                            }
                        },
                        "required": ["title"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_tasks",
                    "description": "Retrieve user's tasks with optional status filter",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "status": {
                                "type": "string",
                                "enum": ["all", "pending", "completed"],
                                "description": "Filter by completion status"
                            }
                        },
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "complete_task",
                    "description": "Mark a task as completed",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "string",
                                "description": "UUID of the task to mark complete"
                            }
                        },
                        "required": ["task_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "update_task",
                    "description": "Update a task's title or description",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "string",
                                "description": "UUID of the task to update"
                            },
                            "title": {
                                "type": "string",
                                "description": "New title (optional)"
                            },
                            "description": {
                                "type": "string",
                                "description": "New description (optional)"
                            }
                        },
                        "required": ["task_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_task",
                    "description": "Delete a task permanently",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "string",
                                "description": "UUID of the task to delete"
                            }
                        },
                        "required": ["task_id"]
                    }
                }
            }
        ]

        # Call OpenAI API with tools
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        # Track tool calls
        tool_calls_log = []

        # Check if agent wants to call tools
        message = response.choices[0].message

        if message.tool_calls:
            # Execute tool calls
            for tool_call in message.tool_calls:
                function_name = tool_call.function.name
                import json
                function_args = json.loads(tool_call.function.arguments)

                # Add user_id to all tool calls (agent doesn't have access to this)
                function_args["user_id"] = user_id

                # Call the appropriate tool
                if function_name == "add_task":
                    result = add_task(**function_args)
                elif function_name == "list_tasks":
                    result = list_tasks(**function_args)
                elif function_name == "complete_task":
                    result = complete_task(**function_args)
                elif function_name == "update_task":
                    result = update_task(**function_args)
                elif function_name == "delete_task":
                    result = delete_task(**function_args)
                else:
                    result = {"status": "error", "data": None, "error": f"Unknown tool: {function_name}"}

                # Log tool call
                tool_calls_log.append({
                    "tool": function_name,
                    "parameters": function_args,
                    "result": result
                })

                # Add tool result to conversation for agent to formulate response
                messages.append({
                    "role": "assistant",
                    "content": message.content or "",
                    "tool_calls": [
                        {
                            "id": tool_call.id,
                            "type": "function",
                            "function": {
                                "name": function_name,
                                "arguments": tool_call.function.arguments
                            }
                        }
                    ]
                })
                messages.append({
                    "role": "tool",
                    "content": json.dumps(result),
                    "tool_call_id": tool_call.id
                })

            # Get final response from agent after tool execution
            final_response = client.chat.completions.create(
                model=model,
                messages=messages
            )
            final_content = final_response.choices[0].message.content
        else:
            # No tools called, use direct response
            final_content = message.content

        return {
            "content": final_content or "I'm here to help you manage your tasks. What would you like to do?",
            "tool_calls": tool_calls_log
        }

    except Exception as e:
        # Return error response
        return {
            "content": f"I'm having trouble processing your request right now. Please try again in a moment. (Error: {str(e)})",
            "tool_calls": []
        }
