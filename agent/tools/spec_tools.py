from __future__ import annotations

from agent.state import AgentState
from agent.tools.base import AgentTool
from skills.analyze_ambiguities import analyze_bundle_ambiguities
from skills.generate_testcases_from_bundle import generate_testcases_from_bundle
from skills.ingest_specs import build_normalized_spec_bundle
from skills.merge_understanding import build_unified_understanding
from skills.understand_design_screenshots import enrich_bundle_from_design_screenshots
from skills.understand_tables import enrich_bundle_from_table_like_text
from skills.understand_text_specs import enrich_bundle_from_text_specs
from skills.validate_testcases import validate_testcase_bundle


class ReadSpecSourcesTool(AgentTool):
    name = "read_spec_sources"
    description = (
        "Register and normalize incoming spec sources and design inputs into an initial bundle."
    )

    def run(self, state: AgentState, **kwargs) -> AgentState:
        bundle = build_normalized_spec_bundle(
            title=state.title,
            spec_sources=state.raw_inputs.get("spec_sources", []),
            design_images=state.raw_inputs.get("design_images", []),
        )

        state.understanding = bundle
        state.tool_trace.append(
            {
                "tool": self.name,
                "status": "ok",
                "spec_source_count": len(state.raw_inputs.get("spec_sources", [])),
                "design_image_count": len(state.raw_inputs.get("design_images", [])),
            }
        )
        return state


class ExtractRequirementCandidatesTool(AgentTool):
    name = "extract_requirement_candidates"
    description = (
        "Extract candidate requirements, rules, acceptance criteria, and ambiguities from narrative text."
    )

    def run(self, state: AgentState, **kwargs) -> AgentState:
        if state.understanding is None:
            raise ValueError("understanding bundle not initialized")

        state.understanding = enrich_bundle_from_text_specs(state.understanding)
        state.tool_trace.append(
            {
                "tool": self.name,
                "status": "ok",
                "requirement_count": len(state.understanding.requirements),
                "business_rule_count": len(state.understanding.business_rules),
                "acceptance_criteria_count": len(state.understanding.acceptance_criteria),
                "ambiguity_count": len(state.understanding.ambiguities),
            }
        )
        return state


class ExtractTableRulesTool(AgentTool):
    name = "extract_table_rules"
    description = (
        "Extract UI fields, validations, and behavior constraints from table-like spec content."
    )

    def run(self, state: AgentState, **kwargs) -> AgentState:
        if state.understanding is None:
            raise ValueError("understanding bundle not initialized")

        state.understanding = enrich_bundle_from_table_like_text(state.understanding)
        state.tool_trace.append(
            {
                "tool": self.name,
                "status": "ok",
                "ui_element_count": len(state.understanding.ui_elements),
                "business_rule_count": len(state.understanding.business_rules),
                "acceptance_criteria_count": len(state.understanding.acceptance_criteria),
            }
        )
        return state


class InspectUiArtifactTool(AgentTool):
    name = "inspect_ui_artifact"
    description = (
        "Infer visible UI structure and possible mismatches from design image metadata."
    )

    def run(self, state: AgentState, **kwargs) -> AgentState:
        if state.understanding is None:
            raise ValueError("understanding bundle not initialized")

        state.understanding = enrich_bundle_from_design_screenshots(state.understanding)
        state.tool_trace.append(
            {
                "tool": self.name,
                "status": "ok",
                "ui_element_count": len(state.understanding.ui_elements),
                "ambiguity_count": len(state.understanding.ambiguities),
                "design_image_count": len(state.understanding.design_images),
            }
        )
        return state


class MergeUnderstandingTool(AgentTool):
    name = "merge_understanding"
    description = (
        "Consolidate signals from text, tables, and design metadata into one unified understanding model."
    )

    def run(self, state: AgentState, **kwargs) -> AgentState:
        if state.understanding is None:
            raise ValueError("understanding bundle not initialized")

        state.understanding = build_unified_understanding(state.understanding)
        state.tool_trace.append(
            {
                "tool": self.name,
                "status": "ok",
                "requirement_count": len(state.understanding.requirements),
                "ui_element_count": len(state.understanding.ui_elements),
                "business_rule_count": len(state.understanding.business_rules),
                "acceptance_criteria_count": len(state.understanding.acceptance_criteria),
                "ambiguity_count": len(state.understanding.ambiguities),
            }
        )
        return state


