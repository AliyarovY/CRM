from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime
from decimal import Decimal


class DealCreate(BaseModel):
    contact_id: UUID
    assigned_to: Optional[UUID] = None
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    amount: Optional[Decimal] = Field(None, gt=0)
    expected_close_date: Optional[datetime] = None


class DealUpdate(BaseModel):
    assigned_to: Optional[UUID] = None
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    amount: Optional[Decimal] = Field(None, gt=0)
    status: Optional[str] = None
    expected_close_date: Optional[datetime] = None


class DealStatusChange(BaseModel):
    status: str = Field(..., pattern="^(new|in_progress|won|lost|closed)$")


class DealResponse(BaseModel):
    id: UUID
    organization_id: UUID
    contact_id: UUID
    assigned_to: Optional[UUID]
    title: str
    description: Optional[str]
    amount: Optional[Decimal]
    status: str
    expected_close_date: Optional[datetime]
    closed_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
