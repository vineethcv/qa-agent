from pathlib import Path

from models import SpecInput
from skills.generate_testcases import generate_testcases
from skills.write_testcases import write_testcase_artifacts


def test_write_testcase_artifacts(tmp_path: Path):
    spec = SpecInput(
        title="Login Spec",
        raw_text="Action: Click login\nExpected: User is redirected"
    )
    bundle = generate_testcases(spec)

    result = write_testcase_artifacts(bundle, str(tmp_path))

    assert Path(result["json_path"]).exists()
    assert Path(result["text_path"]).exists()
    assert Path(result["markdown_path"]).exists()