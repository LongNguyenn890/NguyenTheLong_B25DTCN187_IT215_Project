# Phân quyền
from fastapi import Depends, status
from sqlalchemy.orm import Session
from dependencies import get_current_user
from core import AppException
from models import UserModel, CampaignMemberModel, CampaignModel, CampaignTaskModel
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
        
        if current_user.role == "admin":
            return current_user

        existing_campaign = (
            db.query(CampaignModel).filter(
                CampaignModel.id == campaign_id, CampaignModel.is_deleted == False).first()
        )

        if not existing_campaign:
            raise AppException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Truy cập không thành công",
                error="Chiến dịch không tồn tại",
            )

        
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


class CampaignTaskRoleCheck:
    def __init__(self, allowed_role: list):
        self.allowed_role = allowed_role

    def __call__(
        self,
        task_id: int,
        current_user: UserModel = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):

        task = (
            db.query(CampaignTaskModel).filter(
                CampaignTaskModel.id == task_id,
                CampaignTaskModel.campaign.has(CampaignModel.is_deleted == False),
            ).first()
        )

        if task is None:
            raise AppException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Truy cập thất bại",
                error="Đầu việc không tồn tại",
            )

        if current_user.role == "admin":
            return current_user

        membership = (
            db.query(CampaignMemberModel)
            .filter(
                CampaignMemberModel.campaign_id == task.campaign_id,
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

        return membership
