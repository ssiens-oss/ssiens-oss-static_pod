"""Bridge between Antigravity and existing POD Gateway."""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional
from antigravity.pod.orchestrator import PODOrchestrator
from antigravity.integrations.slack import notify_slack


# Add gateway to path if it exists
gateway_path = Path(__file__).parent.parent / "gateway"
if gateway_path.exists():
    sys.path.insert(0, str(gateway_path))


class GatewayBridge:
    """
    Bridge that integrates Antigravity with the existing POD Gateway.

    This allows the Gateway to use Antigravity's AI decision-making
    while maintaining the existing human-in-the-loop approval workflow.
    """

    def __init__(
        self,
        state_file: Optional[str] = None,
        require_human: bool = True,
        dry_run: bool = False,
    ):
        """
        Initialize gateway bridge.

        Args:
            state_file: Path to gateway state file
            require_human: If True, require human approval
            dry_run: If True, don't actually modify gateway state
        """
        self.state_file = state_file or os.environ.get(
            "POD_STATE_FILE",
            "/workspace/gateway/state.json"
        )
        self.require_human = require_human
        self.dry_run = dry_run

        # Initialize POD orchestrator
        self.orchestrator = PODOrchestrator(
            dry_run=dry_run,
            require_human=require_human,
        )

    def process_pending_designs(self) -> Dict[str, Any]:
        """
        Process all pending designs in the gateway.

        Returns:
            Dict with processing summary
        """
        print("\n🔗 Gateway Bridge: Processing pending designs")

        state = self._load_gateway_state()
        if not state:
            print("   No gateway state found")
            return {"processed": 0, "approved": 0, "rejected": 0}

        pending = [
            (design_id, info)
            for design_id, info in state.items()
            if info.get("status") == "pending"
        ]

        print(f"   Found {len(pending)} pending designs")

        approved = 0
        rejected = 0

        for design_id, design_info in pending:
            print(f"\n   Processing: {design_id}")

            image_path = design_info.get("path")
            if not image_path or not Path(image_path).exists():
                print(f"      ⚠️  Image not found: {image_path}")
                continue

            # Process through Antigravity
            result = self.orchestrator.process_design(
                design_path=image_path,
                product_type="hoodie",  # TODO: Make configurable
            )

            if result and result.get("ready_for_publish"):
                # Update gateway state to approved
                if not self.dry_run:
                    self._update_design_status(
                        design_id,
                        "approved",
                        antigravity_result=result
                    )
                approved += 1
                print(f"      ✅ Approved")
            else:
                # Update gateway state to rejected
                if not self.dry_run:
                    self._update_design_status(
                        design_id,
                        "rejected",
                        reason="AI decision: not approved"
                    )
                rejected += 1
                print(f"      ❌ Rejected")

        summary = {
            "processed": len(pending),
            "approved": approved,
            "rejected": rejected,
        }

        notify_slack(
            f"📊 Gateway processing complete:\n"
            f"   Processed: {summary['processed']}\n"
            f"   Approved: {summary['approved']}\n"
            f"   Rejected: {summary['rejected']}"
        )

        return summary

    def enhance_design(
        self,
        design_id: str,
        image_path: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Enhance a design with Antigravity intelligence.

        This can be called by the gateway to get AI recommendations
        without changing the approval status.

        Args:
            design_id: Design ID
            image_path: Path to design image

        Returns:
            Enhancement data or None
        """
        print(f"\n🔗 Enhancing design: {design_id}")

        result = self.orchestrator.process_design(
            design_path=image_path,
            product_type="hoodie",
        )

        if result:
            # Store enhancement data
            enhancement = {
                "design_id": design_id,
                "antigravity_result": result,
                "recommended_action": "approve" if result["ready_for_publish"] else "reject",
                "confidence": result["ai_decision"]["confidence"],
                "risk_level": result["risk_assessment"]["level"],
            }

            return enhancement

        return None

    def _load_gateway_state(self) -> Optional[Dict[str, Any]]:
        """Load gateway state file."""
        try:
            state_path = Path(self.state_file)
            if not state_path.exists():
                return None

            with open(state_path, 'r') as f:
                return json.load(f)

        except Exception as e:
            print(f"Failed to load gateway state: {e}")
            return None

    def _update_design_status(
        self,
        design_id: str,
        status: str,
        **kwargs
    ) -> bool:
        """Update design status in gateway state."""
        try:
            state = self._load_gateway_state()
            if not state:
                return False

            if design_id not in state:
                print(f"Design {design_id} not found in state")
                return False

            # Update status
            state[design_id]["status"] = status

            # Add any additional data
            for key, value in kwargs.items():
                state[design_id][key] = value

            # Write back to file
            state_path = Path(self.state_file)
            state_path.parent.mkdir(parents=True, exist_ok=True)

            with open(state_path, 'w') as f:
                json.dump(state, f, indent=2)

            return True

        except Exception as e:
            print(f"Failed to update design status: {e}")
            return False


def integrate_with_gateway(
    watch_mode: bool = False,
    process_pending: bool = True,
):
    """
    Main integration function.

    Args:
        watch_mode: If True, continuously watch for new designs
        process_pending: If True, process existing pending designs
    """
    print("\n" + "="*70)
    print("🔗 ANTIGRAVITY GATEWAY INTEGRATION")
    print("="*70)

    bridge = GatewayBridge(
        require_human=True,
        dry_run=False,
    )

    if process_pending:
        print("\n📋 Processing pending designs...")
        bridge.process_pending_designs()

    if watch_mode:
        print("\n👁️  Entering watch mode...")
        print("   (This feature requires implementing a file watcher)")
        print("   Press Ctrl+C to stop")
        # TODO: Implement continuous watching
        import time
        try:
            while True:
                time.sleep(60)  # Check every minute
                bridge.process_pending_designs()
        except KeyboardInterrupt:
            print("\n⏹️  Stopped")


if __name__ == "__main__":
    integrate_with_gateway(
        watch_mode=False,
        process_pending=True,
    )
