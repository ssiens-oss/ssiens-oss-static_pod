#!/usr/bin/env python3
"""
Agent Orchestrator
Manages and coordinates multiple autonomous agents
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
from pathlib import Path

from agents.core.agent import Agent, ScheduledAgent

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """
    Central orchestrator for managing multiple agents
    Handles coordination, scheduling, and communication between agents
    """

    def __init__(self, data_dir: Path):
        self.agents: Dict[str, Agent] = {}
        self.scheduled_agents: List[ScheduledAgent] = []
        self.running = False
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Agent communication channels
        self.message_bus = asyncio.Queue()

        logger.info("Agent Orchestrator initialized")

    def register_agent(self, agent: Agent):
        """
        Register an agent with the orchestrator

        Args:
            agent: Agent instance to register
        """
        self.agents[agent.name] = agent

        if isinstance(agent, ScheduledAgent):
            self.scheduled_agents.append(agent)

        logger.info(f"Registered agent: {agent.name}")

    def unregister_agent(self, agent_name: str):
        """Unregister an agent"""
        if agent_name in self.agents:
            agent = self.agents[agent_name]
            agent.stop()
            del self.agents[agent_name]

            if isinstance(agent, ScheduledAgent) and agent in self.scheduled_agents:
                self.scheduled_agents.remove(agent)

            logger.info(f"Unregistered agent: {agent_name}")

    async def start(self):
        """Start the orchestrator and all scheduled agents"""
        self.running = True

        logger.info("Starting Agent Orchestrator...")

        # Start all scheduled agents
        tasks = []
        for agent in self.scheduled_agents:
            task = asyncio.create_task(agent.start_scheduler())
            tasks.append(task)

        # Start message bus processor
        tasks.append(asyncio.create_task(self.process_messages()))

        logger.info(f"Started {len(self.scheduled_agents)} scheduled agents")

        # Wait for all tasks
        await asyncio.gather(*tasks)

    async def stop(self):
        """Stop the orchestrator and all agents"""
        logger.info("Stopping Agent Orchestrator...")

        self.running = False

        # Stop all agents
        for agent in self.agents.values():
            agent.stop()

        logger.info("Agent Orchestrator stopped")

    async def run_agent(self, agent_name: str) -> Dict[str, Any]:
        """
        Manually run a specific agent

        Args:
            agent_name: Name of agent to run

        Returns:
            dict: Execution result
        """
        if agent_name not in self.agents:
            raise ValueError(f"Agent '{agent_name}' not found")

        agent = self.agents[agent_name]
        return await agent.run()

    async def run_pipeline(self, agent_names: List[str]) -> List[Dict[str, Any]]:
        """
        Run multiple agents in sequence (pipeline)

        Args:
            agent_names: List of agent names to run in order

        Returns:
            list: Results from each agent
        """
        results = []

        logger.info(f"Running agent pipeline: {' → '.join(agent_names)}")

        for agent_name in agent_names:
            result = await self.run_agent(agent_name)
            results.append(result)

            # Stop pipeline if agent failed
            if not result.get("success"):
                logger.error(f"Pipeline stopped at agent '{agent_name}' due to failure")
                break

        return results

    async def run_parallel(self, agent_names: List[str]) -> List[Dict[str, Any]]:
        """
        Run multiple agents in parallel

        Args:
            agent_names: List of agent names to run concurrently

        Returns:
            list: Results from each agent
        """
        logger.info(f"Running agents in parallel: {', '.join(agent_names)}")

        tasks = [self.run_agent(name) for name in agent_names]
        results = await asyncio.gather(*tasks)

        return list(results)

    async def send_message(self, from_agent: str, to_agent: str, message: Dict[str, Any]):
        """
        Send message between agents

        Args:
            from_agent: Sender agent name
            to_agent: Recipient agent name
            message: Message payload
        """
        await self.message_bus.put({
            "from": from_agent,
            "to": to_agent,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        })

    async def process_messages(self):
        """Process messages from the message bus"""
        while self.running:
            try:
                # Get message with timeout
                message = await asyncio.wait_for(
                    self.message_bus.get(),
                    timeout=1.0
                )

                # Deliver message to recipient agent
                to_agent = message["to"]
                if to_agent in self.agents:
                    # Agent-specific message handling would go here
                    logger.info(f"Message: {message['from']} → {message['to']}")

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Message processing error: {e}")

    def get_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        return {
            "orchestrator_running": self.running,
            "total_agents": len(self.agents),
            "scheduled_agents": len(self.scheduled_agents),
            "agents": {
                name: agent.get_status()
                for name, agent in self.agents.items()
            }
        }

    def save_state(self):
        """Save orchestrator state to file"""
        state = {
            "timestamp": datetime.utcnow().isoformat(),
            "status": self.get_status()
        }

        state_file = self.data_dir / "orchestrator_state.json"
        with open(state_file, "w") as f:
            json.dump(state, f, indent=2)

        logger.info(f"Orchestrator state saved to {state_file}")

    async def execute_workflow(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a complex workflow with multiple agents

        Workflow format:
        {
            "name": "workflow_name",
            "steps": [
                {"type": "sequential", "agents": ["agent1", "agent2"]},
                {"type": "parallel", "agents": ["agent3", "agent4"]},
                {"type": "conditional", "condition": "...", "agents": ["agent5"]}
            ]
        }

        Args:
            workflow: Workflow definition

        Returns:
            dict: Workflow execution result
        """
        workflow_name = workflow.get("name", "unnamed")
        steps = workflow.get("steps", [])

        logger.info(f"Executing workflow: {workflow_name}")

        results = []

        for i, step in enumerate(steps):
            step_type = step.get("type")
            agents = step.get("agents", [])

            logger.info(f"Workflow '{workflow_name}' - Step {i+1}/{len(steps)}: {step_type}")

            if step_type == "sequential":
                step_result = await self.run_pipeline(agents)
            elif step_type == "parallel":
                step_result = await self.run_parallel(agents)
            else:
                logger.warning(f"Unknown step type: {step_type}")
                continue

            results.append({
                "step": i + 1,
                "type": step_type,
                "agents": agents,
                "results": step_result
            })

            # Check for failures
            if step.get("stop_on_failure", True):
                if any(not r.get("success") for r in step_result):
                    logger.error(f"Workflow stopped at step {i+1} due to failure")
                    break

        return {
            "workflow": workflow_name,
            "completed": True,
            "steps_executed": len(results),
            "timestamp": datetime.utcnow().isoformat(),
            "results": results
        }
