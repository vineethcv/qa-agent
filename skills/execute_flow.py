from __future__ import annotations

from typing import List

from adapters.vibium_adapter import VibiumAdapter
from agent.models import (
    AgentRequest,
    EvidenceItem,
    FlowDefinition,
    StepResult,
)
from agent.policy import should_capture_screenshot_for_step, status_from_exception
from skills.capture_evidence import capture_screenshot


def execute_flow(
    adapter: VibiumAdapter,
    request: AgentRequest,
    flow: FlowDefinition,
    run_dir: str,
    open_start_url: bool = True,
) -> tuple[list[StepResult], list[EvidenceItem], str]:
    """
    Execute a predefined flow using an existing Vibium adapter/session.

    Returns:
        (step_results, evidence_items, final_status)
    """
    step_results: List[StepResult] = []
    evidence_items: List[EvidenceItem] = []
    final_status = "PASSED"

    if open_start_url and flow.start_url:
        adapter.open(flow.start_url)

    for index, step in enumerate(flow.steps, start=1):
        resolved_target = _resolve_value(step.target, request.variables)
        resolved_value = _resolve_value(step.value, request.variables)

        try:
            step_result = _execute_single_step(
                adapter=adapter,
                step_index=index,
                action=step.action,
                target=resolved_target,
                value=resolved_value,
            )

            if should_capture_screenshot_for_step(
                capture_mode=request.capture_mode,
                action=step.action,
                status=step_result.status,
            ):
                screenshot_path, evidence = capture_screenshot(
                    adapter=adapter,
                    run_dir=run_dir,
                    step_index=index,
                    label=_step_label(step.action, resolved_value),
                    note=f"Captured for step {index} in flow {flow.name}",
                )
                step_result.screenshot_path = screenshot_path
                evidence_items.append(evidence)

            step_results.append(step_result)

            if step_result.status != "PASSED":
                final_status = step_result.status
                break

        except Exception as exc:
            status = status_from_exception(exc)

            screenshot_path = None
            try:
                screenshot_path, evidence = capture_screenshot(
                    adapter=adapter,
                    run_dir=run_dir,
                    step_index=index,
                    label="failure",
                    note=f"Failure on step {index}: {step.action} in flow {flow.name}",
                )
                evidence_items.append(evidence)
            except Exception:
                pass

            step_results.append(
                StepResult(
                    step_index=index,
                    action=step.action,
                    target=resolved_target,
                    expected=_expected_for_step(step.action, resolved_value),
                    actual=None,
                    status=status,
                    error_message=str(exc),
                    screenshot_path=screenshot_path,
                )
            )
            final_status = status
            break

    return step_results, evidence_items, final_status


def _execute_single_step(
    adapter: VibiumAdapter,
    step_index: int,
    action: str,
    target: str | None,
    value: str | None,
) -> StepResult:
    normalized_action = action.strip().lower()

    if normalized_action == "open":
        if not value:
            raise ValueError("Step action 'open' requires a value.")
        adapter.open(value)
        return StepResult(
            step_index=step_index,
            action=normalized_action,
            target=target,
            expected=value,
            actual=value,
            status="PASSED",
        )

    if normalized_action == "click":
        if not target:
            raise ValueError("Step action 'click' requires a target.")
        adapter.click(target)
        return StepResult(
            step_index=step_index,
            action=normalized_action,
            target=target,
            expected=f"Click {target}",
            actual=f"Clicked {target}",
            status="PASSED",
        )

    if normalized_action == "fill":
        if not target:
            raise ValueError("Step action 'fill' requires a target.")
        if value is None:
            raise ValueError("Step action 'fill' requires a value.")
        adapter.fill(target, value)
        return StepResult(
            step_index=step_index,
            action=normalized_action,
            target=target,
            expected=f"Fill {target}",
            actual=f"Filled {target}",
            status="PASSED",
        )

    if normalized_action == "assert_text":
        if not value:
            raise ValueError("Step action 'assert_text' requires a value.")
        ok = adapter.assert_text(value)
        return StepResult(
            step_index=step_index,
            action=normalized_action,
            target=target,
            expected=value,
            actual=value if ok else None,
            status="PASSED" if ok else "FAILED",
            error_message=None if ok else f"Expected text not found: {value}",
        )

    if normalized_action == "screenshot":
        return StepResult(
            step_index=step_index,
            action=normalized_action,
            target=target,
            expected=value or "screenshot",
            actual=value or "screenshot",
            status="PASSED",
        )

    raise ValueError(f"Unsupported action: {action}")


def _resolve_value(raw_value: str | None, variables: dict[str, str] | None) -> str | None:
    if raw_value is None:
        return None

    if not variables:
        return raw_value

    resolved = raw_value
    for key, value in variables.items():
        resolved = resolved.replace(f"${{{key}}}", value)
    return resolved


def _expected_for_step(action: str, value: str | None) -> str | None:
    normalized_action = action.strip().lower()

    if normalized_action == "assert_text":
        return value
    if normalized_action == "open":
        return value
    if normalized_action == "screenshot":
        return value or "screenshot"

    return None


def _step_label(action: str, value: str | None) -> str:
    normalized_action = action.strip().lower()

    if normalized_action == "screenshot" and value:
        return _safe_label(value)

    return normalized_action


def _safe_label(value: str) -> str:
    cleaned = value.strip().lower().replace(" ", "_")
    return "".join(ch for ch in cleaned if ch.isalnum() or ch in ("_", "-"))