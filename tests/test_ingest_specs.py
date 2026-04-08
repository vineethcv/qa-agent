from models import DesignImageInput, SpecSource
from skills.ingest_specs import build_normalized_spec_bundle


def test_build_normalized_spec_bundle_with_multiple_sources():
    sources = [
        SpecSource(
            name="overview.txt",
            content="User can log in.",
            source_type="text",
        ),
        SpecSource(
            name="validation.txt",
            content="Password must be at least 8 characters.",
            source_type="text",
        ),
    ]

    images = [
        DesignImageInput(
            name="login_screen.png",
            path="designs/login_screen.png",
        )
    ]

    bundle = build_normalized_spec_bundle(
        title="Login Feature",
        spec_sources=sources,
        design_images=images,
    )

    assert bundle.title == "Login Feature"
    assert len(bundle.spec_sources) == 2
    assert len(bundle.design_images) == 1

    assert bundle.requirements == []
    assert bundle.ui_elements == []
    assert bundle.business_rules == []
    assert bundle.acceptance_criteria == []
    assert bundle.ambiguities == []