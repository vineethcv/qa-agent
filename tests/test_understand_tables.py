from models import SpecSource
from skills.ingest_specs import build_normalized_spec_bundle
from skills.understand_tables import enrich_bundle_from_table_like_text


def test_enrich_bundle_from_table_like_text_extracts_ui_rules_and_acceptance():
    sources = [
        SpecSource(
            name="login_table.txt",
            content=(
                "| Field | Behavior | Required | Validation | Notes |\n"
                "| --- | --- | --- | --- | --- |\n"
                "| Email | Accept user email input | Yes | Must be a valid email address | Visible on login form |\n"
                "| Password | Accept password input | Yes | Must not be empty | Mask input |\n"
            ),
            source_type="text",
        )
    ]

    bundle = build_normalized_spec_bundle(
        title="Login Form",
        spec_sources=sources,
        design_images=[],
    )

    enriched = enrich_bundle_from_table_like_text(bundle)

    assert len(enriched.ui_elements) == 2
    assert len(enriched.business_rules) == 2
    assert len(enriched.acceptance_criteria) == 4

    assert enriched.ui_elements[0].name == "Email"
    assert "required" in enriched.business_rules[0].description.lower()
    assert "valid email address" in enriched.acceptance_criteria[0].description.lower()