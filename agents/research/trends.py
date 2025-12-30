#!/usr/bin/env python3
"""
Trend Research Agent
Analyzes market trends using various data sources
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime, timedelta
import json
import re
from collections import Counter

from agents.core.agent import DataCollectorAgent

logger = logging.getLogger(__name__)


class TrendAnalysisAgent(DataCollectorAgent):
    """
    Analyze trends from collected data
    Aggregates data from browser agents and identifies patterns
    """

    async def execute(self) -> Dict[str, Any]:
        """Analyze trends from collected data"""
        logger.info("Starting trend analysis...")

        # Load data from browser agents
        marketplace_data = self.load_marketplace_data()

        # Analyze trends
        trends = {
            "keywords": self.extract_trending_keywords(marketplace_data),
            "price_ranges": self.analyze_price_ranges(marketplace_data),
            "top_products": self.identify_top_products(marketplace_data),
            "timestamp": datetime.utcnow().isoformat()
        }

        # Save analysis
        self.save_data(trends, "trend_analysis.json")

        return trends

    def load_marketplace_data(self) -> List[Dict[str, Any]]:
        """Load marketplace data from recent scrapes"""
        all_data = []

        # Look for recent marketplace data files
        for data_file in self.output_dir.glob("*_*.json"):
            try:
                with open(data_file) as f:
                    data = json.load(f)

                    # Only include recent data (last 7 days)
                    if "timestamp" in data:
                        timestamp = datetime.fromisoformat(data["timestamp"])
                        if datetime.utcnow() - timestamp < timedelta(days=7):
                            all_data.append(data)
            except Exception as e:
                logger.warning(f"Failed to load {data_file}: {e}")

        return all_data

    def extract_trending_keywords(self, marketplace_data: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Extract trending keywords from product titles

        Args:
            marketplace_data: List of marketplace data

        Returns:
            dict: Keyword frequency map
        """
        all_words = []

        for data in marketplace_data:
            products = data.get("products", [])

            for product in products:
                title = product.get("title", "")

                # Extract words (remove common words)
                words = re.findall(r'\b\w+\b', title.lower())

                # Filter stopwords
                stopwords = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for"}
                words = [w for w in words if w not in stopwords and len(w) > 3]

                all_words.extend(words)

        # Count frequency
        word_counts = Counter(all_words)

        # Return top 20 keywords
        return dict(word_counts.most_common(20))

    def analyze_price_ranges(self, marketplace_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze price distribution

        Args:
            marketplace_data: List of marketplace data

        Returns:
            dict: Price statistics
        """
        all_prices = []

        for data in marketplace_data:
            products = data.get("products", [])

            for product in products:
                price_str = product.get("price", "")

                # Extract numeric price
                price_match = re.search(r'[\d.]+', price_str)
                if price_match:
                    try:
                        price = float(price_match.group())
                        all_prices.append(price)
                    except ValueError:
                        pass

        if not all_prices:
            return {}

        all_prices.sort()

        return {
            "count": len(all_prices),
            "min": min(all_prices),
            "max": max(all_prices),
            "average": sum(all_prices) / len(all_prices),
            "median": all_prices[len(all_prices) // 2],
            "price_tiers": {
                "budget": [p for p in all_prices if p < 20],
                "mid_range": [p for p in all_prices if 20 <= p < 50],
                "premium": [p for p in all_prices if p >= 50]
            }
        }

    def identify_top_products(self, marketplace_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Identify top-performing products

        Args:
            marketplace_data: List of marketplace data

        Returns:
            list: Top products
        """
        top_products = []

        for data in marketplace_data:
            products = data.get("products", [])[:5]  # Top 5 from each marketplace
            marketplace = data.get("marketplace", "unknown")

            for product in products:
                product["marketplace"] = marketplace
                top_products.append(product)

        return top_products


class OpportunityFinderAgent(DataCollectorAgent):
    """
    Identify market opportunities and gaps
    """

    async def execute(self) -> Dict[str, Any]:
        """Find market opportunities"""
        logger.info("Searching for market opportunities...")

        # Load trend analysis
        try:
            trends = self.load_data("trend_analysis.json")
        except FileNotFoundError:
            logger.warning("No trend analysis found. Run TrendAnalysisAgent first.")
            return {"opportunities": []}

        opportunities = []

        # Analyze keyword trends
        keywords = trends.get("keywords", {})

        # Find trending but underserved keywords
        for keyword, count in keywords.items():
            if 5 <= count <= 15:  # Sweet spot: popular but not saturated
                opportunities.append({
                    "type": "keyword",
                    "keyword": keyword,
                    "frequency": count,
                    "confidence": "medium"
                })

        # Analyze price gaps
        price_ranges = trends.get("price_ranges", {})
        price_tiers = price_ranges.get("price_tiers", {})

        # If budget tier is underrepresented
        if len(price_tiers.get("budget", [])) < len(price_tiers.get("premium", [])):
            opportunities.append({
                "type": "price_gap",
                "gap": "budget",
                "recommendation": "Create affordable products under $20",
                "confidence": "high"
            })

        data = {
            "opportunities_found": len(opportunities),
            "timestamp": datetime.utcnow().isoformat(),
            "opportunities": opportunities
        }

        self.save_data(data, "opportunities.json")

        return data


class SeasonalTrendsAgent(DataCollectorAgent):
    """
    Track seasonal trends and predict upcoming demand
    """

    async def execute(self) -> Dict[str, Any]:
        """Analyze seasonal trends"""
        logger.info("Analyzing seasonal trends...")

        current_month = datetime.utcnow().month
        current_season = self.get_season(current_month)

        # Predict upcoming trends based on season
        upcoming_trends = self.predict_seasonal_trends(current_season)

        data = {
            "current_season": current_season,
            "month": current_month,
            "upcoming_trends": upcoming_trends,
            "timestamp": datetime.utcnow().isoformat()
        }

        self.save_data(data, "seasonal_trends.json")

        return data

    def get_season(self, month: int) -> str:
        """Get season from month"""
        if month in [12, 1, 2]:
            return "winter"
        elif month in [3, 4, 5]:
            return "spring"
        elif month in [6, 7, 8]:
            return "summer"
        else:
            return "fall"

    def predict_seasonal_trends(self, season: str) -> List[Dict[str, Any]]:
        """
        Predict trends for upcoming season

        Args:
            season: Current season

        Returns:
            list: Predicted trends
        """
        seasonal_keywords = {
            "winter": [
                {"keyword": "cozy", "confidence": 0.9},
                {"keyword": "warm", "confidence": 0.85},
                {"keyword": "holiday", "confidence": 0.8},
                {"keyword": "snow", "confidence": 0.75}
            ],
            "spring": [
                {"keyword": "floral", "confidence": 0.9},
                {"keyword": "pastel", "confidence": 0.85},
                {"keyword": "fresh", "confidence": 0.8},
                {"keyword": "garden", "confidence": 0.75}
            ],
            "summer": [
                {"keyword": "beach", "confidence": 0.9},
                {"keyword": "tropical", "confidence": 0.85},
                {"keyword": "vibrant", "confidence": 0.8},
                {"keyword": "ocean", "confidence": 0.75}
            ],
            "fall": [
                {"keyword": "autumn", "confidence": 0.9},
                {"keyword": "pumpkin", "confidence": 0.85},
                {"keyword": "cozy", "confidence": 0.8},
                {"keyword": "leaves", "confidence": 0.75}
            ]
        }

        return seasonal_keywords.get(season, [])
