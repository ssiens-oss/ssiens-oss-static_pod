"""
Product Catalog API
Browse and import curated products (DropCommerce-style)
"""
from fastapi import APIRouter, Query, HTTPException, Depends
from typing import List, Optional
from sqlalchemy.orm import Session
from loguru import logger

from models.saas import ProductCatalog, ImportedProduct, Shop
from workers.product_import import import_product_by_id

router = APIRouter(prefix="/catalog", tags=["Product Catalog"])


# Database dependency (placeholder)
def get_db():
    pass


@router.get("/products")
async def browse_products(
    category: Optional[str] = Query(None, description="Filter by category"),
    min_price: Optional[float] = Query(None, description="Minimum price"),
    max_price: Optional[float] = Query(None, description="Maximum price"),
    min_rating: Optional[float] = Query(4.0, description="Minimum rating"),
    ships_from: Optional[str] = Query(None, description="Shipping region: US, EU, CN"),
    sort: str = Query("trending", description="Sort by: trending, price_asc, price_desc, rating"),
    page: int = Query(1, ge=1),
    limit: int = Query(24, ge=1, le=100),
    # db: Session = Depends(get_db),
):
    """
    Browse curated product catalog

    Returns:
        Paginated list of products available for import
    """
    # query = db.query(ProductCatalog).filter(ProductCatalog.is_available == True)
    #
    # # Apply filters
    # if category:
    #     query = query.filter(ProductCatalog.category == category)
    #
    # if min_price:
    #     query = query.filter(ProductCatalog.cost >= min_price)
    #
    # if max_price:
    #     query = query.filter(ProductCatalog.cost <= max_price)
    #
    # if min_rating:
    #     query = query.filter(ProductCatalog.rating >= min_rating)
    #
    # if ships_from:
    #     query = query.filter(ProductCatalog.ships_from == ships_from)
    #
    # # Sorting
    # if sort == "trending":
    #     query = query.order_by(ProductCatalog.trending_score.desc())
    # elif sort == "price_asc":
    #     query = query.order_by(ProductCatalog.cost.asc())
    # elif sort == "price_desc":
    #     query = query.order_by(ProductCatalog.cost.desc())
    # elif sort == "rating":
    #     query = query.order_by(ProductCatalog.rating.desc())
    #
    # # Pagination
    # total = query.count()
    # products = query.offset((page - 1) * limit).limit(limit).all()

    # Mock data for demonstration
    products = [
        {
            "id": 1,
            "supplier_product_id": "1005001234567890",
            "supplier": "aliexpress",
            "title": "Wireless Bluetooth Earbuds Pro",
            "description": "High-quality wireless earbuds with noise cancellation",
            "category": "Electronics",
            "cost": 12.99,
            "suggested_price": 39.99,
            "rating": 4.8,
            "reviews_count": 2543,
            "orders_count": 15234,
            "images": [
                "https://ae01.alicdn.com/example1.jpg",
                "https://ae01.alicdn.com/example2.jpg",
            ],
            "featured_image": "https://ae01.alicdn.com/example1.jpg",
            "ships_from": "CN",
            "shipping_days_min": 7,
            "shipping_days_max": 14,
            "available_quantity": 5000,
            "import_count": 234,
            "trending_score": 8.5,
            "tags": ["bluetooth", "audio", "wireless"],
        },
        {
            "id": 2,
            "supplier_product_id": "1005009876543210",
            "supplier": "printify",
            "title": "Custom Print T-Shirt - Premium Cotton",
            "description": "High-quality cotton t-shirt with custom printing",
            "category": "Apparel",
            "cost": 8.50,
            "suggested_price": 24.99,
            "rating": 4.9,
            "reviews_count": 1823,
            "orders_count": 8932,
            "images": [
                "https://printify.com/example-tshirt.jpg",
            ],
            "featured_image": "https://printify.com/example-tshirt.jpg",
            "ships_from": "US",
            "shipping_days_min": 3,
            "shipping_days_max": 7,
            "available_quantity": 999999999,  # Unlimited (Printify)
            "import_count": 567,
            "trending_score": 9.2,
            "tags": ["apparel", "custom", "print-on-demand"],
        },
    ]

    return {
        "products": products,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": 2,  # total in production
            "total_pages": 1,
        },
        "filters": {
            "category": category,
            "min_price": min_price,
            "max_price": max_price,
            "ships_from": ships_from,
        },
    }


