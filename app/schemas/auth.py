from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional

# User Authentication Schemas
class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str

    @field_validator("email")
    @classmethod
    def email_to_lower(cls, v: str) -> str:
        return v.lower()

# User Login Schema
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Token Schema
class Token(BaseModel):
    access_token: str
    token_type: str

# Token Data Schema
class TokenData(BaseModel):
    email: Optional[str] = None

# User Response Schema
class UserResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
