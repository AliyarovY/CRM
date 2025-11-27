from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Optional, List

from app.database import get_db
from app.models import User
from app.api.v1.dependencies import get_current_user, get_organization_context, check_organization_member
from app.api.v1.schemas import ActivityCreate, ActivityResponse
from app.services import ActivityService

router = APIRouter(prefix="/activities", tags=["activities"])


@router.get("/deals/{deal_id}", response_model=List[ActivityResponse])
async def list_deal_activities(
    deal_id: UUID,
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    organization_id: UUID = Depends(get_organization_context),
    db: AsyncSession = Depends(get_db),
):
    await check_organization_member(current_user, organization_id, db)

    service = ActivityService(db)
    activities = await service.list_deal_activities(deal_id, limit)
    return activities


@router.post("/deals/{deal_id}", response_model=ActivityResponse, status_code=status.HTTP_201_CREATED)
async def create_deal_activity(
    deal_id: UUID,
    request: ActivityCreate,
    current_user: User = Depends(get_current_user),
    organization_id: UUID = Depends(get_organization_context),
    db: AsyncSession = Depends(get_db),
):
    await check_organization_member(current_user, organization_id, db)

    service = ActivityService(db)
    data = request.model_dump(exclude={"contact_id", "deal_id"})
    activity = await service.create_activity(
        organization_id=organization_id,
        created_by=current_user.id,
        deal_id=deal_id,
        **data
    )
    return activity


@router.get("/contacts/{contact_id}", response_model=List[ActivityResponse])
async def list_contact_activities(
    contact_id: UUID,
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    organization_id: UUID = Depends(get_organization_context),
    db: AsyncSession = Depends(get_db),
):
    await check_organization_member(current_user, organization_id, db)

    service = ActivityService(db)
    activities = await service.list_contact_activities(contact_id, limit)
    return activities


@router.post("/contacts/{contact_id}", response_model=ActivityResponse, status_code=status.HTTP_201_CREATED)
async def create_contact_activity(
    contact_id: UUID,
    request: ActivityCreate,
    current_user: User = Depends(get_current_user),
    organization_id: UUID = Depends(get_organization_context),
    db: AsyncSession = Depends(get_db),
):
    await check_organization_member(current_user, organization_id, db)

    service = ActivityService(db)
    data = request.model_dump(exclude={"contact_id", "deal_id"})
    activity = await service.create_activity(
        organization_id=organization_id,
        created_by=current_user.id,
        contact_id=contact_id,
        **data
    )
    return activity
