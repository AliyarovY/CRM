from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import OrganizationMember
from app.api.v1.dependencies import get_current_user
from app.api.v1.schemas import OrganizationResponse
from app.repositories import OrganizationRepository

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.get("/me", response_model=OrganizationResponse)
async def get_my_organization(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(OrganizationMember).where(OrganizationMember.user_id == current_user.id)
    result = await db.execute(stmt)
    org_member = result.scalar_one_or_none()

    if org_member is None:
        return None

    org_repo = OrganizationRepository(db)
    organization = await org_repo.get(org_member.organization_id)
    return organization
