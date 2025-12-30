"""
Application Settings and Configuration
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application configuration settings"""

    # App Settings
    APP_NAME: str = "Automated Dropshipping Platform"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    SECRET_KEY: str

    # Database
    DATABASE_URL: str

    # Shopify
    SHOPIFY_API_KEY: str
    SHOPIFY_API_SECRET: str
    SHOPIFY_ACCESS_TOKEN: str
    SHOPIFY_SHOP_URL: str
    SHOPIFY_API_VERSION: str = "2025-10"

    # AliExpress
    ALIEXPRESS_APP_KEY: str
    ALIEXPRESS_APP_SECRET: str
    ALIEXPRESS_ACCESS_TOKEN: Optional[str] = None
    ALIEXPRESS_EMAIL: Optional[str] = None
    ALIEXPRESS_PASSWORD: Optional[str] = None

    # TikTok
    TIKTOK_APP_KEY: str
    TIKTOK_APP_SECRET: str
    TIKTOK_ACCESS_TOKEN: Optional[str] = None
    TIKTOK_SHOP_ID: Optional[str] = None

    # Meta (Facebook & Instagram)
    META_ACCESS_TOKEN: Optional[str] = None
    META_CATALOG_ID: Optional[str] = None
    META_AD_ACCOUNT_ID: Optional[str] = None

    # YouTube
    YT_API_KEY: Optional[str] = None
    GOOGLE_CREDENTIALS: Optional[str] = None
    MERCHANT_ID: Optional[str] = None

    # Printify
    PRINTIFY_API_TOKEN: Optional[str] = None

    # WooCommerce
    WOOCOMMERCE_URL: Optional[str] = None
    WOOCOMMERCE_CONSUMER_KEY: Optional[str] = None
    WOOCOMMERCE_CONSUMER_SECRET: Optional[str] = None

    # Redis (for Celery)
    REDIS_URL: str = "redis://localhost:6379/0"

    # Stripe (for billing)
    STRIPE_API_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None

    # Webhook Secrets
    SHOPIFY_WEBHOOK_SECRET: Optional[str] = None
    TIKTOK_WEBHOOK_SECRET: Optional[str] = None

    # API Rate Limits
    RATE_LIMIT_PER_MINUTE: int = 60

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
