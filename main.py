from __future__ import annotations

import argparse
import os

from models import DesignImageInput, SpecInput, SpecSource
from skills.analyze_ambiguities import analyze_bundle_ambiguities
from skills.generate_testcases import generate_testcases
from skills.generate_testcases_from_bundle import generate_testcases_from_bundle
from skills.ingest_specs import build_normalized_spec_bundle
from skills.merge_understanding import build_unified_understanding
from skills.validate_testcases import validate_testcase_bundle
from skills.write_testcases import write_testcase_artifacts
from skills.write_understanding import write_understanding_artifacts


def load_text_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _build_spec_sources(spec_files: list[str]) -> list[SpecSource]:
    sources = []
    for path in spec_files:
        sources.append(
            SpecSource(
                name=os.path.basename(path),
                content=load_text_file(path),
                source_type="text",
            )
        )
    return sources


def _build_design_inputs(design_images: list[str]) -> list[DesignImageInput]:
    inputs = []
    for path in design_images:
        inputs.append(
            DesignImageInput(
                name=os.path.basename(path),
                path=path,
                description="",
            )
        )
    return inputs


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skill", required=True)
    parser.add_argument("--spec-file", action="append", default=[])
    parser.add_argument("--design-image", action="append", default=[])
    parser.add_argument("--title", required=False)
    parser.add_argument("--output-dir", required=False, default="artifacts/generated_testcases")

    args = parser.parse_args()

    if args.skill == "generate_testcases":
        # V2 path: use normalized bundle pipeline when multi-source inputs are provided.
        if args.spec_file or args.design_image:
            title = args.title or "Generated Testcases"

            spec_sources = _build_spec_sources(args.spec_file)
            design_inputs = _build_design_inputs(args.design_image)

            bundle = build_normalized_spec_bundle(
                title=title,
                spec_sources=spec_sources,
                design_images=design_inputs,
            )
            bundle = build_unified_understanding(bundle)
            bundle = analyze_bundle_ambiguities(bundle)

            testcase_bundle = generate_testcases_from_bundle(bundle)
            validation_errors = validate_testcase_bundle(testcase_bundle)
            if validation_errors:
                raise ValueError(f"Generated testcase validation failed: {validation_errors}")

            understanding_paths = write_understanding_artifacts(bundle, args.output_dir)
            testcase_paths = write_testcase_artifacts(testcase_bundle, args.output_dir)

            print("Generated understanding artifacts:")
            for key, value in understanding_paths.items():
                print(f"{key}: {value}")

            print("Generated testcase artifacts:")
            for key, value in testcase_paths.items():
                print(f"{key}: {value}")
            return

        # V1 fallback path
        raise ValueError("At least one --spec-file or --design-image input is required for generate_testcases")

    raise ValueError(f"Unsupported skill: {args.skill}")


if __name__ == "__main__":
    main()