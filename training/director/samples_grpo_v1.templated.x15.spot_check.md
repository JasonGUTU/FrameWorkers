# GRPO (templated) spot check — 30 of 15649 samples

**Track A (templated chain-free).** Variation: 3 rationale skeletons × per-sample shuffled reject list × 3 intent variants per agent (md5-hash picked).
Sister track: samples_grpo_v1.jsonl (with-chain flow narrative).

---

## #1  (story_ultra, grpo_templated_x15, grpo_tmpl_x15_14155)
**user_goal** (273 chars):

> I'm sending you a watercolor of a 2010s YouTube-Ryan-ToysReview-superfan — render a kids' audiobook in English about his playroom-toy-haul morning, with YouTube-Ryan-ToysReview-pop-3 BGM, YouTube-Ryan-ToysReview-playroom-toy-haul-morning ambience, and Vietnamese subtitles.

**rationale:** Illustrated storytelling slideshow produced from a text brief + uploaded reference image, layered with BGM + ambient layer + bilingual narration track. Skipped: TranscriptionAgent (no subtitle requested); IntakeVideoAgent (no source clip uploaded); KeyFrameAgent (no keyframe planning required); StoryAgent (no NEW film authoring requested); HighlightAgent (not a highlight workflow); VideoAnalysisAgent (no source-video analysis required); VideoExtendAgent (no video extension requested); ScreenplayAgent (no NEW film scene-decomposition needed); StyleTransferAgent (no style transfer requested); VideoAgent (no NEW motion-clip generation requested).

**plan:**
  - `IntakeImageAgent` — Register the uploaded image as a captioned workspace artifact.
  - `BriefEnricherAgent` — Augment the brief with the uploaded image's descriptive content.
  - `NarrationAgent` — Author the narration script from the brief — paragraph-by-paragraph story text.
  - `IllustrationAgent` — Produce per-paragraph illustrations matching the narration.
  - `NarratorAgent` — Synthesize the narrator audio track from the narration script.
  - `MusicAgent` — Compose the BGM the user requested, matching the brief's emotional register.
  - `AmbienceAgent` — Author the environmental ambient layer per the brief.
  - `AudioMixAgent` — Layer the available audio tracks into the final mixed wav.
  - `TranslationAgent` — Translate the source-language subtitles into the requested target language.
  - `CompositorAgent` — Output the final mp4 by composing the video, audio, and subtitle / transition elements.

## #2  (extend_ambience, grpo_templated_x15, grpo_tmpl_x15_04435)
**user_goal** (101 chars):

> Uploading a 1-minute monastic-courtyard reel — extend to 3 minutes and overlay distant-bell ambience.

**rationale:** Extended video cut produced from an uploaded source video, layered with ambient layer. Skipped: TranslationAgent (no translation / second language requested); StoryAgent (no NEW film authoring requested); IllustrationAgent (not a slideshow / illustrated-storytelling format); IntakeImageAgent (no image upload); NarratorAgent (not a slideshow / illustrated-storytelling format); ScreenplayAgent (no NEW film scene-decomposition needed); NarrationAgent (not a slideshow / illustrated-storytelling format); KeyFrameAgent (no keyframe planning required); BriefEnricherAgent (no image upload to enrich the brief with); StyleTransferAgent (no style transfer requested); TranscriptionAgent (no subtitle requested); VideoAnalysisAgent (no source-video analysis required); VideoAgent (no NEW motion-clip generation requested); MusicAgent (no BGM requested); HighlightAgent (not a highlight workflow).

**plan:**
  - `IntakeVideoAgent` — Register the uploaded video as a captioned workspace artifact.
  - `VideoExtendAgent` — Extend the source video beyond its original duration.
  - `AmbienceAgent` — Author the environmental ambient layer per the brief.
  - `AudioMixAgent` — Mix the available audio tracks into one final mixed wav.
  - `CompositorAgent` — Mux the final mp4, combining the rendered visual track with audio and any subtitle overlay.

## #3  (story_music, grpo_templated_x15, grpo_tmpl_x15_09475)
**user_goal** (89 chars):

> Cook up a children's audiobook about a baby sloth napping on a vine, with slow-piano BGM.

**rationale:** Illustrated storytelling slideshow from a text brief with BGM as the only added overlays. Reject: HighlightAgent (not a highlight workflow); IntakeImageAgent (no image upload); VideoExtendAgent (no video extension requested); ScreenplayAgent (no NEW film scene-decomposition needed); TranslationAgent (no translation / second language requested); TranscriptionAgent (no subtitle requested); StoryAgent (no NEW film authoring requested); KeyFrameAgent (no keyframe planning required); IntakeVideoAgent (no source clip uploaded); BriefEnricherAgent (no image upload to enrich the brief with); StyleTransferAgent (no style transfer requested); AmbienceAgent (no environmental layer requested); VideoAnalysisAgent (no source-video analysis required); VideoAgent (no NEW motion-clip generation requested).

**plan:**
  - `NarrationAgent` — Author the narration script from the brief — paragraph-by-paragraph story text.
  - `IllustrationAgent` — Generate one illustration image per paragraph of the narration.
  - `NarratorAgent` — Produce the spoken narrator track via TTS over the narration text.
  - `MusicAgent` — Compose the BGM the user requested, matching the brief's emotional register.
  - `AudioMixAgent` — Layer the available audio tracks into the final mixed wav.
  - `CompositorAgent` — Mux the final mp4, combining the rendered visual track with audio and any subtitle overlay.

## #4  (vid_music_ambience, grpo_templated_x15, grpo_tmpl_x15_03874)
**user_goal** (106 chars):

> Uploading a 90-second beachfront yoga session — please add a meditative-flute BGM and ocean-wave ambience.

**rationale:** Modified video cut from an uploaded source video with BGM + ambient layer as the only added overlays. Reject: StyleTransferAgent (no style transfer requested); TranslationAgent (no translation / second language requested); KeyFrameAgent (no keyframe planning required); NarrationAgent (not a slideshow / illustrated-storytelling format); HighlightAgent (not a highlight workflow); StoryAgent (no NEW film authoring requested); VideoAgent (no NEW motion-clip generation requested); BriefEnricherAgent (no image upload to enrich the brief with); IntakeImageAgent (no image upload); VideoAnalysisAgent (no source-video analysis required); VideoExtendAgent (no video extension requested); IllustrationAgent (not a slideshow / illustrated-storytelling format); NarratorAgent (not a slideshow / illustrated-storytelling format); TranscriptionAgent (no subtitle requested); ScreenplayAgent (no NEW film scene-decomposition needed).

