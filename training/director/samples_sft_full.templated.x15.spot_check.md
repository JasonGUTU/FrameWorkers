# Templated SFT spot check — 50 of 15850 samples

Variation comes from: 3 rationale skeletons × per-sample shuffled reject list × 3 intent variants per agent (md5-hash picked).

---

## #1
**user_goal** (149 chars):

> I have a Singin'-in-the-Rain reference — please analyze its rain-soaked lamppost dance and produce a 30-second new mini-drama with English subtitles.

**rationale:** Reference-video-informed cinematic mini-drama from an uploaded source video; overlays applied: subtitles. Excluded — IntakeImageAgent (no image upload); TranslationAgent (no translation / second language requested); HighlightAgent (not a highlight workflow); StyleTransferAgent (no style transfer requested); VideoExtendAgent (no video extension requested); AmbienceAgent (no environmental layer requested); IllustrationAgent (not a slideshow / illustrated-storytelling format); NarratorAgent (not a slideshow / illustrated-storytelling format); AudioMixAgent (no audio tracks to mix); BriefEnricherAgent (no image upload to enrich the brief with); MusicAgent (no BGM requested); NarrationAgent (not a slideshow / illustrated-storytelling format).

**plan:**
  - `IntakeVideoAgent` — Ingest the uploaded video into the workspace with caption metadata.
  - `VideoAnalysisAgent` — Produce a scene-level analysis report of the source video for downstream reasoning.
  - `StoryAgent` — Author the story blueprint following the brief, with a clear arc and beat structure.
  - `ScreenplayAgent` — Decompose the story into scenes with mood progression aligned to the brief.
  - `KeyFrameAgent` — Design keyframes from the screenplay scene by scene.
  - `VideoAgent` — Animate each keyframe into a per-shot motion clip.
  - `TranscriptionAgent` — Author the timestamped transcription of the spoken dialogue.
  - `CompositorAgent` — Composite the final mp4 — assemble video, audio, and any subtitle / transitions into the deliverable.

## #2
**user_goal** (121 chars):

> Here's a sketch of a young Niuafo'ou-shellsmith — render a 45-second cinematic short with Niuafo'ou and Tongan subtitles.

**rationale:** Cinematic mini-drama produced from a text brief + uploaded reference image, layered with bilingual subtitles. Skipped: VideoExtendAgent (no video extension requested); IntakeVideoAgent (no source clip uploaded); StyleTransferAgent (no style transfer requested); AudioMixAgent (no audio tracks to mix); AmbienceAgent (no environmental layer requested); NarrationAgent (not a slideshow / illustrated-storytelling format); HighlightAgent (not a highlight workflow); MusicAgent (no BGM requested); NarratorAgent (not a slideshow / illustrated-storytelling format); VideoAnalysisAgent (no source-video analysis required); IllustrationAgent (not a slideshow / illustrated-storytelling format).

**plan:**
  - `IntakeImageAgent` — Persist the uploaded image into the workspace as a captioned artifact.
  - `BriefEnricherAgent` — Enrich the brief by integrating descriptions of the uploaded reference images.
  - `StoryAgent` — Author the story blueprint following the brief, with a clear arc and beat structure.
  - `ScreenplayAgent` — Convert the story into a scene-by-scene screenplay matching the brief's register.
  - `KeyFrameAgent` — Plan keyframes for the screenplay's settings, one per scene.
  - `VideoAgent` — Render per-shot motion clips from the keyframes, preserving visual continuity.
  - `TranscriptionAgent` — Generate the subtitle track from the dialogue audio with per-line timestamps.
  - `TranslationAgent` — Produce the second-language subtitle track from the source transcription.
  - `CompositorAgent` — Mux the final mp4, combining the rendered visual track with audio and any subtitle overlay.

## #3
**user_goal** (125 chars):

> Uploading a 30-second Hanoi-old-quarter reel — render as a Vietnamese-folk illustration and overlay a Vietnamese-dan-bau BGM.

**rationale:** Style-transferred video cut from an uploaded source video with BGM as the only added overlays. Reject: StoryAgent (no NEW film authoring requested); TranscriptionAgent (no subtitle requested); IntakeImageAgent (no image upload); VideoAgent (no NEW motion-clip generation requested); VideoAnalysisAgent (no source-video analysis required); IllustrationAgent (not a slideshow / illustrated-storytelling format); ScreenplayAgent (no NEW film scene-decomposition needed); BriefEnricherAgent (no image upload to enrich the brief with); NarratorAgent (not a slideshow / illustrated-storytelling format); VideoExtendAgent (no video extension requested); KeyFrameAgent (no keyframe planning required); TranslationAgent (no translation / second language requested); NarrationAgent (not a slideshow / illustrated-storytelling format); HighlightAgent (not a highlight workflow); AmbienceAgent (no environmental layer requested).

**plan:**
  - `IntakeVideoAgent` — Register the uploaded video as a captioned workspace artifact.
  - `StyleTransferAgent` — Re-render the source video under the requested visual style.
  - `MusicAgent` — Compose the BGM the user requested, matching the brief's emotional register.
  - `AudioMixAgent` — Mix the available audio tracks into one final mixed wav.
  - `CompositorAgent` — Mux the final mp4, combining the rendered visual track with audio and any subtitle overlay.

## #4
**user_goal** (120 chars):

> Uploading a 1-minute Bridgetown-Garrison reel — style as Caribbean-tropical, extend to 3 minutes, and add a calypso BGM.

**rationale:** Style-transferred + extended video cut from an uploaded source video with BGM as the only added overlays. Reject: NarratorAgent (not a slideshow / illustrated-storytelling format); BriefEnricherAgent (no image upload to enrich the brief with); NarrationAgent (not a slideshow / illustrated-storytelling format); TranslationAgent (no translation / second language requested); VideoAgent (no NEW motion-clip generation requested); HighlightAgent (not a highlight workflow); ScreenplayAgent (no NEW film scene-decomposition needed); TranscriptionAgent (no subtitle requested); IntakeImageAgent (no image upload); KeyFrameAgent (no keyframe planning required); VideoAnalysisAgent (no source-video analysis required); IllustrationAgent (not a slideshow / illustrated-storytelling format); StoryAgent (no NEW film authoring requested); AmbienceAgent (no environmental layer requested).

**plan:**
  - `IntakeVideoAgent` — Register the uploaded video as a captioned workspace artifact.
  - `StyleTransferAgent` — Apply the requested style transfer to the source video.
  - `VideoExtendAgent` — Extend the source video beyond its original duration.
  - `MusicAgent` — Generate the requested BGM, scored to the brief's mood.
  - `AudioMixAgent` — Combine the produced audio layers into a single mixed wav.
  - `CompositorAgent` — Output the final mp4 by composing the video, audio, and subtitle / transition elements.

## #5
**user_goal** (128 chars):

> I have a 1-minute Pashmina-shawl-Kashmir reel — extend to 3 minutes, style as Kashmiri-jamawar-print, and add English subtitles.

**rationale:** Style-transferred + extended video cut from an uploaded source video; overlays applied: subtitles. Excluded — VideoAnalysisAgent (no source-video analysis required); KeyFrameAgent (no keyframe planning required); HighlightAgent (not a highlight workflow); StoryAgent (no NEW film authoring requested); AmbienceAgent (no environmental layer requested); BriefEnricherAgent (no image upload to enrich the brief with); IllustrationAgent (not a slideshow / illustrated-storytelling format); NarratorAgent (not a slideshow / illustrated-storytelling format); MusicAgent (no BGM requested); AudioMixAgent (no audio tracks to mix); IntakeImageAgent (no image upload); ScreenplayAgent (no NEW film scene-decomposition needed); NarrationAgent (not a slideshow / illustrated-storytelling format); TranslationAgent (no translation / second language requested); VideoAgent (no NEW motion-clip generation requested).

**plan:**
  - `IntakeVideoAgent` — Register the uploaded video as a captioned workspace artifact.
  - `VideoExtendAgent` — Produce extended footage that continues the source video.
  - `StyleTransferAgent` — Apply the requested style transfer to the source video.
  - `TranscriptionAgent` — Author the timestamped transcription of the spoken dialogue.
  - `CompositorAgent` — Output the final mp4 by composing the video, audio, and subtitle / transition elements.

## #6
**user_goal** (96 chars):

> Generate a narrated picture-book in Ukrainian about a young steppe wolf, with English subtitles.

**rationale:** Illustrated storytelling slideshow from a text brief; overlays applied: bilingual narration track. Excluded — MusicAgent (no BGM requested); VideoExtendAgent (no video extension requested); ScreenplayAgent (no NEW film scene-decomposition needed); IntakeImageAgent (no image upload); IntakeVideoAgent (no source clip uploaded); VideoAgent (no NEW motion-clip generation requested); AudioMixAgent (no audio tracks to mix); AmbienceAgent (no environmental layer requested); TranscriptionAgent (no subtitle requested); KeyFrameAgent (no keyframe planning required); StoryAgent (no NEW film authoring requested); VideoAnalysisAgent (no source-video analysis required); StyleTransferAgent (no style transfer requested); BriefEnricherAgent (no image upload to enrich the brief with); HighlightAgent (not a highlight workflow).

**plan:**
  - `NarrationAgent` — Author the narration script from the brief — paragraph-by-paragraph story text.
  - `IllustrationAgent` — Generate one illustration image per paragraph of the narration.
  - `NarratorAgent` — Synthesize the narrator audio track from the narration script.
  - `TranslationAgent` — Translate the source-language subtitles into the requested target language.
  - `CompositorAgent` — Mux the final mp4, combining the rendered visual track with audio and any subtitle overlay.

