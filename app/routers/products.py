import os, uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Product, AdminUser
from app.schemas import ProductOut
from app.security import get_current_admin
from app.config import settings
from app.services import upload_image_to_r2

router = APIRouter(prefix="/api/products", tags=["Standard Products"])

@router.get("", response_model=List[ProductOut])
def list_products(db: Session = Depends(get_db)):
    return db.query(Product).all()

@router.post("/image")
async def upload_single_image(file: UploadFile = File(...)):
    """Uploads a single image to Cloudflare R2 and returns the image URL.

    Use this when uploading image assets before form submission.
    """
    image_url = upload_image_to_r2(file, folder="products")
    return {"status": "success", "image_url": image_url}

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
    

    """Uploads the product image to R2 and creates the product entry."""
    # Upload image to R2
    image_url = upload_image_to_r2(image, folder="products")
    product = Product(title=title, description=description, price=price, image_url=image_url)
    db.add(product)
    db.commit()
    db.refresh(product)
    return {
        "status": "success",
        "product": {
            "title": title,
            "price": price,
            "description": description,
            "image_url": image_url,
        },
    }

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