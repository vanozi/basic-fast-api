from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from sqlalchemy.orm import Session

from app import config
from app.config import get_settings
from app.services.auth import Auth
from app.services.mailer import Mailer
from app.services.user_utils import get_user_response
from app.sql_app import crud
from app.sql_app import schemas
from app.sql_app.database import get_db
from app.sql_app.schemas import Token

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={404: {"description": "Not found"}},
)


@router.post("/token", response_model=Token)
async def login_for_access_token(settings: config.Settings = Depends(get_settings), db: Session = Depends(get_db),
                                 form_data: OAuth2PasswordRequestForm = Depends()):
    user = Auth.authenticate_user(db=db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = Auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires, settings=settings
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/activate_email/{token}", response_model=schemas.User)
async def verify_email(token: str, settings: config.Settings = Depends(get_settings), db: Session = Depends(get_db)):
    invalid_token_error = HTTPException(status_code=400, detail="Invalid token")
    # Check if token expiration date is reached
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=settings.algorithm)
    except jwt.JWTError:
        raise HTTPException(status_code=403, detail="Token has expired")
    # Check if scope of the token is valid
    if payload['scope'] != 'registration':
        raise invalid_token_error
    user = crud.get_user_by_email(db=db, email=payload['sub'])
    # Check if token belongs to user and not already been used
    if not user or user.confirmation is None or user.confirmation.hex != payload['jti']:
        raise invalid_token_error
    # Check if email is already activated
    if user.is_active:
        raise HTTPException(status_code=403, detail="User already activated")
    user.confirmation = None
    user.is_active = True
    db.commit()
    return get_user_response(db=db, user_id=user.id)

@router.post("/forgot_password")
async def forgot_password(user: schemas.UserBase, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db=db, email=user.email)
    if not user:
        raise HTTPException(status_code=400, detail="Email address does not exist")
    reset = Auth.create_password_reset_token(user_email=user.email)
    try:
        Mailer.send_password_reset_message(token=reset["token"], mail_to=user.email)
    except ConnectionRefusedError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Email couldn't be send. Please try again."
        )
    return True

# reset password
@router.post("/reset_password/{token}")
async def reset_password(data:schemas.ResetPassword, token: str, settings: config.Settings = Depends(get_settings), db: Session = Depends(get_db)):
    # decode token and get user
    invalid_token_error = HTTPException(status_code=400, detail="Invalid token")
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=settings.algorithm)
    except jwt.JWTError:
        raise HTTPException(status_code=403, detail="Token has expired")
    if payload['scope'] != 'reset_password':
        raise invalid_token_error
    # Look up user from token
    user = crud.get_user_by_email(db=db, email=payload['sub'])
    if not user:
        raise invalid_token_error
    # hash the new password and save it
    hashed_password = Auth.get_password_hash(password=data.password)
    user.hashed_password = hashed_password
    db.commit()
    return get_user_response(db=db, user_id=user.id)
# https://dev.to/paurakhsharma/flask-rest-api-part-5-password-reset-2f2e

# reset password
