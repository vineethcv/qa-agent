from models import (
    AcceptanceCriterion,
    Ambiguity,
    BusinessRule,
    DesignImageInput,
    NormalizedSpecBundle,
    RequirementItem,
    SourceReference,
    SpecSource,
    UIElement,
)


def test_normalized_spec_bundle_can_hold_multimodal_inputs():
    text_source = SpecSource(
        name="login_spec.txt",
        content="User can log in with valid credentials.",
        source_type="text",
    )

    image_source = DesignImageInput(
        name="login_screen.png",
        path="designs/login_screen.png",
        description="Login form design screenshot",
    )

    source_ref = SourceReference(
        source_type="text",
        source_name="login_spec.txt",
        section="Overview",
        excerpt="User can log in with valid credentials.",
    )

    requirement = RequirementItem(
        id="REQ-1",
        title="User login",
        description="System shall allow a valid user to log in.",
        category="functional",
        source_refs=[source_ref],
    )

    ui_element = UIElement(
        name="Email field",
        element_type="input",
        expected_behavior="Accepts a valid email address",
        source_refs=[source_ref],
    )

    rule = BusinessRule(
        rule_id="BR-1",
        description="Only valid credentials should authenticate the user.",
        source_refs=[source_ref],
    )

    criterion = AcceptanceCriterion(
        criterion_id="AC-1",
        description="User is redirected to dashboard after successful login.",
        source_refs=[source_ref],
    )

    ambiguity = Ambiguity(
        description="Password complexity requirement is not specified.",
        severity="medium",
        source_refs=[source_ref],
    )

    bundle = NormalizedSpecBundle(
        title="Login Feature",
        summary="Normalized understanding of login requirements",
        spec_sources=[text_source],
        design_images=[image_source],
        requirements=[requirement],
        ui_elements=[ui_element],
        business_rules=[rule],
        acceptance_criteria=[criterion],
        ambiguities=[ambiguity],
    )

    assert bundle.title == "Login Feature"
    assert len(bundle.spec_sources) == 1
    assert len(bundle.design_images) == 1
    assert len(bundle.requirements) == 1
    assert len(bundle.ui_elements) == 1
    assert len(bundle.business_rules) == 1
    assert len(bundle.acceptance_criteria) == 1
    assert len(bundle.ambiguities) == 1
    assert bundle.requirements[0].id == "REQ-1"