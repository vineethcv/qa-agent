from __future__ import annotations

from models import (
    GeneratedTestCase,
    SpecInput,
    TestCaseBundle,
    TestStep,
)
from skills.spec_parser import parse_spec


def _build_happy_path_case(spec_title: str, parsed) -> GeneratedTestCase:
    steps = []

    if parsed.actions and parsed.expected_outcomes:
        for index, action in enumerate(parsed.actions, start=1):
            expected = (
                parsed.expected_outcomes[min(index - 1, len(parsed.expected_outcomes) - 1)]
                if parsed.expected_outcomes
                else "System behaves as expected"
            )
            steps.append(TestStep(
                step_number=index,
                action=action,
                expected_result=expected
            ))
    else:
        steps.append(TestStep(
            step_number=1,
            action="Review specification manually",
            expected_result="Specification contains enough detail to derive test steps"
        ))

    return GeneratedTestCase(
        title=f"{spec_title} - Happy Path",
        objective=f"Validate the primary successful flow for {spec_title}",
        preconditions=parsed.preconditions,
        steps=steps,
        priority="High",
        tags=["happy_path", "regression"],
    )


def generate_testcases(spec: SpecInput) -> TestCaseBundle:
    parsed = parse_spec(spec)

    happy_path = _build_happy_path_case(spec.title, parsed)

    warnings = []
    if not parsed.actions:
        warnings.append("No explicit actions found in spec.")
    if not parsed.expected_outcomes:
        warnings.append("No explicit expected outcomes found in spec.")

    return TestCaseBundle(
        source_title=spec.title,
        test_cases=[happy_path],
        warnings=warnings,
    )