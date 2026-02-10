"""MCP tools for task operations - AI agent interface to task management."""

from typing import Dict, Any, List, Optional
from uuid import UUID
from sqlmodel import Session, select
from src.models.task import Task
from src.database import engine


def add_task(user_id: str, title: str, description: str = "") -> Dict[str, Any]:
    """
    Create a new task for the authenticated user.

    MCP Tool: add_task
    Purpose: Allows AI agent to create tasks based on natural language commands.

    Args:
        user_id: UUID of the task owner (from JWT, enforces user scoping)
        title: Task title (1-200 characters)
        description: Task description (optional, 0-1000 characters)

    Returns:
        dict: {status: "success"|"error", data: task_dict|None, error: error_msg|None}

    Examples:
        User: "I need to buy groceries tomorrow"
        Agent calls: add_task(user_id, "Buy groceries tomorrow", "")
        Returns: {status: "success", data: {id: ..., title: "Buy groceries tomorrow", ...}, error: None}
    """
    try:
        # Validate inputs
        if not title or not title.strip():
            return {
                "status": "error",
                "data": None,
                "error": "Title is required and cannot be empty"
            }

        if len(title) > 200:
            return {
                "status": "error",
                "data": None,
                "error": "Title must be 200 characters or less"
            }

        # Convert user_id string to UUID
        try:
            user_uuid = UUID(user_id)
        except ValueError:
            return {
                "status": "error",
                "data": None,
                "error": "Invalid user ID format"
            }

        # Create task in database
        with Session(engine) as session:
            task = Task(
                user_id=user_uuid,
                title=title.strip(),
                description=description.strip() if description else "",
                completed=False
            )
            session.add(task)
            session.commit()
            session.refresh(task)

            # Return task data
            return {
                "status": "success",
                "data": {
                    "id": str(task.id),
                    "user_id": str(task.user_id),
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat()
                },
                "error": None
            }

    except Exception as e:
        return {
            "status": "error",
            "data": None,
            "error": f"An error occurred while creating the task: {str(e)}"
        }


def list_tasks(user_id: str, status: str = "all") -> Dict[str, Any]:
    """
    Retrieve tasks for the authenticated user, optionally filtered by completion status.

    MCP Tool: list_tasks
    Purpose: Allows AI agent to query user's tasks based on natural language queries.

    Args:
        user_id: UUID of the task owner (from JWT, enforces user scoping)
        status: Filter by completion status ("all"|"pending"|"completed")

    Returns:
        dict: {status: "success"|"error", data: [task_dicts]|None, error: error_msg|None}

    Examples:
        User: "Show me my pending tasks"
        Agent calls: list_tasks(user_id, "pending")
        Returns: {status: "success", data: [{id: ..., title: "Buy groceries", completed: False}, ...], error: None}

        User: "What have I finished?"
        Agent calls: list_tasks(user_id, "completed")
        Returns: {status: "success", data: [{id: ..., title: "Old task", completed: True}, ...], error: None}
    """
    try:
        # Validate status parameter
        if status not in ("all", "pending", "completed"):
            return {
                "status": "error",
                "data": None,
                "error": "Status must be 'all', 'pending', or 'completed'"
            }

        # Convert user_id string to UUID
        try:
            user_uuid = UUID(user_id)
        except ValueError:
            return {
                "status": "error",
                "data": None,
                "error": "Invalid user ID format"
            }

        # Query tasks with user scoping
        with Session(engine) as session:
            query = select(Task).where(Task.user_id == user_uuid)

            # Apply status filter
            if status == "pending":
                query = query.where(Task.completed == False)
            elif status == "completed":
                query = query.where(Task.completed == True)

            # Execute query and order by creation date
            query = query.order_by(Task.created_at.desc())
            tasks = session.exec(query).all()

            # Convert tasks to dictionaries
            tasks_data = [
                {
                    "id": str(task.id),
                    "user_id": str(task.user_id),
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat()
                }
                for task in tasks
            ]

            return {
                "status": "success",
                "data": tasks_data,
                "error": None
            }

    except Exception as e:
        return {
            "status": "error",
            "data": None,
            "error": f"An error occurred while retrieving tasks: {str(e)}"
        }


