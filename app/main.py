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
    title="Project_FastAPI_marketing",
    version="1.0.0",
    description="Dự án quản lí API về Marketing"
)

app.state.limiter = limiter


app.add_exception_handler(
    AppException,
    http_exeption_handler
)

app.mount(
    "/storage",
    StaticFiles(directory=STORAGE_FOLDER),
    name="storage"
)


@app.get("/")
def health():
    return {
        "message": "API running"
    }


app.include_router(auth_router)
app.include_router(user_router)
app.include_router(campaign_router)
app.include_router(task_router)
