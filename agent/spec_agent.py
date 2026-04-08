from __future__ import annotations

from agent.state import AgentState
from agent.tools.spec_tools import (
    AskClarificationQuestionsTool,
    DraftTestScenariosTool,
    ExtractRequirementCandidatesTool,
    ExtractTableRulesTool,
    FindGapsAndConflictsTool,
    InspectUiArtifactTool,
    MapUserFlowsTool,
    MergeUnderstandingTool,
    ReadSpecSourcesTool,
    ResolveConflictsTool,
    ScoreConfidenceTool,
    ValidateTestOutputTool,
    WriteArtifactsTool,
)


class SpecUnderstandingAgent:
    def __init__(self) -> None:
        self.read_spec_sources = ReadSpecSourcesTool()
        self.extract_requirement_candidates = ExtractRequirementCandidatesTool()
        self.extract_table_rules = ExtractTableRulesTool()
        self.inspect_ui_artifact = InspectUiArtifactTool()
        self.merge_understanding = MergeUnderstandingTool()
        self.map_user_flows = MapUserFlowsTool()
        self.resolve_conflicts = ResolveConflictsTool()
        self.find_gaps_and_conflicts = FindGapsAndConflictsTool()
        self.score_confidence = ScoreConfidenceTool()
        self.ask_clarification_questions = AskClarificationQuestionsTool()
        self.draft_test_scenarios = DraftTestScenariosTool()
        self.validate_test_output = ValidateTestOutputTool()
        self.write_artifacts = WriteArtifactsTool()

    def run(self, state: AgentState, *, output_dir: str | None = None) -> AgentState:
        state = self.read_spec_sources.run(state)
        state = self.extract_requirement_candidates.run(state)
        state = self.extract_table_rules.run(state)
        state = self.inspect_ui_artifact.run(state)
        state = self.merge_understanding.run(state)
        state = self.map_user_flows.run(state)
        state = self.resolve_conflicts.run(state)
        state = self.find_gaps_and_conflicts.run(state)
        state = self.score_confidence.run(state)
        state = self.ask_clarification_questions.run(state)
        state = self.draft_test_scenarios.run(state)
        state = self.validate_test_output.run(state)

        if output_dir is not None:
            state = self.write_artifacts.run(state, output_dir=output_dir)

        return state