**plan:**
  - `IntakeVideoAgent` — Ingest the uploaded video into the workspace with caption metadata.
  - `MusicAgent` — Compose the BGM the user requested, matching the brief's emotional register.
  - `AmbienceAgent` — Generate the ambient sound bed the brief asks for.
  - `AudioMixAgent` — Layer the available audio tracks into the final mixed wav.
  - `CompositorAgent` — Mux the final mp4, combining the rendered visual track with audio and any subtitle overlay.

## #5  (story_full_imgref_music_bil, grpo_templated_x15, grpo_tmpl_x15_10956)
**user_goal** (189 chars):

> I'm sending you a sketch of a young 1880s Wisconsin cheesemaker boy — produce a children's audiobook in English about his cheese-cellar morning, with Bavarian-folk BGM and German subtitles.

**rationale:** Illustrated storytelling slideshow from a text brief + uploaded reference image with BGM + bilingual narration track as the only added overlays. Reject: VideoExtendAgent (no video extension requested); VideoAgent (no NEW motion-clip generation requested); StoryAgent (no NEW film authoring requested); HighlightAgent (not a highlight workflow); StyleTransferAgent (no style transfer requested); TranscriptionAgent (no subtitle requested); VideoAnalysisAgent (no source-video analysis required); IntakeVideoAgent (no source clip uploaded); ScreenplayAgent (no NEW film scene-decomposition needed); AmbienceAgent (no environmental layer requested); KeyFrameAgent (no keyframe planning required).

**plan:**
  - `IntakeImageAgent` — Ingest the uploaded image into the workspace with caption metadata.
  - `BriefEnricherAgent` — Augment the brief with the uploaded image's descriptive content.
  - `NarrationAgent` — Author the narration script from the brief — paragraph-by-paragraph story text.
  - `IllustrationAgent` — Generate one illustration image per paragraph of the narration.
  - `NarratorAgent` — Generate the TTS narrator audio track from the narration script.
  - `MusicAgent` — Compose the BGM the user requested, matching the brief's emotional register.
  - `AudioMixAgent` — Mix the available audio tracks into one final mixed wav.
  - `TranslationAgent` — Render the bilingual translation of the subtitle track.
  - `CompositorAgent` — Mux the final mp4, combining the rendered visual track with audio and any subtitle overlay.

## #6  (highlight_music_subtitle, grpo_templated_x15, grpo_tmpl_x15_01924)
**user_goal** (115 chars):

> I have a 5-hour Iditarod sled-dog livestream — make a highlight reel with epic-orchestral BGM and English captions.

**rationale:** Highlight reel from an uploaded source video with BGM + subtitles as the only added overlays. Reject: NarratorAgent (not a slideshow / illustrated-storytelling format); AmbienceAgent (no environmental layer requested); StyleTransferAgent (no style transfer requested); KeyFrameAgent (no keyframe planning required); ScreenplayAgent (no NEW film scene-decomposition needed); BriefEnricherAgent (no image upload to enrich the brief with); StoryAgent (no NEW film authoring requested); VideoExtendAgent (no video extension requested); VideoAgent (no NEW motion-clip generation requested); TranslationAgent (no translation / second language requested); IntakeImageAgent (no image upload); IllustrationAgent (not a slideshow / illustrated-storytelling format); NarrationAgent (not a slideshow / illustrated-storytelling format).

**plan:**
  - `IntakeVideoAgent` — Persist the uploaded video into the workspace as a captioned artifact.
  - `VideoAnalysisAgent` — Analyze the source video into a scene-by-scene report (genre, mood, beats, entities).
  - `HighlightAgent` — Select the highlight segments from the analyzed source video.
  - `MusicAgent` — Generate the requested BGM, scored to the brief's mood.
  - `TranscriptionAgent` — Generate the subtitle track from the dialogue audio with per-line timestamps.
  - `AudioMixAgent` — Combine the produced audio layers into a single mixed wav.
  - `CompositorAgent` — Output the final mp4 by composing the video, audio, and subtitle / transition elements.

## #7  (extend_style_subtitle, grpo_templated_x15, grpo_tmpl_x15_06645)
**user_goal** (117 chars):

> Here's a 30-second 3D-rendering tutorial — extend to 90 seconds, style as low-poly PS1, and overlay English captions.

**rationale:** Style-transferred + extended video cut produced from an uploaded source video, layered with subtitles. Skipped: KeyFrameAgent (no keyframe planning required); MusicAgent (no BGM requested); StoryAgent (no NEW film authoring requested); VideoAnalysisAgent (no source-video analysis required); AudioMixAgent (no audio tracks to mix); IllustrationAgent (not a slideshow / illustrated-storytelling format); VideoAgent (no NEW motion-clip generation requested); NarratorAgent (not a slideshow / illustrated-storytelling format); BriefEnricherAgent (no image upload to enrich the brief with); ScreenplayAgent (no NEW film scene-decomposition needed); HighlightAgent (not a highlight workflow); NarrationAgent (not a slideshow / illustrated-storytelling format); TranslationAgent (no translation / second language requested); IntakeImageAgent (no image upload); AmbienceAgent (no environmental layer requested).

**plan:**
  - `IntakeVideoAgent` — Persist the uploaded video into the workspace as a captioned artifact.
  - `VideoExtendAgent` — Produce extended footage that continues the source video.
  - `StyleTransferAgent` — Re-render the source video under the requested visual style.
  - `TranscriptionAgent` — Author the timestamped transcription of the spoken dialogue.
  - `CompositorAgent` — Output the final mp4 by composing the video, audio, and subtitle / transition elements.

## #8  (extend_style, grpo_templated_x15, grpo_tmpl_x15_06177)
**user_goal** (85 chars):

> Here's a 30-second BMX-trick reel — extend to 90 seconds and style as Banksy stencil.

