"""Central topology of agent relationships, consumed by router.py.

Each agent declares only its own self-description (purpose / inputs /
output / trigger semantics) in ``agents/*/descriptor.py``. The relational
knowledge — who runs before/after whom, alternative upstreams, when to
include or skip an agent — lives here, in the Director layer.

Rationale (CLAUDE.md principle of sub-agent decoupling): sub-agents should not name other
sub-agents in their own self-description. The Director is the
orchestration layer and naturally knows about every subordinate agent,
so this is the correct place for cross-agent wiring.

Consumed by ``router._agents_catalog_for_prompt`` when rendering the
agent catalog for the Upfront planner's LLM call.
"""

from __future__ import annotations

from typing import Any, Dict


AGENT_TOPOLOGY: Dict[str, Dict[str, str]] = {
    # ── Intake layer (pipeline entry points) ─────────────────────────
    "IntakeTextAgent": {
        "upstream": "(none — pipeline entry point for the user's text message)",
        "downstream": "any content-producing or editing agent, depending on intent",
        "when_to_include": (
            "MANDATORY first step for any task with a text goal. "
            "For greetings / noise / unrelated chat / empty input, the plan should "
            "terminate at this step (no downstream creative agents)."
        ),
    },
    "IntakeVideoAgent": {
        "upstream": "(raw user-uploaded video, pre-intake)",
        "downstream": (
            "any video-consuming agent — VideoAnalysisAgent, HighlightAgent, "
            "StyleTransferAgent, VideoExtendAgent, TranscriptionAgent"
        ),
        "when_to_include": "iff the user uploaded a video file",
    },
    "IntakeImageAgent": {
        "upstream": "(raw user-uploaded image, pre-intake)",
        "downstream": "BriefEnricherAgent",
        "when_to_include": "iff the user uploaded image(s) as creative reference",
    },

    # ── Creative pipeline (brief → finished film) ─────────────────────
    "BriefEnricherAgent": {
        "upstream": "IntakeImageAgent",
        "downstream": "StoryAgent",
        "when_to_include": (
            "iff IntakeImageAgent ran (image-reference creative flow). "
            "Skip otherwise."
        ),
    },
    "StoryAgent": {
        "upstream": (
            "one of: IntakeTextAgent (plain brief) / BriefEnricherAgent "
            "(image-reference flow) / VideoAnalysisAgent (continuation flow — "
            "analyse then write same-genre new story / sequel)"
        ),
        "downstream": "ScreenplayAgent",
        "when_to_include": (
            "new film creation tasks only. Skip on pure existing-video edits "
            "(style / extend / highlight / subtitle-only / transcribe-only) and "
            "on greeting / noise / unrelated input."
        ),
    },
    "ScreenplayAgent": {
        "upstream": "StoryAgent",
        "downstream": (
            "KeyFrameAgent (keyframe planning); also read by "
            "SubtitleAgent / MusicAgent / AmbienceAgent for shot-level "
            "dialogue / mood / duration"
        ),
        "when_to_include": "Always follows StoryAgent in creative flows.",
    },
    "KeyFrameAgent": {
        "upstream": "ScreenplayAgent",
        "downstream": "VideoAgent",
        "when_to_include": "Always in creative flows.",
    },
    "VideoAgent": {
        "upstream": "KeyFrameAgent",
        "downstream": (
            "audio chain (MusicAgent / AmbienceAgent / AudioMixAgent); "
            "VideoExtendAgent may insert between Video and the audio chain "
            "in scene-extension flows"
        ),
        "when_to_include": "Always in creative flows.",
    },

    # ── Audio chain ──────────────────────────────────────────────────
    "MusicAgent": {
        "upstream": (
            "ScreenplayAgent (creative flow) or VideoAnalysisAgent (existing-video)"
        ),
        "downstream": "AudioMixAgent",
        "when_to_include": (
            "Cinematic default for any newly-created film deliverable (unless "
            "user specifies ambience-only). On existing video, only when user "
            "explicitly requests music / BGM / soundtrack / score."
        ),
    },
    "AmbienceAgent": {
        "upstream": (
            "ScreenplayAgent (creative flow) or VideoAnalysisAgent (existing-video)"
        ),
        "downstream": "AudioMixAgent",
        "when_to_include": (
            "Cinematic default alongside MusicAgent for any newly-created film "
            "deliverable (unless user specifies music-only). On existing video, "
            "only when user explicitly requests ambient / atmospheric beds."
        ),
    },
    "AudioMixAgent": {
        "upstream": "whichever of MusicAgent / AmbienceAgent ran",
        "downstream": "CompositorAgent",
        "when_to_include": (
            "Whenever any audio-underlay agent ran. Skip when the deliverable "
            "is a single-track artifact (style-only, extend-only, highlight-only, "
            "subtitle-file-only)."
        ),
    },

    # ── Subtitle / Translation ───────────────────────────────────────
    "SubtitleAgent": {
        "upstream": (
            "ScreenplayAgent (creative flow) or TranscriptionAgent (existing-video flow)"
        ),
        "downstream": (
            "TranslationAgent (for bilingual / foreign-language output) or "
            "CompositorAgent (direct burn-in when no translation needed)"
        ),
        "when_to_include": (
            "Only when user explicitly requests subtitles. The task being a "
            "'short drama / mini-drama / manhua' alone is NOT a subtitle trigger."
        ),
    },
    "TranslationAgent": {
        "upstream": "SubtitleAgent (direct neighbor — never precedes it)",
        "downstream": "CompositorAgent",
        "when_to_include": (
            "Bilingual subtitle output or foreign-language subtitle on existing "
            "video. Must follow SubtitleAgent so cue boundaries are defined."
        ),
    },
    "TranscriptionAgent": {
        "upstream": (
            "IntakeVideoAgent (raw upload) or any video-edit agent (HighlightAgent, "
            "StyleTransferAgent, VideoExtendAgent) that produced a reusable video"
        ),
        "downstream": "SubtitleAgent",
        "when_to_include": (
            "Existing-video flow needing subtitles or translation. Skip in "
            "creative flows (ScreenplayAgent feeds SubtitleAgent directly there). "
            "Skip on silent video without subtitle intent."
        ),
    },

    # ── Video analysis / edit / composition ──────────────────────────
    "VideoAnalysisAgent": {
        "upstream": "IntakeVideoAgent",
        "downstream": (
            "HighlightAgent (supplies scene-selection seeds) or StoryAgent "
            "(supplies genre/mood/entities as creative reference)"
        ),
        "when_to_include": (
            "User explicitly asks for analysis / climax extraction / pacing / "
            "mood curve. Also implicit when HighlightAgent runs or when the "
            "plan is 'analyse this video + write same-genre new story / sequel'. "
            "Do NOT include for pure edit tasks (style-only / extend-only / "
            "add-music-only / combos)."
        ),
    },
    "HighlightAgent": {
        "upstream": "VideoAnalysisAgent",
        "downstream": (
            "(terminal by default — the highlight reel IS the deliverable). "
            "May extend into TranscriptionAgent → SubtitleAgent → CompositorAgent "
            "if subtitles requested, or MusicAgent → AudioMixAgent → CompositorAgent "
            "if BGM requested, or CompositorAgent alone if user asks for a "
            "composed output."
        ),
        "when_to_include": (
            "User requests extracting specific themed moments / climax / best "
            "clips / highlight scenes into a reel."
        ),
    },
    "StyleTransferAgent": {
        "upstream": "IntakeVideoAgent (or VideoExtendAgent in extend-then-stylise chain)",
        "downstream": (
            "(terminal by default — the stylised video IS the deliverable). "
            "May extend with VideoExtendAgent, TranscriptionAgent → SubtitleAgent → "
            "CompositorAgent, or MusicAgent → AudioMixAgent → CompositorAgent when "
            "user requests subtitles / BGM / composed output."
        ),
        "when_to_include": (
            "User requests a visual style transformation (anime, ink-wash, "
            "cyberpunk, oil painting, named-artist style, etc.) of an existing "
            "video."
        ),
    },
    "VideoExtendAgent": {
        "upstream": "IntakeVideoAgent (or StyleTransferAgent in style-then-extend chain)",
        "downstream": (
            "(terminal by default — the extended clip IS the deliverable). "
            "May chain with StyleTransferAgent, MusicAgent → AudioMixAgent → "
            "CompositorAgent, or TranscriptionAgent → SubtitleAgent → "
            "CompositorAgent when user requests additional treatment."
        ),
        "when_to_include": (
            "User requests lengthening / adding cinematic devices (slow-mo, "
            "atmospheric inserts, close-ups, sound-effect overlays) to an "
            "existing clip. NOT for narrative continuation ('write next scene's "
            "plot') — that belongs to a Story-chain task."
        ),
    },
    "CompositorAgent": {
        "upstream": (
            "AudioMixAgent (when audio was mixed) or SubtitleAgent (subtitle-only "
            "burn-in path)"
        ),
        "downstream": "(terminal — no downstream)",
        "when_to_include": (
            "When the deliverable is a composed video that combines video with "
            "audio and/or subtitles. Skip when the deliverable is a single-track "
            "artifact (style-only / extend-only / highlight-only reel / "
            "subtitle-file-only / transcript-only)."
        ),
    },
}


def get_topology_block(agent_id: str) -> str:
    """Render a single agent's topology as a prompt-visible block.

    Returns an empty string if the agent has no topology entry (it will
    silently fall through the renderer — InputResolver and the planner
    will rely on the agent's own descriptor text).
    """
    topo = AGENT_TOPOLOGY.get(agent_id)
    if not topo:
        return ""
    return (
        "[Director topology]\n"
        f"  Upstream: {topo.get('upstream', '(none specified)')}\n"
        f"  Downstream: {topo.get('downstream', '(none specified)')}\n"
        f"  When to include: {topo.get('when_to_include', '(always)')}"
    )
