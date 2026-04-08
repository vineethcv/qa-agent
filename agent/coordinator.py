from __future__ import annotations

from pathlib import Path

import yaml

from adapters.vibium_adapter import VibiumAdapter
from agent.models import AgentRequest, EnvironmentConfig, QAReport
from skills.capture_evidence import create_run_directory
from skills.execute_flow import execute_flow
from skills.load_flow import load_flow
from skills.write_report import write_report


def run_agent(request: AgentRequest) -> QAReport:
    """
    Main orchestration entrypoint for QA Agent V1.

    Session-preserving behavior:
    - one Vibium adapter/session per request
    - multiple flows can run in sequence in the same session
    """
    _validate_request(request)

    environment = _load_environment_config(request.environment)
    flow_names = _resolve_flow_chain(request.flow_name)

    flows = [load_flow(flow_name) for flow_name in flow_names]

    run_dir = create_run_directory(
        base_dir="evidence",
        flow_name="_then_".join(flow_names),
        environment=environment.name,
    )

    adapter = VibiumAdapter(base_url=environment.base_url)

    all_step_results = []
    all_evidence_items = []
    final_status = "PASSED"

    try:
        adapter.start()

        for idx, flow in enumerate(flows):
            step_results, evidence_items, flow_status = execute_flow(
                adapter=adapter,
                request=request,
                flow=flow,
                run_dir=run_dir,
                open_start_url=True,
            )

            all_step_results.extend(step_results)
            all_evidence_items.extend(evidence_items)

            if flow_status != "PASSED":
                final_status = flow_status
                break

    finally:
        try:
            adapter.close()
        except Exception:
            pass

    report = write_report(
        flow_name=" -> ".join(flow_names),
        environment=environment.name,
        status=final_status,
        step_results=all_step_results,
        evidence_items=all_evidence_items,
        run_dir=run_dir,
    )

    return report


def _resolve_flow_chain(flow_name: str) -> list[str]:
    """
    Support both:
    - single flow: login_testing
    - chained flow alias: login_and_post_login_testing
    """
    normalized = flow_name.strip()

    if normalized == "login_and_post_login_testing":
        return ["login_testing", "post_login_navigation_testing"]

    return [normalized]


def _validate_request(request: AgentRequest) -> None:
    if not request.flow_name or not request.flow_name.strip():
        raise ValueError("flow_name is required")

    if not request.environment or not request.environment.strip():
        raise ValueError("environment is required")

    if not request.capture_mode or not request.capture_mode.strip():
        raise ValueError("capture_mode is required")


def _load_environment_config(environment_name: str) -> EnvironmentConfig:
    config_path = Path("config") / "environments.yaml"

    if not config_path.exists():
        raise ValueError(f"Environment config file not found: {config_path}")

    raw = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}

    if environment_name not in raw:
        available = ", ".join(sorted(raw.keys())) if raw else "none"
        raise ValueError(
            f"Environment '{environment_name}' not found in {config_path}. "
            f"Available: {available}"
        )

    env_data = raw[environment_name] or {}
    base_url = env_data.get("base_url")

    if not base_url:
        raise ValueError(
            f"Environment '{environment_name}' is missing required field 'base_url'"
        )

    return EnvironmentConfig(
        name=environment_name,
        base_url=base_url,
    )