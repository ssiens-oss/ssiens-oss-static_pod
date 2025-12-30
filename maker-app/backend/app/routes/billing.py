"""
Billing routes - Stripe subscriptions and token purchases
"""

import os
import stripe
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timedelta

from app.database import get_db
from app.deps import get_current_user
from app.models import Subscription, TokenBalance

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

router = APIRouter(prefix="/billing", tags=["billing"])

# Subscription tiers
TIERS = {
    "creator": {
        "price_id": os.getenv("STRIPE_PRICE_CREATOR"),
        "monthly_tokens": 300,
        "price": 19
    },
    "studio": {
        "price_id": os.getenv("STRIPE_PRICE_STUDIO"),
        "monthly_tokens": 800,
        "price": 49
    },
    "pro": {
        "price_id": os.getenv("STRIPE_PRICE_PRO"),
        "monthly_tokens": 2000,
        "price": 99
    }
}

# Token packs (one-time purchases)
TOKEN_PACKS = {
    "small": {"tokens": 100, "price": 10, "price_id": os.getenv("STRIPE_PRICE_TOKENS_100")},
    "medium": {"tokens": 300, "price": 25, "price_id": os.getenv("STRIPE_PRICE_TOKENS_300")},
    "large": {"tokens": 1000, "price": 75, "price_id": os.getenv("STRIPE_PRICE_TOKENS_1000")}
}


class CreateSubscriptionRequest(BaseModel):
    tier: str  # creator, studio, pro


class BuyTokensRequest(BaseModel):
    pack: str  # small, medium, large


@router.post("/subscribe")
async def create_subscription(
    req: CreateSubscriptionRequest,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create or update user subscription"""
    if req.tier not in TIERS:
        raise HTTPException(status_code=400, detail="Invalid tier")

    tier_config = TIERS[req.tier]
    brand_id = user["brand_id"]

    # Get or create Stripe customer
    sub = db.query(Subscription).filter_by(brand_id=brand_id).first()

    if not sub or not sub.stripe_customer_id:
        # Create new customer
        customer = stripe.Customer.create(
            metadata={"brand_id": brand_id}
        )
        customer_id = customer.id
    else:
        customer_id = sub.stripe_customer_id

    # Create checkout session
    checkout_session = stripe.checkout.Session.create(
        customer=customer_id,
        payment_method_types=["card"],
        line_items=[{
            "price": tier_config["price_id"],
            "quantity": 1
        }],
        mode="subscription",
        success_url=os.getenv("FRONTEND_URL") + "/success?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=os.getenv("FRONTEND_URL") + "/pricing",
        metadata={
            "brand_id": brand_id,
            "tier": req.tier
        }
    )

    return {
        "checkout_url": checkout_session.url,
        "session_id": checkout_session.id
    }


@router.post("/buy-tokens")
async def buy_tokens(
    req: BuyTokensRequest,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """One-time token pack purchase"""
    if req.pack not in TOKEN_PACKS:
        raise HTTPException(status_code=400, detail="Invalid pack")

    pack = TOKEN_PACKS[req.pack]

    # Create checkout session
    checkout_session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price": pack["price_id"],
            "quantity": 1
        }],
        mode="payment",
        success_url=os.getenv("FRONTEND_URL") + "/success?tokens=" + str(pack["tokens"]),
        cancel_url=os.getenv("FRONTEND_URL") + "/tokens",
        metadata={
            "brand_id": user["brand_id"],
            "tokens": pack["tokens"]
        }
    )

    return {
        "checkout_url": checkout_session.url,
        "session_id": checkout_session.id
    }


@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Stripe webhook events"""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Handle subscription events
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        brand_id = int(session["metadata"]["brand_id"])

        if session["mode"] == "subscription":
            # Handle subscription checkout
            subscription_id = session["subscription"]
            tier = session["metadata"]["tier"]

            # Get subscription details
            subscription = stripe.Subscription.retrieve(subscription_id)

            # Update database
            sub = db.query(Subscription).filter_by(brand_id=brand_id).first()
            if not sub:
                sub = Subscription(brand_id=brand_id)
                db.add(sub)

            sub.stripe_customer_id = session["customer"]
            sub.stripe_subscription_id = subscription_id
            sub.tier = tier
            sub.monthly_tokens = TIERS[tier]["monthly_tokens"]
            sub.status = "active"
            sub.current_period_end = datetime.fromtimestamp(subscription["current_period_end"])

            # Grant initial tokens
            balance = db.query(TokenBalance).filter_by(brand_id=brand_id).first()
            if not balance:
                balance = TokenBalance(brand_id=brand_id)
                db.add(balance)

            balance.balance += TIERS[tier]["monthly_tokens"]

            db.commit()

        elif session["mode"] == "payment":
            # Handle token pack purchase
            tokens = int(session["metadata"]["tokens"])

            balance = db.query(TokenBalance).filter_by(brand_id=brand_id).first()
            if not balance:
                balance = TokenBalance(brand_id=brand_id)
                db.add(balance)

            balance.balance += tokens
            db.commit()

    elif event["type"] == "invoice.paid":
        # Monthly subscription renewal
        invoice = event["data"]["object"]
        subscription_id = invoice["subscription"]

        sub = db.query(Subscription).filter_by(
            stripe_subscription_id=subscription_id
        ).first()

        if sub:
            # Refill monthly tokens
            balance = db.query(TokenBalance).filter_by(brand_id=sub.brand_id).first()
            if not balance:
                balance = TokenBalance(brand_id=sub.brand_id)
                db.add(balance)

            balance.balance += sub.monthly_tokens
            db.commit()

    elif event["type"] == "customer.subscription.deleted":
        # Subscription canceled
        subscription = event["data"]["object"]
        subscription_id = subscription["id"]

        sub = db.query(Subscription).filter_by(
            stripe_subscription_id=subscription_id
        ).first()

        if sub:
            sub.status = "canceled"
            db.commit()

    return {"status": "success"}


@router.get("/subscription")
async def get_subscription(
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's current subscription"""
    sub = db.query(Subscription).filter_by(brand_id=user["brand_id"]).first()

    if not sub:
        return {
            "tier": "free",
            "status": "active",
            "monthly_tokens": 0
        }

    return {
        "tier": sub.tier,
        "status": sub.status,
        "monthly_tokens": sub.monthly_tokens,
        "current_period_end": sub.current_period_end.isoformat() if sub.current_period_end else None
    }


@router.post("/cancel-subscription")
async def cancel_subscription(
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel user's subscription"""
    sub = db.query(Subscription).filter_by(brand_id=user["brand_id"]).first()

    if not sub or not sub.stripe_subscription_id:
        raise HTTPException(status_code=404, detail="No active subscription")

    # Cancel at period end (don't delete immediately)
    stripe.Subscription.modify(
        sub.stripe_subscription_id,
        cancel_at_period_end=True
    )

    return {"status": "Subscription will cancel at period end"}
