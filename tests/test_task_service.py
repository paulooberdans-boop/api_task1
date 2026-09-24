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


@pytest.fixture()
def repository():
    return FakeTaskRepository()


@pytest.fixture()
def service(repository):
    return TaskService(repository)


def test_service_creates_task(service):
    task = service.create("Nova tarefa")

    assert task.title == "Nova tarefa"
    assert task.status == TaskStatus.PENDING


def test_service_lists_tasks(service):
    service.create("Primeira")
    service.create("Segunda")

    tasks = service.list()

    assert [task.title for task in tasks] == ["Primeira", "Segunda"]


def test_service_gets_task_by_id(service):
    created = service.create("Consultar")

    task = service.get_by_id(created.id)

    assert task is created


def test_service_updates_task(service):
    task = service.create("Antes")

    updated = service.update(task.id, {"title": "Depois"})

    assert updated.title == "Depois"


def test_service_marks_task_as_completed(service):
    task = service.create("Concluir")

    completed = service.update(task.id, {"status": TaskStatus.COMPLETED})

    assert completed.status == TaskStatus.COMPLETED


def test_service_filters_tasks_by_status(service):
    pending = service.create("Pendente")
    completed = service.create("Concluida")
    service.update(completed.id, {"status": TaskStatus.COMPLETED})

    tasks = service.list(TaskStatus.COMPLETED)

    assert tasks == [completed]
    assert tasks != [pending]


def test_service_deletes_task(service):
    task = service.create("Excluir")

    service.delete(task.id)

    with pytest.raises(TaskNotFoundError):
        service.get_by_id(task.id)


def test_service_raises_domain_error_for_missing_task(service):
    with pytest.raises(TaskNotFoundError):
        service.get_by_id(999)

    with pytest.raises(TaskNotFoundError):
        service.update(999, {"status": TaskStatus.COMPLETED})

    with pytest.raises(TaskNotFoundError):
        service.delete(999)

def test_service_accepts_optional_priority_advisor(repository):
    class FakeAdvisor:
        def suggest_priority(self, _):
            return TaskPriority.HIGH

    service = TaskService(repository, priority_advisor=FakeAdvisor())

    assert service.suggest_priority("Qualquer tarefa") == TaskPriority.HIGH
