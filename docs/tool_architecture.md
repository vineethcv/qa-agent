# Tool-Based Spec Agent Architecture

## Overview

The spec-understanding flow has been refactored from a pipeline-oriented structure into a tool-based agent structure.

The current implementation still uses the existing deterministic skills under the hood, but these skills are now exposed through agent tools and orchestrated through a single planner.

This keeps the current behavior usable while creating a better foundation for future intelligence improvements such as conflict handling, confidence scoring, clarification loops, and richer scenario generation.

## Current agent flow

The current `SpecUnderstandingAgent` executes tools in this order:

1. `read_spec_sources`
2. `extract_requirement_candidates`
3. `extract_table_rules`
4. `inspect_ui_artifact`
5. `merge_understanding`
6. `map_user_flows`
7. `resolve_conflicts`
8. `find_gaps_and_conflicts`
9. `score_confidence`
10. `ask_clarification_questions`
11. `draft_test_scenarios`
12. `validate_test_output`
13. `write_artifacts` (when an output directory is provided)

## Tool responsibilities

- `read_spec_sources`  
  Registers input sources and creates the initial normalized bundle.

- `extract_requirement_candidates`  
  Uses narrative text parsing to infer requirements, rules, acceptance criteria, and ambiguities.

- `extract_table_rules`  
  Uses table-like spec parsing to extract field-level validations and behavior constraints.

- `inspect_ui_artifact`  
  Uses design image metadata to infer visible UI structure and possible UI-related gaps.

- `merge_understanding`  
  Consolidates the different understanding passes into a single unified model.

- `map_user_flows`  
  Builds lightweight journey and transition paths from the current understanding.

- `resolve_conflicts`  
  Detects duplicate, contradictory, or incomplete requirement signals.

- `find_gaps_and_conflicts`  
  Expands ambiguity analysis into state-level gaps, questions, and conflict tracking.

- `score_confidence`  
  Assigns lightweight confidence levels to the current understanding.

- `ask_clarification_questions`  
  Converts open questions and conflicts into more explicit clarification prompts.

- `draft_test_scenarios`  
  Generates testcase scenarios from the refined understanding.

- `validate_test_output`  
  Validates generated testcase output for structural quality.

- `write_artifacts`  
  Writes understanding and testcase artifacts and stores output paths in agent state.

## Agent state

The agent now uses a shared `AgentState` object to carry:

- raw inputs
- understanding bundle
- testcase bundle
- open questions
- clarification questions
- findings
- decisions
- user flows
- conflicts
- confidence summary
- validation summary
- artifact paths
- tool execution trace

This state object is the main contract between tools.

## Why this refactor matters

The previous structure primarily chained deterministic skill functions directly from the entrypoint.

The new structure introduces:

- a shared state model
- explicit tool contracts
- traceable execution history
- intermediate reasoning artifacts
- a planner layer that can evolve later without rewriting the whole codebase

## Current limitations

This refactor improves structure more than raw intelligence.

The current implementation still depends on the existing deterministic extraction logic for:

- narrative spec understanding
- table parsing
- design metadata interpretation
- ambiguity analysis
- testcase generation

So this is best understood as an architectural refactor that creates room for more intelligent behavior in future iterations, not a full intelligence upgrade by itself.

## Suggested future direction

Possible future improvements after this refactor include:

- replacing keyword-heavy extraction with stronger semantic parsing
- improving UI artifact understanding beyond metadata-only interpretation
- adding stronger conflict resolution logic
- making user-flow modeling more explicit and state-driven
- improving testcase generation to use flow structure more directly
- adding requirement-to-test traceability
- introducing richer confidence scoring based on evidence quality