"""
Notion Sync - Dashboard integration for tracking asset pipeline
Syncs asset data, performance metrics, and analysis to Notion databases
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
import requests
from config import config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class NotionClient:
    """Notion API client for database operations"""

    def __init__(self, api_key: Optional[str] = None, database_id: Optional[str] = None):
        self.api_key = api_key or config.notion.api_key
        self.database_id = database_id or config.notion.database_id
        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }

    def create_page(self, properties: Dict) -> Optional[Dict]:
        """Create a new page in the database"""
        url = f"{self.base_url}/pages"

        data = {
            "parent": {"database_id": self.database_id},
            "properties": properties
        }

        try:
            response = requests.post(url, headers=self.headers, json=data, timeout=30)
            response.raise_for_status()
            page = response.json()
            logger.info(f"Created page: {page.get('id')}")
            return page

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to create page: {e}")
            return None

    def update_page(self, page_id: str, properties: Dict) -> Optional[Dict]:
        """Update an existing page"""
        url = f"{self.base_url}/pages/{page_id}"

        data = {"properties": properties}

        try:
            response = requests.patch(url, headers=self.headers, json=data, timeout=30)
            response.raise_for_status()
            page = response.json()
            logger.info(f"Updated page: {page_id}")
            return page

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to update page: {e}")
            return None

    def query_database(
        self,
        filter_obj: Optional[Dict] = None,
        sorts: Optional[List[Dict]] = None
    ) -> List[Dict]:
        """Query database with optional filters and sorts"""
        url = f"{self.base_url}/databases/{self.database_id}/query"

        data = {}
        if filter_obj:
            data["filter"] = filter_obj
        if sorts:
            data["sorts"] = sorts

        try:
            response = requests.post(url, headers=self.headers, json=data, timeout=30)
            response.raise_for_status()
            result = response.json()
            pages = result.get("results", [])
            logger.info(f"Queried database: {len(pages)} results")
            return pages

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to query database: {e}")
            return []

    def find_page_by_name(self, asset_name: str) -> Optional[Dict]:
        """Find page by asset name"""
        filter_obj = {
            "property": "Name",
            "title": {
                "equals": asset_name
            }
        }

        pages = self.query_database(filter_obj=filter_obj)
        return pages[0] if pages else None


class NotionDashboard:
    """Manages Notion dashboard for asset tracking"""

    def __init__(self):
        self.client = NotionClient()

    def create_asset_entry(
        self,
        theme: str,
        asset_type: str,
        status: str,
        revenue: float = 0,
        views: int = 0,
        downloads: int = 0,
        tiktok_views: int = 0,
        claude_score: float = 0,
        marketplace: str = "Gumroad",
        archive_path: Optional[str] = None,
        listing_data: Optional[Dict] = None
    ) -> Optional[Dict]:
        """Create new asset entry in Notion"""
        logger.info(f"Creating Notion entry: {theme}")

        properties = {
            "Name": {
                "title": [{"text": {"content": theme}}]
            },
            "Asset Type": {
                "select": {"name": asset_type}
            },
            "Status": {
                "select": {"name": status}
            },
            "Revenue": {
                "number": revenue
            },
            "Views": {
                "number": views
            },
            "Downloads": {
                "number": downloads
            },
            "TikTok Views": {
                "number": tiktok_views
            },
            "Claude Score": {
                "number": claude_score
            },
            "Marketplace": {
                "select": {"name": marketplace}
            },
            "Created": {
                "date": {"start": datetime.now().isoformat()}
            }
        }

        # Add optional fields
        if archive_path:
            properties["Archive Path"] = {
                "rich_text": [{"text": {"content": archive_path}}]
            }

        if listing_data:
            # Add SEO title and tags
            if "seo_title" in listing_data:
                properties["SEO Title"] = {
                    "rich_text": [{"text": {"content": listing_data["seo_title"]}}]
                }

            if "tags" in listing_data:
                properties["Tags"] = {
                    "multi_select": [{"name": tag} for tag in listing_data["tags"][:5]]
                }

        return self.client.create_page(properties)

    def update_asset_metrics(
        self,
        asset_name: str,
        revenue: Optional[float] = None,
        views: Optional[int] = None,
        downloads: Optional[int] = None,
        tiktok_views: Optional[int] = None,
        claude_score: Optional[float] = None,
        status: Optional[str] = None
    ) -> Optional[Dict]:
        """Update metrics for existing asset"""
        logger.info(f"Updating metrics for: {asset_name}")

        # Find existing page
        page = self.client.find_page_by_name(asset_name)

        if not page:
            logger.warning(f"Asset not found: {asset_name}")
            return None

        page_id = page["id"]
        properties = {}

        # Update only provided fields
        if revenue is not None:
            properties["Revenue"] = {"number": revenue}
        if views is not None:
            properties["Views"] = {"number": views}
        if downloads is not None:
            properties["Downloads"] = {"number": downloads}
        if tiktok_views is not None:
            properties["TikTok Views"] = {"number": tiktok_views}
        if claude_score is not None:
            properties["Claude Score"] = {"number": claude_score}
        if status is not None:
            properties["Status"] = {"select": {"name": status}}

        # Add last updated timestamp
        properties["Last Updated"] = {
            "date": {"start": datetime.now().isoformat()}
        }

        return self.client.update_page(page_id, properties)

    def sync_kill_list_analysis(self, analysis: Dict) -> Dict[str, int]:
        """Sync kill list analysis results to Notion"""
        logger.info("Syncing kill list analysis to Notion")

        results = {"updated": 0, "failed": 0}

        # Update assets with recommendations
        for category in ["keep", "optimize", "kill"]:
            for asset in analysis.get(category, []):
                asset_analysis = asset.get("analysis", {})

                updated = self.update_asset_metrics(
                    asset_name=asset["name"],
                    revenue=asset.get("revenue"),
                    views=asset.get("views"),
                    downloads=asset.get("downloads"),
                    claude_score=asset_analysis.get("overall_score"),
                    status=f"{category.capitalize()}"
                )

                if updated:
                    results["updated"] += 1
                else:
                    results["failed"] += 1

        logger.info(f"Sync complete: {results['updated']} updated, {results['failed']} failed")
        return results

    def get_all_assets(self) -> List[Dict]:
        """Get all assets from Notion database"""
        logger.info("Fetching all assets from Notion")

        pages = self.client.query_database(
            sorts=[{"property": "Revenue", "direction": "descending"}]
        )

        assets = []
        for page in pages:
            props = page.get("properties", {})

            # Extract properties
            asset = {
                "name": self._extract_title(props.get("Name")),
                "asset_type": self._extract_select(props.get("Asset Type")),
                "status": self._extract_select(props.get("Status")),
                "revenue": self._extract_number(props.get("Revenue")),
                "views": self._extract_number(props.get("Views")),
                "downloads": self._extract_number(props.get("Downloads")),
                "tiktok_views": self._extract_number(props.get("TikTok Views")),
                "claude_score": self._extract_number(props.get("Claude Score")),
                "marketplace": self._extract_select(props.get("Marketplace")),
                "notion_page_id": page["id"]
            }

            assets.append(asset)

        logger.info(f"Fetched {len(assets)} assets")
        return assets

    @staticmethod
    def _extract_title(prop: Optional[Dict]) -> str:
        """Extract title from Notion property"""
        if not prop or "title" not in prop:
            return ""
        titles = prop["title"]
        return titles[0]["text"]["content"] if titles else ""

    @staticmethod
    def _extract_select(prop: Optional[Dict]) -> str:
        """Extract select value from Notion property"""
        if not prop or "select" not in prop or not prop["select"]:
            return ""
        return prop["select"]["name"]

    @staticmethod
    def _extract_number(prop: Optional[Dict]) -> float:
        """Extract number from Notion property"""
        if not prop or "number" not in prop or prop["number"] is None:
            return 0
        return float(prop["number"])


class PipelineTracker:
    """Tracks asset creation pipeline status in Notion"""

    def __init__(self):
        self.dashboard = NotionDashboard()

    def track_generation(
        self,
        theme: str,
        asset_type: str,
        prompts: List[str],
        archive_path: str
    ) -> Optional[Dict]:
        """Track asset generation phase"""
        return self.dashboard.create_asset_entry(
            theme=theme,
            asset_type=asset_type,
            status="Generated",
            archive_path=archive_path
        )

    def track_listing_creation(
        self,
        asset_name: str,
        listing_data: Dict
    ) -> Optional[Dict]:
        """Track listing creation phase"""
        claude_score = listing_data.get("pricing_suggestion", {})

        return self.dashboard.update_asset_metrics(
            asset_name=asset_name,
            status="Listed",
            claude_score=8.0  # Default score for newly listed
        )

    def track_marketplace_upload(
        self,
        asset_name: str,
        marketplace: str,
        success: bool
    ) -> Optional[Dict]:
        """Track marketplace upload"""
        status = "Published" if success else "Upload Failed"

        return self.dashboard.update_asset_metrics(
            asset_name=asset_name,
            status=status
        )

    def track_performance(
        self,
        asset_name: str,
        revenue: float,
        views: int,
        downloads: int,
        tiktok_views: int = 0
    ) -> Optional[Dict]:
        """Track asset performance metrics"""
        return self.dashboard.update_asset_metrics(
            asset_name=asset_name,
            revenue=revenue,
            views=views,
            downloads=downloads,
            tiktok_views=tiktok_views
        )


def main():
    """Example usage"""
    tracker = PipelineTracker()

    # Example: Track asset generation
    asset_entry = tracker.track_generation(
        theme="Fantasy Potion Icons",
        asset_type="Icon Pack",
        prompts=["fantasy potion icons, vibrant colors"],
        archive_path="./archives/fantasy_potions.zip"
    )

    if asset_entry:
        print("✓ Asset tracked in Notion")

        # Update with performance data
        tracker.track_performance(
            asset_name="Fantasy Potion Icons",
            revenue=145.50,
            views=2340,
            downloads=87,
            tiktok_views=1200
        )

        print("✓ Performance metrics updated")

    # Example: Fetch all assets
    dashboard = NotionDashboard()
    all_assets = dashboard.get_all_assets()

    print(f"\n{'=' * 60}")
    print("NOTION DASHBOARD ASSETS")
    print(f"{'=' * 60}")
    for asset in all_assets[:5]:  # Top 5
        print(f"\n{asset['name']}")
        print(f"  Revenue: ${asset['revenue']:.2f}")
        print(f"  Score: {asset['claude_score']}/10")
        print(f"  Status: {asset['status']}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
