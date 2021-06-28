from typing import Optional, List

from pydantic import BaseModel, EmailStr, UUID4


# Role schema
class Role(BaseModel):
    role: str

    class Config:
        orm_mode = True


class RoleCreate(BaseModel):
    owner_id: int
    role: str


# User Schema

class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr]


class User(UserBase):
    id: int
    is_active: bool
    confirmation: Optional[UUID4]
    roles: List[str]

    class Config:
        orm_mode = True


# Token Schema
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None

# reset password Schema
class ResetPassword(BaseModel):
    password:str