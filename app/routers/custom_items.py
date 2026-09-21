import os, uuid
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import CustomItem, AdminUser
from app.schemas import CustomItemOut
from app.security import get_current_admin
from app.config import settings
from app.services import upload_image_to_r2

router = APIRouter(prefix="/api/custom-items", tags=["Customizable Component Items"])

@router.get("", response_model=List[CustomItemOut])
def list_custom_items(db: Session = Depends(get_db)):
    return db.query(CustomItem).all()

@router.post("", response_model=CustomItemOut, status_code=status.HTTP_201_CREATED)
async def add_custom_item(
    name: str = Form(...),
    category: str = Form(...), # e.g., 'flowers', 'chocolates', 'toys', 'bases'
    unit_price: float = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin) # Protected Admin Endpoint
):
    image_url = upload_image_to_r2(image, folder="products")
    item = CustomItem(name=name, category=category, unit_price=unit_price, image_url=image_url)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_custom_item(
    item_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    item = db.query(CustomItem).filter(CustomItem.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Custom item not found"
        )
    
    db.delete(item)
    db.commit()
    return None