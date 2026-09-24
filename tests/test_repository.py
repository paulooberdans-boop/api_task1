from app.models import TaskStatus
from app.repositories.tasks import TaskRepository


def test_repository_crud_and_status_filter(db_session):
    repository = TaskRepository(db_session)

    pending = repository.create("Tarefa pendente")
    completed = repository.create("Tarefa concluida")
    repository.update(completed, {"status": TaskStatus.COMPLETED})

    assert repository.get_by_id(pending.id).title == "Tarefa pendente"
    assert repository.get_by_id(999) is None
    assert repository.list(TaskStatus.PENDING) == [pending]
    assert repository.list(TaskStatus.COMPLETED) == [completed]

    repository.update(pending, {"title": "Tarefa atualizada"})
    assert repository.get_by_id(pending.id).title == "Tarefa atualizada"

    repository.delete(pending)
    assert repository.get_by_id(pending.id) is None


def test_repository_data_survives_new_session(test_engine, db_session):
    repository = TaskRepository(db_session)
    task = repository.create("Persistir entre sessoes")
    db_session.close()

    from sqlalchemy.orm import Session

    with Session(test_engine) as new_session:
        persisted = TaskRepository(new_session).get_by_id(task.id)
        assert persisted is not None
        assert persisted.status == TaskStatus.PENDING
