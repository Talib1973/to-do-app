"""Task management API endpoints."""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select

from src.database import get_session
from src.models.task import Task
from src.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskPatch,
    TaskResponse
)
from src.auth.jwt import get_current_user_id

router = APIRouter()


@router.post(
    "/",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
    description="Create a new task for the authenticated user."
)
def create_task(
    task_data: TaskCreate,
    user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> TaskResponse:
    """
    Create a new task.

    - **title**: Task title (required, max 500 chars)
    - **description**: Task description (optional, max 5000 chars)
    - **completed**: Completion status (optional, default: false)

    User ID is automatically set from JWT token (cannot be overridden).

    Returns the created task with generated ID and timestamps.
    """
    # Create task with user_id from JWT (ignore any user_id in request body)
    new_task = Task(
        user_id=UUID(user_id),
        title=task_data.title,
        description=task_data.description,
        completed=task_data.completed
    )

    session.add(new_task)
    session.commit()
    session.refresh(new_task)

    return TaskResponse.from_orm(new_task)


@router.get(
    "/",
    response_model=list[TaskResponse],
    status_code=status.HTTP_200_OK,
    summary="List all tasks for authenticated user",
    description="Retrieve all tasks belonging to the authenticated user, optionally filtered by completion status."
)
def list_tasks(
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> list[TaskResponse]:
    """
    List all tasks for the authenticated user.

    - **completed**: Optional filter (true/false)

    Returns array of tasks (empty array if no tasks).
    Only returns tasks owned by the authenticated user.
    """
    # Build query filtered by user_id
    query = select(Task).where(Task.user_id == UUID(user_id))

    # Add completion filter if provided
    if completed is not None:
        query = query.where(Task.completed == completed)

    tasks = session.exec(query).all()
    return [TaskResponse.from_orm(task) for task in tasks]


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a single task",
    description="Retrieve a specific task by ID. Must be owned by authenticated user."
)
def get_task(
    task_id: UUID,
    user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> TaskResponse:
    """
    Get a single task by ID.

    - **task_id**: Task UUID

    Returns task if it exists and belongs to authenticated user.

    Raises:
        404: Task not found
        403: Task belongs to different user
    """
    task = session.get(Task, task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )

    # Check ownership
    if str(task.user_id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this task"
        )

    return TaskResponse.from_orm(task)


@router.put(
    "/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a task (full replacement)",
    description="Replace all task fields. Must be owned by authenticated user."
)
def update_task(
    task_id: UUID,
    task_data: TaskUpdate,
    user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> TaskResponse:
    """
    Update a task (full replacement).

    - **title**: New title (required)
    - **description**: New description (optional)
    - **completed**: New completion status (optional)

    User ID cannot be modified (immutable).

    Returns updated task.

    Raises:
        404: Task not found
        403: Task belongs to different user
        400: Attempt to modify user_id
    """
    task = session.get(Task, task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )

    # Check ownership
    if str(task.user_id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to modify this task"
        )

    # Update fields (user_id is immutable)
    task.title = task_data.title
    task.description = task_data.description
    task.completed = task_data.completed

    session.add(task)
    session.commit()
    session.refresh(task)

    return TaskResponse.from_orm(task)


@router.patch(
    "/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a task (partial update)",
    description="Update specific task fields. Must be owned by authenticated user."
)
def patch_task(
    task_id: UUID,
    task_data: TaskPatch,
    user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> TaskResponse:
    """
    Update a task (partial update).

    Only provided fields are updated. Other fields remain unchanged.

    - **title**: Update title (optional)
    - **description**: Update description (optional)
    - **completed**: Update completion status (optional)

    User ID cannot be modified (immutable).

    Returns updated task.

    Raises:
        404: Task not found
        403: Task belongs to different user
    """
    task = session.get(Task, task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )

    # Check ownership
    if str(task.user_id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to modify this task"
        )

    # Update only provided fields
    update_data = task_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)

    session.add(task)
    session.commit()
    session.refresh(task)

    return TaskResponse.from_orm(task)


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task",
    description="Permanently delete a task. Must be owned by authenticated user."
)
def delete_task(
    task_id: UUID,
    user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> None:
    """
    Delete a task permanently.

    - **task_id**: Task UUID

    Returns 204 No Content on success.

    Raises:
        404: Task not found
        403: Task belongs to different user
    """
    task = session.get(Task, task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )

    # Check ownership
    if str(task.user_id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this task"
        )

    session.delete(task)
    session.commit()

    return None
