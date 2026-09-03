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
from utils import make_success_response,add_log
import services
from models import UserModel

router = APIRouter(
    prefix="/campaigns",
    tags=["Campaign"],
)


@router.post(
    "/",
    summary="Tạo chiến dịch",
    description="Tạo chiến dịch mới và gán người dùng hiện tại làm chủ sở hữu.",
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
    
    add_log(user_id=current_user.id, action="CREATE_NEW_CAMPAIGN", message=f"Tạo campaign {new_campaign.name}", db=db)
    
    return make_success_response(
        status_code=status.HTTP_201_CREATED,
        message="Tạo chiến dịch mới thành công",
        data=new_campaign,
        request=req,
    )


@router.get(
    "/",
    summary="Danh sách chiến dịch",
    description="Lấy các chiến dịch mà người dùng hiện tại sở hữu hoặc tham gia.",
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
    summary="Chi tiết chiến dịch",
    description="Xem thông tin chi tiết của chiến dịch mà người dùng có quyền truy cập.",
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
    summary="Thêm thành viên",
    description="Thêm người dùng vào chiến dịch; chỉ chủ sở hữu được phép thực hiện.",
    status_code=status.HTTP_201_CREATED,
    response_model=APIResponse[CampaignMemberResponse],
    dependencies=[Depends(RoleCheck(["user"])), Depends(
        CampaignRoleCheck(["owner"]))],
)
def add_member(
    req: Request,
    campaign_id: int,
    campaign_member: CampaignMemberCreateSchema,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    new_member, error = services.add_member(campaign_id, campaign_member, db)

    if error == "CAMPAIGN_NOT_FOUND":
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thêm thành viên mới thất bại",
            error="Chiến dịch không tồn tại",
        )


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
        
    add_log(
        user_id=current_user.id,
        action="ADD_MEMBER",
        message=f"Thêm user {campaign_member.user_id} vào campaign {campaign_id}",
        db=db,
    )

    return make_success_response(
        status_code=status.HTTP_201_CREATED,
        message=f"Thêm thành viên mới thành công",
        data=new_member,
        request=req,
    )


@router.patch(
    "/{campaign_id}",
    summary="Cập nhật chiến dịch",
    description="Cập nhật thông tin chiến dịch; chỉ chủ sở hữu được phép thực hiện.",
    response_model=APIResponse[CampaignResponse],
    dependencies=[Depends(RoleCheck(["user"])), Depends(
        CampaignRoleCheck(["owner"]))],
)
def update_campaign(
    req: Request,
    campaign_id: int,
    data: CampaignUpdateSchema,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    updated_campaign = services.update_campaign(campaign_id, data, db)

    if updated_campaign is None:
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cập nhật chiến dịch thất bại",
            error="Chiến dịch không tồn tại",
        )
    
    add_log(user_id=current_user.id, action="UPDATE_CAMPAIGN", message=f"Cập nhật campaign {campaign_id}", db=db)
    
    return make_success_response(
        status_code=status.HTTP_200_OK,
        message=f"Cập nhật chiến dịch thành công",
        data=updated_campaign,
        request=req,
    )


@router.delete(
    "/{campaign_id}",
    summary="Xóa chiến dịch",
    description="Xóa một chiến dịch do người dùng hiện tại sở hữu.",
    response_model=APIResponse[CampaignResponse],
    dependencies=[Depends(RoleCheck(["user"])), Depends(
        CampaignRoleCheck(["owner"]))],
)
def delete_campaign(
    req: Request,
    campaign_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    deleted_campaign = services.delete_campaign(campaign_id, db)

    if deleted_campaign is None:
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Xóa chiến dịch thất bại",
            error="Chiến dịch không tồn tại hoặc đã bị xóa",
        )

    add_log(
        user_id=current_user.id,
        action="DELETE_CAMPAIGN",
        message=f"Xóa campaign {campaign_id}",
        db=db,
    )

    return make_success_response(
        status_code=status.HTTP_200_OK,
        message="Xóa chiến dịch thành công",
        data=deleted_campaign,
        request=req,
    )


@router.get(
    "/{campaign_id}/members",
    summary="Danh sách thành viên",
    description="Lấy danh sách thành viên của chiến dịch.",
    response_model=APIResponse[list[CampaignMemberResponse]],
    dependencies=[
        Depends(RoleCheck(["user"])),
        Depends(CampaignRoleCheck(["owner", "member"])),
    ],
)
def get_members(req: Request, campaign_id: int, db: Session = Depends(get_db)):
    members_list = services.get_all_members(campaign_id, db)

    if members_list == "CAMPAIGN_NOT_FOUND":
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lấy danh sách thành viên thất bại",
            error="Chiến dịch không tồn tại",
        )

    return make_success_response(
        status_code=status.HTTP_200_OK,
        message="Danh sách thành viên chiến dịch",
        data=members_list,
        request=req,
    )


@router.delete(
    "/{campaign_id}/members/{user_id}",
    summary="Xóa thành viên",
    description="Xóa thành viên khỏi chiến dịch; không thể xóa chủ sở hữu.",
    dependencies=[Depends(RoleCheck(["user"])), Depends(
        CampaignRoleCheck(["owner"]))],
)
def remove_member(
    req: Request, campaign_id: int, user_id: int,current_user: UserModel = Depends(get_current_user), db: Session = Depends(get_db)
):
    deleted_members = services.delete_member(campaign_id, user_id, db)

    if deleted_members == "CAMPAIGN_NOT_FOUND":
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Xóa thành viên thất bại",
            error="Chiến dịch không tồn tại",
        )

    if deleted_members == "MEMBER_NOT_EXIST":
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Xóa thành viên thất bại",
            error="Không tìm thấy thành viên",
        )

    if deleted_members == "CANNOT_DELETE_OWNER":
        raise AppException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Xóa thành viên thất bại",
            error="Không thể xóa chủ sở hữu chiến dịch",
        )
        
    add_log(
        user_id=current_user.id,
        action="DELETE_MEMBER",
        message=f"Xóa user {user_id} khỏi campaign {campaign_id}",
        db=db,
    )

    return make_success_response(
        status_code=status.HTTP_200_OK,
        message="Xóa thành viên thành công",
        data=None,
        request=req,
    )


@router.post(
    "/{campaign_id}/campaign_tasks",
    summary="Tạo đầu việc",
    description="Tạo một đầu việc mới trong chiến dịch.",
    status_code=status.HTTP_201_CREATED,
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
    current_user: UserModel = Depends(get_current_user),
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

    add_log(
        user_id=current_user.id,
        action="CREATE_TASK",
        message=f"Tạo task trong campaign {campaign_id}",
        db=db,
    )

    return make_success_response(
        status_code=status.HTTP_201_CREATED,
        message="Tạo đầu việc thành công",
        data=new_campaign,
        request=req,
    )


@router.get(
    "/{campaign_id}/campaign_tasks",
    summary="Danh sách đầu việc",
    description="Lấy danh sách đầu việc với bộ lọc, sắp xếp và phân trang.",
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
    page: int = Query(1, ge=1, description="Số trang, bắt đầu từ 1."),
    size: int = Query(5, ge=1, le=100, description="Số đầu việc mỗi trang."),
    order_by: Optional[Literal["created_at", "due_date"]] = Query(None),
    db: Session = Depends(get_db),
):
    tasks = services.get_campaign_tasks(
        campaign_id, task_status, priority, title, page, size, order_by, db
    )

    return make_success_response(
        status_code=status.HTTP_200_OK,
        message=f"Danh sách đầu việc chiến dịch {campaign_id}",
        data=tasks,
        request=req,
    )
