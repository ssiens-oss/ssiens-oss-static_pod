"""Model routing logic for task distribution."""

from antigravity.models import Role


def select_model(role: Role) -> str:
    """
    Select the best model for a given role.

    Strategy:
    - analysis: GPT (systems thinking, architecture)
    - copy: GPT (creative writing, marketing)
    - safety: Claude (safety-aware, policy checking)
    - pricing: GPT (market analysis, optimization)
    - execution: none (Playwright handles this)
    """
    routing_table = {
        Role.ANALYSIS: "gpt",
        Role.COPY: "gpt",
        Role.SAFETY: "claude",
        Role.PRICING: "gpt",
        Role.EXECUTION: "none",
    }
    return routing_table.get(role, "gpt")


def should_use_multiple_models(task_complexity: str) -> bool:
    """Determine if multiple models should be consulted."""
    return task_complexity in ["high", "critical"]
