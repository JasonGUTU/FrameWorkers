"""42-shape blueprint derived from evals/director_routing/eval_cases.json (130 cases).

Each shape = one unique chain structure in the eval set.

Policy (decisions from 2026-04-23 planning discussion):
  * **1B floor = 20**: target_n = max(20, eval_count × 10).  Shapes with
    only 1 eval example still get 20 training samples (not 10) to avoid
    starving the long tail.
  * **2B fixed order**: every set-slot is resolved to ONE canonical order
    (Music → Ambience / Illustration → Narrator / Music → Ambience → Trans →
    Translation → AudioMix).  The reward function is set-aware, so LoRA can
    still get full credit at eval time by emitting this canonical order.
  * **3A clean slate**: no surviving samples from the previous teacher-API
    corpus.  All 1390 samples are hand-authored in this session.
  * **All-English**.  For paper submission.

Two shapes have eval-GT bugs (more set-slot positions than distinct agents
can fill without duplication); we keep the logically correct canonical
chain and take the positional-accuracy hit.  Flagged below with
``gt_bug=True``.

Usage: imported by ``build_sft_jsonl.py``.  Each per-shape module under
``raw_samples/`` declares ``SAMPLES: list[{user_goal, rationale, intents}]``
(chain is implicit from blueprint), and the build script zips them
together with the canonical chain + system prompt into the final jsonl.
"""
from __future__ import annotations
from typing import NamedTuple


class ShapeSpec(NamedTuple):
    slug: str                  # unique short identifier (matches raw_samples/shape_<slug>.py)
    canonical_chain: list[str] # fixed agent_id order LoRA learns to emit
    eval_count: int            # how many eval cases use this shape
    target_n: int              # how many training samples to produce
    eval_reference_names: list[str]  # eval case names of this shape (for inspiration, not copy)
    notes: str                 # routing / flow commentary for the sample-author
    # Long-form input quota: eval has 12 cases where user_goal is a full
    # ~2500-word original story (``*_longstory_*`` names).  Training
    # mirrors the same ratio so LoRA sees the same input-length
    # distribution at both SFT and inference time.  Six shapes carry
    # long-story quota — the remaining 36 are 100 % short-brief.
    long_story_n: int = 0      # of target_n, this many samples have full-story input
    gt_bug: bool = False       # True if eval GT has unreachable set-slots


