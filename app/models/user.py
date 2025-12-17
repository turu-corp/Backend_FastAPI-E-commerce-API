import uuid
from typing import List, Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship, SQLModel
from .base import TimeStampedModel, BaseUUIDModel
from datetime import datetime
from sqlalchemy import String

if TYPE_CHECKING:
    from .order import Order
    from .cart import Cart
    from .product import Review

# User Address and Role Models
class Role(TimeStampedModel, table=True):
    __tablename__ = "roles"
    name: str = Field(max_length=255, unique=True, nullable=False)
    users: List["User"] = Relationship(back_populates="role")

class User(TimeStampedModel, table=True):
    __tablename__ = "users"
    role_id: uuid.UUID = Field(foreign_key="roles.id")
    name: str = Field(max_length=255)
    email: str = Field(max_length=255, unique=True, index=True, nullable=False)
    email_verified_at: Optional[str] = Field(default=None)
    hashed_password: str = Field(nullable=False)
    remember_token: Optional[str] = Field(max_length=100, default=None)

    role: Role = Relationship(back_populates="users")
    profile: Optional["UserProfile"] = Relationship(back_populates="user", sa_relationship_kwargs={'uselist': False})
    addresses: List["Address"] = Relationship(back_populates="user")
    reviews: List["Review"] = Relationship(back_populates="user")
    orders: List["Order"] = Relationship(back_populates="user")
    cart: Optional["Cart"] = Relationship(back_populates="user", sa_relationship_kwargs={'uselist': False})

class UserProfile(TimeStampedModel, table=True):
    __tablename__ = "user_profiles"
    user_id: uuid.UUID = Field(foreign_key="users.id", unique=True)
    phone: Optional[str] = Field(max_length=255, default=None)
    gender: Optional[str] = Field(max_length=255, default=None)
    birth_date: Optional[str] = Field(default=None)

    user: User = Relationship(back_populates="profile")

class Address(TimeStampedModel, table=True):
    __tablename__ = "addresses"

    user_id: uuid.UUID = Field(foreign_key="users.id")
    label: str = Field(max_length=100)
    recipient_name: str = Field(max_length=255)
    phone_number: str = Field(max_length=20)
    address_line: str = Field(max_length=255)
    city: str = Field(max_length=100)
    province: str = Field(max_length=100)
    postal_code: str = Field(max_length=10)
    is_primary: bool = Field(default=False)

    user: "User" = Relationship(back_populates="addresses")
    orders: List["Order"] = Relationship(back_populates="address")
