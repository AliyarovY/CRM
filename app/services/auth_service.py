from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, Organization, OrganizationMember
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
)
from app.core.permissions import Role
from app.repositories import UserRepository
from app.core.exceptions import BadRequest, Unauthorized


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)

    async def register(
        self,
        email: str,
        username: str,
        first_name: str,
        last_name: str,
        password: str,
    ) -> dict:
        if await self.user_repo.email_exists(email):
            raise BadRequest("Email already registered")

        if await self.user_repo.username_exists(username):
            raise BadRequest("Username already taken")

        user = User(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
            password_hash=hash_password(password),
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)

        org = Organization(
            name=f"{first_name} {last_name}'s Organization",
        )
        self.session.add(org)
        await self.session.commit()
        await self.session.refresh(org)

        org_member = OrganizationMember(
            user_id=user.id,
            organization_id=org.id,
            role=Role.OWNER,
        )
        self.session.add(org_member)
        await self.session.commit()

        access_token = create_access_token({"sub": str(user.id)})
        refresh_token = create_refresh_token({"sub": str(user.id)})

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": user,
            "organization": org,
        }

    async def login(self, email: str, password: str) -> dict:
        user = await self.user_repo.get_by_email(email)

        if user is None or not verify_password(password, user.password_hash):
            raise Unauthorized("Invalid email or password")

        if not user.is_active:
            raise BadRequest("User account is inactive")

        access_token = create_access_token({"sub": str(user.id)})
        refresh_token = create_refresh_token({"sub": str(user.id)})

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": user,
        }

    async def change_password(self, user_id: UUID, old_password: str, new_password: str) -> bool:
        user = await self.user_repo.get(user_id)

        if user is None:
            raise BadRequest("User not found")

        if not verify_password(old_password, user.password_hash):
            raise Unauthorized("Old password is incorrect")

        user.password_hash = hash_password(new_password)
        await self.session.commit()
        return True
