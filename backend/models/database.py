"""
Database Models for Automated Dropshipping Platform
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON, ForeignKey, Text, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()


class PlatformType(str, enum.Enum):
    """Supported e-commerce platforms"""
    SHOPIFY = "shopify"
    ALIEXPRESS = "aliexpress"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    YOUTUBE = "youtube"
    PRINTIFY = "printify"
    WOOCOMMERCE = "woocommerce"


class OrderStatus(str, enum.Enum):
    """Order processing statuses"""
    PENDING = "pending"
    PROCESSING = "processing"
    FULFILLED = "fulfilled"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class Product(Base):
    """Product catalog"""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String(255), unique=True, index=True)  # Platform product ID
    platform = Column(Enum(PlatformType), nullable=False)

    title = Column(String(500), nullable=False)
    description = Column(Text)
    sku = Column(String(255), unique=True, index=True)

    cost_price = Column(Float, nullable=False)
    selling_price = Column(Float, nullable=False)
    markup_percentage = Column(Float, default=30.0)

    stock_quantity = Column(Integer, default=0)
    low_stock_threshold = Column(Integer, default=10)

    supplier_id = Column(Integer, ForeignKey("suppliers.id"))
    supplier = relationship("Supplier", back_populates="products")

    images = Column(JSON)  # List of image URLs
    variants = Column(JSON)  # Product variants
    meta_data = Column(JSON)  # Platform-specific metadata

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    orders = relationship("OrderItem", back_populates="product")


class Supplier(Base):
    """Supplier information"""
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    platform = Column(Enum(PlatformType), nullable=False)

    contact_email = Column(String(255))
    rating = Column(Float, default=0.0)
    total_orders = Column(Integer, default=0)

    shipping_time_min = Column(Integer)  # Days
    shipping_time_max = Column(Integer)

    api_credentials = Column(JSON)  # Encrypted API keys
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    products = relationship("Product", back_populates="supplier")


class Order(Base):
    """Customer orders"""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String(255), unique=True, index=True)
    platform = Column(Enum(PlatformType), nullable=False)

    customer_email = Column(String(255))
    customer_name = Column(String(255))

    shipping_address = Column(JSON)
    billing_address = Column(JSON)

    subtotal = Column(Float, nullable=False)
    shipping_cost = Column(Float, default=0.0)
    tax = Column(Float, default=0.0)
    total = Column(Float, nullable=False)

    profit = Column(Float, default=0.0)

    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)

    tracking_number = Column(String(255))
    shipped_at = Column(DateTime)
    delivered_at = Column(DateTime)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    items = relationship("OrderItem", back_populates="order")
    fulfillments = relationship("Fulfillment", back_populates="order")


class OrderItem(Base):
    """Individual items in an order"""
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))

    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    cost = Column(Float, nullable=False)

    variant_details = Column(JSON)

    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="orders")


class Fulfillment(Base):
    """Order fulfillment tracking"""
    __tablename__ = "fulfillments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))

    supplier_order_id = Column(String(255))  # Order ID at supplier
    supplier_id = Column(Integer, ForeignKey("suppliers.id"))

    status = Column(String(50))
    tracking_number = Column(String(255))
    carrier = Column(String(100))

    processed_at = Column(DateTime)
    shipped_at = Column(DateTime)

    notes = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    order = relationship("Order", back_populates="fulfillments")


class Campaign(Base):
    """Marketing campaigns"""
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    platform = Column(Enum(PlatformType), nullable=False)

    campaign_type = Column(String(100))  # video_ad, carousel, collection

    budget = Column(Float)
    daily_budget = Column(Float)

    targeting = Column(JSON)  # Audience targeting
    creative_assets = Column(JSON)  # Images, videos

    status = Column(String(50), default="draft")

    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    spend = Column(Float, default=0.0)
    revenue = Column(Float, default=0.0)

    started_at = Column(DateTime)
    ended_at = Column(DateTime)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Inventory(Base):
    """Inventory tracking and history"""
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))

    change_type = Column(String(50))  # sync, sale, return, adjustment
    quantity_before = Column(Integer)
    quantity_after = Column(Integer)
    quantity_change = Column(Integer)

    reason = Column(String(255))

    created_at = Column(DateTime, default=datetime.utcnow)


class Analytics(Base):
    """Daily analytics snapshots"""
    __tablename__ = "analytics"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, nullable=False, index=True)
    platform = Column(Enum(PlatformType))

    total_sales = Column(Float, default=0.0)
    total_orders = Column(Integer, default=0)
    total_profit = Column(Float, default=0.0)

    ad_spend = Column(Float, default=0.0)
    ad_revenue = Column(Float, default=0.0)
    roas = Column(Float, default=0.0)  # Return on Ad Spend

    unique_visitors = Column(Integer, default=0)
    conversion_rate = Column(Float, default=0.0)

    top_products = Column(JSON)

    created_at = Column(DateTime, default=datetime.utcnow)
