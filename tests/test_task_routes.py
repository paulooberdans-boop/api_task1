def create_task(client, title="Estudar FastAPI"):
    response = client.post("/tasks", json={"title": title})
    assert response.status_code == 201
    return response.json()


def test_health_check(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_and_list_tasks(client):
    created = create_task(client)

    response = client.get("/tasks")

    assert response.status_code == 200
    assert response.json() == [created]


def test_get_task_by_id(client):
    created = create_task(client)

    response = client.get(f"/tasks/{created['id']}")

    assert response.status_code == 200
    assert response.json() == created


def test_update_task(client):
    created = create_task(client)

    response = client.patch(
        f"/tasks/{created['id']}",
        json={"title": "Estudar SQLAlchemy"},
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Estudar SQLAlchemy"
    assert response.json()["status"] == "pending"


def test_complete_task(client):
    created = create_task(client)

    response = client.patch(
        f"/tasks/{created['id']}",
        json={"status": "completed"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "completed"


def test_filter_tasks_by_status(client):
    pending = create_task(client, "Pendente")
    completed = create_task(client, "Concluida")
    client.patch(f"/tasks/{completed['id']}", json={"status": "completed"})

    completed_response = client.get("/tasks?status=completed")
    pending_response = client.get("/tasks?status=pending")

    assert completed_response.status_code == 200
    assert [task["id"] for task in completed_response.json()] == [completed["id"]]
    assert [task["id"] for task in pending_response.json()] == [pending["id"]]


def test_delete_task(client):
    created = create_task(client)

    response = client.delete(f"/tasks/{created['id']}")

    assert response.status_code == 204
    assert response.content == b""
    assert client.get(f"/tasks/{created['id']}").status_code == 404


def test_missing_task_returns_not_found(client):
    assert client.get("/tasks/999").status_code == 404
    assert client.patch("/tasks/999", json={"status": "completed"}).status_code == 404
    assert client.delete("/tasks/999").status_code == 404


def test_invalid_payload_returns_unprocessable_entity(client):
    assert client.post("/tasks", json={}).status_code == 422
    assert client.post("/tasks", json={"title": "   "}).status_code == 422
    assert client.patch("/tasks/1", json={}).status_code == 422
    assert client.get("/tasks?status=unknown").status_code == 422


def test_task_is_observable_across_requests(client):
    created = create_task(client, "Persistir entre requisicoes")

    first_read = client.get(f"/tasks/{created['id']}")
    second_read = client.get("/tasks")

    assert first_read.status_code == 200
    assert first_read.json()["title"] == "Persistir entre requisicoes"
    assert any(task["id"] == created["id"] for task in second_read.json())