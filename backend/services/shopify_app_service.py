"""
Shopify App Service
OAuth installation, billing, and app management
"""
import hmac
import hashlib
import secrets
from typing import Dict, Any, Optional
from urllib.parse import urlencode, parse_qs
from loguru import logger
import shopify

from config.settings import settings


class ShopifyAppService:
    """Service for Shopify App OAuth and management"""

    # Scopes required by the app
    SCOPES = [
        "read_products",
        "write_products",
        "read_orders",
        "write_orders",
        "read_inventory",
        "write_inventory",
        "read_fulfillments",
        "write_fulfillments",
        "read_shipping",
        "write_shipping",
    ]

    # App URLs
    APP_URL = settings.APP_URL if hasattr(settings, 'APP_URL') else "https://your-app.com"
    REDIRECT_URI = f"{APP_URL}/api/shopify-app/callback"

    def __init__(self):
        self.api_key = settings.SHOPIFY_API_KEY
        self.api_secret = settings.SHOPIFY_API_SECRET

    def generate_install_url(self, shop: str, state: Optional[str] = None) -> str:
        """
        Generate Shopify OAuth installation URL

        Args:
            shop: Shop domain (mystore.myshopify.com)
            state: CSRF protection token

        Returns:
            Installation URL to redirect merchant to
        """
        if not state:
            state = secrets.token_urlsafe(32)

        params = {
            "client_id": self.api_key,
            "scope": ",".join(self.SCOPES),
            "redirect_uri": self.REDIRECT_URI,
            "state": state,
        }

        url = f"https://{shop}/admin/oauth/authorize?{urlencode(params)}"

        logger.info(f"Generated install URL for shop: {shop}")
        return url

    def verify_hmac(self, params: Dict[str, str]) -> bool:
        """
        Verify HMAC signature from Shopify

        Args:
            params: Query parameters from Shopify callback

        Returns:
            True if signature is valid
        """
        hmac_to_verify = params.get("hmac")
        if not hmac_to_verify:
            return False

        # Remove hmac from params
        params_without_hmac = {k: v for k, v in params.items() if k != "hmac"}

        # Sort and encode
        encoded_params = urlencode(sorted(params_without_hmac.items()))

        # Calculate HMAC
        calculated_hmac = hmac.new(
            self.api_secret.encode("utf-8"),
            encoded_params.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        return hmac.compare_digest(calculated_hmac, hmac_to_verify)

    async def exchange_code_for_token(
        self, shop: str, code: str
    ) -> Dict[str, Any]:
        """
        Exchange authorization code for permanent access token

        Args:
            shop: Shop domain
            code: Temporary authorization code

        Returns:
            Token data including access_token and scope
        """
        session = shopify.Session(shop, settings.SHOPIFY_API_VERSION)

        try:
            token = session.request_token({
                "code": code,
                "client_id": self.api_key,
                "client_secret": self.api_secret,
            })

            logger.info(f"✅ Obtained access token for shop: {shop}")

            return {
                "access_token": token,
                "scope": session.scope,
                "shop": shop,
            }

        except Exception as e:
            logger.error(f"Failed to exchange code for token: {e}")
            raise

    async def get_shop_info(self, shop: str, access_token: str) -> Dict[str, Any]:
        """
        Fetch shop information from Shopify

        Args:
            shop: Shop domain
            access_token: Shop's access token

        Returns:
            Shop details (name, email, currency, etc.)
        """
        session = shopify.Session(shop, settings.SHOPIFY_API_VERSION, access_token)
        shopify.ShopifyResource.activate_session(session)

        try:
            shop_data = shopify.Shop.current()

            info = {
                "id": shop_data.id,
                "name": shop_data.name,
                "email": shop_data.email,
                "owner": shop_data.shop_owner,
                "domain": shop_data.domain,
                "currency": shop_data.currency,
                "timezone": shop_data.iana_timezone,
                "plan_name": shop_data.plan_name,
                "country": shop_data.country,
            }

            logger.info(f"Fetched info for shop: {shop_data.name}")
            return info

        except Exception as e:
            logger.error(f"Failed to fetch shop info: {e}")
            raise
        finally:
            shopify.ShopifyResource.clear_session()

    async def create_recurring_charge(
        self, shop: str, access_token: str, plan_name: str, price: float
    ) -> Dict[str, Any]:
        """
        Create recurring application charge (subscription)

        Args:
            shop: Shop domain
            access_token: Shop's access token
            plan_name: Plan name ("Starter", "Professional", etc.)
            price: Monthly price

        Returns:
            Charge details with confirmation URL
        """
        session = shopify.Session(shop, settings.SHOPIFY_API_VERSION, access_token)
        shopify.ShopifyResource.activate_session(session)

        try:
            charge = shopify.RecurringApplicationCharge()
            charge.name = plan_name
            charge.price = price
            charge.return_url = f"{self.APP_URL}/api/shopify-app/billing/confirm"
            charge.test = settings.DEBUG  # Test mode in development

            # Optional trial
            if plan_name == "Starter":
                charge.trial_days = 14

            success = charge.save()

            if not success:
                raise Exception(f"Failed to create charge: {charge.errors.full_messages()}")

            logger.info(f"Created recurring charge for {shop}: ${price}/month")

            return {
                "id": charge.id,
                "confirmation_url": charge.confirmation_url,
                "status": charge.status,
            }

        except Exception as e:
            logger.error(f"Failed to create recurring charge: {e}")
            raise
        finally:
            shopify.ShopifyResource.clear_session()

    async def activate_recurring_charge(
        self, shop: str, access_token: str, charge_id: str
    ) -> bool:
        """
        Activate recurring charge after merchant confirmation

        Args:
            shop: Shop domain
            access_token: Shop's access token
            charge_id: Charge ID to activate

        Returns:
            True if activated successfully
        """
        session = shopify.Session(shop, settings.SHOPIFY_API_VERSION, access_token)
        shopify.ShopifyResource.activate_session(session)

        try:
            charge = shopify.RecurringApplicationCharge.find(charge_id)

            if charge.status == "accepted":
                charge.activate()
                logger.info(f"✅ Activated recurring charge {charge_id} for {shop}")
                return True
            else:
                logger.warning(f"Charge {charge_id} not accepted: {charge.status}")
                return False

        except Exception as e:
            logger.error(f"Failed to activate charge: {e}")
            raise
        finally:
            shopify.ShopifyResource.clear_session()

    async def cancel_recurring_charge(
        self, shop: str, access_token: str, charge_id: str
    ):
        """
        Cancel recurring charge (unsubscribe)

        Args:
            shop: Shop domain
            access_token: Shop's access token
            charge_id: Charge ID to cancel
        """
        session = shopify.Session(shop, settings.SHOPIFY_API_VERSION, access_token)
        shopify.ShopifyResource.activate_session(session)

        try:
            charge = shopify.RecurringApplicationCharge.find(charge_id)
            charge.destroy()

            logger.info(f"Cancelled recurring charge {charge_id} for {shop}")

        except Exception as e:
            logger.error(f"Failed to cancel charge: {e}")
            raise
        finally:
            shopify.ShopifyResource.clear_session()

    async def register_webhooks(
        self, shop: str, access_token: str
    ) -> Dict[str, Any]:
        """
        Register required webhooks for the app

        Args:
            shop: Shop domain
            access_token: Shop's access token

        Returns:
            Webhook registration results
        """
        session = shopify.Session(shop, settings.SHOPIFY_API_VERSION, access_token)
        shopify.ShopifyResource.activate_session(session)

        webhooks_to_create = [
            {
                "topic": "app/uninstalled",
                "address": f"{self.APP_URL}/api/webhooks/shopify/app/uninstalled",
                "format": "json",
            },
            {
                "topic": "orders/create",
                "address": f"{self.APP_URL}/api/webhooks/shopify/orders/create",
                "format": "json",
            },
            {
                "topic": "products/update",
                "address": f"{self.APP_URL}/api/webhooks/shopify/products/update",
                "format": "json",
            },
            {
                "topic": "shop/update",
                "address": f"{self.APP_URL}/api/webhooks/shopify/shop/update",
                "format": "json",
            },
        ]

        results = []

        try:
            for webhook_config in webhooks_to_create:
                webhook = shopify.Webhook()
                webhook.topic = webhook_config["topic"]
                webhook.address = webhook_config["address"]
                webhook.format = webhook_config["format"]

                success = webhook.save()

                if success:
                    logger.info(f"✅ Registered webhook: {webhook.topic}")
                    results.append({"topic": webhook.topic, "status": "success"})
                else:
                    logger.error(f"Failed to register webhook: {webhook.errors.full_messages()}")
                    results.append({"topic": webhook.topic, "status": "failed"})

            return {"webhooks": results}

        except Exception as e:
            logger.error(f"Failed to register webhooks: {e}")
            raise
        finally:
            shopify.ShopifyResource.clear_session()

    async def uninstall_app(self, shop: str):
        """
        Handle app uninstallation

        Args:
            shop: Shop domain that uninstalled the app
        """
        logger.info(f"App uninstalled by shop: {shop}")

        # Mark shop as uninstalled in database
        # Cancel any active charges
        # Clean up resources

        # This is handled in the webhook handler