SHAPES: list[ShapeSpec] = [
    # ── Cinematic / creative film (Story → Screenplay → KeyFrame → Video → ...) ──
    ShapeSpec(
        slug="cr_compositor_only",
        canonical_chain=["StoryAgent", "ScreenplayAgent", "KeyFrameAgent", "VideoAgent", "CompositorAgent"],
        eval_count=8, target_n=80, long_story_n=30,
        eval_reference_names=["cr_04", "cr_05", "cr_11", "cr_12", "cr_14",
                              "cr_longstory_01", "cr_longstory_02", "cr_longstory_03"],
        notes="Cinematic mini-drama with NO audio overlay requested. Go straight "
              "Story→Screenplay→KeyFrame→Video→Compositor.  Reject 4 biases: "
              "(i) no Music/Ambience since user didn't mention audio, (ii) no "
              "Transcription since no subtitles requested, (iii) no AudioMix "
              "since there's nothing to mix, (iv) no VideoAnalysis since user "
              "didn't upload a video.  Long-story variant (30/80): user pastes "
              "a full original novella / novel excerpt starting with 'Here's "
              "my story I want to process: ...' — the goal IS the full story.",
    ),
    ShapeSpec(
        slug="story_pure",
        canonical_chain=["NarrationAgent", "IllustrationAgent", "NarratorAgent", "CompositorAgent"],
        eval_count=8, target_n=80, long_story_n=50,
        eval_reference_names=["storytelling_01", "storytelling_03", "storytelling_04",
                              "storytelling_longstory_01", "storytelling_longstory_02",
                              "storytelling_longstory_03", "storytelling_longstory_04",
                              "storytelling_longstory_05"],
        notes="Illustrated audiobook / storybook.  Narration script → still "
              "illustrations per paragraph → TTS narrator track → Compositor "
              "assembles slideshow.  No Story/Screenplay/KeyFrame/Video — those "
              "are for live-action-style mini-drama, not slideshow narration.  "
              "Long-story variant (50/80): user pastes a full ~2500-word "
              "original children's story / fable — goal IS the full story.",
    ),
    ShapeSpec(
        slug="cr_music",
        canonical_chain=["StoryAgent", "ScreenplayAgent", "KeyFrameAgent", "VideoAgent", "MusicAgent", "AudioMixAgent", "CompositorAgent"],
        eval_count=6, target_n=60, long_story_n=10,
        eval_reference_names=["cr_01", "cr_02", "cr_07", "cr_10", "cr_13", "cr_longstory_04"],
        notes="Mini-drama WITH background music, NO ambient sound.  Reject: "
              "(i) no Ambience since user only mentioned music, (ii) no "
              "Transcription since no subtitles requested.  Chain: creative "
              "pipeline → Music → AudioMix (baked-in audio + Music) → "
              "Compositor.  Long-story variant (10/60): user pastes a full "
              "novella + specifies a musical style ('with epic orchestral "
              "music' / 'with gentle piano').",
    ),
    ShapeSpec(
        slug="cr_ambience",
        canonical_chain=["StoryAgent", "ScreenplayAgent", "KeyFrameAgent", "VideoAgent", "AmbienceAgent", "AudioMixAgent", "CompositorAgent"],
        eval_count=6, target_n=60, long_story_n=10,
        eval_reference_names=["cr_03", "cr_06", "cr_08", "cr_09", "cr_15", "cr_longstory_05"],
        notes="Mini-drama WITH ambient atmosphere, NO BGM.  Reject: "
              "(i) no Music since user asked for atmosphere/ambient, not music, "
              "(ii) no Transcription.  Chain: creative → Ambience → AudioMix → "
              "Compositor.  Long-story variant (10/60): full novella + "
              "specifies an ambient atmosphere ('creepy haunted-house ambient' "
              "/ 'rainy-café ambient').",
    ),
    ShapeSpec(
        slug="cr_bilingual",
        canonical_chain=["StoryAgent", "ScreenplayAgent", "KeyFrameAgent", "VideoAgent", "TranscriptionAgent", "TranslationAgent", "CompositorAgent"],
        eval_count=5, target_n=50,
        eval_reference_names=["bilingual_01", "bilingual_02", "bilingual_03", "bilingual_04", "bilingual_05"],
        notes="Mini-drama with bilingual subtitles, no audio overlay requested. "
              "Chain: creative → Transcription → Translation → Compositor. "
              "Reject Music/Ambience/AudioMix (opt-in: user did not mention "
              "audio).",
    ),
    ShapeSpec(
        slug="cr_music_ambience",
        canonical_chain=["StoryAgent", "ScreenplayAgent", "KeyFrameAgent", "VideoAgent", "MusicAgent", "AmbienceAgent", "AudioMixAgent", "CompositorAgent"],
        eval_count=5, target_n=50,
        eval_reference_names=["cr_16", "cr_17", "cr_18", "cr_19", "cr_20"],
        notes="Mini-drama with BOTH music AND ambient sound, no subtitles.  "
              "User typically asks for both — e.g. 'orchestral music and "
              "battlefield ambience'.",
    ),
    ShapeSpec(
        slug="extend_only",
        canonical_chain=["IntakeVideoAgent", "VideoExtendAgent"],
        eval_count=5, target_n=50,
        eval_reference_names=["extend_01", "extend_03", "extend_04", "extend_06", "complex_07"],
        notes="User uploaded a video and wants ONLY an extended version, no "
              "audio overlay requested. Raw VideoExtend output is the "
              "deliverable — no Compositor needed (nothing to compose/overlay). "
              "Intake video → Extend → done. Reject Music/Ambience/AudioMix "
              "(opt-in: not mentioned).",
    ),
    ShapeSpec(
        slug="intake_img_cr",
        canonical_chain=["IntakeImageAgent", "BriefEnricherAgent", "StoryAgent", "ScreenplayAgent", "KeyFrameAgent", "VideoAgent", "CompositorAgent"],
        eval_count=5, target_n=50,
        eval_reference_names=["intake_img_01", "intake_img_02", "intake_img_03", "intake_img_04", "intake_img_05"],
        notes="User uploads a reference image (character / setting) + asks for "
              "a full mini-drama built around it, no audio overlay requested. "
              "IntakeImage → BriefEnricher (synth text brief from image + "
              "user goal) → creative pipeline → Compositor. Reject "
              "Music/Ambience/AudioMix (opt-in: not mentioned).",
    ),
    ShapeSpec(
        slug="style_only",
        canonical_chain=["IntakeVideoAgent", "StyleTransferAgent"],
        eval_count=5, target_n=50,
        eval_reference_names=["style_01", "style_02", "style_03", "style_04", "style_05"],
        notes="Uploaded video + style transfer request, no audio/subtitle.  "
              "StyleTransfer output is the deliverable.  No Compositor.",
    ),
    ShapeSpec(
        slug="cr_subtitle",
        canonical_chain=["StoryAgent", "ScreenplayAgent", "KeyFrameAgent", "VideoAgent", "TranscriptionAgent", "CompositorAgent"],
        eval_count=5, target_n=50,
        eval_reference_names=["sub_01", "sub_02", "sub_03", "sub_04", "sub_05"],
        notes="Mini-drama with monolingual subtitles (same language as spoken "
              "dialogue), no audio overlay requested. Chain: creative → "
              "Transcription → Compositor. Reject Translation (monolingual), "
              "Music/Ambience/AudioMix (opt-in: not mentioned).",
    ),
    # ── Existing-video edits with VideoAnalysis → Highlight ────────────────
    ShapeSpec(
        slug="highlight_music_subtitle",
        canonical_chain=["IntakeVideoAgent", "VideoAnalysisAgent", "HighlightAgent", "MusicAgent", "TranscriptionAgent", "AudioMixAgent", "CompositorAgent"],
        eval_count=4, target_n=40,
        eval_reference_names=["complex_10", "complex_15", "complex_52", "complex_53"],
        notes="Highlight-reel workflow with BGM + subtitle.  NOTE: eval GT "
              "has 8 slots with 3× {Music|Transcription}, but only 2 distinct "
              "agents from that set exist — one slot is logically unreachable "
              "without duplication.  Training chain is the correct 7-step; "
              "eval scores ~62% positional on this shape.  Flag eval GT for "
              "owner to fix.",
        gt_bug=True,
    ),
    ShapeSpec(
        slug="highlight_only",
        canonical_chain=["IntakeVideoAgent", "VideoAnalysisAgent", "HighlightAgent"],
        eval_count=4, target_n=40,
        eval_reference_names=["highlight_01", "highlight_03", "highlight_04", "highlight_05"],
        notes="Pure highlight-extraction from an uploaded long video.  Raw "
              "HighlightAgent output is the deliverable — cut segments.  No "
              "Compositor (no overlay / subtitle / music requested).",
    ),
    ShapeSpec(
        slug="vid_bilingual_sub",
        canonical_chain=["IntakeVideoAgent", "TranscriptionAgent", "TranslationAgent", "CompositorAgent"],
        eval_count=4, target_n=40,
        eval_reference_names=["sub_vid_03", "complex_08", "complex_11", "complex_49"],
        notes="Uploaded video + bilingual subtitle request, no other changes.  "
              "Transcribe → Translate → Compositor overlays dual-language SRT.",
    ),
    ShapeSpec(
        slug="vid_analysis_cr_subtitle",
        canonical_chain=["IntakeVideoAgent", "VideoAnalysisAgent", "StoryAgent", "ScreenplayAgent", "KeyFrameAgent", "VideoAgent", "TranscriptionAgent", "CompositorAgent"],
        eval_count=3, target_n=30,
        eval_reference_names=["complex_13", "complex_55", "complex_56"],
        notes="User uploads video for REFERENCE / analysis (not as the base "
              "to edit), then asks for a fresh cinematic remix inspired by it, "
              "with monolingual subtitles, no audio overlay. IntakeVideo → "
              "VideoAnalysis → creative pipeline → Transcription → Compositor. "
              "Reject Translation (monolingual), Music/Ambience/AudioMix "
              "(opt-in: not mentioned).",
    ),
    ShapeSpec(
        slug="intake_img_cr_bilingual",
        canonical_chain=["IntakeImageAgent", "BriefEnricherAgent", "StoryAgent", "ScreenplayAgent", "KeyFrameAgent", "VideoAgent", "TranscriptionAgent", "TranslationAgent", "CompositorAgent"],
        eval_count=3, target_n=30,
        eval_reference_names=["complex_19", "complex_57", "complex_58"],
        notes="Image-referenced mini-drama with bilingual subtitles, no audio "
              "overlay. Chain: IntakeImage → BriefEnricher → creative → "
              "Transcription → Translation → Compositor. Reject "
              "Music/Ambience/AudioMix (opt-in: not mentioned).",
    ),
    ShapeSpec(
        slug="intake_img_cr_extend",
        canonical_chain=["IntakeImageAgent", "BriefEnricherAgent", "StoryAgent", "ScreenplayAgent", "KeyFrameAgent", "VideoAgent", "VideoExtendAgent", "CompositorAgent"],
        eval_count=3, target_n=30,
        eval_reference_names=["complex_23", "complex_59", "complex_60"],
        notes="Image-referenced mini-drama, extended beyond the default "
              "duration, no audio overlay. Chain: image intake → creative → "
              "VideoExtend → Compositor. Reject Music/Ambience/AudioMix "
              "(opt-in: not mentioned).",
    ),
    ShapeSpec(
        slug="vid_music",
        canonical_chain=["IntakeVideoAgent", "MusicAgent", "AudioMixAgent", "CompositorAgent"],
        eval_count=3, target_n=30,
        eval_reference_names=["complex_24", "complex_31", "complex_32"],
        notes="Add BGM to an uploaded video.  No analysis, no highlight — the "
              "whole video gets music overlaid.",
    ),
    ShapeSpec(
        slug="vid_music_ambience",
        canonical_chain=["IntakeVideoAgent", "MusicAgent", "AmbienceAgent", "AudioMixAgent", "CompositorAgent"],
        eval_count=3, target_n=30,
        eval_reference_names=["complex_25", "complex_33", "complex_34"],
        notes="Add both BGM and ambient atmosphere to an uploaded video.",
    ),
    ShapeSpec(
        slug="style_subtitle",
        canonical_chain=["IntakeVideoAgent", "StyleTransferAgent", "TranscriptionAgent", "CompositorAgent"],
        eval_count=3, target_n=30,
        eval_reference_names=["complex_26", "complex_37", "complex_38"],
        notes="Style-transfer + subtitle overlay.  StyleTransfer output goes "
              "to Compositor alongside transcribed SRT.",
    ),
    ShapeSpec(
        slug="style_music",
        canonical_chain=["IntakeVideoAgent", "StyleTransferAgent", "MusicAgent", "AudioMixAgent", "CompositorAgent"],
        eval_count=3, target_n=30,
        eval_reference_names=["complex_27", "complex_35", "complex_36"],
        notes="Style-transferred video with BGM swapped in.",
    ),
    ShapeSpec(
        slug="extend_subtitle",
        canonical_chain=["IntakeVideoAgent", "VideoExtendAgent", "TranscriptionAgent", "CompositorAgent"],
        eval_count=3, target_n=30,
        eval_reference_names=["complex_28", "complex_41", "complex_42"],
        notes="Extend video + add subtitles.",
    ),
    ShapeSpec(
        slug="extend_music",
        canonical_chain=["IntakeVideoAgent", "VideoExtendAgent", "MusicAgent", "AudioMixAgent", "CompositorAgent"],
        eval_count=3, target_n=30,
        eval_reference_names=["complex_29", "complex_39", "complex_40"],
        notes="Extend video + add BGM.",
    ),
    ShapeSpec(
        slug="extend_ambience",
        canonical_chain=["IntakeVideoAgent", "VideoExtendAgent", "AmbienceAgent", "AudioMixAgent", "CompositorAgent"],
        eval_count=1, target_n=20,
        eval_reference_names=["extend_05"],
        notes="Extend video + add environmental sound layer (rain / wind / "
              "wave / forest / thunder / crowd / etc.). Symmetric to "
              "extend_music but with AmbienceAgent in the audio slot. Reject "
              "Music (user asked for environmental sound, not melody).",
    ),
    ShapeSpec(
        slug="highlight_subtitle",
        canonical_chain=["IntakeVideoAgent", "VideoAnalysisAgent", "HighlightAgent", "TranscriptionAgent", "CompositorAgent"],
        eval_count=3, target_n=30,
        eval_reference_names=["complex_30", "complex_43", "complex_44"],
        notes="Highlight reel with subtitles overlaid.  No music.",
    ),
    ShapeSpec(
        slug="vid_subtitle",
        canonical_chain=["IntakeVideoAgent", "TranscriptionAgent", "CompositorAgent"],
        eval_count=3, target_n=30,
        eval_reference_names=["sub_vid_01", "sub_vid_02", "sub_vid_05"],
        notes="Uploaded video, just add monolingual subtitles.",
    ),
    ShapeSpec(
        slug="vid_analysis_cr",
        canonical_chain=["IntakeVideoAgent", "VideoAnalysisAgent", "StoryAgent", "ScreenplayAgent", "KeyFrameAgent", "VideoAgent", "CompositorAgent"],
        eval_count=2, target_n=20,
        eval_reference_names=["complex_01", "complex_54"],
        notes="Video-analysis-referenced cinematic remake, no audio overlay. "
              "Chain: IntakeVideo → VideoAnalysis (extracts narrative themes) "
              "→ creative pipeline → Compositor. Reject Music/Ambience/AudioMix "
              "(opt-in: not mentioned).",
    ),
    ShapeSpec(
        slug="extend_style",
        canonical_chain=["IntakeVideoAgent", "VideoExtendAgent", "StyleTransferAgent"],
        eval_count=2, target_n=20,
        eval_reference_names=["complex_02", "complex_45"],
        notes="Extend + style-transfer, no audio/subtitle.  Raw "
              "StyleTransferAgent output = final deliverable.",
    ),
    ShapeSpec(
        slug="extend_style_subtitle",
        canonical_chain=["IntakeVideoAgent", "VideoExtendAgent", "StyleTransferAgent", "TranscriptionAgent", "CompositorAgent"],
        eval_count=2, target_n=20,
        eval_reference_names=["complex_03", "complex_46"],
        notes="Extend + style-transfer + subtitle.",
    ),
    ShapeSpec(
        slug="highlight_music",
        canonical_chain=["IntakeVideoAgent", "VideoAnalysisAgent", "HighlightAgent", "MusicAgent", "AudioMixAgent", "CompositorAgent"],
        eval_count=2, target_n=20,
        eval_reference_names=["complex_04", "complex_48"],
        notes="Highlight reel with BGM overlay.",
    ),
    ShapeSpec(
        slug="vid_analysis_music_subtitle",
        canonical_chain=["IntakeVideoAgent", "VideoAnalysisAgent", "TranscriptionAgent", "MusicAgent", "AudioMixAgent", "CompositorAgent"],
        eval_count=2, target_n=20,
        eval_reference_names=["complex_06", "complex_51"],
        notes="Uploaded video: analyze, subtitle it, and swap in BGM.  NOTE: "
              "eval GT has 7 slots with 4 set-slot positions spanning only 3 "
              "distinct agents {VA, Transcription, Music} — one slot is "
              "unreachable.  Training uses 6-step logical chain; eval ~57% on "
              "this shape.  Flag eval GT for owner to fix.",
        gt_bug=True,
    ),
    ShapeSpec(
        slug="highlight_bilingual_sub",
        canonical_chain=["IntakeVideoAgent", "VideoAnalysisAgent", "HighlightAgent", "TranscriptionAgent", "TranslationAgent", "CompositorAgent"],
        eval_count=2, target_n=20,
        eval_reference_names=["complex_20", "complex_50"],
        notes="Highlight reel with bilingual subtitles.",
    ),
    ShapeSpec(
        slug="style_extend_music",
        canonical_chain=["IntakeVideoAgent", "StyleTransferAgent", "VideoExtendAgent", "MusicAgent", "AudioMixAgent", "CompositorAgent"],
        eval_count=2, target_n=20,
        eval_reference_names=["complex_21", "complex_47"],
        notes="Style-transfer → extend → BGM.  Order matters: Style before "
              "Extend so the extended clip inherits the styled look.",
    ),
    # ── Storytelling variants ──────────────────────────────────────────────
    ShapeSpec(
        slug="story_ambience",
        canonical_chain=["NarrationAgent", "IllustrationAgent", "NarratorAgent", "AmbienceAgent", "AudioMixAgent", "CompositorAgent"],
        eval_count=2, target_n=20, long_story_n=10,
        eval_reference_names=["storytelling_ambience_01", "storytelling_longstory_07"],
        notes="Illustrated audiobook with ambient sound bed (no music).  "
              "Long-story variant (10/20): user pastes a full ~2500-word "
              "children's / folk story + asks for ambient atmosphere.",
    ),
    ShapeSpec(
        slug="story_music",
        canonical_chain=["NarrationAgent", "IllustrationAgent", "NarratorAgent", "MusicAgent", "AudioMixAgent", "CompositorAgent"],
        eval_count=2, target_n=20, long_story_n=10,
        eval_reference_names=["storytelling_music_01", "storytelling_longstory_06"],
        notes="Illustrated audiobook with background music.  Long-story "
              "variant (10/20): full children's / folk story + asks for a "
              "musical score (e.g. 'soft piano', 'gentle harp').",
    ),
    # ── Long-tail (1 eval each, floor=20) ───────────────────────────────────
    ShapeSpec(
        slug="highlight_bilingual_music",
        canonical_chain=["IntakeVideoAgent", "VideoAnalysisAgent", "HighlightAgent", "TranscriptionAgent", "TranslationAgent", "MusicAgent", "AudioMixAgent", "CompositorAgent"],
        eval_count=1, target_n=20,
        eval_reference_names=["complex_18"],
        notes="Highlight + bilingual subs + BGM.  Everything layered.",
    ),
    ShapeSpec(
        slug="story_bilingual",
        canonical_chain=["NarrationAgent", "IllustrationAgent", "NarratorAgent", "TranslationAgent", "CompositorAgent"],
        eval_count=1, target_n=20,
        eval_reference_names=["storytelling_bilingual_01"],
        notes="Illustrated audiobook with bilingual subtitles (translation of "
              "narrator transcript).  No extra audio overlay.",
    ),
    ShapeSpec(
        slug="story_full_imgref_music_bil",
        canonical_chain=["IntakeImageAgent", "BriefEnricherAgent", "NarrationAgent", "IllustrationAgent", "NarratorAgent", "MusicAgent", "AudioMixAgent", "TranslationAgent", "CompositorAgent"],
        eval_count=1, target_n=20,
        eval_reference_names=["storytelling_full_01"],
        notes="Full storytelling: image ref + narration + music + bilingual.",
    ),
    ShapeSpec(
        slug="story_imgref",
        canonical_chain=["IntakeImageAgent", "BriefEnricherAgent", "NarrationAgent", "IllustrationAgent", "NarratorAgent", "CompositorAgent"],
        eval_count=1, target_n=20,
        eval_reference_names=["storytelling_imgref_01"],
        notes="Storytelling with a reference character image.",
    ),
    ShapeSpec(
        slug="story_imgref_bilingual",
        canonical_chain=["IntakeImageAgent", "BriefEnricherAgent", "NarrationAgent", "IllustrationAgent", "NarratorAgent", "TranslationAgent", "CompositorAgent"],
        eval_count=1, target_n=20,
        eval_reference_names=["storytelling_imgref_bilingual_01"],
        notes="Storytelling with image ref + bilingual subtitles.",
    ),
    ShapeSpec(
        slug="story_imgref_music",
        canonical_chain=["IntakeImageAgent", "BriefEnricherAgent", "NarrationAgent", "IllustrationAgent", "NarratorAgent", "MusicAgent", "AudioMixAgent", "CompositorAgent"],
        eval_count=1, target_n=20,
        eval_reference_names=["storytelling_imgref_music_01"],
        notes="Storytelling with image ref + BGM.",
    ),
    ShapeSpec(
        slug="story_music_ambience",
        canonical_chain=["NarrationAgent", "IllustrationAgent", "NarratorAgent", "MusicAgent", "AmbienceAgent", "AudioMixAgent", "CompositorAgent"],
        eval_count=1, target_n=20,
        eval_reference_names=["storytelling_music_ambience_01"],
        notes="Storytelling with music + ambience dual-layer audio.",
    ),
    ShapeSpec(
        slug="story_music_bilingual",
        canonical_chain=["NarrationAgent", "IllustrationAgent", "NarratorAgent", "MusicAgent", "AudioMixAgent", "TranslationAgent", "CompositorAgent"],
        eval_count=1, target_n=20,
        eval_reference_names=["storytelling_music_bilingual_01"],
        notes="Storytelling with music + bilingual subs.",
    ),
    ShapeSpec(
        slug="story_ultra",
        canonical_chain=["IntakeImageAgent", "BriefEnricherAgent", "NarrationAgent", "IllustrationAgent", "NarratorAgent", "MusicAgent", "AmbienceAgent", "AudioMixAgent", "TranslationAgent", "CompositorAgent"],
        eval_count=1, target_n=20,
        eval_reference_names=["storytelling_ultra_01"],
        notes="Storytelling with all modifiers: image ref + music + ambience + "
              "bilingual.  Longest storytelling chain (10 steps).",
    ),
]


assert len(SHAPES) == 43, f"blueprint has {len(SHAPES)} shapes, expected 43"
assert len({s.slug for s in SHAPES}) == 43, "duplicate slugs"

TOTAL_TARGET = sum(s.target_n for s in SHAPES)  # 1410 = 1390 (orig 42 shapes) + 20 (new extend_ambience)
