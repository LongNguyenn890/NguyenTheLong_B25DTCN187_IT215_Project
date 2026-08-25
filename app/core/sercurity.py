import bcrypt
import jwt
from datetime import datetime, timezone, timedelta

from core import ACCESS_EXPIRATION_TIME_LIMIT, SECRET_KEY, ALGORITHM, REFRESH_TOKEN_EXPIRE_DAYS


def gen_hashed_password(plain_password: str) -> str:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
    return hashed_password.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def gen_access_token(email: str, full_name: str, role: str) -> str:
    now = datetime.now(timezone.utc)
    expire_time = now + timedelta(minutes=int(ACCESS_EXPIRATION_TIME_LIMIT))

    payload = {
        "sub": email,
        "role": role,
        "full_name": full_name,
        "type": "access",
        "exp": expire_time,
    }

    access_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return access_token


def gen_refresh_token(email: str, full_name: str, role: str) -> str:
    now = datetime.now(timezone.utc)
    expire_time = now + timedelta(days=int(REFRESH_TOKEN_EXPIRE_DAYS))

    payload = {
        "sub": email,
        "role": role,
        "full_name": full_name,
        "type": "refresh",
        "exp": expire_time,
    }

    access_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return access_token


def decode_access_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


def decode_refresh_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
