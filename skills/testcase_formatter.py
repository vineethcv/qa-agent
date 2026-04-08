from __future__ import annotations

from models import TestCaseBundle


def format_testcases_as_text(bundle: TestCaseBundle) -> str:
    lines = [f"Test Case Bundle: {bundle.source_title}", ""]

    if bundle.warnings:
        lines.append("Warnings:")
        for warning in bundle.warnings:
            lines.append(f"- {warning}")
        lines.append("")

    for index, case in enumerate(bundle.test_cases, start=1):
        lines.append(f"{index}. {case.title}")
        lines.append(f"Objective: {case.objective}")
        lines.append(f"Priority: {case.priority}")
        lines.append(f"Tags: {', '.join(case.tags)}")

        if case.preconditions:
            lines.append("Preconditions:")
            for precondition in case.preconditions:
                lines.append(f"- {precondition}")

        lines.append("Steps:")
        for step in case.steps:
            lines.append(f"{step.step_number}. Action: {step.action}")
            lines.append(f"   Expected: {step.expected_result}")

        lines.append("")

    return "\n".join(lines).strip()


def format_testcases_as_markdown(bundle: TestCaseBundle) -> str:
    lines = [f"# Test Case Bundle: {bundle.source_title}", ""]

    if bundle.warnings:
        lines.append("## Warnings")
        for warning in bundle.warnings:
            lines.append(f"- {warning}")
        lines.append("")

    for case in bundle.test_cases:
        lines.append(f"## {case.title}")
        lines.append(f"**Objective:** {case.objective}")
        lines.append(f"**Priority:** {case.priority}")
        lines.append(f"**Tags:** {', '.join(case.tags)}")
        lines.append("")

        if case.preconditions:
            lines.append("### Preconditions")
            for precondition in case.preconditions:
                lines.append(f"- {precondition}")
            lines.append("")

        lines.append("### Steps")
        for step in case.steps:
            lines.append(f"{step.step_number}. **Action:** {step.action}")
            lines.append(f"   - **Expected:** {step.expected_result}")
        lines.append("")

    return "\n".join(lines).strip()