@router.get("/products/{product_id}")
async def get_product_details(
    product_id: int,
    # db: Session = Depends(get_db),
):
    """
    Get detailed product information

    Args:
        product_id: Catalog product ID

    Returns:
        Full product details with variants, shipping, etc.
    """
    # product = db.query(ProductCatalog).filter(ProductCatalog.id == product_id).first()
    #
    # if not product:
    #     raise HTTPException(status_code=404, detail="Product not found")

    # Mock detailed product
    product = {
        "id": product_id,
        "supplier_product_id": "1005001234567890",
        "supplier": "aliexpress",
        "title": "Wireless Bluetooth Earbuds Pro",
        "description": "Premium wireless earbuds with active noise cancellation...",
        "category": "Electronics",
        "cost": 12.99,
        "suggested_price": 39.99,
        "min_price": 29.99,
        "profit_margin": 67.5,  # (39.99 - 12.99) / 39.99 * 100
        "rating": 4.8,
        "reviews_count": 2543,
        "orders_count": 15234,
        "images": [
            "https://ae01.alicdn.com/example1.jpg",
            "https://ae01.alicdn.com/example2.jpg",
            "https://ae01.alicdn.com/example3.jpg",
        ],
        "featured_image": "https://ae01.alicdn.com/example1.jpg",
        "ships_from": "CN",
        "shipping_days_min": 7,
        "shipping_days_max": 14,
        "shipping_cost": 0,  # Free shipping
        "available_quantity": 5000,
        "import_count": 234,
        "trending_score": 8.5,
        "tags": ["bluetooth", "audio", "wireless", "noise-cancellation"],
        "variants": [
            {"option": "Color", "values": ["Black", "White", "Blue"]},
            {"option": "Size", "values": ["Standard"]},
        ],
        "specifications": {
            "Brand": "Generic",
            "Bluetooth Version": "5.0",
            "Battery Life": "8 hours",
            "Charging Time": "2 hours",
        },
    }

    return product


@router.post("/import")
async def import_product_to_shop(
    shop_domain: str = Query(..., description="Shop domain"),
    product_id: int = Query(..., description="Catalog product ID"),
    markup_percentage: float = Query(40.0, ge=0, le=500),
    # db: Session = Depends(get_db),
):
    """
    One-click import product to shop

    Args:
        shop_domain: Merchant's shop domain
        product_id: Catalog product ID to import
        markup_percentage: Price markup percentage

    Returns:
        Import task details
    """
    # Verify shop exists and is active
    # shop = db.query(Shop).filter(Shop.shop_domain == shop_domain).first()
    # if not shop:
    #     raise HTTPException(status_code=404, detail="Shop not found")
    #
    # if shop.status != ShopStatus.ACTIVE:
    #     raise HTTPException(status_code=403, detail="Shop is not active")
    #
    # # Check plan limits
    # if shop.products_imported >= shop.max_products:
    #     raise HTTPException(
    #         status_code=403,
    #         detail=f"Product limit reached ({shop.max_products}). Upgrade your plan."
    #     )
    #
    # # Get product from catalog
    # catalog_product = db.query(ProductCatalog).filter(
    #     ProductCatalog.id == product_id
    # ).first()
    #
    # if not catalog_product:
    #     raise HTTPException(status_code=404, detail="Product not found in catalog")

    try:
        # Queue import task
        supplier_product_id = "1005001234567890"  # catalog_product.supplier_product_id

        task = import_product_by_id.delay(
            product_id=supplier_product_id,
            markup_percentage=markup_percentage,
        )

        # Track import in database
        # imported_product = ImportedProduct(
        #     shop_id=shop.id,
        #     supplier_product_id=catalog_product.supplier_product_id,
        #     supplier=catalog_product.supplier,
        #     title=catalog_product.title,
        #     price=catalog_product.suggested_price,
        #     cost=catalog_product.cost,
        #     profit_margin=markup_percentage,
        # )
        # db.add(imported_product)
        #
        # shop.products_imported += 1
        # catalog_product.import_count += 1
        #
        # db.commit()

        logger.info(f"Product import queued for shop: {shop_domain}")

        return {
            "status": "queued",
            "task_id": task.id,
            "product_id": product_id,
            "shop": shop_domain,
            "message": "Product import started. You'll be notified when complete.",
        }

    except Exception as e:
        logger.error(f"Failed to import product: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/categories")
