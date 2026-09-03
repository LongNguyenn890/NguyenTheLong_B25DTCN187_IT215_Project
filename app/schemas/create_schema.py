from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Literal
from datetime import datetime


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=72)
    full_name: str = Field(..., min_length=4, max_length=100)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class CampaignCreateSchema(BaseModel):
    name: str = Field(..., min_length=4, max_length=255)
    description: Optional[str] = None


class CampaignMemberCreateSchema(BaseModel):
    user_id: int = Field(..., ge=1)


class CampaignTaskCreateSchema(BaseModel):
    title: str = Field(..., min_length=4, max_length=255)
    description: Optional[str] = None
    priority: Literal["low", "medium", "high"] = "medium"
    due_date: Optional[datetime] = None
    
class CampaignTaskCommentCreateSchema(BaseModel):
    content: str = Field(min_length=1, max_length=1000)
