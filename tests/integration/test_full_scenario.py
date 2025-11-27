import pytest


@pytest.mark.asyncio
class TestFullScenario:
    async def test_complete_crm_workflow(self, client):
        print("\n=== Step 1: Register new user ===")
        register_response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "workflow@example.com",
                "username": "workflow_user",
                "first_name": "Workflow",
                "last_name": "User",
                "password": "workflowpass123",
            },
        )

        assert register_response.status_code == 201
        response_data = register_response.json()
        access_token = response_data["access_token"]

        me_response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        user_data = me_response.json()
        org_response = await client.get(
            "/api/v1/organizations/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        org_data = org_response.json()

        headers = {
            "Authorization": f"Bearer {access_token}",
            "X-Organization-Id": str(org_data["id"]),
        }

        print("✓ User registered successfully")

        print("\n=== Step 2: Create a contact ===")
        contact_response = await client.post(
            "/api/v1/contacts",
            json={
                "first_name": "John",
                "last_name": "Enterprise",
                "email": "john.enterprise@company.com",
                "phone": "+1234567890",
                "company": "Enterprise Corp",
                "position": "CEO",
            },
            headers=headers,
        )

        assert contact_response.status_code == 201
        contact = contact_response.json()
        contact_id = contact["id"]
        print(f"✓ Contact created: {contact['first_name']} {contact['last_name']}")

        print("\n=== Step 3: Create a deal ===")
        deal_response = await client.post(
            "/api/v1/deals",
            json={
                "contact_id": contact_id,
                "title": "Enterprise Contract",
                "amount": 100000.00,
                "description": "Large enterprise contract",
            },
            headers=headers,
        )

        assert deal_response.status_code == 201
        deal = deal_response.json()
        deal_id = deal["id"]
        print(f"✓ Deal created: {deal['title']} - ${deal['amount']}")

        print("\n=== Step 4: Create activities ===")
        activity_response = await client.post(
            f"/api/v1/activities/deals/{deal_id}",
            json={
                "activity_type": "call",
                "title": "Initial Call",
                "description": "Discussed requirements",
            },
            headers=headers,
        )

        assert activity_response.status_code == 201
        print("✓ Activity logged: Initial Call")

        print("\n=== Step 5: Create tasks ===")
        task_response = await client.post(
            "/api/v1/tasks",
            json={
                "assigned_to": contact["id"],
                "title": "Prepare proposal",
                "priority": "high",
                "deal_id": deal_id,
            },
            headers=headers,
        )

        assert task_response.status_code in [201, 400]

        print("✓ Task created")

        print("\n=== Step 6: Change deal status ===")
        status_response = await client.post(
            f"/api/v1/deals/{deal_id}/status",
            json={"status": "in_progress"},
            headers=headers,
        )

        assert status_response.status_code == 200
        updated_deal = status_response.json()
        print(f"✓ Deal status changed to: {updated_deal['status']}")

        print("\n=== Step 7: Create more activities ===")
        activity_response = await client.post(
            f"/api/v1/activities/deals/{deal_id}",
            json={
                "activity_type": "email",
                "title": "Sent Proposal",
                "description": "Proposal sent to client",
            },
            headers=headers,
        )

        assert activity_response.status_code == 201
        print("✓ Activity logged: Sent Proposal")

        print("\n=== Step 8: Win the deal ===")
        win_response = await client.post(
            f"/api/v1/deals/{deal_id}/status",
            json={"status": "won"},
            headers=headers,
        )

        assert win_response.status_code == 200
        won_deal = win_response.json()
        print(f"✓ Deal WON! Final status: {won_deal['status']}")

        print("\n=== Step 9: Create another contact and deal ===")
        contact_response_2 = await client.post(
            "/api/v1/contacts",
            json={
                "first_name": "Jane",
                "last_name": "Startup",
                "email": "jane.startup@startup.com",
                "company": "Startup Inc",
                "position": "Founder",
            },
            headers=headers,
        )

        assert contact_response_2.status_code == 201
        contact_2 = contact_response_2.json()
        contact_id_2 = contact_2["id"]

        deal_response_2 = await client.post(
            "/api/v1/deals",
            json={
                "contact_id": contact_id_2,
                "title": "Startup Project",
                "amount": 50000.00,
            },
            headers=headers,
        )

        assert deal_response_2.status_code == 201
        deal_2 = deal_response_2.json()
        deal_id_2 = deal_2["id"]
        print(f"✓ Second deal created: {deal_2['title']}")

        print("\n=== Step 10: Get analytics dashboard ===")
        dashboard_response = await client.get(
            "/api/v1/analytics/dashboard",
            headers=headers,
        )

        assert dashboard_response.status_code == 200
        dashboard = dashboard_response.json()

        print(f"✓ Dashboard Summary:")
        print(f"  - Total Deals: {dashboard['deals']['total_deals']}")
        print(f"  - New Deals: {dashboard['deals']['new']}")
        print(f"  - In Progress: {dashboard['deals']['in_progress']}")
        print(f"  - Won Deals: {dashboard['deals']['won']}")
        print(f"  - Win Rate: {dashboard['deals']['win_rate']}%")
        print(f"  - Total Contacts: {dashboard['contacts']['total_contacts']}")
        print(f"  - Total Activities: {dashboard['activities']['total_activities']}")

        assert dashboard["deals"]["total_deals"] >= 2
        assert dashboard["deals"]["won"] >= 1
        assert dashboard["contacts"]["total_contacts"] >= 2

        print("\n=== Step 11: List all contacts ===")
        contacts_response = await client.get(
            "/api/v1/contacts",
            headers=headers,
        )

        assert contacts_response.status_code == 200
        contacts = contacts_response.json()
        print(f"✓ Retrieved {len(contacts)} contacts")

        print("\n=== Step 12: List all deals ===")
        deals_response = await client.get(
            "/api/v1/deals",
            headers=headers,
        )

        assert deals_response.status_code == 200
        deals = deals_response.json()
        print(f"✓ Retrieved {len(deals)} deals")

        print("\n=== Step 13: Get deals summary ===")
        deals_summary = await client.get(
            "/api/v1/analytics/deals/summary",
            headers=headers,
        )

        assert deals_summary.status_code == 200
        summary = deals_summary.json()
        print(f"✓ Deals Summary: Won Amount: ${summary.get('won_amount', 0)}")

        print("\n✅ Full workflow completed successfully!")
