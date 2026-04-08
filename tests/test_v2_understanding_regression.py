from models import DesignImageInput, SpecSource
from skills.analyze_ambiguities import analyze_bundle_ambiguities
from skills.ingest_specs import build_normalized_spec_bundle
from skills.merge_understanding import build_unified_understanding


def test_v2_understanding_regression_free_form_only():
    bundle = build_normalized_spec_bundle(
        title="Password Reset",
        spec_sources=[
            SpecSource(
                name="password_reset_overview.txt",
                content=(
                    "The user opens the password reset page. "
                    "The system shall allow reset only for registered email addresses. "
                    "The user should see a confirmation message after submitting the request."
                ),
                source_type="text",
            )
        ],
        design_images=[],
    )

    bundle = build_unified_understanding(bundle)
    bundle = analyze_bundle_ambiguities(bundle)

    assert len(bundle.requirements) >= 1
    assert len(bundle.business_rules) >= 1
    assert len(bundle.acceptance_criteria) >= 1


def test_v2_understanding_regression_table_heavy_input():
    bundle = build_normalized_spec_bundle(
        title="Profile Form",
        spec_sources=[
            SpecSource(
                name="profile_form_table.txt",
                content=(
                    "| Field | Behavior | Required | Validation | Notes |\n"
                    "| --- | --- | --- | --- | --- |\n"
                    "| First Name | Accept user first name | Yes | Must not be empty | Visible on profile form |\n"
                    "| Email | Accept user email address | Yes | Must be a valid email address | Editable |\n"
                ),
                source_type="text",
            )
        ],
        design_images=[],
    )

    bundle = build_unified_understanding(bundle)
    bundle = analyze_bundle_ambiguities(bundle)

    assert len(bundle.ui_elements) >= 2
    assert len(bundle.business_rules) >= 2
    assert len(bundle.acceptance_criteria) >= 2


def test_v2_understanding_regression_text_and_screenshot_assisted():
    bundle = build_normalized_spec_bundle(
        title="Checkout",
        spec_sources=[
            SpecSource(
                name="checkout_overview.txt",
                content=(
                    "The user reviews the cart on the checkout page. "
                    "The system shall require a delivery address before order submission. "
                    "The user should be redirected to order confirmation after successful payment."
                ),
                source_type="text",
            )
        ],
        design_images=[
            DesignImageInput(
                name="checkout_primary_button.png",
                path="designs/checkout_primary_button.png",
                description="Primary submit order button visible on checkout form",
            )
        ],
    )

    bundle = build_unified_understanding(bundle)
    bundle = analyze_bundle_ambiguities(bundle)

    assert len(bundle.requirements) >= 2
    assert len(bundle.business_rules) >= 1
    assert len(bundle.ui_elements) >= 1


def test_v2_understanding_regression_detects_missing_detail_for_undescribed_image():
    bundle = build_normalized_spec_bundle(
        title="Dashboard",
        spec_sources=[],
        design_images=[
            DesignImageInput(
                name="dashboard_screen.png",
                path="designs/dashboard_screen.png",
                description="",
            )
        ],
    )

    bundle = build_unified_understanding(bundle)
    bundle = analyze_bundle_ambiguities(bundle)

    assert len(bundle.ambiguities) >= 1
    descriptions = [item.description.lower() for item in bundle.ambiguities]
    assert any("description" in description or "descriptive context" in description for description in descriptions)