from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter
from slowapi.util import get_remote_address

from db import Base, engine
import models
from core import AppException, STORAGE_FOLDER
from core.exception_handler import http_exeption_handler
from routers import auth_router, user_router, campaign_router, task_router

Base.metadata.create_all(bind=engine)

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Campaign Management API",
    version="1.0.0",
    summary="API quản lý chiến dịch marketing",
    description=(
        "API hỗ trợ quản lý chiến dịch marketing, thành viên, đầu việc, "
        "bình luận và tệp đính kèm. API sử dụng JWT để xác thực và phân quyền "
        "theo vai trò người dùng trong từng chiến dịch."
    ),
)

app.state.limiter = limiter


app.add_exception_handler(AppException, http_exeption_handler)

app.mount("/storage", StaticFiles(directory=STORAGE_FOLDER), name="storage")


@app.get("/")
def health():
    return {"message": "API running"}


app.include_router(auth_router)
app.include_router(user_router)
app.include_router(campaign_router)
app.include_router(task_router)
