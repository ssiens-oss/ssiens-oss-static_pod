"""
Database models for StaticWaves Maker
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class TokenBalance(Base):
    """User token balance for generation credits"""
    __tablename__ = "token_balances"

    brand_id = Column(Integer, primary_key=True)
    balance = Column(Integer, default=10)  # Free tier starts with 10
    total_earned = Column(Integer, default=0)  # From ads
    total_spent = Column(Integer, default=0)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Subscription(Base):
    """User subscription details"""
    __tablename__ = "subscriptions"

    brand_id = Column(Integer, primary_key=True)
    stripe_customer_id = Column(String, unique=True)
    stripe_subscription_id = Column(String, unique=True)
    tier = Column(String)  # free, creator, studio, pro
    monthly_tokens = Column(Integer)
    status = Column(String, default="active")  # active, canceled, past_due
    current_period_end = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)


class GenerationJob(Base):
    """Generation job tracking"""
    __tablename__ = "generation_jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    brand_id = Column(Integer, nullable=False, index=True)
    type = Column(String, nullable=False)  # image, video, music, book
    prompt = Column(Text, nullable=False)
    status = Column(String, default="queued", index=True)  # queued, processing, completed, failed
    output_url = Column(String)
    output_format = Column(String)  # png, mp4, mp3, pdf, epub
    tokens_used = Column(Integer)
    metadata = Column(Text)  # JSON string for additional data
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    completed_at = Column(DateTime)


class AdReward(Base):
    """Ad reward tracking for rate limiting"""
    __tablename__ = "ad_rewards"

    id = Column(Integer, primary_key=True, autoincrement=True)
    brand_id = Column(Integer, nullable=False, index=True)
    tokens_awarded = Column(Integer, default=5)
    ad_network = Column(String)  # admob, carbon_ads
    rewarded_at = Column(DateTime, default=datetime.utcnow, index=True)


class Library(Base):
    """User's saved creations"""
    __tablename__ = "library"

    id = Column(Integer, primary_key=True, autoincrement=True)
    brand_id = Column(Integer, nullable=False, index=True)
    job_id = Column(Integer, nullable=False)
    title = Column(String)
    favorited = Column(Boolean, default=False)
    downloads = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class UsageStats(Base):
    """Daily usage statistics for analytics"""
    __tablename__ = "usage_stats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    brand_id = Column(Integer, nullable=False, index=True)
    date = Column(DateTime, nullable=False, index=True)
    images_generated = Column(Integer, default=0)
    videos_generated = Column(Integer, default=0)
    music_generated = Column(Integer, default=0)
    books_generated = Column(Integer, default=0)
    tokens_spent = Column(Integer, default=0)
    tokens_earned = Column(Integer, default=0)
