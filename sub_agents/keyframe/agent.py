"""KeyframeAgent — image factory.

Phase 1: render story-level anchors (character + location variants) in parallel.
Phase 2: for each shot in parallel, LLM-plan composition → render storyboard
         sheet, capture composition notes. (Blocking diagram dropped — camera
         info lives in ShotPromptAgent's [CAMERA] text section.)

gpt-image-2 calls are inline (not going through ``inference/generation/`` registry)
per prototyping scope. ``inference.clients.LLMClient`` reused for planning.
"""
from __future__ import annotations

import asyncio
import base64
import json
import os
from pathlib import Path
from typing import Optional

from inference.clients import LLMClient

from .. import DEFAULT_LLM_MODEL
from .._guidance_loader import active_categories_for_shot, load_guidance
from ..audit import agent as audit
from ..story.schema import Character, Location, ShotIntent, StoryOutput
from .schema import KeyframeOutput, ShotVisualPack


_CONCURRENCY = asyncio.Semaphore(8)  # gpt-image-2 + LLM, conservative

# VLM audit loop. When _AUDIT_ENABLED=1, both anchors AND storyboards go through
# audit + retry loop. Storyboard audit context uses LENIENT severity thresholds
# (only EGREGIOUS issues blocking; minor drift → warning → no retry).
# Use FW_SUB_AGENTS_AUDIT_STORYBOARD=0 to disable storyboard audit specifically.
_AUDIT_ENABLED = os.environ.get("FW_SUB_AGENTS_AUDIT", "0") == "1"
_AUDIT_STORYBOARD = os.environ.get("FW_SUB_AGENTS_AUDIT_STORYBOARD", "1") == "1"
_AUDIT_MAX_ATTEMPTS = int(os.environ.get("FW_SUB_AGENTS_AUDIT_MAX_ATTEMPTS", "3"))


