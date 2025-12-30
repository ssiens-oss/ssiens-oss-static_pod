"""
Kill List Analyzer - Product lifecycle management with AI-powered decisions
Analyzes asset performance and recommends which products to keep, optimize, or discontinue
"""

import json
import logging
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime, timedelta
import anthropic
from config import config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PerformanceMetrics:
    """Calculate performance metrics for assets"""

    @staticmethod
    def calculate_roi(revenue: float, cost: float) -> float:
        """Calculate return on investment"""
        if cost == 0:
            return float('inf') if revenue > 0 else 0
        return ((revenue - cost) / cost) * 100

    @staticmethod
    def calculate_conversion_rate(downloads: int, views: int) -> float:
        """Calculate view-to-download conversion rate"""
        if views == 0:
            return 0
        return (downloads / views) * 100

    @staticmethod
    def calculate_revenue_per_view(revenue: float, views: int) -> float:
        """Calculate revenue per view"""
        if views == 0:
            return 0
        return revenue / views

    @staticmethod
    def calculate_daily_revenue(revenue: float, age_days: int) -> float:
        """Calculate average daily revenue"""
        if age_days == 0:
            return 0
        return revenue / age_days

    @staticmethod
    def calculate_trend_score(recent_revenue: float, total_revenue: float) -> str:
        """Determine revenue trend"""
        if total_revenue == 0:
            return "no_data"

        recent_percentage = (recent_revenue / total_revenue) * 100

        if recent_percentage > 60:
            return "strong_growth"
        elif recent_percentage > 40:
            return "steady"
        elif recent_percentage > 20:
            return "declining"
        else:
            return "dead"


