import os
from dotenv import load_dotenv
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = APP_DIR.parent
load_dotenv(APP_DIR / ".env")
load_dotenv(PROJECT_DIR / ".env", override=False)

DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_EXPIRATION_TIME_LIMIT = os.getenv("ACCESS_EXPIRATION_TIME_LIMIT")
REFRESH_TOKEN_EXPIRE_DAYS = os.getenv("REFRESH_TOKEN_EXPIRE_DAYS")


STORAGE_FOLDER = PROJECT_DIR / "storage"
TASK_ATTACHMENT_FOLDER = STORAGE_FOLDER / "task_attachment"

TASK_ATTACHMENT_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)
