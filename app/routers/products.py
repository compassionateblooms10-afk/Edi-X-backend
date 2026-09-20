import os, uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Product, AdminUser
from app.schemas import ProductOut
from app.security import get_current_admin
from app.config import settings

router = APIRouter(prefix="/api/products", tags=["Standard Products"])

@router.get("", response_model=List[ProductOut])
def list_products(db: Session = Depends(get_db)):
    return db.query(Product).all()

@router.post("", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
async def create_product(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    price: float = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin) # Protected Admin Endpoint
):
    # Save Image File locally
    filename = f"{uuid.uuid4()}_{image.filename}"
    file_path = os.path.join(settings.UPLOAD_DIR, filename)
    with open(file_path, "wb") as f:
        f.write(await image.read())

    image_url = f"/uploads/{filename}"
    product = Product(title=title, description=description, price=price, image_url=image_url)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Product not found"
        )
    
    db.delete(product)
    db.commit()
    return None