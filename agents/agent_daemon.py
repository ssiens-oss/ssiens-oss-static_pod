#!/usr/bin/env python3
"""
Agent Daemon
Background service that runs the agent orchestrator
"""

import asyncio
import logging
import signal
import sys
from pathlib import Path

# Add parent to path
sys.path.append(str(Path(__file__).parent.parent))

from agents.core.orchestrator import AgentOrchestrator
from agents.browser.automation import MarketplaceMonitorAgent
from agents.research.trends import TrendAnalysisAgent, SeasonalTrendsAgent, OpportunityFinderAgent
from agents.prompts.generator import PromptGeneratorAgent
from agents.core.agent import ScheduledAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global orchestrator
orchestrator = None

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}, shutting down...")
    if orchestrator:
        asyncio.create_task(orchestrator.stop())
    sys.exit(0)

async def main():
    """Main daemon loop"""
    global orchestrator

    logger.info("Starting StaticWaves Agent Daemon...")

    # Setup data directory
    data_dir = Path("/opt/staticwaves-pod/data/agents")
    data_dir.mkdir(parents=True, exist_ok=True)

    # Create orchestrator
    orchestrator = AgentOrchestrator(data_dir)

    # Register scheduled agents
    logger.info("Registering agents...")

    # Marketplace monitor - runs every 6 hours
    etsy_monitor = MarketplaceMonitorAgent(
        "marketplace_monitor_etsy",
        data_dir,
        {"marketplace": "etsy", "search_query": "trending", "headless": True}
    )
    # Wrap in scheduled agent
    etsy_scheduled = ScheduledAgent("etsy_monitor_scheduled", interval_seconds=21600)
    etsy_scheduled.execute = etsy_monitor.execute
    orchestrator.register_agent(etsy_scheduled)

    # Trend analysis - runs every 12 hours
    trend_agent = TrendAnalysisAgent("trend_analysis", data_dir)
    trend_scheduled = ScheduledAgent("trend_analysis_scheduled", interval_seconds=43200)
    trend_scheduled.execute = trend_agent.execute
    orchestrator.register_agent(trend_scheduled)

    # Seasonal trends - runs daily
    seasonal_agent = SeasonalTrendsAgent("seasonal_trends", data_dir)
    seasonal_scheduled = ScheduledAgent("seasonal_trends_scheduled", interval_seconds=86400)
    seasonal_scheduled.execute = seasonal_agent.execute
    orchestrator.register_agent(seasonal_scheduled)

    # Opportunity finder - runs every 12 hours
    opportunity_agent = OpportunityFinderAgent("opportunity_finder", data_dir)
    opportunity_scheduled = ScheduledAgent("opportunity_finder_scheduled", interval_seconds=43200)
    opportunity_scheduled.execute = opportunity_agent.execute
    orchestrator.register_agent(opportunity_scheduled)

    # Prompt generator - runs every 6 hours
    prompt_agent = PromptGeneratorAgent(
        "prompt_generator",
        ["trend_analysis", "seasonal_trends"],
        {}
    )
    prompt_scheduled = ScheduledAgent("prompt_generator_scheduled", interval_seconds=21600)
    prompt_scheduled.execute = prompt_agent.execute
    orchestrator.register_agent(prompt_scheduled)

    logger.info(f"Registered {len(orchestrator.agents)} agents")

    # Start orchestrator
    try:
        await orchestrator.start()
    except KeyboardInterrupt:
        logger.info("Received interrupt, shutting down...")
        await orchestrator.stop()

if __name__ == "__main__":
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Run daemon
    asyncio.run(main())