## #7
**user_goal** (158 chars):

> I'm sending you a watercolor of a young Babylonian astrologer girl — build an illustrated children's tale of her lapis-tower dusk, with Mesopotamian-lyre BGM.

**rationale:** Illustrated storytelling slideshow from a text brief + uploaded reference image with BGM as the only added overlays. Reject: VideoAnalysisAgent (no source-video analysis required); AmbienceAgent (no environmental layer requested); VideoExtendAgent (no video extension requested); HighlightAgent (not a highlight workflow); VideoAgent (no NEW motion-clip generation requested); KeyFrameAgent (no keyframe planning required); ScreenplayAgent (no NEW film scene-decomposition needed); TranslationAgent (no translation / second language requested); StoryAgent (no NEW film authoring requested); IntakeVideoAgent (no source clip uploaded); StyleTransferAgent (no style transfer requested); TranscriptionAgent (no subtitle requested).

**plan:**
  - `IntakeImageAgent` — Register the uploaded image as a captioned workspace artifact.
  - `BriefEnricherAgent` — Augment the brief with the uploaded image's descriptive content.
  - `NarrationAgent` — Write the narration script broken into reading paragraphs.
  - `IllustrationAgent` — Generate one illustration image per paragraph of the narration.
  - `NarratorAgent` — Produce the spoken narrator track via TTS over the narration text.
  - `MusicAgent` — Write the requested BGM, aligned to the brief's tonal cue.
  - `AudioMixAgent` — Combine the produced audio layers into a single mixed wav.
  - `CompositorAgent` — Mux the final mp4, combining the rendered visual track with audio and any subtitle overlay.

## #8
**user_goal** (108 chars):

> Uploading a Luca-Guadagnino reference — analyze its summer sensuality and produce a 2-minute new mini-drama.

**rationale:** Reference-video-informed cinematic mini-drama from an uploaded source video; no overlays added. Excluded — AmbienceAgent (no environmental layer requested); BriefEnricherAgent (no image upload to enrich the brief with); NarratorAgent (not a slideshow / illustrated-storytelling format); VideoExtendAgent (no video extension requested); StyleTransferAgent (no style transfer requested); IntakeImageAgent (no image upload); AudioMixAgent (no audio tracks to mix); NarrationAgent (not a slideshow / illustrated-storytelling format); HighlightAgent (not a highlight workflow); TranslationAgent (no translation / second language requested); MusicAgent (no BGM requested); TranscriptionAgent (no subtitle requested); IllustrationAgent (not a slideshow / illustrated-storytelling format).

**plan:**
  - `IntakeVideoAgent` — Persist the uploaded video into the workspace as a captioned artifact.
  - `VideoAnalysisAgent` — Generate a structured scene-level report of the source video.
  - `StoryAgent` — Author the story blueprint following the brief, with a clear arc and beat structure.
  - `ScreenplayAgent` — Decompose the story into scenes with mood progression aligned to the brief.
  - `KeyFrameAgent` — Plan keyframes for the screenplay's settings, one per scene.
  - `VideoAgent` — Render per-shot motion clips from the keyframes, preserving visual continuity.
  - `CompositorAgent` — Output the final mp4 by composing the video, audio, and subtitle / transition elements.

## #9
**user_goal** (99 chars):

> Here's a 30-second whimsical-NY reel — extend to 90 seconds and style as Maira-Kalman illustration.

**rationale:** Style-transferred + extended video cut produced from an uploaded source video, nothing layered on top. Skipped: VideoAgent (no NEW motion-clip generation requested); MusicAgent (no BGM requested); BriefEnricherAgent (no image upload to enrich the brief with); NarrationAgent (not a slideshow / illustrated-storytelling format); AudioMixAgent (no audio tracks to mix); TranscriptionAgent (no subtitle requested); StoryAgent (no NEW film authoring requested); KeyFrameAgent (no keyframe planning required); CompositorAgent (no final mux required); IntakeImageAgent (no image upload); NarratorAgent (not a slideshow / illustrated-storytelling format); HighlightAgent (not a highlight workflow); IllustrationAgent (not a slideshow / illustrated-storytelling format); TranslationAgent (no translation / second language requested); ScreenplayAgent (no NEW film scene-decomposition needed); AmbienceAgent (no environmental layer requested); VideoAnalysisAgent (no source-video analysis required).

**plan:**
  - `IntakeVideoAgent` — Persist the uploaded video into the workspace as a captioned artifact.
  - `VideoExtendAgent` — Produce extended footage that continues the source video.
  - `StyleTransferAgent` — Apply the requested style transfer to the source video.

## #10
**user_goal** (111 chars):

> Cook up a children's audiobook about a baby leaf-insect mimicking a forest-leaf, with forest-canopy-2 ambience.

**rationale:** Illustrated storytelling slideshow from a text brief with ambient layer as the only added overlays. Reject: MusicAgent (no BGM requested); IntakeImageAgent (no image upload); StyleTransferAgent (no style transfer requested); StoryAgent (no NEW film authoring requested); TranslationAgent (no translation / second language requested); BriefEnricherAgent (no image upload to enrich the brief with); VideoAnalysisAgent (no source-video analysis required); VideoExtendAgent (no video extension requested); KeyFrameAgent (no keyframe planning required); IntakeVideoAgent (no source clip uploaded); VideoAgent (no NEW motion-clip generation requested); TranscriptionAgent (no subtitle requested); ScreenplayAgent (no NEW film scene-decomposition needed); HighlightAgent (not a highlight workflow).

**plan:**
  - `NarrationAgent` — Write the narration script broken into reading paragraphs.
  - `IllustrationAgent` — Generate one illustration image per paragraph of the narration.
  - `NarratorAgent` — Synthesize the narrator audio track from the narration script.
  - `AmbienceAgent` — Generate the ambient sound bed the brief asks for.
  - `AudioMixAgent` — Combine the produced audio layers into a single mixed wav.
  - `CompositorAgent` — Mux the final mp4, combining the rendered visual track with audio and any subtitle overlay.

## #11
**user_goal** (108 chars):

> I'm sending you a 30-second Vatican-Museum reel — extend to 90 seconds and overlay Vatican-Sistine ambience.

**rationale:** Extended video cut produced from an uploaded source video, layered with ambient layer. Skipped: IllustrationAgent (not a slideshow / illustrated-storytelling format); MusicAgent (no BGM requested); VideoAnalysisAgent (no source-video analysis required); TranslationAgent (no translation / second language requested); HighlightAgent (not a highlight workflow); TranscriptionAgent (no subtitle requested); NarrationAgent (not a slideshow / illustrated-storytelling format); StoryAgent (no NEW film authoring requested); IntakeImageAgent (no image upload); NarratorAgent (not a slideshow / illustrated-storytelling format); StyleTransferAgent (no style transfer requested); BriefEnricherAgent (no image upload to enrich the brief with); VideoAgent (no NEW motion-clip generation requested); KeyFrameAgent (no keyframe planning required); ScreenplayAgent (no NEW film scene-decomposition needed).

**plan:**
  - `IntakeVideoAgent` — Register the uploaded video as a captioned workspace artifact.
  - `VideoExtendAgent` — Produce extended footage that continues the source video.
  - `AmbienceAgent` — Author the environmental ambient layer per the brief.
  - `AudioMixAgent` — Mix the available audio tracks into one final mixed wav.
  - `CompositorAgent` — Output the final mp4 by composing the video, audio, and subtitle / transition elements.

## #12
**user_goal** (107 chars):

> Generate a children's bedtime audiobook in Assamese about a young one-horned rhino, with Bengali subtitles.

**rationale:** Illustrated storytelling slideshow from a text brief with bilingual narration track as the only added overlays. Reject: VideoExtendAgent (no video extension requested); AmbienceAgent (no environmental layer requested); ScreenplayAgent (no NEW film scene-decomposition needed); VideoAgent (no NEW motion-clip generation requested); MusicAgent (no BGM requested); StyleTransferAgent (no style transfer requested); AudioMixAgent (no audio tracks to mix); IntakeVideoAgent (no source clip uploaded); BriefEnricherAgent (no image upload to enrich the brief with); HighlightAgent (not a highlight workflow); TranscriptionAgent (no subtitle requested); VideoAnalysisAgent (no source-video analysis required); IntakeImageAgent (no image upload); StoryAgent (no NEW film authoring requested); KeyFrameAgent (no keyframe planning required).

**plan:**
  - `NarrationAgent` — Draft the narration script per the brief, paragraph-by-paragraph.
  - `IllustrationAgent` — Produce per-paragraph illustrations matching the narration.
  - `NarratorAgent` — Generate the TTS narrator audio track from the narration script.
  - `TranslationAgent` — Produce the second-language subtitle track from the source transcription.
  - `CompositorAgent` — Output the final mp4 by composing the video, audio, and subtitle / transition elements.

## #13
**user_goal** (144 chars):

> Uploading an Albert-Lamorisse Red-Balloon reference — please analyze its silent Parisian-childhood whimsy and produce a 1-minute new mini-drama.

**rationale:** Reference-video-informed cinematic mini-drama produced from an uploaded source video, nothing layered on top. Skipped: IllustrationAgent (not a slideshow / illustrated-storytelling format); AudioMixAgent (no audio tracks to mix); TranscriptionAgent (no subtitle requested); VideoExtendAgent (no video extension requested); MusicAgent (no BGM requested); StyleTransferAgent (no style transfer requested); IntakeImageAgent (no image upload); TranslationAgent (no translation / second language requested); NarrationAgent (not a slideshow / illustrated-storytelling format); NarratorAgent (not a slideshow / illustrated-storytelling format); AmbienceAgent (no environmental layer requested); BriefEnricherAgent (no image upload to enrich the brief with); HighlightAgent (not a highlight workflow).

