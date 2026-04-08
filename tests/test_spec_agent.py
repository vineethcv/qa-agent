from __future__ import annotations

from pathlib import Path

from agent.spec_agent import SpecUnderstandingAgent
from agent.state import AgentState
from models import SpecSource


def test_spec_understanding_agent_runs_end_to_end(tmp_path: Path) -> None:
    state = AgentState(
        title="Spec Agent Test",
        raw_inputs={
            "spec_sources": [
                SpecSource(
                    name="login_spec.txt",
                    source_type="text",
                    content=(
                        "User can login with email and password. "
                        "Email is required. "
                        "Password is required. "
                        "On success the user is redirected to the dashboard. "
                        "If credentials are invalid, an error is displayed."
                    ),
                )
            ],
            "design_images": [],
        },
    )

    agent = SpecUnderstandingAgent()
    result = agent.run(state, output_dir=str(tmp_path))

    tool_names = [entry["tool"] for entry in result.tool_trace]

    assert "read_spec_sources" in tool_names
    assert "extract_requirement_candidates" in tool_names
    assert "extract_table_rules" in tool_names
    assert "inspect_ui_artifact" in tool_names
    assert "merge_understanding" in tool_names
    assert "map_user_flows" in tool_names
    assert "resolve_conflicts" in tool_names
    assert "find_gaps_and_conflicts" in tool_names
    assert "score_confidence" in tool_names
    assert "ask_clarification_questions" in tool_names
    assert "draft_test_scenarios" in tool_names
    assert "validate_test_output" in tool_names
    assert "write_artifacts" in tool_names

    assert result.understanding is not None
    assert result.testcases is not None
    assert isinstance(result.user_flows, list)
    assert isinstance(result.conflicts, list)
    assert isinstance(result.confidence, dict)
    assert isinstance(result.validation, dict)
    assert isinstance(result.artifacts, dict)
    assert "overall" in result.confidence
    assert "is_valid" in result.validation


def test_spec_understanding_agent_writes_artifacts(tmp_path: Path) -> None:
    state = AgentState(
        title="Artifact Write Test",
        raw_inputs={
            "spec_sources": [
                SpecSource(
                    name="signup_spec.txt",
                    source_type="text",
                    content=(
                        "User can sign up with email and password. "
                        "Email is required. "
                        "On success the user should see a welcome page."
                    ),
                )
            ],
            "design_images": [],
        },
    )

    agent = SpecUnderstandingAgent()
    result = agent.run(state, output_dir=str(tmp_path))

    assert "understanding" in result.artifacts
    assert "testcases" in result.artifacts

    for group_paths in result.artifacts.values():
        for _, path in group_paths.items():
            assert Path(path).exists()


def test_spec_understanding_agent_collects_validation_state(tmp_path: Path) -> None:
    state = AgentState(
        title="Validation State Test",
        raw_inputs={
            "spec_sources": [
                SpecSource(
                    name="validation_spec.txt",
                    source_type="text",
                    content=(
                        "User submits a form. "
                        "Name is required. "
                        "If the name is missing, an error is displayed."
                    ),
                )
            ],
            "design_images": [],
        },
    )

    agent = SpecUnderstandingAgent()
    result = agent.run(state, output_dir=str(tmp_path))

    assert "is_valid" in result.validation
    assert "error_count" in result.validation
    assert "errors" in result.validation
    assert isinstance(result.validation["errors"], list)