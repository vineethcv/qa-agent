from __future__ import annotations

from models import Ambiguity, NormalizedSpecBundle, SourceReference


def analyze_bundle_ambiguities(bundle: NormalizedSpecBundle) -> NormalizedSpecBundle:
    """
    V2 Phase 7:
    - Add QA-oriented ambiguity and missing-detail findings
    - Keep behavior deterministic and conservative
    """
    ambiguities = list(bundle.ambiguities)

    if not bundle.requirements:
        ambiguities.append(
            Ambiguity(
                description="No requirements were inferred from the provided sources.",
                severity="high",
                source_refs=[],
            )
        )

    if bundle.ui_elements and not bundle.acceptance_criteria:
        ambiguities.append(
            Ambiguity(
                description="UI elements were identified, but no acceptance criteria were inferred.",
                severity="high",
                source_refs=[],
            )
        )

    if bundle.requirements and not bundle.business_rules:
        ambiguities.append(
            Ambiguity(
                description="Requirements were inferred, but no business rules were identified.",
                severity="medium",
                source_refs=[],
            )
        )

    described_image_names = {
        image.name for image in bundle.design_images if image.description.strip()
    }
    if bundle.design_images and not described_image_names:
        ambiguities.append(
            Ambiguity(
                description="Design images were provided without usable descriptive context.",
                severity="medium",
                source_refs=[
                    SourceReference(
                        source_type="image",
                        source_name=image.name,
                        section="",
                        excerpt=image.description,
                    )
                    for image in bundle.design_images
                ],
            )
        )

    bundle.ambiguities = ambiguities
    return bundle