**rationale:** Style-transferred + extended video cut from an uploaded source video; no overlays added. Excluded — NarratorAgent (not a slideshow / illustrated-storytelling format); CompositorAgent (no final mux required); TranscriptionAgent (no subtitle requested); AmbienceAgent (no environmental layer requested); NarrationAgent (not a slideshow / illustrated-storytelling format); IllustrationAgent (not a slideshow / illustrated-storytelling format); TranslationAgent (no translation / second language requested); VideoAnalysisAgent (no source-video analysis required); VideoAgent (no NEW motion-clip generation requested); StoryAgent (no NEW film authoring requested); MusicAgent (no BGM requested); BriefEnricherAgent (no image upload to enrich the brief with); ScreenplayAgent (no NEW film scene-decomposition needed); IntakeImageAgent (no image upload); HighlightAgent (not a highlight workflow); AudioMixAgent (no audio tracks to mix); KeyFrameAgent (no keyframe planning required).

**plan:**
  - `IntakeVideoAgent` — Persist the uploaded video into the workspace as a captioned artifact.
  - `VideoExtendAgent` — Generate continuation footage extending the source video.
  - `StyleTransferAgent` — Apply the requested style transfer to the source video.

## #9  (story_imgref, grpo_templated_x15, grpo_tmpl_x15_11537)
**user_goal** (133 chars):

> Here's a sketch of a young 1900s Alexandria-Greek-quarter girl — produce a children's audiobook of her Cleopatra-Boulevard afternoon.

**rationale:** Illustrated storytelling slideshow from a text brief + uploaded reference image with no audio / subtitle overlays. Reject: ScreenplayAgent (no NEW film scene-decomposition needed); TranscriptionAgent (no subtitle requested); HighlightAgent (not a highlight workflow); IntakeVideoAgent (no source clip uploaded); VideoAnalysisAgent (no source-video analysis required); AudioMixAgent (no audio tracks to mix); VideoAgent (no NEW motion-clip generation requested); KeyFrameAgent (no keyframe planning required); TranslationAgent (no translation / second language requested); AmbienceAgent (no environmental layer requested); StyleTransferAgent (no style transfer requested); StoryAgent (no NEW film authoring requested); MusicAgent (no BGM requested); VideoExtendAgent (no video extension requested).

**plan:**
  - `IntakeImageAgent` — Register the uploaded image as a captioned workspace artifact.
  - `BriefEnricherAgent` — Enrich the brief by integrating descriptions of the uploaded reference images.
  - `NarrationAgent` — Draft the narration script per the brief, paragraph-by-paragraph.
  - `IllustrationAgent` — Render one still illustration per narration paragraph.
  - `NarratorAgent` — Produce the spoken narrator track via TTS over the narration text.
  - `CompositorAgent` — Mux the final mp4, combining the rendered visual track with audio and any subtitle overlay.

## #10  (vid_music_ambience, grpo_templated_x15, grpo_tmpl_x15_03971)
**user_goal** (112 chars):

> Uploading a 2-minute clip of a Lamar-Valley wolf watch — please add a sparse-piano BGM and prairie-wind ambient.

**rationale:** Modified video cut from an uploaded source video with BGM + ambient layer as the only added overlays. Reject: TranscriptionAgent (no subtitle requested); IntakeImageAgent (no image upload); TranslationAgent (no translation / second language requested); HighlightAgent (not a highlight workflow); StoryAgent (no NEW film authoring requested); VideoExtendAgent (no video extension requested); KeyFrameAgent (no keyframe planning required); VideoAnalysisAgent (no source-video analysis required); NarratorAgent (not a slideshow / illustrated-storytelling format); StyleTransferAgent (no style transfer requested); NarrationAgent (not a slideshow / illustrated-storytelling format); IllustrationAgent (not a slideshow / illustrated-storytelling format); VideoAgent (no NEW motion-clip generation requested); ScreenplayAgent (no NEW film scene-decomposition needed); BriefEnricherAgent (no image upload to enrich the brief with).

**plan:**
  - `IntakeVideoAgent` — Register the uploaded video as a captioned workspace artifact.
  - `MusicAgent` — Generate the requested BGM, scored to the brief's mood.
  - `AmbienceAgent` — Author the environmental ambient layer per the brief.
  - `AudioMixAgent` — Mix the available audio tracks into one final mixed wav.
  - `CompositorAgent` — Output the final mp4 by composing the video, audio, and subtitle / transition elements.

## #11  (highlight_only, grpo_templated_x15, grpo_tmpl_x15_02006)
**user_goal** (91 chars):

> Uploading a 4-hour orchid-show recording — please extract the highlight rare-bloom moments.

**rationale:** Highlight reel produced from an uploaded source video, nothing layered on top. Skipped: CompositorAgent (no final mux required); MusicAgent (no BGM requested); TranscriptionAgent (no subtitle requested); KeyFrameAgent (no keyframe planning required); TranslationAgent (no translation / second language requested); IntakeImageAgent (no image upload); VideoExtendAgent (no video extension requested); VideoAgent (no NEW motion-clip generation requested); AmbienceAgent (no environmental layer requested); StyleTransferAgent (no style transfer requested); NarratorAgent (not a slideshow / illustrated-storytelling format); ScreenplayAgent (no NEW film scene-decomposition needed); BriefEnricherAgent (no image upload to enrich the brief with); IllustrationAgent (not a slideshow / illustrated-storytelling format); StoryAgent (no NEW film authoring requested); AudioMixAgent (no audio tracks to mix); NarrationAgent (not a slideshow / illustrated-storytelling format).

**plan:**
  - `IntakeVideoAgent` — Ingest the uploaded video into the workspace with caption metadata.
  - `VideoAnalysisAgent` — Analyze the source video into a scene-by-scene report (genre, mood, beats, entities).
  - `HighlightAgent` — Pick the top highlight clips from the source video using the analysis report.

## #12  (story_imgref_music, grpo_templated_x15, grpo_tmpl_x15_12732)
**user_goal** (180 chars):

> Here's a watercolor of a 2010s YouTube-Linus-Tech-Tips-fan kid — build an illustrated children's tale of his bedroom-gaming-PC-build afternoon, with Linus-Tech-Tips-electronic BGM.

