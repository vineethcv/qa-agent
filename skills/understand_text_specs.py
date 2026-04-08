from __future__ import annotations

import re
from typing import List

from models import (
    AcceptanceCriterion,
    Ambiguity,
    BusinessRule,
    NormalizedSpecBundle,
    RequirementItem,
    SourceReference,
)


SENTENCE_SPLIT_REGEX = re.compile(r"(?<=[.!?])\s+")


def _split_sentences(text: str) -> List[str]:
    parts = [part.strip() for part in SENTENCE_SPLIT_REGEX.split(text.strip()) if part.strip()]
    if parts:
        return parts

    fallback_parts = [line.strip() for line in text.splitlines() if line.strip()]
    return fallback_parts


def _build_source_ref(source_name: str, excerpt: str) -> SourceReference:
    return SourceReference(
        source_type="text",
        source_name=source_name,
        section="",
        excerpt=excerpt,
    )


def enrich_bundle_from_text_specs(bundle: NormalizedSpecBundle) -> NormalizedSpecBundle:
    """
    V2 Phase 3:
    - Infer simple requirement understanding from free-form text specs
    - Populate normalized requirement fields
    - Keep behavior deterministic and conservative
    """
    requirements: List[RequirementItem] = []
    business_rules: List[BusinessRule] = []
    acceptance_criteria: List[AcceptanceCriterion] = []
    ambiguities: List[Ambiguity] = []

    requirement_index = 1
    business_rule_index = 1
    acceptance_index = 1

    for source in bundle.spec_sources:
        if source.source_type != "text":
            continue

        sentences = _split_sentences(source.content)

        for sentence in sentences:
            lower = sentence.lower()
            source_ref = _build_source_ref(source.name, sentence)

            if any(keyword in lower for keyword in ["must", "shall", "only", "required"]):
                business_rules.append(
                    BusinessRule(
                        rule_id=f"BR-{business_rule_index}",
                        description=sentence,
                        source_refs=[source_ref],
                    )
                )
                business_rule_index += 1

            if any(keyword in lower for keyword in ["should", "expected", "success", "redirected", "displayed"]):
                acceptance_criteria.append(
                    AcceptanceCriterion(
                        criterion_id=f"AC-{acceptance_index}",
                        description=sentence,
                        source_refs=[source_ref],
                    )
                )
                acceptance_index += 1

            if any(keyword in lower for keyword in ["user", "system", "screen", "page", "button", "field", "form", "login", "submit"]):
                requirements.append(
                    RequirementItem(
                        id=f"REQ-{requirement_index}",
                        title=f"Inferred requirement {requirement_index}",
                        description=sentence,
                        category="functional",
                        source_refs=[source_ref],
                    )
                )
                requirement_index += 1

            if any(keyword in lower for keyword in ["maybe", "etc", "and so on", "as needed", "if applicable"]):
                ambiguities.append(
                    Ambiguity(
                        description=f"Potential ambiguity detected: {sentence}",
                        severity="medium",
                        source_refs=[source_ref],
                    )
                )

        if not sentences:
            ambiguities.append(
                Ambiguity(
                    description=f"No understandable content found in source '{source.name}'.",
                    severity="high",
                    source_refs=[
                        SourceReference(
                            source_type="text",
                            source_name=source.name,
                            section="",
                            excerpt="",
                        )
                    ],
                )
            )

    summary_parts = []
    for source in bundle.spec_sources:
        if source.source_type == "text" and source.content.strip():
            summary_parts.append(source.content.strip())

    bundle.summary = " ".join(summary_parts).strip()
    bundle.requirements = requirements
    bundle.business_rules = business_rules
    bundle.acceptance_criteria = acceptance_criteria
    bundle.ambiguities = ambiguities

    return bundle