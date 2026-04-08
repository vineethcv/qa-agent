from models import (
    Ambiguity,
    BusinessRule,
    NormalizedSpecBundle,
    RequirementItem,
    SourceReference,
    UIElement,
)


def test_generate_testcases_from_bundle_creates_expanded_case_types_with_traceability():
    from skills.generate_testcases_from_bundle import generate_testcases_from_bundle

    text_ref = SourceReference(
        source_type="text",
        source_name="login_spec.txt",
        section="Overview",
        excerpt="User can log in with valid credentials.",
    )

    image_ref = SourceReference(
        source_type="image",
        source_name="login_screen.png",
        section="",
        excerpt="Primary login button visible on login form",
    )

    bundle = NormalizedSpecBundle(
        title="Login Feature",
        requirements=[
            RequirementItem(
                id="REQ-1",
                title="Login",
                description="User can log in with valid credentials.",
                category="functional",
                source_refs=[text_ref],
            ),
            RequirementItem(
                id="REQ-2",
                title="Dashboard redirect",
                description="User is redirected to the dashboard after login.",
                category="navigation",
                source_refs=[text_ref],
            ),
        ],
        ui_elements=[
            UIElement(
                name="Login button",
                element_type="button",
                expected_behavior="Submits the login form",
                source_refs=[image_ref],
            )
        ],
        business_rules=[
            BusinessRule(
                rule_id="BR-1",
                description="Only valid credentials should authenticate the user.",
                source_refs=[text_ref],
            )
        ],
        ambiguities=[
            Ambiguity(
                description="Password complexity requirement is not specified.",
                severity="medium",
                source_refs=[text_ref],
            )
        ],
    )

    result = generate_testcases_from_bundle(bundle)

    assert result.source_title == "Login Feature"
    assert len(result.test_cases) == 5

    titles = [case.title for case in result.test_cases]
    assert "Login Feature - Happy Path" in titles
    assert "Login Feature - Validation" in titles
    assert "Login Feature - Negative Path" in titles
    assert "Login Feature - UI Presence" in titles
    assert "Login Feature - Navigation and State" in titles
    assert len(result.warnings) == 1

    happy_path_case = next(case for case in result.test_cases if case.title == "Login Feature - Happy Path")
    ui_case = next(case for case in result.test_cases if case.title == "Login Feature - UI Presence")

    assert len(happy_path_case.source_refs) >= 1
    assert happy_path_case.source_refs[0].source_name == "login_spec.txt"

    assert len(ui_case.source_refs) == 1
    assert ui_case.source_refs[0].source_name == "login_screen.png"