**rationale:** Illustrated storytelling slideshow from a text brief + uploaded reference image with BGM as the only added overlays. Reject: AmbienceAgent (no environmental layer requested); KeyFrameAgent (no keyframe planning required); StyleTransferAgent (no style transfer requested); ScreenplayAgent (no NEW film scene-decomposition needed); IntakeVideoAgent (no source clip uploaded); StoryAgent (no NEW film authoring requested); TranslationAgent (no translation / second language requested); VideoAgent (no NEW motion-clip generation requested); HighlightAgent (not a highlight workflow); VideoAnalysisAgent (no source-video analysis required); VideoExtendAgent (no video extension requested); TranscriptionAgent (no subtitle requested).

**plan:**
  - `IntakeImageAgent` — Ingest the uploaded image into the workspace with caption metadata.
  - `BriefEnricherAgent` — Fold image-reference descriptions into the brief to produce an enriched creative brief.
  - `NarrationAgent` — Write the narration script broken into reading paragraphs.
  - `IllustrationAgent` — Produce per-paragraph illustrations matching the narration.
  - `NarratorAgent` — Synthesize the narrator audio track from the narration script.
  - `MusicAgent` — Compose the BGM the user requested, matching the brief's emotional register.
  - `AudioMixAgent` — Mix the available audio tracks into one final mixed wav.
  - `CompositorAgent` — Composite the final mp4 — assemble video, audio, and any subtitle / transitions into the deliverable.

## #13  (highlight_music, grpo_templated_x15, grpo_tmpl_x15_07333)
**user_goal** (110 chars):

> Here's a 90-minute San-Sebastian-Jazz-Festival livestream — please cut highlights with San-Sebastian-Jazz BGM.

**rationale:** Highlight reel produced from an uploaded source video, layered with BGM. Skipped: IllustrationAgent (not a slideshow / illustrated-storytelling format); AmbienceAgent (no environmental layer requested); NarrationAgent (not a slideshow / illustrated-storytelling format); VideoAgent (no NEW motion-clip generation requested); KeyFrameAgent (no keyframe planning required); StyleTransferAgent (no style transfer requested); TranslationAgent (no translation / second language requested); NarratorAgent (not a slideshow / illustrated-storytelling format); TranscriptionAgent (no subtitle requested); StoryAgent (no NEW film authoring requested); ScreenplayAgent (no NEW film scene-decomposition needed); VideoExtendAgent (no video extension requested); BriefEnricherAgent (no image upload to enrich the brief with); IntakeImageAgent (no image upload).

**plan:**
  - `IntakeVideoAgent` — Ingest the uploaded video into the workspace with caption metadata.
  - `VideoAnalysisAgent` — Generate a structured scene-level report of the source video.
  - `HighlightAgent` — Pick the top highlight clips from the source video using the analysis report.
  - `MusicAgent` — Write the requested BGM, aligned to the brief's tonal cue.
  - `AudioMixAgent` — Mix the available audio tracks into one final mixed wav.
  - `CompositorAgent` — Output the final mp4 by composing the video, audio, and subtitle / transition elements.

## #14  (vid_music_ambience, grpo_templated_x15, grpo_tmpl_x15_03904)
**user_goal** (113 chars):

> Uploading a 90-second hot-spring-soak reel — please add a meditative-shakuhachi BGM and steam-and-water ambience.

**rationale:** Modified video cut from an uploaded source video; overlays applied: BGM + ambient layer. Excluded — StyleTransferAgent (no style transfer requested); VideoAgent (no NEW motion-clip generation requested); StoryAgent (no NEW film authoring requested); ScreenplayAgent (no NEW film scene-decomposition needed); IllustrationAgent (not a slideshow / illustrated-storytelling format); TranscriptionAgent (no subtitle requested); HighlightAgent (not a highlight workflow); NarratorAgent (not a slideshow / illustrated-storytelling format); VideoAnalysisAgent (no source-video analysis required); IntakeImageAgent (no image upload); VideoExtendAgent (no video extension requested); TranslationAgent (no translation / second language requested); NarrationAgent (not a slideshow / illustrated-storytelling format); BriefEnricherAgent (no image upload to enrich the brief with); KeyFrameAgent (no keyframe planning required).

**plan:**
  - `IntakeVideoAgent` — Register the uploaded video as a captioned workspace artifact.
  - `MusicAgent` — Compose the BGM the user requested, matching the brief's emotional register.
  - `AmbienceAgent` — Author the environmental ambient layer per the brief.
  - `AudioMixAgent` — Combine the produced audio layers into a single mixed wav.
  - `CompositorAgent` — Composite the final mp4 — assemble video, audio, and any subtitle / transitions into the deliverable.

## #15  (cr_ambience, grpo_templated_x15, grpo_tmpl_x15_00887)
**user_goal** (158 chars):

> Produce a 30-second short of a young apprentice in a Cuban cigar atelier, with cigar-atelier ambient (knife slice, distant son cubano radio, distant traffic).

**rationale:** Cinematic mini-drama from a text brief; overlays applied: ambient layer. Excluded — HighlightAgent (not a highlight workflow); BriefEnricherAgent (no image upload to enrich the brief with); MusicAgent (no BGM requested); IllustrationAgent (not a slideshow / illustrated-storytelling format); NarrationAgent (not a slideshow / illustrated-storytelling format); IntakeVideoAgent (no source clip uploaded); VideoExtendAgent (no video extension requested); IntakeImageAgent (no image upload); StyleTransferAgent (no style transfer requested); TranslationAgent (no translation / second language requested); VideoAnalysisAgent (no source-video analysis required); NarratorAgent (not a slideshow / illustrated-storytelling format); TranscriptionAgent (no subtitle requested).

**plan:**
  - `StoryAgent` — Author the story blueprint following the brief, with a clear arc and beat structure.
  - `ScreenplayAgent` — Break the drafted story into scene-by-scene units, preserving the brief's tonal register.
  - `KeyFrameAgent` — Plan keyframes for the screenplay's settings, one per scene.
  - `VideoAgent` — Animate each keyframe into a per-shot motion clip.
  - `AmbienceAgent` — Produce the requested ambient atmosphere as an audio bed.
  - `AudioMixAgent` — Layer the available audio tracks into the final mixed wav.
  - `CompositorAgent` — Composite the final mp4 — assemble video, audio, and any subtitle / transitions into the deliverable.

