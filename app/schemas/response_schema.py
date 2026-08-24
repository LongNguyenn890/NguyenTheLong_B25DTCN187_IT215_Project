from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, Generic, TypeVar

T = TypeVar("T")  # Biến kiểu dữ liệu


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserReponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class CampaignResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    owner_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
    

class CampaignMemberResponse(BaseModel):
    id: int
    full_name: str
    email: str
    role: str
        
    model_config = ConfigDict(from_attributes=True)


class CampaignTaskResponse(BaseModel):
    id: int
    campaign_id: int
    title: int
    description: Optional[str] = None
    assignee_id: Optional[int] = None
    status: str
    priority: str
    due_date: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class APIResponse(BaseModel, Generic[T]):
    statusCode: int
    message: str
    error: Optional[str] = None
    data: T
    url: str
    timestamp: datetime
