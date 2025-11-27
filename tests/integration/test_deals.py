import pytest


@pytest.mark.asyncio
class TestDeals:
    async def test_create_deal(self, client, auth_headers):
        contact_response = await client.post(
            "/api/v1/contacts",
            json={
                "first_name": "Deal",
                "last_name": "Contact",
                "email": "deal@example.com",
            },
            headers=auth_headers,
        )

        contact_id = contact_response.json()["id"]

        response = await client.post(
            "/api/v1/deals",
            json={
                "contact_id": contact_id,
                "title": "Test Deal",
                "amount": 10000.00,
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Deal"
        assert float(data["amount"]) == 10000.00
        assert data["status"] == "new"

    async def test_list_deals(self, client, auth_headers):
        contact_response = await client.post(
            "/api/v1/contacts",
            json={
                "first_name": "List",
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
                "amount": 5000.00,
            },
            headers=auth_headers,
        )

        response = await client.get(
            "/api/v1/deals",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0

    async def test_change_deal_status_new_to_in_progress(self, client, auth_headers):
        contact_response = await client.post(
            "/api/v1/contacts",
            json={
                "first_name": "Status",
                "last_name": "Contact",
            },
            headers=auth_headers,
        )

        contact_id = contact_response.json()["id"]

        deal_response = await client.post(
            "/api/v1/deals",
            json={
                "contact_id": contact_id,
                "title": "Status Deal",
                "amount": 7000.00,
            },
            headers=auth_headers,
        )

        deal_id = deal_response.json()["id"]

        response = await client.post(
            f"/api/v1/deals/{deal_id}/status",
            json={"status": "in_progress"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "in_progress"

    async def test_change_deal_status_in_progress_to_won(self, client, auth_headers):
        contact_response = await client.post(
            "/api/v1/contacts",
            json={
                "first_name": "Won",
                "last_name": "Contact",
            },
            headers=auth_headers,
        )

        contact_id = contact_response.json()["id"]

        deal_response = await client.post(
            "/api/v1/deals",
            json={
                "contact_id": contact_id,
                "title": "Won Deal",
                "amount": 15000.00,
            },
            headers=auth_headers,
        )

        deal_id = deal_response.json()["id"]

        await client.post(
            f"/api/v1/deals/{deal_id}/status",
            json={"status": "in_progress"},
            headers=auth_headers,
        )

        response = await client.post(
            f"/api/v1/deals/{deal_id}/status",
            json={"status": "won"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "won"

    async def test_change_deal_status_invalid_transition(self, client, auth_headers):
        contact_response = await client.post(
            "/api/v1/contacts",
            json={
                "first_name": "Invalid",
                "last_name": "Contact",
            },
            headers=auth_headers,
        )

        contact_id = contact_response.json()["id"]

        deal_response = await client.post(
            "/api/v1/deals",
            json={
                "contact_id": contact_id,
                "title": "Invalid Deal",
                "amount": 5000.00,
            },
            headers=auth_headers,
        )

        deal_id = deal_response.json()["id"]

        response = await client.post(
            f"/api/v1/deals/{deal_id}/status",
            json={"status": "won"},
            headers=auth_headers,
        )

        assert response.status_code == 400

    async def test_change_deal_status_won_without_amount(self, client, auth_headers):
        contact_response = await client.post(
            "/api/v1/contacts",
            json={
                "first_name": "No Amount",
                "last_name": "Contact",
            },
            headers=auth_headers,
        )

        contact_id = contact_response.json()["id"]

        deal_response = await client.post(
            "/api/v1/deals",
            json={
                "contact_id": contact_id,
                "title": "No Amount Deal",
            },
            headers=auth_headers,
        )

        deal_id = deal_response.json()["id"]

        await client.post(
            f"/api/v1/deals/{deal_id}/status",
            json={"status": "in_progress"},
            headers=auth_headers,
        )

        response = await client.post(
            f"/api/v1/deals/{deal_id}/status",
            json={"status": "won"},
            headers=auth_headers,
        )

        assert response.status_code == 400

    async def test_get_deal(self, client, auth_headers):
        contact_response = await client.post(
            "/api/v1/contacts",
            json={
                "first_name": "Get",
                "last_name": "Contact",
            },
            headers=auth_headers,
        )

        contact_id = contact_response.json()["id"]

        deal_response = await client.post(
            "/api/v1/deals",
            json={
                "contact_id": contact_id,
                "title": "Get Deal",
                "amount": 3000.00,
            },
            headers=auth_headers,
        )

        deal_id = deal_response.json()["id"]

        response = await client.get(
            f"/api/v1/deals/{deal_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == deal_id

    async def test_delete_deal(self, client, auth_headers):
        contact_response = await client.post(
            "/api/v1/contacts",
            json={
                "first_name": "Delete",
                "last_name": "Contact",
            },
            headers=auth_headers,
        )

        contact_id = contact_response.json()["id"]

        deal_response = await client.post(
            "/api/v1/deals",
            json={
                "contact_id": contact_id,
                "title": "Delete Deal",
            },
            headers=auth_headers,
        )

        deal_id = deal_response.json()["id"]

        response = await client.delete(
            f"/api/v1/deals/{deal_id}",
            headers=auth_headers,
        )

        assert response.status_code == 204

    async def test_filter_deals_by_status(self, client, auth_headers):
        contact_response = await client.post(
            "/api/v1/contacts",
            json={
                "first_name": "Filter",
                "last_name": "Contact",
            },
            headers=auth_headers,
        )

        contact_id = contact_response.json()["id"]

        deal_response = await client.post(
            "/api/v1/deals",
            json={
                "contact_id": contact_id,
                "title": "Filter Deal",
                "amount": 8000.00,
            },
            headers=auth_headers,
        )

        deal_id = deal_response.json()["id"]

        await client.post(
            f"/api/v1/deals/{deal_id}/status",
            json={"status": "in_progress"},
            headers=auth_headers,
        )

        response = await client.get(
            "/api/v1/deals?status=in_progress",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert any(d["id"] == deal_id for d in data)