class MapUserFlowsTool(AgentTool):
    name = "map_user_flows"
    description = (
        "Build lightweight user journey and transition paths from the current understanding."
    )

    def run(self, state: AgentState, **kwargs) -> AgentState:
        if state.understanding is None:
            raise ValueError("understanding bundle not initialized")

        requirements = state.understanding.requirements
        acceptance_criteria = state.understanding.acceptance_criteria
        business_rules = state.understanding.business_rules

        flows: list[dict[str, object]] = []

        requirement_texts = [item.description for item in requirements]
        acceptance_texts = [item.description for item in acceptance_criteria]
        business_rule_texts = [item.description for item in business_rules]

        login_related = [
            text
            for text in requirement_texts + acceptance_texts + business_rule_texts
            if "login" in text.lower() or "sign in" in text.lower()
        ]
        redirect_related = [
            text
            for text in acceptance_texts + requirement_texts
            if "redirect" in text.lower() or "dashboard" in text.lower()
        ]
        validation_related = [
            text
            for text in acceptance_texts + business_rule_texts
            if "error" in text.lower()
            or "invalid" in text.lower()
            or "required" in text.lower()
            or "validation" in text.lower()
        ]

        if login_related:
            flows.append(
                {
                    "name": "login_journey",
                    "start_state": "user_not_authenticated",
                    "trigger": "submit_login_credentials",
                    "possible_transitions": (
                        ["authenticated_redirect"]
                        if redirect_related
                        else ["authentication_result_unknown"]
                    ),
                    "evidence": login_related[:5],
                }
            )

        if validation_related:
            flows.append(
                {
                    "name": "validation_feedback",
                    "start_state": "form_in_progress",
                    "trigger": "submit_invalid_or_incomplete_input",
                    "possible_transitions": ["inline_or_blocking_error_feedback"],
                    "evidence": validation_related[:5],
                }
            )

        if not flows and requirement_texts:
            flows.append(
                {
                    "name": "generic_requirement_journey",
                    "start_state": "unknown",
                    "trigger": "user_interacts_with_feature",
                    "possible_transitions": ["behavior_defined_by_requirements"],
                    "evidence": requirement_texts[:5],
                }
            )

        state.user_flows = flows
        state.tool_trace.append(
            {
                "tool": self.name,
                "status": "ok",
                "flow_count": len(state.user_flows),
            }
        )
        return state


class ResolveConflictsTool(AgentTool):
    name = "resolve_conflicts"
    description = (
        "Detect duplicate, contradictory, or incomplete requirement signals across the current understanding."
    )

    def run(self, state: AgentState, **kwargs) -> AgentState:
        if state.understanding is None:
            raise ValueError("understanding bundle not initialized")

        requirements = state.understanding.requirements
        acceptance_criteria = state.understanding.acceptance_criteria
        business_rules = state.understanding.business_rules

        conflicts: list[str] = []
        seen_requirements: set[str] = set()

        for requirement in requirements:
            normalized = requirement.description.strip().lower()
            if normalized in seen_requirements:
                conflicts.append(f"Duplicate requirement detected: {requirement.description}")
            else:
                seen_requirements.add(normalized)

        requirement_text = " ".join(item.description.lower() for item in requirements)
        acceptance_text = " ".join(item.description.lower() for item in acceptance_criteria)
        business_rule_text = " ".join(item.description.lower() for item in business_rules)

        required_signal = "required" in business_rule_text
        optional_signal = (
            "optional" in requirement_text
            or "optional" in acceptance_text
            or "optional" in business_rule_text
        )
        if required_signal and optional_signal:
            conflicts.append(
                "Possible contradiction detected: both required and optional signals exist in current understanding."
            )

        login_signal = "login" in requirement_text or "sign in" in requirement_text
        redirect_signal = "redirect" in acceptance_text or "dashboard" in acceptance_text
        if login_signal and not redirect_signal:
            conflicts.append(
                "Potentially incomplete login flow: authentication is referenced without a clear post-login outcome."
            )

        state.conflicts = conflicts
        state.findings.extend(conflicts)
        state.tool_trace.append(
            {
                "tool": self.name,
                "status": "ok",
                "conflict_count": len(state.conflicts),
            }
        )
        return state


class FindGapsAndConflictsTool(AgentTool):
    name = "find_gaps_and_conflicts"
    description = (
        "Surface missing testability details, underspecified behavior, and ambiguity-driven clarification points."
    )

    def run(self, state: AgentState, **kwargs) -> AgentState:
        if state.understanding is None:
            raise ValueError("understanding bundle not initialized")

        state.understanding = analyze_bundle_ambiguities(state.understanding)

        ambiguity_messages = [
            ambiguity.description for ambiguity in state.understanding.ambiguities
        ]
        state.open_questions.extend(ambiguity_messages)
        state.findings.extend(ambiguity_messages)

        for message in ambiguity_messages:
            if message not in state.conflicts:
                state.conflicts.append(message)

        state.tool_trace.append(
            {
                "tool": self.name,
                "status": "ok",
                "ambiguity_count": len(state.understanding.ambiguities),
                "open_question_count": len(state.open_questions),
                "conflict_count": len(state.conflicts),
            }
        )
        return state


