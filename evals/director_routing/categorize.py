"""Single-source-of-truth bucket rule for director_routing eval cases.

categorize(expected_chain) -> bucket_name (one of 11 buckets).

The rule projects a chain onto three axes:
  1. Primary capability set (which transformations are present)
  2. Intake type (text-brief / image / video upload)
  3. Addon set (subtitle / translation / audio overlay)

A "primary" is a transformation that defines task identity. An "addon" is a
modifier that doesn't promote the chain to a different bucket on its own.

Buckets:
  cr            — creative-from-brief (no addon)
  intake_img    — imgref + creative-from-brief (any addon variant)
  sub           — creative-from-brief + Transcription
  sub_vid       — IntakeVideo + Transcription only (no creative primary)
  bilingual     — creative-from-brief + Transcription + Translation
  storytelling  — creative-illustrated (NarrationAgent present)
  style         — IntakeVideo + StyleTransfer (single primary)
  extend        — IntakeVideo + VideoExtend (single primary)
  highlight     — IntakeVideo + VideoAnalysis + Highlight (single primary)
  audio         — IntakeVideo + Music/Ambience only (no other primary)
  complex       — >=2 primaries

Primaries:
  creative-from-brief         {Story, Screenplay, KeyFrame, Video} all present
  creative-illustrated        Narration present
  StyleTransfer
  VideoExtend
  Highlight                   (with VideoAnalysis as its scaffold prep)
  VideoAnalysis-as-input      VideoAnalysis present, Highlight absent

Addons (do not count toward primary):
  Transcription, Translation, Music, Ambience
"""

from __future__ import annotations


def _flatten_agents(expected_chain) -> set[str]:
    """Collect every agent name appearing in any step (including alternation)."""
    agents: set[str] = set()
    for step in expected_chain:
        if isinstance(step, list):
            agents.update(step)
        else:
            agents.add(step)
    return agents


def _has_creative_from_brief(agents: set[str]) -> bool:
    return {"StoryAgent", "ScreenplayAgent", "KeyFrameAgent", "VideoAgent"}.issubset(agents)


def _has_creative_illustrated(agents: set[str]) -> bool:
    return "NarrationAgent" in agents


def _primary_count(agents: set[str]) -> int:
    n = 0
    if _has_creative_from_brief(agents):
        n += 1
    if _has_creative_illustrated(agents):
        n += 1
    if "StyleTransferAgent" in agents:
        n += 1
    if "VideoExtendAgent" in agents:
        n += 1
    if "HighlightAgent" in agents:
        n += 1
    if "VideoAnalysisAgent" in agents and "HighlightAgent" not in agents:
        n += 1
    return n


def categorize(expected_chain) -> str:
    agents = _flatten_agents(expected_chain)

    if _has_creative_illustrated(agents):
        return "storytelling"

    if _primary_count(agents) >= 2:
        return "complex"

    if _has_creative_from_brief(agents):
        if "IntakeImageAgent" in agents:
            return "intake_img"
        if "TranslationAgent" in agents:
            return "bilingual"
        if "TranscriptionAgent" in agents:
            return "sub"
        return "cr"

    if "StyleTransferAgent" in agents:
        return "style"
    if "VideoExtendAgent" in agents:
        return "extend"
    if "HighlightAgent" in agents:
        return "highlight"
    if "VideoAnalysisAgent" in agents:
        # VideoAnalysis without Highlight and without creative primary —
        # currently no such case in the dataset; fall back to highlight family.
        return "highlight"

    if "TranscriptionAgent" in agents:
        return "sub_vid"
    if "MusicAgent" in agents or "AmbienceAgent" in agents:
        return "audio"

    return "unknown"


BUCKET_ORDER = [
    "cr",
    "intake_img",
    "sub",
    "sub_vid",
    "bilingual",
    "storytelling",
    "style",
    "extend",
    "highlight",
    "audio",
    "complex",
]
