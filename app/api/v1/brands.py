from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.database import get_db
from app.models.product import Brand
from app.schemas.product import BrandCreate, BrandUpdate, BrandResponse
from app.dependencies import get_current_user, get_admin_user
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=List[BrandResponse])
def get_brands(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get all brands with pagination"""
    brands = db.query(Brand).offset(skip).limit(limit).all()
    return brands


@router.get("/{brand_id}", response_model=BrandResponse)
def get_brand(brand_id: str, db: Session = Depends(get_db)):
    """Get a specific brand by ID"""
    try:
        brand_uuid = uuid.UUID(brand_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid brand ID format")
    
    brand = db.query(Brand).filter(Brand.id == brand_uuid).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    
    return brand


@router.post("/", response_model=BrandResponse, status_code=status.HTTP_201_CREATED)
def create_brand(
    brand_data: BrandCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """(Admin Only) Create a new brand (requires authentication)"""
    new_brand = Brand(
        id=uuid.uuid4(),
        name=brand_data.name,
        country=brand_data.country
    )
    
    db.add(new_brand)
    db.commit()
    db.refresh(new_brand)
    
    return new_brand


@router.put("/{brand_id}", response_model=BrandResponse)
def update_brand(
    brand_id: str,
    brand_data: BrandUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """(Admin Only) Update a brand (requires authentication)"""
    try:
        brand_uuid = uuid.UUID(brand_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid brand ID format")
    
    brand = db.query(Brand).filter(Brand.id == brand_uuid).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    
    update_data = brand_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(brand, field, value)
    
    db.commit()
    db.refresh(brand)
    
    return brand


@router.delete("/{brand_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_brand(
    brand_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Delete a brand (requires authentication)"""
    try:
        brand_uuid = uuid.UUID(brand_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid brand ID format")
    
    brand = db.query(Brand).filter(Brand.id == brand_uuid).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    
    db.delete(brand)
    db.commit()
    
    return None