async def run(
    story: StoryOutput,
    *,
    output_dir: Path,
    llm: Optional[LLMClient] = None,
) -> KeyframeOutput:
    """Render all anchors + per-shot visuals. Fans out across all variants & shots."""
    llm = llm or LLMClient(model=DEFAULT_LLM_MODEL)
    anchors_dir = output_dir / "anchors"
    shots_dir = output_dir / "shots"
    anchors_dir.mkdir(parents=True, exist_ok=True)
    shots_dir.mkdir(parents=True, exist_ok=True)

    # Phase 1 — anchors fan-out (style + chars + locations, 1 each, no variants)
    # (Blocking diagram dropped — camera info lives in ShotPromptAgent's [CAMERA] section.)
    # Combine setting + style_anchor into one "world context" brief passed
    # to every anchor render so chars/locs inherit cultural / era / ethnicity.
    world_brief = f"{story.setting} | {story.style_anchor}"

    if _AUDIT_ENABLED:
        print(f"[keyframe] audit ON (max_attempts={_AUDIT_MAX_ATTEMPTS})")
        anchor_tasks: list = [_render_style_anchor_with_audit(story, out_dir=anchors_dir)]
        for char in story.characters:
            anchor_tasks.append(
                _render_anchor_with_audit(
                    char, kind="character", story=story,
                    out_dir=anchors_dir, style_brief=world_brief,
                )
            )
        for loc in story.locations:
            anchor_tasks.append(
                _render_anchor_with_audit(
                    loc, kind="location", story=story,
                    out_dir=anchors_dir, style_brief=world_brief,
                )
            )
    else:
        anchor_tasks = [_render_style_anchor(story, out_dir=anchors_dir)]
        for char in story.characters:
            anchor_tasks.append(
                _render_anchor(char, kind="character", out_dir=anchors_dir, style_brief=world_brief)
            )
        for loc in story.locations:
            anchor_tasks.append(
                _render_anchor(loc, kind="location", out_dir=anchors_dir, style_brief=world_brief)
            )
    anchor_results = await asyncio.gather(*anchor_tasks)

    # When audit ON, anchor_results are 4-tuples (kind, id, path, corrections).
    # Without audit they're 3-tuples. Normalize to extract paths + (audit) collect corrections.
    style_anchor_path = None
    character_anchors = {}
    location_anchors = {}
    char_corrs_collected: dict[str, list[str]] = {}
    loc_corrs_collected: dict[str, list[str]] = {}
    style_corrs_collected: list[str] = []
    for res in anchor_results:
        if len(res) == 4:
            k, eid, p, corrs = res
        else:
            k, eid, p = res
            corrs = []
        if k == "style":
            style_anchor_path = p
            style_corrs_collected = corrs
        elif k == "character":
            character_anchors[eid] = p
            if corrs:
                char_corrs_collected[eid] = corrs
        elif k == "location":
            location_anchors[eid] = p
            if corrs:
                loc_corrs_collected[eid] = corrs

    # Phase 2 — per-shot visuals fan-out (storyboards). Audit gated separately
    # from anchor audit (see _AUDIT_STORYBOARD docstring); default OFF.
    if _AUDIT_ENABLED and _AUDIT_STORYBOARD:
        shot_tasks = [
            _render_shot_visuals_with_audit(
                shot, story, character_anchors, location_anchors, style_anchor_path,
                out_dir=shots_dir, llm=llm,
            )
            for shot in story.shots
        ]
    else:
        if _AUDIT_ENABLED:
            print("[keyframe] storyboard audit OFF (FW_SUB_AGENTS_AUDIT_STORYBOARD=0)")
        shot_tasks = [
            _render_shot_visuals(
                shot, story, character_anchors, location_anchors, style_anchor_path,
                out_dir=shots_dir, llm=llm,
            )
            for shot in story.shots
        ]
    shot_packs_raw = await asyncio.gather(*shot_tasks, return_exceptions=True)
    shot_visuals = {}
    shot_corrs_collected: dict[str, list[str]] = {}
    for shot, raw in zip(story.shots, shot_packs_raw):
        if isinstance(raw, Exception):
            print(f"  [SHOT FAILED] {shot.shot_id}: {type(raw).__name__}: {raw}")
            continue
        # Audit ON path returns (pack, corrections); non-audit path returns pack
        if isinstance(raw, tuple):
            pack, corrs = raw
            if corrs:
                shot_corrs_collected[shot.shot_id] = corrs
        else:
            pack = raw
        shot_visuals[shot.shot_id] = pack

    # ── Feedback loop: LLM-synthesize corrections INTO the primary fields ──
    # (option B "Rewrite") — single source of truth, no parallel audit_enrichments list.
    if char_corrs_collected or loc_corrs_collected or style_corrs_collected or shot_corrs_collected:
        synthesize_tasks = []
        # Anchor entities: rewrite look_description / style_anchor with corrections merged in
        char_targets = [(c, char_corrs_collected[c.id]) for c in story.characters if c.id in char_corrs_collected]
        loc_targets  = [(l, loc_corrs_collected[l.id])  for l in story.locations  if l.id in loc_corrs_collected]
        shot_targets = [(s, shot_corrs_collected[s.shot_id]) for s in story.shots if s.shot_id in shot_corrs_collected]

        for c, corrs in char_targets:
            synthesize_tasks.append(audit.synthesize_enriched(c.look_description, corrs, llm=llm))
        for l, corrs in loc_targets:
            synthesize_tasks.append(audit.synthesize_enriched(l.look_description, corrs, llm=llm))
        if style_corrs_collected:
            synthesize_tasks.append(audit.synthesize_enriched(story.style_anchor, style_corrs_collected, llm=llm))
        for s, corrs in shot_targets:
            synthesize_tasks.append(audit.synthesize_enriched(s.audit_notes or "", corrs, llm=llm))

        synthesized = await asyncio.gather(*synthesize_tasks)
        idx = 0
        for c, _ in char_targets:
            c.look_description = synthesized[idx]; idx += 1
        for l, _ in loc_targets:
            l.look_description = synthesized[idx]; idx += 1
        if style_corrs_collected:
            story.style_anchor = synthesized[idx]; idx += 1
        for s, _ in shot_targets:
            s.audit_notes = synthesized[idx]; idx += 1

        story_path = output_dir.parent / "story.json"
        story_path.write_text(story.model_dump_json(indent=2), encoding="utf-8")
        n_total = len(char_targets) + len(loc_targets) + (1 if style_corrs_collected else 0) + len(shot_targets)
        print(f"[feedback] story.json rewritten: {n_total} entity descriptions enriched (Option B / synthesize)")

    return KeyframeOutput(
        style_anchor_path=style_anchor_path,
        character_anchors=character_anchors,
        location_anchors=location_anchors,
        shot_visuals=shot_visuals,
    )


# ─── Phase 1 ─────────────────────────────────────────────────────────────

# 3-view anchor labels — PIL-stamped post-render so downstream i2i can
# identify which section is which orientation. Universal across all
# characters and locations (no per-instance customization) — model
# interprets "FRONT" / "BACK" of a location the same way it interprets
# the front of a character: pick the most iconic / approach view, then
# 180° opposite for BACK. OVERHEAD is always bird's-eye.
_CHAR_3VIEW_LABELS = ["FRONT", "SIDE", "BACK"]
_LOC_3VIEW_LABELS = ["FRONT", "BACK", "OVERHEAD"]


