from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Optional, List

from app.database import get_db
from app.models import User, DealStatusEnum
from app.api.v1.dependencies import get_current_user, get_organization_context, check_organization_member
from app.api.v1.schemas import DealCreate, DealUpdate, DealStatusChange, DealResponse
from app.services import DealService
from app.core.exceptions import BadRequest

router = APIRouter(prefix="/deals", tags=["deals"])


@router.get("", response_model=List[DealResponse])
async def list_deals(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    organization_id: UUID = Depends(get_organization_context),
    db: AsyncSession = Depends(get_db),
):
    await check_organization_member(current_user, organization_id, db)

    service = DealService(db)

    if search:
        deals = await service.search_deals(organization_id, search, skip, limit)
    elif status:
        try:
            status_enum = DealStatusEnum[status.upper()]
            deals = await service.get_deals_by_status(organization_id, status_enum, skip, limit)
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status",
            )
    else:
        deals = await service.list_deals(organization_id, skip, limit)

    return deals


@router.post("", response_model=DealResponse, status_code=status.HTTP_201_CREATED)
async def create_deal(
    request: DealCreate,
    current_user: User = Depends(get_current_user),
    organization_id: UUID = Depends(get_organization_context),
    db: AsyncSession = Depends(get_db),
):
    await check_organization_member(current_user, organization_id, db)

    service = DealService(db)
    try:
        deal = await service.create_deal(
            organization_id=organization_id,
            **request.model_dump()
        )
        return deal
    except BadRequest as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/{deal_id}", response_model=DealResponse)
async def get_deal(
    deal_id: UUID,
    current_user: User = Depends(get_current_user),
    organization_id: UUID = Depends(get_organization_context),
    db: AsyncSession = Depends(get_db),
):
    await check_organization_member(current_user, organization_id, db)

    service = DealService(db)
    deal = await service.get_deal(deal_id)

    if deal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deal not found",
        )

    return deal


@router.patch("/{deal_id}", response_model=DealResponse)
async def update_deal(
    deal_id: UUID,
    request: DealUpdate,
    current_user: User = Depends(get_current_user),
    organization_id: UUID = Depends(get_organization_context),
    db: AsyncSession = Depends(get_db),
):
    await check_organization_member(current_user, organization_id, db)

    service = DealService(db)
    updates = request.model_dump(exclude_unset=True)

    try:
        deal = await service.update_deal(deal_id, updates)
        if deal is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deal not found",
            )
        return deal
    except BadRequest as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/{deal_id}/status", response_model=DealResponse)
async def change_deal_status(
    deal_id: UUID,
    request: DealStatusChange,
    current_user: User = Depends(get_current_user),
    organization_id: UUID = Depends(get_organization_context),
    db: AsyncSession = Depends(get_db),
):
    await check_organization_member(current_user, organization_id, db)

    service = DealService(db)
    try:
        status_enum = DealStatusEnum[request.status.upper()]
        deal = await service.change_deal_status(deal_id, status_enum, current_user.id)

        if deal is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deal not found",
            )

        return deal
    except BadRequest as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/{deal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_deal(
    deal_id: UUID,
    current_user: User = Depends(get_current_user),
    organization_id: UUID = Depends(get_organization_context),
    db: AsyncSession = Depends(get_db),
):
    await check_organization_member(current_user, organization_id, db)

    service = DealService(db)
    success = await service.delete_deal(deal_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deal not found",
        )

    return None
