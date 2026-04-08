from __future__ import annotations

from models import (
    GeneratedTestCase,
    NormalizedSpecBundle,
    SourceReference,
    TestCaseBundle,
    TestStep,
)


def _collect_source_refs(items) -> list[SourceReference]:
    refs: list[SourceReference] = []
    for item in items:
        refs.extend(item.source_refs)
    return refs


def _build_happy_path_case(bundle: NormalizedSpecBundle) -> GeneratedTestCase:
    steps = []
    relevant_requirements = [
        requirement
        for requirement in bundle.requirements
        if requirement.category in {"functional", "navigation", "ui", "state"}
    ]

    step_number = 1
    for requirement in relevant_requirements:
        steps.append(
            TestStep(
                step_number=step_number,
                action=f"Validate requirement: {requirement.description}",
                expected_result="System behavior matches the understood requirement",
            )
        )
        step_number += 1

    if not steps:
        steps.append(
            TestStep(
                step_number=1,
                action="Review normalized requirement bundle manually",
                expected_result="Bundle contains enough understood detail to derive executable QA tests",
            )
        )

    return GeneratedTestCase(
        title=f"{bundle.title} - Happy Path",
        objective=f"Validate the primary successful flow for {bundle.title}",
        preconditions=[],
        steps=steps,
        priority="High",
        tags=["happy_path", "regression"],
        source_refs=_collect_source_refs(relevant_requirements),
    )


def _build_validation_case(bundle: NormalizedSpecBundle) -> GeneratedTestCase:
    steps = []
    step_number = 1

    for rule in bundle.business_rules:
        steps.append(
            TestStep(
                step_number=step_number,
                action=f"Validate business rule: {rule.description}",
                expected_result="System enforces the rule correctly",
            )
        )
        step_number += 1

    if not steps:
        steps.append(
            TestStep(
                step_number=1,
                action="Submit incomplete or invalid input",
                expected_result="System prevents invalid submission and shows validation feedback",
            )
        )

    return GeneratedTestCase(
        title=f"{bundle.title} - Validation",
        objective=f"Validate rules and input handling for {bundle.title}",
        preconditions=[],
        steps=steps,
        priority="High",
        tags=["validation", "negative", "regression"],
        source_refs=_collect_source_refs(bundle.business_rules),
    )


def _build_negative_case(bundle: NormalizedSpecBundle) -> GeneratedTestCase:
    steps = []
    step_number = 1

    for ambiguity in bundle.ambiguities:
        steps.append(
            TestStep(
                step_number=step_number,
                action=f"Probe ambiguous behavior area: {ambiguity.description}",
                expected_result="System behavior is clarified, rejected safely, or documented for follow-up",
            )
        )
        step_number += 1

    if not steps:
        steps.append(
            TestStep(
                step_number=1,
                action="Attempt an invalid or unauthorized user path",
                expected_result="System rejects the action safely with appropriate feedback",
            )
        )

    return GeneratedTestCase(
        title=f"{bundle.title} - Negative Path",
        objective=f"Validate unsuccessful or unclear flows for {bundle.title}",
        preconditions=[],
        steps=steps,
        priority="Medium",
        tags=["negative", "error_handling"],
        source_refs=_collect_source_refs(bundle.ambiguities),
    )


def _build_ui_presence_case(bundle: NormalizedSpecBundle) -> GeneratedTestCase:
    steps = []
    step_number = 1

    for element in bundle.ui_elements:
        steps.append(
            TestStep(
                step_number=step_number,
                action=f"Verify UI element is present and visible: {element.name}",
                expected_result=f"Element '{element.name}' is displayed as expected",
            )
        )
        step_number += 1

    if not steps:
        steps.append(
            TestStep(
                step_number=1,
                action="Review expected UI inventory manually",
                expected_result="Expected UI elements are identified for the feature",
            )
        )

    return GeneratedTestCase(
        title=f"{bundle.title} - UI Presence",
        objective=f"Validate expected UI elements for {bundle.title}",
        preconditions=[],
        steps=steps,
        priority="Medium",
        tags=["ui", "visibility", "regression"],
        source_refs=_collect_source_refs(bundle.ui_elements),
    )


def _build_navigation_state_case(bundle: NormalizedSpecBundle) -> GeneratedTestCase:
    steps = []
    relevant_requirements = [
        requirement
        for requirement in bundle.requirements
        if requirement.category in {"navigation", "state", "ui"}
    ]

    step_number = 1
    for requirement in relevant_requirements:
        steps.append(
            TestStep(
                step_number=step_number,
                action=f"Validate navigation or state behavior: {requirement.description}",
                expected_result="System transitions and screen state match the understood behavior",
            )
        )
        step_number += 1

    if not steps:
        steps.append(
            TestStep(
                step_number=1,
                action="Trigger a key user transition in the feature",
                expected_result="System lands in the correct screen or state",
            )
        )

    return GeneratedTestCase(
        title=f"{bundle.title} - Navigation and State",
        objective=f"Validate navigation and UI state behavior for {bundle.title}",
        preconditions=[],
        steps=steps,
        priority="Medium",
        tags=["navigation", "state", "ui"],
        source_refs=_collect_source_refs(relevant_requirements),
    )


def generate_testcases_from_bundle(bundle: NormalizedSpecBundle) -> TestCaseBundle:
    warnings = [ambiguity.description for ambiguity in bundle.ambiguities]

    test_cases = [
        _build_happy_path_case(bundle),
        _build_validation_case(bundle),
        _build_negative_case(bundle),
        _build_ui_presence_case(bundle),
        _build_navigation_state_case(bundle),
    ]

    return TestCaseBundle(
        source_title=bundle.title,
        test_cases=test_cases,
        warnings=warnings,
    )