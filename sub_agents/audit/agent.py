"""AnchorAuditAgent — autonomous VLM image verifier.

Given an image path + free-form source context (story setting / entity
look_description / structural rules / prop counts / etc.), the VLM
self-directs which dimensions to check. NO hardcoded axes — different
stories / aesthetics imply different checks (wuxia → ethnicity / era /
weapon; cyberpunk → neon / synthwear / tech; etc).

Two abstraction layers:
  - ``run(image, context)``: the low-level call. Caller builds context.
  - ``build_anchor_context(story, entity, kind)``: helper for char / loc
    anchor audits. Checks era / culture / cast / costume / equipment match.
  - ``build_storyboard_context(story, shot)``: helper for storyboard audits.
    Checks physics realism / identity preservation / cardinality (props
    matching characters_present) / panel structure / per-panel content.

Reuses Gemini multimodal via the existing inference.clients.LLMClient
(CF AI Gateway native-Gemini channel, same as the rest of sub_agents).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional, Any

from inference.clients import LLMClient

from .. import DEFAULT_LLM_MODEL
from .schema import AuditResult


_AUDIT_SYSTEM = """You are an autonomous image-quality auditor for film pre-production.

You receive:
  (a) free-form SOURCE CONTEXT — the ground truth this image should match. May include story setting, character / location description, structural rules, prop counts, cultural / era / ethnicity anchors, panel-layout rules, etc.
  (b) the rendered image (attached).

YOUR JOB: Examine the image and find mismatches against the context. SELF-DIRECT what dimensions to check based on what the context IMPLIES matters. DO NOT rely on a fixed checklist — DERIVE the axes from the context yourself.

Examples of axes you MAY check (only check what the context implies relevant):
  - setting says "wuxia / ancient China" → ethnicity (should be East Asian), era (pre-modern costume), weapons (traditional Chinese, not katanas / Western), architecture
  - setting says "cyberpunk Tokyo" → neon presence, synthetic materials, tech level, NOT period-rural
  - look_description says "curved Dao saber" → weapon shape / blade curvature
  - structural rule "5 panels in 3x2 grid" → count panels, verify layout
  - setting says "Han Chinese cast" → all visible humans East Asian (no Caucasian / Black / etc unless context specifies mixed)
  - look_description has specific clothing color → verify
  - storyboard rule "2 swords total" → count blades across all panels

Be RIGOROUS but FAIR: only flag mismatches you can VISUALLY confirm. Don't speculate. If ambiguous, mark as "warning" not "blocking".

Output ONE JSON object exactly matching:
{
  "passed": bool   // true ONLY if zero "blocking" issues
  "issues": [
    {"dimension": str (your chosen axis name), "expected": str (from context), "observed": str (from image), "severity": "blocking" | "warning"}
  ],
  "repair_prompt_addition": str   // concrete corrective text to append to a re-render prompt; empty if passed
}

Output ONLY the JSON. No prose, no code fences."""


_SYNTHESIZE_SYSTEM = """You are a prompt editor for an image-gen pipeline.

INPUT:
  (a) ORIGINAL description — a paragraph describing an entity (character look / location / style brief / shot constraint).
  (b) AUDIT CORRECTIONS — a list of "fix this" directives gathered from prior render attempts that detected mismatches.

YOUR JOB: Output ONE synthesized description that:
  - Preserves the original's creative details (names, distinctive features, style references) — don't drop them.
  - INCORPORATES every correction inline so the description reads as if the corrections were always part of it.
  - Resolves contradictions by preferring the correction (corrections are downstream truth from VLM audit of actual renders).
  - Stays prose-like (1-3 sentences). NOT a bulleted list. NOT prefixed with "CORRECTION:" or markers.
  - Approximately similar length to original — maybe slightly longer if corrections add real new detail.

