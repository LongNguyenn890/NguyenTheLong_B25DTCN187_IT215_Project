from fastapi import APIRouter, status, Depends, Request, Query
from sqlalchemy.orm import Session
from typing import Optional

from dependencies import get_current_user, RoleCheck
from schemas import UserReponse, APIResponse
from utils import make_success_response
from db import get_db
from services import search_user

ALLOWED_ADMIN = RoleCheck(allowed_role=["admin"])

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=APIResponse[UserReponse])
def get_me(req: Request, current_user: dict = Depends(get_current_user)):
    return make_success_response(
        status_code=status.HTTP_200_OK,
        message="Thông tin chi tiết tài khoản",
        data=current_user,
        request=req,
    )


@router.get(
    "/",
    response_model=APIResponse[list[UserReponse]],
    dependencies=[Depends(ALLOWED_ADMIN)],
)
def search_user_infor(
    req: Request,
    keyword: Optional[str] = Query(
        None, description="Tìm kiếm theo email, tên, trạng thái"
    ),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
):
    users = search_user(keyword, is_active, db)

    return make_success_response(
        status_code=status.HTTP_200_OK,
        message="Danh sách người dùng tìm kiếm",
        data=users,
        request=req,
    )
