import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_EXPIRATION_TIME_LIMIT = os.getenv("ACCESS_EXPIRATION_TIME_LIMIT")
MAX_LOGIN = os.getenv("MAX_LOGIN")
