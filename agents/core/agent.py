#!/usr/bin/env python3
"""
Base Agent Framework
Abstract base class for all autonomous agents
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, Optional, List
import json
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Agent(ABC):
    """Base class for all autonomous agents"""

    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.config = config or {}
        self.state = "idle"  # idle, running, paused, stopped
        self.last_run = None
        self.run_count = 0
        self.errors = []

        logger.info(f"Agent '{self.name}' initialized")

    @abstractmethod
    async def execute(self) -> Dict[str, Any]:
        """
        Main execution logic - must be implemented by subclasses

        Returns:
            dict: Execution result with status and data
        """
        pass

    async def run(self) -> Dict[str, Any]:
        """
        Run the agent with error handling and state management

        Returns:
            dict: Execution result
        """
        try:
            self.state = "running"
            self.run_count += 1
            self.last_run = datetime.utcnow()

            logger.info(f"Agent '{self.name}' starting execution #{self.run_count}")

            # Execute agent logic
            result = await self.execute()

            self.state = "idle"

            logger.info(f"Agent '{self.name}' completed successfully")

            return {
                "success": True,
                "agent": self.name,
                "timestamp": self.last_run.isoformat(),
                "run_count": self.run_count,
                "result": result
            }

        except Exception as e:
            self.state = "idle"
            error_msg = str(e)
            self.errors.append({
                "timestamp": datetime.utcnow().isoformat(),
                "error": error_msg
            })

            logger.error(f"Agent '{self.name}' failed: {error_msg}")

            return {
                "success": False,
                "agent": self.name,
                "timestamp": datetime.utcnow().isoformat(),
                "error": error_msg
            }

    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "name": self.name,
            "state": self.state,
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "run_count": self.run_count,
            "error_count": len(self.errors),
            "config": self.config
        }

    def pause(self):
        """Pause agent execution"""
        self.state = "paused"
        logger.info(f"Agent '{self.name}' paused")

    def resume(self):
        """Resume agent execution"""
        self.state = "idle"
        logger.info(f"Agent '{self.name}' resumed")

    def stop(self):
        """Stop agent"""
        self.state = "stopped"
        logger.info(f"Agent '{self.name}' stopped")


class ScheduledAgent(Agent):
    """Agent that runs on a schedule"""

    def __init__(self, name: str, interval_seconds: int, config: Optional[Dict[str, Any]] = None):
        super().__init__(name, config)
        self.interval = interval_seconds
        self.running = False

    async def start_scheduler(self):
        """Start the agent scheduler"""
        self.running = True
        self.state = "idle"

        logger.info(f"Scheduled agent '{self.name}' started (interval: {self.interval}s)")

        while self.running:
            if self.state == "idle":
                await self.run()

            # Wait for next execution
            await asyncio.sleep(self.interval)

    def stop(self):
        """Stop the scheduler"""
        self.running = False
        super().stop()


class EventDrivenAgent(Agent):
    """Agent that responds to events"""

    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(name, config)
        self.event_queue = asyncio.Queue()

    async def handle_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle an incoming event

        Args:
            event: Event data

        Returns:
            dict: Event handling result
        """
        await self.event_queue.put(event)
        return await self.run()

    async def get_next_event(self) -> Dict[str, Any]:
        """Get next event from queue"""
        return await self.event_queue.get()


class DataCollectorAgent(Agent):
    """Agent that collects and stores data"""

    def __init__(self, name: str, output_dir: Path, config: Optional[Dict[str, Any]] = None):
        super().__init__(name, config)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def save_data(self, data: Dict[str, Any], filename: Optional[str] = None):
        """
        Save collected data to file

        Args:
            data: Data to save
            filename: Optional filename (defaults to timestamp)
        """
        if filename is None:
            filename = f"{self.name}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"

        output_file = self.output_dir / filename

        with open(output_file, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Agent '{self.name}' saved data to {output_file}")

    def load_data(self, filename: str) -> Dict[str, Any]:
        """Load data from file"""
        with open(self.output_dir / filename) as f:
            return json.load(f)


class ProcessorAgent(Agent):
    """Agent that processes data from other agents"""

    def __init__(self, name: str, input_agents: List[str], config: Optional[Dict[str, Any]] = None):
        super().__init__(name, config)
        self.input_agents = input_agents

    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input data

        Args:
            input_data: Data from input agents

        Returns:
            dict: Processed result
        """
        pass

    async def execute(self) -> Dict[str, Any]:
        """Execute processing"""
        # Collect data from input agents
        input_data = await self.collect_inputs()

        # Process
        result = await self.process(input_data)

        return result

    async def collect_inputs(self) -> Dict[str, Any]:
        """Collect data from input agents"""
        # This would integrate with the agent orchestrator
        # For now, return placeholder
        return {"inputs": self.input_agents}
