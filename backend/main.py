"""
StaticWaves POD Engine - FastAPI Backend
Complete REST API for POD automation and management
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import uuid
import os
import io
from pathlib import Path

# Database imports
from sqlalchemy import create_engine, Column, String, Integer, Float, Boolean, DateTime, JSON, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import func

# Image processing
from PIL import Image
import base64

# Authentication
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

# Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./staticwaves_pod.db")
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

# Database setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# FastAPI app
app = FastAPI(
    title="StaticWaves POD Engine API",
    description="Complete REST API for Print-on-Demand automation",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Database Models
# ============================================================================

class ProductStatus(str, Enum):
    DRAFT = "draft"
    PROCESSING = "processing"
    PUBLISHED = "published"
    FAILED = "failed"
    ARCHIVED = "archived"

class PlatformType(str, Enum):
    PRINTIFY = "printify"
    SHOPIFY = "shopify"
    TIKTOK = "tiktok"
    ETSY = "etsy"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # API keys for platforms
    printify_api_key = Column(String, nullable=True)
    printify_shop_id = Column(String, nullable=True)
    shopify_store_url = Column(String, nullable=True)
    shopify_access_token = Column(String, nullable=True)

    # Usage tracking
    designs_created = Column(Integer, default=0)
    products_published = Column(Integer, default=0)
    total_revenue = Column(Float, default=0.0)

class Design(Base):
    __tablename__ = "designs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)

    # Image details
    filename = Column(String, nullable=False)
    filepath = Column(String, nullable=False)
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    file_size = Column(Integer, nullable=False)  # bytes
    format = Column(String, nullable=False)  # PNG, JPG, etc.

    # AI generation metadata
    prompt = Column(String, nullable=True)
    model = Column(String, nullable=True)
    generation_time = Column(Float, nullable=True)  # seconds

    # Tags and categorization
    tags = Column(JSON, default=list)
    category = Column(String, nullable=True)

    # Status
    status = Column(SQLEnum(ProductStatus), default=ProductStatus.DRAFT)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Product(Base):
    __tablename__ = "products"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    design_id = Column(String, nullable=False, index=True)
    user_id = Column(String, nullable=False, index=True)

    # Product details
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    product_type = Column(String, nullable=False)  # tshirt, hoodie, etc.

    # Pricing
    base_cost = Column(Float, nullable=False)  # Cost to produce
    sale_price = Column(Float, nullable=False)  # Selling price
    profit_margin = Column(Float, nullable=False)  # Calculated profit

    # Platform publishing
    platform = Column(SQLEnum(PlatformType), nullable=False)
    platform_product_id = Column(String, nullable=True)
    platform_url = Column(String, nullable=True)

    # Variants
    variants_count = Column(Integer, default=0)
    variants_data = Column(JSON, default=dict)

    # Status
    status = Column(SQLEnum(ProductStatus), default=ProductStatus.DRAFT)
    published_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)

    name = Column(String, nullable=False)
    description = Column(String, nullable=True)

    # Campaign settings
    design_count = Column(Integer, default=10)
    product_types = Column(JSON, default=["tshirt", "hoodie"])
    platforms = Column(JSON, default=["printify"])
    auto_publish = Column(Boolean, default=False)

    # AI generation settings
    prompt_template = Column(String, nullable=True)
    style_preferences = Column(JSON, default=dict)

    # Scheduling
    scheduled_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Results
    designs_generated = Column(Integer, default=0)
    products_created = Column(Integer, default=0)
    total_cost = Column(Float, default=0.0)

    status = Column(String, default="pending")  # pending, running, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)

class Analytics(Base):
    __tablename__ = "analytics"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    date = Column(DateTime, default=datetime.utcnow, index=True)

    # Daily metrics
    designs_created = Column(Integer, default=0)
    products_published = Column(Integer, default=0)
    total_views = Column(Integer, default=0)
    total_sales = Column(Integer, default=0)
    revenue = Column(Float, default=0.0)
    costs = Column(Float, default=0.0)
    profit = Column(Float, default=0.0)

    # Platform breakdown
    platform_stats = Column(JSON, default=dict)

# Create all tables
Base.metadata.create_all(bind=engine)

# ============================================================================
# Pydantic Models (API schemas)
# ============================================================================

class UserCreate(BaseModel):
    email: str
    username: str
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    is_active: bool
    is_admin: bool
    designs_created: int
    products_published: int
    total_revenue: float
    created_at: datetime

class DesignCreate(BaseModel):
    prompt: Optional[str] = None
    tags: List[str] = []
    category: Optional[str] = None

class DesignResponse(BaseModel):
    id: str
    filename: str
    width: int
    height: int
    file_size: int
    format: str
    prompt: Optional[str]
    tags: List[str]
    status: str
    created_at: datetime

class ProductCreate(BaseModel):
    design_id: str
    product_type: str
    sale_price: float
    platform: str
    auto_publish: bool = False

class ProductResponse(BaseModel):
    id: str
    title: str
    product_type: str
    sale_price: float
    profit_margin: float
    platform: str
    status: str
    platform_url: Optional[str]
    created_at: datetime

class CampaignCreate(BaseModel):
    name: str
    description: Optional[str] = None
    design_count: int = 10
    product_types: List[str] = ["tshirt", "hoodie"]
    platforms: List[str] = ["printify"]
    prompt_template: Optional[str] = None
    auto_publish: bool = False
    scheduled_at: Optional[datetime] = None

class CampaignResponse(BaseModel):
    id: str
    name: str
    design_count: int
    designs_generated: int
    products_created: int
    status: str
    created_at: datetime

class AnalyticsResponse(BaseModel):
    date: datetime
    designs_created: int
    products_published: int
    revenue: float
    profit: float
    platform_stats: Dict[str, Any]

class Token(BaseModel):
    access_token: str
    token_type: str

# ============================================================================
# Dependency Injection
# ============================================================================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

# ============================================================================
# API Endpoints - Authentication
# ============================================================================

@app.post("/api/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user exists
    existing_user = db.query(User).filter(
        (User.email == user.email) | (User.username == user.username)
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    # Create new user
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=get_password_hash(user.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/api/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login and get access token"""
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/users/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user

