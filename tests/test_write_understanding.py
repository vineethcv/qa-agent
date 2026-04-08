from pathlib import Path

from models import NormalizedSpecBundle
from skills.write_understanding import write_understanding_artifacts


def test_write_understanding_artifacts(tmp_path: Path):
    bundle = NormalizedSpecBundle(
        title="Test Feature",
        summary="Sample summary",
    )

    result = write_understanding_artifacts(bundle, str(tmp_path))

    assert Path(result["json_path"]).exists()
    assert Path(result["summary_md_path"]).exists()
    assert Path(result["ambiguities_md_path"]).exists()