**plan:**
  - `IntakeVideoAgent` — Register the uploaded video as a captioned workspace artifact.
  - `VideoAnalysisAgent` — Produce a scene-level analysis report of the source video for downstream reasoning.
  - `StoryAgent` — Author the story blueprint following the brief, with a clear arc and beat structure.
  - `ScreenplayAgent` — Break the drafted story into scene-by-scene units, preserving the brief's tonal register.
  - `KeyFrameAgent` — Plan keyframes for the screenplay's settings, one per scene.
  - `VideoAgent` — Animate each keyframe into a per-shot motion clip.
  - `CompositorAgent` — Composite the final mp4 — assemble video, audio, and any subtitle / transitions into the deliverable.

## #14
**user_goal** (122 chars):

> Using this uploaded photo of an old mansion, make a haunted-house mystery mini-drama where a new tenant discovers a ghost.

**rationale:** Cinematic mini-drama produced from a text brief + uploaded reference image, nothing layered on top. Skipped: MusicAgent (no BGM requested); TranscriptionAgent (no subtitle requested); StyleTransferAgent (no style transfer requested); NarratorAgent (not a slideshow / illustrated-storytelling format); AudioMixAgent (no audio tracks to mix); TranslationAgent (no translation / second language requested); HighlightAgent (not a highlight workflow); IllustrationAgent (not a slideshow / illustrated-storytelling format); VideoAnalysisAgent (no source-video analysis required); AmbienceAgent (no environmental layer requested); NarrationAgent (not a slideshow / illustrated-storytelling format); VideoExtendAgent (no video extension requested); IntakeVideoAgent (no source clip uploaded).

**plan:**
  - `IntakeImageAgent` — Register the uploaded image as a captioned workspace artifact.
  - `BriefEnricherAgent` — Enrich the brief by integrating descriptions of the uploaded reference images.
  - `StoryAgent` — Author the story blueprint following the brief, with a clear arc and beat structure.
  - `ScreenplayAgent` — Convert the story into a scene-by-scene screenplay matching the brief's register.
  - `KeyFrameAgent` — Design keyframes from the screenplay scene by scene.
  - `VideoAgent` — Produce per-shot video clips from each keyframe, holding aesthetic continuity across cuts.
  - `CompositorAgent` — Composite the final mp4 — assemble video, audio, and any subtitle / transitions into the deliverable.

## #15
**user_goal** (107 chars):

> Produce a narrated children's audiobook in Icelandic about a young Icelandic horse, with English subtitles.

**rationale:** Illustrated storytelling slideshow from a text brief; overlays applied: bilingual narration track. Excluded — StyleTransferAgent (no style transfer requested); BriefEnricherAgent (no image upload to enrich the brief with); VideoExtendAgent (no video extension requested); StoryAgent (no NEW film authoring requested); AudioMixAgent (no audio tracks to mix); TranscriptionAgent (no subtitle requested); KeyFrameAgent (no keyframe planning required); HighlightAgent (not a highlight workflow); IntakeImageAgent (no image upload); VideoAgent (no NEW motion-clip generation requested); ScreenplayAgent (no NEW film scene-decomposition needed); MusicAgent (no BGM requested); VideoAnalysisAgent (no source-video analysis required); IntakeVideoAgent (no source clip uploaded); AmbienceAgent (no environmental layer requested).

**plan:**
  - `NarrationAgent` — Write the narration script broken into reading paragraphs.
  - `IllustrationAgent` — Generate one illustration image per paragraph of the narration.
  - `NarratorAgent` — Produce the spoken narrator track via TTS over the narration text.
  - `TranslationAgent` — Render the bilingual translation of the subtitle track.
  - `CompositorAgent` — Mux the final mp4, combining the rendered visual track with audio and any subtitle overlay.

## #16
**user_goal** (77 chars):

> Uploading a 45-minute high-school soccer match — extract the highlight clips.

**rationale:** Highlight reel from an uploaded source video with no audio / subtitle overlays. Reject: NarrationAgent (not a slideshow / illustrated-storytelling format); TranscriptionAgent (no subtitle requested); ScreenplayAgent (no NEW film scene-decomposition needed); AmbienceAgent (no environmental layer requested); IllustrationAgent (not a slideshow / illustrated-storytelling format); VideoExtendAgent (no video extension requested); StyleTransferAgent (no style transfer requested); NarratorAgent (not a slideshow / illustrated-storytelling format); BriefEnricherAgent (no image upload to enrich the brief with); MusicAgent (no BGM requested); CompositorAgent (no final mux required); TranslationAgent (no translation / second language requested); StoryAgent (no NEW film authoring requested); AudioMixAgent (no audio tracks to mix); IntakeImageAgent (no image upload); VideoAgent (no NEW motion-clip generation requested); KeyFrameAgent (no keyframe planning required).

**plan:**
  - `IntakeVideoAgent` — Register the uploaded video as a captioned workspace artifact.
  - `VideoAnalysisAgent` — Generate a structured scene-level report of the source video.
  - `HighlightAgent` — Extract the highlight moments from the analyzed video.

## #17
**user_goal** (147 chars):

> Uploading a watercolor of a young Tang-Luoyang-Imperial-Palace dance-girl — make a 1-minute mini-drama with Middle-Chinese and Tocharian subtitles.

**rationale:** Cinematic mini-drama produced from a text brief + uploaded reference image, layered with bilingual subtitles. Skipped: IntakeVideoAgent (no source clip uploaded); AmbienceAgent (no environmental layer requested); AudioMixAgent (no audio tracks to mix); NarratorAgent (not a slideshow / illustrated-storytelling format); VideoExtendAgent (no video extension requested); MusicAgent (no BGM requested); HighlightAgent (not a highlight workflow); IllustrationAgent (not a slideshow / illustrated-storytelling format); VideoAnalysisAgent (no source-video analysis required); NarrationAgent (not a slideshow / illustrated-storytelling format); StyleTransferAgent (no style transfer requested).

**plan:**
  - `IntakeImageAgent` — Ingest the uploaded image into the workspace with caption metadata.
  - `BriefEnricherAgent` — Fold image-reference descriptions into the brief to produce an enriched creative brief.
  - `StoryAgent` — Author the story blueprint following the brief, with a clear arc and beat structure.
  - `ScreenplayAgent` — Decompose the story into scenes with mood progression aligned to the brief.
  - `KeyFrameAgent` — Lay out keyframes for the screenplay's settings, scene-by-scene.
  - `VideoAgent` — Animate each keyframe into a per-shot motion clip.
  - `TranscriptionAgent` — Generate the subtitle track from the dialogue audio with per-line timestamps.
  - `TranslationAgent` — Produce the second-language subtitle track from the source transcription.
  - `CompositorAgent` — Output the final mp4 by composing the video, audio, and subtitle / transition elements.

## #18
**user_goal** (81 chars):

> Uploading a 5-hour cricket test match — pull highlights with epic-orchestral BGM.

**rationale:** Highlight reel produced from an uploaded source video, layered with BGM. Skipped: StyleTransferAgent (no style transfer requested); VideoAgent (no NEW motion-clip generation requested); BriefEnricherAgent (no image upload to enrich the brief with); NarrationAgent (not a slideshow / illustrated-storytelling format); VideoExtendAgent (no video extension requested); TranslationAgent (no translation / second language requested); AmbienceAgent (no environmental layer requested); ScreenplayAgent (no NEW film scene-decomposition needed); KeyFrameAgent (no keyframe planning required); TranscriptionAgent (no subtitle requested); NarratorAgent (not a slideshow / illustrated-storytelling format); IntakeImageAgent (no image upload); StoryAgent (no NEW film authoring requested); IllustrationAgent (not a slideshow / illustrated-storytelling format).

**plan:**
  - `IntakeVideoAgent` — Ingest the uploaded video into the workspace with caption metadata.
  - `VideoAnalysisAgent` — Analyze the source video into a scene-by-scene report (genre, mood, beats, entities).
  - `HighlightAgent` — Extract the highlight moments from the analyzed video.
  - `MusicAgent` — Compose the BGM the user requested, matching the brief's emotional register.
  - `AudioMixAgent` — Layer the available audio tracks into the final mixed wav.
  - `CompositorAgent` — Composite the final mp4 — assemble video, audio, and any subtitle / transitions into the deliverable.

## #19
**user_goal** (146 chars):

> Narrate this forest-adventure children's story as an illustrated audiobook with a gentle forest-ambience bed (wind through leaves, distant birds).

**rationale:** Illustrated storytelling slideshow produced from a text brief, layered with ambient layer. Skipped: StyleTransferAgent (no style transfer requested); StoryAgent (no NEW film authoring requested); TranscriptionAgent (no subtitle requested); VideoExtendAgent (no video extension requested); MusicAgent (no BGM requested); VideoAnalysisAgent (no source-video analysis required); HighlightAgent (not a highlight workflow); VideoAgent (no NEW motion-clip generation requested); ScreenplayAgent (no NEW film scene-decomposition needed); TranslationAgent (no translation / second language requested); IntakeImageAgent (no image upload); IntakeVideoAgent (no source clip uploaded); BriefEnricherAgent (no image upload to enrich the brief with); KeyFrameAgent (no keyframe planning required).

**plan:**
  - `NarrationAgent` — Write the narration script broken into reading paragraphs.
  - `IllustrationAgent` — Render one still illustration per narration paragraph.
  - `NarratorAgent` — Synthesize the narrator audio track from the narration script.
  - `AmbienceAgent` — Generate the ambient sound bed the brief asks for.
  - `AudioMixAgent` — Combine the produced audio layers into a single mixed wav.
  - `CompositorAgent` — Mux the final mp4, combining the rendered visual track with audio and any subtitle overlay.

