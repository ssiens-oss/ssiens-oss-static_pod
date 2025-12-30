"""
Multi-Tenant SaaS Database Models
Shopify App and TikTok Shop App infrastructure
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, JSON, Enum as SQLEnum, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from enum import Enum

Base = declarative_base()


class PlanTier(str, Enum):
    """Subscription plan tiers"""
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class ShopStatus(str, Enum):
    """Shop installation status"""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    UNINSTALLED = "uninstalled"
    TRIAL = "trial"


class Shop(Base):
    """
    Multi-tenant shop model
    Represents a Shopify or TikTok Shop that has installed the app
    """
    __tablename__ = "shops"

    id = Column(Integer, primary_key=True, index=True)

    # Shop identification
    shop_domain = Column(String, unique=True, index=True)  # mystore.myshopify.com
    platform = Column(String, index=True)  # "shopify" or "tiktok"
    platform_id = Column(String, unique=True, index=True)  # Platform's shop ID

    # OAuth tokens (encrypted in production)
    access_token = Column(String, nullable=False)
    scope = Column(String)

    # Shop info
    shop_name = Column(String)
    shop_email = Column(String)
    shop_owner = Column(String)
    currency = Column(String, default="USD")
    timezone = Column(String, default="UTC")

    # Subscription
    plan_tier = Column(SQLEnum(PlanTier), default=PlanTier.FREE)
    status = Column(SQLEnum(ShopStatus), default=ShopStatus.TRIAL)

    # Billing
    billing_charge_id = Column(String)  # Shopify recurring charge ID
    billing_confirmed_at = Column(DateTime)
    trial_ends_at = Column(DateTime)

    # Usage tracking
    products_imported = Column(Integer, default=0)
    orders_fulfilled = Column(Integer, default=0)
    monthly_usage = Column(Integer, default=0)

    # Limits (based on plan)
    max_products = Column(Integer, default=25)  # Free tier
    max_orders_per_month = Column(Integer, default=100)

    # Metadata
    app_settings = Column(JSON, default={})
    installed_at = Column(DateTime, default=datetime.utcnow)
    last_active_at = Column(DateTime, default=datetime.utcnow)
    uninstalled_at = Column(DateTime, nullable=True)

    # Relationships
    products = relationship("ImportedProduct", back_populates="shop", cascade="all, delete-orphan")
    orders = relationship("ShopOrder", back_populates="shop", cascade="all, delete-orphan")
    webhooks = relationship("WebhookLog", back_populates="shop", cascade="all, delete-orphan")
    usage_logs = relationship("UsageLog", back_populates="shop", cascade="all, delete-orphan")


class ImportedProduct(Base):
    """
    Products imported by merchants
    Tracks which shop imported which supplier products
    """
    __tablename__ = "imported_products"

    id = Column(Integer, primary_key=True, index=True)

    # Shop relationship
    shop_id = Column(Integer, ForeignKey("shops.id"), nullable=False)
    shop = relationship("Shop", back_populates="products")

    # Product identification
    platform_product_id = Column(String, index=True)  # Shopify/TikTok product ID
    supplier_product_id = Column(String, index=True)  # AliExpress/Printify ID
    supplier = Column(String)  # "aliexpress", "printify"

    # Product data
    title = Column(String)
    description = Column(String)
    price = Column(Numeric(10, 2))
    cost = Column(Numeric(10, 2))
    profit_margin = Column(Numeric(5, 2))  # Percentage

    # Inventory
    inventory_quantity = Column(Integer, default=0)
    sku = Column(String)

    # Status
    is_active = Column(Boolean, default=True)
    imported_at = Column(DateTime, default=datetime.utcnow)
    last_synced_at = Column(DateTime, default=datetime.utcnow)

    # Metadata
    product_data = Column(JSON, default={})  # Full product details
    sync_enabled = Column(Boolean, default=True)


class ShopOrder(Base):
    """
    Orders placed through the app
    Tracks fulfillment status per shop
    """
    __tablename__ = "shop_orders"

    id = Column(Integer, primary_key=True, index=True)

    # Shop relationship
    shop_id = Column(Integer, ForeignKey("shops.id"), nullable=False)
    shop = relationship("Shop", back_populates="orders")

    # Order identification
    platform_order_id = Column(String, index=True)  # Shopify/TikTok order ID
    order_number = Column(String)

    # Supplier order
    supplier_order_id = Column(String)  # AliExpress order ID
    supplier = Column(String)  # "aliexpress"

    # Order details
    total_price = Column(Numeric(10, 2))
    total_cost = Column(Numeric(10, 2))
    profit = Column(Numeric(10, 2))

    # Fulfillment
    fulfillment_status = Column(String, default="pending")  # pending, processing, fulfilled, failed
    tracking_number = Column(String)
    tracking_url = Column(String)

    # Timestamps
    ordered_at = Column(DateTime, default=datetime.utcnow)
    fulfilled_at = Column(DateTime, nullable=True)

    # Metadata
    order_data = Column(JSON, default={})
    customer_email = Column(String)


class ProductCatalog(Base):
    """
    Curated product catalog for merchants to browse
    Similar to DropCommerce's product library
    """
    __tablename__ = "product_catalog"

    id = Column(Integer, primary_key=True, index=True)

    # Product identification
    supplier_product_id = Column(String, unique=True, index=True)
    supplier = Column(String, index=True)  # "aliexpress", "printify"

    # Product info
    title = Column(String, index=True)
    description = Column(String)
    category = Column(String, index=True)

    # Pricing
    cost = Column(Numeric(10, 2))
    suggested_price = Column(Numeric(10, 2))
    min_price = Column(Numeric(10, 2))

    # Quality metrics
    rating = Column(Numeric(3, 2))  # 0.00 to 5.00
    reviews_count = Column(Integer, default=0)
    orders_count = Column(Integer, default=0)

    # Images
    images = Column(JSON, default=[])
    featured_image = Column(String)

    # Shipping
    ships_from = Column(String)  # "US", "EU", "CN"
    shipping_days_min = Column(Integer)
    shipping_days_max = Column(Integer)

    # Inventory
    available_quantity = Column(Integer)
    is_available = Column(Boolean, default=True)

    # Popularity
    import_count = Column(Integer, default=0)  # How many shops imported this
    trending_score = Column(Numeric(5, 2), default=0.0)

    # Metadata
    product_data = Column(JSON, default={})
    tags = Column(JSON, default=[])

    # Timestamps
    added_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_synced_at = Column(DateTime, default=datetime.utcnow)


class WebhookLog(Base):
    """
    Webhook events log
    Track all webhooks received from platforms
    """
    __tablename__ = "webhook_logs"

    id = Column(Integer, primary_key=True, index=True)

    # Shop relationship
    shop_id = Column(Integer, ForeignKey("shops.id"), nullable=True)
    shop = relationship("Shop", back_populates="webhooks")

    # Webhook details
    platform = Column(String)  # "shopify", "tiktok", "stripe"
    topic = Column(String, index=True)  # "orders/create", "app/uninstalled"

    # Payload
    payload = Column(JSON)
    headers = Column(JSON)

    # Processing
    processed = Column(Boolean, default=False)
    processed_at = Column(DateTime, nullable=True)
    error = Column(String, nullable=True)

    # Timestamp
    received_at = Column(DateTime, default=datetime.utcnow)


class UsageLog(Base):
    """
    Usage tracking for billing
    Track API calls, imports, fulfillments per shop
    """
    __tablename__ = "usage_logs"

    id = Column(Integer, primary_key=True, index=True)

    # Shop relationship
    shop_id = Column(Integer, ForeignKey("shops.id"), nullable=False)
    shop = relationship("Shop", back_populates="usage_logs")

    # Usage type
    action = Column(String, index=True)  # "import_product", "fulfill_order", "api_call"
    quantity = Column(Integer, default=1)

    # Billing period
    billing_period = Column(String, index=True)  # "2025-01"

    # Metadata
    metadata = Column(JSON, default={})

    # Timestamp
    logged_at = Column(DateTime, default=datetime.utcnow, index=True)


class PlanFeatures(Base):
    """
    Plan features and limits
    Define what each plan tier includes
    """
    __tablename__ = "plan_features"

    id = Column(Integer, primary_key=True, index=True)

    # Plan identification
    tier = Column(SQLEnum(PlanTier), unique=True, index=True)
    name = Column(String)  # "Free", "Starter", "Professional", "Enterprise"

    # Pricing
    monthly_price = Column(Numeric(10, 2))
    yearly_price = Column(Numeric(10, 2), nullable=True)

    # Limits
    max_products = Column(Integer)
    max_orders_per_month = Column(Integer)
    max_team_members = Column(Integer, default=1)

    # Features (JSON flags)
    features = Column(JSON, default={})  # {"auto_fulfillment": true, "analytics": true}

    # Metadata
    description = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class AppReview(Base):
    """
    App reviews and ratings
    Social proof for app store listing
    """
    __tablename__ = "app_reviews"

    id = Column(Integer, primary_key=True, index=True)

    # Shop relationship
    shop_id = Column(Integer, ForeignKey("shops.id"), nullable=False)

    # Review
    rating = Column(Integer)  # 1-5 stars
    title = Column(String)
    content = Column(String)

    # Response
    response = Column(String, nullable=True)
    responded_at = Column(DateTime, nullable=True)

    # Visibility
    is_published = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=False)

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow)


# Initialize database
def init_saas_db(engine):
    """Create all SaaS tables"""
    Base.metadata.create_all(bind=engine)
