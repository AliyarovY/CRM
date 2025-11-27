from uuid import UUID
from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Task, TaskStatusEnum, TaskPriorityEnum
from app.repositories import TaskRepository
from app.core.exceptions import NotFound, BadRequest, Forbidden
from app.core.permissions import Role


class TaskService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.task_repo = TaskRepository(session)

    async def create_task(
        self,
        organization_id: UUID,
        assigned_to: UUID,
        title: str,
        contact_id: Optional[UUID] = None,
        deal_id: Optional[UUID] = None,
        description: Optional[str] = None,
        priority: TaskPriorityEnum = TaskPriorityEnum.MEDIUM,
        due_date: Optional[datetime] = None,
    ) -> Task:
        if due_date is not None:
            if due_date.date() < datetime.utcnow().date():
                raise BadRequest("Due date cannot be in the past")

        task = Task(
            organization_id=organization_id,
            contact_id=contact_id,
            deal_id=deal_id,
            assigned_to=assigned_to,
            title=title,
            description=description,
            priority=priority,
            due_date=due_date,
        )
        return await self.task_repo.create(task)

    async def get_task(self, task_id: UUID) -> Optional[Task]:
        return await self.task_repo.get(task_id)

    async def list_tasks(
        self, organization_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Task]:
        return await self.task_repo.list_by_organization(organization_id, skip, limit)

    async def list_tasks_for_user(
        self,
        organization_id: UUID,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Task]:
        return await self.task_repo.list_by_assigned_to(
            organization_id, user_id, skip, limit
        )

    async def update_task(
        self,
        task_id: UUID,
        updates: dict,
        current_user_id: UUID,
        user_role: Role,
    ) -> Optional[Task]:
        task = await self.task_repo.get(task_id)
        if task is None:
            raise NotFound("Task not found")

        if user_role.value == "sales" and task.assigned_to != current_user_id:
            raise Forbidden("You can only update your own tasks")

        if "due_date" in updates and updates["due_date"] is not None:
            if updates["due_date"].date() < datetime.utcnow().date():
                raise BadRequest("Due date cannot be in the past")

        return await self.task_repo.update(task_id, updates)

    async def complete_task(
        self, task_id: UUID, current_user_id: UUID, user_role: Role
    ) -> Optional[Task]:
        task = await self.task_repo.get(task_id)
        if task is None:
            raise NotFound("Task not found")

        if user_role.value == "sales" and task.assigned_to != current_user_id:
            raise Forbidden("You can only complete your own tasks")

        updates = {
            "status": TaskStatusEnum.DONE,
            "completed_at": datetime.utcnow(),
        }
        return await self.task_repo.update(task_id, updates)

    async def delete_task(
        self,
        task_id: UUID,
        current_user_id: UUID,
        user_role: Role,
    ) -> bool:
        task = await self.task_repo.get(task_id)
        if task is None:
            raise NotFound("Task not found")

        if user_role.value == "sales" and task.assigned_to != current_user_id:
            raise Forbidden("You can only delete your own tasks")

        return await self.task_repo.delete(task_id)

    async def list_overdue_tasks(
        self, organization_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Task]:
        return await self.task_repo.list_overdue(organization_id, skip, limit)

    async def search_tasks(
        self,
        organization_id: UUID,
        query: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Task]:
        return await self.task_repo.search_by_organization(
            organization_id, query, skip, limit
        )

    async def get_task_count(self, organization_id: UUID) -> int:
        return await self.task_repo.count_by_organization(organization_id)
