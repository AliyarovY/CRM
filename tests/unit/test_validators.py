import pytest
from pydantic import ValidationError

from app.api.v1.schemas import (
    ContactCreate,
    DealCreate,
    DealStatusChange,
    TaskCreate,
    TaskStatusChange,
    ActivityCreate,
)


class TestContactValidator:
    def test_valid_contact_create(self):
        contact = ContactCreate(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            phone="+1234567890",
        )
        assert contact.first_name == "John"
        assert contact.last_name == "Doe"
        assert contact.email == "john@example.com"

    def test_contact_first_name_required(self):
        with pytest.raises(ValidationError):
            ContactCreate(last_name="Doe")

    def test_contact_last_name_required(self):
        with pytest.raises(ValidationError):
            ContactCreate(first_name="John")

    def test_contact_email_validation(self):
        with pytest.raises(ValidationError):
            ContactCreate(first_name="John", last_name="Doe", email="invalid-email")

    def test_contact_first_name_max_length(self):
        with pytest.raises(ValidationError):
            ContactCreate(
                first_name="J" * 101,
                last_name="Doe",
            )


class TestDealValidator:
    def test_valid_deal_create(self):
        from uuid import uuid4
        from decimal import Decimal

        deal = DealCreate(
            contact_id=uuid4(),
            title="Test Deal",
            amount=Decimal("10000.00"),
        )
        assert deal.title == "Test Deal"
        assert deal.amount == Decimal("10000.00")

    def test_deal_title_required(self):
        from uuid import uuid4

        with pytest.raises(ValidationError):
            DealCreate(contact_id=uuid4())

    def test_deal_contact_id_required(self):
        with pytest.raises(ValidationError):
            DealCreate(title="Test Deal")

    def test_deal_amount_must_be_positive(self):
        from uuid import uuid4
        from decimal import Decimal

        with pytest.raises(ValidationError):
            DealCreate(
                contact_id=uuid4(),
                title="Bad Deal",
                amount=Decimal("-100.00"),
            )

    def test_deal_status_change_valid_statuses(self):
        valid_statuses = ["new", "in_progress", "won", "lost", "closed"]
        for status in valid_statuses:
            status_change = DealStatusChange(status=status)
            assert status_change.status == status

    def test_deal_status_change_invalid_status(self):
        with pytest.raises(ValidationError):
            DealStatusChange(status="invalid_status")


class TestTaskValidator:
    def test_valid_task_create(self):
        from uuid import uuid4

        task = TaskCreate(
            assigned_to=uuid4(),
            title="Test Task",
            priority="high",
        )
        assert task.title == "Test Task"
        assert task.priority == "high"

    def test_task_assigned_to_required(self):
        with pytest.raises(ValidationError):
            TaskCreate(title="Test Task")

    def test_task_title_required(self):
        from uuid import uuid4

        with pytest.raises(ValidationError):
            TaskCreate(assigned_to=uuid4())

    def test_task_priority_default_is_medium(self):
        from uuid import uuid4

        task = TaskCreate(assigned_to=uuid4(), title="Test Task")
        assert task.priority == "medium"

    def test_task_priority_valid_values(self):
        from uuid import uuid4

        valid_priorities = ["low", "medium", "high", "urgent"]
        for priority in valid_priorities:
            task = TaskCreate(
                assigned_to=uuid4(),
                title="Test Task",
                priority=priority,
            )
            assert task.priority == priority

    def test_task_status_change_valid_statuses(self):
        valid_statuses = ["todo", "in_progress", "done", "cancelled"]
        for status in valid_statuses:
            status_change = TaskStatusChange(status=status)
            assert status_change.status == status

    def test_task_status_change_invalid_status(self):
        with pytest.raises(ValidationError):
            TaskStatusChange(status="invalid")


class TestActivityValidator:
    def test_valid_activity_create(self):
        activity = ActivityCreate(
            activity_type="call",
            title="Test Call",
            description="Call description",
        )
        assert activity.activity_type == "call"
        assert activity.title == "Test Call"

    def test_activity_type_required(self):
        with pytest.raises(ValidationError):
            ActivityCreate(title="Test Activity")

    def test_activity_title_required(self):
        with pytest.raises(ValidationError):
            ActivityCreate(activity_type="call")

    def test_activity_type_valid_values(self):
        valid_types = ["call", "email", "meeting", "note", "task"]
        for activity_type in valid_types:
            activity = ActivityCreate(
                activity_type=activity_type,
                title="Test",
            )
            assert activity.activity_type == activity_type

    def test_activity_type_invalid_value(self):
        with pytest.raises(ValidationError):
            ActivityCreate(activity_type="invalid", title="Test")
