# Phân quyền
from fastapi import Depends, status
from sqlalchemy.orm import Session
from dependencies import get_current_user
from core import AppException
from models import UserModel, CampaignMemberModel, CampaignModel
from db import get_db


class RoleCheck:
    def __init__(self, allowed_role: list):
        self.allowed_role = allowed_role

    def __call__(self, current_user: UserModel = Depends(get_current_user)):

        if current_user.role == "admin":
            return current_user

        if current_user.role not in self.allowed_role:
            raise AppException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn không có quyền truy cập",
                error=None,
            )


class CampaignRoleCheck:
    def __init__(self, allowed_role: list):
        self.allowed_role = allowed_role

    def __call__(
        self,
        campaign_id: int,
        current_user: UserModel = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        
        existing_campaign = db.query(CampaignModel).filter(CampaignModel.id == campaign_id).first()
        
        if not existing_campaign:
            raise AppException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Truy cập không thành công",
                error="Chiến dịch không tồn tại"
            )

        if current_user.role == "admin":
            return current_user
        
        membership = (
            db.query(CampaignMemberModel)
            .filter(
                CampaignMemberModel.campaign_id == campaign_id,
                CampaignMemberModel.user_id == current_user.id,
            )
            .first()
        )

        if not membership:
            raise AppException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn không phải thành viên của chiến dịch",
                error=None,
            )

        if membership.role not in self.allowed_role:
            raise AppException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn không có quyền truy cập",
                error=None,
            )

        return current_user
