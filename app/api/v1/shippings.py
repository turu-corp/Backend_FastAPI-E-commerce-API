from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.database import get_db
from app.models.order import Shipping
from app.schemas.order import ShippingResponse, ShippingCreate, ShippingUpdate
from app.dependencies import get_admin_user
from app.models.user import User

router = APIRouter()

# Shipping Endpoints
# Create Shipping
@router.post("/", response_model=ShippingResponse, status_code=status.HTTP_201_CREATED)
def create_shipping(
    shipping_data: ShippingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    Create a new shipping record (Admin only).
    """
    existing_shipping = db.query(Shipping).filter(Shipping.carrier == shipping_data.carrier).first()
    if existing_shipping:
        raise HTTPException(status_code=400, detail="Shipping carrier already exists.")

    new_shipping = Shipping(**shipping_data.model_dump(), id=uuid.uuid4())
    db.add(new_shipping)
    db.commit()
    db.refresh(new_shipping)
    return new_shipping

# Get All Shippings
@router.get("/", response_model=List[ShippingResponse])
def get_all_shippings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    Get a list of all shipping records (Admin only).
    """
    shippings = db.query(Shipping).all()
    return shippings

# Get Shipping by ID
@router.put("/{shipping_id}", response_model=ShippingResponse)
def update_shipping(
    shipping_id: str,
    shipping_data: ShippingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    Update an existing shipping record (Admin only).
    """
    try:
        shipping_uuid = uuid.UUID(shipping_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid shipping ID format")
                            
    shipping = db.get(Shipping, shipping_uuid)
    if not shipping:
        raise HTTPException(status_code=404, detail="Shipping record not found")

    update_data = shipping_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(shipping, key, value)

    db.add(shipping)
    db.commit()
    db.refresh(shipping)
    return shipping

# Delete Shipping
@router.delete("/shippings/{shipping_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_shipping(
    shipping_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    Delete a shipping record (Admin only).
    """
    try:
        shipping_uuid = uuid.UUID(shipping_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid shipping ID format")

    shipping = db.get(Shipping, shipping_uuid)
    if not shipping:
        raise HTTPException(status_code=404, detail="Shipping record not found")

    db.delete(shipping)
    db.commit()

    return None
