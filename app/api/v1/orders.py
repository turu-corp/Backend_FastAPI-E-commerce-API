from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, selectinload
from typing import List, Optional, Any
from datetime import datetime, timezone
import uuid

from app.database import get_db
from app.models.order import Order, OrderItem, Payment, Shipping, Discount
from app.models.cart import Cart, CartItem
from app.models.product import ProductVariant
from app.models.user import User, Address
from app.schemas.order import (
    OrderCreate, OrderResponse, OrderListResponse, OrderPreviewRequest, OrderPreviewResponse,
    OrderPreviewItem, OrderStatus, PaymentCreate, PaymentResponse, WebhookPayload,
    OrderUpdateStatusByAdmin, OrderUpdateStatusByCustomer, PaymentStatus
)
from app.dependencies import get_current_user, get_admin_user
from app.services.email_service import EmailService

router = APIRouter()


def validate_discount(code: str, subtotal: int, db: Session) -> Optional[Discount]:
    """Validate discount code and return discount object"""
    discount = db.query(Discount).filter(Discount.code == code).first()
    
    if not discount:
        return None
    
    if not discount.is_active:
        return None

    # Check if discount is active
    now = datetime.now(timezone.utc)
    if discount.valid_from > now:
        return None

    if discount.valid_until and now > discount.valid_until:
        return None
    
    # Check minimum purchase
    if subtotal < discount.min_purchase:
        return None
    
    return discount


def calculate_discount_amount(discount: Discount, subtotal: int) -> int:
    """Calculate discount amount based on type"""
    if discount.percentage is not None:
        return int(subtotal * (discount.percentage / 100))
    elif discount.fixed_amount is not None:
        return min(discount.fixed_amount, subtotal)
    return 0


