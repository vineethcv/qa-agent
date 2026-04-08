from models import SpecInput
from skills.generate_testcases import generate_testcases
from skills.testcase_formatter import (
    format_testcases_as_markdown,
    format_testcases_as_text,
)


def test_format_testcases_as_text():
    spec = SpecInput(
        title="Login Spec",
        raw_text="Action: Click login\nExpected: User is redirected"
    )
    bundle = generate_testcases(spec)

    output = format_testcases_as_text(bundle)

    assert "Test Case Bundle: Login Spec" in output
    assert "Login Spec - Happy Path" in output


def test_format_testcases_as_markdown():
    spec = SpecInput(
        title="Login Spec",
        raw_text="Action: Click login\nExpected: User is redirected"
    )
    bundle = generate_testcases(spec)

    output = format_testcases_as_markdown(bundle)

    assert "# Test Case Bundle: Login Spec" in output
    assert "## Login Spec - Happy Path" in output