from __future__ import annotations


VALID_CAPTURE_MODES = {"failure_only", "checkpoints", "all_steps"}
CHECKPOINT_ACTIONS = {"assert_text", "screenshot"}


def should_capture_screenshot_for_step(
    capture_mode: str,
    action: str,
    status: str,
) -> bool:
    """
    Decide whether a screenshot should be captured for a step.

    Rules:
    - failure_only: capture only when a step fails
    - checkpoints: capture on failed steps and on checkpoint actions
    - all_steps: capture on every step
    """
    normalized_mode = _normalize_capture_mode(capture_mode)
    normalized_action = action.strip().lower()
    normalized_status = status.strip().upper()

    if normalized_mode == "all_steps":
        return True

    if normalized_mode == "failure_only":
        return normalized_status != "PASSED"

    if normalized_mode == "checkpoints":
        if normalized_status != "PASSED":
            return True
        return normalized_action in CHECKPOINT_ACTIONS

    return False


def status_from_exception(exc: Exception) -> str:
    """
    Map exceptions to a run status.

    Current V1 policy:
    - ValueError -> BLOCKED
    - everything else -> ERROR

    Rationale:
    - ValueError is used in the current flow execution layer for missing
      required inputs, malformed steps, or unsupported actions.
    - unexpected runtime/tool failures should surface as ERROR.
    """
    if isinstance(exc, ValueError):
        return "BLOCKED"

    return "ERROR"


def should_stop_on_step_status(status: str) -> bool:
    """
    Decide whether execution should stop after a step result.

    V1 behavior:
    - stop on anything that is not PASSED
    """
    return status.strip().upper() != "PASSED"


def final_status_from_step_results(step_statuses: list[str]) -> str:
    """
    Compute final status from collected step statuses.

    Precedence:
    ERROR > BLOCKED > FAILED > PASSED
    """
    normalized = [s.strip().upper() for s in step_statuses]

    if any(s == "ERROR" for s in normalized):
        return "ERROR"
    if any(s == "BLOCKED" for s in normalized):
        return "BLOCKED"
    if any(s == "FAILED" for s in normalized):
        return "FAILED"
    return "PASSED"


def _normalize_capture_mode(capture_mode: str) -> str:
    mode = capture_mode.strip().lower()
    if mode not in VALID_CAPTURE_MODES:
        raise ValueError(
            f"Unsupported capture mode: {capture_mode}. "
            f"Expected one of: {sorted(VALID_CAPTURE_MODES)}"
        )
    return mode