def _stamp_3view_labels(out_path: Path, labels: list[str]) -> None:
    """Overlay direction labels on a 3-section anchor sheet. Small font
    (32pt) + black outline so downstream i2i prompts can be told to treat
    these as direction tags (e.g. 'use the FRONT section of [Image 1]')
    without the labels themselves dominating the visual signal.
    """
    from PIL import Image, ImageDraw, ImageFont

    img = Image.open(out_path).convert("RGB")
    w, h = img.size
    third_w = w // 3
    try:
        font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32
        )
    except (OSError, IOError):
        font = ImageFont.load_default()
    draw = ImageDraw.Draw(img)
    for i, label in enumerate(labels):
        x = i * third_w + 14
        y = 12
        for dx in (-2, -1, 0, 1, 2):
            for dy in (-2, -1, 0, 1, 2):
                draw.text((x + dx, y + dy), label, fill="black", font=font)
        draw.text((x, y), label, fill="white", font=font)
    img.save(out_path)


async def _render_style_anchor(
    story: StoryOutput, *, out_dir: Path, correction: str = "",
) -> tuple[str, str, str]:
    """Render the story-wide visual style reference via gpt-image-2 t2i.

    Style anchor stays single-view (no 3-view concept) — it's an abstract
    aesthetic plate (empty street / texture / lighting study), used as an
    i2i ref at storyboard rendering time for color/lighting consistency.
    NOT fed to the video stage (it leaks as a literal subject scene there).
    """
    prompt = (
        "Photorealistic single cinematic frame at 1536x1024, live-action 35mm film still "
        "aesthetic, NOT illustration, NOT anime, NOT concept art, NOT painting.\n\n"
        "Visual STYLE reference image — capture LOOK AND FEEL only, no specific characters, "
        "no specific scene narrative. Show a single neutral frame (e.g. an empty street / "
        "abstract texture / lighting study) that fully conveys the following aesthetic:\n"
        f"{story.style_anchor}"
    )
    if correction:
        prompt = prompt + "\n\n" + correction
    out_path = out_dir / "_style.png"
    await _gpt_image_2_call(prompt=prompt, out_path=out_path, refs=None, size="1536x1024")
    return ("style", "_style", str(out_path))


