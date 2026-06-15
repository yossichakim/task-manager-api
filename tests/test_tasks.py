def test_create_task(client, auth_headers):
    response = client.post(
        "/tasks",
        headers=auth_headers,
        json={
            "title": "Learn pytest",
            "description": "Write automated tests",
            "category": "study"
        }
    )

    data = response.get_json()

    assert response.status_code == 201
    assert data["title"] == "Learn pytest"
    assert data["description"] == "Write automated tests"
    assert data["category"] == "study"
    assert data["status"] == "pending"
    assert "id" in data


def test_create_task_without_title(client, auth_headers):
    response = client.post(
        "/tasks",
        headers=auth_headers,
        json={
            "description": "Missing title"
        }
    )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "Title is required"
    }

def test_get_all_tasks(client, auth_headers):
    client.post(
        "/tasks",
        headers=auth_headers,
        json={
            "title": "First task",
            "category": "work"
        }
    )

    client.post(
        "/tasks",
        headers=auth_headers,
        json={
            "title": "Second task",
            "category": "personal"
        }
    )

    response = client.get(
        "/tasks",
        headers=auth_headers
    )

    data = response.get_json()

    assert response.status_code == 200
    assert len(data) == 2
    assert data[0]["title"] == "First task"
    assert data[1]["title"] == "Second task"


def test_get_task_by_id(client, auth_headers):
    create_response = client.post(
        "/tasks",
        headers=auth_headers,
        json={
            "title": "Specific task"
        }
    )

    task_id = create_response.get_json()["id"]

    response = client.get(
        f"/tasks/{task_id}",
        headers=auth_headers
    )

    data = response.get_json()

    assert response.status_code == 200
    assert data["id"] == task_id
    assert data["title"] == "Specific task"


def test_get_nonexistent_task(client, auth_headers):
    response = client.get(
        "/tasks/9999",
        headers=auth_headers
    )

    assert response.status_code == 404
    assert response.get_json() == {
        "error": "Task not found"
    }


def test_update_task(client, auth_headers):
    create_response = client.post(
        "/tasks",
        headers=auth_headers,
        json={
            "title": "Old title",
            "category": "work"
        }
    )

    task_id = create_response.get_json()["id"]

    response = client.put(
        f"/tasks/{task_id}",
        headers=auth_headers,
        json={
            "title": "New title",
            "status": "completed"
        }
    )

    data = response.get_json()

    assert response.status_code == 200
    assert data["title"] == "New title"
    assert data["status"] == "completed"
    assert data["category"] == "work"


def test_update_task_with_invalid_status(client, auth_headers):
    create_response = client.post(
        "/tasks",
        headers=auth_headers,
        json={
            "title": "Test task"
        }
    )

    task_id = create_response.get_json()["id"]

    response = client.put(
        f"/tasks/{task_id}",
        headers=auth_headers,
        json={
            "status": "in-progress"
        }
    )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": (
            "Status must be either "
            "'pending' or 'completed'"
        )
    }

def test_delete_task(client, auth_headers):
    create_response = client.post(
        "/tasks",
        headers=auth_headers,
        json={
            "title": "Task to delete"
        }
    )

    task_id = create_response.get_json()["id"]

    delete_response = client.delete(
        f"/tasks/{task_id}",
        headers=auth_headers
    )

    get_response = client.get(
        f"/tasks/{task_id}",
        headers=auth_headers
    )

    assert delete_response.status_code == 200
    assert delete_response.get_json() == {
        "message": "Task deleted successfully"
    }

    assert get_response.status_code == 404


def test_filter_tasks_by_category(client, auth_headers):
    client.post(
        "/tasks",
        headers=auth_headers,
        json={
            "title": "Work task",
            "category": "work"
        }
    )

    client.post(
        "/tasks",
        headers=auth_headers,
        json={
            "title": "Personal task",
            "category": "personal"
        }
    )

    response = client.get(
        "/tasks?category=work",
        headers=auth_headers
    )

    data = response.get_json()

    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]["category"] == "work"


def test_user_cannot_access_another_users_task(client):
    client.post(
        "/register",
        json={
            "username": "firstuser",
            "password": "123456"
        }
    )

    first_login = client.post(
        "/login",
        json={
            "username": "firstuser",
            "password": "123456"
        }
    )

    first_headers = {
        "Authorization": (
            f"Bearer "
            f"{first_login.get_json()['access_token']}"
        )
    }

    create_response = client.post(
        "/tasks",
        headers=first_headers,
        json={
            "title": "Private task"
        }
    )

    task_id = create_response.get_json()["id"]

    client.post(
        "/register",
        json={
            "username": "seconduser",
            "password": "123456"
        }
    )

    second_login = client.post(
        "/login",
        json={
            "username": "seconduser",
            "password": "123456"
        }
    )

    second_headers = {
        "Authorization": (
            f"Bearer "
            f"{second_login.get_json()['access_token']}"
        )
    }

    response = client.get(
        f"/tasks/{task_id}",
        headers=second_headers
    )

    assert response.status_code == 404
    assert response.get_json() == {
        "error": "Task not found"
    }