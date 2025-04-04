# Pydantic models for the request and response bodies of the API

from pydantic import BaseModel, EmailStr, constr
from datetime import datetime, date
from typing import Optional, Literal, List


class UserCreate(BaseModel):
    email: EmailStr
    password: constr(min_length=4)

class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True # to convert to a pydantic model since this class is used as a response

# use Outh2PasswordRequestForm instead
# class UserLogin(BaseModel):
#     email: EmailStr
#     password: constr(min_length=4)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[int] = None


class TextInput(BaseModel):
    text: str
    language: Literal["en", "hi", "ml"]

class Filter(BaseModel):
    languages: Optional[List[str]]
    category: Optional[str]