# Generate Testcases Skill (V2)

## Purpose

Generate QA-style test cases from multimodal requirement inputs using a normalized requirement-understanding pipeline.

V2 expands the capability from deterministic text parsing to a broader understanding model that can work with:

- free-form plain text specs
- table-like text specs
- multiple spec text files
- design screenshots provided as image files

The goal is still test design generation, not browser execution.

---

## Supported Inputs

### 1. Plain text specs

The agent can infer requirement signals from free-form PM-style descriptions.

Examples:
- feature overviews
- acceptance notes
- user-flow descriptions
- validation notes written in paragraph form

### 2. Table-like text specs

The agent can interpret simple text tables, such as markdown-style or pipe-delimited rows.

Examples:
- field behavior tables
- validation rule tables
- required/optional field listings

### 3. Multiple spec files

The agent can combine several text files into one normalized requirement bundle.

Typical examples:
- one overview file
- one validation file
- one field behavior file

### 4. Design screenshots

The agent can use screenshot metadata as a design understanding input.

Current V2 behavior uses:
- image file name
- optional image description

This creates a design-understanding interface without requiring Figma API access or `.fig` parsing.

---

## Output Artifacts

V2 generates both understanding artifacts and testcase artifacts.

### Understanding artifacts

- `understanding_summary.json`
- `understanding_summary.md`
- `ambiguities.md`

These explain:
- what the agent inferred
- which requirement signals were extracted
- what is missing or unclear

### Testcase artifacts

- `generated_testcases.json`
- `generated_testcases.txt`
- `generated_testcases.md`

These contain:
- generated QA test cases
- testcase categories
- warnings derived from ambiguities

---

## Current V2 Pipeline

The high-level pipeline is:

1. Ingest multiple spec files and design image inputs
2. Build a normalized spec bundle
3. Run free-form text understanding
4. Run table-like text understanding
5. Run screenshot-based design understanding
6. Merge all understanding into one normalized bundle
7. Analyze ambiguities and missing detail
8. Generate test cases from the normalized bundle
9. Write understanding and testcase artifacts

---

## Generated Testcase Categories

Current V2 generation supports:

- Happy Path
- Validation
- Negative Path
- UI Presence
- Navigation and State

---

## Source Traceability

Generated test cases now include source traceability.

A testcase may carry references back to:
- a text spec file
- a table-derived source row
- a design screenshot source

This is intended to support later review, refinement, and possible ticket-system integration.

---

## CLI Usage

Example:

```bash
python3 main.py \
  --skill generate_testcases \
  --title "Login Feature" \
  --spec-file examples/specs/login_spec.txt \
  --spec-file examples/specs/post_login_navigation_spec.txt \
  --design-image examples/designs/login_screen.png \
  --output-dir artifacts/v2_test_run_1
```
## Current Limitations

V2 is intentionally scoped and does not yet support:

direct Figma API integration
.fig file parsing
real visual parsing of image content
OCR-based layout extraction
automatic flow YAML generation
ClickUp integration
direct browser execution from inferred test cases
advanced contradiction resolution or deduplication across sources

For design screenshots specifically, V2 currently relies on image metadata rather than deep visual understanding.

## Design Principles

This skill is designed around three principles:

1. Understanding before generation

The agent should first build a normalized understanding of the requirements before generating test cases.

2. Separation of analysis and execution

Requirement understanding artifacts and testcase artifacts are intentionally separate.

3. Conservative inference

The current system is designed to infer carefully and emit ambiguities when details are missing.

Intended Next Direction

Future iterations may expand into:

deeper screenshot understanding
contradiction detection across sources
stronger traceability
ticket-system export mappings
tighter alignment between understood requirements and executable test flows

These are intentionally outside the current V2 scope.