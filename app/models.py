import enum
from sqlalchemy import Column, Integer, String, Float, Enum, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class OrderStatus(str, enum.Enum):
    PENDING = "PENDING"
    ADVANCE_PAID = "ADVANCE_PAID"
    FULLY_PAID = "FULLY_PAID"
    CANCELLED = "CANCELLED"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String,unique=True,index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    orders = relationship("Order", back_populates="customer")

class AdminUser(Base):
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Product(Base):
    """Standard pre-made items (e.g. 12-Rose Bouquet, Giant Bear Box)"""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    image_url = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class CustomItem(Base):
    """Individual single items for custom builder (e.g. 1 Flower, 1 Chocolate)"""
    __tablename__ = "custom_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False) # e.g., 'flowers', 'chocolates', 'toys', 'bases'
    unit_price = Column(Float, nullable=False)
    image_url = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Order(Base):
    """Customer Orders with WhatsApp Advance Payment Tracking"""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    order_code = Column(String, unique=True, index=True, nullable=False) # e.g. ORD-1001
    customer_name = Column(String, nullable=False)
    customer_phone = Column(String, nullable=False)
    delivery_address = Column(String, nullable=False)
    delivery_date = Column(String, nullable=False)
    
    # JSON breakdown: [{"type": "custom_item", "item_id": 1, "name": "Rose", "unit_price": 200, "qty": 3}]
    items_breakdown = Column(JSON, nullable=False)
    
    total_amount = Column(Float, nullable=False)
    advance_paid_amount = Column(Float, default=0.0)
    remaining_balance = Column(Float, nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)

    customer = relationship("User", back_populates="orders")
    