import pytest

from app.models import Task, TaskStatus
from app.services.priority_advisor import TaskPriority
from app.services.task_service import TaskNotFoundError, TaskService


class FakeTaskRepository:
    def __init__(self):
        self.tasks = {}
        self.next_id = 1

    def create(self, title):
        task = Task(id=self.next_id, title=title, status=TaskStatus.PENDING)
        self.tasks[task.id] = task
        self.next_id += 1
        return task

    def list(self, status_filter=None):
        tasks = list(self.tasks.values())
        if status_filter is not None:
            tasks = [task for task in tasks if task.status == status_filter]
        return tasks

    def get_by_id(self, task_id):
        return self.tasks.get(task_id)

    def update(self, task, changes):
        for field, value in changes.items():
            setattr(task, field, value)
        return task

    def delete(self, task):
        del self.tasks[task.id]


def test_service_coordinates_crud_completion_and_filter():
    service = TaskService(FakeTaskRepository())
    pending = service.create("Pendente")
    completed = service.create("Concluida")

    service.update(completed.id, {"status": TaskStatus.COMPLETED})

    assert service.get_by_id(pending.id).title == "Pendente"
    assert service.list(TaskStatus.COMPLETED) == [completed]

    service.update(pending.id, {"title": "Atualizada"})
    assert service.get_by_id(pending.id).title == "Atualizada"

    service.delete(pending.id)
    with pytest.raises(TaskNotFoundError):
        service.get_by_id(pending.id)


def test_service_raises_domain_error_for_missing_task():
    service = TaskService(FakeTaskRepository())

    with pytest.raises(TaskNotFoundError):
        service.update(999, {"status": TaskStatus.COMPLETED})
    with pytest.raises(TaskNotFoundError):
        service.delete(999)


def test_service_accepts_optional_priority_advisor():
    class FakeAdvisor:
        def suggest_priority(self, _):
            return TaskPriority.HIGH

    service = TaskService(FakeTaskRepository(), priority_advisor=FakeAdvisor())

    assert service.suggest_priority("Qualquer tarefa") == TaskPriority.HIGH
