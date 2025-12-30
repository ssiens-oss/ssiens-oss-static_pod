"""
Rewards routes - AdMob rewarded ads and token balance
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.deps import get_current_user, reward_ad_tokens, get_token_balance

router = APIRouter(prefix="/rewards", tags=["rewards"])


class AdCompleteRequest(BaseModel):
    ad_network: str = "admob"  # admob, carbon_ads
    ad_unit_id: str


@router.post("/ad-complete")
async def ad_complete(
    req: AdCompleteRequest,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Called when user completes watching a rewarded ad
    Awards tokens with daily rate limiting
    """
    result = reward_ad_tokens(db, user["brand_id"])

    return {
        "success": True,
        **result
    }


@router.get("/balance")
async def get_balance(
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's token balance and stats"""
    balance = get_token_balance(db, user["brand_id"])

    return {
        "balance": balance.balance,
        "total_earned": balance.total_earned,
        "total_spent": balance.total_spent,
        "last_updated": balance.last_updated.isoformat()
    }


@router.get("/ad-availability")
async def check_ad_availability(
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check if user can watch more ads today"""
    from datetime import datetime
    from app.models import AdReward
    from app.deps import MAX_AD_REWARDS_PER_DAY

    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_count = db.query(AdReward).filter(
        AdReward.brand_id == user["brand_id"],
        AdReward.rewarded_at >= today_start
    ).count()

    return {
        "available": today_count < MAX_AD_REWARDS_PER_DAY,
        "watched_today": today_count,
        "limit": MAX_AD_REWARDS_PER_DAY,
        "remaining": max(0, MAX_AD_REWARDS_PER_DAY - today_count)
    }
