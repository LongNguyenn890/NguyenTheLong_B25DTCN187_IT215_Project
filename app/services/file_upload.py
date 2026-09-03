from pathlib import Path
import shutil
import uuid
from fastapi import UploadFile
from sqlalchemy.orm import Session

from core import TASK_ATTACHMENT_FOLDER
from models import CampaignTaskFileModel, CampaignTaskModel


ALLOWED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".pdf",
    ".doc",
    ".docx",
    ".xlsx",
    ".ppt",
    ".pptx",
}

MAX_FILE_SIZE = 10 * 1024 * 1024


def upload_attachment(task_id: int, file_upload: UploadFile, current_user, db: Session):
    task = db.query(CampaignTaskModel).filter(CampaignTaskModel.id == task_id).first()
    if task is None:
        return "TASK_NOT_FOUND"

    original_name = Path(file_upload.filename or "").name
    extension = Path(original_name).suffix.lower()
    
    if extension not in ALLOWED_EXTENSIONS:
        return "INVALID_EXTENSION"
    
    if file_upload.size is not None and file_upload.size > MAX_FILE_SIZE:
        return "FILE_TOO_LARGE"
    
    task_folder = TASK_ATTACHMENT_FOLDER / f"task_{task_id}"
    
    task_folder.mkdir(parents=True, exist_ok=True)
    
    file_name = f"{uuid.uuid4()}_{original_name}"
    
    file_path = task_folder / file_name
    file_url = f"/storage/task_attachment/task_{task_id}/{file_name}"
    
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file_upload.file, buffer)
        
    attacment = CampaignTaskFileModel(
        task_id=task_id,
        user_id=current_user.id,
        original_name=original_name,
        file_path=file_url,
        file_size = file_upload.size,
        content_type = file_upload.content_type
    )
    
    db.add(attacment)
    db.commit()
    db.refresh(attacment)
    
    return attacment
    
    
    
