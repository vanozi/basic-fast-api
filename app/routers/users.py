from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.sql_app.models import User
from app.utils.security import get_password_hash, get_current_user

from app.utils.dependencies import RoleChecker

from app.sql_app import crud, schemas
from app.sql_app.database import get_db
from app.utils.user_utils import get_user_response, get_all_users_response

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user, hashed_password=get_password_hash(user.password))


@router.get("/", response_model=List[schemas.User], dependencies=[Depends(RoleChecker(['admin']))])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = get_all_users_response(db, skip=skip, limit=limit)
    return users


@router.get("/me", response_model=schemas.User)
def read_user(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return get_user_response(db, user_id=current_user.id)


@router.get("/{user_id}", response_model=schemas.User, dependencies=[Depends(RoleChecker(['admin']))])
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user = get_user_response(db, user_id=user_id)
    return user