## #20
**user_goal** (122 chars):

> Tell me an illustrated children's audiobook in Zulu about a young rhino, with Zulu-isicathamiya BGM and English subtitles.

**rationale:** Illustrated storytelling slideshow from a text brief with BGM + bilingual narration track as the only added overlays. Reject: VideoAnalysisAgent (no source-video analysis required); VideoExtendAgent (no video extension requested); IntakeImageAgent (no image upload); IntakeVideoAgent (no source clip uploaded); StoryAgent (no NEW film authoring requested); StyleTransferAgent (no style transfer requested); ScreenplayAgent (no NEW film scene-decomposition needed); AmbienceAgent (no environmental layer requested); KeyFrameAgent (no keyframe planning required); TranscriptionAgent (no subtitle requested); BriefEnricherAgent (no image upload to enrich the brief with); HighlightAgent (not a highlight workflow); VideoAgent (no NEW motion-clip generation requested).

**plan:**
  - `NarrationAgent` — Write the narration script broken into reading paragraphs.
  - `IllustrationAgent` — Generate one illustration image per paragraph of the narration.
  - `NarratorAgent` — Synthesize the narrator audio track from the narration script.
  - `MusicAgent` — Generate the requested BGM, scored to the brief's mood.
  - `AudioMixAgent` — Combine the produced audio layers into a single mixed wav.
  - `TranslationAgent` — Render the bilingual translation of the subtitle track.
  - `CompositorAgent` — Composite the final mp4 — assemble video, audio, and any subtitle / transitions into the deliverable.

## #21
**user_goal** (142 chars):

> I'm sending you a 1-minute clip of a Prague-old-town stroll — style as an Alfons-Mucha Art-Nouveau poster and overlay a Czech-folk-fiddle BGM.

**rationale:** Style-transferred video cut from an uploaded source video; overlays applied: BGM. Excluded — VideoExtendAgent (no video extension requested); TranscriptionAgent (no subtitle requested); KeyFrameAgent (no keyframe planning required); AmbienceAgent (no environmental layer requested); HighlightAgent (not a highlight workflow); IntakeImageAgent (no image upload); NarratorAgent (not a slideshow / illustrated-storytelling format); VideoAnalysisAgent (no source-video analysis required); NarrationAgent (not a slideshow / illustrated-storytelling format); BriefEnricherAgent (no image upload to enrich the brief with); TranslationAgent (no translation / second language requested); VideoAgent (no NEW motion-clip generation requested); StoryAgent (no NEW film authoring requested); ScreenplayAgent (no NEW film scene-decomposition needed); IllustrationAgent (not a slideshow / illustrated-storytelling format).

**plan:**
  - `IntakeVideoAgent` — Ingest the uploaded video into the workspace with caption metadata.
  - `StyleTransferAgent` — Run style transfer on the source video to match the requested aesthetic.
  - `MusicAgent` — Compose the BGM the user requested, matching the brief's emotional register.
  - `AudioMixAgent` — Layer the available audio tracks into the final mixed wav.
  - `CompositorAgent` — Mux the final mp4, combining the rendered visual track with audio and any subtitle overlay.

## #22
**user_goal** (155 chars):

> I'd like a kids' audiobook in Attic-Greek about a young Athenian philosopher's daughter at the agora at evening, with Greek-lyre BGM and English subtitles.

**rationale:** Illustrated storytelling slideshow from a text brief + uploaded reference image; overlays applied: BGM + bilingual narration track. Excluded — ScreenplayAgent (no NEW film scene-decomposition needed); StyleTransferAgent (no style transfer requested); TranscriptionAgent (no subtitle requested); HighlightAgent (not a highlight workflow); VideoAgent (no NEW motion-clip generation requested); VideoAnalysisAgent (no source-video analysis required); IntakeVideoAgent (no source clip uploaded); StoryAgent (no NEW film authoring requested); KeyFrameAgent (no keyframe planning required); AmbienceAgent (no environmental layer requested); VideoExtendAgent (no video extension requested).

**plan:**
  - `IntakeImageAgent` — Ingest the uploaded image into the workspace with caption metadata.
  - `BriefEnricherAgent` — Fold image-reference descriptions into the brief to produce an enriched creative brief.
  - `NarrationAgent` — Author the narration script from the brief — paragraph-by-paragraph story text.
  - `IllustrationAgent` — Produce per-paragraph illustrations matching the narration.
  - `NarratorAgent` — Synthesize the narrator audio track from the narration script.
  - `MusicAgent` — Compose the BGM the user requested, matching the brief's emotional register.
  - `AudioMixAgent` — Layer the available audio tracks into the final mixed wav.
  - `TranslationAgent` — Produce the second-language subtitle track from the source transcription.
  - `CompositorAgent` — Mux the final mp4, combining the rendered visual track with audio and any subtitle overlay.

## #23
**user_goal** (100 chars):

> Produce a 30-second short retelling Pandora opening the box at a Mediterranean storage-unit auction.

**rationale:** Cinematic mini-drama from a text brief; no overlays added. Excluded — MusicAgent (no BGM requested); VideoExtendAgent (no video extension requested); IllustrationAgent (not a slideshow / illustrated-storytelling format); NarrationAgent (not a slideshow / illustrated-storytelling format); HighlightAgent (not a highlight workflow); NarratorAgent (not a slideshow / illustrated-storytelling format); IntakeImageAgent (no image upload); TranscriptionAgent (no subtitle requested); VideoAnalysisAgent (no source-video analysis required); StyleTransferAgent (no style transfer requested); AmbienceAgent (no environmental layer requested); BriefEnricherAgent (no image upload to enrich the brief with); TranslationAgent (no translation / second language requested); AudioMixAgent (no audio tracks to mix); IntakeVideoAgent (no source clip uploaded).

**plan:**
  - `StoryAgent` — Draft the story blueprint from the brief — character arc and act structure.
  - `ScreenplayAgent` — Decompose the story into scenes with mood progression aligned to the brief.
  - `KeyFrameAgent` — Design keyframes from the screenplay scene by scene.
  - `VideoAgent` — Animate each keyframe into a per-shot motion clip.
  - `CompositorAgent` — Mux the final mp4, combining the rendered visual track with audio and any subtitle overlay.

## #24
**user_goal** (135 chars):

> Uploading a portrait of a young Achaemenid-Susa royal-road courier — make a 1-minute mini-drama with Old-Persian and Aramaic subtitles.

**rationale:** Cinematic mini-drama produced from a text brief + uploaded reference image, layered with bilingual subtitles. Skipped: AmbienceAgent (no environmental layer requested); AudioMixAgent (no audio tracks to mix); MusicAgent (no BGM requested); NarrationAgent (not a slideshow / illustrated-storytelling format); IllustrationAgent (not a slideshow / illustrated-storytelling format); StyleTransferAgent (no style transfer requested); VideoExtendAgent (no video extension requested); IntakeVideoAgent (no source clip uploaded); VideoAnalysisAgent (no source-video analysis required); NarratorAgent (not a slideshow / illustrated-storytelling format); HighlightAgent (not a highlight workflow).

**plan:**
  - `IntakeImageAgent` — Persist the uploaded image into the workspace as a captioned artifact.
  - `BriefEnricherAgent` — Enrich the brief by integrating descriptions of the uploaded reference images.
  - `StoryAgent` — Author the story blueprint following the brief, with a clear arc and beat structure.
  - `ScreenplayAgent` — Decompose the story into scenes with mood progression aligned to the brief.
  - `KeyFrameAgent` — Design keyframes from the screenplay scene by scene.
  - `VideoAgent` — Produce per-shot video clips from each keyframe, holding aesthetic continuity across cuts.
  - `TranscriptionAgent` — Generate the subtitle track from the dialogue audio with per-line timestamps.
  - `TranslationAgent` — Translate the source-language subtitles into the requested target language.
  - `CompositorAgent` — Composite the final mp4 — assemble video, audio, and any subtitle / transitions into the deliverable.

## #25
**user_goal** (103 chars):

> Cook up a children's audiobook about a turtle resting in tide-pool ripples, with coastal-tide ambience.

**rationale:** Illustrated storytelling slideshow produced from a text brief, layered with ambient layer. Skipped: ScreenplayAgent (no NEW film scene-decomposition needed); IntakeVideoAgent (no source clip uploaded); HighlightAgent (not a highlight workflow); KeyFrameAgent (no keyframe planning required); MusicAgent (no BGM requested); TranslationAgent (no translation / second language requested); VideoExtendAgent (no video extension requested); BriefEnricherAgent (no image upload to enrich the brief with); StoryAgent (no NEW film authoring requested); TranscriptionAgent (no subtitle requested); VideoAgent (no NEW motion-clip generation requested); VideoAnalysisAgent (no source-video analysis required); StyleTransferAgent (no style transfer requested); IntakeImageAgent (no image upload).

**plan:**
  - `NarrationAgent` — Write the narration script broken into reading paragraphs.
  - `IllustrationAgent` — Render one still illustration per narration paragraph.
  - `NarratorAgent` — Synthesize the narrator audio track from the narration script.
  - `AmbienceAgent` — Generate the ambient sound bed the brief asks for.
  - `AudioMixAgent` — Layer the available audio tracks into the final mixed wav.
  - `CompositorAgent` — Mux the final mp4, combining the rendered visual track with audio and any subtitle overlay.

## #26
**user_goal** (111 chars):

> Here's a 4-minute Donegal-tweed-weaver workshop — analyze it, add English captions, and add Donegal-fiddle BGM.

