from __future__ import annotations

from models import TestCaseBundle


def validate_testcase_bundle(bundle: TestCaseBundle) -> list[str]:
    errors = []

    for case in bundle.test_cases:
        if not case.title.strip():
            errors.append("Test case title cannot be empty.")

        if not case.steps:
            errors.append(f"Test case '{case.title}' has no steps.")

        for step in case.steps:
            if not step.action.strip():
                errors.append(f"Test case '{case.title}' has a step with empty action.")
            if not step.expected_result.strip():
                errors.append(f"Test case '{case.title}' has a step with empty expected result.")

    return errors