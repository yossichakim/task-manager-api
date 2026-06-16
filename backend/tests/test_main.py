def test_home_endpoint(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.get_json() == {
        "message": "Task Manager API is running"
    }