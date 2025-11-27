from typing import Optional
from uuid import UUID
from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.core.security import extract_user_id_from_token
from app.core.permissions import Role, has_permission, Permission
from app.models import User, OrganizationMember


async def get_token_from_header(
    authorization: Optional[str] = Header(None),
) -> str:
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
        )

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header",
        )

    return parts[1]


async def get_current_user(
    token: str = Depends(get_token_from_header),
    db: AsyncSession = Depends(get_db),
) -> User:
    user_id = extract_user_id_from_token(token)

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    return user


async def get_organization_context(
    x_organization_id: Optional[str] = Header(None),
) -> UUID:
    if not x_organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing X-Organization-Id header",
        )

    try:
        return UUID(x_organization_id)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid organization ID format",
        )


async def check_organization_member(
    current_user: User = Depends(get_current_user),
    organization_id: UUID = Depends(get_organization_context),
    db: AsyncSession = Depends(get_db),
) -> OrganizationMember:
    stmt = select(OrganizationMember).where(
        (OrganizationMember.user_id == current_user.id)
        & (OrganizationMember.organization_id == organization_id)
        & (OrganizationMember.is_active == True)
    )
    result = await db.execute(stmt)
    member = result.scalar_one_or_none()

    if member is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this organization",
        )

    return member


def require_permission(permission: Permission):
    async def permission_checker(
        member: OrganizationMember = Depends(check_organization_member),
    ) -> OrganizationMember:
        if not has_permission(member.role, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You don't have {permission} permission",
            )
        return member

    return permission_checker


def require_role(role: Role):
    async def role_checker(
        member: OrganizationMember = Depends(check_organization_member),
    ) -> OrganizationMember:
        if member.role != role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This action requires {role} role",
            )
        return member

    return role_checker
