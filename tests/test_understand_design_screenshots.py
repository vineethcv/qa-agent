from models import DesignImageInput, SpecSource
from skills.ingest_specs import build_normalized_spec_bundle
from skills.understand_design_screenshots import enrich_bundle_from_design_screenshots


def test_enrich_bundle_from_design_screenshots_adds_ui_elements_and_requirements():
    bundle = build_normalized_spec_bundle(
        title="Login Screen",
        spec_sources=[
            SpecSource(
                name="overview.txt",
                content="Login feature overview.",
                source_type="text",
            )
        ],
        design_images=[
            DesignImageInput(
                name="login_button_screen.png",
                path="designs/login_button_screen.png",
                description="Primary login button visible on login form",
            )
        ],
    )

    enriched = enrich_bundle_from_design_screenshots(bundle)

    assert len(enriched.ui_elements) == 1
    assert len(enriched.requirements) == 1
    assert enriched.ui_elements[0].name == "login_button_screen.png"
    assert enriched.ui_elements[0].element_type == "button"
    assert enriched.requirements[0].category == "ui"


def test_enrich_bundle_from_design_screenshots_adds_ambiguity_when_description_missing():
    bundle = build_normalized_spec_bundle(
        title="Dashboard Screen",
        spec_sources=[],
        design_images=[
            DesignImageInput(
                name="dashboard_screen.png",
                path="designs/dashboard_screen.png",
                description="",
            )
        ],
    )

    enriched = enrich_bundle_from_design_screenshots(bundle)

    assert len(enriched.ui_elements) == 1
    assert len(enriched.requirements) == 1
    assert len(enriched.ambiguities) == 1
    assert "no description" in enriched.ambiguities[0].description.lower()