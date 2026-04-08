from models import DesignImageInput, SpecSource
from skills.ingest_specs import build_normalized_spec_bundle
from skills.merge_understanding import build_unified_understanding


def test_build_unified_understanding_combines_text_table_and_design_signals():
    sources = [
        SpecSource(
            name="login_overview.txt",
            content=(
                "The user logs in from the login page. "
                "The system shall allow access only with valid credentials. "
                "The user should be redirected to the dashboard after successful login."
            ),
            source_type="text",
        ),
        SpecSource(
            name="login_table.txt",
            content=(
                "| Field | Behavior | Required | Validation | Notes |\n"
                "| --- | --- | --- | --- | --- |\n"
                "| Email | Accept user email input | Yes | Must be a valid email address | Visible on login form |\n"
            ),
            source_type="text",
        ),
    ]

    images = [
        DesignImageInput(
            name="login_button_screen.png",
            path="designs/login_button_screen.png",
            description="Primary login button visible on login form",
        )
    ]

    bundle = build_normalized_spec_bundle(
        title="Login Feature",
        spec_sources=sources,
        design_images=images,
    )

    enriched = build_unified_understanding(bundle)

    assert enriched.title == "Login Feature"
    assert len(enriched.requirements) >= 2
    assert len(enriched.business_rules) >= 1
    assert len(enriched.acceptance_criteria) >= 1
    assert len(enriched.ui_elements) >= 2