class ScoreConfidenceTool(AgentTool):
    name = "score_confidence"
    description = (
        "Assign lightweight confidence levels to the current understanding based on evidence counts and signal coverage."
    )

    def run(self, state: AgentState, **kwargs) -> AgentState:
        if state.understanding is None:
            raise ValueError("understanding bundle not initialized")

        requirement_count = len(state.understanding.requirements)
        ui_element_count = len(state.understanding.ui_elements)
        business_rule_count = len(state.understanding.business_rules)
        acceptance_criteria_count = len(state.understanding.acceptance_criteria)
        ambiguity_count = len(state.understanding.ambiguities)
        flow_count = len(state.user_flows)
        conflict_count = len(state.conflicts)

        evidence_score = (
            requirement_count
            + ui_element_count
            + business_rule_count
            + acceptance_criteria_count
            + flow_count
        )

        if evidence_score >= 12 and ambiguity_count <= 2 and conflict_count == 0:
            overall_confidence = "high"
        elif evidence_score >= 6 and ambiguity_count <= 5:
            overall_confidence = "medium"
        else:
            overall_confidence = "low"

        state.confidence = {
            "overall": overall_confidence,
            "requirements": "high" if requirement_count >= 3 else "medium" if requirement_count >= 1 else "low",
            "ui": "high" if ui_element_count >= 3 else "medium" if ui_element_count >= 1 else "low",
            "rules": "high" if business_rule_count >= 2 else "medium" if business_rule_count >= 1 else "low",
            "acceptance": (
                "high"
                if acceptance_criteria_count >= 3
                else "medium"
                if acceptance_criteria_count >= 1
                else "low"
            ),
            "flows": "high" if flow_count >= 2 else "medium" if flow_count >= 1 else "low",
            "ambiguities": ambiguity_count,
            "conflicts": conflict_count,
        }

        state.tool_trace.append(
            {
                "tool": self.name,
                "status": "ok",
                "overall_confidence": state.confidence["overall"],
            }
        )
        return state


class AskClarificationQuestionsTool(AgentTool):
    name = "ask_clarification_questions"
    description = (
        "Convert unresolved gaps, conflicts, and low-confidence areas into concrete clarification questions."
    )

    def run(self, state: AgentState, **kwargs) -> AgentState:
        questions: list[str] = []

        for item in state.open_questions:
            questions.append(f"What is the expected behavior for: {item}?")

        for conflict in state.conflicts:
            questions.append(f"Can you clarify this apparent conflict: {conflict}?")

        overall_confidence = state.confidence.get("overall")
        if overall_confidence == "low":
            questions.append(
                "Can you provide more detailed acceptance criteria or examples to improve understanding confidence?"
            )

        deduped_questions: list[str] = []
        seen: set[str] = set()
        for question in questions:
            normalized = question.strip().lower()
            if normalized not in seen:
                seen.add(normalized)
                deduped_questions.append(question)

        state.clarification_questions = deduped_questions
        state.tool_trace.append(
            {
                "tool": self.name,
                "status": "ok",
                "clarification_question_count": len(state.clarification_questions),
            }
        )
        return state


class DraftTestScenariosTool(AgentTool):
    name = "draft_test_scenarios"
    description = (
        "Generate testcase scenarios from the current refined understanding bundle."
    )

    def run(self, state: AgentState, **kwargs) -> AgentState:
        if state.understanding is None:
            raise ValueError("understanding bundle not initialized")

        state.testcases = generate_testcases_from_bundle(state.understanding)
        state.tool_trace.append(
            {
                "tool": self.name,
                "status": "ok",
                "testcase_count": len(state.testcases.test_cases),
            }
        )
        return state


class ValidateTestOutputTool(AgentTool):
    name = "validate_test_output"
    description = (
        "Validate generated testcase output for basic structural quality before artifact writing."
    )

    def run(self, state: AgentState, **kwargs) -> AgentState:
        if state.testcases is None:
            raise ValueError("testcase bundle not initialized")

        validation_result = validate_testcase_bundle(state.testcases)
        state.validation = {
            "is_valid": validation_result.is_valid,
            "error_count": len(validation_result.errors),
            "errors": validation_result.errors,
        }

        if validation_result.errors:
            state.findings.extend(validation_result.errors)

        state.tool_trace.append(
            {
                "tool": self.name,
                "status": "ok",
                "is_valid": validation_result.is_valid,
                "error_count": len(validation_result.errors),
            }
        )
        return state