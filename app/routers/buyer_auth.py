from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List

from app.database import get_db
from app.models import User, Order
from app.schemas import UserCreate, UserLogin, Token  
from app.security import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/api/buyer/auth", tags=["Buyer Authentication"])

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_buyer(user_in: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists by email or phone
    existing_user = db.query(User).filter(
        or_(User.email == user_in.email, User.phone == user_in.phone)
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=400, 
            detail="User with this email or phone already registered"
        )
    
    user = User(
        username=user_in.full_name,
        email=user_in.email,
        phone=user_in.phone,
        hashed_password=hash_password(user_in.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    token = create_access_token({"sub": user.email, "role": "buyer", "user_id": user.id})
    
    return {
        "access_token": token, 
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.username,
            "email": user.email,
            "phone": user.phone
        }
    }

@router.post("/login")
def login_buyer(login_in: UserLogin, db: Session = Depends(get_db)):
    # Search by either email or phone so both credentials work seamlessly
    identifier = login_in.email 
    user = db.query(User).filter(
        or_(User.email == identifier, User.phone == identifier)
    ).first()

    if not user or not verify_password(login_in.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid email/phone or password")

    token = create_access_token({"sub": user.email, "role": "buyer", "user_id": user.id})
    
    return {
        "access_token": token, 
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.username,
            "email": user.email,
            "phone": user.phone
        }
    }

@router.get("/me/orders")
def get_my_orders(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """Fetch orders matching either the logged-in user's customer_id or phone number."""
    orders = db.query(Order).filter(
        or_(
            Order.customer_id == current_user.id,
            Order.customer_phone == current_user.phone
        )
    ).order_by(Order.created_at.desc()).all()
    
    return orders