## #16  (extend_style_subtitle, grpo_templated_x15, grpo_tmpl_x15_06494)
**user_goal** (132 chars):

> Uploading a 30-second crocheter demo — extend to 90 seconds, render as a Norse-tapestry illustration, and overlay English subtitles.

**rationale:** Style-transferred + extended video cut produced from an uploaded source video, layered with subtitles. Skipped: IntakeImageAgent (no image upload); IllustrationAgent (not a slideshow / illustrated-storytelling format); VideoAgent (no NEW motion-clip generation requested); ScreenplayAgent (no NEW film scene-decomposition needed); AudioMixAgent (no audio tracks to mix); KeyFrameAgent (no keyframe planning required); StoryAgent (no NEW film authoring requested); HighlightAgent (not a highlight workflow); TranslationAgent (no translation / second language requested); NarrationAgent (not a slideshow / illustrated-storytelling format); MusicAgent (no BGM requested); BriefEnricherAgent (no image upload to enrich the brief with); NarratorAgent (not a slideshow / illustrated-storytelling format); VideoAnalysisAgent (no source-video analysis required); AmbienceAgent (no environmental layer requested).

**plan:**
  - `IntakeVideoAgent` — Ingest the uploaded video into the workspace with caption metadata.
  - `VideoExtendAgent` — Generate continuation footage extending the source video.
  - `StyleTransferAgent` — Apply the requested style transfer to the source video.
  - `TranscriptionAgent` — Generate the subtitle track from the dialogue audio with per-line timestamps.
  - `CompositorAgent` — Composite the final mp4 — assemble video, audio, and any subtitle / transitions into the deliverable.

## #17  (vid_analysis_cr, grpo_templated_x15, grpo_tmpl_x15_05717)
**user_goal** (141 chars):

> I have a Kenneth-Anger Scorpio-Rising reference — please analyze its biker-occult pop-soundtrack and produce a 30-second new cinematic short.

**rationale:** Reference-video-informed cinematic mini-drama produced from an uploaded source video, nothing layered on top. Skipped: VideoExtendAgent (no video extension requested); NarrationAgent (not a slideshow / illustrated-storytelling format); TranslationAgent (no translation / second language requested); StyleTransferAgent (no style transfer requested); NarratorAgent (not a slideshow / illustrated-storytelling format); TranscriptionAgent (no subtitle requested); AmbienceAgent (no environmental layer requested); HighlightAgent (not a highlight workflow); IllustrationAgent (not a slideshow / illustrated-storytelling format); BriefEnricherAgent (no image upload to enrich the brief with); MusicAgent (no BGM requested); IntakeImageAgent (no image upload); AudioMixAgent (no audio tracks to mix).

**plan:**
  - `IntakeVideoAgent` — Persist the uploaded video into the workspace as a captioned artifact.
  - `VideoAnalysisAgent` — Analyze the source video into a scene-by-scene report (genre, mood, beats, entities).
  - `StoryAgent` — Draft the story blueprint from the brief — character arc and act structure.
  - `ScreenplayAgent` — Break the drafted story into scene-by-scene units, preserving the brief's tonal register.
  - `KeyFrameAgent` — Lay out keyframes for the screenplay's settings, scene-by-scene.
  - `VideoAgent` — Produce per-shot video clips from each keyframe, holding aesthetic continuity across cuts.
  - `CompositorAgent` — Output the final mp4 by composing the video, audio, and subtitle / transition elements.

## #18  (cr_compositor_only, grpo_templated_x15, grpo_tmpl_x15_00188)
**user_goal** (125 chars):

> Make me a 30-second magical-realism piece where a Lima fishmonger's fish keep telling small jokes only her daughter can hear.

**rationale:** Cinematic mini-drama produced from a text brief, nothing layered on top. Skipped: IntakeImageAgent (no image upload); MusicAgent (no BGM requested); VideoExtendAgent (no video extension requested); StyleTransferAgent (no style transfer requested); HighlightAgent (not a highlight workflow); VideoAnalysisAgent (no source-video analysis required); TranslationAgent (no translation / second language requested); NarrationAgent (not a slideshow / illustrated-storytelling format); AmbienceAgent (no environmental layer requested); AudioMixAgent (no audio tracks to mix); IllustrationAgent (not a slideshow / illustrated-storytelling format); BriefEnricherAgent (no image upload to enrich the brief with); IntakeVideoAgent (no source clip uploaded); NarratorAgent (not a slideshow / illustrated-storytelling format); TranscriptionAgent (no subtitle requested).

**plan:**
  - `StoryAgent` — Outline the story blueprint per the brief — protagonist arc and pivot beats.
  - `ScreenplayAgent` — Break the drafted story into scene-by-scene units, preserving the brief's tonal register.
  - `KeyFrameAgent` — Lay out keyframes for the screenplay's settings, scene-by-scene.
  - `VideoAgent` — Animate each keyframe into a per-shot motion clip.
  - `CompositorAgent` — Output the final mp4 by composing the video, audio, and subtitle / transition elements.

## #19  (story_music_ambience, grpo_templated_x15, grpo_tmpl_x15_12836)
**user_goal** (140 chars):

> Generate a kids' picture-book audiobook about a baby grasshopper learning her highest leap, with bouncy-flute BGM and meadow-grass ambience.

**rationale:** Illustrated storytelling slideshow from a text brief with BGM + ambient layer as the only added overlays. Reject: StyleTransferAgent (no style transfer requested); StoryAgent (no NEW film authoring requested); HighlightAgent (not a highlight workflow); VideoExtendAgent (no video extension requested); VideoAgent (no NEW motion-clip generation requested); ScreenplayAgent (no NEW film scene-decomposition needed); TranslationAgent (no translation / second language requested); VideoAnalysisAgent (no source-video analysis required); IntakeVideoAgent (no source clip uploaded); BriefEnricherAgent (no image upload to enrich the brief with); TranscriptionAgent (no subtitle requested); IntakeImageAgent (no image upload); KeyFrameAgent (no keyframe planning required).

