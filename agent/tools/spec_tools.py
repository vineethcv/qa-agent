from __future__ import annotations

from agent.state import AgentState
from agent.tools.base import AgentTool
from skills.ingest_specs import build_normalized_spec_bundle
from skills.merge_understanding import build_unified_understanding
from skills.understand_design_screenshots import enrich_bundle_from_design_screenshots
from skills.understand_tables import enrich_bundle_from_table_like_text
from skills.understand_text_specs import enrich_bundle_from_text_specs


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