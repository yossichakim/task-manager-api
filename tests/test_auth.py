def test_register_user_successfully(client):
    response = client.post(
        "/register",
        json={
            "username": "yossi",
            "password": "123456"
        }
    )

    data = response.get_json()

    assert response.status_code == 201
    assert data["username"] == "yossi"
    assert data["message"] == "User registered successfully"
    assert "id" in data


def test_register_duplicate_username(client):
    user_data = {
        "username": "yossi",
        "password": "123456"
    }

    first_response = client.post(
        "/register",
        json=user_data
    )

    second_response = client.post(
        "/register",
        json=user_data
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.get_json() == {
        "error": "Username already exists"
    } 


def test_login_successfully(client):
    client.post(
        "/register",
        json={
            "username": "yossi",
            "password": "123456"
        }
    )

    response = client.post(
        "/login",
        json={
            "username": "yossi",
            "password": "123456"
        }
    )

    data = response.get_json()

    assert response.status_code == 200
    assert "access_token" in data
    assert data["user"]["username"] == "yossi"
    assert data["message"] == "Login successful"