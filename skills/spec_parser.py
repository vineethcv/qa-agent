from __future__ import annotations

from models import ParsedSpec, SpecInput


def parse_spec(spec: SpecInput) -> ParsedSpec:
    """
    Deterministic plain-text parser for V1.
    Current behavior is intentionally simple:
    - title comes from SpecInput
    - summary is the raw text
    - preconditions/actions/expected_outcomes are inferred
      from line prefixes where available
    """
    lines = [line.strip() for line in spec.raw_text.splitlines() if line.strip()]

    preconditions = []
    actions = []
    expected_outcomes = []
    notes = []

    for line in lines:
        lower = line.lower()

        if lower.startswith("precondition:"):
            preconditions.append(line.split(":", 1)[1].strip())
        elif lower.startswith("action:"):
            actions.append(line.split(":", 1)[1].strip())
        elif lower.startswith("expected:"):
            expected_outcomes.append(line.split(":", 1)[1].strip())
        elif lower.startswith("note:"):
            notes.append(line.split(":", 1)[1].strip())

    summary = " ".join(lines).strip()

    return ParsedSpec(
        title=spec.title,
        summary=summary,
        preconditions=preconditions,
        actions=actions,
        expected_outcomes=expected_outcomes,
        notes=notes,
    )