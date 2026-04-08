from __future__ import annotations

import json
from datetime import datetime
from typing import List

from agent.models import EvidenceItem, QAReport, StepResult
from skills.capture_evidence import (
    write_report_markdown,
    write_run_result_json,
)


def write_report(
    flow_name: str,
    environment: str,
    status: str,
    step_results: List[StepResult],
    evidence_items: List[EvidenceItem],
    run_dir: str,
) -> QAReport:
    """
    Build both:
    - machine-readable JSON
    - human-readable Markdown

    Also saves both into the run directory.
    """

    json_data = _build_json(
        flow_name=flow_name,
        environment=environment,
        status=status,
        step_results=step_results,
        evidence_items=evidence_items,
    )

    markdown = _build_markdown(
        flow_name=flow_name,
        environment=environment,
        status=status,
        step_results=step_results,
        evidence_items=evidence_items,
    )

    # Persist artifacts
    write_run_result_json(run_dir, json.dumps(json_data, indent=2))
    write_report_markdown(run_dir, markdown)

    return QAReport(
        title=f"{flow_name} ({environment})",
        status=status,
        markdown=markdown,
        json_data=json_data,
    )


# ----------------------------
# JSON builder
# ----------------------------

def _build_json(
    flow_name: str,
    environment: str,
    status: str,
    step_results: List[StepResult],
    evidence_items: List[EvidenceItem],
) -> dict:
    return {
        "flow_name": flow_name,
        "environment": environment,
        "status": status,
        "generated_at": datetime.utcnow().isoformat(),
        "steps": [
            {
                "step_index": s.step_index,
                "action": s.action,
                "target": s.target,
                "expected": s.expected,
                "actual": s.actual,
                "status": s.status,
                "error_message": s.error_message,
                "screenshot": s.screenshot_path,
            }
            for s in step_results
        ],
        "evidence": [
            {
                "type": e.type,
                "path": e.path,
                "step_index": e.step_index,
                "note": e.note,
            }
            for e in evidence_items
        ],
    }


# ----------------------------
# Markdown builder
# ----------------------------

def _build_markdown(
    flow_name: str,
    environment: str,
    status: str,
    step_results: List[StepResult],
    evidence_items: List[EvidenceItem],
) -> str:
    lines: List[str] = []

    lines.append(f"# QA Report")
    lines.append("")
    lines.append(f"**Flow:** {flow_name}")
    lines.append(f"**Environment:** {environment}")
    lines.append(f"**Status:** {status}")
    lines.append("")

    # Step results
    lines.append("## Step Results")
    lines.append("")

    for s in step_results:
        line = f"{s.step_index}. {s.action.upper()}"

        if s.target:
            line += f" ({s.target})"

        line += f" — {s.status}"

        lines.append(line)

        if s.error_message:
            lines.append(f"   - Error: {s.error_message}")

    lines.append("")

    # Expected vs Actual (only for failures)
    failure_steps = [s for s in step_results if s.status != "PASSED"]

    if failure_steps:
        lines.append("## Failures")
        lines.append("")

        for s in failure_steps:
            lines.append(f"### Step {s.step_index} — {s.action.upper()}")
            lines.append("")

            if s.expected:
                lines.append(f"**Expected:** {s.expected}")

            if s.actual:
                lines.append(f"**Actual:** {s.actual}")
            else:
                lines.append("**Actual:** Not observed")

            if s.error_message:
                lines.append(f"**Error:** {s.error_message}")

            if s.screenshot_path:
                lines.append(f"**Evidence:** {s.screenshot_path}")

            lines.append("")

    # Evidence section
    if evidence_items:
        lines.append("## Evidence")
        lines.append("")

        for e in evidence_items:
            line = f"- {e.type}: {e.path}"
            if e.note:
                line += f" ({e.note})"
            lines.append(line)

        lines.append("")

    # Conclusion
    lines.append("## Conclusion")
    lines.append("")
    lines.append(_build_conclusion(status, flow_name))
    lines.append("")

    return "\n".join(lines)


def _build_conclusion(status: str, flow_name: str) -> str:
    status = status.upper()

    if status == "PASSED":
        return f"The `{flow_name}` flow executed successfully with all validations passing."

    if status == "FAILED":
        return f"The `{flow_name}` flow did not meet expected behavior. Review failed steps and evidence."

    if status == "BLOCKED":
        return f"The `{flow_name}` flow could not be completed due to missing configuration or invalid setup."

    if status == "ERROR":
        return f"The `{flow_name}` flow encountered an unexpected error during execution."

    return f"The `{flow_name}` flow finished with status: {status}."