"""
Shopify App API Router
OAuth installation, billing, and app management
"""
from fastapi import APIRouter, Request, HTTPException, Query, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta
from loguru import logger

from services.shopify_app_service import ShopifyAppService
from models.saas import Shop, ShopStatus, PlanTier
from config.settings import settings

router = APIRouter(prefix="/shopify-app", tags=["Shopify App"])

# Dependency for database session (implement your own)
def get_db():
    # This is a placeholder - implement your database session management
    pass


@router.get("/install")
async def install_app(
    shop: str = Query(..., description="Shop domain (mystore.myshopify.com)"),
):
    """
    Start Shopify OAuth installation flow

    Args:
        shop: Shop domain

    Returns:
        Redirect to Shopify authorization page
    """
    if not shop.endswith(".myshopify.com"):
        raise HTTPException(status_code=400, detail="Invalid shop domain")

    app_service = ShopifyAppService()

    # Generate install URL
    install_url = app_service.generate_install_url(shop)

    logger.info(f"Starting installation for shop: {shop}")

    return RedirectResponse(url=install_url)


@router.get("/callback")
async def oauth_callback(
    request: Request,
    shop: str = Query(...),
    code: str = Query(...),
    hmac: str = Query(...),
    state: Optional[str] = Query(None),
    # db: Session = Depends(get_db),
):
    """
    OAuth callback - handle authorization code

    Completes installation by:
    1. Verifying HMAC
    2. Exchanging code for access token
    3. Fetching shop info
    4. Saving shop to database
    5. Registering webhooks
    6. Redirecting to billing (if not free tier)
    """
    app_service = ShopifyAppService()

    # 1. Verify HMAC
    query_params = dict(request.query_params)
    if not app_service.verify_hmac(query_params):
        raise HTTPException(status_code=400, detail="Invalid HMAC signature")

    try:
        # 2. Exchange code for token
        token_data = await app_service.exchange_code_for_token(shop, code)
        access_token = token_data["access_token"]
        scope = token_data["scope"]

        # 3. Fetch shop info
        shop_info = await app_service.get_shop_info(shop, access_token)

        # 4. Save shop to database
        # shop_record = db.query(Shop).filter(Shop.shop_domain == shop).first()
        #
        # if not shop_record:
        #     shop_record = Shop(
        #         shop_domain=shop,
        #         platform="shopify",
        #         platform_id=str(shop_info["id"]),
        #         access_token=access_token,  # Encrypt in production!
        #         scope=scope,
        #         shop_name=shop_info["name"],
        #         shop_email=shop_info["email"],
        #         shop_owner=shop_info["owner"],
        #         currency=shop_info["currency"],
        #         timezone=shop_info["timezone"],
        #         plan_tier=PlanTier.FREE,
        #         status=ShopStatus.TRIAL,
        #         trial_ends_at=datetime.utcnow() + timedelta(days=14),
        #         installed_at=datetime.utcnow(),
        #     )
        #     db.add(shop_record)
        # else:
        #     # Reinstall
        #     shop_record.access_token = access_token
        #     shop_record.scope = scope
        #     shop_record.status = ShopStatus.ACTIVE
        #     shop_record.installed_at = datetime.utcnow()
        #
        # db.commit()

        # 5. Register webhooks
        await app_service.register_webhooks(shop, access_token)

        logger.info(f"✅ Shop {shop} installed successfully")

        # 6. Redirect to app or billing
        # For free tier, redirect to app
        # For paid tiers, redirect to billing

        return RedirectResponse(
            url=f"https://{shop}/admin/apps/{settings.SHOPIFY_API_KEY}"
        )

    except Exception as e:
        logger.error(f"Installation failed for {shop}: {e}")
        raise HTTPException(status_code=500, detail=f"Installation failed: {str(e)}")


@router.get("/billing/create")
async def create_billing_charge(
    shop: str = Query(...),
    plan: str = Query("starter", description="Plan tier: starter, professional, enterprise"),
    # db: Session = Depends(get_db),
):
    """
    Create recurring billing charge

    Args:
        shop: Shop domain
        plan: Plan tier to subscribe to

    Returns:
        Redirect to Shopify billing confirmation page
    """
    # shop_record = db.query(Shop).filter(Shop.shop_domain == shop).first()
    # if not shop_record:
    #     raise HTTPException(status_code=404, detail="Shop not found")

    # Plan pricing (example)
    plan_pricing = {
        "starter": {"name": "Starter Plan", "price": 29.99},
        "professional": {"name": "Professional Plan", "price": 79.99},
        "enterprise": {"name": "Enterprise Plan", "price": 199.99},
    }

    if plan not in plan_pricing:
        raise HTTPException(status_code=400, detail="Invalid plan")

    app_service = ShopifyAppService()

    try:
        # Create recurring charge
        access_token = "placeholder"  # shop_record.access_token
        plan_info = plan_pricing[plan]

        charge_result = await app_service.create_recurring_charge(
            shop=shop,
            access_token=access_token,
            plan_name=plan_info["name"],
            price=plan_info["price"],
        )

        # Save charge ID to database
        # shop_record.billing_charge_id = charge_result["id"]
        # shop_record.plan_tier = PlanTier(plan)
        # db.commit()

        logger.info(f"Created billing charge for {shop}: {plan}")

        # Redirect to confirmation URL
        return RedirectResponse(url=charge_result["confirmation_url"])

    except Exception as e:
        logger.error(f"Failed to create billing charge: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/billing/confirm")
