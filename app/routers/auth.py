from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.sql_app.database import get_db
from app.sql_app.schemas import Token
from app.utils.security import authenticate_user, create_access_token
from sqlalchemy.orm import Session

from app import config
from app.config import get_settings

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={404: {"description": "Not found"}},
)

@router.post("/token", response_model=Token)
async def login_for_access_token(settings: config.Settings = Depends(get_settings), db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(db=db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires, settings=settings
    )
    return {"access_token": access_token, "token_type": "bearer"}

# forgot password
# https://dev.to/paurakhsharma/flask-rest-api-part-5-password-reset-2f2e

# reset password