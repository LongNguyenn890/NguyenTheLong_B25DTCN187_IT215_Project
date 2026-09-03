from sqlalchemy.orm import Session

from schemas import CampaignTaskCommentCreateSchema
from models import CampaignTaskCommentModel, CampaignTaskModel, UserModel

def create_comment(task_id: int, data: CampaignTaskCommentCreateSchema, current_user: UserModel, db: Session):
    task = db.query(CampaignTaskModel).filter(CampaignTaskModel.id == task_id).first()
    if task is None:
        return "TASK_NOT_FOUND"

    new_comment = CampaignTaskCommentModel(
        task_id = task_id,
        user_id = current_user.id,
        content = data.content
    )
    
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    
    return new_comment

def get_comments(task_id: int, db: Session):
    task = db.query(CampaignTaskModel).filter(CampaignTaskModel.id == task_id).first()
    if task is None:
        return "TASK_NOT_FOUND"

    lst = db.query(CampaignTaskCommentModel).filter(CampaignTaskCommentModel.task_id == task_id).order_by(CampaignTaskCommentModel.created_at.asc()).all()
    return lst