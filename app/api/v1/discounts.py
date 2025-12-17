from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.database import get_db
from app.models.order import Discount
from app.schemas.order import DiscountCreate, DiscountUpdate, DiscountResponse
from app.dependencies import get_admin_user
from app.models.user import User

router = APIRouter()

# Discount Endpoints
@router.post("/", response_model=DiscountResponse, status_code=status.HTTP_201_CREATED)
def create_discount(
    discount_data: DiscountCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    Create a new discount code (Admin only).
    - `type` can be 'percentage' or 'fixed'.
    - `amount` is the percentage value (e.g., 10 for 10%) or the fixed amount.
    """
    existing_discount = db.query(Discount).filter(Discount.code == discount_data.code).first()
    if existing_discount:
        raise HTTPException(status_code=400, detail="Discount code already exists.")

    new_discount = Discount(**discount_data.model_dump(), id=uuid.uuid4())
    db.add(new_discount)
    db.commit()
    db.refresh(new_discount)
    return new_discount

# Get All Discounts
@router.get("/", response_model=List[DiscountResponse])
def get_all_discounts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    Get a list of all discount codes (Admin only).
    """
    discounts = db.query(Discount).all()
    return discounts

# Get Discount by ID
@router.put("/{discount_id}", response_model=DiscountResponse)
def update_discount(
    discount_id: str,
    discount_data: DiscountUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    Update an existing discount code (Admin only).
    """
    try:
        discount_uuid = uuid.UUID(discount_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid discount ID format")

    discount = db.get(Discount, discount_uuid)
    if not discount:
        raise HTTPException(status_code=404, detail="Discount not found.")

    update_data = discount_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(discount, key, value)

    db.add(discount)
    db.commit()
    db.refresh(discount)
    return discount

@router.delete("/discounts/{discount_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_discount(
    discount_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):  
    """
    Delete a discount code (Admin only).
    """
    try:
        discount_uuid = uuid.UUID(discount_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid discount ID format")

    discount = db.get(Discount, discount_uuid)
    if not discount:
        raise HTTPException(status_code=404, detail="Discount not found.")

    db.delete(discount)
    db.commit()

    return None