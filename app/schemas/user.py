from pydantic import BaseModel, EmailStr, UUID4, field_validator
from typing import Optional, List
from datetime import datetime


# --- User Schemas ---
class UserBase(BaseModel):
    email: EmailStr
    name: str

    @field_validator("email")
    @classmethod
    def email_to_lower(cls, v: str) -> str:
        return v.lower()


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: UUID4
    role_id: UUID4
    created_at: datetime

    # Add addresses to the user response model
    addresses: List['AddressResponse'] = []

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class RoleBase(BaseModel):
    name: str

class RoleCreate(RoleBase):
    pass

class RoleRead(RoleBase):
    id: UUID4

    class Config:
        from_attributes = True

class UserProfileBase(BaseModel):
    phone_number: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None

class UserProfileCreate(UserProfileBase):
    pass

class UserProfileRead(UserProfileBase):
    id: UUID4
    user_id: UUID4

    class Config:
        from_attributes = True

class UserProfileUpdate(UserProfileBase):
    pass


# --- Address Schemas ---
class AddressBase(BaseModel):
    label: str
    recipient_name: str
    phone_number: str
    address_line: str
    city: str
    province: str
    postal_code: str

class AddressCreate(AddressBase):
    pass

class AddressResponse(AddressBase):
    id: UUID4

    class Config:
        from_attributes = True

class AddressUpdate(BaseModel):
    label: Optional[str] = None
    recipient_name: Optional[str] = None
    phone_number: Optional[str] = None
    address_line: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    postal_code: Optional[str] = None