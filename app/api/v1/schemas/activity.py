from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class ActivityCreate(BaseModel):
    contact_id: Optional[UUID] = None
    deal_id: Optional[UUID] = None
    activity_type: str = Field(..., pattern="^(call|email|meeting|note|task)$")
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    activity_date: Optional[datetime] = None


class ActivityResponse(BaseModel):
    id: UUID
    organization_id: UUID
    contact_id: Optional[UUID]
    deal_id: Optional[UUID]
    created_by: UUID
    activity_type: str
    title: str
    description: Optional[str]
    activity_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
