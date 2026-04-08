from __future__ import annotations

from typing import List

from models import (
    Ambiguity,
    NormalizedSpecBundle,
    RequirementItem,
    SourceReference,
    UIElement,
)


def _infer_element_type(text: str) -> str:
    lower = text.lower()

    if "button" in lower:
        return "button"
    if "field" in lower or "input" in lower:
        return "input"
    if "menu" in lower or "nav" in lower or "navigation" in lower:
        return "menu"
    if "modal" in lower or "dialog" in lower:
        return "modal"
    if "table" in lower or "grid" in lower:
        return "table"
    if "card" in lower:
        return "card"
    if "label" in lower or "text" in lower:
        return "label"

    return "screen"


def enrich_bundle_from_design_screenshots(bundle: NormalizedSpecBundle) -> NormalizedSpecBundle:
    """
    V2 Phase 5:
    - Infer simple UI signals from design image metadata only
    - Use image name and description as the source of understanding
    - Keep behavior deterministic and conservative
    """
    ui_elements = list(bundle.ui_elements)
    requirements = list(bundle.requirements)
    ambiguities = list(bundle.ambiguities)

    requirement_index = len(requirements) + 1

    for image in bundle.design_images:
        source_text = f"{image.name} {image.description}".strip()
        source_ref = SourceReference(
            source_type="image",
            source_name=image.name,
            section="",
            excerpt=image.description,
        )

        if not source_text.strip():
            ambiguities.append(
                Ambiguity(
                    description=f"Design image '{image.name}' does not contain descriptive metadata.",
                    severity="medium",
                    source_refs=[source_ref],
                )
            )
            continue

        ui_elements.append(
            UIElement(
                name=image.name,
                element_type=_infer_element_type(source_text),
                expected_behavior=image.description,
                source_refs=[source_ref],
            )
        )

        requirements.append(
            RequirementItem(
                id=f"REQ-{requirement_index}",
                title=f"Inferred design requirement {requirement_index}",
                description=f"UI represented by design image '{image.name}' should be available and consistent with the provided design context.",
                category="ui",
                source_refs=[source_ref],
            )
        )
        requirement_index += 1

        if not image.description.strip():
            ambiguities.append(
                Ambiguity(
                    description=f"Design image '{image.name}' has no description, so inferred UI understanding may be incomplete.",
                    severity="medium",
                    source_refs=[source_ref],
                )
            )

    bundle.ui_elements = ui_elements
    bundle.requirements = requirements
    bundle.ambiguities = ambiguities

    return bundle