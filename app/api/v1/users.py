from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.database import get_db
from app.models.user import User, Address
from app.schemas.user import UserRead, AddressCreate, AddressResponse
from app.dependencies import get_current_active_user

router = APIRouter()

# User Endpoints
# Get Current User Profile
@router.get("/me", response_model=UserRead)
def read_users_me(current_user: User = Depends(get_current_active_user)):
    """
    Get current user's profile.
    """
    return current_user

# Add Address for Current User
@router.post("/me/addresses", response_model=AddressResponse, status_code=status.HTTP_201_CREATED)
def add_address(
    address_data: AddressCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Add a new address for the current user.
    """
    new_address = Address(
        **address_data.model_dump(),
        id=uuid.uuid4(),
        user_id=current_user.id
    )
    db.add(new_address)
    db.commit()
    db.refresh(new_address)
    return new_address

# Get All Addresses for Current User
@router.get("/me/addresses", response_model=List[AddressResponse])
def get_my_addresses(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all addresses for the current user.
    """
    return db.query(Address).filter(Address.user_id == current_user.id).all()

# Delete Address for Current User
@router.delete("/me/addresses/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_address(
    address_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete an address for the current user.
    """
    try:
        address_uuid = uuid.UUID(address_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid address ID format")

    address = db.query(Address).filter(
        Address.id == address_uuid,
        Address.user_id == current_user.id
    ).first()

    if not address:
        raise HTTPException(status_code=404, detail="Address not found")

    db.delete(address)
    db.commit()
    return None