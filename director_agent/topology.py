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
    # IntakeTextAgent was retired 2026-04-23 — chat messages and
    # text/plain uploads are now persisted as [creative_brief] artifacts
    # directly by ``workspace.persist_raw_upload`` + the
    # ``create_user_message`` side-effect, so no agent step is needed
    # to bridge user text into the workspace. StoryAgent / NarrationAgent
    # / BriefEnricherAgent resolve ``[creative_brief]`` straight out of
    # global memory.
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
        "downstream": (
            "StoryAgent (cinematic creative flow) OR NarrationAgent "
            "(illustrated-storytelling flow with a user-uploaded "
            "character / setting reference)"
        ),
        "when_to_include": (
            "iff IntakeImageAgent ran (image-reference creative flow OR "
            "illustrated-storytelling flow with a reference portrait). "
            "Skip otherwise."
        ),
    },
    "StoryAgent": {
        "upstream": (
            "one of: [creative_brief] (plain brief — auto-persisted from the "
            "user's chat / text upload by the workspace layer) / BriefEnricherAgent "
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
            "MusicAgent / AmbienceAgent for shot-level mood / duration"
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
            "ScreenplayAgent (cinematic flow) / NarrationAgent (illustrated-"
            "storytelling flow) / VideoAnalysisAgent (existing-video flow)"
        ),
        "downstream": "AudioMixAgent",
        "when_to_include": (
            "Opt-in across all flows. Include only when the user explicitly "
            "mentions music / BGM / soundtrack / score (e.g. 'add some music', "
            "'with an orchestral score', 'piano BGM under the narrator'). No "
            "chain has a 'default' music layer — silence is the default."
        ),
    },
    "AmbienceAgent": {
        "upstream": (
            "ScreenplayAgent (cinematic flow) / NarrationAgent (illustrated-"
            "storytelling flow) / VideoAnalysisAgent (existing-video flow)"
        ),
        "downstream": "AudioMixAgent",
        "when_to_include": (
            "Opt-in across all flows. Include only when the user explicitly "
            "mentions ambient / atmospheric / environmental sound design "
            "(e.g. 'add some ambient sounds', 'layer in rain + café murmur', "
            "'jungle ambience under the narration'). No chain has a 'default' "
            "ambience layer — silence is the default."
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
    # Post-refactor: SubtitleAgent has been retired. The canonical source
    # of truth for subtitle text is the actual audio track (either
    # VideoAgent's in-clip baked voice on creative flows OR the original
    # audio on existing-video flows), so TranscriptionAgent's STT output
    # feeds subtitle burn-in directly. CompositorAgent's materializer
    # renders TranscriptionAgent's timestamped segments to SRT with a
    # pure-Python helper — no separate LLM pass needed.
    "TranscriptionAgent": {
        "upstream": (
            "Any agent producing playable audio/video: AudioMixAgent "
            "(creative-flow in-clip baked voice), IntakeVideoAgent (raw "
            "upload), StyleTransferAgent / VideoExtendAgent / "
            "HighlightAgent (existing-video edit outputs)"
        ),
        "downstream": (
            "CompositorAgent (its materializer converts the segments to "
            "SRT and burns them in); TranslationAgent inserts between "
            "Transcription and Compositor for bilingual / foreign-"
            "language subtitle flows"
        ),
        "when_to_include": (
            "Whenever the user asks for subtitles / captions / a "
            "transcript — on creative flows AND existing-video flows. "
            "Skip on silent video or when no subtitle / caption track is "
            "requested on the deliverable. The task being a 'short drama "
            "/ mini-drama / manhua' alone is NOT a subtitle trigger."
        ),
    },
    "TranslationAgent": {
        "upstream": "TranscriptionAgent (direct neighbor — never precedes it)",
        "downstream": "CompositorAgent",
        "when_to_include": (
            "Bilingual subtitle output or foreign-language subtitle on any "
            "video flow. Must follow TranscriptionAgent so cue boundaries "
            "are defined."
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
            "May extend into TranscriptionAgent → CompositorAgent if "
            "subtitles requested, or MusicAgent → AudioMixAgent → "
            "CompositorAgent if BGM requested, or CompositorAgent alone if "
            "user asks for a composed output."
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
            "May extend with VideoExtendAgent, TranscriptionAgent → "
            "CompositorAgent, or MusicAgent → AudioMixAgent → CompositorAgent "
            "when user requests subtitles / BGM / composed output."
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
            "CompositorAgent, or TranscriptionAgent → CompositorAgent when "
            "user requests additional treatment."
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
            "AudioMixAgent (when audio was mixed), TranscriptionAgent / "
            "TranslationAgent (subtitle burn-in path), or NarratorAgent + "
            "IllustrationAgent (illustrated-storytelling slideshow path)"
        ),
        "downstream": "(terminal — no downstream)",
        "when_to_include": (
            "When the deliverable is a composed video that combines video with "
            "audio and/or subtitles — including illustrated-storytelling "
            "slideshows where the video track is an image sequence rather than "
            "an assembled mp4. Skip when the deliverable is a single-track "
            "artifact (style-only / extend-only / highlight-only reel / "
            "subtitle-file-only / transcript-only)."
        ),
    },

    # ── Illustrated-storytelling chain ───────────────────────────────
    # Mutually exclusive with the creative-film chain
    # (Story → Screenplay → KeyFrame → Video → AudioMix → Compositor).
    # Triggered only when the user asks for an audiobook-with-pictures /
    # storytime / illustrated-narration video — a slideshow of still
    # illustrations timed to a narrator voiceover.
    "NarrationAgent": {
        "upstream": (
            "the user's auto-persisted [creative_brief] (plain brief or long prose), "
            "OR BriefEnricherAgent "
            "(when the user uploaded a character / setting reference image to "
            "anchor the illustrations)"
        ),
        "downstream": "IllustrationAgent AND NarratorAgent (both consume it in parallel)",
        "when_to_include": (
            "Only on illustrated-storytelling / audiobook-with-pictures / "
            "storytime video requests. NEVER include together with StoryAgent / "
            "ScreenplayAgent / KeyFrameAgent / VideoAgent — those are the "
            "mutually-exclusive cinematic chain. Triggers: 'read this story "
            "as an illustrated audiobook', 'make an illustrated story-time "
            "video', 'narrate with matching pictures', 'kids storybook video' "
            "etc. Optional extensions of the storytelling chain (add "
            "MusicAgent / AmbienceAgent / AudioMixAgent for scored narration; "
            "add TranslationAgent for bilingual subtitle burn-in; prepend "
            "IntakeImageAgent + BriefEnricherAgent for a character-reference "
            "illustrated audiobook) are OPT-IN only — triggered by explicit "
            "user mention, not by default."
        ),
    },
    "IllustrationAgent": {
        "upstream": "NarrationAgent",
        "downstream": "CompositorAgent (via illustration_sequence label)",
        "when_to_include": (
            "Always follows NarrationAgent in illustrated-storytelling flows. "
            "Never runs outside that chain — it consumes NarrationAgent's "
            "per-segment image_prompt and overall_style anchor."
        ),
    },
    "NarratorAgent": {
        "upstream": "NarrationAgent",
        "downstream": (
            "CompositorAgent (supplies audio_file via audio_package, SRT via "
            "subtitle_tracks, and per-segment durations via segment_timing)"
        ),
        "when_to_include": (
            "Always follows NarrationAgent in illustrated-storytelling flows. "
            "Provides the TTS voiceover + burned subtitles + per-segment timing "
            "the slideshow compositor uses to align each illustration."
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
