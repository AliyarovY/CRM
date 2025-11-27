import pytest


@pytest.mark.asyncio
class TestAuth:
    async def test_register_new_user(self, client):
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "username": "newuser",
                "first_name": "New",
                "last_name": "User",
                "password": "securepassword123",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["access_token"]
        assert data["refresh_token"]

    async def test_register_duplicate_email(self, client, test_user):
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": test_user.email,
                "username": "anotheruser",
                "first_name": "Another",
                "last_name": "User",
                "password": "password123",
            },
        )

        assert response.status_code == 409

    async def test_register_duplicate_username(self, client, test_user):
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "different@example.com",
                "username": test_user.username,
                "first_name": "Different",
                "last_name": "User",
                "password": "password123",
            },
        )

        assert response.status_code == 409

    async def test_login_success(self, client, test_user):
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": "testpassword123",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    async def test_login_invalid_password(self, client, test_user):
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": "wrongpassword",
            },
        )

        assert response.status_code == 401

    async def test_login_nonexistent_user(self, client):
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "password123",
            },
        )

        assert response.status_code == 401

    async def test_get_current_user(self, client, auth_headers):
        response = await client.get(
            "/api/v1/auth/me",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "testuser@example.com"
        assert data["username"] == "testuser"

    async def test_get_current_user_without_token(self, client):
        response = await client.get("/api/v1/auth/me")

        assert response.status_code == 401

    async def test_refresh_token(self, client, test_user_token):
        response = await client.post(
            "/api/v1/auth/refresh",
            json={
                "refresh_token": test_user_token["refresh_token"],
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    async def test_change_password(self, client, auth_headers, test_user):
        response = await client.post(
            "/api/v1/auth/change-password",
            json={
                "old_password": "testpassword123",
                "new_password": "newpassword123",
            },
            headers=auth_headers,
        )

        assert response.status_code == 200

    async def test_change_password_wrong_old_password(self, client, auth_headers):
        response = await client.post(
            "/api/v1/auth/change-password",
            json={
                "old_password": "wrongpassword",
                "new_password": "newpassword123",
            },
            headers=auth_headers,
        )

        assert response.status_code == 401
