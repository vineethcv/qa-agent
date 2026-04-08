from __future__ import annotations

from typing import List

from models import (
    AcceptanceCriterion,
    BusinessRule,
    NormalizedSpecBundle,
    SourceReference,
    UIElement,
)


def _is_table_row(line: str) -> bool:
    stripped = line.strip()
    return "|" in stripped and len([part for part in stripped.split("|") if part.strip()]) >= 2


def _split_table_row(line: str) -> List[str]:
    return [part.strip() for part in line.strip().split("|") if part.strip()]


def enrich_bundle_from_table_like_text(bundle: NormalizedSpecBundle) -> NormalizedSpecBundle:
    """
    V2 Phase 4:
    - Detect simple table-like rows from text sources
    - Infer UI elements, business rules, and acceptance criteria
    - Keep behavior deterministic and conservative
    """
    ui_elements = list(bundle.ui_elements)
    business_rules = list(bundle.business_rules)
    acceptance_criteria = list(bundle.acceptance_criteria)

    ui_index = len(ui_elements) + 1
    business_rule_index = len(business_rules) + 1
    acceptance_index = len(acceptance_criteria) + 1

    for source in bundle.spec_sources:
        if source.source_type != "text":
            continue

        lines = [line.strip() for line in source.content.splitlines() if line.strip()]
        if not lines:
            continue

        header = []
        for line in lines:
            if not _is_table_row(line):
                continue

            columns = _split_table_row(line)

            if not header:
                header = [column.lower() for column in columns]
                continue

            if set(columns) <= {"---", "----", "-----"}:
                continue

            row_map = {}
            for idx, value in enumerate(columns):
                key = header[idx] if idx < len(header) else f"column_{idx + 1}"
                row_map[key] = value

            field_name = row_map.get("field", "") or row_map.get("name", "")
            behavior = row_map.get("behavior", "") or row_map.get("expected", "")
            required_value = row_map.get("required", "")
            validation_value = row_map.get("validation", "")
            notes_value = row_map.get("notes", "")

            source_ref = SourceReference(
                source_type="table",
                source_name=source.name,
                section="",
                excerpt=" | ".join(columns),
            )

            if field_name:
                ui_elements.append(
                    UIElement(
                        name=field_name,
                        element_type="input",
                        expected_behavior=behavior or validation_value or notes_value,
                        source_refs=[source_ref],
                    )
                )
                ui_index += 1

            if required_value:
                normalized_required = required_value.lower()
                if normalized_required in {"yes", "true", "required"}:
                    business_rules.append(
                        BusinessRule(
                            rule_id=f"BR-{business_rule_index}",
                            description=f"Field '{field_name}' is required.",
                            source_refs=[source_ref],
                        )
                    )
                    business_rule_index += 1

            if validation_value:
                acceptance_criteria.append(
                    AcceptanceCriterion(
                        criterion_id=f"AC-{acceptance_index}",
                        description=f"Field '{field_name}' validation: {validation_value}",
                        source_refs=[source_ref],
                    )
                )
                acceptance_index += 1

            if behavior:
                acceptance_criteria.append(
                    AcceptanceCriterion(
                        criterion_id=f"AC-{acceptance_index}",
                        description=f"Field '{field_name}' behavior: {behavior}",
                        source_refs=[source_ref],
                    )
                )
                acceptance_index += 1

    bundle.ui_elements = ui_elements
    bundle.business_rules = business_rules
    bundle.acceptance_criteria = acceptance_criteria

    return bundle