#!/usr/bin/env python3
"""
Agent Management API
API endpoints for controlling and monitoring agents
"""

from flask import Blueprint, request, jsonify
import asyncio
from pathlib import Path
from typing import Dict, Any

from agents.core.orchestrator import AgentOrchestrator
from agents.browser.automation import MarketplaceMonitorAgent, CompetitorAnalysisAgent
from agents.research.trends import TrendAnalysisAgent, OpportunityFinderAgent, SeasonalTrendsAgent
from agents.prompts.generator import PromptGeneratorAgent
from agents.workflows.presets import get_workflow, list_workflows

# Create Blueprint
agents_bp = Blueprint('agents', __name__, url_prefix='/agents')

# Global orchestrator instance
orchestrator = None

def get_orchestrator() -> AgentOrchestrator:
    """Get or create orchestrator instance"""
    global orchestrator
    if orchestrator is None:
        data_dir = Path("/opt/staticwaves-pod/data/agents")
        orchestrator = AgentOrchestrator(data_dir)

        # Register default agents
        register_default_agents(orchestrator)

    return orchestrator

def register_default_agents(orch: AgentOrchestrator):
    """Register default agent set"""

    output_dir = Path("/opt/staticwaves-pod/data/agents")

    # Browser agents
    etsy_monitor = MarketplaceMonitorAgent(
        "marketplace_monitor_etsy",
        output_dir,
        {"marketplace": "etsy", "search_query": "trending", "headless": True}
    )
    orch.register_agent(etsy_monitor)

    # Research agents
    trend_agent = TrendAnalysisAgent("trend_analysis", output_dir)
    orch.register_agent(trend_agent)

    opportunity_agent = OpportunityFinderAgent("opportunity_finder", output_dir)
    orch.register_agent(opportunity_agent)

    seasonal_agent = SeasonalTrendsAgent("seasonal_trends", output_dir)
    orch.register_agent(seasonal_agent)

    # Prompt generator
    prompt_agent = PromptGeneratorAgent(
        "prompt_generator",
        ["trend_analysis", "seasonal_trends"],
        {}
    )
    orch.register_agent(prompt_agent)


@agents_bp.route('/status', methods=['GET'])
def get_status():
    """Get status of all agents"""
    orch = get_orchestrator()
    return jsonify(orch.get_status())

@agents_bp.route('/agents', methods=['GET'])
def list_agents():
    """List all registered agents"""
    orch = get_orchestrator()
    agents = orch.get_status()["agents"]

    return jsonify({
        "count": len(agents),
        "agents": list(agents.keys())
    })

@agents_bp.route('/agents/<agent_name>', methods=['GET'])
def get_agent_status(agent_name: str):
    """Get status of specific agent"""
    orch = get_orchestrator()

    if agent_name not in orch.agents:
        return jsonify({"error": f"Agent '{agent_name}' not found"}), 404

    agent = orch.agents[agent_name]
    return jsonify(agent.get_status())

@agents_bp.route('/agents/<agent_name>/run', methods=['POST'])
def run_agent(agent_name: str):
    """Manually run a specific agent"""
    orch = get_orchestrator()

    if agent_name not in orch.agents:
        return jsonify({"error": f"Agent '{agent_name}' not found"}), 404

    # Run agent asynchronously
    result = asyncio.run(orch.run_agent(agent_name))

    return jsonify(result)

@agents_bp.route('/agents/<agent_name>/pause', methods=['POST'])
def pause_agent(agent_name: str):
    """Pause an agent"""
    orch = get_orchestrator()

    if agent_name not in orch.agents:
        return jsonify({"error": f"Agent '{agent_name}' not found"}), 404

    agent = orch.agents[agent_name]
    agent.pause()

    return jsonify({
        "success": True,
        "agent": agent_name,
        "state": "paused"
    })

@agents_bp.route('/agents/<agent_name>/resume', methods=['POST'])
def resume_agent(agent_name: str):
    """Resume an agent"""
    orch = get_orchestrator()

    if agent_name not in orch.agents:
        return jsonify({"error": f"Agent '{agent_name}' not found"}), 404

    agent = orch.agents[agent_name]
    agent.resume()

    return jsonify({
        "success": True,
        "agent": agent_name,
        "state": "idle"
    })

@agents_bp.route('/workflows', methods=['GET'])
def get_workflows():
    """List available workflows"""
    workflows = list_workflows()

    return jsonify({
        "count": len(workflows),
        "workflows": workflows
    })

@agents_bp.route('/workflows/<workflow_name>/run', methods=['POST'])
def run_workflow(workflow_name: str):
    """Execute a workflow"""
    orch = get_orchestrator()

    workflow = get_workflow(workflow_name)

    if not workflow:
        return jsonify({"error": f"Workflow '{workflow_name}' not found"}), 404

    # Execute workflow
    result = asyncio.run(orch.execute_workflow(workflow))

    return jsonify(result)

@agents_bp.route('/pipeline', methods=['POST'])
def run_pipeline():
    """
    Run custom agent pipeline

    Body: {
        "agents": ["agent1", "agent2", "agent3"]
    }
    """
    data = request.json
    agent_names = data.get("agents", [])

    if not agent_names:
        return jsonify({"error": "No agents specified"}), 400

    orch = get_orchestrator()

    # Validate agents exist
    for name in agent_names:
        if name not in orch.agents:
            return jsonify({"error": f"Agent '{name}' not found"}), 404

    # Run pipeline
    results = asyncio.run(orch.run_pipeline(agent_names))

    return jsonify({
        "pipeline": agent_names,
        "results": results
    })

@agents_bp.route('/parallel', methods=['POST'])
def run_parallel():
    """
    Run agents in parallel

    Body: {
        "agents": ["agent1", "agent2", "agent3"]
    }
    """
    data = request.json
    agent_names = data.get("agents", [])

    if not agent_names:
        return jsonify({"error": "No agents specified"}), 400

    orch = get_orchestrator()

    # Validate agents exist
    for name in agent_names:
        if name not in orch.agents:
            return jsonify({"error": f"Agent '{name}' not found"}), 404

    # Run in parallel
    results = asyncio.run(orch.run_parallel(agent_names))

    return jsonify({
        "agents": agent_names,
        "results": results
    })

@agents_bp.route('/quick-launch', methods=['POST'])
def quick_launch():
    """
    Quick launch: keyword → prompt → design → publish

    Body: {
        "keyword": "cosmic waves",
        "product_type": "hoodie",
        "auto_publish": true
    }
    """
    data = request.json
    keyword = data.get("keyword")
    product_type = data.get("product_type", "hoodie")
    auto_publish = data.get("auto_publish", False)

    if not keyword:
        return jsonify({"error": "Keyword required"}), 400

    # Generate custom workflow
    workflow = {
        "name": "quick_launch",
        "steps": [
            {
                "type": "sequential",
                "agents": [
                    "prompt_generator",
                    "comfy_worker"
                ]
            }
        ]
    }

    orch = get_orchestrator()
    result = asyncio.run(orch.execute_workflow(workflow))

    return jsonify({
        "keyword": keyword,
        "product_type": product_type,
        "auto_publish": auto_publish,
        "workflow_result": result
    })
