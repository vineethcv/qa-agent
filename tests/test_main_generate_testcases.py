import subprocess
import sys
from pathlib import Path


def test_main_generate_testcases_cli_v2_with_multiple_specs(tmp_path: Path):
    spec_file_1 = tmp_path / "login_overview.txt"
    spec_file_1.write_text(
        (
            "The user logs in from the login page. "
            "The system shall allow access only with valid credentials. "
            "The user should be redirected to the dashboard after successful login."
        ),
        encoding="utf-8",
    )

    spec_file_2 = tmp_path / "login_table.txt"
    spec_file_2.write_text(
        (
            "| Field | Behavior | Required | Validation | Notes |\n"
            "| --- | --- | --- | --- | --- |\n"
            "| Email | Accept user email input | Yes | Must be a valid email address | Visible on login form |\n"
        ),
        encoding="utf-8",
    )

    design_image = tmp_path / "login_screen.png"
    design_image.write_bytes(b"fake-image-content")

    output_dir = tmp_path / "out"

    result = subprocess.run(
        [
            sys.executable,
            "main.py",
            "--skill",
            "generate_testcases",
            "--title",
            "Login Feature",
            "--spec-file",
            str(spec_file_1),
            "--spec-file",
            str(spec_file_2),
            "--design-image",
            str(design_image),
            "--output-dir",
            str(output_dir),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert (output_dir / "generated_testcases.json").exists()
    assert (output_dir / "generated_testcases.txt").exists()
    assert (output_dir / "generated_testcases.md").exists()
    assert (output_dir / "understanding_summary.json").exists()
    assert (output_dir / "understanding_summary.md").exists()
    assert (output_dir / "ambiguities.md").exists()