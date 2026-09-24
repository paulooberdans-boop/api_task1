from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Task, TaskStatus


class TaskRepository:
    """Encapsulate database operations for tasks."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, title: str) -> Task:
        task = Task(title=title)
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def list(self, status_filter: TaskStatus | None = None) -> list[Task]:
        statement = select(Task).order_by(Task.id)
        if status_filter is not None:
            statement = statement.where(Task.status == status_filter)
        return list(self.db.scalars(statement).all())

    def get(self, task_id: int) -> Task | None:
        return self.db.get(Task, task_id)

    def update(self, task: Task, changes: dict[str, object]) -> Task:
        for field, value in changes.items():
            setattr(task, field, value)
        self.db.commit()
        self.db.refresh(task)
        return task

    def delete(self, task: Task) -> None:
        self.db.delete(task)
        self.db.commit()