@router.post("/preview", response_model=OrderPreviewResponse)
def preview_order(
    preview_data: OrderPreviewRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a preview of the order with all cost calculations before finalizing.
    """
    # 1. Validate address
    address = db.query(Address).filter(
        Address.id == preview_data.address_id,
        Address.user_id == current_user.id
    ).first()
    if not address:
        raise HTTPException(status_code=404, detail="Address not found for this user.")

    # 2. Get cart items
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    if not cart or not cart.items:
        raise HTTPException(status_code=400, detail="Cart is empty.")

    # 3. Calculate subtotal and validate stock
    subtotal = 0
    preview_items = []
    is_stock_sufficient = True

    for cart_item in cart.items:
        variant = cart_item.variant  # Access variant via relationship

        if not variant:
            # This case should be rare if data is consistent
            raise HTTPException(status_code=404, detail=f"Variant for cart item {cart_item.id} not found.")

        if variant.stock < cart_item.quantity:
            is_stock_sufficient = False

        # In a real app, this would be product.base_price + variant.price_adjustment
        price_per_unit = variant.price_adjustment
        item_subtotal = price_per_unit * cart_item.quantity
        subtotal += item_subtotal

        preview_items.append(
            OrderPreviewItem(
                variant_id=variant.id,
                product_name=variant.product.name, # Access product name
                sku=variant.sku,
                quantity=cart_item.quantity,
                price_per_unit=price_per_unit,
                subtotal=item_subtotal,
            )
        )

    # 4. Simulate shipping cost calculation
    # In a real application, you would call a third-party API (e.g., RajaOngkir)
    # using the address details and total weight of items.
    shipping_cost = 15000  # Dummy value for now

    # 5. Apply discount if provided
    discount_amount = 0
    if preview_data.discount_code:
        discount = validate_discount(preview_data.discount_code, subtotal, db)
        if discount:
            discount_amount = calculate_discount_amount(discount, subtotal)

    # 6. Calculate grand total
    grand_total = subtotal + shipping_cost - discount_amount
    if grand_total < 0:
        grand_total = 0

    # 7. Return the preview
    return OrderPreviewResponse(
        subtotal=subtotal,
        shipping_cost=shipping_cost,
        discount_amount=discount_amount,
        grand_total=grand_total,
        items=preview_items,
        is_stock_sufficient=is_stock_sufficient,
    )


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create order from cart items (checkout)
    
    Workflow Automation: Sends order confirmation email after successful order
    """
    try:
        # Validate address
        address = db.query(Address).filter(
            Address.id == order_data.address_id,
            Address.user_id == current_user.id
        ).first()
        if not address:
            raise HTTPException(status_code=404, detail="Address not found")
        
        # Get cart with items and variants preloaded to avoid N+1 queries
        cart = db.query(Cart).options(
            selectinload(Cart.items).selectinload(CartItem.variant)
        ).filter(Cart.user_id == current_user.id).first()
        
        if not cart or not cart.items:
            raise HTTPException(status_code=400, detail="Cart is empty")
        
        # Validate shipping method
        shipping_option = db.query(Shipping).filter(
            Shipping.carrier == order_data.shipping_name,
            Shipping.is_active == True
        ).first()
        if not shipping_option:
            raise HTTPException(status_code=404, detail="Invalid shipping method selected.")
        
        # Calculate subtotal and validate stock
        subtotal = 0
        order_items_data: List[dict[str, Any]] = []
        
        for cart_item in cart.items:
            variant = cart_item.variant
            if variant.stock < cart_item.quantity:
                raise HTTPException(
                    status_code=400,
                    detail=f"Insufficient stock for {variant.sku}. Only {variant.stock} available"
                )
            
            price_per_unit = variant.price_adjustment
            item_subtotal = price_per_unit * cart_item.quantity
            subtotal += item_subtotal
            
            order_items_data.append({
                "variant": variant,
                "quantity": cart_item.quantity,
                "price_per_unit": price_per_unit,
                "subtotal": item_subtotal
            })
        
        # Apply discount
        discount_amount = 0
        discount_obj = None
        if order_data.discount_code:
            discount_obj = validate_discount(order_data.discount_code, subtotal, db)
            if discount_obj:
                discount_amount = calculate_discount_amount(discount_obj, subtotal)
        
        # SERVER-SIDE CALCULATION of total price
        shipping_cost = shipping_option.cost
        total_price = subtotal + shipping_cost - discount_amount
        if total_price < 0:
            total_price = 0
        
        # Create order
        new_order = Order(
            user_id=current_user.id,
            address_id=order_data.address_id,
            shipping_id=shipping_option.id,
            total_price=total_price,
            status=OrderStatus.PENDING,
            discount_id=discount_obj.id if discount_obj else None
        )
        db.add(new_order)
        
        # Create order items and update stock
        for item_data in order_items_data:
            order_item = OrderItem(
                order=new_order,
                variant_id=item_data["variant"].id,
                quantity=item_data["quantity"],
                price_per_unit=item_data["price_per_unit"],
                subtotal=item_data["subtotal"]
            )
            db.add(order_item)
            item_data["variant"].stock -= item_data["quantity"]
        
        # Clear cart
        db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
        
        db.commit()
        db.refresh(new_order)

        # WORKFLOW AUTOMATION: Send order confirmation email
        await EmailService.send_order_confirmation(
            current_user.email,
            current_user.name,
            str(new_order.id),
            total_price
        )
        
        return new_order

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        # In production, you should log the error `e`
        raise HTTPException(status_code=500, detail="An internal error occurred while creating the order.")


@router.post("/{order_id}/pay", response_model=PaymentResponse)
def create_payment_for_order(
    order_id: str,
    payment_data: PaymentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a payment record for an existing order.
    Chosen payment methods:
    - credit_card
    - debit_card
    - bank_transfer
    - e_wallet

    """
    try:
        order_uuid = uuid.UUID(order_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid order ID format")

    # 1. Find the order and ensure it belongs to the user
    order = db.query(Order).filter(
        Order.id == order_uuid,
        Order.user_id == current_user.id
    ).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # 2. Check if the order is in a payable state
    if order.status != OrderStatus.PENDING:
        raise HTTPException(status_code=400, detail=f"Order with status '{order.status}' cannot be paid.")

    # 3. Create the payment record
    # In a real scenario, you would now interact with a payment gateway API
    new_payment = Payment(
        order_id=order.id,
        method=payment_data.method.value, # Using .value to get the string "credit_card", etc.
        status="pending" # The status will be updated by the payment gateway webhook
    )
    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)

    return new_payment


@router.post("/webhooks/payment-gateway", status_code=status.HTTP_200_OK)
def handle_payment_webhook(
    payload: WebhookPayload,
    # Di produksi, Anda akan mendapatkan signature dari header
    # x_signature: str = Header(...),
    db: Session = Depends(get_db)
):
    """
    [SIMULATION] (Public, but Verified)
    
    Endpoint to receive notifications from the Payment Gateway.

    When the payment is successful, this endpoint will change the Order status to 'processing'.

    Payment status: 'completed', 'pending', 'failed', 'refunded'.
    """
    # Validasi payload (order_id, payment_status) sudah dilakukan oleh FastAPI berkat skema WebhookPayload.

    # 1. Verifikasi webhook (sangat penting di produksi!)
    # secret = "YOUR_WEBHOOK_SECRET_FROM_PAYMENT_GATEWAY"
    # verify_signature(payload, x_signature, secret) -> raises HTTPException if invalid

    # 2. Cari order dan payment
    order = db.get(Order, payload.order_id)
    if not order:
        # Mungkin log error, tapi jangan kirim 404 ke webhook
        return {"message": "Order not found, notification ignored."}

    payment = db.query(Payment).filter(Payment.order_id == order.id).first()

    # 3. Update status jika pembayaran berhasil
    if payload.payment_status == PaymentStatus.COMPLETED:
        if payment:
            payment.status = PaymentStatus.COMPLETED
            payment.transaction_time = datetime.now(timezone.utc)
        
        if order.status == OrderStatus.PENDING:
            order.status = OrderStatus.PROCESSING
        
        db.commit()
        # Kirim email notifikasi pembayaran berhasil ke customer

    return {"message": "Webhook processed successfully"}

@router.get("/", response_model=List[OrderListResponse])
def get_my_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[OrderStatus] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's orders with optional status filter
    """
    from sqlalchemy import func

    # Efficiently query orders and count of items in one go
    query = db.query(
        Order,
        func.count(OrderItem.id).label("items_count")
    ).outerjoin(OrderItem, Order.id == OrderItem.order_id).filter(
        Order.user_id == current_user.id
    ).group_by(Order.id)
    
    if status:
        query = query.filter(Order.status == status)
    
    results = query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()

    # Construct the response using the custom classmethod
    return [
        OrderListResponse.from_orm_with_items_count(order, items_count) for order, items_count in results
    ]


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get order details by ID
    """
    try:
        order_uuid = uuid.UUID(order_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid order ID format")
    
    # Preload items to avoid extra queries when serializing the response
    order = db.query(Order).filter(
        Order.id == order_uuid,
        Order.user_id == current_user.id
    ).options(selectinload(Order.items)).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return order


@router.patch("/{order_id}/cancel", response_model=OrderResponse)
def cancel_order(
    order_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cancel an order (only if status is pending or processing)
    """
    try:
        order_uuid = uuid.UUID(order_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid order ID format")
    
    try:
        # Preload items and their variants to efficiently restore stock
        order = db.query(Order).options(
            selectinload(Order.items).selectinload(OrderItem.variant)
        ).filter(
            Order.id == order_uuid,
            Order.user_id == current_user.id
        ).first()
        
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        if order.status not in [OrderStatus.PENDING, OrderStatus.PROCESSING]:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot cancel order with status {order.status}"
            )
        
        # Restore stock
        for item in order.items:
            if item.variant:
                item.variant.stock += item.quantity
        
        order.status = OrderStatus.CANCELLED
        
        # Update payment status if it exists
        payment = db.query(Payment).filter(Payment.order_id == order.id).first()
        if payment and payment.status == PaymentStatus.COMPLETED:
            payment.status = PaymentStatus.REFUNDED
        
        db.commit()
        db.refresh(order)
        
        return order
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        # In production, you should log the error `e`
        raise HTTPException(status_code=500, detail="An internal error occurred while cancelling the order.")


@router.patch("/{order_id}/ship", response_model=OrderResponse)
def ship_order_by_admin(
    order_id: str,
    order_update: OrderUpdateStatusByAdmin, # Menggunakan schema baru
    current_user: User = Depends(get_admin_user), # Hanya untuk admin
    db: Session = Depends(get_db)
):
    """
    (Admin Only) Update order status to 'shipped'.
    """
    try:
        order_uuid = uuid.UUID(order_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid order ID format")

    order = db.query(Order).filter(Order.id == order_uuid).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.status != OrderStatus.PROCESSING:
        raise HTTPException(
            status_code=400,
            detail=f"Order must be in 'processing' status to be shipped. Current status: {order.status}"
        )

    order.status = order_update.status # Akan selalu 'shipped' karena validasi schema
    db.commit()
    db.refresh(order)
    # Kirim email notifikasi pengiriman ke customer
    return order


@router.patch("/{order_id}/deliver", response_model=OrderResponse)
def deliver_order_by_customer(
    order_id: str,
    order_update: OrderUpdateStatusByCustomer, # Menggunakan schema baru
    current_user: User = Depends(get_current_user), # Untuk customer
    db: Session = Depends(get_db)
):
    """
    (Customer) Confirm that the order has been delivered.
    """
    try:
        order_uuid = uuid.UUID(order_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid order ID format")

    order = db.query(Order).filter(Order.id == order_uuid, Order.user_id == current_user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.status != OrderStatus.SHIPPED:
        raise HTTPException(status_code=400, detail=f"Cannot confirm delivery for an order that is not 'shipped'.")

    order.status = order_update.status # Akan selalu 'delivered'
    db.commit()
    db.refresh(order)
    return order
