from models import SpecInput
from skills.generate_testcases import generate_testcases


def test_generate_testcases_creates_happy_path_case():
    spec = SpecInput(
        title="Login Spec",
        raw_text="""
        Precondition: User is on login page
        Action: Enter valid email
        Action: Enter valid password
        Action: Click login
        Expected: Email is accepted
        Expected: Password is accepted
        Expected: User is redirected to dashboard
        """
    )

    result = generate_testcases(spec)

    assert result.source_title == "Login Spec"
    assert len(result.test_cases) == 1

    case = result.test_cases[0]
    assert case.title == "Login Spec - Happy Path"
    assert case.priority == "High"
    assert "happy_path" in case.tags
    assert len(case.steps) == 3