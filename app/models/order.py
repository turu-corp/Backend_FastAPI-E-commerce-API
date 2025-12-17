import uuid
from typing import List, Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship, SQLModel
from .base import TimeStampedModel
from .product import ProductVariant
from datetime import datetime   

if TYPE_CHECKING:
    from .user import User, Address


class Order(TimeStampedModel, table=True):
    __tablename__ = "orders"
    user_id: uuid.UUID = Field(foreign_key="users.id")
    address_id: uuid.UUID = Field(foreign_key="addresses.id")
    shipping_id: uuid.UUID = Field(foreign_key="shippings.id")
    discount_id: Optional[uuid.UUID] = Field(
        default=None,
        foreign_key="discounts.id"
    )
    total_price: int
    status: str = Field(max_length=255, default="pending")

    user: "User" = Relationship(back_populates="orders")
    address: "Address" = Relationship(back_populates="orders")
    shipping: "Shipping" = Relationship(back_populates="orders")
    discount: Optional["Discount"] = Relationship(back_populates="orders")
    items: List["OrderItem"] = Relationship(back_populates="order")
    payment: Optional["Payment"] = Relationship(back_populates="order", sa_relationship_kwargs={'uselist': False})
    

class OrderItem(TimeStampedModel, table=True):
    __tablename__ = "order_items"
    order_id: uuid.UUID = Field(foreign_key="orders.id")
    variant_id: uuid.UUID = Field(foreign_key="product_variants.id")
    quantity: int
    price_per_unit: int
    subtotal: int

    order: Order = Relationship(back_populates="items")
    variant: ProductVariant = Relationship()

class Payment(TimeStampedModel, table=True):
    __tablename__ = "payments"
    order_id: uuid.UUID = Field(foreign_key="orders.id", unique=True)
    method: str = Field(max_length=255)
    status: str = Field(max_length=255)
    transaction_time: Optional[datetime] = Field(default=None) # Menggunakan datetime

    order: Order = Relationship(back_populates="payment")

class Shipping(TimeStampedModel, table=True):
    __tablename__ = "shippings"
    # This model represents available shipping options, not a specific order's shipping details.
    # A specific order will have its own shipping details, possibly linking here.
    carrier: str = Field(max_length=100, nullable=False) # e.g., "JNE REG"
    description: str = Field(max_length=255) # e.g., "Regular Service (2-3 days)"
    cost: int # Biaya pengiriman
    is_active: bool = Field(default=True)
    taxpayer_identification_number: Optional[str] = Field(max_length=12, default=None)
    orders: List["Order"] = Relationship(back_populates="shipping")

class Discount(TimeStampedModel, table=True):
    __tablename__ = "discounts"
    code: str = Field(max_length=255, unique=True, nullable=False)
    description: Optional[str] = Field(max_length=255, default=None)
    percentage: Optional[int] = Field(default=None)
    fixed_amount: Optional[int] = Field(default=None)
    min_purchase: int = Field(default=0)
    valid_from: datetime
    valid_until: Optional[datetime] = None
    is_active: bool = Field(default=True)

    orders: List["Order"] = Relationship(back_populates="discount")
