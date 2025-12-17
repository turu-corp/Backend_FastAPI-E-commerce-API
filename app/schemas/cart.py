from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime

# Forward reference for ProductVariantResponse if needed
class ProductVariantResponse(BaseModel):
    id: uuid.UUID
    sku: str
    price_adjustment: int
    stock: int

    class Config:
        from_attributes = True

class CartItemBase(BaseModel):
    variant_id: uuid.UUID
    quantity: int

class CartItemCreate(CartItemBase):
    pass

class CartItemUpdate(BaseModel):
    quantity: Optional[int] = None

class CartItemResponse(CartItemBase):
    id: uuid.UUID
    variant: Optional[ProductVariantResponse] = None

    class Config:
        from_attributes = True

class CartResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime  # <-- Tipe data yang benar
    updated_at: datetime  # <-- Tipe data yang benar
    items: List[CartItemResponse] = []

    class Config:
        from_attributes = True

class AddToCartResponse(BaseModel):
    message: str
    cart_item: CartItemResponse