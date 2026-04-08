from models import NormalizedSpecBundle, SpecSource
from skills.ingest_specs import build_normalized_spec_bundle
from skills.understand_text_specs import enrich_bundle_from_text_specs


def test_enrich_bundle_from_text_specs_infers_requirements_rules_and_acceptance():
    sources = [
        SpecSource(
            name="login_overview.txt",
            content=(
                "The user logs in from the login page. "
                "The system shall allow access only with valid credentials. "
                "The user should be redirected to the dashboard after successful login."
            ),
            source_type="text",
        )
    ]

    bundle = build_normalized_spec_bundle(
        title="Login Feature",
        spec_sources=sources,
        design_images=[],
    )

    enriched = enrich_bundle_from_text_specs(bundle)

    assert enriched.title == "Login Feature"
    assert len(enriched.requirements) >= 1
    assert len(enriched.business_rules) == 1
    assert len(enriched.acceptance_criteria) == 1
    assert enriched.summary != ""


def test_enrich_bundle_from_text_specs_detects_ambiguity_keywords():
    sources = [
        SpecSource(
            name="vague_spec.txt",
            content="The system may show additional fields if applicable.",
            source_type="text",
        )
    ]

    bundle = build_normalized_spec_bundle(
        title="Dynamic Form",
        spec_sources=sources,
        design_images=[],
    )

    enriched = enrich_bundle_from_text_specs(bundle)

    assert len(enriched.ambiguities) == 1
    assert "Potential ambiguity detected" in enriched.ambiguities[0].description