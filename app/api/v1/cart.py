from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.database import get_db
from app.models.cart import Cart, CartItem
from app.models.product import ProductVariant
from app.schemas.cart import (
    CartItemCreate, CartItemUpdate, CartItemResponse,
    CartResponse, AddToCartResponse
)
from app.dependencies import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=CartResponse)
def get_cart(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Get the current user's cart with all items
    """
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()

    if not cart:
        # Create empty cart if none exists
        cart = Cart(id=uuid.uuid4(), user_id=current_user.id)
        db.add(cart)
        db.commit()
        db.refresh(cart)

    return cart


@router.post("/items", response_model=AddToCartResponse, status_code=status.HTTP_201_CREATED)
def add_to_cart(
    item_data: CartItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add an item to the cart
    """
    # Get or create cart
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    if not cart:
        cart = Cart(id=uuid.uuid4(), user_id=current_user.id)
        db.add(cart)
        db.commit()
        db.refresh(cart)

    # Check if variant exists
    variant = db.query(ProductVariant).filter(ProductVariant.id == item_data.variant_id).first()
    if not variant:
        raise HTTPException(status_code=404, detail="Product variant not found")

    # Check if item already in cart
    existing_item = db.query(CartItem).filter(
        CartItem.cart_id == cart.id,
        CartItem.variant_id == item_data.variant_id
    ).first()

    if existing_item:
        # Update quantity
        existing_item.quantity += item_data.quantity
        db.commit()
        db.refresh(existing_item)
        return AddToCartResponse(
            message="Item quantity updated in cart",
            cart_item=existing_item
        )
    else:
        # Add new item
        cart_item = CartItem(
            id=uuid.uuid4(),
            cart_id=cart.id,
            variant_id=item_data.variant_id,
            quantity=item_data.quantity
        )
        db.add(cart_item)
        db.commit()
        db.refresh(cart_item)
        return AddToCartResponse(
            message="Item added to cart",
            cart_item=cart_item
        )


@router.put("/items/{item_id}", response_model=CartItemResponse)
def update_cart_item(
    item_id: str,
    item_data: CartItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update the quantity of a cart item
    """
    try:
        item_uuid = uuid.UUID(item_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid item ID format")

    # Get cart
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")

    # Get cart item
    cart_item = db.query(CartItem).filter(
        CartItem.id == item_uuid,
        CartItem.cart_id == cart.id
    ).first()

    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    # Update quantity
    if item_data.quantity is not None:
        if item_data.quantity <= 0:
            # Remove item if quantity is 0 or negative
            db.delete(cart_item)
            db.commit()
            raise HTTPException(status_code=204, detail="Item removed from cart")
        cart_item.quantity = item_data.quantity

    db.commit()
    db.refresh(cart_item)
    return cart_item


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_cart_item(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Remove an item from the cart
    """
    try:
        item_uuid = uuid.UUID(item_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid item ID format")

    # Get cart
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")

    # Get cart item
    cart_item = db.query(CartItem).filter(
        CartItem.id == item_uuid,
        CartItem.cart_id == cart.id
    ).first()

    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    db.delete(cart_item)
    db.commit()

    return None