class KillListAnalyzer:
    """Analyzes product portfolio and creates kill list recommendations"""

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=config.claude.api_key)
        self.model = config.claude.model
        self.metrics = PerformanceMetrics()

    def analyze_asset(
        self,
        name: str,
        description: str,
        revenue: float,
        revenue_last_30d: float,
        views: int,
        downloads: int,
        age_days: int,
        production_cost: float = 0,
        marketplace: str = "Gumroad",
        category: str = "Asset Pack"
    ) -> Dict:
        """Comprehensive asset performance analysis"""
        logger.info(f"Analyzing: {name}")

        # Calculate metrics
        roi = self.metrics.calculate_roi(revenue, production_cost)
        conversion_rate = self.metrics.calculate_conversion_rate(downloads, views)
        revenue_per_view = self.metrics.calculate_revenue_per_view(revenue, views)
        daily_revenue = self.metrics.calculate_daily_revenue(revenue, age_days)
        trend = self.metrics.calculate_trend_score(revenue_last_30d, revenue)

        # Build context for Claude
        context = f"""Asset Performance Analysis:

**Name:** {name}
**Category:** {category}
**Marketplace:** {marketplace}
**Age:** {age_days} days ({age_days / 30:.1f} months)

**Revenue Metrics:**
- Total Revenue: ${revenue:.2f}
- Last 30 Days: ${revenue_last_30d:.2f}
- Daily Average: ${daily_revenue:.2f}
- Production Cost: ${production_cost:.2f}
- ROI: {roi:.1f}%

**Engagement Metrics:**
- Total Views: {views:,}
- Total Downloads: {downloads}
- Conversion Rate: {conversion_rate:.2f}%
- Revenue per View: ${revenue_per_view:.4f}

**Trend:** {trend}

**Description:** {description}"""

        # Ask Claude for analysis
        prompt = f"""{context}

Based on this data, provide a comprehensive analysis as JSON:

1. **overall_score**: 0-10 rating of asset health
2. **recommendation**: "keep", "optimize", or "kill"
3. **confidence**: 0-100% confidence in recommendation
4. **priority**: "high", "medium", or "low" (urgency of action)

5. **analysis**: Detailed assessment covering:
   - Revenue performance vs expectations
   - Market fit and demand indicators
   - Trend trajectory (growing/stable/declining)
   - Cost-effectiveness

6. **action_items**: If "optimize", provide 3-5 specific actions
7. **kill_reasoning**: If "kill", explain why in 2-3 sentences
8. **keep_reasoning**: If "keep", explain why in 2-3 sentences

9. **metrics_breakdown**:
   - revenue_health: "excellent", "good", "fair", "poor"
   - engagement_health: "excellent", "good", "fair", "poor"
   - trend_health: "excellent", "good", "fair", "poor"
   - roi_health: "excellent", "good", "fair", "poor"

10. **predicted_6month_revenue**: Estimate based on trends

Return ONLY valid JSON."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                temperature=0.3,  # Lower temp for analytical consistency
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            content = response.content[0].text

            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            analysis = json.loads(content)

            # Add calculated metrics
            analysis["calculated_metrics"] = {
                "roi": roi,
                "conversion_rate": conversion_rate,
                "revenue_per_view": revenue_per_view,
                "daily_revenue": daily_revenue,
                "trend": trend
            }

            logger.info(
                f"Score: {analysis.get('overall_score')}/10 - "
                f"Recommendation: {analysis.get('recommendation')}"
            )

            return analysis

        except Exception as e:
            logger.error(f"Failed to analyze asset: {e}")
            return {}

    def analyze_portfolio(self, assets: List[Dict]) -> Dict:
        """Analyze entire product portfolio"""
        logger.info("=" * 60)
        logger.info(f"Analyzing Portfolio ({len(assets)} assets)")
        logger.info("=" * 60)

        results = {
            "keep": [],
            "optimize": [],
            "kill": [],
            "total_revenue": 0,
            "total_views": 0,
            "total_downloads": 0,
            "analysis_date": datetime.now().isoformat()
        }

        for asset in assets:
            analysis = self.analyze_asset(
                name=asset.get("name", "Unknown"),
                description=asset.get("description", ""),
                revenue=asset.get("revenue", 0),
                revenue_last_30d=asset.get("revenue_last_30d", 0),
                views=asset.get("views", 0),
                downloads=asset.get("downloads", 0),
                age_days=asset.get("age_days", 0),
                production_cost=asset.get("production_cost", 0),
                marketplace=asset.get("marketplace", "Unknown"),
                category=asset.get("category", "Asset Pack")
            )

            if analysis:
                recommendation = analysis.get("recommendation", "unknown")
                asset_data = {
                    **asset,
                    "analysis": analysis
                }

                if recommendation == "keep":
                    results["keep"].append(asset_data)
                elif recommendation == "optimize":
                    results["optimize"].append(asset_data)
                elif recommendation == "kill":
                    results["kill"].append(asset_data)

                # Accumulate totals
                results["total_revenue"] += asset.get("revenue", 0)
                results["total_views"] += asset.get("views", 0)
                results["total_downloads"] += asset.get("downloads", 0)

        # Sort each category by overall_score
        results["keep"].sort(
            key=lambda x: x["analysis"].get("overall_score", 0),
            reverse=True
        )
        results["optimize"].sort(
            key=lambda x: x["analysis"].get("overall_score", 0),
            reverse=True
        )
        results["kill"].sort(
            key=lambda x: x["analysis"].get("overall_score", 0)
        )

        # Calculate portfolio metrics
        results["portfolio_metrics"] = {
            "total_assets": len(assets),
            "healthy_assets": len(results["keep"]),
            "at_risk_assets": len(results["optimize"]),
            "failing_assets": len(results["kill"]),
            "health_percentage": (len(results["keep"]) / len(assets) * 100) if assets else 0,
            "average_revenue": results["total_revenue"] / len(assets) if assets else 0,
            "average_conversion": (results["total_downloads"] / results["total_views"] * 100) if results["total_views"] > 0 else 0
        }

        logger.info("\n" + "=" * 60)
        logger.info("Portfolio Analysis Complete")
        logger.info("=" * 60)
        logger.info(f"✓ Keep: {len(results['keep'])} assets")
        logger.info(f"⚠ Optimize: {len(results['optimize'])} assets")
        logger.info(f"✗ Kill: {len(results['kill'])} assets")
        logger.info(f"Portfolio Health: {results['portfolio_metrics']['health_percentage']:.1f}%")
        logger.info("=" * 60)

        return results

    def generate_kill_list_report(self, analysis: Dict) -> str:
        """Generate human-readable kill list report"""
        report = []

        report.append("=" * 80)
        report.append("KILL LIST REPORT")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total Assets Analyzed: {analysis['portfolio_metrics']['total_assets']}")
        report.append("")

        # Portfolio Summary
        report.append("PORTFOLIO HEALTH")
        report.append("-" * 80)
        metrics = analysis["portfolio_metrics"]
        report.append(f"Healthy (Keep):        {metrics['healthy_assets']} assets ({metrics['health_percentage']:.1f}%)")
        report.append(f"At Risk (Optimize):    {metrics['at_risk_assets']} assets")
        report.append(f"Failing (Kill):        {metrics['failing_assets']} assets")
        report.append(f"Total Revenue:         ${analysis['total_revenue']:.2f}")
        report.append(f"Average per Asset:     ${metrics['average_revenue']:.2f}")
        report.append(f"Overall Conversion:    {metrics['average_conversion']:.2f}%")
        report.append("")

        # Assets to Kill (highest priority)
        if analysis["kill"]:
            report.append("=" * 80)
            report.append("🗑️  ASSETS TO DISCONTINUE")
            report.append("=" * 80)

            for asset in analysis["kill"]:
                a = asset["analysis"]
                report.append(f"\n📦 {asset['name']}")
                report.append(f"   Score: {a.get('overall_score', 0)}/10 | Priority: {a.get('priority', 'unknown').upper()}")
                report.append(f"   Revenue: ${asset.get('revenue', 0):.2f} | Views: {asset.get('views', 0):,}")
                report.append(f"   Reasoning: {a.get('kill_reasoning', 'No reasoning provided')}")
                report.append("-" * 80)

        # Assets to Optimize
        if analysis["optimize"]:
            report.append("\n" + "=" * 80)
            report.append("⚠️  ASSETS NEEDING OPTIMIZATION")
            report.append("=" * 80)

            for asset in analysis["optimize"]:
                a = asset["analysis"]
                report.append(f"\n📦 {asset['name']}")
                report.append(f"   Score: {a.get('overall_score', 0)}/10 | Priority: {a.get('priority', 'unknown').upper()}")
                report.append(f"   Revenue: ${asset.get('revenue', 0):.2f} | Trend: {asset['analysis']['calculated_metrics']['trend']}")
                report.append(f"   Action Items:")
                for i, action in enumerate(a.get('action_items', []), 1):
                    report.append(f"     {i}. {action}")
                report.append("-" * 80)

        # Top Performing Assets
        if analysis["keep"]:
            report.append("\n" + "=" * 80)
            report.append("✅ TOP PERFORMING ASSETS (Keep)")
            report.append("=" * 80)

            for asset in analysis["keep"][:5]:  # Top 5
                a = asset["analysis"]
                report.append(f"\n📦 {asset['name']}")
                report.append(f"   Score: {a.get('overall_score', 0)}/10")
                report.append(f"   Revenue: ${asset.get('revenue', 0):.2f} | Daily Avg: ${a['calculated_metrics']['daily_revenue']:.2f}")
                report.append(f"   Reasoning: {a.get('keep_reasoning', 'No reasoning provided')}")
                report.append("-" * 80)

        report.append("\n" + "=" * 80)
        report.append("END OF REPORT")
        report.append("=" * 80)

        return "\n".join(report)

    def save_analysis(self, analysis: Dict, output_path: Path):
        """Save analysis to JSON file"""
        try:
            with open(output_path, 'w') as f:
                json.dump(analysis, f, indent=2)
            logger.info(f"Analysis saved to: {output_path}")
        except Exception as e:
            logger.error(f"Failed to save analysis: {e}")


def main():
    """Example usage"""
    analyzer = KillListAnalyzer()

    # Example asset portfolio
    assets = [
        {
            "name": "Fantasy Potion Icons",
            "description": "32 hand-painted RPG potion icons",
            "revenue": 245.50,
            "revenue_last_30d": 78.00,
            "views": 3420,
            "downloads": 127,
            "age_days": 45,
            "production_cost": 20.00,
            "marketplace": "Gumroad",
            "category": "Icon Pack"
        },
        {
            "name": "Sci-Fi HUD Elements",
            "description": "Futuristic UI components",
            "revenue": 89.25,
            "revenue_last_30d": 12.50,
            "views": 1850,
            "downloads": 34,
            "age_days": 90,
            "production_cost": 25.00,
            "marketplace": "Itch.io",
            "category": "UI Kit"
        },
        {
            "name": "Medieval Weapon Pack",
            "description": "20 detailed weapon sprites",
            "revenue": 12.00,
            "revenue_last_30d": 0.00,
            "views": 890,
            "downloads": 8,
            "age_days": 120,
            "production_cost": 30.00,
            "marketplace": "Gumroad",
            "category": "Sprite Pack"
        },
        {
            "name": "Magic Spell Effects",
            "description": "Animated particle effects",
            "revenue": 567.80,
            "revenue_last_30d": 234.50,
            "views": 8920,
            "downloads": 289,
            "age_days": 60,
            "production_cost": 40.00,
            "marketplace": "Gumroad",
            "category": "VFX Pack"
        }
    ]

    # Analyze portfolio
    analysis = analyzer.analyze_portfolio(assets)

    # Generate and print report
    report = analyzer.generate_kill_list_report(analysis)
    print("\n" + report)

    # Save analysis
    output_dir = Path("./output")
    output_dir.mkdir(exist_ok=True)
    analyzer.save_analysis(analysis, output_dir / "kill_list_analysis.json")

    print(f"\n✓ Full analysis saved to: {output_dir / 'kill_list_analysis.json'}")


if __name__ == "__main__":
    main()