async def _render_anchor(
    entity,
    *,
    kind: str,
    out_dir: Path,
    style_brief: str = "",
    correction: str = "",
) -> tuple[str, str, str]:
    """Render one entity anchor as a 3-view sheet via gpt-image-2 t2i.

    entity: Character (kind="character") or Location (kind="location") — exposes
            ``.id`` and ``.look_description`` (Location also has
            ``.primary_axis_hint`` for per-location PRIMARY definition).

    Output: a single 1536x1024 image divided into 3 equal-width vertical
    sections. PIL-stamped with direction labels (FRONT / SIDE / BACK for
    characters; PRIMARY / REVERSE / OVERHEAD for locations). Downstream
    i2i (storyboard render) can reference specific sections by label.

    correction: optional VLM-supplied correction text appended at the
    bottom; used by the audit loop on retry attempts.
    """
    if kind == "character":
        setting_clause = f"\nWorld / era / cultural context: {style_brief}" if style_brief else ""
        prompt = (
            "Photorealistic studio photograph of a single subject, shot on Arri Alexa 35 "
            "with a 35mm prime lens — live-action film still aesthetic, NOT illustration, "
            "NOT anime, NOT concept art, NOT painting.\n\n"
            "The single 16:9 widescreen image is composed of THREE equal-width vertical "
            "sections, each showing the SAME real human subject from a different angle, "
            "photographed in the same studio session:\n"
            "- LEFT section: FRONT view (subject facing camera straight on, full body)\n"
            "- MIDDLE section: SIDE view (subject's left profile, 90 degrees turned, full body)\n"
            "- RIGHT section: BACK view (subject's back facing camera, full body)\n\n"
            "Strict rules:\n"
            "- Treat this as a real photo shoot of an actor in costume — not a character "
            "sheet, not a turnaround render. Face, skin, hair, fabric, leather, metal must "
            "look like photography.\n"
            "- All three sections must depict the EXACT same human identity (face, age, "
            "build, hair, costume, same actor, same lighting setup).\n"
            "- Neutral pose (standing relaxed, arms at sides), neutral expression.\n"
            "- Even soft studio lighting, neutral mid-gray seamless backdrop, no scene "
            "props, no environmental context.\n\n"
            f"Subject: {entity.look_description}"
            f"{setting_clause}"
        )
        labels = _CHAR_3VIEW_LABELS
    elif kind == "location":
        setting_clause = f"\nWorld / era context: {style_brief}" if style_brief else ""
        prompt = (
            "Photorealistic on-location photography of a single physical place, shot on "
            "Arri Alexa 35 — live-action film still aesthetic, NOT illustration, NOT anime, "
            "NOT concept art, NOT painting.\n\n"
            "The single 16:9 widescreen image is composed of THREE equal-width vertical "
            "sections, each showing the SAME real-world location from a different camera "
            "position, captured in the same shoot:\n"
            "- LEFT section: FRONT view — the iconic / canonical / approach view of this "
            "location, the camera angle a director would default to for establishing "
            "this place to an audience.\n"
            "- MIDDLE section: BACK view — 180-degree opposite of FRONT (camera turned "
            "around, looking back from where FRONT was facing toward).\n"
            "- RIGHT section: OVERHEAD view — bird's-eye / aerial / top-down view revealing "
            "spatial layout, dominant pathways, roof lines, arrangement of structures.\n\n"
            "Strict rules:\n"
            "- On-location photography of a real physical place — not a matte painting, "
            "not a concept render. Materials must look like photography.\n"
            "- All three sections depict the EXACT same physical location (same architecture, "
            "era, atmosphere, lighting, time of day).\n"
            "- NO people / characters / figures in any section.\n\n"
            f"Location: {entity.look_description}"
            f"{setting_clause}"
        )
        labels = _LOC_3VIEW_LABELS
    else:
        raise ValueError(f"unknown anchor kind: {kind!r}")
    if correction:
        prompt = prompt + "\n\n" + correction
    out_path = out_dir / f"{entity.id}.png"
    await _gpt_image_2_call(prompt=prompt, out_path=out_path, refs=None, size="1536x1024")
    _stamp_3view_labels(out_path, labels)
    return (kind, entity.id, str(out_path))


# ─── Audit-loop wrappers (opt-in via FW_SUB_AGENTS_AUDIT=1) ──────────────


def _format_accumulated_corrections(corrections: list[str]) -> str:
    """Render the running list of VLM corrections as appendable prompt text."""
    if not corrections:
        return ""
    return "\n\n".join(
        f"CORRECTION (round {i+1}): {c}" for i, c in enumerate(corrections)
    )


async def _render_anchor_with_audit(
    entity, *, kind: str, story: StoryOutput, out_dir: Path, style_brief: str = "",
) -> tuple[str, str, str, list[str]]:
    """Render-audit-retry loop for character / location anchors.

    Resume optimization: if the PNG already exists on disk, audit it FIRST —
    only re-render if it fails audit. Skip re-render of already-passing anchors.

    Returns 4-tuple (kind, id, path, corrections_from_this_run).
    """
    ctx = audit.build_anchor_context(story, entity, kind)
    out_path_pre = out_dir / f"{entity.id}.png"

    # Resume skip: if PNG exists, audit it; if passes, no render needed.
    if out_path_pre.exists():
        verdict = await audit.run(out_path_pre, ctx)
        if verdict.passed:
            print(f"  [audit] {entity.id} EXISTING png passed — skip re-render")
            return ("character" if kind == "character" else "location", entity.id, str(out_path_pre), [])
        print(f"  [audit] {entity.id} existing png failed: {[i.dimension for i in verdict.issues]}; will re-render")
        corrections: list[str] = [verdict.repair_prompt_addition]
    else:
        corrections = []

    result = None
    for attempt in range(_AUDIT_MAX_ATTEMPTS):
        full_corr = _format_accumulated_corrections(corrections)
        result = await _render_anchor(
            entity, kind=kind, out_dir=out_dir,
            style_brief=style_brief, correction=full_corr,
        )
        verdict = await audit.run(result[2], ctx)
        if verdict.passed:
            print(f"  [audit] {entity.id} passed (attempt {attempt+1}/{_AUDIT_MAX_ATTEMPTS})")
            return (*result, corrections)
        flags = [i.dimension for i in verdict.issues]
        print(f"  [audit] {entity.id} attempt {attempt+1} failed: {flags}")
        corrections.append(verdict.repair_prompt_addition)
    print(f"  [audit] {entity.id} EXHAUSTED {_AUDIT_MAX_ATTEMPTS}; accepting last render")
    return (*result, corrections)


