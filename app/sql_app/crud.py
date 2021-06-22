from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from . import models, schemas


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate, hashed_password: str, confirmation: str):
    db_user = models.User(email=user.email, hashed_password=hashed_password)

    db_user.confirmation = confirmation
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, updated_user=schemas.User):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    update_user_encoded = jsonable_encoder(updated_user)
    db_user.update(**update_user_encoded)
    db.commit()
    return db_user


# Roles
def create_user_role(db: Session, role: schemas.RoleCreate):
    db_role = models.Role(**role.dict())
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role


def get_user_roles(db: Session, user_id: int):
    return db.query(models.Role).filter(models.Role.owner_id == user_id).all()
