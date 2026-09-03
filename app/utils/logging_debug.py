from sqlalchemy.orm import Session

from models import LogModel

def add_log(
    user_id: int,
    action: str,
    message: str,
    db: Session,
):
    log = LogModel(
        user_id=user_id,
        action=action,
        message=message,
    )

    db.add(log)
    db.commit()
    
    return log


    