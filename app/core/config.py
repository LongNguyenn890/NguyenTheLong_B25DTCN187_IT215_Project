import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_EXPIRATION_TIME_LIMIT = os.getenv("ACCESS_EXPIRATION_TIME_LIMIT")
REFRESH_TOKEN_EXPIRE_DAYS = os.getenv("REFRESH_TOKEN_EXPIRE_DAYS")


STORAGE_FOLDER = Path("storage")
TASK_ATTACHMENT_FOLDER = STORAGE_FOLDER / "task_attachment"

TASK_ATTACHMENT_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)