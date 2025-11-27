from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models import Task, TaskStatusEnum, TaskPriorityEnum
from app.repositories.base import BaseRepository


class TaskRepository(BaseRepository[Task]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Task)

    async def list_by_organization(
        self, organization_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Task]:
        stmt = select(Task).where(
            Task.organization_id == organization_id
        ).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def list_by_contact(
        self, contact_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Task]:
        stmt = select(Task).where(
            Task.contact_id == contact_id
        ).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def list_by_deal(
        self, deal_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Task]:
        stmt = select(Task).where(
            Task.deal_id == deal_id
        ).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def list_by_assigned_to(
        self, organization_id: UUID, user_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Task]:
        stmt = select(Task).where(
            and_(
                Task.organization_id == organization_id,
                Task.assigned_to == user_id
            )
        ).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def list_by_status(
        self, organization_id: UUID, status: TaskStatusEnum, skip: int = 0, limit: int = 100
    ) -> List[Task]:
        stmt = select(Task).where(
            and_(
                Task.organization_id == organization_id,
                Task.status == status
            )
        ).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def list_by_priority(
        self, organization_id: UUID, priority: TaskPriorityEnum, skip: int = 0, limit: int = 100
    ) -> List[Task]:
        stmt = select(Task).where(
            and_(
                Task.organization_id == organization_id,
                Task.priority == priority
            )
        ).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def list_overdue(
        self, organization_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Task]:
        from datetime import datetime
        stmt = select(Task).where(
            and_(
                Task.organization_id == organization_id,
                Task.due_date < datetime.utcnow(),
                Task.status != TaskStatusEnum.DONE
            )
        ).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def search_by_organization(
        self, organization_id: UUID, query: str, skip: int = 0, limit: int = 100
    ) -> List[Task]:
        stmt = select(Task).where(
            and_(
                Task.organization_id == organization_id,
                Task.title.ilike(f"%{query}%")
            )
        ).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_by_organization(self, organization_id: UUID) -> int:
        stmt = select(Task).where(
            Task.organization_id == organization_id
        )
        result = await self.session.execute(stmt)
        return len(result.scalars().all())

    async def count_by_status(
        self, organization_id: UUID, status: TaskStatusEnum
    ) -> int:
        stmt = select(Task).where(
            and_(
                Task.organization_id == organization_id,
                Task.status == status
            )
        )
        result = await self.session.execute(stmt)
        return len(result.scalars().all())
