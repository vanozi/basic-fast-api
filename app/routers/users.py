from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from app.services.auth import Auth, get_current_user
from app.services.auth import RoleChecker
from app.services.mailer import Mailer
from app.services.user_utils import get_user_response, get_all_users_response
from app.sql_app import crud, schemas
from app.sql_app.database import get_db
from app.sql_app.models import User

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    confirmation = Auth.create_confirmation_token(user.email)
    try:
        Mailer.send_confirmation_message(confirmation["token"], user.email)
    except ConnectionRefusedError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Email couldn't be send. Please try again."
        )
    user = crud.create_user(db=db, user=user, hashed_password=Auth.get_password_hash(user.password),
                            confirmation=confirmation["jti"])
    role = schemas.RoleCreate(owner_id=user.id, role="user")
    crud.create_user_role(db=db, role=role)
    print(confirmation['token'])
    return get_user_response(db=db, user_id=user.id)


@router.get("/", response_model=List[schemas.User], dependencies=[Depends(RoleChecker(['admin']))])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = get_all_users_response(db, skip=skip, limit=limit)
    return users


@router.get("/me", response_model=schemas.User)
def read_user(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return get_user_response(db, user_id=current_user.id)


@router.put("/me", response_model=schemas.User)
def update_me(user: schemas.UserUpdate, current_user: User = Depends(get_current_user),
              db: Session = Depends(get_db)):
    updated_user = crud.update_user(db=db, user_id=current_user.id, updated_user=user)
    return get_user_response(db=db, user_id=updated_user.id)


@router.get("/{user_id}", response_model=schemas.User, dependencies=[Depends(RoleChecker(['admin']))])
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user = get_user_response(db, user_id=user_id)
    return user
