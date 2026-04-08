from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentRequest:
    flow_name: str
    environment: str
    variables: dict[str, str] | None = None
    capture_mode: str = "failure_only"


@dataclass
class EnvironmentConfig:
    name: str
    base_url: str


@dataclass
class FlowStep:
    action: str
    target: str | None = None
    value: str | None = None
    name: str | None = None


@dataclass
class FlowDefinition:
    name: str
    start_url: str | None
    steps: list[FlowStep]


@dataclass
class StepResult:
    step_index: int
    action: str
    target: str | None
    expected: str | None
    actual: str | None
    status: str
    error_message: str | None = None
    screenshot_path: str | None = None


@dataclass
class EvidenceItem:
    type: str
    path: str
    step_index: int | None = None
    note: str | None = None


@dataclass
class RunResult:
    flow_name: str
    environment: str
    status: str
    started_at: str
    finished_at: str
    steps: list[StepResult] = field(default_factory=list)
    evidence: list[EvidenceItem] = field(default_factory=list)
    summary: str = ""


@dataclass
class QAReport:
    title: str
    status: str
    markdown: str
    json_data: dict[str, Any]