**plan:**
  - `NarrationAgent` — Author the narration script from the brief — paragraph-by-paragraph story text.
  - `IllustrationAgent` — Produce per-paragraph illustrations matching the narration.
  - `NarratorAgent` — Produce the spoken narrator track via TTS over the narration text.
  - `MusicAgent` — Generate the requested BGM, scored to the brief's mood.
  - `AmbienceAgent` — Generate the ambient sound bed the brief asks for.
  - `AudioMixAgent` — Mix the available audio tracks into one final mixed wav.
  - `CompositorAgent` — Output the final mp4 by composing the video, audio, and subtitle / transition elements.

## #20  (style_extend_music, grpo_templated_x15, grpo_tmpl_x15_08787)
**user_goal** (126 chars):

> I have a 1-minute Jerash-Roman-ruins reel — style as Jerash-Roman-mosaic, extend to 3 minutes, and add a Jordanian-mijwiz BGM.

**rationale:** Style-transferred + extended video cut from an uploaded source video with BGM as the only added overlays. Reject: NarrationAgent (not a slideshow / illustrated-storytelling format); TranslationAgent (no translation / second language requested); VideoAnalysisAgent (no source-video analysis required); KeyFrameAgent (no keyframe planning required); TranscriptionAgent (no subtitle requested); VideoAgent (no NEW motion-clip generation requested); NarratorAgent (not a slideshow / illustrated-storytelling format); IllustrationAgent (not a slideshow / illustrated-storytelling format); ScreenplayAgent (no NEW film scene-decomposition needed); BriefEnricherAgent (no image upload to enrich the brief with); HighlightAgent (not a highlight workflow); IntakeImageAgent (no image upload); StoryAgent (no NEW film authoring requested); AmbienceAgent (no environmental layer requested).

**plan:**
  - `IntakeVideoAgent` — Persist the uploaded video into the workspace as a captioned artifact.
  - `StyleTransferAgent` — Apply the requested style transfer to the source video.
  - `VideoExtendAgent` — Produce extended footage that continues the source video.
  - `MusicAgent` — Generate the requested BGM, scored to the brief's mood.
  - `AudioMixAgent` — Mix the available audio tracks into one final mixed wav.
  - `CompositorAgent` — Composite the final mp4 — assemble video, audio, and any subtitle / transitions into the deliverable.

## #21  (story_bilingual, grpo_templated_x15, grpo_tmpl_x15_10617)
**user_goal** (113 chars):

> Cook up a children's audiobook in English about a young Gold-Coast-Surfers-Paradise child, with Korean subtitles.

**rationale:** Illustrated storytelling slideshow from a text brief with bilingual narration track as the only added overlays. Reject: AmbienceAgent (no environmental layer requested); StoryAgent (no NEW film authoring requested); MusicAgent (no BGM requested); StyleTransferAgent (no style transfer requested); HighlightAgent (not a highlight workflow); BriefEnricherAgent (no image upload to enrich the brief with); VideoAnalysisAgent (no source-video analysis required); VideoAgent (no NEW motion-clip generation requested); IntakeImageAgent (no image upload); KeyFrameAgent (no keyframe planning required); TranscriptionAgent (no subtitle requested); ScreenplayAgent (no NEW film scene-decomposition needed); AudioMixAgent (no audio tracks to mix); VideoExtendAgent (no video extension requested); IntakeVideoAgent (no source clip uploaded).

**plan:**
  - `NarrationAgent` — Author the narration script from the brief — paragraph-by-paragraph story text.
  - `IllustrationAgent` — Render one still illustration per narration paragraph.
  - `NarratorAgent` — Synthesize the narrator audio track from the narration script.
  - `TranslationAgent` — Translate the source-language subtitles into the requested target language.
  - `CompositorAgent` — Composite the final mp4 — assemble video, audio, and any subtitle / transitions into the deliverable.

## #22  (vid_music_ambience, grpo_templated, grpo_tmpl_0850)
**user_goal** (111 chars):

> Layer Brazilian samba BGM and a beach-crowd-and-distant-drum ambient bed over my Brazilian-beach festival clip.

**rationale:** Modified video cut from an uploaded source video; overlays applied: BGM + ambient layer. Excluded — VideoAnalysisAgent (no source-video analysis required); TranslationAgent (no translation / second language requested); IllustrationAgent (not a slideshow / illustrated-storytelling format); VideoExtendAgent (no video extension requested); BriefEnricherAgent (no image upload to enrich the brief with); VideoAgent (no NEW motion-clip generation requested); IntakeImageAgent (no image upload); ScreenplayAgent (no NEW film scene-decomposition needed); StyleTransferAgent (no style transfer requested); HighlightAgent (not a highlight workflow); KeyFrameAgent (no keyframe planning required); StoryAgent (no NEW film authoring requested); NarratorAgent (not a slideshow / illustrated-storytelling format); TranscriptionAgent (no subtitle requested); NarrationAgent (not a slideshow / illustrated-storytelling format).

**plan:**
  - `IntakeVideoAgent` — Register the uploaded video as a captioned workspace artifact.
  - `MusicAgent` — Write the requested BGM, aligned to the brief's tonal cue.
  - `AmbienceAgent` — Author the environmental ambient layer per the brief.
  - `AudioMixAgent` — Layer the available audio tracks into the final mixed wav.
  - `CompositorAgent` — Composite the final mp4 — assemble video, audio, and any subtitle / transitions into the deliverable.

## #23  (story_pure, grpo_templated_x15, grpo_tmpl_x15_00386)
**user_goal** (97 chars):

> Generate a children's audiobook based on a Greek tale of how Athena planted the first olive tree.

**rationale:** Illustrated storytelling slideshow from a text brief; no overlays added. Excluded — VideoExtendAgent (no video extension requested); AudioMixAgent (no audio tracks to mix); IntakeVideoAgent (no source clip uploaded); IntakeImageAgent (no image upload); VideoAnalysisAgent (no source-video analysis required); MusicAgent (no BGM requested); ScreenplayAgent (no NEW film scene-decomposition needed); StoryAgent (no NEW film authoring requested); TranscriptionAgent (no subtitle requested); AmbienceAgent (no environmental layer requested); KeyFrameAgent (no keyframe planning required); StyleTransferAgent (no style transfer requested); TranslationAgent (no translation / second language requested); VideoAgent (no NEW motion-clip generation requested); BriefEnricherAgent (no image upload to enrich the brief with); HighlightAgent (not a highlight workflow).