# ============================================================================
# API Endpoints - Designs
# ============================================================================

@app.post("/api/designs/upload", response_model=DesignResponse)
async def upload_design(
    file: UploadFile = File(...),
    prompt: Optional[str] = None,
    tags: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a new design image"""
    # Read and validate image
    contents = await file.read()
    try:
        image = Image.open(io.BytesIO(contents))
        width, height = image.size
        format = image.format
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")

    # Save file
    upload_dir = Path(f"uploads/{current_user.id}/designs")
    upload_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{uuid.uuid4()}_{file.filename}"
    filepath = upload_dir / filename

    with open(filepath, "wb") as f:
        f.write(contents)

    # Create database entry
    design = Design(
        user_id=current_user.id,
        filename=file.filename,
        filepath=str(filepath),
        width=width,
        height=height,
        file_size=len(contents),
        format=format,
        prompt=prompt,
        tags=tags.split(",") if tags else []
    )
    db.add(design)

    # Update user stats
    current_user.designs_created += 1

    db.commit()
    db.refresh(design)

    return design

@app.get("/api/designs", response_model=List[DesignResponse])
async def list_designs(
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all designs for current user"""
    query = db.query(Design).filter(Design.user_id == current_user.id)

    if status:
        query = query.filter(Design.status == status)

    designs = query.offset(skip).limit(limit).all()
    return designs

@app.get("/api/designs/{design_id}", response_model=DesignResponse)
async def get_design(
    design_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific design"""
    design = db.query(Design).filter(
        Design.id == design_id,
        Design.user_id == current_user.id
    ).first()

    if not design:
        raise HTTPException(status_code=404, detail="Design not found")

    return design

@app.get("/api/designs/{design_id}/preview")
async def get_design_preview(
    design_id: str,
    width: Optional[int] = None,
    height: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get design image with optional resizing"""
    design = db.query(Design).filter(
        Design.id == design_id,
        Design.user_id == current_user.id
    ).first()

    if not design:
        raise HTTPException(status_code=404, detail="Design not found")

    # Load and optionally resize image
    image = Image.open(design.filepath)

    if width or height:
        # Maintain aspect ratio
        if width and not height:
            ratio = width / image.width
            height = int(image.height * ratio)
        elif height and not width:
            ratio = height / image.height
            width = int(image.width * ratio)

        image = image.resize((width, height), Image.LANCZOS)

    # Return as stream
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format=design.format)
    img_byte_arr.seek(0)

    return StreamingResponse(img_byte_arr, media_type=f"image/{design.format.lower()}")

# ============================================================================
# API Endpoints - Products
# ============================================================================

@app.post("/api/products", response_model=ProductResponse)
async def create_product(
    product: ProductCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new product from a design"""
    # Verify design exists
    design = db.query(Design).filter(
        Design.id == product.design_id,
        Design.user_id == current_user.id
    ).first()

    if not design:
        raise HTTPException(status_code=404, detail="Design not found")

    # Calculate costs and profit
    base_costs = {
        "tshirt": 8.00,
        "hoodie": 20.00
    }
    base_cost = base_costs.get(product.product_type, 10.00)
    profit_margin = product.sale_price - base_cost

    # Create product record
    db_product = Product(
        design_id=product.design_id,
        user_id=current_user.id,
        title=f"{design.filename.split('.')[0]} - {product.product_type.title()}",
        product_type=product.product_type,
        base_cost=base_cost,
        sale_price=product.sale_price,
        profit_margin=profit_margin,
        platform=product.platform
    )

    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    # Publish in background if requested
    if product.auto_publish:
        background_tasks.add_task(publish_product_to_platform, db_product.id, current_user.id, db)

    return db_product

@app.get("/api/products", response_model=List[ProductResponse])
async def list_products(
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
    platform: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all products for current user"""
    query = db.query(Product).filter(Product.user_id == current_user.id)

    if status:
        query = query.filter(Product.status == status)
    if platform:
        query = query.filter(Product.platform == platform)

    products = query.offset(skip).limit(limit).all()
    return products

# ============================================================================
# API Endpoints - Campaigns
# ============================================================================

@app.post("/api/campaigns", response_model=CampaignResponse)
async def create_campaign(
    campaign: CampaignCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new design generation campaign"""
    db_campaign = Campaign(
        user_id=current_user.id,
        name=campaign.name,
        description=campaign.description,
        design_count=campaign.design_count,
        product_types=campaign.product_types,
        platforms=campaign.platforms,
        prompt_template=campaign.prompt_template,
        auto_publish=campaign.auto_publish,
        scheduled_at=campaign.scheduled_at
    )

    db.add(db_campaign)
    db.commit()
    db.refresh(db_campaign)

    # Run campaign in background if not scheduled
    if not campaign.scheduled_at:
        background_tasks.add_task(run_campaign, db_campaign.id, current_user.id, db)

    return db_campaign

@app.get("/api/campaigns", response_model=List[CampaignResponse])
async def list_campaigns(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all campaigns for current user"""
    campaigns = db.query(Campaign).filter(
        Campaign.user_id == current_user.id
    ).offset(skip).limit(limit).all()

    return campaigns

# ============================================================================
# API Endpoints - Analytics
# ============================================================================

@app.get("/api/analytics/dashboard")
async def get_dashboard_analytics(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get dashboard analytics for the specified period"""
    start_date = datetime.utcnow() - timedelta(days=days)

    # Aggregate metrics
    total_designs = db.query(func.count(Design.id)).filter(
        Design.user_id == current_user.id,
        Design.created_at >= start_date
    ).scalar()

    total_products = db.query(func.count(Product.id)).filter(
        Product.user_id == current_user.id,
        Product.created_at >= start_date
    ).scalar()

    published_products = db.query(func.count(Product.id)).filter(
        Product.user_id == current_user.id,
        Product.status == ProductStatus.PUBLISHED,
        Product.created_at >= start_date
    ).scalar()

    total_revenue = db.query(func.sum(Product.sale_price)).filter(
        Product.user_id == current_user.id,
        Product.status == ProductStatus.PUBLISHED,
        Product.created_at >= start_date
    ).scalar() or 0.0

    total_profit = db.query(func.sum(Product.profit_margin)).filter(
        Product.user_id == current_user.id,
        Product.status == ProductStatus.PUBLISHED,
        Product.created_at >= start_date
    ).scalar() or 0.0

    # Platform breakdown
    platform_stats = {}
    for platform in PlatformType:
        count = db.query(func.count(Product.id)).filter(
            Product.user_id == current_user.id,
            Product.platform == platform.value,
            Product.status == ProductStatus.PUBLISHED
        ).scalar()
        platform_stats[platform.value] = count

    return {
        "period_days": days,
        "total_designs": total_designs,
        "total_products": total_products,
        "published_products": published_products,
        "total_revenue": total_revenue,
        "total_profit": total_profit,
        "platform_stats": platform_stats,
        "avg_profit_per_product": total_profit / published_products if published_products > 0 else 0
    }

@app.get("/api/analytics/trends")
async def get_analytics_trends(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get daily analytics trends"""
    start_date = datetime.utcnow() - timedelta(days=days)

    analytics = db.query(Analytics).filter(
        Analytics.user_id == current_user.id,
        Analytics.date >= start_date
    ).order_by(Analytics.date).all()

    return analytics

# ============================================================================
# Background Tasks
# ============================================================================

async def publish_product_to_platform(product_id: str, user_id: str, db: Session):
    """Background task to publish product to platform"""
    # This would call the actual platform APIs
    # For now, just simulate the process
    await asyncio.sleep(2)

    product = db.query(Product).filter(Product.id == product_id).first()
    if product:
        product.status = ProductStatus.PUBLISHED
        product.published_at = datetime.utcnow()
        product.platform_product_id = f"mock_{uuid.uuid4()}"
        product.platform_url = f"https://example.com/products/{product.id}"

        db.commit()

async def run_campaign(campaign_id: str, user_id: str, db: Session):
    """Background task to run a campaign"""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        return

    campaign.status = "running"
    db.commit()

    # Simulate campaign execution
    for i in range(campaign.design_count):
        await asyncio.sleep(1)  # Simulate AI generation time
        campaign.designs_generated += 1
        db.commit()

    campaign.status = "completed"
    campaign.completed_at = datetime.utcnow()
    db.commit()

# ============================================================================
# Health Check
# ============================================================================

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "timestamp": datetime.utcnow()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
