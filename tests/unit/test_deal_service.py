import pytest
from uuid import uuid4
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession

from app.services import DealService
from app.models import Deal, DealStatusEnum, Contact, Organization
from app.core.exceptions import BadRequest
from app.repositories import DealRepository, ContactRepository


@pytest.mark.asyncio
class TestDealService:
    async def test_create_deal_with_positive_amount(self, test_db, test_organization, test_user):
        db = await self._get_db_session(test_db)

        contact = Contact(
            id=uuid4(),
            organization_id=test_organization.id,
            first_name="John",
            last_name="Doe",
            email="john@example.com",
        )
        db.add(contact)
        await db.commit()

        service = DealService(db)
        deal = await service.create_deal(
            organization_id=test_organization.id,
            contact_id=contact.id,
            title="Test Deal",
            amount=Decimal("10000.00"),
        )

        assert deal.title == "Test Deal"
        assert deal.amount == Decimal("10000.00")
        assert deal.status == DealStatusEnum.NEW

        await db.close()

    async def test_create_deal_with_zero_amount_fails(self, test_db, test_organization, test_user):
        db = await self._get_db_session(test_db)

        contact = Contact(
            id=uuid4(),
            organization_id=test_organization.id,
            first_name="Jane",
            last_name="Doe",
            email="jane@example.com",
        )
        db.add(contact)
        await db.commit()

        service = DealService(db)

        with pytest.raises(BadRequest):
            await service.create_deal(
                organization_id=test_organization.id,
                contact_id=contact.id,
                title="Bad Deal",
                amount=Decimal("0"),
            )

        await db.close()

    async def test_deal_status_transition_new_to_in_progress(self, test_db, test_organization, test_user):
        db = await self._get_db_session(test_db)

        contact = Contact(
            id=uuid4(),
            organization_id=test_organization.id,
            first_name="Bob",
            last_name="Smith",
        )
        db.add(contact)
        await db.commit()

        service = DealService(db)
        deal = await service.create_deal(
            organization_id=test_organization.id,
            contact_id=contact.id,
            title="Test Deal",
            amount=Decimal("5000.00"),
        )

        updated_deal = await service.change_deal_status(
            deal.id, DealStatusEnum.IN_PROGRESS, test_user.id
        )

        assert updated_deal.status == DealStatusEnum.IN_PROGRESS

        await db.close()

    async def test_deal_status_transition_invalid(self, test_db, test_organization, test_user):
        db = await self._get_db_session(test_db)

        contact = Contact(
            id=uuid4(),
            organization_id=test_organization.id,
            first_name="Alice",
            last_name="Johnson",
        )
        db.add(contact)
        await db.commit()

        service = DealService(db)
        deal = await service.create_deal(
            organization_id=test_organization.id,
            contact_id=contact.id,
            title="Test Deal",
            amount=Decimal("3000.00"),
        )

        with pytest.raises(BadRequest):
            await service.change_deal_status(
                deal.id, DealStatusEnum.CLOSED, test_user.id
            )

        await db.close()

    async def test_deal_cannot_be_won_without_amount(self, test_db, test_organization, test_user):
        db = await self._get_db_session(test_db)

        contact = Contact(
            id=uuid4(),
            organization_id=test_organization.id,
            first_name="Charlie",
            last_name="Brown",
        )
        db.add(contact)
        await db.commit()

        service = DealService(db)
        deal = await service.create_deal(
            organization_id=test_organization.id,
            contact_id=contact.id,
            title="No Amount Deal",
        )

        await service.change_deal_status(
            deal.id, DealStatusEnum.IN_PROGRESS, test_user.id
        )

        with pytest.raises(BadRequest):
            await service.change_deal_status(
                deal.id, DealStatusEnum.WON, test_user.id
            )

        await db.close()

    @staticmethod
    async def _get_db_session(test_db):
        from sqlalchemy.ext.asyncio import AsyncSession
        return AsyncSession(test_db, expire_on_commit=False)