async def _render_style_anchor_with_audit(
    story: StoryOutput, *, out_dir: Path,
) -> tuple[str, str, str, list[str]]:
    """Audit loop for the style anchor. Returns 4-tuple, last item = full corrections."""
    ctx = (
        f"STORY SETTING:\n{story.setting}\n\n"
        f"VISUAL STYLE BRIEF (the goal):\n{story.style_anchor}\n\n"
        "This is a story-wide VISUAL STYLE reference image — no specific characters / "
        "subject / scene narrative. Verify only that the rendered image faithfully "
        "captures the style brief (color palette / lighting key / aesthetic / texture / "
        "contrast). DO NOT flag missing characters or scene specifics — those aren't expected here."
    )
    # Resume skip: if _style.png exists and passes audit, no re-render.
    out_path_pre = out_dir / "_style.png"
    if out_path_pre.exists():
        verdict = await audit.run(out_path_pre, ctx)
        if verdict.passed:
            print(f"  [audit] _style EXISTING png passed — skip re-render")
            return ("style", "_style", str(out_path_pre), [])
        print(f"  [audit] _style existing png failed; will re-render")
        corrections: list[str] = [verdict.repair_prompt_addition]
    else:
        corrections = []

    result = None
    for attempt in range(_AUDIT_MAX_ATTEMPTS):
        full_corr = _format_accumulated_corrections(corrections)
        result = await _render_style_anchor(story, out_dir=out_dir, correction=full_corr)
        verdict = await audit.run(result[2], ctx)
        if verdict.passed:
            print(f"  [audit] _style passed (attempt {attempt+1}/{_AUDIT_MAX_ATTEMPTS})")
            return (*result, corrections)
        flags = [i.dimension for i in verdict.issues]
        print(f"  [audit] _style attempt {attempt+1} failed: {flags}")
        corrections.append(verdict.repair_prompt_addition)
    print(f"  [audit] _style EXHAUSTED; accepting last render")
    return (*result, corrections)


async def _audit_panels(
    storyboard_path: Path,
    shot: ShotIntent,
    story: StoryOutput,
    panel_composition_notes: Optional[list[str]] = None,
) -> tuple[bool, str, list[str]]:
    """Per-panel storyboard audit. Crops each cell from the sheet (via
    ``_grid_dims`` layout) and runs ``audit.run`` per panel in parallel.

    Returns ``(all_pass, combined_repair_prompt, per_panel_failure_flags)``.

    Why per-panel (vs whole-sheet via ``build_storyboard_context``): whole-sheet
    LENIENT audit misses panel-specific failures (e.g. panel 4 'tiger cleaved
    in half' rendered as 'tiger intact' — whole-sheet passes because most
    panels look OK overall, but the one wrong panel cascades into bad video).
    Per-panel STRICT audit catches these on the cheap (image) side before
    the expensive (video) side burns money on bad input.

    ``panel_composition_notes``: optional planner notes per panel (planner's
    framing intent). Pass ``None`` on the resume / cached-render path where
    no fresh plan was generated — context falls back to story-level
    ``panel.moment_description`` only, which is still STRICT enough.
    """
    import tempfile
    from PIL import Image

    n_panels = len(shot.panels)
    cols, rows = _grid_dims(n_panels)
    sheet = Image.open(storyboard_path).convert("RGB")
    w, h = sheet.size
    panel_w, panel_h = w // cols, h // rows

    notes = panel_composition_notes or [""] * n_panels

    with tempfile.TemporaryDirectory(prefix=f"panel_audit_{shot.shot_id}_") as tmpdir:
        tmp = Path(tmpdir)
        crop_paths: list[Path] = []
        for i in range(n_panels):
            col, row = i % cols, i // cols
            box = (col * panel_w, row * panel_h, (col + 1) * panel_w, (row + 1) * panel_h)
            p = tmp / f"p{i + 1}.png"
            sheet.crop(box).save(p)
            crop_paths.append(p)

        verdicts = await asyncio.gather(*[
            audit.run(
                crop_paths[i],
                audit.build_panel_context(story, shot, i, notes[i]),
            )
            for i in range(n_panels)
        ])

    all_pass = all(v.passed for v in verdicts)
    combined_repair = "\n\n".join(
        f"PANEL {i + 1} NEEDS FIX: {v.repair_prompt_addition}"
        for i, v in enumerate(verdicts)
        if not v.passed
    )
    flags = [
        f"P{i + 1}:{[issue.dimension for issue in v.issues]}"
        for i, v in enumerate(verdicts)
        if not v.passed
    ]
    return all_pass, combined_repair, flags


