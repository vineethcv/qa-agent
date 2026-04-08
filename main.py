from __future__ import annotations

import argparse
from pathlib import Path

from agent.spec_agent import SpecUnderstandingAgent
from agent.state import AgentState
from models import DesignImageInput, SpecSource


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="QA agent for spec understanding and testcase generation."
    )
    parser.add_argument(
        "--mode",
        required=True,
        choices=["generate_testcases"],
        help="Execution mode.",
    )
    parser.add_argument(
        "--title",
        default="QA Agent Run",
        help="Title for the current run.",
    )
    parser.add_argument(
        "--spec-file",
        action="append",
        default=[],
        help="Path to a text or markdown spec file. Can be provided multiple times.",
    )
    parser.add_argument(
        "--design-image",
        action="append",
        default=[],
        help="Path to a design image. Can be provided multiple times.",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Directory where generated artifacts will be written.",
    )
    return parser.parse_args()


def load_spec_sources(paths: list[str]) -> list[SpecSource]:
    spec_sources: list[SpecSource] = []

    for raw_path in paths:
        path = Path(raw_path)
        content = path.read_text(encoding="utf-8")
        spec_sources.append(
            SpecSource(
                name=path.name,
                content=content,
                source_type="text",
            )
        )

    return spec_sources


def load_design_images(paths: list[str]) -> list[DesignImageInput]:
    design_images: list[DesignImageInput] = []

    for raw_path in paths:
        path = Path(raw_path)
        design_images.append(
            DesignImageInput(
                name=path.name,
                path=str(path),
                description="",
            )
        )

    return design_images


def run_generate_testcases(args: argparse.Namespace) -> None:
    spec_sources = load_spec_sources(args.spec_file)
    design_images = load_design_images(args.design_image)

    state = AgentState(
        title=args.title,
        raw_inputs={
            "spec_sources": spec_sources,
            "design_images": design_images,
        },
    )

    agent = SpecUnderstandingAgent()
    state = agent.run(state, output_dir=args.output_dir)

    print("Run completed.")
    print(f"Tool trace entries: {len(state.tool_trace)}")
    print(f"Open questions: {len(state.open_questions)}")
    print(f"Clarification questions: {len(state.clarification_questions)}")
    print(f"Conflicts: {len(state.conflicts)}")
    print(f"Confidence: {state.confidence.get('overall', 'unknown')}")
    print(f"Validation passed: {state.validation.get('is_valid', False)}")

    artifact_groups = ", ".join(state.artifacts.keys()) if state.artifacts else "none"
    print(f"Artifacts written: {artifact_groups}")


def main() -> None:
    args = parse_args()

    if args.mode == "generate_testcases":
        run_generate_testcases(args)
        return

    raise ValueError(f"Unsupported mode: {args.mode}")


if __name__ == "__main__":
    main()