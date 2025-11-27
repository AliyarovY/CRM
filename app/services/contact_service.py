from uuid import UUID
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Contact, Deal
from app.repositories import ContactRepository, DealRepository
from app.core.exceptions import NotFound, BadRequest


class ContactService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.contact_repo = ContactRepository(session)
        self.deal_repo = DealRepository(session)

    async def create_contact(
        self,
        organization_id: UUID,
        first_name: str,
        last_name: str,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        position: Optional[str] = None,
        company: Optional[str] = None,
        address: Optional[str] = None,
        city: Optional[str] = None,
        country: Optional[str] = None,
        postal_code: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Contact:
        contact = Contact(
            organization_id=organization_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            position=position,
            company=company,
            address=address,
            city=city,
            country=country,
            postal_code=postal_code,
            notes=notes,
        )
        return await self.contact_repo.create(contact)

    async def get_contact(self, contact_id: UUID) -> Optional[Contact]:
        return await self.contact_repo.get(contact_id)

    async def list_contacts(
        self, organization_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Contact]:
        return await self.contact_repo.list_by_organization(organization_id, skip, limit)

    async def update_contact(
        self, contact_id: UUID, updates: dict
    ) -> Optional[Contact]:
        contact = await self.contact_repo.get(contact_id)
        if contact is None:
            raise NotFound("Contact not found")

        return await self.contact_repo.update(contact_id, updates)

    async def delete_contact(self, contact_id: UUID) -> bool:
        contact = await self.contact_repo.get(contact_id)
        if contact is None:
            raise NotFound("Contact not found")

        deals = await self.deal_repo.list_by_contact(contact_id)
        if deals:
            raise BadRequest(
                "Cannot delete contact with associated deals. "
                "Please delete or reassign deals first."
            )

        return await self.contact_repo.delete(contact_id)

    async def search_contacts(
        self,
        organization_id: UUID,
        query: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Contact]:
        return await self.contact_repo.search_by_organization(
            organization_id, query, skip, limit
        )

    async def get_contact_count(self, organization_id: UUID) -> int:
        return await self.contact_repo.count_by_organization(organization_id)
