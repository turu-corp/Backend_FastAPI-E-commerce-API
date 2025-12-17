from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from app.database import get_db
from app.models.product import Category
from app.schemas.category import (
    CategoryCreate, CategoryUpdate, CategoryResponse,
    CategoryWithChildren, CategoryWithParent
)
from app.dependencies import get_current_user, get_admin_user
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=List[CategoryResponse])
def get_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    parent_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get all categories with optional parent filter
    
    - **parent_id**: Filter by parent category (use 'null' for root categories)
    """
    query = db.query(Category)
    
    # Filter by parent_id
    if parent_id:
        if parent_id.lower() == 'null':
            query = query.filter(Category.parent_id.is_(None))
        else:
            try:
                query = query.filter(Category.parent_id == uuid.UUID(parent_id))
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid parent_id format")
    
    categories = query.offset(skip).limit(limit).all()
    return categories


@router.get("/tree", response_model=List[CategoryWithChildren])
def get_category_tree(db: Session = Depends(get_db)):
    """
    Get category tree structure (root categories with their children)
    """
    root_categories = db.query(Category).filter(Category.parent_id.is_(None)).all()
    return root_categories


@router.get("/{category_id}", response_model=CategoryWithParent)
def get_category(category_id: str, db: Session = Depends(get_db)):
    """Get a specific category by ID with parent info"""
    try:
        category_uuid = uuid.UUID(category_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid category ID format")
    
    category = db.query(Category).filter(Category.id == category_uuid).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return category


@router.get("/slug/{slug}", response_model=CategoryWithChildren)
def get_category_by_slug(slug: str, db: Session = Depends(get_db)):
    """Get a category by its slug with subcategories"""
    category = db.query(Category).filter(Category.slug == slug).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return category


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    category_data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """(Admin Only) Create a new category (requires authentication)"""
    
    # Check if slug already exists
    existing = db.query(Category).filter(Category.slug == category_data.slug).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category slug already exists")
    
    # Validate parent_id if provided
    if category_data.parent_id:
        parent = db.query(Category).filter(Category.id == category_data.parent_id).first()
        if not parent:
            raise HTTPException(status_code=404, detail="Parent category not found")
    
    new_category = Category(
        id=uuid.uuid4(),
        name=category_data.name,
        slug=category_data.slug,
        parent_id=category_data.parent_id
    )
    
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    
    return new_category


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: str,
    category_data: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """(Admin Only) Update a category (requires authentication)"""
    try:
        category_uuid = uuid.UUID(category_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid category ID format")
    
    category = db.query(Category).filter(Category.id == category_uuid).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    update_data = category_data.model_dump(exclude_unset=True)
    
    # Check slug uniqueness if updating
    if "slug" in update_data and update_data["slug"] != category.slug:
        existing = db.query(Category).filter(Category.slug == update_data["slug"]).first()
        if existing:
            raise HTTPException(status_code=400, detail="Category slug already exists")
    
    # Validate parent_id if updating
    if "parent_id" in update_data and update_data["parent_id"]:
        # Prevent circular reference
        if update_data["parent_id"] == category.id:
            raise HTTPException(status_code=400, detail="Category cannot be its own parent")
        
        parent = db.query(Category).filter(Category.id == update_data["parent_id"]).first()
        if not parent:
            raise HTTPException(status_code=404, detail="Parent category not found")
    
    for field, value in update_data.items():
        setattr(category, field, value)
    
    db.commit()
    db.refresh(category)
    
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    (Admin Only)

    Delete a category (requires authentication)
    
    Note: This will also affect subcategories and products
    """
    try:
        category_uuid = uuid.UUID(category_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid category ID format")
    
    category = db.query(Category).filter(Category.id == category_uuid).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    db.delete(category)
    db.commit()
    
    return None