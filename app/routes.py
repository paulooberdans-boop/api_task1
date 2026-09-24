from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Task, TaskStatus
from app.repositories.tasks import TaskRepository
from app.schemas import TaskCreate, TaskOut, TaskUpdate
from app.services.task_service import TaskNotFoundError, TaskService


router = APIRouter(prefix="/tasks", tags=["tasks"])


def get_task_service(db: Session = Depends(get_db)) -> TaskService:
    return TaskService(TaskRepository(db))


@router.post("", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(
    payload: TaskCreate, service: TaskService = Depends(get_task_service)
) -> Task:
    """Create a pending task."""
    return service.create(payload.title)


@router.get("", response_model=list[TaskOut])
def list_tasks(
    status_filter: TaskStatus | None = Query(default=None, alias="status"),
    service: TaskService = Depends(get_task_service),
) -> list[Task]:
    """List tasks, optionally filtered by status."""
    return service.list(status_filter)


@router.get("/{task_id}", response_model=TaskOut)
def get_task(
    task_id: int, service: TaskService = Depends(get_task_service)
) -> Task:
    """Return a task by ID."""
    try:
        return service.get_by_id(task_id)
    except TaskNotFoundError as error:
        raise HTTPException(status_code=404, detail="Task not found") from error


@router.patch("/{task_id}", response_model=TaskOut)
def update_task(
    task_id: int,
    payload: TaskUpdate,
    service: TaskService = Depends(get_task_service),
) -> Task:
    """Update a task title, status, or both."""
    try:
        return service.update(task_id, payload.model_dump(exclude_unset=True))
    except TaskNotFoundError as error:
        raise HTTPException(status_code=404, detail="Task not found") from error


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int, service: TaskService = Depends(get_task_service)
) -> None:
    """Delete a task by ID."""
    try:
        service.delete(task_id)
    except TaskNotFoundError as error:
        raise HTTPException(status_code=404, detail="Task not found") from error