**plan:**
  - `NarrationAgent` — Write the narration script broken into reading paragraphs.
  - `IllustrationAgent` — Generate one illustration image per paragraph of the narration.
  - `NarratorAgent` — Generate the TTS narrator audio track from the narration script.
  - `CompositorAgent` — Mux the final mp4, combining the rendered visual track with audio and any subtitle overlay.

## #24  (extend_ambience, grpo_templated_x15, grpo_tmpl_x15_04718)
**user_goal** (108 chars):

> Here's a 45-second Vélodrome-Marseille reel — extend to 2 minutes and add Vélodrome-Marseille-bowl ambience.

**rationale:** Extended video cut from an uploaded source video; overlays applied: ambient layer. Excluded — HighlightAgent (not a highlight workflow); BriefEnricherAgent (no image upload to enrich the brief with); VideoAnalysisAgent (no source-video analysis required); ScreenplayAgent (no NEW film scene-decomposition needed); NarratorAgent (not a slideshow / illustrated-storytelling format); TranscriptionAgent (no subtitle requested); IllustrationAgent (not a slideshow / illustrated-storytelling format); TranslationAgent (no translation / second language requested); StyleTransferAgent (no style transfer requested); VideoAgent (no NEW motion-clip generation requested); StoryAgent (no NEW film authoring requested); IntakeImageAgent (no image upload); KeyFrameAgent (no keyframe planning required); MusicAgent (no BGM requested); NarrationAgent (not a slideshow / illustrated-storytelling format).

**plan:**
  - `IntakeVideoAgent` — Register the uploaded video as a captioned workspace artifact.
  - `VideoExtendAgent` — Produce extended footage that continues the source video.
  - `AmbienceAgent` — Generate the ambient sound bed the brief asks for.
  - `AudioMixAgent` — Mix the available audio tracks into one final mixed wav.
  - `CompositorAgent` — Mux the final mp4, combining the rendered visual track with audio and any subtitle overlay.

## #25  (story_music_bilingual, grpo_templated_x15, grpo_tmpl_x15_13576)
**user_goal** (140 chars):

> Tell me an illustrated children's audiobook in German about The-Goose-Girl on the Falada-road, with German-folk-3 BGM and English subtitles.

**rationale:** Illustrated storytelling slideshow from a text brief with BGM + bilingual narration track as the only added overlays. Reject: VideoExtendAgent (no video extension requested); StyleTransferAgent (no style transfer requested); HighlightAgent (not a highlight workflow); IntakeVideoAgent (no source clip uploaded); TranscriptionAgent (no subtitle requested); KeyFrameAgent (no keyframe planning required); VideoAgent (no NEW motion-clip generation requested); ScreenplayAgent (no NEW film scene-decomposition needed); StoryAgent (no NEW film authoring requested); BriefEnricherAgent (no image upload to enrich the brief with); IntakeImageAgent (no image upload); AmbienceAgent (no environmental layer requested); VideoAnalysisAgent (no source-video analysis required).

**plan:**
  - `NarrationAgent` — Draft the narration script per the brief, paragraph-by-paragraph.
  - `IllustrationAgent` — Render one still illustration per narration paragraph.
  - `NarratorAgent` — Generate the TTS narrator audio track from the narration script.
  - `MusicAgent` — Write the requested BGM, aligned to the brief's tonal cue.
  - `AudioMixAgent` — Combine the produced audio layers into a single mixed wav.
  - `TranslationAgent` — Render the bilingual translation of the subtitle track.
  - `CompositorAgent` — Mux the final mp4, combining the rendered visual track with audio and any subtitle overlay.

## #26  (story_full_imgref_music_bil, grpo_templated_x15, grpo_tmpl_x15_11109)
**user_goal** (170 chars):

> Uploading a sketch of a 1920s Beirut-Bristol-Hotel waiter — build an interwar audiobook in Arabic about his Hamra-Street night, with Beirut-jazz BGM and French subtitles.

**rationale:** Illustrated storytelling slideshow produced from a text brief + uploaded reference image, layered with BGM + bilingual narration track. Skipped: ScreenplayAgent (no NEW film scene-decomposition needed); IntakeVideoAgent (no source clip uploaded); AmbienceAgent (no environmental layer requested); StyleTransferAgent (no style transfer requested); TranscriptionAgent (no subtitle requested); VideoAnalysisAgent (no source-video analysis required); VideoExtendAgent (no video extension requested); KeyFrameAgent (no keyframe planning required); HighlightAgent (not a highlight workflow); VideoAgent (no NEW motion-clip generation requested); StoryAgent (no NEW film authoring requested).

**plan:**
  - `IntakeImageAgent` — Persist the uploaded image into the workspace as a captioned artifact.
  - `BriefEnricherAgent` — Augment the brief with the uploaded image's descriptive content.
  - `NarrationAgent` — Draft the narration script per the brief, paragraph-by-paragraph.
  - `IllustrationAgent` — Produce per-paragraph illustrations matching the narration.
  - `NarratorAgent` — Generate the TTS narrator audio track from the narration script.
  - `MusicAgent` — Write the requested BGM, aligned to the brief's tonal cue.
  - `AudioMixAgent` — Combine the produced audio layers into a single mixed wav.
  - `TranslationAgent` — Render the bilingual translation of the subtitle track.
  - `CompositorAgent` — Composite the final mp4 — assemble video, audio, and any subtitle / transitions into the deliverable.

## #27  (extend_style_subtitle, grpo_templated_x15, grpo_tmpl_x15_06767)
**user_goal** (125 chars):

> Here's a 1-minute NVIDIA-RTX-GPU-unboxing reel — extend to 3 minutes, convert to NVIDIA-render, and overlay English captions.

