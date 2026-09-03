from fastapi import APIRouter, Depends, status, Request, UploadFile, File
from sqlalchemy.orm import Session

from core import AppException
from dependencies import RoleCheck, CampaignTaskRoleCheck
from db import get_db
import services
from utils import make_success_response
from schemas import (
    CampaignTaskUpdateSchema,
    APIResponse,
    CampaignTaskCommentCreateSchema,
    CampaignTaskCommentResponse,
    CampaignTaskResponse,
    AttachmentResponse,
)
from models import UserModel
from dependencies import get_current_user

router = APIRouter(
    prefix="/campaign-task",
    tags=["Campaign Tasks"],
)


@router.get(
    "/{task_id}",
    summary="Chi tiết đầu việc",
    description="Xem thông tin của một đầu việc trong chiến dịch.",
    response_model=APIResponse[CampaignTaskResponse],
    dependencies=[
        Depends(RoleCheck(["user"])),
        Depends(CampaignTaskRoleCheck(["owner", "member"])),
    ],
)
def get_task_detail(req: Request, task_id: int, db: Session = Depends(get_db)):
    lst = services.get_campaign_task(task_id, db)
    return make_success_response(
        status_code=status.HTTP_200_OK,
        message="Lấy thông tin đầu việc thành công",
        data=lst,
        request=req
    )


@router.delete(
    "/{task_id}",
    summary="Xóa đầu việc",
    description="Xóa đầu việc; chỉ chủ sở hữu đầu việc được phép thực hiện.",
    response_model=APIResponse[None],
    dependencies=[
        Depends(RoleCheck(["user"])),
        Depends(CampaignTaskRoleCheck(["owner"])),
    ],
)
def delete_task(req: Request, task_id: int, db: Session = Depends(get_db)):
    deleted_task = services.delete_campaign_task(task_id, db)

    if deleted_task == "TASK_NOT_FOUND":
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Xóa đầu việc thất bại",
            error="Đầu việc không tồn tại",
        )

    return make_success_response(
        status_code=status.HTTP_200_OK,
        message="Xóa việc thành công",
        data=deleted_task,
        request=req,
    )


@router.patch(
    "/{task_id}",
    summary="Cập nhật đầu việc",
    description="Cập nhật đầu việc theo quyền của người dùng trong chiến dịch.",
    response_model=APIResponse[CampaignTaskResponse],
    dependencies=[Depends(RoleCheck(["user"]))],
)
def update_task(
    req: Request,
    task_id: int,
    data: CampaignTaskUpdateSchema,
    current_user: UserModel = Depends(
        CampaignTaskRoleCheck(["owner", "member"])),
    db: Session = Depends(get_db),
):
    updated_data = services.update_task(task_id, current_user, data, db)

    if updated_data == "TASK_NOT_FOUND":
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cập nhật thất bại",
            error="Đầu việc không tồn tại",
        )

    if updated_data == "ACCESS_DENIED":
        raise AppException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cập nhật thất bại",
            error="Bạn không có quyền cập nhật đầu việc khác",
        )

    if updated_data == "USER_NOT_FOUND":
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cập nhật thất bại",
            error=f"Người dùng {data.assignee_id} không tồn tại",
        )

    if updated_data == "NOT_MEMBER":
        raise AppException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cập nhật thất bại",
            error=f"Người dùng {data.assignee_id} Không phải thành viên của chiến dịch",
        )

    if updated_data == "CANNOT_UPDATE_PRIORITY":
        raise AppException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cập nhật thất bại",
            error="Bạn không có quyền cập nhật priority",
        )

    return make_success_response(
        status_code=status.HTTP_200_OK,
        message="Cập nhật thành công",
        data=updated_data,
        request=req,
    )


@router.post(
    "/{task_id}/comments",
    summary="Thêm bình luận",
    description="Tạo bình luận mới cho một đầu việc.",
    response_model=APIResponse[CampaignTaskCommentResponse],
    dependencies=[
        Depends(RoleCheck(["user"])),
        Depends(CampaignTaskRoleCheck(["owner", "member"])),
    ],status_code=status.HTTP_201_CREATED
)
def create_comment(
    req: Request,
    task_id: int,
    data: CampaignTaskCommentCreateSchema,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    new_comment = services.create_comment(task_id, data, current_user, db)

    return make_success_response(
        status_code=status.HTTP_201_CREATED,
        message="Thêm comment thành công",
        data=new_comment,
        request=req,
    )


@router.get(
    "/{task_id}/comments",
    summary="Danh sách bình luận",
    description="Lấy toàn bộ bình luận của một đầu việc.",
    response_model=APIResponse[list[CampaignTaskCommentResponse]],
    dependencies=[
        Depends(RoleCheck(["user"])),
        Depends(CampaignTaskRoleCheck(["owner", "member"]))
    ]
)
def get_comments(req: Request, task_id: int, db: Session = Depends(get_db)):
    comments = services.get_comments(task_id, db)

    return make_success_response(
        status_code=status.HTTP_200_OK,
        message="Chi tiết commnets",
        data=comments,
        request=req
    )


@router.post(
    "/{task_id}/attachments",
    summary="Tải tệp đính kèm",
    description="Tải tệp lên và liên kết tệp với một đầu việc.",
    response_model=APIResponse[AttachmentResponse],
    dependencies=[
        Depends(RoleCheck(["user"])),
        Depends(CampaignTaskRoleCheck(["owner", "member"])),
    ],
)
def upload_file(
    req: Request,
    task_id: int,
    file_upload: UploadFile = File(...),
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    attachment = services.upload_attachment(
        task_id, file_upload, current_user, db)

    if attachment == "INVALID_EXTENSION":
        raise AppException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Upload file thất bại",
            error="Định dạng file không được hỗ trợ",
        )

    if attachment == "FILE_TOO_LARGE":
        raise AppException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Upload file thất bại",
            error="File vượt quá kích thước cho phép",
        )

    return make_success_response(
        status_code=status.HTTP_201_CREATED,
        message="Upload file thành công",
        data=attachment,
        request=req,
    )
