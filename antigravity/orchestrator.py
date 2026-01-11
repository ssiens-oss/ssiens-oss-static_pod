"""Main Antigravity orchestrator for multi-model AI decision-making."""

import uuid
import time
from typing import List, Optional, Dict, Any
from antigravity.models import SubTask, ModelResponse, ExecutionPlan, Role
from antigravity.router import select_model
from antigravity.uncertainty import should_escalate, confidence_mean, disagreement_score
from antigravity.voting import weighted_consensus
from antigravity.memory.vector import VectorMemory
from antigravity.memory.provenance import record_provenance
from antigravity.integrations.slack import notify_slack
from antigravity.integrations.email import notify_email

# LLM imports
from antigravity.llms.gpt import call as call_gpt
from antigravity.llms.claude import call as call_claude
from antigravity.llms.grok import call as call_grok


# Model registry
MODEL_REGISTRY = {
    "gpt": call_gpt,
    "claude": call_claude,
    "grok": call_grok,
}


class AntigravityOrchestrator:
    """
    Multi-model AI orchestrator with safety, verification, and memory.

    This is the core control plane that:
    - Decomposes tasks into subtasks
    - Routes subtasks to appropriate models
    - Detects uncertainty and disagreement
    - Escalates to humans when needed
    - Records all decisions for learning
    """

    def __init__(
        self,
        dry_run: bool = False,
        require_human: bool = False,
        use_memory: bool = True,
        memory_persist_dir: Optional[str] = None,
    ):
        """
        Initialize orchestrator.

        Args:
            dry_run: If True, plan but don't execute
            require_human: If True, always require human approval
            use_memory: If True, use vector memory for learning
            memory_persist_dir: Directory to persist memory
        """
        self.dry_run = dry_run
        self.require_human = require_human
        self.responses: List[ModelResponse] = []
        self.current_task: Optional[str] = None

        # Initialize memory
        if use_memory:
            try:
                self.memory = VectorMemory(
                    collection_name="pod_decisions",
                    persist_dir=memory_persist_dir,
                )
            except Exception as e:
                print(f"Warning: Vector memory not available: {e}")
                self.memory = None
        else:
            self.memory = None

    def decompose(self, task: str) -> List[SubTask]:
        """
        Decompose a task into subtasks for different models.

        Args:
            task: Task description

        Returns:
            List of subtasks
        """
        # For POD tasks, we typically want:
        # 1. Analysis (understand what we're doing)
        # 2. Safety check (is this risky?)
        # 3. Copy generation (if needed)
        # 4. Pricing decision (if needed)

        subtasks = [
            SubTask(
                role=Role.ANALYSIS,
                prompt=f"Analyze this POD task and provide strategic guidance:\n{task}",
            ),
            SubTask(
                role=Role.SAFETY,
                prompt=f"Evaluate safety and risk for this POD task:\n{task}\n\n"
                       f"Check for:\n"
                       f"- Platform policy violations\n"
                       f"- Copyright/trademark issues\n"
                       f"- Pricing risks\n"
                       f"- Reputation risks\n\n"
                       f"Respond with PROCEED if safe, or BLOCK with reason if risky.",
            ),
        ]

        # Check if task involves pricing
        if any(word in task.lower() for word in ["price", "pricing", "cost", "$"]):
            subtasks.append(
                SubTask(
                    role=Role.PRICING,
                    prompt=f"Recommend optimal pricing strategy for:\n{task}",
                )
            )

        # Check if task involves copywriting
        if any(word in task.lower() for word in ["copy", "description", "headline", "title"]):
            subtasks.append(
                SubTask(
                    role=Role.COPY,
                    prompt=f"Generate compelling marketing copy for:\n{task}",
                )
            )

        return subtasks

    def run_llms(self, subtasks: List[SubTask]) -> None:
        """
        Execute subtasks across models and collect responses.

        Args:
            subtasks: List of subtasks to execute
        """
        self.responses = []

        for subtask in subtasks:
            model_name = select_model(subtask.role)

            if model_name == "none":
                continue

            if model_name not in MODEL_REGISTRY:
                print(f"Warning: Model '{model_name}' not available")
                continue

            try:
                print(f"🤖 Consulting {model_name} for {subtask.role.value}...")

                content, confidence = MODEL_REGISTRY[model_name](subtask.prompt)

                response = ModelResponse(
                    model=model_name,
                    role=subtask.role,
                    content=content,
                    confidence=confidence,
                )

                self.responses.append(response)
                print(f"   ✓ {model_name}: {confidence:.2%} confidence")

            except Exception as e:
                print(f"Error calling {model_name}: {e}")
                # Continue with other models even if one fails

    def check_memory(self, task: str) -> Optional[Dict[str, Any]]:
        """
        Check if we've seen a similar task before.

        Args:
            task: Task description

        Returns:
            Previous similar decision if found
        """
        if not self.memory:
            return None

        try:
            has_seen, similar = self.memory.has_seen_similar(
                task,
                similarity_threshold=0.85
            )

            if has_seen:
                print(f"📚 Found similar past decision (similarity: {similar['similarity']:.2%})")
                return similar

        except Exception as e:
            print(f"Memory check failed: {e}")

        return None

    def synthesize(self) -> Optional[ExecutionPlan]:
        """
        Synthesize model responses into an execution plan.

        Returns:
            ExecutionPlan if safe to proceed, None otherwise
        """
        if not self.responses:
            notify_slack("⚠️ No model responses received")
            return None

        # Check for safety blocks
        safety_blocks = [
            r for r in self.responses
            if r.role == Role.SAFETY and "BLOCK" in r.content.upper()
        ]

        if safety_blocks:
            reason = safety_blocks[0].content
            print(f"🛑 Safety model blocked execution: {reason}")
            notify_slack(f"🛑 Execution blocked by safety check:\n{reason}")
            notify_email(
                subject="POD Action Blocked by Safety Check",
                body=f"Task: {self.current_task}\n\nReason: {reason}"
            )
            return None

        # Check uncertainty and escalation
        needs_escalation, escalation_reason = should_escalate(self.responses)

        if needs_escalation or self.require_human:
            print(f"\n⚠️  HUMAN REVIEW REQUIRED")
            print(f"Reason: {escalation_reason}")
            print(f"\nModel Responses:")
            for r in self.responses:
                print(f"  {r.model} ({r.role.value}): {r.content[:100]}...")

            # Calculate statistics
            avg_conf = confidence_mean(self.responses)
            disagreement = disagreement_score(self.responses)

            notify_slack(
                f"🚨 Human review required\n\n"
                f"Task: {self.current_task}\n"
                f"Reason: {escalation_reason}\n"
                f"Avg Confidence: {avg_conf:.2%}\n"
                f"Disagreement Score: {disagreement:.3f}"
            )

            if not self.dry_run:
                approval = input("\n👤 Approve execution? (yes/no): ").strip().lower()
                if approval != "yes":
                    print("❌ Execution rejected by human")
                    return None
                print("✅ Execution approved")

        # Build consensus
        consensus_content, total_confidence = weighted_consensus(self.responses)

        print(f"\n📊 Consensus (confidence: {total_confidence:.2%})")
        print(f"   {consensus_content[:200]}...")

        # For now, return a placeholder execution plan
        # This will be filled in by the POD-specific orchestrator
        plan = ExecutionPlan(
            actions=[],
            metadata={
                "task": self.current_task,
                "consensus": consensus_content,
                "confidence": total_confidence,
                "model_count": len(self.responses),
            }
        )

        return plan

    def execute(self, task: str) -> Optional[ExecutionPlan]:
        """
        Main execution flow.

        Args:
            task: Task description

        Returns:
            ExecutionPlan if successful, None otherwise
        """
        self.current_task = task
        print(f"\n🚀 Antigravity Orchestrator")
        print(f"Task: {task}")
        print(f"Dry run: {self.dry_run}")
        print(f"Require human: {self.require_human}")

        # Check memory first
        similar_decision = self.check_memory(task)
        if similar_decision:
            print(f"Previous decision: {similar_decision['document'][:100]}...")
            # Could use this to inform current decision

        # Decompose task
        print(f"\n📋 Decomposing task...")
        subtasks = self.decompose(task)
        print(f"   Created {len(subtasks)} subtasks")

        # Run LLMs
        print(f"\n🧠 Consulting models...")
        self.run_llms(subtasks)

        # Synthesize
        print(f"\n⚙️  Synthesizing responses...")
        plan = self.synthesize()

        if not plan:
            print("❌ No execution plan generated")
            return None

        # Record provenance
        decision_id = record_provenance(
            task=task,
            responses=self.responses,
            plan=plan,
            outcome="planned" if self.dry_run else "executing",
        )
        print(f"\n📝 Decision recorded: {decision_id}")

        # Store in memory
        if self.memory:
            try:
                self.memory.remember(
                    text=task,
                    id=decision_id,
                    metadata={
                        "confidence": plan.metadata.get("confidence", 0.0),
                        "timestamp": time.time(),
                    }
                )
                print(f"💾 Stored in memory")
            except Exception as e:
                print(f"Memory storage failed: {e}")

        return plan