async def get_categories(
    # db: Session = Depends(get_db),
):
    """
    Get available product categories

    Returns:
        List of categories with product counts
    """
    # categories = db.query(
    #     ProductCatalog.category,
    #     func.count(ProductCatalog.id)
    # ).group_by(ProductCatalog.category).all()

    # Mock categories
    categories = [
        {"name": "Electronics", "count": 1234},
        {"name": "Apparel", "count": 892},
        {"name": "Home & Garden", "count": 567},
        {"name": "Beauty & Personal Care", "count": 445},
        {"name": "Sports & Outdoors", "count": 334},
        {"name": "Toys & Games", "count": 223},
        {"name": "Pet Supplies", "count": 178},
    ]

    return {"categories": categories}


@router.get("/trending")
async def get_trending_products(
    limit: int = Query(10, ge=1, le=50),
    # db: Session = Depends(get_db),
):
    """
    Get trending products

    Returns:
        Top trending products by score
    """
    # products = db.query(ProductCatalog).filter(
    #     ProductCatalog.is_available == True
    # ).order_by(
    #     ProductCatalog.trending_score.desc()
    # ).limit(limit).all()

    # Mock trending
    products = [
        {
            "id": 1,
            "title": "Wireless Bluetooth Earbuds Pro",
            "cost": 12.99,
            "suggested_price": 39.99,
            "trending_score": 9.5,
            "import_count": 567,
        },
        {
            "id": 2,
            "title": "Smart Watch Fitness Tracker",
            "cost": 15.99,
            "suggested_price": 49.99,
            "trending_score": 9.2,
            "import_count": 445,
        },
    ]

    return {"trending": products}


@router.get("/my-imports")
async def get_my_imports(
    shop_domain: str = Query(...),
    page: int = Query(1, ge=1),
    limit: int = Query(24, ge=1, le=100),
    # db: Session = Depends(get_db),
):
    """
    Get products imported by this shop

    Args:
        shop_domain: Merchant's shop domain
        page: Page number
        limit: Results per page

    Returns:
        Shop's imported products
    """
    # shop = db.query(Shop).filter(Shop.shop_domain == shop_domain).first()
    # if not shop:
    #     raise HTTPException(status_code=404, detail="Shop not found")
    #
    # query = db.query(ImportedProduct).filter(ImportedProduct.shop_id == shop.id)
    #
    # total = query.count()
    # products = query.offset((page - 1) * limit).limit(limit).all()

    # Mock imported products
    products = [
        {
            "id": 1,
            "platform_product_id": "7890123456",
            "supplier_product_id": "1005001234567890",
            "title": "Wireless Bluetooth Earbuds Pro",
            "price": 39.99,
            "cost": 12.99,
            "profit_margin": 67.5,
            "inventory_quantity": 9999,
            "is_active": True,
            "imported_at": "2025-01-15T10:30:00Z",
        }
    ]

    return {
        "products": products,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": 1,
            "total_pages": 1,
        },
    }
