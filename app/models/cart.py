import uuid
from typing import List
from sqlmodel import Field, Relationship
from .base import TimeStampedModel
from .product import ProductVariant
from app.models.user import User

# Cart and CartItem Models
class Cart(TimeStampedModel, table=True):
    __tablename__ = "carts"
    user_id: uuid.UUID = Field(foreign_key="users.id")

    user: "User" = Relationship(back_populates="cart")
    items: List["CartItem"] = Relationship(back_populates="cart")

# CartItem Model
class CartItem(TimeStampedModel, table=True):
    __tablename__ = "cart_items"
    cart_id: uuid.UUID = Field(foreign_key="carts.id")
    variant_id: uuid.UUID = Field(foreign_key="product_variants.id")
    quantity: int = Field(default=1)

    cart: Cart = Relationship(back_populates="items")
    variant: ProductVariant = Relationship()
