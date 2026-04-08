from __future__ import annotations

from models import NormalizedSpecBundle
from skills.understand_design_screenshots import enrich_bundle_from_design_screenshots
from skills.understand_tables import enrich_bundle_from_table_like_text
from skills.understand_text_specs import enrich_bundle_from_text_specs


def build_unified_understanding(bundle: NormalizedSpecBundle) -> NormalizedSpecBundle:
    """
    V2 Phase 6:
    - Run all currently available understanding stages
    - Return one unified normalized bundle
    - Keep behavior simple and deterministic
    """
    bundle = enrich_bundle_from_text_specs(bundle)
    bundle = enrich_bundle_from_table_like_text(bundle)
    bundle = enrich_bundle_from_design_screenshots(bundle)
    return bundle