from __future__ import annotations

from agent.state import AgentState
from agent.tools.base import AgentTool
from skills.ingest_specs import build_normalized_spec_bundle


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