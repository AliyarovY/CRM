import pytest


@pytest.mark.asyncio
class TestContacts:
    async def test_list_contacts_empty(self, client, auth_headers):
        response = await client.get(
            "/api/v1/contacts",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    async def test_create_contact(self, client, auth_headers):
        response = await client.post(
            "/api/v1/contacts",
            json={
                "first_name": "John",
                "last_name": "Doe",
                "email": "john@example.com",
                "phone": "+1234567890",
                "position": "Manager",
                "company": "ACME Corp",
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["first_name"] == "John"
        assert data["last_name"] == "Doe"
        assert data["email"] == "john@example.com"
        assert "id" in data

    async def test_list_contacts_after_create(self, client, auth_headers):
        await client.post(
            "/api/v1/contacts",
            json={
                "first_name": "Jane",
                "last_name": "Smith",
                "email": "jane@example.com",
            },
            headers=auth_headers,
        )

        response = await client.get(
            "/api/v1/contacts",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["first_name"] == "Jane"

    async def test_get_contact(self, client, auth_headers):
        create_response = await client.post(
            "/api/v1/contacts",
            json={
                "first_name": "Bob",
                "last_name": "Johnson",
                "email": "bob@example.com",
            },
            headers=auth_headers,
        )

        contact_id = create_response.json()["id"]

        response = await client.get(
            f"/api/v1/contacts/{contact_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == contact_id
        assert data["first_name"] == "Bob"

    async def test_update_contact(self, client, auth_headers):
        create_response = await client.post(
            "/api/v1/contacts",
            json={
                "first_name": "Alice",
                "last_name": "Williams",
                "email": "alice@example.com",
            },
            headers=auth_headers,
        )

        contact_id = create_response.json()["id"]

        response = await client.patch(
            f"/api/v1/contacts/{contact_id}",
            json={
                "first_name": "Alicia",
                "phone": "+9876543210",
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "Alicia"
        assert data["phone"] == "+9876543210"

    async def test_delete_contact(self, client, auth_headers):
        create_response = await client.post(
            "/api/v1/contacts",
            json={
                "first_name": "Charlie",
                "last_name": "Brown",
                "email": "charlie@example.com",
            },
            headers=auth_headers,
        )

        contact_id = create_response.json()["id"]

        response = await client.delete(
            f"/api/v1/contacts/{contact_id}",
            headers=auth_headers,
        )

        assert response.status_code == 204

        get_response = await client.get(
            f"/api/v1/contacts/{contact_id}",
            headers=auth_headers,
        )

        assert get_response.status_code == 404

    async def test_search_contacts(self, client, auth_headers):
        await client.post(
            "/api/v1/contacts",
            json={
                "first_name": "David",
                "last_name": "Miller",
                "email": "david@example.com",
            },
            headers=auth_headers,
        )

        response = await client.get(
            "/api/v1/contacts?search=David",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert any(c["first_name"] == "David" for c in data)

    async def test_contact_pagination(self, client, auth_headers):
        for i in range(5):
            await client.post(
                "/api/v1/contacts",
                json={
                    "first_name": f"Contact{i}",
                    "last_name": "Test",
                },
                headers=auth_headers,
            )

        response = await client.get(
            "/api/v1/contacts?skip=0&limit=2",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 2

    async def test_missing_auth_headers(self, client):
        response = await client.get("/api/v1/contacts")

        assert response.status_code == 401

    async def test_missing_organization_header(self, client, test_user_token):
        response = await client.get(
            "/api/v1/contacts",
            headers={
                "Authorization": f"Bearer {test_user_token['access_token']}",
            },
        )

        assert response.status_code == 400
