from collections.abc import Mapping
from typing import Protocol

from app.models import Task, TaskStatus
from app.services.priority_advisor import PriorityAdvisor, TaskPriority


class TaskNotFoundError(LookupError):
    """Raised when a requested task does not exist."""


class TaskRepositoryPort(Protocol):
    """Persistence operations required by TaskService."""

    def create(self, title: str) -> Task: ...

    def list(self, status_filter: TaskStatus | None = None) -> list[Task]: ...

    def get_by_id(self, task_id: int) -> Task | None: ...

    def update(self, task: Task, changes: dict[str, object]) -> Task: ...

    def delete(self, task: Task) -> None: ...


class PriorityAdvisorPort(Protocol):
    """Priority suggestion contract accepted by the application service."""

    def suggest_priority(self, text: str) -> TaskPriority: ...


class TaskService:
    """Coordinate task use cases independently of HTTP and database details."""

    def __init__(
        self,
        repository: TaskRepositoryPort,
        priority_advisor: PriorityAdvisorPort | None = None,
    ):
        self.repository = repository
        self.priority_advisor = priority_advisor

    def create(self, title: str) -> Task:
        return self.repository.create(title)

    def list(self, status_filter: TaskStatus | None = None) -> list[Task]:
        return self.repository.list(status_filter)

    def get_by_id(self, task_id: int) -> Task:
        task = self.repository.get_by_id(task_id)
        if task is None:
            raise TaskNotFoundError(task_id)
        return task

    def update(self, task_id: int, changes: Mapping[str, object]) -> Task:
        task = self.get_by_id(task_id)
        return self.repository.update(task, dict(changes))

    def delete(self, task_id: int) -> None:
        task = self.get_by_id(task_id)
        self.repository.delete(task)

    def suggest_priority(self, text: str) -> TaskPriority:
        advisor = self.priority_advisor or PriorityAdvisor()
        return advisor.suggest_priority(text)