async def _render_shot_visuals_with_audit(
    shot: ShotIntent,
    story: StoryOutput,
    character_anchors: dict[str, str],
    location_anchors: dict[str, str],
    style_anchor_path: str,
    *,
    out_dir: Path,
    llm: LLMClient,
) -> tuple[ShotVisualPack, list[str]]:
    """Audit loop for storyboard render. Returns (pack, all_corrections).

    Per-panel STRICT audit replaces the previous whole-sheet LENIENT path
    (cf. ``build_storyboard_context``'s "good enough" stance) — see
    ``_audit_panels`` docstring for rationale.

    Caller writes all_corrections back to story.shots[i].audit_enrichments.
    """
    storyboard_path_pre = out_dir / f"{shot.shot_id}_storyboard.png"

    # Resume skip: if storyboard exists and ALL panels pass per-panel audit,
    # no re-render. No planner notes available on resume — audit falls back
    # to panel.moment_description only.
    if storyboard_path_pre.exists():
        all_pass, combined_repair, flags = await _audit_panels(
            storyboard_path_pre, shot, story, panel_composition_notes=None
        )
        if all_pass:
            print(f"  [audit] {shot.shot_id} storyboard EXISTING png ALL panels passed — skip re-render")
            return (
                ShotVisualPack(
                    storyboard_image_path=str(storyboard_path_pre),
                    panel_composition_notes=[
                        f"(panel {i+1} cached)" for i in range(len(shot.panels))
                    ],
                    storyboard_prompt="(resumed from cached render — no fresh plan)",
                ),
                [],
            )
        print(f"  [audit] {shot.shot_id} existing storyboard panel fails: {flags}; will re-render")
        corrections_init: list[str] = [combined_repair]
    else:
        corrections_init = []

    plan = await _plan_shot_visuals(shot, story, llm)
    # shot.audit_notes was already passed to _plan_shot_visuals as constraint context
    # → already in plan["storyboard_prompt"]. No need to pre-load corrections again.

    shot_char_refs = list({
        character_anchors[cid]
        for panel in shot.panels
        for cid in panel.characters_present
        if cid in character_anchors
    })
    loc_ref = location_anchors.get(shot.primary_location)
    storyboard_refs = shot_char_refs + ([loc_ref] if loc_ref else []) + [style_anchor_path]
    storyboard_path = out_dir / f"{shot.shot_id}_storyboard.png"

    corrections: list[str] = list(corrections_init)
    final_prompt = plan["storyboard_prompt"]
    for attempt in range(_AUDIT_MAX_ATTEMPTS):
        full_corr = _format_accumulated_corrections(corrections)
        attempt_prompt = (
            plan["storyboard_prompt"] + "\n\n" + full_corr if full_corr
            else plan["storyboard_prompt"]
        )
        await _gpt_image_2_call(
            prompt=attempt_prompt,
            out_path=storyboard_path,
            refs=storyboard_refs or None,
            size="1536x1024",
        )
        _overlay_panel_numbers(storyboard_path, n_panels=len(shot.panels))
        final_prompt = attempt_prompt
        all_pass, combined_repair, flags = await _audit_panels(
            storyboard_path, shot, story,
            panel_composition_notes=plan["panel_composition_notes"],
        )
        if all_pass:
            print(f"  [audit] {shot.shot_id} ALL panels passed (attempt {attempt+1}/{_AUDIT_MAX_ATTEMPTS})")
            break
        print(f"  [audit] {shot.shot_id} attempt {attempt+1} panel fails: {flags}")
        corrections.append(combined_repair)
    else:
        print(f"  [audit] {shot.shot_id} storyboard EXHAUSTED; accepting last render")

    pack = ShotVisualPack(
        storyboard_image_path=str(storyboard_path),
        panel_composition_notes=plan["panel_composition_notes"],
        storyboard_prompt=final_prompt,
    )
    return (pack, corrections)


# ─── Phase 2 ─────────────────────────────────────────────────────────────