Output ONLY the synthesized description text. No JSON, no prose framing, no quotes."""


async def synthesize_enriched(
    original: str,
    corrections: list[str],
    *,
    llm: Optional[LLMClient] = None,
) -> str:
    """Merge original description + audit corrections into a single clean description.

    Used by the feedback-loop write-back so story.json stays single-source-of-truth
    (no parallel `audit_enrichments` list to maintain).
    """
    if not corrections:
        return original
    llm = llm or LLMClient(model=DEFAULT_LLM_MODEL)
    correction_text = "\n".join(f"- {c}" for c in corrections)
    return await llm.chat_text(
        system_prompt=_SYNTHESIZE_SYSTEM,
        user_prompt=(
            f"=== ORIGINAL ===\n{original}\n\n"
            f"=== AUDIT CORRECTIONS (incorporate inline) ===\n{correction_text}"
        ),
    )


async def run(
    image_path: str | Path,
    context: str,
    *,
    llm: Optional[LLMClient] = None,
    reference_images: Optional[list[tuple[str, str | Path]]] = None,
) -> AuditResult:
    """Audit one image against free-form source context. VLM self-directs axes.

    Parameters
    ----------
    image_path : the image to audit (PNG / JPG)
    context    : free-form ground-truth text — pass whatever's relevant from
                 StoryOutput / KeyframeOutput etc. (setting, look_description,
                 structural rules). The VLM reads this and decides what to check.
    llm        : optional LLMClient override (defaults to project default).
    reference_images : optional list of (label, path) tuples. Gets attached
                       AFTER the audit image, with labels embedded in the
                       prompt so VLM knows each ref's role. Use for identity
                       comparison (e.g. storyboard vs char anchors).
    """
    llm = llm or LLMClient(model=DEFAULT_LLM_MODEL)

    refs = reference_images or []
    refs_clause = ""
    if refs:
        lines = ["", "=== ATTACHED IMAGES (in order) ===",
                 "Image #1 = THE AUDIT TARGET (the image being judged)."]
        for i, (label, _) in enumerate(refs, start=2):
            lines.append(f"Image #{i} = REFERENCE: {label}")
        lines.append(
            "Compare the audit target (Image #1) against the references for identity / "
            "consistency wherever relevant. References are GROUND TRUTH for character "
            "look / location look — flag if Image #1 deviates."
        )
        refs_clause = "\n".join(lines)

    media = [{"type": "image", "path": str(image_path)}]
    for _, p in refs:
        media.append({"type": "image", "path": str(p)})

    raw = await llm.chat_json(
        system_prompt=_AUDIT_SYSTEM,
        user_prompt=(
            "=== SOURCE CONTEXT (ground truth) ===\n"
            f"{context}\n"
            f"{refs_clause}\n\n"
            "Examine the attached image (Image #1) and find any mismatches. "
            "Self-direct what dimensions to check based on what the context implies matters."
        ),
        media_attachments=media,
    )
    return AuditResult.model_validate(raw)


# ─── context builders ───────────────────────────────────────────────────
#
# These build the SOURCE CONTEXT string for two common use cases. The VLM
# still self-directs which specific axes to check — these helpers just
# enumerate the *categories* of dimension that tend to matter (era / culture
# / identity / physics / cardinality / structure). Caller can pass extra
# free-form rules by concatenating to the returned string.

def build_anchor_context(story, entity, kind: str) -> str:
    """Compose audit context for a CHARACTER or LOCATION anchor.

    Verifies the rendered anchor matches:
      - era / cultural / ethnicity context (from story.setting)
      - look description fidelity (face / hair / costume / equipment from
        entity.look_description)
      - anchor-quality conventions (isolated subject, neutral bg)
    """
    style_brief = getattr(story, "style_anchor", "")
    anchor_quality_clause = (
        "⚠️ HARD RULE FOR CHARACTER ANCHORS — neutral / studio background is CORRECT, NOT a defect. "
        "The anchor is an isolated identity-card image (no scene, no environment). "
        "If you see neutral / plain gray / white / flat-color background, DO NOT flag it as a missing scene. "
        "The story.setting governs ONLY the character (ethnicity / costume / equipment / era markers) — "
        "NOT the anchor's background. Background expectations only apply to LOCATION anchors and storyboards."
        if kind == "character"
        else (
            "⚠️ HARD RULE FOR LOCATION ANCHORS — establishing wide shot, NO people / characters / figures. "
            "Background, sky, lighting, weather, architecture matching setting IS the requirement. "
            "If you see characters in frame, flag that as blocking."
        )
    )
    return (
        f"STORY SETTING (era / culture / cast ethnicity / world context):\n"
        f"{story.setting}\n\n"
        f"VISUAL STYLE BRIEF:\n{style_brief}\n\n"
        f"{kind.upper()} look_description (ground truth):\n{entity.look_description}\n\n"
        f"{anchor_quality_clause}\n\n"
        "DIMENSION CATEGORIES THE VLM SHOULD AUTO-DERIVE AGAINST (pick what applies):\n"
        "- Era / period authenticity vs setting (no anachronistic objects ON THE CHARACTER)\n"
        "- Ethnicity / cast match vs setting (for character anchors)\n"
        "- Costume / accessory / equipment fidelity vs look_description\n"
        "- Architectural / environmental match vs setting (LOCATION anchors only)\n"
        "- DO NOT flag character-anchor background as wrong (neutral is correct)"
    )


def build_storyboard_context(story, shot) -> str:
    """Compose audit context for a multi-panel STORYBOARD sheet.

    Verifies (with LENIENT severity threshold — storyboard is intermediate
    artifact, gpt-image-2 has known limits with multi-panel composition;
    we want pass on "good enough" not "perfect"):
      - physics realism inside each panel + continuity across panels
      - identity preservation (chars in panels match anchor refs)
      - cardinality / conflict rules (prop counts match characters_present)
      - panel structure (count + grid layout + numbering)
      - per-panel content matches moment_description
      - era / cultural consistency across all panels
    """
    panels_brief = "\n".join(
        f"  - panel {i+1} t={list(p.time_range)}: "
        f"characters_present={p.characters_present}, "
        f"action={p.moment_description!r}, "
        f"dialogue={p.dialogue!r}"
        for i, p in enumerate(shot.panels)
    )
    grid_map = {
        1: "1x1", 2: "2x1", 3: "3x1",
        4: "2x2", 5: "3x2 (6th cell blank)", 6: "3x2",
    }
    expected_grid = grid_map.get(len(shot.panels), "3x2")
    chars_lib = json.dumps(
        [{"id": c.id, "role": c.role, "look": c.look_description}
         for c in story.characters],
        ensure_ascii=False, indent=2,
    )
    return (
        f"STORY SETTING:\n{story.setting}\n\n"
        f"VISUAL STYLE BRIEF:\n{getattr(story, 'style_anchor', '')}\n\n"
        f"STORYBOARD STRUCTURE (expected):\n"
        f"- panel count: {len(shot.panels)}\n"
        f"- grid layout: {expected_grid}, reading order top-row left-to-right then next row\n"
        f"- each panel has a large white index number (1..N) in its top-left corner\n\n"
        f"PER-PANEL CONTENT (each panel must visually depict its action):\n{panels_brief}\n\n"
        f"CHARACTER LIBRARY (each character appears with their declared equipment, NO duplicates):\n{chars_lib}\n\n"
        "⚠️ LENIENT SEVERITY THRESHOLD FOR STORYBOARDS — this is an INTERMEDIATE artifact "
        "rendered by gpt-image-2's multi-panel mode (which has known limits). Reserve "
        "'blocking' for EGREGIOUS violations only:\n"
        "  ✗ blocking: completely wrong ethnicity of characters; wrong era/cultural context "
        "(modern in ancient story); panel count totally wrong (0 panels, or 10 when expected 4); "
        "3+ extra unaccounted props/characters; main subject missing from a panel.\n"
        "  ⚠ warning (NOT blocking): minor identity drift (similar face but not identical); "
        "small pose / physics imperfections; slight costume color drift; missing number labels; "
        "minor scale issues; small environmental detail mismatches; one panel slightly off.\n"
        "If you're not 100% sure the issue is BLOCKING-egregious, mark it warning. We want "
        "the storyboard to pass on 'good enough', not 'pixel-perfect'.\n\n"
        "DIMENSION CATEGORIES THE VLM SHOULD AUTO-DERIVE AGAINST (pick what applies):\n"
        "- Physics realism (warning unless completely impossible, e.g. floating without context)\n"
        "- Identity preservation: characters in panels visually match (a) their look_description AND (b) their attached anchor reference images (Image #2, #3, ...). MINOR drift = warning. COMPLETELY DIFFERENT person = blocking.\n"
        "- Cardinality / conflict rules: prop count vs characters_present × their equipment. 1 extra prop = warning. 3+ extra OR completely impossible scene = blocking.\n"
        "- Panel structure: count matches expected. Missing numbers = warning. Completely wrong grid = blocking.\n"
        "- Per-panel content match: each panel's visible action roughly matches moment_description (don't require word-for-word match).\n"
        "- Era / cultural consistency: blocking only if clearly anachronistic / wrong culture.\n"
        "- Dialogue plausibility: skip this check (storyboard is still image, lip-sync N/A)."
    )


def build_panel_context(
    story,
    shot,
    panel_idx: int,
    panel_composition_note: str = "",
) -> str:
    """Compose audit context for ONE PANEL cropped from a storyboard sheet.

    Use STRICT severity (unlike `build_storyboard_context`'s LENIENT) — per-panel
    audit's job is exactly to catch per-panel failures that the whole-sheet
    LENIENT audit misses. The image stage is the cheap place to catch errors;
    a single bad panel cascades into bad video downstream since Seedance follows
    the storyboard faithfully.

    Caller flow (see keyframe/agent.py `_render_shot_visuals_with_audit`):
      1. crop each cell from rendered sheet via `_grid_dims(N)` layout
      2. for each panel: build_panel_context() + audit.run(panel_crop)
      3. aggregate per-panel verdicts; any blocking → fail the whole sheet
      4. retry with corrections labeled per-panel so the model knows which
         cell to fix next round
    """
    panel = shot.panels[panel_idx]
    chars_str = (
        ", ".join(panel.characters_present)
        if panel.characters_present
        else "(none — this is a no-character panel)"
    )
    style_brief = getattr(story, "style_anchor", "")
    note_clause = (
        f"PLANNER'S COMPOSITION NOTE (framing intent):\n{panel_composition_note}\n\n"
        if panel_composition_note
        else ""
    )
    return (
        f"STORY SETTING:\n{story.setting}\n\n"
        f"VISUAL STYLE BRIEF:\n{style_brief}\n\n"
        f"This image is PANEL {panel_idx + 1} of {len(shot.panels)} cropped from a "
        f"storyboard sheet for shot {shot.shot_id}.\n\n"
        f"PANEL TIME RANGE: {panel.time_range[0]}-{panel.time_range[1]}s of the shot.\n"
        f"REQUIRED CHARACTERS IN FRAME: {chars_str}\n"
        f"PRIMARY LOCATION: {shot.primary_location}\n\n"
        f"PANEL MOMENT (the canonical action / visual state this panel must depict):\n"
        f"{panel.moment_description}\n\n"
        f"{note_clause}"
        "⚠️ STRICT SEVERITY — per-panel audit catches failures that cascade into bad video. "
        "Mark BLOCKING if:\n"
        "  ✗ any required character listed above is missing or unrecognizable;\n"
        "  ✗ the distinguishing visual state from PANEL MOMENT is NOT depicted "
        "(e.g. moment says 'tiger sliced in half' but tiger appears whole; "
        "'character kneeling on one knee' but character is standing; "
        "'two halves of beast' but only one body visible; "
        "'extreme close-up' but rendered as wide shot, or vice versa);\n"
        "  ✗ era / culture / setting is wrong (modern in ancient story, wrong ethnicity);\n"
        "  ✗ scene shows panel borders, panel numbers, text overlays, or other multi-panel "
        "sheet artifacts inside this single panel (it should look like ONE clean cinematic frame).\n"
        "Warning (NOT blocking): minor identity drift, small pose imperfections, slight color "
        "drift, environmental detail mismatches.\n\n"
        "DIMENSIONS TO CHECK:\n"
        "- presence of required characters\n"
        "- correctness of the distinguishing action / visual state from PANEL MOMENT\n"
        "- framing / scale match vs composition note\n"
        "- props / equipment / weapons matching characters' canonical look\n"
        "- era / culture consistency"
    )
