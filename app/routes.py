from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Task, TaskStatus
from app.repositories.tasks import TaskRepository
from app.schemas import TaskCreate, TaskRead, TaskUpdate


router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)) -> Task:
    """Create a pending task."""
    return TaskRepository(db).create(payload.title)


@router.get("", response_model=list[TaskRead])
def list_tasks(
    status_filter: TaskStatus | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
) -> list[Task]:
    """List tasks, optionally filtered by status."""
    return TaskRepository(db).list(status_filter)


@router.get("/{task_id}", response_model=TaskRead)
def get_task(task_id: int, db: Session = Depends(get_db)) -> Task:
    """Return a task by ID."""
    task = TaskRepository(db).get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch("/{task_id}", response_model=TaskRead)
def update_task(
    task_id: int, payload: TaskUpdate, db: Session = Depends(get_db)
) -> Task:
    """Update a task title, status, or both."""
    repository = TaskRepository(db)
    task = repository.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return repository.update(task, payload.model_dump(exclude_unset=True))


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db)) -> None:
    """Delete a task by ID."""
    repository = TaskRepository(db)
    task = repository.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    repository.delete(task)
