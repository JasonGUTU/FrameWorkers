"""AnchorAuditAgent — autonomous image-vs-context verifier output schema.

The VLM self-directs what dimensions to check from free-form source context;
no hardcoded axes here. Use ``dimension`` field as the VLM's chosen axis name.
"""
from __future__ import annotations

from pydantic import BaseModel, Field


class AuditIssue(BaseModel):
    dimension: str = Field(
        description="VLM-chosen mismatch axis derived from context "
                    "(e.g. 'ethnicity', 'weapon_type', 'era_costume', 'panel_count', "
                    "'sword_count', 'architecture_period'). NOT predetermined."
    )
    expected: str = Field(description="What the source context implies should be true.")
    observed: str = Field(description="What's actually visible in the image.")
    severity: str = Field(
        description="'blocking' (must fix before pipeline continues) | "
                    "'warning' (minor, doesn't block)."
    )


class AuditResult(BaseModel):
    passed: bool = Field(
        description="True iff zero 'blocking' issues. 'warning'-only result also "
                    "passes — callers can inspect issues list for warnings."
    )
    issues: list[AuditIssue] = Field(default_factory=list)
    repair_prompt_addition: str = Field(
        default="",
        description="Concrete corrective text the caller can append to a re-render "
                    "prompt to fix the blocking issues. Empty when passed.",
    )
