from sqlalchemy import Column, String, Integer, Text, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
import enum
from datetime import datetime

from db import Base


class STATUS(str, enum.Enum):
    todo = "todo"
    in_progress = "in_progress"
    done = "done"


class PRIORITY(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"


class CampaignTaskModel(Base):
    __tablename__ = "campaign_tasks"
    id = Column(Integer, primary_key=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    assignee_id = Column(Integer, ForeignKey("users.id"), default=None)
    status = Column(Enum(STATUS), nullable=False)
    priority = Column(Enum(PRIORITY), nullable=False)
    due_date = Column(DateTime)
    created_at = Column(DateTime, nullable=False, default=datetime.now())

    assignee = relationship(
        "UserModel", back_populates="assigned_tasks"
    )  # Liên kết bảng User
    campaign = relationship(
        "CampaignModel", back_populates="tasks"
    )  # Liên kết bảng Campaign

    comments = relationship(
        "CampaignTaskCommentModel", back_populates="task", cascade="all, delete-orphan"
    )
    attachments = relationship(
        "CampaignTaskFileModel",
        back_populates="task",
        cascade="all, delete-orphan",
    )
