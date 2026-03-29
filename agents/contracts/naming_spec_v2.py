"""Naming spec v2 schema for media outputs."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class NamingRuleV2:
    artifact_family: str
    semantic_meaning: str
    recommended_name_pattern: str
    id_source: str
    ordering_rules: str
    examples: list[str] = field(default_factory=list)
    rename_hints: dict[str, str] = field(default_factory=dict)


@dataclass
class NamingSpecV2:
    agent_id: str
    spec_version: str
    rules: list[NamingRuleV2] = field(default_factory=list)
