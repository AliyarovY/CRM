import pytest


@pytest.mark.asyncio
class TestAnalytics:
    async def test_get_deals_summary(self, client, auth_headers):
        response = await client.get(
            "/api/v1/analytics/deals/summary",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "total_deals" in data
        assert "new" in data
        assert "in_progress" in data
        assert "won" in data
        assert "lost" in data
        assert "win_rate" in data
        assert "pipeline_amount" in data

    async def test_get_tasks_summary(self, client, auth_headers):
        response = await client.get(
            "/api/v1/analytics/tasks/summary",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "total_tasks" in data
        assert "todo" in data
        assert "in_progress" in data
        assert "done" in data
        assert "overdue" in data
        assert "completion_rate" in data

    async def test_get_contacts_statistics(self, client, auth_headers):
        response = await client.get(
            "/api/v1/analytics/contacts/statistics",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "total_contacts" in data

    async def test_get_activities_statistics(self, client, auth_headers):
        response = await client.get(
            "/api/v1/analytics/activities/statistics",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "total_activities" in data
        assert "calls" in data
        assert "emails" in data
        assert "meetings" in data
        assert "notes" in data

    async def test_get_dashboard_summary(self, client, auth_headers):
        response = await client.get(
            "/api/v1/analytics/dashboard",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "deals" in data
        assert "tasks" in data
        assert "contacts" in data
        assert "activities" in data
        assert "recent_activities" in data

    async def test_deals_summary_with_data(self, client, auth_headers):
        contact_response = await client.post(
            "/api/v1/contacts",
            json={
                "first_name": "Analytics",
                "last_name": "Contact",
            },
            headers=auth_headers,
        )

        contact_id = contact_response.json()["id"]

        await client.post(
            "/api/v1/deals",
            json={
                "contact_id": contact_id,
                "title": "Deal 1",
                "amount": 10000.00,
            },
            headers=auth_headers,
        )

        response = await client.get(
            "/api/v1/analytics/deals/summary",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total_deals"] >= 1
        assert data["new"] >= 1

    async def test_dashboard_includes_recent_activities(self, client, auth_headers):
        contact_response = await client.post(
            "/api/v1/contacts",
            json={
                "first_name": "Dashboard",
                "last_name": "Contact",
            },
            headers=auth_headers,
        )

        contact_id = contact_response.json()["id"]

        await client.post(
            "/api/v1/activities/contacts/{}".format(contact_id),
            json={
                "activity_type": "call",
                "title": "Test Call",
            },
            headers=auth_headers,
        )

        response = await client.get(
            "/api/v1/analytics/dashboard",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["recent_activities"], list)

    async def test_analytics_requires_organization_header(self, client, test_user_token):
        response = await client.get(
            "/api/v1/analytics/deals/summary",
            headers={
                "Authorization": f"Bearer {test_user_token['access_token']}",
            },
        )

        assert response.status_code == 400

    async def test_analytics_requires_auth(self, client):
        response = await client.get(
            "/api/v1/analytics/deals/summary",
        )

        assert response.status_code == 401
