from typing import Optional, List

from pydantic import BaseModel, EmailStr


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


class User(UserBase):
    id: int
    is_active: bool
    roles : List[str]

    class Config:
        orm_mode = True


# Token Schema
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None

