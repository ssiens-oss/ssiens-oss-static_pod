#!/usr/bin/env python3
"""
Pre-built Agent Workflows
Common multi-agent automation workflows
"""

from typing import Dict, Any

# Daily Market Research Workflow
DAILY_RESEARCH_WORKFLOW = {
    "name": "daily_market_research",
    "description": "Daily automated market research and trend analysis",
    "steps": [
        {
            "type": "parallel",
            "agents": [
                "marketplace_monitor_etsy",
                "marketplace_monitor_redbubble",
                "social_scraper_instagram"
            ],
            "stop_on_failure": False
        },
        {
            "type": "sequential",
            "agents": [
                "trend_analysis",
                "opportunity_finder"
            ]
        },
        {
            "type": "sequential",
            "agents": [
                "prompt_generator",
                "seasonal_trends"
            ]
        }
    ]
}

# Competitive Analysis Workflow
COMPETITIVE_ANALYSIS_WORKFLOW = {
    "name": "competitive_analysis",
    "description": "Monitor and analyze competitor products",
    "steps": [
        {
            "type": "sequential",
            "agents": [
                "competitor_monitor",
                "price_analysis",
                "competitor_report"
            ]
        }
    ]
}

# Full Automation Workflow (Research → Generate → Publish)
FULL_AUTOMATION_WORKFLOW = {
    "name": "full_pod_automation",
    "description": "Complete autonomous POD workflow from research to publication",
    "steps": [
        {
            "type": "parallel",
            "agents": [
                "marketplace_monitor_etsy",
                "trend_analysis",
                "seasonal_trends"
            ],
            "stop_on_failure": False
        },
        {
            "type": "sequential",
            "agents": [
                "opportunity_finder",
                "prompt_generator"
            ]
        },
        {
            "type": "sequential",
            "agents": [
                "comfy_worker",
                "mockup_worker",
                "uploader_worker"
            ]
        }
    ]
}

# Weekly Optimization Workflow
WEEKLY_OPTIMIZATION_WORKFLOW = {
    "name": "weekly_optimization",
    "description": "Weekly performance analysis and optimization",
    "steps": [
        {
            "type": "sequential",
            "agents": [
                "performance_analyzer",
                "prompt_optimizer",
                "pricing_optimizer"
            ]
        }
    ]
}

# Rapid Launch Workflow (for manual triggers)
RAPID_LAUNCH_WORKFLOW = {
    "name": "rapid_launch",
    "description": "Quick product launch based on specific keyword",
    "steps": [
        {
            "type": "sequential",
            "agents": [
                "keyword_prompt_generator",
                "comfy_worker",
                "mockup_worker",
                "uploader_worker"
            ]
        }
    ]
}

def get_workflow(name: str) -> Dict[str, Any]:
    """
    Get workflow by name

    Args:
        name: Workflow name

    Returns:
        dict: Workflow configuration
    """
    workflows = {
        "daily_research": DAILY_RESEARCH_WORKFLOW,
        "competitive": COMPETITIVE_ANALYSIS_WORKFLOW,
        "full_automation": FULL_AUTOMATION_WORKFLOW,
        "weekly_optimization": WEEKLY_OPTIMIZATION_WORKFLOW,
        "rapid_launch": RAPID_LAUNCH_WORKFLOW
    }

    return workflows.get(name, {})

def list_workflows() -> Dict[str, str]:
    """
    List all available workflows

    Returns:
        dict: Workflow names and descriptions
    """
    return {
        "daily_research": "Daily automated market research and trend analysis",
        "competitive": "Monitor and analyze competitor products",
        "full_automation": "Complete autonomous POD workflow",
        "weekly_optimization": "Weekly performance analysis",
        "rapid_launch": "Quick product launch from keyword"
    }
