from fastapi import APIRouter, Depends, status, Request, Form
from sqlalchemy.orm import Session

from core import AppException
from schemas import UserRegister, APIResponse, UserReponse, TokenResponse, UserLogin
from db import get_db
import services
from utils import make_success_response

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=APIResponse[UserReponse],
)
def register(
    req: Request, data: UserRegister = Form(...), db: Session = Depends(get_db)
):
    new_user = services.register_user(data, db)

    if new_user == "EXISIT_EMAIL":
        raise AppException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tạo tài khoản thất bại",
            error="Tài khoản đã tồn tại",
        )

    return make_success_response(
        status_code=status.HTTP_201_CREATED,
        message="Tạo tài khoản thành công",
        data=new_user,
        request=req,
    )


@router.post(
    "/login", status_code=status.HTTP_200_OK, response_model=APIResponse[TokenResponse]
)
def login(req: Request, data: UserLogin = Form(...), db: Session = Depends(get_db)):
    access_token = services.login_user(data, db)

    if access_token == "INVALID_EMAIL" or access_token == "INVALID_PASSWORD":
        raise AppException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Đăng nhập thất bại",
            error="Email hoặc mật khẩu không hợp lệ",
        )

    if access_token == "ACCOUNT_IS_LOCKED":
        raise AppException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Đăng nhập thất bại",
            error="Tài khoản đã bị khóa",
        )

    if access_token == "OVER_MAX_LOGIN_COUNT":
        raise AppException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tài khoản đã bị khóa",
            error="Vượt quá số lần đăng nhập",
        )

    return make_success_response(
        status_code=status.HTTP_200_OK,
        message="Đăng nhập thành công",
        data={"access_token": access_token},
        request=req,
    )