**rationale:** Modified video cut from an uploaded source video; overlays applied: BGM + subtitles. Excluded — AmbienceAgent (no environmental layer requested); IntakeImageAgent (no image upload); StoryAgent (no NEW film authoring requested); VideoAgent (no NEW motion-clip generation requested); ScreenplayAgent (no NEW film scene-decomposition needed); KeyFrameAgent (no keyframe planning required); NarratorAgent (not a slideshow / illustrated-storytelling format); TranslationAgent (no translation / second language requested); VideoExtendAgent (no video extension requested); IllustrationAgent (not a slideshow / illustrated-storytelling format); StyleTransferAgent (no style transfer requested); NarrationAgent (not a slideshow / illustrated-storytelling format); HighlightAgent (not a highlight workflow); BriefEnricherAgent (no image upload to enrich the brief with).

**plan:**
  - `IntakeVideoAgent` — Register the uploaded video as a captioned workspace artifact.
  - `VideoAnalysisAgent` — Produce a scene-level analysis report of the source video for downstream reasoning.
  - `TranscriptionAgent` — Generate the subtitle track from the dialogue audio with per-line timestamps.
  - `MusicAgent` — Compose the BGM the user requested, matching the brief's emotional register.
  - `AudioMixAgent` — Combine the produced audio layers into a single mixed wav.
  - `CompositorAgent` — Mux the final mp4, combining the rendered visual track with audio and any subtitle overlay.

## #27
**user_goal** (124 chars):

> Uploading a 45-second clip of a tropical-island lagoon snorkel — please add a tropical-marimba BGM and lagoon-water ambient.

**rationale:** Modified video cut from an uploaded source video with BGM + ambient layer as the only added overlays. Reject: NarrationAgent (not a slideshow / illustrated-storytelling format); VideoAgent (no NEW motion-clip generation requested); TranslationAgent (no translation / second language requested); IntakeImageAgent (no image upload); StyleTransferAgent (no style transfer requested); ScreenplayAgent (no NEW film scene-decomposition needed); TranscriptionAgent (no subtitle requested); HighlightAgent (not a highlight workflow); IllustrationAgent (not a slideshow / illustrated-storytelling format); VideoExtendAgent (no video extension requested); BriefEnricherAgent (no image upload to enrich the brief with); StoryAgent (no NEW film authoring requested); NarratorAgent (not a slideshow / illustrated-storytelling format); KeyFrameAgent (no keyframe planning required); VideoAnalysisAgent (no source-video analysis required).

**plan:**
  - `IntakeVideoAgent` — Persist the uploaded video into the workspace as a captioned artifact.
  - `MusicAgent` — Write the requested BGM, aligned to the brief's tonal cue.
  - `AmbienceAgent` — Generate the ambient sound bed the brief asks for.
  - `AudioMixAgent` — Mix the available audio tracks into one final mixed wav.
  - `CompositorAgent` — Output the final mp4 by composing the video, audio, and subtitle / transition elements.

## #28
**user_goal** (132 chars):

> Uploading a 30-second Machu-Picchu reel — style as Machu-Picchu-naturalist-plate, extend to 90 seconds, and add an Andean-quena BGM.

**rationale:** Style-transferred + extended video cut from an uploaded source video; overlays applied: BGM. Excluded — BriefEnricherAgent (no image upload to enrich the brief with); NarrationAgent (not a slideshow / illustrated-storytelling format); VideoAnalysisAgent (no source-video analysis required); TranslationAgent (no translation / second language requested); StoryAgent (no NEW film authoring requested); IntakeImageAgent (no image upload); IllustrationAgent (not a slideshow / illustrated-storytelling format); ScreenplayAgent (no NEW film scene-decomposition needed); KeyFrameAgent (no keyframe planning required); VideoAgent (no NEW motion-clip generation requested); AmbienceAgent (no environmental layer requested); HighlightAgent (not a highlight workflow); TranscriptionAgent (no subtitle requested); NarratorAgent (not a slideshow / illustrated-storytelling format).

**plan:**
  - `IntakeVideoAgent` — Persist the uploaded video into the workspace as a captioned artifact.
  - `StyleTransferAgent` — Re-render the source video under the requested visual style.
  - `VideoExtendAgent` — Produce extended footage that continues the source video.
  - `MusicAgent` — Generate the requested BGM, scored to the brief's mood.
  - `AudioMixAgent` — Mix the available audio tracks into one final mixed wav.
  - `CompositorAgent` — Mux the final mp4, combining the rendered visual track with audio and any subtitle overlay.

## #29
**user_goal** (158 chars):

> I have a digital portrait of a young 18th-c. Saint-Domingue-Bois-Caïman vodou-novice — render a 4-minute extended cinematic piece at the Bois-Caïman-clearing.

**rationale:** Extended-runtime cinematic mini-drama from a text brief + uploaded reference image; no overlays added. Excluded — NarrationAgent (not a slideshow / illustrated-storytelling format); AmbienceAgent (no environmental layer requested); StyleTransferAgent (no style transfer requested); MusicAgent (no BGM requested); HighlightAgent (not a highlight workflow); NarratorAgent (not a slideshow / illustrated-storytelling format); TranscriptionAgent (no subtitle requested); IntakeVideoAgent (no source clip uploaded); AudioMixAgent (no audio tracks to mix); VideoAnalysisAgent (no source-video analysis required); TranslationAgent (no translation / second language requested); IllustrationAgent (not a slideshow / illustrated-storytelling format).

**plan:**
  - `IntakeImageAgent` — Register the uploaded image as a captioned workspace artifact.
  - `BriefEnricherAgent` — Enrich the brief by integrating descriptions of the uploaded reference images.
  - `StoryAgent` — Author the story blueprint following the brief, with a clear arc and beat structure.
  - `ScreenplayAgent` — Break the drafted story into scene-by-scene units, preserving the brief's tonal register.
  - `KeyFrameAgent` — Design keyframes from the screenplay scene by scene.
  - `VideoAgent` — Produce per-shot video clips from each keyframe, holding aesthetic continuity across cuts.
  - `VideoExtendAgent` — Extend the source video beyond its original duration.
  - `CompositorAgent` — Mux the final mp4, combining the rendered visual track with audio and any subtitle overlay.

## #30
**user_goal** (121 chars):

> Here's a 2-hour Sonic-Temple-Columbus — cut highlights with Sonic-Temple-Columbus-rock BGM and English/Spanish subtitles.

**rationale:** Highlight reel from an uploaded source video with BGM + bilingual subtitles as the only added overlays. Reject: VideoAgent (no NEW motion-clip generation requested); StyleTransferAgent (no style transfer requested); StoryAgent (no NEW film authoring requested); NarrationAgent (not a slideshow / illustrated-storytelling format); KeyFrameAgent (no keyframe planning required); IllustrationAgent (not a slideshow / illustrated-storytelling format); AmbienceAgent (no environmental layer requested); VideoExtendAgent (no video extension requested); NarratorAgent (not a slideshow / illustrated-storytelling format); BriefEnricherAgent (no image upload to enrich the brief with); ScreenplayAgent (no NEW film scene-decomposition needed); IntakeImageAgent (no image upload).

**plan:**
  - `IntakeVideoAgent` — Persist the uploaded video into the workspace as a captioned artifact.
  - `VideoAnalysisAgent` — Generate a structured scene-level report of the source video.
  - `HighlightAgent` — Extract the highlight moments from the analyzed video.
  - `TranscriptionAgent` — Author the timestamped transcription of the spoken dialogue.
  - `TranslationAgent` — Produce the second-language subtitle track from the source transcription.
  - `MusicAgent` — Write the requested BGM, aligned to the brief's tonal cue.
  - `AudioMixAgent` — Layer the available audio tracks into the final mixed wav.
  - `CompositorAgent` — Composite the final mp4 — assemble video, audio, and any subtitle / transitions into the deliverable.

## #31
**user_goal** (125 chars):

> Uploading a 4-hour Irish-traditional-music session — cut highlights with Irish-fiddle BGM and Irish-Gaelic/English subtitles.

**rationale:** Highlight reel from an uploaded source video with BGM + bilingual subtitles as the only added overlays. Reject: StoryAgent (no NEW film authoring requested); KeyFrameAgent (no keyframe planning required); NarratorAgent (not a slideshow / illustrated-storytelling format); BriefEnricherAgent (no image upload to enrich the brief with); AmbienceAgent (no environmental layer requested); IllustrationAgent (not a slideshow / illustrated-storytelling format); VideoExtendAgent (no video extension requested); ScreenplayAgent (no NEW film scene-decomposition needed); NarrationAgent (not a slideshow / illustrated-storytelling format); IntakeImageAgent (no image upload); VideoAgent (no NEW motion-clip generation requested); StyleTransferAgent (no style transfer requested).

**plan:**
  - `IntakeVideoAgent` — Ingest the uploaded video into the workspace with caption metadata.
  - `VideoAnalysisAgent` — Analyze the source video into a scene-by-scene report (genre, mood, beats, entities).
  - `HighlightAgent` — Select the highlight segments from the analyzed source video.
  - `TranscriptionAgent` — Generate the subtitle track from the dialogue audio with per-line timestamps.
  - `TranslationAgent` — Produce the second-language subtitle track from the source transcription.
  - `MusicAgent` — Write the requested BGM, aligned to the brief's tonal cue.
  - `AudioMixAgent` — Combine the produced audio layers into a single mixed wav.
  - `CompositorAgent` — Output the final mp4 by composing the video, audio, and subtitle / transition elements.

## #32
**user_goal** (88 chars):

> Cook up a children's audiobook in Norwegian about a young troll, with English subtitles.

