from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


class CampaignUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, min_length=4, max_length=255)
    description: Optional[str] = None


class CampaignTaskUpdateSchema(BaseModel):
    title: Optional[str] = Field(None, min_length=4, max_length=255)
    description: Optional[str] = None
    assignee_id: Optional[int] = Field(None, ge=1)
    status: Optional[Literal["todo", "in_progress", "done"]] = None
    priority: Optional[Literal["low", "medium", "high"]] = None
    due_date: Optional[datetime] = None


class CampaignTaskAssignSchema(BaseModel):
    assignee_id: int = Field(..., ge=1)
