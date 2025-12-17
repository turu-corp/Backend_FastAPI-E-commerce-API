from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from app.database import get_db
from app.models.product import Product, ProductImage, ProductVariant, Brand, Category
from app.schemas.product import (
    ProductCreate, ProductUpdate, ProductResponse, 
    ProductListResponse
)
from app.dependencies import get_current_user, get_admin_user
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=List[ProductListResponse])
def get_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    category_id: Optional[str] = None,
    brand_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get list of products with pagination and filters
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    - **search**: Search by product name
    - **category_id**: Filter by category UUID
    - **brand_id**: Filter by brand UUID
    """
    query = db.query(Product)
    
    # Apply filters
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))
    
    if category_id:
        try:
            query = query.filter(Product.category_id == uuid.UUID(category_id))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid category_id format")
    
    if brand_id:
        try:
            query = query.filter(Product.brand_id == uuid.UUID(brand_id))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid brand_id format")
    
    products = query.offset(skip).limit(limit).all()
    return products


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: str, db: Session = Depends(get_db)):
    """
    Get a specific product by ID with all details (images, variants)
    """
    try:
        product_uuid = uuid.UUID(product_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid product ID format")
    
    product = db.query(Product).filter(Product.id == product_uuid).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return product


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    (Admin Only)

    Create a new product (requires authentication)
    
    Can include images and variants in the same request
    """
    # Check if slug already exists
    existing = db.query(Product).filter(Product.slug == product_data.slug).first()
    if existing:
        raise HTTPException(status_code=400, detail="Product slug already exists")
    
    # Validate foreign keys before creating
    brand = db.get(Brand, product_data.brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail=f"Brand with id {product_data.brand_id} not found")

    category = db.get(Category, product_data.category_id)
    if not category:
        raise HTTPException(status_code=404, detail=f"Category with id {product_data.category_id} not found")


    # Create product
    new_product = Product(
        id=uuid.uuid4(),
        name=product_data.name,
        slug=product_data.slug,
        description=product_data.description,
        brand_id=product_data.brand_id,
        category_id=product_data.category_id
    )
    
    db.add(new_product)
    db.flush()  # Get the product ID
    
    # Add images
    if product_data.images is not None:
        for img_data in product_data.images:
            image = ProductImage(
                id=uuid.uuid4(),
                product_id=new_product.id,
                image_url=img_data.image_url,
                is_thumbnail=img_data.is_thumbnail
            )
            db.add(image)

    # Add variants
    if product_data.variants is not None:
        for var_data in product_data.variants:
            variant = ProductVariant(
                id=uuid.uuid4(),
                product_id=new_product.id,
                sku=var_data.sku,
                price_adjustment=var_data.price_adjustment,
                stock=var_data.stock
            )
            db.add(variant)
    
    db.commit()
    db.refresh(new_product)
    
    return new_product


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: str,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    (Admin Only) Update a product (requires authentication)
    """
    try:
        product_uuid = uuid.UUID(product_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid product ID format")
    
    product = db.query(Product).filter(Product.id == product_uuid).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Update only provided fields
    update_data = product_data.model_dump(exclude_unset=True)
    
    # Check slug uniqueness if updating
    if "slug" in update_data and update_data["slug"] != product.slug:
        existing = db.query(Product).filter(Product.slug == update_data["slug"]).first()
        if existing:
            raise HTTPException(status_code=400, detail="Product slug already exists")
    
    for field, value in update_data.items():
        setattr(product, field, value)
    
    db.commit()
    db.refresh(product)
    
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    (Admin Only)

    Delete a product (requires authentication)
    
    This will cascade delete all related images and variants
    """
    try:
        product_uuid = uuid.UUID(product_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid product ID format")
    
    product = db.query(Product).filter(Product.id == product_uuid).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db.delete(product)
    db.commit()
    
    return None


@router.get("/slug/{slug}", response_model=ProductResponse)
def get_product_by_slug(slug: str, db: Session = Depends(get_db)):
    """
    Get a product by its slug (SEO-friendly)
    """
    product = db.query(Product).filter(Product.slug == slug).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return product