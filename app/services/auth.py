from sqlalchemy.orm import Session

from schemas import UserRegister, UserLogin
from models import UserModel
from core import (
    decode_refresh_token,
    gen_access_token,
    gen_hashed_password,
    gen_refresh_token,
    verify_password,
)
from jwt import ExpiredSignatureError, InvalidTokenError


def register_user(data: UserRegister, db: Session):
    exisiting_email = db.query(UserModel).filter(
        UserModel.email == data.email).first()

    if exisiting_email:
        return "EXISIT_EMAIL"

    hashed_password = gen_hashed_password(data.password)

    new_user = UserModel(
        email=data.email,
        password_hash=hashed_password,
        full_name=data.full_name.title(),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


def login_user(data: UserLogin, db: Session):

    user_db = db.query(UserModel).filter(UserModel.email == data.email).first()

    if not user_db:
        return "INVALID_EMAIL"

    if not user_db.is_active:
        return "ACCOUNT_IS_LOCKED"

    if not verify_password(data.password, user_db.password_hash):
        return "INVALID_PASSWORD"

    access_token = gen_access_token(
        user_db.email, user_db.full_name, user_db.role)
    refresh_token = gen_refresh_token(
        user_db.email, user_db.full_name, user_db.role)

    db.commit()
    db.refresh(user_db)

    return access_token, refresh_token


def refresh_access_token(refresh_token: str, db: Session):
    try:
        payload = decode_refresh_token(refresh_token)
    except ExpiredSignatureError:
        return "REFRESH_TOKEN_EXPIRED"
    except InvalidTokenError:
        return "INVALID_REFRESH_TOKEN"

    if payload.get("type") != "refresh" or not payload.get("sub"):
        return "INVALID_REFRESH_TOKEN"

    user_db = db.query(UserModel).filter(
        UserModel.email == payload["sub"]).first()

    if not user_db:
        return "INVALID_REFRESH_TOKEN"

    if not user_db.is_active:
        return "ACCOUNT_IS_LOCKED"

    return gen_access_token(user_db.email, user_db.full_name, user_db.role)