**rationale:** Illustrated storytelling slideshow from a text brief with bilingual narration track as the only added overlays. Reject: IntakeImageAgent (no image upload); HighlightAgent (not a highlight workflow); VideoAnalysisAgent (no source-video analysis required); TranscriptionAgent (no subtitle requested); BriefEnricherAgent (no image upload to enrich the brief with); KeyFrameAgent (no keyframe planning required); MusicAgent (no BGM requested); AudioMixAgent (no audio tracks to mix); StyleTransferAgent (no style transfer requested); VideoAgent (no NEW motion-clip generation requested); IntakeVideoAgent (no source clip uploaded); VideoExtendAgent (no video extension requested); StoryAgent (no NEW film authoring requested); ScreenplayAgent (no NEW film scene-decomposition needed); AmbienceAgent (no environmental layer requested).

**plan:**
  - `NarrationAgent` — Write the narration script broken into reading paragraphs.
  - `IllustrationAgent` — Produce per-paragraph illustrations matching the narration.
  - `NarratorAgent` — Produce the spoken narrator track via TTS over the narration text.
  - `TranslationAgent` — Render the bilingual translation of the subtitle track.
  - `CompositorAgent` — Mux the final mp4, combining the rendered visual track with audio and any subtitle overlay.

## #33
**user_goal** (235 chars):

> Here's a watercolor of a young 11th-c. Bukhara-Samanid-Library binder — render a kids' audiobook in Persian about her Ismail-Samani-tomb afternoon, with Samanid-rubab-3 BGM, Ismail-Samani-tomb-afternoon ambience, and Sogdian subtitles.

**rationale:** Illustrated storytelling slideshow from a text brief + uploaded reference image with BGM + ambient layer + bilingual narration track as the only added overlays. Reject: VideoExtendAgent (no video extension requested); TranscriptionAgent (no subtitle requested); VideoAnalysisAgent (no source-video analysis required); ScreenplayAgent (no NEW film scene-decomposition needed); IntakeVideoAgent (no source clip uploaded); HighlightAgent (not a highlight workflow); VideoAgent (no NEW motion-clip generation requested); StyleTransferAgent (no style transfer requested); KeyFrameAgent (no keyframe planning required); StoryAgent (no NEW film authoring requested).

**plan:**
  - `IntakeImageAgent` — Persist the uploaded image into the workspace as a captioned artifact.
  - `BriefEnricherAgent` — Fold image-reference descriptions into the brief to produce an enriched creative brief.
  - `NarrationAgent` — Write the narration script broken into reading paragraphs.
  - `IllustrationAgent` — Produce per-paragraph illustrations matching the narration.
  - `NarratorAgent` — Synthesize the narrator audio track from the narration script.
  - `MusicAgent` — Write the requested BGM, aligned to the brief's tonal cue.
  - `AmbienceAgent` — Author the environmental ambient layer per the brief.
  - `AudioMixAgent` — Mix the available audio tracks into one final mixed wav.
  - `TranslationAgent` — Render the bilingual translation of the subtitle track.
  - `CompositorAgent` — Composite the final mp4 — assemble video, audio, and any subtitle / transitions into the deliverable.

## #34
**user_goal** (111 chars):

> Produce a 30-second noir short of a woman climbing a fire-escape ladder in heels under a flickering streetlamp.

**rationale:** Cinematic mini-drama from a text brief with no audio / subtitle overlays. Reject: MusicAgent (no BGM requested); HighlightAgent (not a highlight workflow); VideoAnalysisAgent (no source-video analysis required); StyleTransferAgent (no style transfer requested); AmbienceAgent (no environmental layer requested); NarratorAgent (not a slideshow / illustrated-storytelling format); VideoExtendAgent (no video extension requested); NarrationAgent (not a slideshow / illustrated-storytelling format); IntakeImageAgent (no image upload); BriefEnricherAgent (no image upload to enrich the brief with); IntakeVideoAgent (no source clip uploaded); IllustrationAgent (not a slideshow / illustrated-storytelling format); TranslationAgent (no translation / second language requested); AudioMixAgent (no audio tracks to mix); TranscriptionAgent (no subtitle requested).

**plan:**
  - `StoryAgent` — Outline the story blueprint per the brief — protagonist arc and pivot beats.
  - `ScreenplayAgent` — Decompose the story into scenes with mood progression aligned to the brief.
  - `KeyFrameAgent` — Plan keyframes for the screenplay's settings, one per scene.
  - `VideoAgent` — Produce per-shot video clips from each keyframe, holding aesthetic continuity across cuts.
  - `CompositorAgent` — Mux the final mp4, combining the rendered visual track with audio and any subtitle overlay.

## #35
**user_goal** (108 chars):

> Here's a 45-second Louveciennes-village-road reel — extend to 2 minutes and render as Pissarro-Louveciennes.

**rationale:** Style-transferred + extended video cut from an uploaded source video; no overlays added. Excluded — TranscriptionAgent (no subtitle requested); HighlightAgent (not a highlight workflow); CompositorAgent (no final mux required); NarrationAgent (not a slideshow / illustrated-storytelling format); ScreenplayAgent (no NEW film scene-decomposition needed); IllustrationAgent (not a slideshow / illustrated-storytelling format); NarratorAgent (not a slideshow / illustrated-storytelling format); KeyFrameAgent (no keyframe planning required); VideoAnalysisAgent (no source-video analysis required); BriefEnricherAgent (no image upload to enrich the brief with); StoryAgent (no NEW film authoring requested); TranslationAgent (no translation / second language requested); VideoAgent (no NEW motion-clip generation requested); AudioMixAgent (no audio tracks to mix); IntakeImageAgent (no image upload); MusicAgent (no BGM requested); AmbienceAgent (no environmental layer requested).

**plan:**
  - `IntakeVideoAgent` — Register the uploaded video as a captioned workspace artifact.
  - `VideoExtendAgent` — Generate continuation footage extending the source video.
  - `StyleTransferAgent` — Run style transfer on the source video to match the requested aesthetic.

## #36
**user_goal** (115 chars):

> Generate a kids' picture-book audiobook in Malay about a young pangolin, with Malay-folk BGM and English subtitles.

**rationale:** Illustrated storytelling slideshow from a text brief; overlays applied: BGM + bilingual narration track. Excluded — AmbienceAgent (no environmental layer requested); BriefEnricherAgent (no image upload to enrich the brief with); VideoAnalysisAgent (no source-video analysis required); IntakeVideoAgent (no source clip uploaded); IntakeImageAgent (no image upload); VideoAgent (no NEW motion-clip generation requested); TranscriptionAgent (no subtitle requested); ScreenplayAgent (no NEW film scene-decomposition needed); StoryAgent (no NEW film authoring requested); StyleTransferAgent (no style transfer requested); KeyFrameAgent (no keyframe planning required); HighlightAgent (not a highlight workflow); VideoExtendAgent (no video extension requested).

**plan:**
  - `NarrationAgent` — Draft the narration script per the brief, paragraph-by-paragraph.
  - `IllustrationAgent` — Render one still illustration per narration paragraph.
  - `NarratorAgent` — Synthesize the narrator audio track from the narration script.
  - `MusicAgent` — Compose the BGM the user requested, matching the brief's emotional register.
  - `AudioMixAgent` — Combine the produced audio layers into a single mixed wav.
  - `TranslationAgent` — Render the bilingual translation of the subtitle track.
  - `CompositorAgent` — Composite the final mp4 — assemble video, audio, and any subtitle / transitions into the deliverable.

## #37
**user_goal** (76 chars):

> I have a 3-minute event-photography tutorial — please add English subtitles.

**rationale:** Modified video cut from an uploaded source video; overlays applied: subtitles. Excluded — NarratorAgent (not a slideshow / illustrated-storytelling format); MusicAgent (no BGM requested); IllustrationAgent (not a slideshow / illustrated-storytelling format); TranslationAgent (no translation / second language requested); VideoAnalysisAgent (no source-video analysis required); VideoExtendAgent (no video extension requested); HighlightAgent (not a highlight workflow); NarrationAgent (not a slideshow / illustrated-storytelling format); AmbienceAgent (no environmental layer requested); BriefEnricherAgent (no image upload to enrich the brief with); ScreenplayAgent (no NEW film scene-decomposition needed); IntakeImageAgent (no image upload); AudioMixAgent (no audio tracks to mix); KeyFrameAgent (no keyframe planning required); StyleTransferAgent (no style transfer requested); StoryAgent (no NEW film authoring requested); VideoAgent (no NEW motion-clip generation requested).

**plan:**
  - `IntakeVideoAgent` — Ingest the uploaded video into the workspace with caption metadata.
  - `TranscriptionAgent` — Author the timestamped transcription of the spoken dialogue.
  - `CompositorAgent` — Composite the final mp4 — assemble video, audio, and any subtitle / transitions into the deliverable.

## #38
**user_goal** (155 chars):

> Here's a digital portrait of a young Garifuna drummer girl — render a kids' audiobook in Garifuna about her Caribbean-shore evening with Spanish subtitles.

**rationale:** Illustrated storytelling slideshow from a text brief + uploaded reference image; overlays applied: bilingual narration track. Excluded — KeyFrameAgent (no keyframe planning required); MusicAgent (no BGM requested); VideoExtendAgent (no video extension requested); StoryAgent (no NEW film authoring requested); VideoAgent (no NEW motion-clip generation requested); TranscriptionAgent (no subtitle requested); AmbienceAgent (no environmental layer requested); VideoAnalysisAgent (no source-video analysis required); StyleTransferAgent (no style transfer requested); ScreenplayAgent (no NEW film scene-decomposition needed); IntakeVideoAgent (no source clip uploaded); HighlightAgent (not a highlight workflow); AudioMixAgent (no audio tracks to mix).

