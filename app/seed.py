from datetime import datetime, timedelta

from db import SessionLocal
from models import (
    UserModel,
    CampaignModel,
    CampaignMemberModel,
    CampaignTaskModel,
)
from core import gen_hashed_password


# =========================================================
# 1. SEED USERS
# =========================================================

def seed_users(db):
    users_data = [
        {
            "email": "admin@gmail.com",
            "password": "Admin@123",
            "full_name": "System Admin",
            "role": "admin",
        },
        {
            "email": "owner@gmail.com",
            "password": "Owner@123",
            "full_name": "Campaign Owner",
            "role": "user",
        },
        {
            "email": "member@gmail.com",
            "password": "Member@123",
            "full_name": "Campaign Member",
            "role": "user",
        },
        {
            "email": "member2@gmail.com",
            "password": "Member@123",
            "full_name": "Campaign Member 2",
            "role": "user",
        },
    ]

    users = {}

    for data in users_data:

        user = (
            db.query(UserModel)
            .filter(UserModel.email == data["email"])
            .first()
        )

        if user is None:
            user = UserModel(
                email=data["email"],
                password_hash=gen_hashed_password(data["password"]),
                full_name=data["full_name"],
                role=data["role"],
                is_active=True,
            )

            db.add(user)
            db.flush()

            print(f"[+] Created user: {data['email']}")

        else:
            print(f"[=] User already exists: {data['email']}")

        users[data["email"]] = user

    return users


# =========================================================
# 2. CREATE CAMPAIGN MEMBER
# =========================================================

def create_membership(
    db,
    campaign_id: int,
    user_id: int,
    role: str,
):
    membership = (
        db.query(CampaignMemberModel)
        .filter(
            CampaignMemberModel.campaign_id == campaign_id,
            CampaignMemberModel.user_id == user_id,
        )
        .first()
    )

    if membership is None:
        membership = CampaignMemberModel(
            campaign_id=campaign_id,
            user_id=user_id,
            role=role,
        )

        db.add(membership)
        db.flush()

        print(
            f"[+] Added member: "
            f"user_id={user_id}, "
            f"campaign_id={campaign_id}, "
            f"role={role}"
        )

    return membership


# =========================================================
# 3. SEED CAMPAIGNS
# =========================================================

def seed_campaigns(db, users):

    owner = users["owner@gmail.com"]
    member = users["member@gmail.com"]
    member2 = users["member2@gmail.com"]

    campaigns_data = [
        {
            "name": "Summer Marketing Campaign",
            "description": "Chiến dịch marketing mùa hè",
            "owner_id": owner.id,
        },
        {
            "name": "Product Launch Campaign",
            "description": "Chiến dịch ra mắt sản phẩm mới",
            "owner_id": owner.id,
        },
    ]

    campaigns = []

    for data in campaigns_data:

        campaign = (
            db.query(CampaignModel)
            .filter(
                CampaignModel.name == data["name"],
                CampaignModel.owner_id == data["owner_id"],
            )
            .first()
        )

        if campaign is None:
            campaign = CampaignModel(
                name=data["name"],
                description=data["description"],
                owner_id=data["owner_id"],
            )

            db.add(campaign)
            db.flush()

            print(
                f"[+] Created campaign: "
                f"{campaign.name} "
                f"(id={campaign.id})"
            )

        else:
            print(
                f"[=] Campaign already exists: "
                f"{campaign.name}"
            )

        campaigns.append(campaign)

    campaign1 = campaigns[0]
    campaign2 = campaigns[1]

    # -----------------------------------------
    # Campaign 1
    # -----------------------------------------

    create_membership(
        db,
        campaign_id=campaign1.id,
        user_id=owner.id,
        role="owner",
    )

    create_membership(
        db,
        campaign_id=campaign1.id,
        user_id=member.id,
        role="member",
    )

    create_membership(
        db,
        campaign_id=campaign1.id,
        user_id=member2.id,
        role="member",
    )

    # -----------------------------------------
    # Campaign 2
    # -----------------------------------------

    create_membership(
        db,
        campaign_id=campaign2.id,
        user_id=owner.id,
        role="owner",
    )

    create_membership(
        db,
        campaign_id=campaign2.id,
        user_id=member2.id,
        role="member",
    )

    return campaigns


# =========================================================
# 4. SEED TASKS
# =========================================================

def seed_tasks(db, campaigns, users):

    owner = users["owner@gmail.com"]
    member = users["member@gmail.com"]
    member2 = users["member2@gmail.com"]

    campaign1 = campaigns[0]
    campaign2 = campaigns[1]

    tasks_data = [
        {
            "campaign_id": campaign1.id,
            "title": "Nghiên cứu thị trường",
            "description": "Phân tích thị trường mục tiêu",
            "assignee_id": member.id,
            "status": "todo",
            "priority": "high",
            "due_date": datetime.now() + timedelta(days=3),
        },
        {
            "campaign_id": campaign1.id,
            "title": "Thiết kế nội dung Facebook",
            "description": "Chuẩn bị nội dung cho Facebook",
            "assignee_id": member2.id,
            "status": "in_progress",
            "priority": "medium",
            "due_date": datetime.now() + timedelta(days=5),
        },
        {
            "campaign_id": campaign1.id,
            "title": "Duyệt kế hoạch marketing",
            "description": "Owner kiểm tra kế hoạch marketing",
            "assignee_id": owner.id,
            "status": "done",
            "priority": "high",
            "due_date": datetime.now() - timedelta(days=1),
        },
        {
            "campaign_id": campaign2.id,
            "title": "Chuẩn bị landing page",
            "description": "Xây dựng landing page cho sản phẩm",
            "assignee_id": member2.id,
            "status": "todo",
            "priority": "high",
            "due_date": datetime.now() + timedelta(days=7),
        },
        {
            "campaign_id": campaign2.id,
            "title": "Viết nội dung quảng cáo",
            "description": "Chuẩn bị nội dung quảng cáo",
            "assignee_id": owner.id,
            "status": "in_progress",
            "priority": "medium",
            "due_date": datetime.now() + timedelta(days=4),
        },
    ]

    for data in tasks_data:

        task = (
            db.query(CampaignTaskModel)
            .filter(
                CampaignTaskModel.campaign_id == data["campaign_id"],
                CampaignTaskModel.title == data["title"],
            )
            .first()
        )

        if task is None:
            task = CampaignTaskModel(**data)

            db.add(task)
            db.flush()

            print(
                f"[+] Created task: "
                f"{data['title']}"
            )

        else:
            print(
                f"[=] Task already exists: "
                f"{data['title']}"
            )


# =========================================================
# 5. MAIN SEED
# =========================================================

def seed():

    db = SessionLocal()

    try:
        print("\n========== START SEED ==========\n")

        # 1. Users
        users = seed_users(db)

        # 2. Campaigns + members
        campaigns = seed_campaigns(
            db,
            users
        )

        # 3. Tasks
        seed_tasks(
            db,
            campaigns,
            users
        )

        db.commit()

        print("\n========== SEED SUCCESS ==========\n")

    except Exception as e:

        db.rollback()

        print("\n========== SEED FAILED ==========")
        print(f"Error: {e}")

        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed()
