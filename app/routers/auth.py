from fastapi import APIRouter, Depends, status, Request, Form
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address

from core import AppException
from schemas import (
    APIResponse,
    RefreshTokenRequest,
    TokenResponse,
    UserLogin,
    UserRegister,
    UserReponse,
)
from db import get_db
import services
from utils import make_success_response

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)
limiter = Limiter(key_func=get_remote_address)


@router.post(
    "/register",
    summary="Đăng ký tài khoản",
    description="Tạo tài khoản người dùng mới bằng thông tin biểu mẫu.",
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
    "/login",
    summary="Đăng nhập",
    description="Xác thực thông tin đăng nhập và cấp access token cùng refresh token.",
    status_code=status.HTTP_200_OK,
    response_model=APIResponse[TokenResponse],
)
@limiter.limit("5/minute")
def login(request: Request, data: UserLogin = Form(...), db: Session = Depends(get_db)):
    login_result = services.login_user(data, db)

    if login_result in ("INVALID_EMAIL", "INVALID_PASSWORD"):
        raise AppException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Đăng nhập thất bại",
            error="Email hoặc mật khẩu không hợp lệ",
        )

    if login_result == "ACCOUNT_IS_LOCKED":
        raise AppException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Đăng nhập thất bại",
            error="Tài khoản đã bị khóa",
        )

    if login_result == "OVER_MAX_LOGIN_COUNT":
        raise AppException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tài khoản đã bị khóa",
            error="Vượt quá số lần đăng nhập",
        )

    access_token, refresh_token = login_result

    return make_success_response(
        status_code=status.HTTP_200_OK,
        message="Đăng nhập thành công",
        data={
            "access_token": access_token,
            "refresh_token": refresh_token,
        },
        request=request,
    )


@router.post(
    "/refresh",
    summary="Làm mới access token",
    description="Cấp access token mới từ refresh token còn hiệu lực.",
    status_code=status.HTTP_200_OK,
    response_model=APIResponse[TokenResponse],
)
def refresh_token(
    req: Request,
    data: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    access_token = services.refresh_access_token(data.refresh_token, db)

    if access_token == "REFRESH_TOKEN_EXPIRED":
        raise AppException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Làm mới token thất bại",
            error="Refresh Token hết hạn",
        )

    if access_token == "INVALID_REFRESH_TOKEN":
        raise AppException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Làm mới token thất bại",
            error="Refresh Token không hợp lệ",
        )

    if access_token == "ACCOUNT_IS_LOCKED":
        raise AppException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Làm mới token thất bại",
            error="Tài khoản đã bị khóa",
        )

    return make_success_response(
        status_code=status.HTTP_200_OK,
        message="Làm mới token thành công",
        data={
            "access_token": access_token,
            "refresh_token": data.refresh_token,
        },
        request=req,
    )
