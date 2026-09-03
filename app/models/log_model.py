from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from datetime import datetime

from db import Base

class LogModel(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String(50), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now)