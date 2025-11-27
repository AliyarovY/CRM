from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Optional, List

from app.database import get_db
from app.models import User
from app.api.v1.dependencies import get_current_user, get_organization_context, check_organization_member
from app.api.v1.schemas import ContactCreate, ContactUpdate, ContactResponse
from app.services import ContactService
from app.core.exceptions import NotFound

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("", response_model=List[ContactResponse])
async def list_contacts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    organization_id: UUID = Depends(get_organization_context),
    db: AsyncSession = Depends(get_db),
):
    await check_organization_member(current_user, organization_id, db)

    service = ContactService(db)

    if search:
        contacts = await service.search_contacts(organization_id, search, skip, limit)
    else:
        contacts = await service.list_contacts(organization_id, skip, limit)

    return contacts


@router.post("", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    request: ContactCreate,
    current_user: User = Depends(get_current_user),
    organization_id: UUID = Depends(get_organization_context),
    db: AsyncSession = Depends(get_db),
):
    await check_organization_member(current_user, organization_id, db)

    service = ContactService(db)
    contact = await service.create_contact(organization_id, **request.model_dump())
    return contact


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: UUID,
    current_user: User = Depends(get_current_user),
    organization_id: UUID = Depends(get_organization_context),
    db: AsyncSession = Depends(get_db),
):
    await check_organization_member(current_user, organization_id, db)

    service = ContactService(db)
    contact = await service.get_contact(contact_id)

    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found",
        )

    return contact


@router.patch("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: UUID,
    request: ContactUpdate,
    current_user: User = Depends(get_current_user),
    organization_id: UUID = Depends(get_organization_context),
    db: AsyncSession = Depends(get_db),
):
    await check_organization_member(current_user, organization_id, db)

    service = ContactService(db)
    updates = request.model_dump(exclude_unset=True)
    contact = await service.update_contact(contact_id, updates)

    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found",
        )

    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(
    contact_id: UUID,
    current_user: User = Depends(get_current_user),
    organization_id: UUID = Depends(get_organization_context),
    db: AsyncSession = Depends(get_db),
):
    await check_organization_member(current_user, organization_id, db)

    service = ContactService(db)
    success = await service.delete_contact(contact_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found",
        )

    return None
