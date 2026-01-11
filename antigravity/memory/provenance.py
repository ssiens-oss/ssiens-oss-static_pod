"""Decision provenance tracking for audit trails."""

import json
import uuid
import time
from pathlib import Path
from typing import List, Optional, Dict, Any
from antigravity.models import ModelResponse, ExecutionPlan


def record_provenance(
    task: str,
    responses: List[ModelResponse],
    plan: Optional[ExecutionPlan],
    outcome: Optional[str] = None,
    log_file: str = "provenance.jsonl",
    metadata: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Record decision provenance for audit trail.

    Args:
        task: Task description
        responses: Model responses
        plan: Execution plan (if any)
        outcome: Outcome of execution (if completed)
        log_file: Path to log file
        metadata: Optional additional metadata

    Returns:
        Decision ID
    """
    decision_id = str(uuid.uuid4())

    entry = {
        "id": decision_id,
        "timestamp": time.time(),
        "task": task,
        "responses": [r.dict() for r in responses],
        "plan": plan.dict() if plan else None,
        "outcome": outcome,
        "metadata": metadata or {},
    }

    try:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        with open(log_path, "a") as f:
            f.write(json.dumps(entry) + "\n")

    except Exception as e:
        print(f"Failed to record provenance: {e}")

    return decision_id


def load_provenance(
    log_file: str = "provenance.jsonl",
    decision_id: Optional[str] = None,
    limit: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    Load provenance records.

    Args:
        log_file: Path to log file
        decision_id: Optional specific decision ID to load
        limit: Optional limit on number of records

    Returns:
        List of provenance records
    """
    try:
        log_path = Path(log_file)
        if not log_path.exists():
            return []

        records = []
        with open(log_path, "r") as f:
            for line in f:
                try:
                    record = json.loads(line.strip())

                    # Filter by decision_id if specified
                    if decision_id and record.get("id") != decision_id:
                        continue

                    records.append(record)

                    # Check limit
                    if limit and len(records) >= limit:
                        break

                except json.JSONDecodeError:
                    continue

        return records

    except Exception as e:
        print(f"Failed to load provenance: {e}")
        return []


def get_decision_by_id(
    decision_id: str,
    log_file: str = "provenance.jsonl",
) -> Optional[Dict[str, Any]]:
    """
    Get a specific decision by ID.

    Args:
        decision_id: Decision ID to look up
        log_file: Path to log file

    Returns:
        Decision record or None
    """
    records = load_provenance(log_file=log_file, decision_id=decision_id)
    return records[0] if records else None


def get_recent_decisions(
    count: int = 10,
    log_file: str = "provenance.jsonl",
) -> List[Dict[str, Any]]:
    """
    Get recent decisions.

    Args:
        count: Number of recent decisions to retrieve
        log_file: Path to log file

    Returns:
        List of recent decision records
    """
    try:
        log_path = Path(log_file)
        if not log_path.exists():
            return []

        # Read file in reverse to get most recent
        with open(log_path, "r") as f:
            lines = f.readlines()

        records = []
        for line in reversed(lines):
            try:
                record = json.loads(line.strip())
                records.append(record)
                if len(records) >= count:
                    break
            except json.JSONDecodeError:
                continue

        return records

    except Exception as e:
        print(f"Failed to load recent decisions: {e}")
        return []


def analyze_provenance(
    log_file: str = "provenance.jsonl",
) -> Dict[str, Any]:
    """
    Analyze provenance data for insights.

    Args:
        log_file: Path to log file

    Returns:
        Analysis dict with stats
    """
    records = load_provenance(log_file=log_file)

    if not records:
        return {
            "total_decisions": 0,
            "success_rate": 0.0,
            "avg_confidence": 0.0,
        }

    total = len(records)
    successful = sum(1 for r in records if r.get("outcome") == "success")

    # Calculate average confidence
    all_confidences = []
    for r in records:
        for resp in r.get("responses", []):
            all_confidences.append(resp.get("confidence", 0.0))

    avg_confidence = sum(all_confidences) / len(all_confidences) if all_confidences else 0.0

    # Model usage stats
    model_usage = {}
    for r in records:
        for resp in r.get("responses", []):
            model = resp.get("model", "unknown")
            model_usage[model] = model_usage.get(model, 0) + 1

    return {
        "total_decisions": total,
        "successful": successful,
        "failed": total - successful,
        "success_rate": successful / total if total > 0 else 0.0,
        "avg_confidence": avg_confidence,
        "model_usage": model_usage,
    }
