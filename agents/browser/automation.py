#!/usr/bin/env python3
"""
Browser Automation Agent
Uses Playwright for web scraping, monitoring, and automation
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
import json

try:
    from playwright.async_api import async_playwright, Browser, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logging.warning("Playwright not installed. Install with: pip install playwright && playwright install")

from agents.core.agent import DataCollectorAgent

logger = logging.getLogger(__name__)


class BrowserAgent(DataCollectorAgent):
    """Base browser automation agent using Playwright"""

    def __init__(self, name: str, output_dir: Path, config: Optional[Dict[str, Any]] = None):
        super().__init__(name, output_dir, config)
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.headless = config.get("headless", True) if config else True

    async def start_browser(self):
        """Start browser instance"""
        if not PLAYWRIGHT_AVAILABLE:
            raise RuntimeError("Playwright not available")

        playwright = await async_playwright().start()

        # Choose browser type
        browser_type = self.config.get("browser", "chromium")

        if browser_type == "chromium":
            self.browser = await playwright.chromium.launch(headless=self.headless)
        elif browser_type == "firefox":
            self.browser = await playwright.firefox.launch(headless=self.headless)
        elif browser_type == "webkit":
            self.browser = await playwright.webkit.launch(headless=self.headless)

        # Create new page
        self.page = await self.browser.new_page()

        logger.info(f"Browser started ({browser_type}, headless={self.headless})")

    async def close_browser(self):
        """Close browser instance"""
        if self.browser:
            await self.browser.close()
            self.browser = None
            self.page = None
            logger.info("Browser closed")

    async def navigate(self, url: str, wait_for: str = "load"):
        """
        Navigate to URL

        Args:
            url: URL to navigate to
            wait_for: Wait condition (load, domcontentloaded, networkidle)
        """
        if not self.page:
            await self.start_browser()

        await self.page.goto(url, wait_until=wait_for)
        logger.info(f"Navigated to: {url}")

    async def screenshot(self, filename: str, full_page: bool = False):
        """
        Take screenshot

        Args:
            filename: Output filename
            full_page: Capture full scrollable page
        """
        if not self.page:
            raise RuntimeError("No active page")

        output_file = self.output_dir / filename
        await self.page.screenshot(path=str(output_file), full_page=full_page)
        logger.info(f"Screenshot saved: {output_file}")

    async def extract_text(self, selector: str) -> str:
        """Extract text from element"""
        if not self.page:
            raise RuntimeError("No active page")

        element = await self.page.query_selector(selector)
        if element:
            return await element.inner_text()
        return ""

    async def extract_all_text(self, selector: str) -> List[str]:
        """Extract text from all matching elements"""
        if not self.page:
            raise RuntimeError("No active page")

        elements = await self.page.query_selector_all(selector)
        texts = []

        for element in elements:
            text = await element.inner_text()
            texts.append(text)

        return texts


class MarketplaceMonitorAgent(BrowserAgent):
    """
    Monitor marketplaces (Etsy, Redbubble, etc.) for trends and pricing
    """

    async def execute(self) -> Dict[str, Any]:
        """Monitor marketplace"""
        marketplace = self.config.get("marketplace", "etsy")
        search_query = self.config.get("search_query", "trending")

        logger.info(f"Monitoring {marketplace} for: {search_query}")

        try:
            await self.start_browser()

            # Navigate to marketplace
            if marketplace == "etsy":
                url = f"https://www.etsy.com/search?q={search_query}"
            elif marketplace == "redbubble":
                url = f"https://www.redbubble.com/shop/?query={search_query}"
            elif marketplace == "teespring":
                url = f"https://www.teespring.com/discover?query={search_query}"
            else:
                url = f"https://{marketplace}.com/search?q={search_query}"

            await self.navigate(url)

            # Wait for products to load
            await asyncio.sleep(3)

            # Extract product data
            products = await self.scrape_products(marketplace)

            # Save data
            data = {
                "marketplace": marketplace,
                "query": search_query,
                "timestamp": self.last_run.isoformat(),
                "product_count": len(products),
                "products": products
            }

            self.save_data(data, f"{marketplace}_{search_query.replace(' ', '_')}.json")

            return data

        finally:
            await self.close_browser()

    async def scrape_products(self, marketplace: str) -> List[Dict[str, Any]]:
        """
        Scrape product listings

        Args:
            marketplace: Marketplace name

        Returns:
            list: Product data
        """
        products = []

        # Marketplace-specific selectors (simplified)
        if marketplace == "etsy":
            # Extract product titles and prices
            titles = await self.extract_all_text("h3.v2-listing-card__title")
            prices = await self.extract_all_text("span.currency-value")

            for i, (title, price) in enumerate(zip(titles[:20], prices[:20])):
                products.append({
                    "title": title,
                    "price": price,
                    "position": i + 1
                })

        # Add more marketplace-specific logic here

        return products


class CompetitorAnalysisAgent(BrowserAgent):
    """
    Analyze competitor products and pricing
    """

    async def execute(self) -> Dict[str, Any]:
        """Analyze competitors"""
        competitors = self.config.get("competitors", [])

        logger.info(f"Analyzing {len(competitors)} competitors")

        results = []

        try:
            await self.start_browser()

            for competitor_url in competitors:
                try:
                    await self.navigate(competitor_url)
                    await asyncio.sleep(2)

                    # Extract competitor data
                    competitor_data = {
                        "url": competitor_url,
                        "title": await self.page.title(),
                        "timestamp": self.last_run.isoformat()
                    }

                    results.append(competitor_data)

                except Exception as e:
                    logger.error(f"Failed to analyze {competitor_url}: {e}")

            # Save results
            data = {
                "competitors_analyzed": len(results),
                "timestamp": self.last_run.isoformat(),
                "results": results
            }

            self.save_data(data, "competitor_analysis.json")

            return data

        finally:
            await self.close_browser()


class SocialMediaScraperAgent(BrowserAgent):
    """
    Scrape social media for trending content and hashtags
    """

    async def execute(self) -> Dict[str, Any]:
        """Scrape social media"""
        platform = self.config.get("platform", "instagram")
        hashtag = self.config.get("hashtag", "art")

        logger.info(f"Scraping {platform} for #{hashtag}")

        try:
            await self.start_browser()

            # Navigate to hashtag page
            if platform == "instagram":
                # Note: Instagram requires login for most scraping
                url = f"https://www.instagram.com/explore/tags/{hashtag}/"
            elif platform == "twitter":
                url = f"https://twitter.com/hashtag/{hashtag}"
            elif platform == "tiktok":
                url = f"https://www.tiktok.com/tag/{hashtag}"

            await self.navigate(url)
            await asyncio.sleep(5)  # Wait for dynamic content

            # Take screenshot for manual review
            await self.screenshot(f"{platform}_{hashtag}.png", full_page=True)

            data = {
                "platform": platform,
                "hashtag": hashtag,
                "timestamp": self.last_run.isoformat(),
                "screenshot": f"{platform}_{hashtag}.png"
            }

            self.save_data(data, f"{platform}_trends.json")

            return data

        finally:
            await self.close_browser()
