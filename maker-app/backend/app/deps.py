"""
Dependencies for token enforcement, authentication, and rate limiting
"""

import os
from fastapi import Depends, HTTPException, Header
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.database import get_db
from app.models import TokenBalance, AdReward, UsageStats

# Token costs for each generation type
TOKEN_COST = {
    "image": 1,
    "music": 2,
    "video": 5,
    "book": 15
}

# Ad reward limits
MAX_AD_REWARDS_PER_DAY = 10
AD_REWARD_TOKENS = 5


def get_current_user(authorization: str = Header(...)):
    """
    Extract user from Authorization header
    In production, validate JWT token here
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Mock user extraction - replace with real JWT decode
    token = authorization.replace("Bearer ", "")

    # For demo: extract brand_id from token (in production use JWT)
    # Example: "brand_123" -> brand_id = 123
    if not token.startswith("brand_"):
        raise HTTPException(status_code=401, detail="Invalid token")

    brand_id = int(token.replace("brand_", ""))

    return {"brand_id": brand_id, "token": token}


def charge_tokens(db: Session, brand_id: int, cost: int) -> TokenBalance:
    """
    Deduct tokens from user balance
    Raises HTTPException if insufficient tokens
    """
    balance = db.query(TokenBalance).filter_by(brand_id=brand_id).first()

    if not balance:
        # Create new balance for first-time users
        balance = TokenBalance(brand_id=brand_id, balance=10)  # Free tier
        db.add(balance)
        db.commit()
        db.refresh(balance)

    if balance.balance < cost:
        raise HTTPException(
            status_code=402,
            detail={
                "error": "Insufficient tokens",
                "required": cost,
                "available": balance.balance,
                "message": "Upgrade or watch an ad to earn more tokens"
            }
        )

    balance.balance -= cost
    balance.total_spent += cost
    db.commit()
    db.refresh(balance)

    return balance


def reward_ad_tokens(db: Session, brand_id: int) -> dict:
    """
    Reward tokens for watching an ad
    Rate-limited to MAX_AD_REWARDS_PER_DAY per day
    """
    # Check daily limit
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_rewards = db.query(AdReward).filter(
        AdReward.brand_id == brand_id,
        AdReward.rewarded_at >= today_start
    ).count()

    if today_rewards >= MAX_AD_REWARDS_PER_DAY:
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Daily ad reward limit reached",
                "limit": MAX_AD_REWARDS_PER_DAY,
                "message": "Upgrade to unlimited tokens"
            }
        )

    # Reward tokens
    balance = db.query(TokenBalance).filter_by(brand_id=brand_id).first()
    if not balance:
        balance = TokenBalance(brand_id=brand_id)
        db.add(balance)

    balance.balance += AD_REWARD_TOKENS
    balance.total_earned += AD_REWARD_TOKENS

    # Track reward
    reward = AdReward(brand_id=brand_id, tokens_awarded=AD_REWARD_TOKENS)
    db.add(reward)

    db.commit()

    return {
        "tokens_awarded": AD_REWARD_TOKENS,
        "new_balance": balance.balance,
        "rewards_today": today_rewards + 1,
        "rewards_remaining": MAX_AD_REWARDS_PER_DAY - (today_rewards + 1)
    }


def track_usage(db: Session, brand_id: int, job_type: str, tokens_spent: int):
    """Track daily usage statistics"""
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    stats = db.query(UsageStats).filter(
        UsageStats.brand_id == brand_id,
        UsageStats.date == today
    ).first()

    if not stats:
        stats = UsageStats(brand_id=brand_id, date=today)
        db.add(stats)

    # Increment counters
    if job_type == "image":
        stats.images_generated += 1
    elif job_type == "video":
        stats.videos_generated += 1
    elif job_type == "music":
        stats.music_generated += 1
    elif job_type == "book":
        stats.books_generated += 1

    stats.tokens_spent += tokens_spent

    db.commit()


def get_token_balance(db: Session, brand_id: int) -> TokenBalance:
    """Get or create token balance for user"""
    balance = db.query(TokenBalance).filter_by(brand_id=brand_id).first()

    if not balance:
        balance = TokenBalance(brand_id=brand_id)
        db.add(balance)
        db.commit()
        db.refresh(balance)

    return balance
