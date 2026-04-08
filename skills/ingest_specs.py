from __future__ import annotations

from typing import List, Optional

from models import (
    DesignImageInput,
    NormalizedSpecBundle,
    SpecSource,
)


def build_normalized_spec_bundle(
    title: str,
    spec_sources: List[SpecSource],
    design_images: Optional[List[DesignImageInput]] = None,
) -> NormalizedSpecBundle:
    """
    V2 Phase 2:
    - Combine multiple spec sources and design inputs into a single bundle
    - No parsing or intelligence yet
    """

    return NormalizedSpecBundle(
        title=title,
        summary="",
        spec_sources=spec_sources,
        design_images=design_images or [],
        requirements=[],
        ui_elements=[],
        business_rules=[],
        acceptance_criteria=[],
        ambiguities=[],
    )