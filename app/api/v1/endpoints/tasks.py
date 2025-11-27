from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Optional, List

from app.database import get_db
from app.models import User, TaskStatusEnum
from app.api.v1.dependencies import get_current_user, get_organization_context, check_organization_member
from app.api.v1.schemas import TaskCreate, TaskUpdate, TaskStatusChange, TaskResponse
from app.services import TaskService
from app.core.exceptions import BadRequest, Forbidden
from app.core.permissions import Role

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=List[TaskResponse])
async def list_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    organization_id: UUID = Depends(get_organization_context),
    db: AsyncSession = Depends(get_db),
):
    await check_organization_member(current_user, organization_id, db)

    service = TaskService(db)

    if search:
        tasks = await service.search_tasks(organization_id, search, skip, limit)
    elif status:
        try:
            status_enum = TaskStatusEnum[status.upper()]
            tasks = await service.list_tasks_for_user(organization_id, current_user.id, skip, limit)
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status",
            )
    else:
        tasks = await service.list_tasks_for_user(organization_id, current_user.id, skip, limit)

    return tasks


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    request: TaskCreate,
    current_user: User = Depends(get_current_user),
    organization_id: UUID = Depends(get_organization_context),
    db: AsyncSession = Depends(get_db),
):
    await check_organization_member(current_user, organization_id, db)

    service = TaskService(db)
    try:
        task = await service.create_task(
            organization_id=organization_id,
            **request.model_dump()
        )
        return task
    except BadRequest as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    organization_id: UUID = Depends(get_organization_context),
    db: AsyncSession = Depends(get_db),
):
    await check_organization_member(current_user, organization_id, db)

    service = TaskService(db)
    task = await service.get_task(task_id)

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return task


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: UUID,
    request: TaskUpdate,
    current_user: User = Depends(get_current_user),
    organization_id: UUID = Depends(get_organization_context),
    db: AsyncSession = Depends(get_db),
):
    await check_organization_member(current_user, organization_id, db)

    org_member = await check_organization_member(current_user, organization_id, db)
    user_role = Role(org_member.role)

    service = TaskService(db)
    updates = request.model_dump(exclude_unset=True)

    try:
        task = await service.update_task(task_id, updates, current_user.id, user_role)
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )
        return task
    except (BadRequest, Forbidden) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST if isinstance(e, BadRequest) else status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.post("/{task_id}/complete", response_model=TaskResponse)
async def complete_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    organization_id: UUID = Depends(get_organization_context),
    db: AsyncSession = Depends(get_db),
):
    await check_organization_member(current_user, organization_id, db)

    org_member = await check_organization_member(current_user, organization_id, db)
    user_role = Role(org_member.role)

    service = TaskService(db)
    try:
        task = await service.complete_task(task_id, current_user.id, user_role)
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )
        return task
    except Forbidden as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    organization_id: UUID = Depends(get_organization_context),
    db: AsyncSession = Depends(get_db),
):
    await check_organization_member(current_user, organization_id, db)

    org_member = await check_organization_member(current_user, organization_id, db)
    user_role = Role(org_member.role)

    service = TaskService(db)
    try:
        success = await service.delete_task(task_id, current_user.id, user_role)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )
    except Forbidden as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )

    return None
