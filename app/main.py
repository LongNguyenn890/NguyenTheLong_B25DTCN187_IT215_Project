from fastapi import FastAPI

from db import Base, engine
import models
from core import AppException
from core.exception_handler import http_exeption_handler
from routers import auth_router, user_router, campaign_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Project_FastAPI_marketing",
    version="1.0.0",
    description="Dự án quản lí API về Marketing"
)

app.add_exception_handler(
    AppException,
    http_exeption_handler
)

@app.get("/")
def health():
    return {
        "message": "API running"
    }
    

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(campaign_router)