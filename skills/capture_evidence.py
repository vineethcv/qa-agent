from __future__ import annotations

from datetime import datetime
from pathlib import Path

from adapters.vibium_adapter import VibiumAdapter
from agent.models import EvidenceItem


def create_run_directory(base_dir: str, flow_name: str, environment: str) -> str:
    """
    Create a timestamped run directory for evidence artifacts.

    Example:
        evidence/2026-03-18_101530_login_testing_testing
    """
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    run_dir = Path(base_dir) / f"{timestamp}_{_safe_name(flow_name)}_{_safe_name(environment)}"
    run_dir.mkdir(parents=True, exist_ok=True)
    return str(run_dir)


def capture_screenshot(
    adapter: VibiumAdapter,
    run_dir: str,
    step_index: int,
    label: str,
    note: str | None = None,
) -> tuple[str, EvidenceItem]:
    """
    Capture a screenshot through the adapter and return:
    - the saved path
    - an EvidenceItem record
    """
    filename = f"step_{step_index:02d}_{_safe_name(label)}.png"
    path = Path(run_dir) / filename

    saved_path = adapter.screenshot(str(path))

    evidence = EvidenceItem(
        type="screenshot",
        path=saved_path,
        step_index=step_index,
        note=note,
    )
    return saved_path, evidence


def write_run_result_json(run_dir: str, json_text: str) -> str:
    """
    Save final machine-readable result into the run folder.
    """
    path = Path(run_dir) / "run_result.json"
    path.write_text(json_text, encoding="utf-8")
    return str(path)


def write_report_markdown(run_dir: str, markdown_text: str) -> str:
    """
    Save final human-readable report into the run folder.
    """
    path = Path(run_dir) / "report.md"
    path.write_text(markdown_text, encoding="utf-8")
    return str(path)


def _safe_name(value: str) -> str:
    cleaned = value.strip().lower().replace(" ", "_")
    return "".join(ch for ch in cleaned if ch.isalnum() or ch in ("_", "-"))