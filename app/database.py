from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# 1. Handle PostgreSQL URL prefix
db_url = settings.DATABASE_URL
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

# 2. Create the Database Engine
engine = create_engine(
    db_url,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True  # Recovers automatically from dropped connections
)

# 3. Create Session Factory & Base Class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 4. Database Dependency for Routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()