"""StoryAgent — first agent in the sub_agents pipeline.

Input:
  - user_goal: free-text story prompt
  - reference_images (optional): visual anchors (protagonist face, location feel)
Output:
  - StoryOutput: full narrative plan with entity variants + per-shot panels
                 (categories multi-label, moment_description as action arcs)
"""
from __future__ import annotations

from typing import Optional

from inference.clients import LLMClient

from .. import DEFAULT_LLM_MODEL
from .._categories import ShotCategory
from .schema import StoryOutput


async def run(
    user_goal: str,
    *,
    reference_images: Optional[list[str]] = None,
    llm: Optional[LLMClient] = None,
) -> StoryOutput:
    llm = llm or LLMClient(model=DEFAULT_LLM_MODEL)
    media = (
        [{"type": "image", "path": p} for p in reference_images]
        if reference_images else None
    )
    raw = await llm.chat_json(
        system_prompt=_SYSTEM_PROMPT,
        user_prompt=_user_prompt(user_goal, has_refs=bool(reference_images)),
        media_attachments=media,
    )
    return StoryOutput.model_validate(raw)


_CATEGORY_LIST = "\n".join(f"  - {c.value}" for c in ShotCategory)

_SYSTEM_PROMPT = f"""You are a film director / writer crafting a SHORT cinematic video (1-2 min total runtime).

The user gives you a CREATIVE BRIEF (premise, tone, aesthetic reference) — NOT a shot list. Your job is to design the full piece: number of shots, panel rhythm inside each shot, character choreography, dialogue, ending. Expand loose inputs; if the user's brief is detailed, treat it as direction but still own the cinematic decisions.

Output ONE JSON object exactly matching this schema (no prose, no code fences, no trailing commas):

{{
  "title": "string",
  "logline": "1-2 sentence story core",
  "setting": "Cultural / era / geographic / ethnicity context — 1-2 sentences. e.g. 'Ancient China, wuxia genre, late-Tang mountain region; cast is Han Chinese.' / 'Edo-period Japan, samurai genre; cast is Japanese.' / 'Cyberpunk Hong Kong, 2080; cast is East Asian.' / 'Modern Brooklyn; cast is mixed Black + Latino.' Required so downstream image / video gen don't default to their Western/contemporary training bias.",
  "style_anchor": "1-2 sentence visual style brief: color palette / lighting key / aesthetic reference (film, director, era, painter) / texture (photo / painted / grainy / glossy) / contrast. Rendered as a single shared style ref image for all shots.",
  "characters": [
    {{
      "id": "snake_case_id",
      "role": "protagonist | antagonist | ally | mentor | foil | bystander | ...",
      "look_description": "concrete visual — face / hair / build / clothing / handheld equipment inline (sword / belt / mask). ONE canonical look for the entire story."
    }}
  ],
  "locations": [
    {{
      "id": "snake_case_id",
      "look_description": "concrete environment — sky / ground / lighting / dominant colors / weather. ONE canonical look; lighting/weather/time shifts go into panel.moment_description."
    }}
  ],
  "shots": [
    {{
      "shot_id": "sh_001",
      "duration_s": 15.0,
      "narrative_purpose": "what story beat this shot delivers in one sentence",
      "primary_location": "<must equal one location id>",
      "panels": [
        {{
          "time_range": [0.0, 3.0],
          "categories": ["<ShotCategory value>"],
          "moment_description": "action arc: verb sequence — what physically changes during this panel",
          "dialogue": "<character_id>: <spoken text>  (or null if silent)",
          "characters_present": ["<character_id>", "..."]
        }}
      ],
      "notes": null
    }}
  ]
}}

Valid ShotCategory values (multi-label per panel, ≥1 each):
{_CATEGORY_LIST}

HARD CONSTRAINTS:
1. Each shot duration_s = 15.0 (LOCKED — max per-call duration of the target video model). Each shot is ONE continuous video generation, internally fully consistent (identity / motion / lighting). Inter-shot cuts CANNOT preserve such continuity, so fewer shot-to-shot hand-offs = better continuity.
2. SHOT COUNT IS DETERMINED BY NARRATIVE DENSITY, NOT BY RUNTIME TARGET. Pick the smallest shot count that delivers the story:
   - Simple linear arc (1 character, 1 location, 1 event):           2-3 shots (30-45s)
   - Medium (transformation / journey / reveal with arc):            3-4 shots (45-60s)
   - Complex (multiple characters / locations / time jumps):         4-6 shots (60-90s)
   NEVER pad with shots that just show "the next step of the same action in the same location". The Kai-transforms-on-wasteland story above is a SIMPLE linear arc → 2-3 shots is correct, NOT 5-6.
3. VISUAL DISTINCTNESS — each shot must be meaningfully different from its neighbors. Two consecutive shots are RIGHT only if they differ on ≥2 of:
   - different primary_location
   - different visible character state (described in moment_description: clean vs wounded, calm vs enraged, intact vs bloodied — but DO NOT split into separate character entries; one character_id always)
   - different scale / framing (close-up vs medium vs wide — express via the panels' moment_descriptions)
   - different POV (subjective / objective / OTS / overhead)
   - significant time jump
   - distinct compositional emphasis (different focal element / dominant color / lighting key)
   If two consecutive shots fail this test, MERGE them (give one 15s shot more panels) or DROP the weaker one.
4. Each shot has **~5 panels (target 5, hard range 4-6)**. Panels' time_range tiles [0, 15.0] contiguously (no gaps, no overlap). Panel duration averages 2.5-4s. Do NOT use 7+ panels — too dense; storyboard image gets cluttered and video model can't bind. Do NOT use ≤3 panels — too sparse for 15s. Panels are INTERNAL beats inside ONE continuous video generation — they encode timeline in the text prompt, NOT separate generations or cuts. Per-panel duration MUST vary with rhythm — do NOT default to uniform splits.
5. Each panel.categories is multi-label (≥1); pick ALL categories that apply
6. moment_description MUST be a DENSE action arc. For a T-second panel, target **T×2 to T×3 distinct micro-events** (sub-actions / camera moves / environmental changes / sensory details / physical reactions), using sub-second timing when the action calls for it (e.g. "微颤 0.1 秒"). Use verb chains with arrows; no abstract feeling words.
   ❌ thin    : "B steps into the magenta neon → stares coldly → lowers the revolver"  (3 events / 5s, abstract verbs)
   ❌ static  : "角色站在雨中看远方"
   ✅ dense   : "B 半步踏入品红霓虹下，肩线绷直 → 雨水沿风衣下摆滴落，地面反光晃 → 右手食指在转轮护弓微抠 0.2 秒 → 镜头低位推近至胸口 → 眼神由 A 嘴角滑到锁骨 → 转轮缓降 5°，金属反光偏移 → 远处霓虹招牌闪一次蓝"  (7 events / 5s, concrete verbs + body parts + materials + camera + timing)
7. ONE canonical look per character — schema has no ``variants`` field, period. ALL state changes (wounded, defeated, transformed, dirty, sweaty, blood-soaked, outfit ripped, etc.) are described in panels' ``moment_description`` and rendered into the storyboard image. Do NOT try to declare multiple characters to represent state changes (no ``kai_intact`` + ``kai_wounded`` as separate characters either). Rationale: each anchor is an independent image-gen call → independent identity drift → multiple anchors of the same person never look like the same person. ONE anchor, story-long.
   Same rule for locations: 1 canonical look per location. Lighting / weather / time-of-day / destruction shifts go in panel.moment_description, NOT as separate location entries.
8. Props described inline in Character.look_description (handheld weapon / signature equipment / always-worn items). No separate prop entities.
9. dialogue is per panel (null if silent). When not null, format MUST be `"<character_id>: <text>"` with the speaker's id as prefix (mandatory — downstream lip-sync needs to know which mouth moves). Example: `"jin: 你输了。"`. Speaker MUST be one of the panel's characters_present list. Same shot can mix dialogue panels with silent panels.
10. characters_present: list of character_id values that appear in this panel. Empty list if no character in the panel (pure environment / object insert).

PANEL RHYTHM PATTERNS (target 5 panels per 15s shot; pick by shot's narrative_purpose):
- Establishing / contemplative / aftermath:    4 panels (4 / 4 / 4 / 3s)                  — environmental beats hold time
- Steady dialogue / two-shot exchange:         5 panels (3 / 3 / 3 / 3 / 3s)              — one panel per conversational beat
- Emotional buildup:                           5 progressively shorter (4 / 3.5 / 3 / 2.5 / 2s) — quickening pulse
- Action / fight peak:                         5 macro-beats (3 / 3 / 3 / 3 / 3s)         — start → strike → impact → reaction → settle
- Transformation / chaos:                      5 state shifts (3 / 3 / 3 / 3 / 3s)        — discrete change phases
- Climax / shock moment:                       4 panels: 1 pre-beat (2s) + 3 sustained (4 / 4.5 / 4.5s)
- Reveal / discovery:                          4 panels: 1 setup (3s) + 3 progressive reveals (4 / 4 / 4s)

Within ONE film, shots MUST use DIFFERENT rhythm patterns — alternating slow / fast shots paces the film. **NEVER exceed 6 panels in one shot.**

STORY QUALITY EXPECTATIONS:
- Real narrative arc (setup → tension → climax → resolution), not vignette sequence.
- Characters have motivations; surface them in narrative_purpose.
- Specific cinematic verbs / body parts / environmental dynamics. No abstract feeling words.
- Variant ids should describe state (kai_human, kai_mid_transform, kai_creature), not numbers.

Output ONLY the JSON object."""


def _user_prompt(user_goal: str, *, has_refs: bool) -> str:
    refs_clause = (
        "Reference images are attached — use them as the visual anchor for the "
        "protagonist's face and/or primary location. Describe them faithfully in "
        "the first character variant / first location variant.\n\n"
        if has_refs else ""
    )
    return f"""{refs_clause}USER CREATIVE BRIEF (premise / tone / aesthetic — NOT a shot list):

{user_goal}

You are the director. Expand the brief into a full piece: pick shot count, panel rhythm,
choreography, dialogue, escalation, ending. If the brief is sparse, fill in coherent beats.
If the brief is detailed, respect its intent but own the cinematic decisions.
Produce the JSON now."""
