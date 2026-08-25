from fastapi import Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError
from jwt import ExpiredSignatureError, InvalidSignatureError

from db import get_db
from core import decode_access_token, AppException
from services import get_user

scheme = HTTPBearer(auto_error=False)


def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(scheme), db: Session = Depends(get_db)
):

    if creds is None:
        raise AppException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Vui lòng cung cấp Access Token",
            error=None,
        )

    token = creds.credentials

    try:
        payload = decode_access_token(token)

        user_email = payload.get("sub")

        token_type = payload.get("type")

        if token_type != "access":
            raise AppException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Xác thực thất bại",
                error="Token không phải Access Token",
            )

        if not user_email:
            raise AppException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Xác thực thất bại",
                error="Token không hợp lệ",
            )

    except ExpiredSignatureError:
        raise AppException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Xác thực thất bại",
            error="Token hết hạn",
        )

    except JWTError:
        raise AppException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Xác thực thất bại",
            error="Token không hợp lệ",
        )

    except InvalidSignatureError:
        raise AppException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Xác thực thất bại",
            error="Token không hợp lệ",
        )

    user_db = get_user(user_email, db)

    if not user_db:
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bạn không có quyền truy cập",
            error="Tài khoản không hợp lệ",
        )

    if not user_db.is_active:
        raise AppException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền truy cập",
            error="Tài khoản đã bị khóa",
        )

    return user_db