**plan:**
  - `IntakeImageAgent` — Ingest the uploaded image into the workspace with caption metadata.
  - `BriefEnricherAgent` — Augment the brief with the uploaded image's descriptive content.
  - `NarrationAgent` — Draft the narration script per the brief, paragraph-by-paragraph.
  - `IllustrationAgent` — Render one still illustration per narration paragraph.
  - `NarratorAgent` — Generate the TTS narrator audio track from the narration script.
  - `TranslationAgent` — Translate the source-language subtitles into the requested target language.
  - `CompositorAgent` — Composite the final mp4 — assemble video, audio, and any subtitle / transitions into the deliverable.

## #39
**user_goal** (137 chars):

> Uploading a sketch of a young automaton-handler — render a kids' audiobook in English about her workshop afternoon with French subtitles.

**rationale:** Illustrated storytelling slideshow from a text brief + uploaded reference image with bilingual narration track as the only added overlays. Reject: StyleTransferAgent (no style transfer requested); HighlightAgent (not a highlight workflow); ScreenplayAgent (no NEW film scene-decomposition needed); VideoAnalysisAgent (no source-video analysis required); VideoExtendAgent (no video extension requested); StoryAgent (no NEW film authoring requested); AudioMixAgent (no audio tracks to mix); AmbienceAgent (no environmental layer requested); IntakeVideoAgent (no source clip uploaded); TranscriptionAgent (no subtitle requested); VideoAgent (no NEW motion-clip generation requested); MusicAgent (no BGM requested); KeyFrameAgent (no keyframe planning required).

**plan:**
  - `IntakeImageAgent` — Persist the uploaded image into the workspace as a captioned artifact.
  - `BriefEnricherAgent` — Enrich the brief by integrating descriptions of the uploaded reference images.
  - `NarrationAgent` — Write the narration script broken into reading paragraphs.
  - `IllustrationAgent` — Render one still illustration per narration paragraph.
  - `NarratorAgent` — Synthesize the narrator audio track from the narration script.
  - `TranslationAgent` — Render the bilingual translation of the subtitle track.
  - `CompositorAgent` — Output the final mp4 by composing the video, audio, and subtitle / transition elements.

## #40
**user_goal** (227 chars):

> Uploading a sketch of a young 12th-c. Marrakesh-Koutoubia-Mosque calligrapher — build an illustrated children's tale in Classical-Arabic about his minaret-rooftop dawn, with Marrakesh-Gnawa-precursor-2 BGM and Berber subtitles.

**rationale:** Illustrated storytelling slideshow from a text brief + uploaded reference image with BGM + bilingual narration track as the only added overlays. Reject: AmbienceAgent (no environmental layer requested); StyleTransferAgent (no style transfer requested); StoryAgent (no NEW film authoring requested); VideoAgent (no NEW motion-clip generation requested); IntakeVideoAgent (no source clip uploaded); VideoExtendAgent (no video extension requested); TranscriptionAgent (no subtitle requested); VideoAnalysisAgent (no source-video analysis required); ScreenplayAgent (no NEW film scene-decomposition needed); KeyFrameAgent (no keyframe planning required); HighlightAgent (not a highlight workflow).

**plan:**
  - `IntakeImageAgent` — Ingest the uploaded image into the workspace with caption metadata.
  - `BriefEnricherAgent` — Augment the brief with the uploaded image's descriptive content.
  - `NarrationAgent` — Write the narration script broken into reading paragraphs.
  - `IllustrationAgent` — Generate one illustration image per paragraph of the narration.
  - `NarratorAgent` — Produce the spoken narrator track via TTS over the narration text.
  - `MusicAgent` — Generate the requested BGM, scored to the brief's mood.
  - `AudioMixAgent` — Mix the available audio tracks into one final mixed wav.
  - `TranslationAgent` — Translate the source-language subtitles into the requested target language.
  - `CompositorAgent` — Output the final mp4 by composing the video, audio, and subtitle / transition elements.

## #41
**user_goal** (133 chars):

> I'd like a 1-minute horror short of a barista finding the same regular customer who drowned last summer ordering a coffee at closing.

**rationale:** Cinematic mini-drama from a text brief; no overlays added. Excluded — IllustrationAgent (not a slideshow / illustrated-storytelling format); TranslationAgent (no translation / second language requested); TranscriptionAgent (no subtitle requested); BriefEnricherAgent (no image upload to enrich the brief with); NarratorAgent (not a slideshow / illustrated-storytelling format); AmbienceAgent (no environmental layer requested); VideoExtendAgent (no video extension requested); MusicAgent (no BGM requested); AudioMixAgent (no audio tracks to mix); StyleTransferAgent (no style transfer requested); IntakeVideoAgent (no source clip uploaded); NarrationAgent (not a slideshow / illustrated-storytelling format); IntakeImageAgent (no image upload); HighlightAgent (not a highlight workflow); VideoAnalysisAgent (no source-video analysis required).

**plan:**
  - `StoryAgent` — Draft the story blueprint from the brief — character arc and act structure.
  - `ScreenplayAgent` — Convert the story into a scene-by-scene screenplay matching the brief's register.
  - `KeyFrameAgent` — Design keyframes from the screenplay scene by scene.
  - `VideoAgent` — Render per-shot motion clips from the keyframes, preserving visual continuity.
  - `CompositorAgent` — Output the final mp4 by composing the video, audio, and subtitle / transition elements.

## #42
**user_goal** (217 chars):

> I'm sending you a watercolor of a young Berber goat-herd girl — build an illustrated children's tale in Berber about her Atlas-mountain dusk, with Berber-bendir BGM, Atlas-mountain-wind ambience, and Arabic subtitles.

**rationale:** Illustrated storytelling slideshow from a text brief + uploaded reference image with BGM + ambient layer + bilingual narration track as the only added overlays. Reject: VideoExtendAgent (no video extension requested); VideoAnalysisAgent (no source-video analysis required); StoryAgent (no NEW film authoring requested); KeyFrameAgent (no keyframe planning required); IntakeVideoAgent (no source clip uploaded); TranscriptionAgent (no subtitle requested); VideoAgent (no NEW motion-clip generation requested); StyleTransferAgent (no style transfer requested); ScreenplayAgent (no NEW film scene-decomposition needed); HighlightAgent (not a highlight workflow).

**plan:**
  - `IntakeImageAgent` — Register the uploaded image as a captioned workspace artifact.
  - `BriefEnricherAgent` — Fold image-reference descriptions into the brief to produce an enriched creative brief.
  - `NarrationAgent` — Draft the narration script per the brief, paragraph-by-paragraph.
  - `IllustrationAgent` — Generate one illustration image per paragraph of the narration.
  - `NarratorAgent` — Generate the TTS narrator audio track from the narration script.
  - `MusicAgent` — Write the requested BGM, aligned to the brief's tonal cue.
  - `AmbienceAgent` — Author the environmental ambient layer per the brief.
  - `AudioMixAgent` — Layer the available audio tracks into the final mixed wav.
  - `TranslationAgent` — Produce the second-language subtitle track from the source transcription.
  - `CompositorAgent` — Composite the final mp4 — assemble video, audio, and any subtitle / transitions into the deliverable.

## #43
**user_goal** (135 chars):

> Uploading a watercolor of a young 17th-c. Algiers-corsair-cabin-boy — build an illustrated children's tale of his Casbah-walls morning.

**rationale:** Illustrated storytelling slideshow from a text brief + uploaded reference image; no overlays added. Excluded — TranscriptionAgent (no subtitle requested); AmbienceAgent (no environmental layer requested); VideoExtendAgent (no video extension requested); StyleTransferAgent (no style transfer requested); ScreenplayAgent (no NEW film scene-decomposition needed); VideoAgent (no NEW motion-clip generation requested); IntakeVideoAgent (no source clip uploaded); TranslationAgent (no translation / second language requested); StoryAgent (no NEW film authoring requested); AudioMixAgent (no audio tracks to mix); HighlightAgent (not a highlight workflow); VideoAnalysisAgent (no source-video analysis required); MusicAgent (no BGM requested); KeyFrameAgent (no keyframe planning required).

**plan:**
  - `IntakeImageAgent` — Persist the uploaded image into the workspace as a captioned artifact.
  - `BriefEnricherAgent` — Enrich the brief by integrating descriptions of the uploaded reference images.
  - `NarrationAgent` — Draft the narration script per the brief, paragraph-by-paragraph.
  - `IllustrationAgent` — Generate one illustration image per paragraph of the narration.
  - `NarratorAgent` — Produce the spoken narrator track via TTS over the narration text.
  - `CompositorAgent` — Output the final mp4 by composing the video, audio, and subtitle / transition elements.

## #44
**user_goal** (111 chars):

> Tell me an audiobook for kids about a young girl scaling the highest bookshelf to retrieve a runaway storybook.

**rationale:** Illustrated storytelling slideshow from a text brief with no audio / subtitle overlays. Reject: TranslationAgent (no translation / second language requested); IntakeVideoAgent (no source clip uploaded); TranscriptionAgent (no subtitle requested); KeyFrameAgent (no keyframe planning required); IntakeImageAgent (no image upload); StoryAgent (no NEW film authoring requested); VideoAgent (no NEW motion-clip generation requested); VideoExtendAgent (no video extension requested); StyleTransferAgent (no style transfer requested); AmbienceAgent (no environmental layer requested); MusicAgent (no BGM requested); VideoAnalysisAgent (no source-video analysis required); HighlightAgent (not a highlight workflow); AudioMixAgent (no audio tracks to mix); BriefEnricherAgent (no image upload to enrich the brief with); ScreenplayAgent (no NEW film scene-decomposition needed).

