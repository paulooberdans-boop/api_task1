def create_task(client, title="Estudar FastAPI"):
    response = client.post("/tasks", json={"title": title})
    assert response.status_code == 201
    return response.json()


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_and_list_tasks(client):
    task = create_task(client)
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == [task]
    assert task["status"] == "pending"


def test_get_task_by_id(client):
    task = create_task(client)
    response = client.get(f"/tasks/{task['id']}")
    assert response.status_code == 200
    assert response.json()["title"] == task["title"]


def test_update_and_complete_task(client):
    task = create_task(client)
    response = client.patch(
        f"/tasks/{task['id']}",
        json={"title": "Estudar SQLAlchemy", "status": "completed"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "completed"
    assert response.json()["title"] == "Estudar SQLAlchemy"


def test_filter_tasks_by_status(client):
    pending = create_task(client, "Pendente")
    completed = create_task(client, "Concluida")
    client.patch(f"/tasks/{completed['id']}", json={"status": "completed"})

    response = client.get("/tasks?status=completed")
    assert response.status_code == 200
    assert [task["id"] for task in response.json()] == [completed["id"]]

    response = client.get("/tasks?status=pending")
    assert [task["id"] for task in response.json()] == [pending["id"]]


def test_delete_task(client):
    task = create_task(client)
    response = client.delete(f"/tasks/{task['id']}")
    assert response.status_code == 204
    assert client.get(f"/tasks/{task['id']}").status_code == 404


def test_not_found_and_invalid_payload(client):
    assert client.get("/tasks/999").status_code == 404
    assert client.patch("/tasks/999", json={"status": "completed"}).status_code == 404
    assert client.post("/tasks", json={"title": ""}).status_code == 422
    assert client.post("/tasks", json={}).status_code == 422
    assert client.get("/tasks?status=unknown").status_code == 422


def test_data_persists_in_database(client):
    task = create_task(client, "Persistir")
    assert client.get(f"/tasks/{task['id']}").json()["title"] == "Persistir"
