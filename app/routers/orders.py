import random
from typing import List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Order, Product, CustomItem, OrderStatus, AdminUser,User
from app.schemas import OrderCreateInput, OrderOut, OrderAdvancePaymentUpdate
from app.security import get_current_admin, get_current_user_optional

router = APIRouter(prefix="/api/orders", tags=["Orders & Payments"])





class CustomItemInput(BaseModel):
    item_id: int
    quantity: int
    bundle_label: Optional[str] = "Custom Component"  # e.g., "Custom Bouquet", "Custom Gift Box"

class StandardProductInput(BaseModel):
    product_id: int
    quantity: int = 1

class UnifiedOrderCreateInput(BaseModel):
    customer_name: str
    customer_phone: str
    delivery_address: str
    delivery_date: str
    standard_products: List[StandardProductInput] = []  # Multiple store products (e.g. Teddy, Mug)
    custom_items: List[CustomItemInput] = []             # Multiple custom components / box items


@router.post("", status_code=status.HTTP_201_CREATED)
def place_unified_order(payload: UnifiedOrderCreateInput, db: Session = Depends(get_db), current_user: Optional[User] = Depends(get_current_user_optional)):
    """
    Unified Endpoint: Places an order containing standard products (e.g., Teddy Bear),
    custom gift boxes, and custom flower bouquets all in a single transaction.
    """
    total_amount = 0.0
    breakdown = []

    # 1. Process all selected standard products
    for p_input in payload.standard_products:
        prod = db.query(Product).filter(Product.id == p_input.product_id).first()
        if not prod:
            raise HTTPException(status_code=400, detail=f"Standard product ID {p_input.product_id} not found")
        
        cost = prod.price * p_input.quantity
        total_amount += cost
        breakdown.append({
            "type": "standard_product",
            "id": prod.id,
            "title": prod.title,
            "unit_price": prod.price,
            "qty": p_input.quantity,
            "subtotal": cost
        })

    # 2. Process all selected custom items / custom box components
    for c_input in payload.custom_items:
        item = db.query(CustomItem).filter(CustomItem.id == c_input.item_id).first()
        if not item:
            raise HTTPException(status_code=400, detail=f"Custom item ID {c_input.item_id} not found")
        
        cost = item.unit_price * c_input.quantity
        total_amount += cost
        breakdown.append({
            "type": "custom_component",
            "bundle_label": c_input.bundle_label,
            "id": item.id,
            "name": item.name,
            "category": item.category,
            "unit_price": item.unit_price,
            "qty": c_input.quantity,
            "subtotal": cost
        })

    if total_amount <= 0:
        raise HTTPException(status_code=400, detail="Cannot place an empty order. Please select at least one item.")

    order_code = f"ORD-{random.randint(10000, 99999)}"


    order = Order(
        customer_id=current_user.id if current_user else None,
        order_code=order_code,
        customer_name=payload.customer_name,
        customer_phone=payload.customer_phone,
        delivery_address=payload.delivery_address,
        delivery_date=payload.delivery_date,
        items_breakdown=breakdown,
        total_amount=round(total_amount, 2),
        advance_paid_amount=0.0,
        remaining_balance=round(total_amount, 2),
        status=OrderStatus.PENDING
    )

    db.add(order)
    db.commit()
    db.refresh(order)

    return order

# --- ADMIN ENDPOINTS ---

@router.get("/admin/all", response_model=List[OrderOut])
def get_all_orders_admin(db: Session = Depends(get_db), admin: AdminUser = Depends(get_current_admin)):
    """Admin views all customer orders in Admin Website."""
    return db.query(Order).order_by(Order.created_at.desc()).all()

@router.patch("/admin/{order_id}/advance-payment", response_model=OrderOut)
def update_advance_payment(
    order_id: int, 
    payment: OrderAdvancePaymentUpdate, 
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    """Admin confirms WhatsApp receipt & updates advance payment amount."""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.advance_paid_amount = payment.advance_amount
    order.remaining_balance = max(0.0, order.total_amount - payment.advance_amount)
    
    if order.remaining_balance == 0:
        order.status = OrderStatus.FULLY_PAID
    else:
        order.status = OrderStatus.ADVANCE_PAID

    db.commit()
    db.refresh(order)
    return order

