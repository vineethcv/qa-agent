from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class SpecInput:
    title: str
    raw_text: str
    source: str = "text"


@dataclass
class ParsedSpec:
    title: str
    summary: str
    preconditions: List[str] = field(default_factory=list)
    actions: List[str] = field(default_factory=list)
    expected_outcomes: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)


@dataclass
class TestStep:
    step_number: int
    action: str
    expected_result: str


@dataclass
class GeneratedTestCase:
    title: str
    objective: str
    preconditions: List[str] = field(default_factory=list)
    steps: List[TestStep] = field(default_factory=list)
    priority: str = "Medium"
    tags: List[str] = field(default_factory=list)
    source_refs: List["SourceReference"] = field(default_factory=list)


@dataclass
class TestCaseBundle:
    source_title: str
    test_cases: List[GeneratedTestCase] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class SourceReference:
    source_type: str  # text | table | image
    source_name: str
    section: str = ""
    excerpt: str = ""


@dataclass
class SpecSource:
    name: str
    content: str
    source_type: str = "text"


@dataclass
class DesignImageInput:
    name: str
    path: str
    description: str = ""


@dataclass
class RequirementItem:
    id: str
    title: str
    description: str
    category: str  # functional | validation | navigation | ui | state | error_handling
    source_refs: List[SourceReference] = field(default_factory=list)


@dataclass
class UIElement:
    name: str
    element_type: str  # input | button | label | link | menu | modal | table | card
    expected_behavior: str = ""
    source_refs: List[SourceReference] = field(default_factory=list)


@dataclass
class BusinessRule:
    rule_id: str
    description: str
    source_refs: List[SourceReference] = field(default_factory=list)


@dataclass
class AcceptanceCriterion:
    criterion_id: str
    description: str
    source_refs: List[SourceReference] = field(default_factory=list)


@dataclass
class Ambiguity:
    description: str
    severity: str = "medium"  # low | medium | high
    source_refs: List[SourceReference] = field(default_factory=list)


@dataclass
class NormalizedSpecBundle:
    title: str
    summary: str = ""
    spec_sources: List[SpecSource] = field(default_factory=list)
    design_images: List[DesignImageInput] = field(default_factory=list)
    requirements: List[RequirementItem] = field(default_factory=list)
    ui_elements: List[UIElement] = field(default_factory=list)
    business_rules: List[BusinessRule] = field(default_factory=list)
    acceptance_criteria: List[AcceptanceCriterion] = field(default_factory=list)
    ambiguities: List[Ambiguity] = field(default_factory=list)