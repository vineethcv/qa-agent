from models import SpecInput
from skills.spec_parser import parse_spec


def test_parse_spec_extracts_prefixed_sections():
    spec = SpecInput(
        title="Login Spec",
        raw_text="""
        Precondition: User is on the login page
        Action: Enter valid email and password
        Action: Click login
        Expected: User is redirected to dashboard
        Note: MFA is out of scope
        """
    )

    parsed = parse_spec(spec)

    assert parsed.title == "Login Spec"
    assert parsed.preconditions == ["User is on the login page"]
    assert parsed.actions == [
        "Enter valid email and password",
        "Click login",
    ]
    assert parsed.expected_outcomes == ["User is redirected to dashboard"]
    assert parsed.notes == ["MFA is out of scope"]