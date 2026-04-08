from __future__ import annotations

import json
import os
from dataclasses import asdict

from models import NormalizedSpecBundle


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def _format_summary_markdown(bundle: NormalizedSpecBundle) -> str:
    lines = [f"# Requirement Understanding: {bundle.title}", ""]

    if bundle.summary:
        lines.append("## Summary")
        lines.append(bundle.summary)
        lines.append("")

    if bundle.requirements:
        lines.append("## Requirements")
        for req in bundle.requirements:
            lines.append(f"- {req.description}")
        lines.append("")

    if bundle.ui_elements:
        lines.append("## UI Elements")
        for el in bundle.ui_elements:
            lines.append(f"- {el.name} ({el.element_type})")
        lines.append("")

    if bundle.business_rules:
        lines.append("## Business Rules")
        for rule in bundle.business_rules:
            lines.append(f"- {rule.description}")
        lines.append("")

    if bundle.acceptance_criteria:
        lines.append("## Acceptance Criteria")
        for ac in bundle.acceptance_criteria:
            lines.append(f"- {ac.description}")
        lines.append("")

    return "\n".join(lines).strip()


def _format_ambiguities_markdown(bundle: NormalizedSpecBundle) -> str:
    lines = [f"# Ambiguities: {bundle.title}", ""]

    if not bundle.ambiguities:
        lines.append("No ambiguities detected.")
        return "\n".join(lines)

    for amb in bundle.ambiguities:
        lines.append(f"- ({amb.severity}) {amb.description}")

    return "\n".join(lines)


def write_understanding_artifacts(bundle: NormalizedSpecBundle, output_dir: str) -> dict:
    ensure_dir(output_dir)

    json_path = os.path.join(output_dir, "understanding_summary.json")
    summary_md_path = os.path.join(output_dir, "understanding_summary.md")
    ambiguities_md_path = os.path.join(output_dir, "ambiguities.md")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(asdict(bundle), f, indent=2)

    with open(summary_md_path, "w", encoding="utf-8") as f:
        f.write(_format_summary_markdown(bundle))

    with open(ambiguities_md_path, "w", encoding="utf-8") as f:
        f.write(_format_ambiguities_markdown(bundle))

    return {
        "json_path": json_path,
        "summary_md_path": summary_md_path,
        "ambiguities_md_path": ambiguities_md_path,
    }