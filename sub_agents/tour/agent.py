"""TourAgent — parallel to StoryAgent for OBSERVATIONAL (non-narrative) videos.

Use cases that don't fit a narrative arc but still want a 1-2 min short:
  - 环境 / 氛围片 (e.g. "穿越机俯视科幻城夜游")
  - 工艺过程 (e.g. "老茶师泡一壶大红袍")
  - 时空切片 (e.g. "紫禁城角楼朝霞到日落")
  - 多视角展示 (e.g. "南宋汝窑器皿烧制工序")

Output: same ``StoryOutput`` schema as StoryAgent (downstream KeyframeAgent +
ShotPromptAgent are agnostic to which agent produced the plan). Difference is
purely in SYSTEM PROMPT: vignettes instead of arcs, observational moment text
instead of verb chains, 0-1 character instead of 2+, etc.
"""
from __future__ import annotations

from typing import Optional

from inference.clients import LLMClient

from .. import DEFAULT_LLM_MODEL
from .._categories import ShotCategory
from ..story.schema import StoryOutput


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

_SYSTEM_PROMPT = f"""You are a director crafting a SHORT OBSERVATIONAL video (1-2 min total runtime). NOT a narrative — a TOUR / VIGNETTE / ATMOSPHERIC PIECE.

The user gives you a SUBJECT (a place / process / object / atmosphere / concept) — NOT a story. Your job: design VIGNETTES showcasing different facets / angles / moments / details of that subject. NO plot. NO climax. NO character arc. NO conflict. Just observation.

Output ONE JSON object exactly matching this schema (no prose, no code fences, no trailing commas):

{{
  "title": "string — name the subject / concept being toured",
  "logline": "1-2 sentence description of WHAT we're showing (NOT a story summary — describe the subject)",
  "setting": "Cultural / era / geographic / world context — required so downstream image gen doesn't default to Western/contemporary bias. e.g. 'Cyberpunk 2090 Hong Kong-like neon city / aerial FPV drone perspective. No specific cast (environment only).'",
  "style_anchor": "1-2 sentence visual style brief: color palette / lighting / aesthetic / texture / contrast. Same role as StoryAgent.",
  "characters": [
    // EMPTY [] for pure environment tours (drone city flight, time-lapse, abstract concept).
    // 0-1 character preferred; NEVER 2+. If used, exactly one entry of:
    //   {{ "id": "snake_case_id", "role": "subject" or descriptor,
    //      "look_description": "concrete visual" }}
  ],
  "locations": [
    // Typically ONE main environment + sub-views explored across shots.
    // Required fields per entry: {{ "id": "snake_case_id",
    //                              "look_description": "concrete environment" }}
    // Example: {{ "id": "neo_shanghai_aerial_corridor",
    //             "look_description": "vertical canyon between 300m megatowers, neon..." }}
  ],
  "shots": [
    {{
      "shot_id": "sh_001",
      "duration_s": 15.0,
      "narrative_purpose": "what FACET of the subject this shot reveals (NOT a story beat) — e.g. 'reveal scale of the city by sweeping over neon canyon'",
      "primary_location": "<must equal one location id>",
      "panels": [
        {{
          "time_range": [0.0, 4.0],
          "categories": ["<ShotCategory value>"],
          "moment_description": "OBSERVATIONAL text describing what camera sees + how it moves + ambient changes. NOT 'character does X then Y'.",
          "dialogue": null,
          "characters_present": []
        }}
      ],
      "notes": null,
      "audit_notes": ""
    }}
  ]
}}

Valid ShotCategory values (multi-label per panel, ≥1 each):
{_CATEGORY_LIST}

HARD CONSTRAINTS (different from StoryAgent — tour mode is looser on arc, stricter on observation discipline):

1. Each shot duration_s = 15.0 (LOCKED — same as narrative pipeline, downstream video model expects this).
2. Shot count: 3-5 (fewer than narrative; tour pacing is slower, each shot lingers).
3. **NO narrative arc.** Shots present FACETS of the subject, no required ordering. Spatial sweep / temporal slice / multi-angle / layered reveal are all valid. NEVER fake setup→climax→resolution.
4. Each shot has 4-5 panels (target 4); panel duration 3-4s; tile [0, 15.0] contiguously.
5. Each panel.categories is multi-label (≥1).
6. moment_description = OBSERVATIONAL TEXT, NOT action arc.
   ❌ thin-narrative-verb: "drone enters → flies between buildings → exits over rooftop"
   ❌ static description: "a beautiful sci-fi city at night"
   ✅ rich observation: "FPV drone glides down neon-soaked canyon, holographic advertisements pulse from 200m towers either side, distant aerial vehicles cross the frame at three altitudes, rain droplets streak the lens, low-frequency engine hum"
7. **characters_present: typically EMPTY []** for environment / atmospheric tours. If a subject character exists (tea master / craftsman), use 1 id. NEVER multiple.
8. dialogue: typically null for tours. Optional VO narration goes in shot.notes if needed.
9. Props described inline in look_description (character) or in moment_description (environment).
10. Do NOT fake drama. If the subject doesn't have conflict, don't invent it. A drone flight is just a drone flight — show the WORLD, not a hero's journey.

PANEL RHYTHM PATTERNS for TOUR mode (pick by what facet you're revealing):
- Establishing → medium → close-up → detail (4 panels, 3-4s each): classic "approach" curve — wide context → narrowing focus
- Time-lapse vignette (3-4 panels): same place at different moments (dawn / midday / dusk / night)
- Spatial sweep (4-5 panels): camera travels through space, each panel a different waypoint
- Multi-angle showcase (4 panels): same subject from N positions (overhead / side / front / detail)
- Layered reveal (3-4 panels): wide → mid (something noticed) → close (focus pull) → reaction shot of viewer or detail

Within ONE tour, shots SHOULD use DIFFERENT rhythm patterns where possible — pace the piece by alternating approach styles.

CAMERA EMPHASIS:
- Camera movement is a CHARACTER in tours. Specify: FPV / overhead / tracking / dolly / orbit / handheld / push-in / pull-out. Make camera intent explicit in moment_description.
- Lighting and texture are SUBJECTS in tours. Don't treat them as backdrop — call them out (the way neon spills on wet concrete; the way smoke catches the lantern light).

STYLE EXPECTATIONS:
- Atmospheric over dramatic.
- Quiet over loud — ambient sound (wind / rain / hum / distant traffic) usually beats dialogue.
- Patience over urgency — let shots breathe.
- Real materials over generic ones (specify: neon tubes / vapor / leather / silk / brushed steel).

Output ONLY the JSON object."""


def _user_prompt(user_goal: str, *, has_refs: bool) -> str:
    refs_clause = (
        "Reference images are attached — use them as the visual anchor for the "
        "primary subject / location. Describe them faithfully in the location / "
        "character entry.\n\n"
        if has_refs else ""
    )
    return f"""{refs_clause}USER SUBJECT BRIEF (a thing / place / process / atmosphere to tour — NOT a story):

{user_goal}

You are the director of a TOUR / OBSERVATIONAL piece. Expand the brief into vignettes
that showcase different facets of the subject. No plot, no character drama, no
manufactured climax. Just well-observed moments. Produce the JSON now."""
