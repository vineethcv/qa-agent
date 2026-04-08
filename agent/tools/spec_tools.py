from __future__ import annotations

from agent.state import AgentState
from agent.tools.base import AgentTool
from skills.ingest_specs import build_normalized_spec_bundle
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