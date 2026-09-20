from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from app.models import OrderStatus

# --- Auth Schemas ---
class AdminCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class AdminLogin(BaseModel):
    username: str
    password: str


class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    phone :str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# --- Product Schemas ---
class ProductOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    price: float
    image_url: str
    created_at: datetime

    class Config:
        from_attributes = True

# --- Custom Item Schemas ---
class CustomItemOut(BaseModel):
    id: int
    name: str
    category: str
    unit_price: float
    image_url: str
    created_at: datetime

    class Config:
        from_attributes = True

# --- Order Schemas ---
class OrderItemInput(BaseModel):
    item_id: int
    quantity: int

class OrderCreateInput(BaseModel):
    customer_name: str
    customer_phone: str
    delivery_address: str
    delivery_date: str
    base_product_id: Optional[int] = None # Optional standard product
    custom_items: List[OrderItemInput] = [] # List of single items selected

class OrderAdvancePaymentUpdate(BaseModel):
    advance_amount: float

class OrderOut(BaseModel):
    id: int
    order_code: str
    customer_name: str
    customer_phone: str
    delivery_address: str
    delivery_date: str
    items_breakdown: list
    total_amount: float
    advance_paid_amount: float
    remaining_balance: float
    status: OrderStatus
    created_at: datetime

    class Config:
        from_attributes = True