import pytest
from pydantic import ValidationError

from app.models import TaskStatus
from app.schemas import TaskCreate, TaskOut, TaskUpdate


def test_task_create_and_update_schemas():
    create = TaskCreate(title="Estudar Pydantic")
    update = TaskUpdate(status=TaskStatus.COMPLETED)

    assert create.title == "Estudar Pydantic"
    assert update.status == TaskStatus.COMPLETED


def test_task_schemas_reject_invalid_values():
    with pytest.raises(ValidationError):
        TaskCreate(title="   ")
    with pytest.raises(ValidationError):
        TaskUpdate()
    with pytest.raises(ValidationError):
        TaskUpdate(status="unknown")


def test_task_out_is_configured_for_orm_objects():
    assert TaskOut.model_config["from_attributes"] is True
