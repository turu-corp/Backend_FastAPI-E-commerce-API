import uuid
from typing import Optional, List, Literal
from pydantic import BaseModel
from enum import Enum
from datetime import datetime
from sqlmodel import Field, Relationship, SQLModel
from app.models.order import Order


class BaseSchema(BaseModel):
    """A base schema for other schemas to inherit from."""
    class Config:
        from_attributes = True
        json_encoders = {
            # Custom JSON encoder for datetime objects
            datetime: lambda v: v.isoformat() if v else None
        }

# --- Enums ---
class OrderStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class PaymentMethod(str, Enum):
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    BANK_TRANSFER = "bank_transfer"
    E_WALLET = "e_wallet"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

# --- Order Schemas ---
class OrderBase(BaseSchema):
    address_id: uuid.UUID
    total_price: int
    status: OrderStatus = OrderStatus.PENDING

class OrderCreate(BaseModel):
    address_id: uuid.UUID
    shipping_name: str # User will send the name of the shipping method
    discount_code: Optional[str] = None

class OrderItemResponse(BaseModel):
    id: uuid.UUID
    quantity: int
    price_per_unit: int
    subtotal: int
    variant_id: uuid.UUID
    # Anda bisa menambahkan detail variant jika perlu
    
    class Config:
        orm_mode = True

class OrderPreviewRequest(BaseModel):
    """Schema for requesting an order preview. Does not need base config."""
    address_id: uuid.UUID
    discount_code: Optional[str] = None

class OrderPreviewItem(BaseModel):
    """Schema for a single item in the order preview. Does not need base config."""
    variant_id: uuid.UUID
    product_name: str
    sku: str
    quantity: int
    price_per_unit: int
    subtotal: int

class OrderPreviewResponse(BaseModel):
    """Schema for the complete order preview response. Does not need base config."""
    subtotal: int
    shipping_cost: int
    discount_amount: int
    grand_total: int
    items: List[OrderPreviewItem]
    is_stock_sufficient: bool

class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None

class OrderUpdateStatusByAdmin(BaseModel):
    """Schema for admin to update order status. Only 'shipped' is allowed."""
    status: Literal[OrderStatus.SHIPPED]

class OrderUpdateStatusByCustomer(BaseModel):
    """Schema for customer to update order status. Only 'delivered' is allowed."""
    status: Literal[OrderStatus.DELIVERED]

class OrderResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    total_price: int
    status: str
    created_at: datetime
    items: List[OrderItemResponse] # Include order items

    class Config:   
        orm_mode = True

class OrderListResponse(BaseSchema):
    id: uuid.UUID
    total_price: int
    status: OrderStatus
    created_at: datetime
    items_count: int

    @classmethod
    def from_orm_with_items_count(cls, order: 'Order', items_count: int):
        return cls(id=order.id, total_price=order.total_price, status=order.status, created_at=order.created_at, items_count=items_count)
    
    class Config(BaseSchema.Config):
        pass

class OrderSummary(BaseModel):
    """Does not need base config."""
    id: uuid.UUID   
    total_price: int
    status: OrderStatus
    created_at: datetime

# --- Payment Schemas ---
class PaymentBase(BaseSchema):
    # Hanya field yang relevan untuk request dan response
    method: PaymentMethod

class PaymentCreate(PaymentBase):
    # Schema ini hanya mewarisi 'method' dari PaymentBase
    pass

class PaymentResponse(PaymentBase):
    id: uuid.UUID
    order_id: uuid.UUID
    status: PaymentStatus # Status ditambahkan di sini, untuk response
    transaction_time: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config(BaseSchema.Config):
        pass

# --- Webhook Schemas ---
class WebhookPayload(BaseModel):
    """
    Schema for incoming payment gateway webhook payload.
    This provides validation for the data sent by the payment gateway.
    """
    order_id: uuid.UUID
    payment_status: PaymentStatus

# --- Shipping Schemas ---
class ShippingBase(BaseSchema):
    carrier: str #JNE, TIKI, etc.
    taxpayer_identification_number: Optional[str] = None
    description: Optional[str] = None
    cost: int
    is_active: bool = True


class ShippingCreate(ShippingBase): # Schema for admin to create/update shipping
    pass

class ShippingUpdate(BaseModel): # Does not need base config
    carrier: Optional[str] = None
    taxpayer_identification_number: Optional[str] = None
    description: Optional[str] = None
    cost: Optional[int] = None
    is_active: Optional[bool] = None


class ShippingResponse(BaseModel):
    id: uuid.UUID
    carrier: str #JNE, TIKI, etc.
    taxpayer_identification_number: Optional[str] = None
    description: Optional[str] = None
    cost: int
    is_active: bool = True

# --- Discount Schemas ---

class DiscountBase(BaseSchema):
    code: str
    description: Optional[str] = None
    percentage: Optional[int] = None
    fixed_amount: Optional[int] = None
    min_purchase: int = 0
    valid_from: datetime
    valid_until: Optional[datetime] = None
    is_active: bool = True

class DiscountCreate(DiscountBase):
    pass

class DiscountUpdate(BaseModel): # Does not need base config
    code: Optional[str] = None
    description: Optional[str] = None
    percentage: Optional[int] = None
    fixed_amount: Optional[int] = None
    min_purchase: Optional[int] = None
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    is_active: Optional[bool] = None

class DiscountResponse(BaseSchema):
    id: uuid.UUID
    code: str
    description: Optional[str] = None
    percentage: Optional[int] = None
    fixed_amount: Optional[int] = None
    min_purchase: int
    valid_from: datetime
    valid_until: Optional[datetime] = None
    is_active: bool
    
    class Config(BaseSchema.Config):
        pass
