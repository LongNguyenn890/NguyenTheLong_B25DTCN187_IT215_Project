from fastapi import APIRouter, status, Depends, Request
from sqlalchemy.orm import Session
from typing import Optional

from schemas import (
    APIResponse,
    CampaignCreateSchema,
    CampaignResponse,
    CampaignMemberCreateSchema,
)
from dependencies import get_current_user, RoleCheck, CampaignRoleCheck
from db import get_db
from core import AppException
from utils import make_success_response
import services
from models import UserModel

router = APIRouter(prefix="/campaigns", tags=["Campaign"])


@router.post(
    "/",
    response_model=APIResponse[CampaignResponse],
    dependencies=[Depends(RoleCheck(["user"]))],
)
def create_campaign(
    req: Request,
    campaign: CampaignCreateSchema,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    new_campaign = services.create_new_campaign(campaign, current_user, db)
    return make_success_response(
        status_code=status.HTTP_201_CREATED,
        message="Tạo chiến dịch mới thành công",
        data=new_campaign,
        request=req,
    )


@router.get(
    "/",
    response_model=APIResponse[list[CampaignResponse]],
    dependencies=[Depends(RoleCheck(["user"]))],
)
def get_campaigns(
    req: Request,
    keyword: Optional[str] = None,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    lst = services.get_campaign_list(keyword, current_user, db)
    return make_success_response(
        status_code=status.HTTP_200_OK,
        message=f"Thông tin chi tiết chiến dịch của bạn",
        data=lst,
        request=req,
    )


@router.get(
    "/{campaign_id}",
    response_model=APIResponse[CampaignResponse],
    dependencies=[Depends(RoleCheck(["user"]))],
)
def get_campaign(
    req: Request,
    campaign_id: int,
    current_user: UserModel = Depends(CampaignRoleCheck(["owner", "member"])),
    db: Session = Depends(get_db),
):
    campaign = services.get_campaign_detail(campaign_id, current_user, db)

    if campaign is None:
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lấy thông tin chiến dịch không thành công",
            error="Thông tin chiến dịch không tồn tại",
        )

    return make_success_response(
        status_code=status.HTTP_200_OK,
        message=f"Thông tin chi tiết chiến dịch {campaign_id}",
        data=campaign,
        request=req,
    )


@router.post("/{campaign_id}/members", dependencies=[Depends(RoleCheck(["user"]))])
def add_member(
    req: Request,
    campaign_id: int,
    campaign_member: CampaignMemberCreateSchema,
    current_user: UserModel = Depends(CampaignRoleCheck(["owner"])),
    db: Session = Depends(get_db),
):
    new_member,error = services.add_member(campaign_id, current_user, campaign_member, db)
    
    if error == "NOT_EXISTED_USER":
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thêm thành viên mới thất bại",
            error="Mã người dùng không tồn tại"
        )
        
    if error == "EXISTED_MEMBER":
        raise AppException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Thêm thành viên mới thất bại",
            error="Thành viên đã tham gia chiến dịch"
        )
        

    return make_success_response(
        status_code=status.HTTP_200_OK,
        message=f"Thêm thành viên mới thành công",
        data=new_member,
        request=req,
    )
