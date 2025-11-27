from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Dict, Any

from app.database import get_db
from app.models import User
from app.api.v1.dependencies import get_current_user, get_organization_context, check_organization_member
from app.services import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/deals/summary", response_model=Dict[str, Any])
async def get_deals_summary(
    current_user: User = Depends(get_current_user),
    organization_id: UUID = Depends(get_organization_context),
    db: AsyncSession = Depends(get_db),
):
    await check_organization_member(current_user, organization_id, db)

    service = AnalyticsService(db)
    summary = await service.get_deals_summary(organization_id)
    return summary


@router.get("/tasks/summary", response_model=Dict[str, Any])
async def get_tasks_summary(
    current_user: User = Depends(get_current_user),
    organization_id: UUID = Depends(get_organization_context),
    db: AsyncSession = Depends(get_db),
):
    await check_organization_member(current_user, organization_id, db)

    service = AnalyticsService(db)
    summary = await service.get_tasks_summary(organization_id)
    return summary


@router.get("/contacts/statistics", response_model=Dict[str, Any])
async def get_contacts_statistics(
    current_user: User = Depends(get_current_user),
    organization_id: UUID = Depends(get_organization_context),
    db: AsyncSession = Depends(get_db),
):
    await check_organization_member(current_user, organization_id, db)

    service = AnalyticsService(db)
    stats = await service.get_contact_statistics(organization_id)
    return stats


@router.get("/activities/statistics", response_model=Dict[str, Any])
async def get_activities_statistics(
    current_user: User = Depends(get_current_user),
    organization_id: UUID = Depends(get_organization_context),
    db: AsyncSession = Depends(get_db),
):
    await check_organization_member(current_user, organization_id, db)

    service = AnalyticsService(db)
    stats = await service.get_activity_statistics(organization_id)
    return stats


@router.get("/dashboard", response_model=Dict[str, Any])
async def get_dashboard_summary(
    current_user: User = Depends(get_current_user),
    organization_id: UUID = Depends(get_organization_context),
    db: AsyncSession = Depends(get_db),
):
    await check_organization_member(current_user, organization_id, db)

    service = AnalyticsService(db)
    dashboard = await service.get_dashboard_summary(organization_id)
    return dashboard
