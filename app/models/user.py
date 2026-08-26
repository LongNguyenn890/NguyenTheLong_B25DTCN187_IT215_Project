from sqlalchemy import Column, String, Integer, DateTime, Boolean, Enum
from sqlalchemy.orm import relationship
import enum
from datetime import datetime

from db import Base


class UserRole(str, enum.Enum):
    user = ("user",)
    admin = "admin"


class UserModel(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(Enum(UserRole), default="user")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now())

    campaigns_owned = relationship(
        "CampaignModel", back_populates="owner"
    )  # Liên kết bảng Campaign
    campaign_memberships = relationship(
        "CampaignMemberModel", back_populates="user"
    )  # Liên kết bảng Campaign Member
    assigned_tasks = relationship(
        "CampaignTaskModel", back_populates="assignee"
    )  # Liên kết bảng Campaign Task
    task_comments = relationship("CampaignTaskCommentModel", back_populates="user")