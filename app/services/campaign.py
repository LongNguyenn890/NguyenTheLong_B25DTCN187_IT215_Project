from sqlalchemy.orm import Session

from schemas import (
    CampaignCreateSchema,
    CampaignMemberCreateSchema,
    CampaignUpdateSchema,
)
from models import CampaignModel, CampaignMemberModel, UserModel


def create_new_campaign(
    campaign: CampaignCreateSchema, current_user: UserModel, db: Session
):
    new_campaign = CampaignModel(
        name=campaign.name, description=campaign.description, owner_id=current_user.id
    )

    db.add(new_campaign)
    db.flush()

    new_campaign_member = CampaignMemberModel(
        campaign_id=new_campaign.id, user_id=new_campaign.owner_id, role="owner"
    )

    db.add(new_campaign_member)

    db.commit()

    db.refresh(new_campaign)

    return new_campaign


def get_campaign_list(keyword: str, current_user: UserModel, db: Session):

    query = db.query(CampaignModel)

    query = query.filter(CampaignModel.is_deleted == False)

    if current_user.role != "admin":
        query = (
            query.join(
                CampaignMemberModel, CampaignMemberModel.campaign_id == CampaignModel.id
            )
            .filter(
                CampaignMemberModel.user_id == current_user.id,
                CampaignMemberModel.role.in_(["owner", "member"]),
            )
        )

    if keyword:
        query = query.filter(CampaignModel.name.ilike(f"%{keyword}%"))

    lst = query.all()

    return lst


def get_campaign_detail(campaign_id: int, db: Session):
    query = db.query(CampaignModel).filter(
        CampaignModel.id == campaign_id, CampaignModel.is_deleted == False
    )

    return query.first()


def add_member(
    campaign_id: int,
    campaign_member: CampaignMemberCreateSchema,
    db: Session,
):
    campaign = get_campaign_detail(campaign_id, db)

    if campaign is None:
        return None, "CAMPAIGN_NOT_FOUND"

    user_db = (
        db.query(UserModel).filter(UserModel.id == campaign_member.user_id).first()
    )

    if user_db is None:
        return None, "NOT_EXISTED_USER"

    user_member = (
        db.query(CampaignMemberModel)
        .filter(
            CampaignMemberModel.user_id == campaign_member.user_id,
            CampaignMemberModel.campaign_id == campaign.id,
        )
        .first()
    )

    if user_member:
        return None, "EXISTED_MEMBER"

    new_member = CampaignMemberModel(
        campaign_id=campaign.id, user_id=campaign_member.user_id, role="member"
    )

    db.add(new_member)
    db.commit()
    db.refresh(new_member)

    return {
        "id": user_db.id,
        "full_name": user_db.full_name,
        "email": user_db.email,
        "role": new_member.role.value,
    }, None


def delete_campaign(campaign_id: int, db: Session):

    campaign = db.query(CampaignModel).filter(
        CampaignModel.id == campaign_id,
        CampaignModel.is_deleted == False,
    ).first()

    if campaign is None:
        return None

    campaign.is_deleted = True
    db.commit()
    db.refresh(campaign)

    return campaign


def update_campaign(campaign_id: int, data: CampaignUpdateSchema, db: Session):

    campaign = db.query(CampaignModel).filter(
        CampaignModel.id == campaign_id,
        CampaignModel.is_deleted == False,
    ).first()

    if campaign is None:
        return None

    updated_data = data.model_dump(exclude_unset=True)

    for key, value in updated_data.items():
        setattr(campaign, key, value)

    db.commit()
    db.refresh(campaign)

    return campaign


def get_all_members(campaign_id: int, db: Session):
    if get_campaign_detail(campaign_id, db) is None:
        return "CAMPAIGN_NOT_FOUND"

    members = (
        db.query(UserModel, CampaignMemberModel.role)
        .join(CampaignMemberModel, CampaignMemberModel.user_id == UserModel.id)
        .filter(CampaignMemberModel.campaign_id == campaign_id)
        .all()
    )

    return [
        {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "role": role.value,
        }
        for user, role in members
    ]


def delete_member(campaign_id: int, user_id: int, db: Session):
    if get_campaign_detail(campaign_id, db) is None:
        return "CAMPAIGN_NOT_FOUND"

    member = (
        db.query(CampaignMemberModel)
        .filter(
            CampaignMemberModel.campaign_id == campaign_id,
            CampaignMemberModel.user_id == user_id,
        )
        .first()
    )

    if member is None:
        return "MEMBER_NOT_EXIST"

    if member.role == "owner":
        return "CANNOT_DELETE_OWNER"

    db.delete(member)
    db.commit()
