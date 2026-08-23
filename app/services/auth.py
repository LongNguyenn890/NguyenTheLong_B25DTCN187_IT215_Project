from sqlalchemy.orm import Session

from schemas import UserRegister, UserLogin
from models import UserModel
from core import gen_hashed_password, gen_access_token, verify_password
from core import MAX_LOGIN


def register_user(data: UserRegister, db: Session):
    exisiting_email = db.query(UserModel).filter(UserModel.email == data.email).first()

    if exisiting_email:
        return "EXISIT_EMAIL"

    hashed_password = gen_hashed_password(data.password)

    new_user = UserModel(
        email=data.email,
        password_hash=hashed_password,
        full_name=data.full_name.capitalize(),
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
        user_db.login_attempt += 1

        if user_db.login_attempt > int(MAX_LOGIN):
            user_db.is_active = False
            db.commit()
            db.refresh(user_db)
            return "OVER_MAX_LOGIN_COUNT"

        db.commit()
        db.refresh(user_db)

        return "INVALID_PASSWORD"

    access_token = gen_access_token(user_db.email, user_db.full_name, user_db.role)
    user_db.login_attempt = 0
    user_db.is_active = True

    db.commit()
    db.refresh(user_db)

    return access_token
