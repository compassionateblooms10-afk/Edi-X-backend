from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import AdminUser
from app.schemas import AdminCreate, AdminLogin, Token
from app.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/api/auth", tags=["Admin Authentication"])

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register_admin(admin_in: AdminCreate, db: Session = Depends(get_db)):
    if db.query(AdminUser).filter(AdminUser.username == admin_in.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    
    admin = AdminUser(
        username=admin_in.username,
        email=admin_in.email,
        hashed_password=hash_password(admin_in.password)
    )
    db.add(admin)
    db.commit()
    
    token = create_access_token({"sub": admin.username})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
def login_admin(login_in: AdminLogin, db: Session = Depends(get_db)):
    admin = db.query(AdminUser).filter(AdminUser.email == login_in.username).first()
    if not admin or not verify_password(login_in.password, admin.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid username or password")

    token = create_access_token({"sub": admin.email})
    return {"access_token": token, "token_type": "bearer"}