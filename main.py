import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.config import settings
from app.routers import auth, products, custom_items, orders, buyer_auth

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

# Auto-create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME)
origins = [
    getattr(settings, "FRONTEND_URL", "https://edi-x-sri-lanka.netlify.app"),
    "http://localhost:3000",
    "http://localhost:8000",
    "*"  # Remove '*' once frontend URL is finalized
]
# Enable CORS for frontend web apps
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # Change to explicit domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded images statically
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Include Routers
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(custom_items.router)
app.include_router(orders.router)
app.include_router(buyer_auth.router)

@app.get("/")
def root():
    return {"message": "Gift Shop Backend API is running!"}