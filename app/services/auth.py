import uuid
from datetime import datetime, timedelta
from typing import Optional, List

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app import config
from app.config import get_settings
from app.sql_app.crud import get_user_by_email
from app.sql_app.database import get_db
from app.sql_app.schemas import TokenData, User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

settings = get_settings()


class Auth:
    password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @classmethod
    def get_password_hash(cls, password: str) -> str:
        return cls.password_context.hash(password)

    @staticmethod
    def verify_password(plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def create_access_token(data: dict, settings: config.Settings,
                            expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        return encoded_jwt

    @staticmethod
    def create_confirmation_token(user_email: str):
        jti = uuid.uuid4()
        claims = {
            "sub": user_email,
            "scope": "registration",
            "jti": jti.hex
        }
        return {
            "jti": jti,
            "token": Auth.create_access_token(
                claims,
                settings,
                timedelta(minutes=settings.registration_token_lifetime)
            )
        }

    # Authenticate and return user
    @staticmethod
    def authenticate_user(email: str, password: str, db: Session):
        user = get_user_by_email(db=db, email=email)
        if not user:
            return False
        if not Auth.verify_password(password, user.hashed_password):
            return False
        return user


# get current user
async def get_current_user(db: Session = Depends(get_db), settings: config.Settings = Depends(get_settings),
                           token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user_by_email(db, email=token_data.username)
    if user is None:
        raise credentials_exception
    return user


# get current active use
async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


class RoleChecker:
    def __init__(self, allowed_roles: List):
        self.allowed_roles = allowed_roles

    def __call__(self, user: User = Depends(get_current_active_user)):
        for role in user.roles:
            if role in self.allowed_roles:
                return True
            else:
                raise HTTPException(status_code=403, detail="Operation not permitted")
