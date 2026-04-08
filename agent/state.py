from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from models import NormalizedSpecBundle, TestCaseBundle


@dataclass
class AgentState:
    title: str
    raw_inputs: dict[str, Any] = field(default_factory=dict)

    understanding: NormalizedSpecBundle | None = None
    testcases: TestCaseBundle | None = None

    open_questions: list[str] = field(default_factory=list)
    findings: list[str] = field(default_factory=list)
    decisions: list[str] = field(default_factory=list)
    tool_trace: list[dict[str, Any]] = field(default_factory=list)