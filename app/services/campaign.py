from sqlalchemy.orm import Session

from schemas import CampaignCreateSchema, CampaignMemberCreateSchema
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

    if current_user.role != "admin":
        query = query.join(
            CampaignMemberModel, CampaignMemberModel.campaign_id == CampaignModel.id
        ).filter(
            CampaignMemberModel.user_id == current_user.id,
            CampaignMemberModel.role.in_(["owner", "member"]),
        )

        if keyword:
            query = query.filter(CampaignModel.name.ilike(f"%{keyword}%"))

    lst = query.all()

    return lst


def get_campaign_detail(campaign_id: int, current_user: UserModel, db: Session):
    query = (
        db.query(CampaignModel)
        .join(CampaignMemberModel, CampaignMemberModel.campaign_id == CampaignModel.id)
        .filter(
            CampaignMemberModel.user_id == current_user.id,
            CampaignModel.id == campaign_id,
            CampaignMemberModel.role.in_(["owner", "member"]),
        )
    )

    if current_user.role == "admin":
        query = db.query(CampaignModel).filter(CampaignModel.id == campaign_id)

    return query.first()


def add_member(
    campaign_id: int,
    current_user: UserModel,
    campaign_member: CampaignMemberCreateSchema,
    db: Session,
):
    campaign = get_campaign_detail(campaign_id, current_user, db)

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

    return new_member, None
