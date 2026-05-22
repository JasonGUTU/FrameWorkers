"""ShotPromptAgent — assembles video-gen text prompt + image set per shot.

One LLM call per shot. Inputs:
  - shot (ShotIntent) + story (for character/location lookup)
  - KeyframeAgent's anchors + this shot's visual pack
  - All unique categories from this shot's panels → load matching guidance docs

Output: ShotPromptOutput with text_prompt ([Image N] role-tagged) +
        ordered video_image_refs. Driver hands the pair to the configured
        video backend (pipeline owns backend choice, not this agent).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from inference.clients import LLMClient

from .. import DEFAULT_LLM_MODEL
from .._categories import ShotCategory
from .._guidance_loader import active_categories_for_shot, load_guidance
from ..keyframe.schema import KeyframeOutput
from ..story.schema import ShotIntent, StoryOutput
from .schema import ShotPromptOutput


async def run(
    shot: ShotIntent,
    story: StoryOutput,
    keyframes: KeyframeOutput,
    *,
    llm: Optional[LLMClient] = None,
) -> ShotPromptOutput:
    llm = llm or LLMClient(model=DEFAULT_LLM_MODEL)

    visual_pack = keyframes.shot_visuals[shot.shot_id]

    # 1. Image refs fed to video model: char anchors for this shot + storyboard.
    #    Char anchors lock identity across shots (was missing → 跨 shot 人物跳变).
    #    Style + blocking still rendered for debug inspection but NOT passed.
    char_ids_present = _ordered_unique(
        cid for panel in shot.panels for cid in panel.characters_present
    )
    char_refs = [
        keyframes.character_anchors[cid]
        for cid in char_ids_present
        if cid in keyframes.character_anchors
    ]
    video_refs = char_refs + [visual_pack.storyboard_image_path]

    # 2. Load guidance docs for all unique categories in this shot's panels
    active_categories = active_categories_for_shot(shot)
    active_guidance = load_guidance(active_categories)

    # 3. Build LLM prompt
    role_table = _build_role_table(shot, visual_pack, char_ids_present, story)
    user_prompt = _build_user_prompt(
        shot=shot, story=story, visual_pack=visual_pack,
        role_table=role_table, active_guidance=active_guidance,
    )

    raw_text = await llm.chat_text(
        system_prompt=_SHOT_PROMPT_SYSTEM,
        user_prompt=user_prompt,
    )

    return ShotPromptOutput(
        shot_id=shot.shot_id,
        text_prompt=raw_text.strip(),
        video_image_refs=video_refs,
    )


# ─── prompt assembly helpers ─────────────────────────────────────────────

def _ordered_unique(it):
    seen = set()
    out = []
    for x in it:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def _build_role_table(
    shot: ShotIntent,
    visual_pack,
    char_ids_present: list[str],
    story: StoryOutput,
) -> str:
    """Compact human-readable table: [Image N] → what it is.

    Refs fed to video model = char anchors (identity locks) + storyboard.
    """
    char_lookup = {c.id: c.look_description for c in story.characters}
    lines = []
    idx = 1
    for cid in char_ids_present:
        if cid in char_lookup:
            lines.append(
                f"[Image {idx}]: CHARACTER IDENTITY anchor for `{cid}` — "
                f"canonical look. ALL appearances of {cid} in the output video "
                f"MUST match this identity (face / hair / clothing / build). "
                f"Look reference: {char_lookup[cid]}"
            )
            idx += 1
    n_panels = len(shot.panels)
    lines.append(
        f"[Image {idx}]: storyboard sheet — {n_panels} panels arranged in a uniform grid. "
        f"Reading order: top row left-to-right, then next row left-to-right "
        f"(panel 1 = top-left, panel {n_panels} = bottom-right; each panel has a large "
        f"white number 1..{n_panels} in its top-left corner). "
        f"Panel index N corresponds to the Nth time_range block in [TIMELINE BEATS] "
        f"in numerical order. Scene composition / actions per panel are canonical for this shot."
    )
    return "\n".join(lines)


def _build_user_prompt(
    *, shot, story, visual_pack, role_table, active_guidance,
) -> str:
    return f"""Write a video-generation prompt for the shot below.

Output the prompt with EXACTLY these sections IN THIS ORDER (use the bracketed English headers verbatim, content in Chinese):
[SETTING]
[STYLE HEADER]
[ROLE ASSIGNMENT]
[CAMERA]
[PHYSICS REALISM]
[TIMELINE BEATS]
[DIALOGUE]
[SFX]

Rules:
- SETTING: paste the story's `setting` field verbatim at the top — this is the world / era / culture / ethnicity anchor. It MUST appear first so the video model locks the right cast, costume, and architecture context before doing anything else.
- PHYSICS REALISM: a 2-4 sentence rule block reminding the video model to obey basic physical laws — gravity / inertia / momentum conservation / impact equal-and-opposite reactions / fabric drape under gravity / no clipping through solid objects / consistent body anatomy / no teleportation between panels. Tailor it to the shot's actions when relevant (e.g., for a sword duel: blade weight gives swing inertia, parry deflects rather than passes through, footwork shifts weight visibly).
- TIMELINE BEATS: one block per panel in input order. Each beat header is its time_range (e.g. "0-3s •"). Integrate ALL active categories' guidance into beat content (don't separate by category).
- ROLE ASSIGNMENT: paste the prebuilt [Image N] table verbatim below — that's the ENTIRE section. Do NOT add any extra lines, do NOT reference any [Image N] that isn't in the table.
- DIALOGUE: list ONLY panels with non-null dialogue, one line each, format: `{{time_range}}: <speaker_id>："<spoken text>"` — speaker_id is taken verbatim from the `<id>:` prefix already in the dialogue field. If no panel has dialogue, write "本 shot 无对白".
- SFX: derive from category guidance SFX vocabularies; one line per panel time range.

=== SHOT ===
{json.dumps(shot.model_dump(mode="json"), ensure_ascii=False, indent=2)}

=== WORLD SETTING (paste verbatim into [SETTING]) ===
{story.setting}

=== STORY CONTEXT (characters + locations for lookup) ===
{json.dumps({
    "characters": [c.model_dump(mode="json") for c in story.characters],
    "locations": [l.model_dump(mode="json") for l in story.locations],
}, ensure_ascii=False, indent=2)}

=== KEYFRAME COMPOSITION NOTES (panel-aligned, in shot.panels order) ===
{json.dumps(visual_pack.panel_composition_notes, ensure_ascii=False, indent=2)}

=== PRE-BUILT [Image N] ROLE TABLE (paste verbatim into [ROLE ASSIGNMENT]) ===
{role_table}

=== ACTIVE GUIDANCE DOCS (vocabularies / rhythm / SFX — integrate ALL coherently) ===
{active_guidance}
"""


_SHOT_PROMPT_SYSTEM = """You are a prompt engineer crafting cinematic video-generation prompts. The prompt will be paired with an ordered image set; refer to specific images via `[Image 1]`, `[Image 2]`, ... (1-based indices matching the image set order).

Write only the prompt itself — no preamble, no explanation, no code fences.

Voice / style requirements:
- Concrete physical detail over abstract feeling. "颧骨开裂 1.5cm 内透橘红脉动" beats "看起来很痛苦".
- Verb-driven action language for body / camera / environment changes.
- Per-second precision on camera moves where guidance suggests it ("镜头应激性微颤 0.1 秒").
- Multi-category panels: weave categories into the same beat rather than splitting into sub-sections.
"""