**rationale:** Style-transferred + extended video cut from an uploaded source video; overlays applied: subtitles. Excluded — TranslationAgent (no translation / second language requested); KeyFrameAgent (no keyframe planning required); HighlightAgent (not a highlight workflow); NarrationAgent (not a slideshow / illustrated-storytelling format); ScreenplayAgent (no NEW film scene-decomposition needed); AudioMixAgent (no audio tracks to mix); BriefEnricherAgent (no image upload to enrich the brief with); IntakeImageAgent (no image upload); MusicAgent (no BGM requested); NarratorAgent (not a slideshow / illustrated-storytelling format); AmbienceAgent (no environmental layer requested); StoryAgent (no NEW film authoring requested); IllustrationAgent (not a slideshow / illustrated-storytelling format); VideoAgent (no NEW motion-clip generation requested); VideoAnalysisAgent (no source-video analysis required).

**plan:**
  - `IntakeVideoAgent` — Ingest the uploaded video into the workspace with caption metadata.
  - `VideoExtendAgent` — Extend the source video beyond its original duration.
  - `StyleTransferAgent` — Run style transfer on the source video to match the requested aesthetic.
  - `TranscriptionAgent` — Generate the subtitle track from the dialogue audio with per-line timestamps.
  - `CompositorAgent` — Output the final mp4 by composing the video, audio, and subtitle / transition elements.

## #28  (cr_music_ambience, grpo_templated_x15, grpo_tmpl_x15_01074)
**user_goal** (154 chars):

> Build a 30-second piece of a young watchmaker assembling a clockwork bird, with music-box score and Victorian-workshop ambient (gear ticks, distant rain).

**rationale:** Cinematic mini-drama from a text brief with BGM + ambient layer as the only added overlays. Reject: VideoExtendAgent (no video extension requested); TranscriptionAgent (no subtitle requested); HighlightAgent (not a highlight workflow); IntakeVideoAgent (no source clip uploaded); BriefEnricherAgent (no image upload to enrich the brief with); StyleTransferAgent (no style transfer requested); IntakeImageAgent (no image upload); NarrationAgent (not a slideshow / illustrated-storytelling format); IllustrationAgent (not a slideshow / illustrated-storytelling format); VideoAnalysisAgent (no source-video analysis required); NarratorAgent (not a slideshow / illustrated-storytelling format); TranslationAgent (no translation / second language requested).

**plan:**
  - `StoryAgent` — Outline the story blueprint per the brief — protagonist arc and pivot beats.
  - `ScreenplayAgent` — Break the drafted story into scene-by-scene units, preserving the brief's tonal register.
  - `KeyFrameAgent` — Plan keyframes for the screenplay's settings, one per scene.
  - `VideoAgent` — Render per-shot motion clips from the keyframes, preserving visual continuity.
  - `MusicAgent` — Generate the requested BGM, scored to the brief's mood.
  - `AmbienceAgent` — Produce the requested ambient atmosphere as an audio bed.
  - `AudioMixAgent` — Mix the available audio tracks into one final mixed wav.
  - `CompositorAgent` — Composite the final mp4 — assemble video, audio, and any subtitle / transitions into the deliverable.

## #29  (style_subtitle, grpo_templated_x15, grpo_tmpl_x15_04036)
**user_goal** (124 chars):

> Uploading a 2-minute fishing-knot tutorial — render as a vintage maritime nautical-knot guide and overlay English subtitles.

**rationale:** Style-transferred video cut from an uploaded source video with subtitles as the only added overlays. Reject: VideoExtendAgent (no video extension requested); VideoAnalysisAgent (no source-video analysis required); HighlightAgent (not a highlight workflow); IllustrationAgent (not a slideshow / illustrated-storytelling format); NarratorAgent (not a slideshow / illustrated-storytelling format); IntakeImageAgent (no image upload); ScreenplayAgent (no NEW film scene-decomposition needed); MusicAgent (no BGM requested); TranslationAgent (no translation / second language requested); StoryAgent (no NEW film authoring requested); KeyFrameAgent (no keyframe planning required); VideoAgent (no NEW motion-clip generation requested); NarrationAgent (not a slideshow / illustrated-storytelling format); AudioMixAgent (no audio tracks to mix); BriefEnricherAgent (no image upload to enrich the brief with); AmbienceAgent (no environmental layer requested).

**plan:**
  - `IntakeVideoAgent` — Register the uploaded video as a captioned workspace artifact.
  - `StyleTransferAgent` — Run style transfer on the source video to match the requested aesthetic.
  - `TranscriptionAgent` — Generate the subtitle track from the dialogue audio with per-line timestamps.
  - `CompositorAgent` — Output the final mp4 by composing the video, audio, and subtitle / transition elements.

## #30  (extend_ambience, grpo_templated_x15, grpo_tmpl_x15_04751)
**user_goal** (116 chars):

> Here's a 45-second Sydney-Cricket-Ground reel — extend to 2 minutes and overlay Sydney-Cricket-Ground-bowl ambience.

**rationale:** Extended video cut from an uploaded source video; overlays applied: ambient layer. Excluded — VideoAnalysisAgent (no source-video analysis required); NarratorAgent (not a slideshow / illustrated-storytelling format); IntakeImageAgent (no image upload); KeyFrameAgent (no keyframe planning required); TranscriptionAgent (no subtitle requested); TranslationAgent (no translation / second language requested); HighlightAgent (not a highlight workflow); IllustrationAgent (not a slideshow / illustrated-storytelling format); StyleTransferAgent (no style transfer requested); VideoAgent (no NEW motion-clip generation requested); ScreenplayAgent (no NEW film scene-decomposition needed); MusicAgent (no BGM requested); StoryAgent (no NEW film authoring requested); BriefEnricherAgent (no image upload to enrich the brief with); NarrationAgent (not a slideshow / illustrated-storytelling format).

**plan:**
  - `IntakeVideoAgent` — Register the uploaded video as a captioned workspace artifact.
  - `VideoExtendAgent` — Produce extended footage that continues the source video.
  - `AmbienceAgent` — Produce the requested ambient atmosphere as an audio bed.
  - `AudioMixAgent` — Combine the produced audio layers into a single mixed wav.
  - `CompositorAgent` — Output the final mp4 by composing the video, audio, and subtitle / transition elements.
