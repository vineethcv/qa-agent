from __future__ import annotations

from pathlib import Path

import yaml

from agent.models import FlowDefinition, FlowStep


SUPPORTED_ACTIONS = {
    "open",
    "fill",
    "click",
    "assert_text",
    "screenshot",
}


def load_flow(flow_name: str) -> FlowDefinition:
    """
    Load and validate a flow YAML file from the flows/ directory.

    Example:
        load_flow("login_testing") -> flows/login_testing.yaml
    """
    if not flow_name or not flow_name.strip():
        raise ValueError("flow_name is required")

    path = Path("flows") / f"{flow_name}.yaml"

    if not path.exists():
        raise ValueError(f"Flow file not found: {path}")

    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return _parse_flow(raw, path=str(path))


def _parse_flow(raw: dict, path: str) -> FlowDefinition:
    if not isinstance(raw, dict):
        raise ValueError(f"Invalid flow structure in {path}: expected a mapping/object")

    name = raw.get("name")
    start_url = raw.get("start_url")
    raw_steps = raw.get("steps")

    if not name or not isinstance(name, str):
        raise ValueError(f"Flow '{path}' is missing a valid 'name'")

    if start_url is not None and not isinstance(start_url, str):
        raise ValueError(f"Flow '{path}' has invalid 'start_url'; expected string")

    if not isinstance(raw_steps, list) or not raw_steps:
        raise ValueError(f"Flow '{path}' must contain a non-empty 'steps' list")

    steps = [_parse_step(item, idx + 1, path) for idx, item in enumerate(raw_steps)]

    return FlowDefinition(
        name=name,
        start_url=start_url,
        steps=steps,
    )


def _parse_step(raw_step: dict, step_number: int, path: str) -> FlowStep:
    if not isinstance(raw_step, dict):
        raise ValueError(
            f"Flow '{path}' step {step_number} is invalid: expected a mapping/object"
        )

    action = raw_step.get("action")
    target = raw_step.get("target")
    value = raw_step.get("value")
    name = raw_step.get("name")

    if not action or not isinstance(action, str):
        raise ValueError(f"Flow '{path}' step {step_number} is missing a valid 'action'")

    normalized_action = action.strip().lower()
    if normalized_action not in SUPPORTED_ACTIONS:
        raise ValueError(
            f"Flow '{path}' step {step_number} has unsupported action '{action}'. "
            f"Supported actions: {sorted(SUPPORTED_ACTIONS)}"
        )

    if target is not None and not isinstance(target, str):
        raise ValueError(f"Flow '{path}' step {step_number} has invalid 'target'")

    if value is not None and not isinstance(value, str):
        raise ValueError(f"Flow '{path}' step {step_number} has invalid 'value'")

    if name is not None and not isinstance(name, str):
        raise ValueError(f"Flow '{path}' step {step_number} has invalid 'name'")

    _validate_action_requirements(
        action=normalized_action,
        target=target,
        value=value,
        step_number=step_number,
        path=path,
    )

    return FlowStep(
        action=normalized_action,
        target=target,
        value=value,
        name=name,
    )


def _validate_action_requirements(
    action: str,
    target: str | None,
    value: str | None,
    step_number: int,
    path: str,
) -> None:
    if action == "open":
        if not value:
            raise ValueError(
                f"Flow '{path}' step {step_number}: action 'open' requires 'value'"
            )

    elif action == "click":
        if not target:
            raise ValueError(
                f"Flow '{path}' step {step_number}: action 'click' requires 'target'"
            )

    elif action == "fill":
        if not target:
            raise ValueError(
                f"Flow '{path}' step {step_number}: action 'fill' requires 'target'"
            )
        if value is None:
            raise ValueError(
                f"Flow '{path}' step {step_number}: action 'fill' requires 'value'"
            )

    elif action == "assert_text":
        if not value:
            raise ValueError(
                f"Flow '{path}' step {step_number}: action 'assert_text' requires 'value'"
            )

    elif action == "screenshot":
        # value is optional; if absent, execute_flow will use a generic label
        return