async def confirm_billing_charge(
    request: Request,
    charge_id: str = Query(...),
    # db: Session = Depends(get_db),
):
    """
    Confirm recurring charge after merchant approval

    Args:
        charge_id: Charge ID from Shopify

    Returns:
        Redirect to app dashboard
    """
    # Find shop by charge ID
    # shop_record = db.query(Shop).filter(Shop.billing_charge_id == charge_id).first()
    # if not shop_record:
    #     raise HTTPException(status_code=404, detail="Charge not found")

    app_service = ShopifyAppService()
    shop = "placeholder.myshopify.com"  # shop_record.shop_domain
    access_token = "placeholder"  # shop_record.access_token

    try:
        # Activate charge
        activated = await app_service.activate_recurring_charge(
            shop=shop,
            access_token=access_token,
            charge_id=charge_id,
        )

        if activated:
            # Update shop status
            # shop_record.status = ShopStatus.ACTIVE
            # shop_record.billing_confirmed_at = datetime.utcnow()
            # db.commit()

            logger.info(f"✅ Billing activated for {shop}")

            # Redirect to app
            return RedirectResponse(
                url=f"https://{shop}/admin/apps/{settings.SHOPIFY_API_KEY}"
            )
        else:
            raise HTTPException(status_code=400, detail="Charge not accepted")

    except Exception as e:
        logger.error(f"Failed to activate charge: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/app-proxy")
async def app_proxy(request: Request):
    """
    Shopify App Proxy endpoint

    Serves content to storefront via App Proxy
    """
    # Verify app proxy signature
    # Serve custom storefront content

    return HTMLResponse(content="""
        <div class="dropcommerce-widget">
            <h2>Browse Products</h2>
            <p>Explore our curated product catalog</p>
        </div>
    """)


@router.get("/embedded")
async def embedded_app(
    shop: str = Query(...),
    # db: Session = Depends(get_db),
):
    """
    Serve embedded app UI

    This is the main app interface within Shopify admin
    """
    # shop_record = db.query(Shop).filter(Shop.shop_domain == shop).first()
    # if not shop_record:
    #     return HTMLResponse(
    #         content="<h1>Shop not found. Please install the app.</h1>",
    #         status_code=404,
    #     )

    # Serve React app or redirect to frontend
    return HTMLResponse(content=f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>DropCommerce Alternative</title>
        <script src="https://cdn.shopify.com/shopifycloud/app-bridge.js"></script>
    </head>
    <body>
        <div id="root">
            <h1>Welcome to Your Dropshipping App</h1>
            <p>Loading...</p>
        </div>

        <script>
            var AppBridge = window['app-bridge'];
            var createApp = AppBridge.default;

            var app = createApp({{
                apiKey: '{settings.SHOPIFY_API_KEY}',
                host: new URLSearchParams(window.location.search).get('host'),
                forceRedirect: true
            }});

            console.log('App Bridge initialized for shop: {shop}');

            // Load your React app here
            // or redirect to your frontend application
        </script>
    </body>
    </html>
    """)


@router.post("/uninstall")
async def handle_uninstall(
    request: Request,
    # db: Session = Depends(get_db),
):
    """
    Handle app uninstallation webhook

    Called when merchant uninstalls the app
    """
    data = await request.json()
    shop_domain = data.get("domain")

    if not shop_domain:
        raise HTTPException(status_code=400, detail="Missing shop domain")

    # shop_record = db.query(Shop).filter(Shop.shop_domain == shop_domain).first()
    # if shop_record:
    #     shop_record.status = ShopStatus.UNINSTALLED
    #     shop_record.uninstalled_at = datetime.utcnow()
    #     db.commit()

    logger.info(f"App uninstalled by shop: {shop_domain}")

    return {"status": "uninstalled"}


@router.get("/plans")
async def get_available_plans():
    """
    Get available subscription plans

    Returns:
        List of plans with features and pricing
    """
    plans = [
        {
            "tier": "free",
            "name": "Free",
            "price": 0,
            "features": {
                "max_products": 25,
                "max_orders_per_month": 100,
                "auto_fulfillment": False,
                "analytics": False,
                "support": "community",
            },
        },
        {
            "tier": "starter",
            "name": "Starter",
            "price": 29.99,
            "trial_days": 14,
            "features": {
                "max_products": 500,
                "max_orders_per_month": 1000,
                "auto_fulfillment": True,
                "analytics": True,
                "support": "email",
            },
        },
        {
            "tier": "professional",
            "name": "Professional",
            "price": 79.99,
            "features": {
                "max_products": -1,  # Unlimited
                "max_orders_per_month": -1,
                "auto_fulfillment": True,
                "analytics": True,
                "priority_fulfillment": True,
                "support": "priority",
            },
        },
        {
            "tier": "enterprise",
            "name": "Enterprise",
            "price": 199.99,
            "features": {
                "max_products": -1,
                "max_orders_per_month": -1,
                "auto_fulfillment": True,
                "analytics": True,
                "priority_fulfillment": True,
                "dedicated_account_manager": True,
                "custom_integrations": True,
                "support": "24/7",
            },
        },
    ]

    return {"plans": plans}
