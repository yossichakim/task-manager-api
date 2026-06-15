def test_missing_token(client):
    response = client.get("/tasks")

    assert response.status_code == 401
    assert response.get_json()["error"] == (
        "Authorization token is required"
    )


def test_invalid_token(client):
    response = client.get(
        "/tasks",
        headers={
            "Authorization": "Bearer invalid-token"
        }
    )

    assert response.status_code == 422
    assert response.get_json()["error"] == (
        "Invalid authorization token"
    )


def test_valid_token(client, auth_headers):
    response = client.get(
        "/tasks",
        headers=auth_headers
    )

    assert response.status_code == 200
    assert response.get_json() == []