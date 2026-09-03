from sqlalchemy.orm import Session

from schemas import CampaignTaskCreateSchema, CampaignTaskUpdateSchema
from models import CampaignTaskModel, CampaignMemberModel, UserModel


def create_campaign_task(
    campaign_id: int, campaign_task: CampaignTaskCreateSchema, db: Session
):

    existing_member = db.query(CampaignMemberModel).filter(
        CampaignMemberModel.campaign_id == campaign_id
    ).first()

    if not existing_member:
        return "NOT_MEMBER"

    new_campaign = CampaignTaskModel(
        campaign_id=campaign_id,
        title=campaign_task.title,
        description=campaign_task.description,
        priority=campaign_task.priority,
        status = "todo",
        due_date=campaign_task.due_date,
    )

    db.add(new_campaign)
    db.commit()
    db.refresh(new_campaign)

    return new_campaign


def get_campaign_tasks(campaign_id: int, status: str, priority: str, title: str, page: int, size: int, sorted_by: str, db: Session):
    query = (
        db.query(CampaignTaskModel)
        .filter(CampaignTaskModel.campaign_id == campaign_id)
    )

    if status:
        query = query.filter(CampaignTaskModel.status == status)

    if priority:
        query = query.filter(CampaignTaskModel.priority == priority)

    if title:
        query = query.filter(CampaignTaskModel.title.ilike(f"%{title}%"))
        
    if sorted_by == "created_at":
        query = query.order_by(CampaignTaskModel.created_at.desc())
    
    if sorted_by == "due_date":
        query = query.order_by(CampaignTaskModel.due_date.desc())

    lst = query.offset(offset=(page - 1) * size).limit(limit=size).all()

    return lst


def get_campaign_task(task_id: int, db: Session):
    task = (
        db.query(CampaignTaskModel).filter(
            CampaignTaskModel.id == task_id).first()
    )
    return task


def delete_campaign_task(task_id: int, db: Session):
    task = db.query(CampaignTaskModel).filter(
        CampaignTaskModel.id == task_id).first()

    if task is None:
        return "TASK_NOT_FOUND"

    db.delete(task)
    db.commit()

    return None


def update_task(task_id: int, current_user: CampaignMemberModel, data: CampaignTaskUpdateSchema, db: Session):

    task = db.query(CampaignTaskModel).filter(
        CampaignTaskModel.id == task_id).first()

    if task is None:
        return "TASK_NOT_FOUND"

    if current_user.role == "member" and task.assignee_id != current_user.user_id:
        return "ACCESS_DENIED"

    if data.assignee_id is not None:
        assignee = db.query(UserModel).filter(
            UserModel.id == data.assignee_id
        ).first()

        if assignee is None:
            return "USER_NOT_FOUND"

        existing_member = db.query(CampaignMemberModel).filter(
            CampaignMemberModel.campaign_id == task.campaign_id, CampaignMemberModel.user_id == data.assignee_id).first()

        if not existing_member:
            return "NOT_MEMBER"

    updated_data = data.model_dump(exclude_unset=True)
    
    if current_user.role == "member" and "priority" in updated_data:
        return "CANNOT_UPDATE_PRIORITY"

    for key, value in updated_data.items():
        setattr(task, key, value)

    db.commit()
    db.refresh(task)

    return task
