from __future__ import annotations

import json
import os
from dataclasses import asdict

from models import TestCaseBundle
from skills.testcase_formatter import (
    format_testcases_as_markdown,
    format_testcases_as_text,
)


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def write_testcase_artifacts(bundle: TestCaseBundle, output_dir: str) -> dict:
    ensure_dir(output_dir)

    json_path = os.path.join(output_dir, "generated_testcases.json")
    text_path = os.path.join(output_dir, "generated_testcases.txt")
    markdown_path = os.path.join(output_dir, "generated_testcases.md")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(asdict(bundle), f, indent=2)

    with open(text_path, "w", encoding="utf-8") as f:
        f.write(format_testcases_as_text(bundle))

    with open(markdown_path, "w", encoding="utf-8") as f:
        f.write(format_testcases_as_markdown(bundle))

    return {
        "json_path": json_path,
        "text_path": text_path,
        "markdown_path": markdown_path,
    }