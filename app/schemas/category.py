from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID

# Category Base Schema
class CategoryBase(BaseModel):
    name: str = Field(..., max_length=255)
    slug: str = Field(..., max_length=255)
    parent_id: Optional[UUID] = None

# Category Create Schema
class CategoryCreate(CategoryBase):
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Smartphones",
                "slug": "smartphones",
                "parent_id": None
            }
        }

# Category Update Schema
class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    slug: Optional[str] = Field(None, max_length=255)
    parent_id: Optional[UUID] = None

# Category Response Schema
class CategoryResponse(CategoryBase):
    id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True

# Category with Children Schema
class CategoryWithChildren(CategoryResponse):
    """Category with its subcategories"""
    children: List['CategoryResponse'] = []
    
    class Config:
        from_attributes = True

# Category with Parent Schema
class CategoryWithParent(CategoryResponse):
    """Category with parent category info"""
    parent: Optional[CategoryResponse] = None
    
    class Config:
        from_attributes = True