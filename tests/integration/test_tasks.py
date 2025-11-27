import pytest


@pytest.mark.asyncio
class TestTasks:
    async def test_create_task(self, client, sales_auth_headers, test_user_sales):
        response = await client.post(
            "/api/v1/tasks",
            json={
                "assigned_to": str(test_user_sales.id),
                "title": "Test Task",
                "priority": "high",
            },
            headers=sales_auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Task"
        assert data["priority"] == "high"
        assert data["status"] == "todo"

    async def test_list_tasks(self, client, sales_auth_headers, test_user_sales):
        await client.post(
            "/api/v1/tasks",
            json={
                "assigned_to": str(test_user_sales.id),
                "title": "Task 1",
            },
            headers=sales_auth_headers,
        )

        response = await client.get(
            "/api/v1/tasks",
            headers=sales_auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    async def test_get_task(self, client, sales_auth_headers, test_user_sales):
        create_response = await client.post(
            "/api/v1/tasks",
            json={
                "assigned_to": str(test_user_sales.id),
                "title": "Get Task",
            },
            headers=sales_auth_headers,
        )

        task_id = create_response.json()["id"]

        response = await client.get(
            f"/api/v1/tasks/{task_id}",
            headers=sales_auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == task_id

    async def test_update_task(self, client, sales_auth_headers, test_user_sales):
        create_response = await client.post(
            "/api/v1/tasks",
            json={
                "assigned_to": str(test_user_sales.id),
                "title": "Update Task",
            },
            headers=sales_auth_headers,
        )

        task_id = create_response.json()["id"]

        response = await client.patch(
            f"/api/v1/tasks/{task_id}",
            json={
                "title": "Updated Task",
                "priority": "urgent",
            },
            headers=sales_auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Task"
        assert data["priority"] == "urgent"

    async def test_complete_task(self, client, sales_auth_headers, test_user_sales):
        create_response = await client.post(
            "/api/v1/tasks",
            json={
                "assigned_to": str(test_user_sales.id),
                "title": "Complete Task",
            },
            headers=sales_auth_headers,
        )

        task_id = create_response.json()["id"]

        response = await client.post(
            f"/api/v1/tasks/{task_id}/complete",
            headers=sales_auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "done"

    async def test_delete_task(self, client, sales_auth_headers, test_user_sales):
        create_response = await client.post(
            "/api/v1/tasks",
            json={
                "assigned_to": str(test_user_sales.id),
                "title": "Delete Task",
            },
            headers=sales_auth_headers,
        )

        task_id = create_response.json()["id"]

        response = await client.delete(
            f"/api/v1/tasks/{task_id}",
            headers=sales_auth_headers,
        )

        assert response.status_code == 204

    async def test_task_default_priority_medium(self, client, sales_auth_headers, test_user_sales):
        response = await client.post(
            "/api/v1/tasks",
            json={
                "assigned_to": str(test_user_sales.id),
                "title": "Default Priority Task",
            },
            headers=sales_auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["priority"] == "medium"

    async def test_task_with_contact(self, client, sales_auth_headers, test_user_sales, auth_headers):
        contact_response = await client.post(
            "/api/v1/contacts",
            json={
                "first_name": "Task",
                "last_name": "Contact",
            },
            headers=auth_headers,
        )

        contact_id = contact_response.json()["id"]

        response = await client.post(
            "/api/v1/tasks",
            json={
                "assigned_to": str(test_user_sales.id),
                "title": "Task with Contact",
                "contact_id": contact_id,
            },
            headers=sales_auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["contact_id"] == contact_id

    async def test_task_with_deal(self, client, sales_auth_headers, test_user_sales, auth_headers):
        contact_response = await client.post(
            "/api/v1/contacts",
            json={
                "first_name": "Deal",
                "last_name": "Contact",
            },
            headers=auth_headers,
        )

        contact_id = contact_response.json()["id"]

        deal_response = await client.post(
            "/api/v1/deals",
            json={
                "contact_id": contact_id,
                "title": "Task Deal",
            },
            headers=auth_headers,
        )

        deal_id = deal_response.json()["id"]

        response = await client.post(
            "/api/v1/tasks",
            json={
                "assigned_to": str(test_user_sales.id),
                "title": "Task with Deal",
                "deal_id": deal_id,
            },
            headers=sales_auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["deal_id"] == deal_id
