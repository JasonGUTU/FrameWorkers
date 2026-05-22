"""StoryAgent output schema.

Drives the entire downstream pipeline:
  - 1 anchor per character (no variants), 1 anchor per location, 1 style anchor
  - Per-panel categories  → ShotPromptAgent picks guidance docs per panel
  - Per-panel characters_present → KeyframeAgent picks char anchors as i2i refs;
                                   identity / state changes (wounded, defeated, etc.)
                                   are described in panel.moment_description and
                                   rendered into the storyboard image — NOT as
                                   separate anchors (multiple anchors of the same
                                   character drift independently each render).

Note: Props described inline in Character.look_description (one anchor per
char + equipment combo). Locations same — one canonical look per location;
lighting / state shifts are described in panel.moment_description.
"""
from __future__ import annotations

from pydantic import BaseModel, Field

from .._categories import ShotCategory


class Character(BaseModel):
    id: str
    role: str
    look_description: str = Field(
        description="Concrete visual: face / hair / build / clothing / handheld equipment inline. "
                    "ONE canonical look for the whole story — state changes (wounded, defeated, "
                    "transformed) are rendered into storyboard panels, not as separate anchors. "
                    "Audit feedback rewrites this field directly (single source of truth)."
    )


class Location(BaseModel):
    id: str
    look_description: str = Field(
        description="Concrete environment: sky / ground / lighting / dominant colors / weather / "
                    "architecture. ONE canonical look. Audit feedback rewrites this field directly."
    )


class StoryboardPanel(BaseModel):
    """One frame inside a shot's storyboard sheet.

    LLM decides panel count and duration per shot (panels' time_range
    should tile [0, ShotIntent.duration_s] without gaps/overlap; not
    enforced here, downstream just reads).
    """
    time_range: tuple[float, float]
    categories: list[ShotCategory] = Field(min_length=1)
    moment_description: str
    dialogue: str | None = Field(
        default=None,
        description="If set, format MUST be '<character_id>: <text>' — speaker prefix "
                    "required so downstream lip-sync knows whose mouth moves. "
                    "Example: 'wei: 你的剑变钝了，师兄。'  null if silent panel.",
    )
    characters_present: list[str] = Field(
        default_factory=list,
        description="List of character_id values appearing in this panel. "
                    "Locations are at shot level (primary_location), not per panel.",
    )


class ShotIntent(BaseModel):
    shot_id: str
    duration_s: float
    narrative_purpose: str
    panels: list[StoryboardPanel] = Field(min_length=1)
    primary_location: str = Field(description="Must equal one location id.")
    notes: str | None = None
    audit_notes: str = Field(
        default="",
        description="Storyboard-render-time constraints synthesized from VLM audit corrections "
                    "across prior runs. Shot has no main 'description' field (unlike char/loc) "
                    "so this dedicated field holds audit feedback. KeyframeAgent planner reads "
                    "this when generating storyboard_prompt; future runs benefit from past lessons.",
    )


class StoryOutput(BaseModel):
    title: str
    logline: str
    setting: str = Field(
        description="Cultural / era / geographic context anchor — 1-2 sentences "
                    "fixing time period (e.g. 'Ancient China, Tang dynasty / "
                    "Edo-period Japan / 1980s Hong Kong / present-day Tokyo'), "
                    "genre world (wuxia / cyberpunk / Western / sci-fi), and "
                    "ethnicity of the cast (East Asian / Black / Latine / White / "
                    "mixed). Propagates into EVERY downstream render (character + "
                    "location anchors, storyboards, shot prompts) so models don't "
                    "default to their training bias (typically Western/contemporary)."
    )
    style_anchor: str = Field(
        description="One- to two-sentence visual style brief covering: color palette "
                    "/ lighting key / aesthetic reference (film / director / era / "
                    "movement) / texture (photo, painted, grainy, glossy) / contrast. "
                    "Rendered as a single style reference image shared across ALL shots' "
                    "video generation. style_anchor is VISUAL aesthetics; setting is "
                    "WORLD context — they complement, not overlap. "
                    "Audit feedback rewrites this field directly."
    )
    characters: list[Character] = Field(
        default_factory=list,
        description="Required for StoryAgent (narrative needs ≥1 character). "
                    "TourAgent may legitimately produce empty list (pure environment tour).",
    )
    locations: list[Location] = Field(min_length=1)
    shots: list[ShotIntent] = Field(min_length=1)
