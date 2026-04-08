from models import (
    GeneratedTestCase,
    TestCaseBundle as GeneratedTestCaseBundle,
    TestStep as GeneratedTestStep,
)
from skills.validate_testcases import validate_testcase_bundle


def test_validate_testcase_bundle_detects_missing_expected_result():
    bundle = GeneratedTestCaseBundle(
        source_title="Example",
        test_cases=[
            GeneratedTestCase(
                title="Case 1",
                objective="Objective",
                steps=[
                    GeneratedTestStep(
                        step_number=1,
                        action="Click submit",
                        expected_result=""
                    )
                ],
            )
        ],
    )

    errors = validate_testcase_bundle(bundle)

    assert len(errors) == 1
    assert "empty expected result" in errors[0]