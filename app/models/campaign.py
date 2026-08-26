from sqlalchemy import Column, String, Integer, Text, ForeignKey, DateTime, Enum, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from db import Base


class CampaignModel(Base):
    __tablename__ = "campaigns"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    owner_id = Column(Integer, ForeignKey("users.id"))
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now())

    owner = relationship(
        "UserModel", back_populates="campaigns_owned"
    )  # Liên kết bảng User
    campaign_members = relationship(
        "CampaignMemberModel", back_populates="campaign", cascade="all, delete-orphan"
    )  # Liên kết bảng Campaign Member
    tasks = relationship(
        "CampaignTaskModel", back_populates="campaign", cascade="all, delete-orphan"
    )  # Liên kết bảng Campaign Task


class Role(str, enum.Enum):
    member = "member"
    owner = "owner"


class CampaignMemberModel(Base):
    __tablename__ = "campaign_members"
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    role = Column(Enum(Role), nullable=False)
    joined_at = Column(DateTime, nullable=False, default=datetime.now())

    campaign = relationship("CampaignModel", back_populates="campaign_members")
    user = relationship("UserModel", back_populates="campaign_memberships")