_SHOT_PLAN_SYSTEM = """You are a film director planning the visual staging for ONE continuous shot.

Produce ONE JSON object with exactly these keys:
- "panel_composition_notes": list[str] of length == number of input panels, IN ORDER. Each entry ~30-60 words describing framing (close/medium/wide), character placement, key visual elements, lighting beat.
- "storyboard_prompt": str — a detailed gpt-image-2 prompt to render a MULTI-PANEL STORYBOARD SHEET at 1536x1024 landscape, fitting {N} panels in a FIXED uniform grid by this exact mapping:
    N=1 → 1×1; N=2 → 2×1 (side by side); N=3 → 3×1 (single row); N=4 → 2×2; N=5 → 3×2 with the 6th cell blank gray; N=6 → 3×2.
  Reading order: top row left-to-right, then next row left-to-right (panel 1 = top-left, panel N = bottom-right). Each panel: equal size, 2px white border. **DO NOT have the model draw any text / numbers / timestamps inside panels** — image gen models hallucinate text. Panel index labels will be overlaid programmatically post-render. Panel content shows the key moment of its time range. Maintain character identity and scene continuity across panels by faithfully following the per-panel descriptions below.

  REFERENCE IMAGE STRUCTURE — every i2i ref attached to this storyboard render is a LABELED 3-section card:
    * Character anchors: 3 vertical sections labeled FRONT / SIDE / BACK (white text in upper-left of each section).
    * Location anchors: 3 vertical sections labeled FRONT / BACK / OVERHEAD (FRONT = canonical iconic approach view; BACK = 180° opposite; OVERHEAD = bird's-eye).
    * Style anchor: single-section abstract aesthetic plate (no labels).
  When a panel needs a specific orientation (e.g. an over-the-shoulder back shot of a character, or an aerial wide of a location), explicitly tell the model in your panel description which section to draw from — e.g. "use the BACK section of the li_mo character anchor" or "use the OVERHEAD section of the west_market location anchor". Do NOT include the section labels themselves in the rendered output; they are direction tags only.

  STYLE: photorealistic live-action 35mm film still aesthetic, NOT illustration, NOT anime, NOT concept art, NOT painting. Apply {style_anchor brief} on top of that photoreal base.

Apply the active GUIDANCE DOCS (passed below) as the aesthetic / vocabulary axis for storyboard_prompt and panel_composition_notes — body-horror panels depict material decay / pulsing veins; action-fight panels depict mid-air impact frames / motion blur; emotional close-ups depict micro-expressions / light play; etc.

Output ONLY the JSON, no surrounding prose, no code fences."""


async def _render_shot_visuals(
    shot: ShotIntent,
    story: StoryOutput,
    character_anchors: dict[str, str],
    location_anchors: dict[str, str],
    style_anchor_path: str,
    *,
    out_dir: Path,
    llm: LLMClient,
) -> ShotVisualPack:
    plan = await _plan_shot_visuals(shot, story, llm)

    # Storyboard i2i refs (gpt-image-2 multi-image edit):
    #   [char anchors used in this shot] + [loc anchor] + [style anchor]
    # — identity, scene, AND style all anchored.
    shot_char_refs = list({
        character_anchors[cid]
        for panel in shot.panels
        for cid in panel.characters_present
        if cid in character_anchors
    })
    loc_ref = location_anchors.get(shot.primary_location)
    storyboard_refs = shot_char_refs + ([loc_ref] if loc_ref else []) + [style_anchor_path]

    storyboard_path = out_dir / f"{shot.shot_id}_storyboard.png"

    await _gpt_image_2_call(
        prompt=plan["storyboard_prompt"],
        out_path=storyboard_path,
        refs=storyboard_refs or None,
        size="1536x1024",
    )
    # PIL overlay panel index labels — gpt-image-2 writes text unreliably, so we
    # render storyboard text-free and stamp 1/2/3 in known grid positions here.
    _overlay_panel_numbers(storyboard_path, n_panels=len(shot.panels))

    return ShotVisualPack(
        storyboard_image_path=str(storyboard_path),
        panel_composition_notes=plan["panel_composition_notes"],
        storyboard_prompt=plan["storyboard_prompt"],
    )


async def _plan_shot_visuals(
    shot: ShotIntent, story: StoryOutput, llm: LLMClient,
) -> dict:
    active_guidance = load_guidance(active_categories_for_shot(shot))
    payload = {
        "shot": shot.model_dump(mode="json"),
        "characters": [c.model_dump(mode="json") for c in story.characters],
        "locations": [l.model_dump(mode="json") for l in story.locations],
        "setting": story.setting,
        "style_anchor": story.style_anchor,
        # shot.audit_notes carries persisted audit constraints from prior runs
        # of this same shot — planner must respect them as hard rules.
        "audit_notes_from_prior_runs": shot.audit_notes or "(none — first render of this shot)",
    }
    user_prompt = (
        json.dumps(payload, ensure_ascii=False, indent=2)
        + "\n\n=== ACTIVE GUIDANCE DOCS (apply as aesthetic / vocabulary axis) ===\n\n"
        + active_guidance
    )
    return await llm.chat_json(
        system_prompt=_SHOT_PLAN_SYSTEM,
        user_prompt=user_prompt,
    )


