from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from db import Base

class CampaignTaskFileModel(Base):
    __tablename__ = "campaign_task_files"

    id = Column(Integer, primary_key=True)
    task_id = Column(
        Integer,
        ForeignKey("campaign_tasks.id"),
        nullable=False,
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )
    original_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    content_type = Column(String(100))
    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.now,
    )

    task = relationship(
        "CampaignTaskModel",
        back_populates="attachments",
    )

    user = relationship("UserModel")