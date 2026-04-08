# Generate Testcases Skill (V1)

## Purpose

Generate QA-style test cases from plain text specifications using deterministic parsing and rule-based generation.

## Input

- Plain text specification
- Local text file passed through CLI

## Output

- `generated_testcases.json`
- `generated_testcases.txt`
- `generated_testcases.md`

## Current Scope

V1 intentionally supports only:

- Plain text input
- Rule-based parsing
- Deterministic testcase generation
- Core testcase types:
  - Happy Path
  - Validation
  - Negative Path

## Out of Scope

The following are explicitly out of scope for V1:

- ClickUp integration
- LLM-based parsing or generation
- Direct linkage to flow execution
- Automatic conversion into runnable flow YAML
- Advanced deduplication
- Requirement traceability mapping

## CLI Usage

```bash
python3 main.py \
  --skill generate_testcases \
  --spec-file examples/specs/login_spec.txt \
  --output-dir artifacts/generated_testcases
```

## Design Notes
This skill is separate from execution skills.
The goal is test design generation, not browser execution.
Output is optimized for reviewability and future mapping to ticket systems.