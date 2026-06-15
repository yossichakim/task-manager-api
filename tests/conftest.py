import os

import pytest

from app import create_app


TEST_DATABASE = "test_tasks.db"


@pytest.fixture
def app():
    app = create_app({
        "TESTING": True,
        "JWT_SECRET_KEY": "test-secret-key",
        "DATABASE": TEST_DATABASE
    })

    yield app

    if os.path.exists(TEST_DATABASE):
        os.remove(TEST_DATABASE)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_headers(client):
    client.post(
        "/register",
        json={
            "username": "testuser",
            "password": "123456"
        }
    )

    response = client.post(
        "/login",
        json={
            "username": "testuser",
            "password": "123456"
        }
    )

    access_token = response.get_json()["access_token"]

    return {
        "Authorization": f"Bearer {access_token}"
    }