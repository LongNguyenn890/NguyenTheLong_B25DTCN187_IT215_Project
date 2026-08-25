from fastapi import APIRouter, status, Depends, Request, Query
from sqlalchemy.orm import Session
from typing import Optional, Literal

from schemas import (
    APIResponse,
    CampaignCreateSchema,
    CampaignResponse,
    CampaignMemberCreateSchema,
    CampaignUpdateSchema,
    CampaignMemberResponse,
    CampaignTaskCreateSchema,
    CampaignTaskResponse,
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
    dependencies=[
        Depends(RoleCheck(["user"])),
        Depends(CampaignRoleCheck(["owner", "member"])),
    ],
)
def get_campaign(
    req: Request,
    campaign_id: int,
    db: Session = Depends(get_db),
):
    campaign = services.get_campaign_detail(campaign_id, db)

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


@router.post(
    "/{campaign_id}/members",
    dependencies=[Depends(RoleCheck(["user"])), Depends(
        CampaignRoleCheck(["owner"]))],
)
def add_member(
    req: Request,
    campaign_id: int,
    campaign_member: CampaignMemberCreateSchema,
    db: Session = Depends(get_db),
):
    new_member, error = services.add_member(campaign_id, campaign_member, db)

    if error == "NOT_EXISTED_USER":
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thêm thành viên mới thất bại",
            error="Mã người dùng không tồn tại",
        )

    if error == "EXISTED_MEMBER":
        raise AppException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Thêm thành viên mới thất bại",
            error="Thành viên đã tham gia chiến dịch",
        )

    return make_success_response(
        status_code=status.HTTP_200_OK,
        message=f"Thêm thành viên mới thành công",
        data=new_member,
        request=req,
    )


@router.patch(
    "/{campaign_id}",
    dependencies=[Depends(RoleCheck(["user"])), Depends(
        CampaignRoleCheck(["owner"]))],
)
def update_campaign(
    req: Request,
    campaign_id: int,
    data: CampaignUpdateSchema,
    db: Session = Depends(get_db),
):
    updated_campaign = services.update_campaign(campaign_id, data, db)
    return make_success_response(
        status_code=status.HTTP_200_OK,
        message=f"Cập nhật chiến dịch thành công",
        data=updated_campaign,
        request=req,
    )


@router.delete(
    "/{campaign_id}",
    response_model=APIResponse,
    dependencies=[Depends(RoleCheck(["user"])), Depends(
        CampaignRoleCheck(["owner"]))],
)
def delete_campaign(
    req: Request,
    campaign_id: int,
    db: Session = Depends(get_db),
):
    deleted_campaign = services.delete_campaign(campaign_id, db)

    return make_success_response(
        status_code=status.HTTP_200_OK,
        message="Xóa chiến dịch thành công",
        data=deleted_campaign,
        request=req,
    )


@router.get(
    "/{campaign_id}/members",
    response_model=APIResponse[list[CampaignMemberResponse]],
    dependencies=[
        Depends(RoleCheck(["user"])),
        Depends(CampaignRoleCheck(["owner", "member"])),
    ],
)
def get_members(req: Request, campaign_id: int, db: Session = Depends(get_db)):
    members_list = services.get_all_members(campaign_id, db)
    return make_success_response(
        status_code=status.HTTP_200_OK,
        message="Danh sách thành viên chiến dịch",
        data=members_list,
        request=req,
    )


@router.delete(
    "/{campaign_id}/members/{user_id}",
    dependencies=[Depends(RoleCheck(["user"])), Depends(
        CampaignRoleCheck(["owner"]))],
)
def remove_member(
    req: Request, campaign_id: int, user_id: int, db: Session = Depends(get_db)
):
    deleted_members = services.delete_member(campaign_id, user_id, db)

    if deleted_members == "MEMBER_NOT_EXIST":
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Xóa thành viên thất bại",
            error="Không tìm thấy thành viên",
        )

    if deleted_members.role == "CANNOT_DELETE_OWNER":
        raise AppException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Xóa thành viên thất bại",
            error="Không thể xóa chủ sở hữu chiến dịch",
        )

    return make_success_response(
        status_code=status.HTTP_200_OK,
        message="Xóa thành viên thành công",
        data=None,
        request=req,
    )


@router.post(
    "/{campaign_id}/campaign_tasks",
    response_model=APIResponse[CampaignTaskResponse],
    dependencies=[
        Depends(RoleCheck(["user"])),
        Depends(CampaignRoleCheck(["owner", "member"])),
    ],
)
def create_task(
    req: Request,
    campaign_id: int,
    campaign_task: CampaignTaskCreateSchema,
    db: Session = Depends(get_db),
):
    new_campaign = services.create_campaign_task(
        campaign_id, campaign_task, db)

    if new_campaign == "NOT_MEMBER":
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tạo đầu việc chiến dịch không thành công",
            error="Thành viên không tồn tại",
        )

    return make_success_response(
        status_code=status.HTTP_200_OK,
        message="Tạo mới chiến dịch thành công",
        data=new_campaign,
        request=req,
    )


@router.get(
    "/{campaign_id}/campaign_tasks",
    response_model=APIResponse[list[CampaignTaskResponse]],
    dependencies=[
        Depends(RoleCheck(["user"])),
        Depends(CampaignRoleCheck(["owner", "member"])),
    ],
)
def get_tasks(
    req: Request,
    campaign_id: int,
    task_status: Optional[Literal["todo", "in_progress", "done"]] = Query(
        None, alias="status"
    ),
    priority: Optional[Literal["low", "medium", "high"]] = Query(None),
    title: Optional[str] = Query(None),
    page: Optional[int] = 1,
    size: Optional[int] = 5,
    db: Session = Depends(get_db),
):
    tasks = services.get_campaign_tasks(
        campaign_id, task_status, priority, title, page, size, db
    )

    return make_success_response(
        status_code=status.HTTP_200_OK,
        message=f"Danh sách đầu việc chiến dịch {campaign_id}",
        data=tasks,
        request=req,
    )