**plan:**
  - `NarrationAgent` — Write the narration script broken into reading paragraphs.
  - `IllustrationAgent` — Produce per-paragraph illustrations matching the narration.
  - `NarratorAgent` — Generate the TTS narrator audio track from the narration script.
  - `CompositorAgent` — Output the final mp4 by composing the video, audio, and subtitle / transition elements.

## #45
**user_goal** (131 chars):

> Here's a digital painting of a young Mitanni-Wassukanni horse-trainer — produce a children's audiobook of his royal-stable morning.

**rationale:** Illustrated storytelling slideshow from a text brief + uploaded reference image; no overlays added. Excluded — VideoAnalysisAgent (no source-video analysis required); VideoExtendAgent (no video extension requested); KeyFrameAgent (no keyframe planning required); IntakeVideoAgent (no source clip uploaded); StyleTransferAgent (no style transfer requested); HighlightAgent (not a highlight workflow); AudioMixAgent (no audio tracks to mix); ScreenplayAgent (no NEW film scene-decomposition needed); TranslationAgent (no translation / second language requested); StoryAgent (no NEW film authoring requested); VideoAgent (no NEW motion-clip generation requested); MusicAgent (no BGM requested); TranscriptionAgent (no subtitle requested); AmbienceAgent (no environmental layer requested).

**plan:**
  - `IntakeImageAgent` — Register the uploaded image as a captioned workspace artifact.
  - `BriefEnricherAgent` — Enrich the brief by integrating descriptions of the uploaded reference images.
  - `NarrationAgent` — Author the narration script from the brief — paragraph-by-paragraph story text.
  - `IllustrationAgent` — Generate one illustration image per paragraph of the narration.
  - `NarratorAgent` — Generate the TTS narrator audio track from the narration script.
  - `CompositorAgent` — Composite the final mp4 — assemble video, audio, and any subtitle / transitions into the deliverable.

## #46
**user_goal** (138 chars):

> Tell me an illustrated children's audiobook about young Jacques-Cousteau in Saint-André-de-Cubzac, with Saint-André-de-Cubzac-strings BGM.

**rationale:** Illustrated storytelling slideshow produced from a text brief, layered with BGM. Skipped: IntakeImageAgent (no image upload); VideoExtendAgent (no video extension requested); StyleTransferAgent (no style transfer requested); IntakeVideoAgent (no source clip uploaded); VideoAgent (no NEW motion-clip generation requested); TranscriptionAgent (no subtitle requested); KeyFrameAgent (no keyframe planning required); HighlightAgent (not a highlight workflow); TranslationAgent (no translation / second language requested); AmbienceAgent (no environmental layer requested); ScreenplayAgent (no NEW film scene-decomposition needed); BriefEnricherAgent (no image upload to enrich the brief with); VideoAnalysisAgent (no source-video analysis required); StoryAgent (no NEW film authoring requested).

**plan:**
  - `NarrationAgent` — Draft the narration script per the brief, paragraph-by-paragraph.
  - `IllustrationAgent` — Render one still illustration per narration paragraph.
  - `NarratorAgent` — Produce the spoken narrator track via TTS over the narration text.
  - `MusicAgent` — Generate the requested BGM, scored to the brief's mood.
  - `AudioMixAgent` — Mix the available audio tracks into one final mixed wav.
  - `CompositorAgent` — Mux the final mp4, combining the rendered visual track with audio and any subtitle overlay.

## #47
**user_goal** (112 chars):

> Here's a 45-second hourglass-and-book-still-life reel — extend to 2 minutes and render as Pieter-Claesz-vanitas.

**rationale:** Style-transferred + extended video cut produced from an uploaded source video, nothing layered on top. Skipped: TranscriptionAgent (no subtitle requested); AudioMixAgent (no audio tracks to mix); MusicAgent (no BGM requested); HighlightAgent (not a highlight workflow); NarrationAgent (not a slideshow / illustrated-storytelling format); StoryAgent (no NEW film authoring requested); TranslationAgent (no translation / second language requested); BriefEnricherAgent (no image upload to enrich the brief with); IllustrationAgent (not a slideshow / illustrated-storytelling format); NarratorAgent (not a slideshow / illustrated-storytelling format); CompositorAgent (no final mux required); VideoAgent (no NEW motion-clip generation requested); KeyFrameAgent (no keyframe planning required); IntakeImageAgent (no image upload); VideoAnalysisAgent (no source-video analysis required); ScreenplayAgent (no NEW film scene-decomposition needed); AmbienceAgent (no environmental layer requested).

**plan:**
  - `IntakeVideoAgent` — Register the uploaded video as a captioned workspace artifact.
  - `VideoExtendAgent` — Generate continuation footage extending the source video.
  - `StyleTransferAgent` — Re-render the source video under the requested visual style.

## #48
**user_goal** (145 chars):

> Make me a picture-book audiobook about a baby tokay-gecko on a Bali-temple-wall, with Balinese-gamelan BGM and Bali-temple-wall-night-2 ambience.

**rationale:** Illustrated storytelling slideshow from a text brief; overlays applied: BGM + ambient layer. Excluded — StoryAgent (no NEW film authoring requested); VideoAgent (no NEW motion-clip generation requested); ScreenplayAgent (no NEW film scene-decomposition needed); VideoAnalysisAgent (no source-video analysis required); HighlightAgent (not a highlight workflow); TranscriptionAgent (no subtitle requested); TranslationAgent (no translation / second language requested); IntakeVideoAgent (no source clip uploaded); VideoExtendAgent (no video extension requested); IntakeImageAgent (no image upload); BriefEnricherAgent (no image upload to enrich the brief with); KeyFrameAgent (no keyframe planning required); StyleTransferAgent (no style transfer requested).

**plan:**
  - `NarrationAgent` — Draft the narration script per the brief, paragraph-by-paragraph.
  - `IllustrationAgent` — Generate one illustration image per paragraph of the narration.
  - `NarratorAgent` — Synthesize the narrator audio track from the narration script.
  - `MusicAgent` — Write the requested BGM, aligned to the brief's tonal cue.
  - `AmbienceAgent` — Produce the requested ambient atmosphere as an audio bed.
  - `AudioMixAgent` — Layer the available audio tracks into the final mixed wav.
  - `CompositorAgent` — Output the final mp4 by composing the video, audio, and subtitle / transition elements.

## #49
**user_goal** (175 chars):

> Make an adventure mini-drama about an Arctic explorer and her sled dogs racing to reach the pole before her rival, with a stirring expedition-orchestra BGM and Arctic ambient.

**rationale:** Cinematic mini-drama from a text brief with BGM + ambient layer as the only added overlays. Reject: VideoAnalysisAgent (no source-video analysis required); HighlightAgent (not a highlight workflow); TranscriptionAgent (no subtitle requested); NarrationAgent (not a slideshow / illustrated-storytelling format); NarratorAgent (not a slideshow / illustrated-storytelling format); BriefEnricherAgent (no image upload to enrich the brief with); TranslationAgent (no translation / second language requested); IllustrationAgent (not a slideshow / illustrated-storytelling format); StyleTransferAgent (no style transfer requested); IntakeImageAgent (no image upload); VideoExtendAgent (no video extension requested); IntakeVideoAgent (no source clip uploaded).

**plan:**
  - `StoryAgent` — Outline the story blueprint per the brief — protagonist arc and pivot beats.
  - `ScreenplayAgent` — Break the drafted story into scene-by-scene units, preserving the brief's tonal register.
  - `KeyFrameAgent` — Lay out keyframes for the screenplay's settings, scene-by-scene.
  - `VideoAgent` — Animate each keyframe into a per-shot motion clip.
  - `MusicAgent` — Write the requested BGM, aligned to the brief's tonal cue.
  - `AmbienceAgent` — Generate the ambient sound bed the brief asks for.
  - `AudioMixAgent` — Layer the available audio tracks into the final mixed wav.
  - `CompositorAgent` — Output the final mp4 by composing the video, audio, and subtitle / transition elements.

## #50
**user_goal** (133 chars):

> Build a bedtime audiobook about a baby Weddell-seal pup on the McMurdo-Sound-fast-ice, with McMurdo-Sound-fast-ice-haul-out ambience.

**rationale:** Illustrated storytelling slideshow produced from a text brief, layered with ambient layer. Skipped: VideoExtendAgent (no video extension requested); TranslationAgent (no translation / second language requested); VideoAgent (no NEW motion-clip generation requested); MusicAgent (no BGM requested); KeyFrameAgent (no keyframe planning required); VideoAnalysisAgent (no source-video analysis required); TranscriptionAgent (no subtitle requested); IntakeVideoAgent (no source clip uploaded); HighlightAgent (not a highlight workflow); BriefEnricherAgent (no image upload to enrich the brief with); IntakeImageAgent (no image upload); StyleTransferAgent (no style transfer requested); StoryAgent (no NEW film authoring requested); ScreenplayAgent (no NEW film scene-decomposition needed).

**plan:**
  - `NarrationAgent` — Write the narration script broken into reading paragraphs.
  - `IllustrationAgent` — Generate one illustration image per paragraph of the narration.
  - `NarratorAgent` — Generate the TTS narrator audio track from the narration script.
  - `AmbienceAgent` — Produce the requested ambient atmosphere as an audio bed.
  - `AudioMixAgent` — Combine the produced audio layers into a single mixed wav.
  - `CompositorAgent` — Composite the final mp4 — assemble video, audio, and any subtitle / transitions into the deliverable.
