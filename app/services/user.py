from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional

from models import UserModel


def get_user(email: str, db: Session):
    return db.query(UserModel).filter(UserModel.email == email).first()


def search_user(keyword: Optional[str], db: Session):
    query = db.query(UserModel)

    if keyword:
        query = query.filter(
            or_(
                UserModel.full_name.ilike(f"%{keyword}%"),
                UserModel.email.ilike(f"%{keyword}%"),
                UserModel.is_active.ilike(f"%{keyword}%"),
            )
        )

    users = query.all()

    return users