def complete_task(user_id: str, task_id: str) -> Dict[str, Any]:
    """
    Mark a task as completed.

    MCP Tool: complete_task
    Purpose: Allows AI agent to mark tasks complete via natural language.

    Args:
        user_id: UUID of the task owner (enforces user scoping)
        task_id: UUID of the task to mark complete

    Returns:
        dict: {status: "success"|"error", data: task_dict|None, error: error_msg|None}
    """
    try:
        user_uuid = UUID(user_id)
        task_uuid = UUID(task_id)
    except ValueError:
        return {
            "status": "error",
            "data": None,
            "error": "Invalid user ID or task ID format"
        }

    try:
        with Session(engine) as session:
            # Query task with user scoping
            task = session.exec(
                select(Task).where(Task.id == task_uuid, Task.user_id == user_uuid)
            ).first()

            if not task:
                return {
                    "status": "error",
                    "data": None,
                    "error": "Task not found or does not belong to user"
                }

            # Mark as complete
            task.completed = True
            session.add(task)
            session.commit()
            session.refresh(task)

            return {
                "status": "success",
                "data": {
                    "id": str(task.id),
                    "user_id": str(task.user_id),
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat()
                },
                "error": None
            }

    except Exception as e:
        return {
            "status": "error",
            "data": None,
            "error": f"An error occurred while completing the task: {str(e)}"
        }


def update_task(user_id: str, task_id: str, title: Optional[str] = None, description: Optional[str] = None) -> Dict[str, Any]:
    """
    Modify an existing task's title or description.

    MCP Tool: update_task
    Purpose: Allows AI agent to update task details via natural language.

    Args:
        user_id: UUID of the task owner (enforces user scoping)
        task_id: UUID of the task to update
        title: New title (optional, 1-200 characters)
        description: New description (optional, 0-1000 characters)

    Returns:
        dict: {status: "success"|"error", data: task_dict|None, error: error_msg|None}
    """
    try:
        user_uuid = UUID(user_id)
        task_uuid = UUID(task_id)
    except ValueError:
        return {
            "status": "error",
            "data": None,
            "error": "Invalid user ID or task ID format"
        }

    if not title and description is None:
        return {
            "status": "error",
            "data": None,
            "error": "At least one field (title or description) must be provided"
        }

    try:
        with Session(engine) as session:
            task = session.exec(
                select(Task).where(Task.id == task_uuid, Task.user_id == user_uuid)
            ).first()

            if not task:
                return {
                    "status": "error",
                    "data": None,
                    "error": "Task not found or does not belong to user"
                }

            # Update fields
            if title:
                task.title = title.strip()
            if description is not None:
                task.description = description.strip()

            session.add(task)
            session.commit()
            session.refresh(task)

            return {
                "status": "success",
                "data": {
                    "id": str(task.id),
                    "user_id": str(task.user_id),
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat()
                },
                "error": None
            }

    except Exception as e:
        return {
            "status": "error",
            "data": None,
            "error": f"An error occurred while updating the task: {str(e)}"
        }


def delete_task(user_id: str, task_id: str) -> Dict[str, Any]:
    """
    Permanently remove a task from the user's task list.

    MCP Tool: delete_task
    Purpose: Allows AI agent to delete tasks via natural language.

    Args:
        user_id: UUID of the task owner (enforces user scoping)
        task_id: UUID of the task to delete

    Returns:
        dict: {status: "success"|"error", data: {id, deleted}|None, error: error_msg|None}
    """
    try:
        user_uuid = UUID(user_id)
        task_uuid = UUID(task_id)
    except ValueError:
        return {
            "status": "error",
            "data": None,
            "error": "Invalid user ID or task ID format"
        }

    try:
        with Session(engine) as session:
            task = session.exec(
                select(Task).where(Task.id == task_uuid, Task.user_id == user_uuid)
            ).first()

            if not task:
                return {
                    "status": "error",
                    "data": None,
                    "error": "Task not found or does not belong to user"
                }

            session.delete(task)
            session.commit()

            return {
                "status": "success",
                "data": {
                    "id": str(task_uuid),
                    "deleted": True
                },
                "error": None
            }

    except Exception as e:
        return {
            "status": "error",
            "data": None,
            "error": f"An error occurred while deleting the task: {str(e)}"
        }
