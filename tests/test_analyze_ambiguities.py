from models import DesignImageInput, SpecSource
from skills.analyze_ambiguities import analyze_bundle_ambiguities
from skills.ingest_specs import build_normalized_spec_bundle


def test_analyze_bundle_ambiguities_flags_missing_acceptance_for_ui():
    bundle = build_normalized_spec_bundle(
        title="UI Only Feature",
        spec_sources=[],
        design_images=[
            DesignImageInput(
                name="screen.png",
                path="designs/screen.png",
                description="Primary navigation menu visible",
            )
        ],
    )

    bundle.ui_elements = []
    bundle.requirements = []
    bundle.acceptance_criteria = []
    bundle.business_rules = []

    analyzed = analyze_bundle_ambiguities(bundle)

    descriptions = [item.description for item in analyzed.ambiguities]
    assert "No requirements were inferred from the provided sources." in descriptions


def test_analyze_bundle_ambiguities_flags_missing_business_rules():
    bundle = build_normalized_spec_bundle(
        title="Login Feature",
        spec_sources=[
            SpecSource(
                name="overview.txt",
                content="The user logs in on the login page.",
                source_type="text",
            )
        ],
        design_images=[],
    )

    bundle.requirements = [
        # intentionally minimal object-free shape is avoided; use actual inferred-like data
    ]
    bundle.requirements.append(
        __import__("models").RequirementItem(
            id="REQ-1",
            title="Login requirement",
            description="The user logs in on the login page.",
            category="functional",
            source_refs=[],
        )
    )
    bundle.business_rules = []
    bundle.acceptance_criteria = []

    analyzed = analyze_bundle_ambiguities(bundle)

    descriptions = [item.description for item in analyzed.ambiguities]
    assert "Requirements were inferred, but no business rules were identified." in descriptions