# ─── Storyboard panel-number overlay ─────────────────────────────────────

def _grid_dims(n: int) -> tuple[int, int]:
    """Map panel count to fixed (cols, rows) grid. Matches the mapping spec'd
    into _SHOT_PLAN_SYSTEM, so PIL overlay positions match gpt-image-2's layout."""
    return {
        1: (1, 1), 2: (2, 1), 3: (3, 1),
        4: (2, 2), 5: (3, 2), 6: (3, 2),
    }.get(n, (3, 2))  # fallback for >6


def _overlay_panel_numbers(image_path: Path, *, n_panels: int) -> None:
    """Open the rendered storyboard and stamp '1', '2', ... in each panel's
    top-left corner using PIL.ImageDraw. Reliable text where image-gen can't.
    """
    from PIL import Image, ImageDraw, ImageFont

    img = Image.open(image_path).convert("RGB")
    w, h = img.size
    cols, rows = _grid_dims(n_panels)
    panel_w, panel_h = w // cols, h // rows
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 96
        )
    except (OSError, IOError):
        font = ImageFont.load_default()

    for i in range(n_panels):
        col, row = i % cols, i // cols
        x = col * panel_w + 24
        y = row * panel_h + 16
        text = str(i + 1)
        # 4px black outline for legibility on any background
        for dx in (-4, -2, 0, 2, 4):
            for dy in (-4, -2, 0, 2, 4):
                draw.text((x + dx, y + dy), text, fill="black", font=font)
        draw.text((x, y), text, fill="white", font=font)

    img.save(image_path)


# ─── nano-banana 2 anchor call ──────────────────────────────────────────
# Reuses the existing GeminiImageService (CF AI Gateway native-Gemini path,
# model id from INFERENCE_IMAGE_MODEL in .env, default gemini-3.1-flash-image-preview).
# Picked specifically for identity preservation on canonical anchors.

async def _nano_banana_call(*, prompt: str, out_path: Path) -> None:
    from inference.generation.image_generators.service import GeminiImageService

    service = GeminiImageService()  # reads GEMINI_API_KEY / GEMINI_BASE_URL / INFERENCE_IMAGE_MODEL
    async with _CONCURRENCY:
        result = await service.generate_image(prompt=prompt)
    out_path.write_bytes(result.bytes)


# ─── gpt-image-2 inline call ─────────────────────────────────────────────
# Used for storyboard sheet rendering (NOT for anchors).
# Direct OpenAI (api.openai.com). Reads OPENAI_API_KEY from .env.

import os


async def _gpt_image_2_call(
    *, prompt: str, out_path: Path, refs: Optional[list[str]], size: str = "1024x1024",
) -> None:
    """gpt-image-2 generate (with optional multi-image i2i edit) at the given size.

    Valid sizes for gpt-image-1 family: 1024x1024 / 1024x1536 / 1536x1024 / auto.
    Multi-image edit: pass `image=[file1, file2, ...]` — model blends all refs
    (identity / scene / style depending on what's in each).
    """
    from openai import AsyncOpenAI

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Image generation needs OPENAI_API_KEY in .env")
    client = AsyncOpenAI(api_key=api_key)

    async with _CONCURRENCY:
        if refs:
            file_handles = [open(p, "rb") for p in refs]
            try:
                try:
                    result = await client.images.edit(
                        model="gpt-image-2",
                        image=file_handles if len(file_handles) > 1 else file_handles[0],
                        prompt=prompt,
                        n=1,
                        size=size,
                    )
                except Exception as e:
                    print(f"[gpt-image-2] i2i edit failed ({e}); falling back to text-only.")
                    try:
                        result = await client.images.generate(
                            model="gpt-image-2", prompt=prompt, n=1, size=size,
                        )
                    except Exception as e2:
                        raise RuntimeError(
                            f"gpt-image-2 BOTH i2i AND text-only failed (likely safety filter on prompt content). "
                            f"out_path={out_path}, i2i_err={e}, text_err={e2}"
                        ) from e2
            finally:
                for f in file_handles:
                    f.close()
        else:
            result = await client.images.generate(
                model="gpt-image-2", prompt=prompt, n=1, size=size,
            )

    b64 = result.data[0].b64_json
    out_path.write_bytes(base64.b64decode(b64))
