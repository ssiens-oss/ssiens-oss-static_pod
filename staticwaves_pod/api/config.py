import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    PRINTIFY_API_KEY = os.getenv("PRINTIFY_API_KEY", "")
    PRINTIFY_SHOP_ID = os.getenv("PRINTIFY_SHOP_ID", "")
    SHOPIFY_STORE = os.getenv("SHOPIFY_STORE", "")
    SHOPIFY_TOKEN = os.getenv("SHOPIFY_TOKEN", "")
    TIKTOK_MODE = os.getenv("TIKTOK_MODE", "guard")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
