from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class TaskCreate(BaseModel):
    contact_id: Optional[UUID] = None
    deal_id: Optional[UUID] = None
    assigned_to: UUID
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    priority: str = Field(default="medium", pattern="^(low|medium|high|urgent)$")
    due_date: Optional[datetime] = None


class TaskUpdate(BaseModel):
    contact_id: Optional[UUID] = None
    deal_id: Optional[UUID] = None
    assigned_to: Optional[UUID] = None
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = Field(None, pattern="^(low|medium|high|urgent)$")
    due_date: Optional[datetime] = None


class TaskStatusChange(BaseModel):
    status: str = Field(..., pattern="^(todo|in_progress|done|cancelled)$")


class TaskResponse(BaseModel):
    id: UUID
    organization_id: UUID
    contact_id: Optional[UUID]
    deal_id: Optional[UUID]
    assigned_to: UUID
    title: str
    description: Optional[str]
    status: str
    priority: str
    due_date: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
