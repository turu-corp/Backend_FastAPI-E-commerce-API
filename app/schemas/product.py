import uuid
from typing import Optional, List
from pydantic import BaseModel

# --- Brand Schemas ---
class BrandBase(BaseModel):
    name: str
    country: str

class BrandCreate(BrandBase):
    pass

class BrandUpdate(BrandBase):
    pass

class BrandResponse(BrandBase):
    id: uuid.UUID
    class Config:
        from_attributes = True

# --- Product Schemas ---
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    slug: str

# Forward declaration for nested schemas
class ProductImageCreate(BaseModel):
    image_url: str
    is_thumbnail: bool = False

class ProductVariantCreate(BaseModel):
    sku: str
    price_adjustment: int = 0
    stock: int = 0

class ProductCreate(ProductBase):
    brand_id: uuid.UUID
    category_id: uuid.UUID
    images: Optional[List[ProductImageCreate]] = None
    variants: Optional[List[ProductVariantCreate]] = None

class ProductUpdate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: uuid.UUID
    brand: BrandResponse
    class Config:
        from_attributes = True

class ProductListResponse(BaseModel):
    products: List[ProductResponse]
    total: int
    page: int
    size: int

# --- Product Image Schemas ---
class ProductImageBase(BaseModel):
    image_url: str
    is_thumbnail: bool = False

class ProductImageResponse(ProductImageBase):
    id: uuid.UUID
    product_id: uuid.UUID
    class Config:
        from_attributes = True

# --- Product Variant Schemas ---
class ProductVariantBase(BaseModel):
    sku: str
    price_adjustment: int = 0
    stock: int = 0

class ProductVariantUpdate(ProductVariantBase):
    pass

class ProductVariantResponse(ProductVariantBase):
    id: uuid.UUID
    product_id: uuid.UUID
    class Config:
        from_attributes = True
