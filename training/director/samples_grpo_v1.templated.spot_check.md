# GRPO (templated) spot check — 30 of 1396 samples

**Track A (templated chain-free).** Variation: 3 rationale skeletons × per-sample shuffled reject list × 3 intent variants per agent (md5-hash picked).
Sister track: samples_grpo_v1.jsonl (with-chain flow narrative).

---

## #1  (highlight_bilingual_sub, grpo_templated, grpo_tmpl_1141)
**user_goal** (119 chars):

> Cut a highlight reel of sharpest exchanges from my German political debate with German-and-English bilingual subtitles.

**rationale:** Highlight reel produced from an uploaded source video, layered with bilingual subtitles. Skipped: BriefEnricherAgent (no image upload to enrich the brief with); StyleTransferAgent (no style transfer requested); AmbienceAgent (no environmental layer requested); IntakeImageAgent (no image upload); StoryAgent (no NEW film authoring requested); ScreenplayAgent (no NEW film scene-decomposition needed); KeyFrameAgent (no keyframe planning required); MusicAgent (no BGM requested); NarrationAgent (not a slideshow / illustrated-storytelling format); VideoExtendAgent (no video extension requested); IllustrationAgent (not a slideshow / illustrated-storytelling format); VideoAgent (no NEW motion-clip generation requested); AudioMixAgent (no audio tracks to mix); NarratorAgent (not a slideshow / illustrated-storytelling format).

**plan:**
  - `IntakeVideoAgent` — Register the uploaded video as a captioned workspace artifact.
  - `VideoAnalysisAgent` — Generate a structured scene-level report of the source video.
  - `HighlightAgent` — Select the highlight segments from the analyzed source video.
  - `TranscriptionAgent` — Generate the subtitle track from the dialogue audio with per-line timestamps.
  - `TranslationAgent` — Translate the source-language subtitles into the requested target language.
  - `CompositorAgent` — Mux the final mp4, combining the rendered visual track with audio and any subtitle overlay.

## #2  (highlight_music_subtitle, grpo_templated, grpo_tmpl_0598)
**user_goal** (130 chars):

> Make a highlight reel of elimination moments from my Cantonese cooking competition with Cantonese subtitles and playful-piano BGM.

**rationale:** Highlight reel produced from an uploaded source video, layered with BGM + subtitles. Skipped: IllustrationAgent (not a slideshow / illustrated-storytelling format); NarratorAgent (not a slideshow / illustrated-storytelling format); StoryAgent (no NEW film authoring requested); VideoExtendAgent (no video extension requested); NarrationAgent (not a slideshow / illustrated-storytelling format); KeyFrameAgent (no keyframe planning required); BriefEnricherAgent (no image upload to enrich the brief with); VideoAgent (no NEW motion-clip generation requested); TranslationAgent (no translation / second language requested); StyleTransferAgent (no style transfer requested); IntakeImageAgent (no image upload); ScreenplayAgent (no NEW film scene-decomposition needed); AmbienceAgent (no environmental layer requested).

**plan:**
  - `IntakeVideoAgent` — Register the uploaded video as a captioned workspace artifact.
  - `VideoAnalysisAgent` — Generate a structured scene-level report of the source video.
  - `HighlightAgent` — Pick the top highlight clips from the source video using the analysis report.
  - `MusicAgent` — Write the requested BGM, aligned to the brief's tonal cue.
  - `TranscriptionAgent` — Transcribe the spoken dialogue into a timestamped subtitle track.
  - `AudioMixAgent` — Layer the available audio tracks into the final mixed wav.
  - `CompositorAgent` — Mux the final mp4, combining the rendered visual track with audio and any subtitle overlay.

## #3  (highlight_only, grpo_templated, grpo_tmpl_0652)
**user_goal** (90 chars):

> Please cut only the final-dish-reveal moments from this 5-hour cooking show season finale.

**rationale:** Highlight reel from an uploaded source video; no overlays added. Excluded — TranslationAgent (no translation / second language requested); IllustrationAgent (not a slideshow / illustrated-storytelling format); KeyFrameAgent (no keyframe planning required); AudioMixAgent (no audio tracks to mix); AmbienceAgent (no environmental layer requested); TranscriptionAgent (no subtitle requested); VideoAgent (no NEW motion-clip generation requested); MusicAgent (no BGM requested); StoryAgent (no NEW film authoring requested); NarratorAgent (not a slideshow / illustrated-storytelling format); VideoExtendAgent (no video extension requested); CompositorAgent (no final mux required); IntakeImageAgent (no image upload); ScreenplayAgent (no NEW film scene-decomposition needed); StyleTransferAgent (no style transfer requested); BriefEnricherAgent (no image upload to enrich the brief with); NarrationAgent (not a slideshow / illustrated-storytelling format).

**plan:**
  - `IntakeVideoAgent` — Register the uploaded video as a captioned workspace artifact.
  - `VideoAnalysisAgent` — Analyze the source video into a scene-by-scene report (genre, mood, beats, entities).
  - `HighlightAgent` — Pick the top highlight clips from the source video using the analysis report.

## #4  (intake_img_cr_bilingual, grpo_templated, grpo_tmpl_0750)
**user_goal** (146 chars):

> Here's a Thai-shaman portrait — make a Thai village-spirit mini-drama where she performs the binding ritual, Thai dialogue with English subtitles.

**rationale:** Cinematic mini-drama from a text brief + uploaded reference image with bilingual subtitles as the only added overlays. Reject: AudioMixAgent (no audio tracks to mix); VideoAnalysisAgent (no source-video analysis required); MusicAgent (no BGM requested); StyleTransferAgent (no style transfer requested); IntakeVideoAgent (no source clip uploaded); AmbienceAgent (no environmental layer requested); VideoExtendAgent (no video extension requested); NarratorAgent (not a slideshow / illustrated-storytelling format); IllustrationAgent (not a slideshow / illustrated-storytelling format); HighlightAgent (not a highlight workflow); NarrationAgent (not a slideshow / illustrated-storytelling format).

**plan:**
  - `IntakeImageAgent` — Register the uploaded image as a captioned workspace artifact.
  - `BriefEnricherAgent` — Enrich the brief by integrating descriptions of the uploaded reference images.
  - `StoryAgent` — Outline the story blueprint per the brief — protagonist arc and pivot beats.
  - `ScreenplayAgent` — Decompose the story into scenes with mood progression aligned to the brief.
  - `KeyFrameAgent` — Design keyframes from the screenplay scene by scene.
  - `VideoAgent` — Produce per-shot video clips from each keyframe, holding aesthetic continuity across cuts.
  - `TranscriptionAgent` — Generate the subtitle track from the dialogue audio with per-line timestamps.
  - `TranslationAgent` — Produce the second-language subtitle track from the source transcription.
  - `CompositorAgent` — Mux the final mp4, combining the rendered visual track with audio and any subtitle overlay.

## #5  (cr_music, grpo_templated, grpo_tmpl_0214)
**user_goal** (188 chars):

> Produce an Andalusian-flamenco mini-drama about a young cantaora challenging the aging rival who once mentored her — at the Festival de Jerez final, with flamenco-castanets-and-guitar BGM.

**rationale:** Cinematic mini-drama from a text brief with BGM as the only added overlays. Reject: IntakeImageAgent (no image upload); TranslationAgent (no translation / second language requested); BriefEnricherAgent (no image upload to enrich the brief with); VideoExtendAgent (no video extension requested); StyleTransferAgent (no style transfer requested); IntakeVideoAgent (no source clip uploaded); AmbienceAgent (no environmental layer requested); TranscriptionAgent (no subtitle requested); NarrationAgent (not a slideshow / illustrated-storytelling format); VideoAnalysisAgent (no source-video analysis required); NarratorAgent (not a slideshow / illustrated-storytelling format); HighlightAgent (not a highlight workflow); IllustrationAgent (not a slideshow / illustrated-storytelling format).

**plan:**
  - `StoryAgent` — Author the story blueprint following the brief, with a clear arc and beat structure.
  - `ScreenplayAgent` — Break the drafted story into scene-by-scene units, preserving the brief's tonal register.
  - `KeyFrameAgent` — Lay out keyframes for the screenplay's settings, scene-by-scene.
  - `VideoAgent` — Animate each keyframe into a per-shot motion clip.
  - `MusicAgent` — Write the requested BGM, aligned to the brief's tonal cue.
  - `AudioMixAgent` — Mix the available audio tracks into one final mixed wav.
  - `CompositorAgent` — Output the final mp4 by composing the video, audio, and subtitle / transition elements.

## #6  (story_bilingual, grpo_templated, grpo_tmpl_1253)
**user_goal** (140 chars):

> Read the Tagalog Maria-Makiling forest-spirit tale aloud with Filipino-watercolor illustrations, narrated in Tagalog with English subtitles.

**rationale:** Illustrated storytelling slideshow produced from a text brief, layered with bilingual narration track. Skipped: AmbienceAgent (no environmental layer requested); HighlightAgent (not a highlight workflow); BriefEnricherAgent (no image upload to enrich the brief with); MusicAgent (no BGM requested); KeyFrameAgent (no keyframe planning required); StyleTransferAgent (no style transfer requested); ScreenplayAgent (no NEW film scene-decomposition needed); AudioMixAgent (no audio tracks to mix); VideoAnalysisAgent (no source-video analysis required); StoryAgent (no NEW film authoring requested); IntakeVideoAgent (no source clip uploaded); TranscriptionAgent (no subtitle requested); IntakeImageAgent (no image upload); VideoExtendAgent (no video extension requested); VideoAgent (no NEW motion-clip generation requested).

**plan:**
  - `NarrationAgent` — Author the narration script from the brief — paragraph-by-paragraph story text.
  - `IllustrationAgent` — Produce per-paragraph illustrations matching the narration.
  - `NarratorAgent` — Generate the TTS narrator audio track from the narration script.
  - `TranslationAgent` — Translate the source-language subtitles into the requested target language.
  - `CompositorAgent` — Mux the final mp4, combining the rendered visual track with audio and any subtitle overlay.

## #7  (extend_style, grpo_templated, grpo_tmpl_1066)
**user_goal** (93 chars):

> Extend my yoga session clip to ~60 seconds and re-render in Japanese-ukiyo-e woodblock style.

**rationale:** Style-transferred + extended video cut produced from an uploaded source video, nothing layered on top. Skipped: AmbienceAgent (no environmental layer requested); StoryAgent (no NEW film authoring requested); IllustrationAgent (not a slideshow / illustrated-storytelling format); MusicAgent (no BGM requested); HighlightAgent (not a highlight workflow); BriefEnricherAgent (no image upload to enrich the brief with); CompositorAgent (no final mux required); IntakeImageAgent (no image upload); TranslationAgent (no translation / second language requested); AudioMixAgent (no audio tracks to mix); ScreenplayAgent (no NEW film scene-decomposition needed); NarratorAgent (not a slideshow / illustrated-storytelling format); TranscriptionAgent (no subtitle requested); NarrationAgent (not a slideshow / illustrated-storytelling format); VideoAgent (no NEW motion-clip generation requested); VideoAnalysisAgent (no source-video analysis required); KeyFrameAgent (no keyframe planning required).

**plan:**
  - `IntakeVideoAgent` — Persist the uploaded video into the workspace as a captioned artifact.
  - `VideoExtendAgent` — Extend the source video beyond its original duration.
  - `StyleTransferAgent` — Re-render the source video under the requested visual style.

## #8  (story_pure, grpo_templated, grpo_tmpl_0114)
**user_goal** (862 chars):

> Here's my story I want to process — whimsical cartoon style: An old wizard named Bertram lived alone in a glass castle on top of a glass mountain. He had built it himself, three hundred years before, when he was young and arrogant and wanted to be seen. People came from far away to admire his castle. They threw stones at it sometimes, just to see the cracks heal themselves. Bertram had grown tired... [+462 chars]

**rationale:** Illustrated storytelling slideshow from a text brief with no audio / subtitle overlays. Reject: TranslationAgent (no translation / second language requested); VideoAnalysisAgent (no source-video analysis required); ScreenplayAgent (no NEW film scene-decomposition needed); HighlightAgent (not a highlight workflow); BriefEnricherAgent (no image upload to enrich the brief with); StoryAgent (no NEW film authoring requested); AmbienceAgent (no environmental layer requested); VideoAgent (no NEW motion-clip generation requested); AudioMixAgent (no audio tracks to mix); IntakeVideoAgent (no source clip uploaded); MusicAgent (no BGM requested); TranscriptionAgent (no subtitle requested); VideoExtendAgent (no video extension requested); IntakeImageAgent (no image upload); StyleTransferAgent (no style transfer requested); KeyFrameAgent (no keyframe planning required).

**plan:**
  - `NarrationAgent` — Author the narration script from the brief — paragraph-by-paragraph story text.
  - `IllustrationAgent` — Render one still illustration per narration paragraph.
  - `NarratorAgent` — Generate the TTS narrator audio track from the narration script.
  - `CompositorAgent` — Composite the final mp4 — assemble video, audio, and any subtitle / transitions into the deliverable.

## #9  (cr_music, grpo_templated, grpo_tmpl_0179)
**user_goal** (173 chars):

> Make a Tudor-court mini-drama about a queen consort outmaneuvering the regent who plans a midnight coup against her sickly king, with lute-and-harpsichord chamber-music BGM.

**rationale:** Cinematic mini-drama produced from a text brief, layered with BGM. Skipped: IntakeImageAgent (no image upload); TranslationAgent (no translation / second language requested); IllustrationAgent (not a slideshow / illustrated-storytelling format); AmbienceAgent (no environmental layer requested); BriefEnricherAgent (no image upload to enrich the brief with); NarrationAgent (not a slideshow / illustrated-storytelling format); VideoExtendAgent (no video extension requested); HighlightAgent (not a highlight workflow); TranscriptionAgent (no subtitle requested); StyleTransferAgent (no style transfer requested); IntakeVideoAgent (no source clip uploaded); VideoAnalysisAgent (no source-video analysis required); NarratorAgent (not a slideshow / illustrated-storytelling format).

**plan:**
  - `StoryAgent` — Outline the story blueprint per the brief — protagonist arc and pivot beats.
  - `ScreenplayAgent` — Convert the story into a scene-by-scene screenplay matching the brief's register.
  - `KeyFrameAgent` — Lay out keyframes for the screenplay's settings, scene-by-scene.
  - `VideoAgent` — Animate each keyframe into a per-shot motion clip.
  - `MusicAgent` — Compose the BGM the user requested, matching the brief's emotional register.
  - `AudioMixAgent` — Layer the available audio tracks into the final mixed wav.
  - `CompositorAgent` — Output the final mp4 by composing the video, audio, and subtitle / transition elements.

## #10  (story_pure, grpo_templated, grpo_tmpl_0118)
**user_goal** (850 chars):

> Here's my story I want to process — Cherokee-textile-pattern style: In the time when the world was new, there was no fire on the earth. The animals were cold. They held a council. The fox tried to bring fire from the sun and burned his tail black. The crow tried and burned all her feathers; she had been white before. The opossum tried and singed off most of her fur. None of the strong, quick anima... [+450 chars]

**rationale:** Illustrated storytelling slideshow from a text brief; no overlays added. Excluded — TranslationAgent (no translation / second language requested); BriefEnricherAgent (no image upload to enrich the brief with); AmbienceAgent (no environmental layer requested); KeyFrameAgent (no keyframe planning required); AudioMixAgent (no audio tracks to mix); VideoAnalysisAgent (no source-video analysis required); VideoExtendAgent (no video extension requested); TranscriptionAgent (no subtitle requested); ScreenplayAgent (no NEW film scene-decomposition needed); StyleTransferAgent (no style transfer requested); HighlightAgent (not a highlight workflow); MusicAgent (no BGM requested); IntakeVideoAgent (no source clip uploaded); StoryAgent (no NEW film authoring requested); VideoAgent (no NEW motion-clip generation requested); IntakeImageAgent (no image upload).

**plan:**
  - `NarrationAgent` — Draft the narration script per the brief, paragraph-by-paragraph.
  - `IllustrationAgent` — Produce per-paragraph illustrations matching the narration.
  - `NarratorAgent` — Produce the spoken narrator track via TTS over the narration text.
  - `CompositorAgent` — Mux the final mp4, combining the rendered visual track with audio and any subtitle overlay.

## #11  (story_ultra, grpo_templated, grpo_tmpl_1391)
**user_goal** (247 chars):

> Here's a photo of our family cat Cocoa — make an illustrated picture-book audiobook starring Cocoa with whimsical cartoon illustrations, playful pizzicato BGM, kitchen-clock-and-distant-tea-kettle ambient, narrated in Greek with English subtitles.

**rationale:** Illustrated storytelling slideshow produced from a text brief + uploaded reference image, layered with BGM + ambient layer + bilingual narration track. Skipped: StoryAgent (no NEW film authoring requested); VideoAgent (no NEW motion-clip generation requested); VideoAnalysisAgent (no source-video analysis required); ScreenplayAgent (no NEW film scene-decomposition needed); IntakeVideoAgent (no source clip uploaded); TranscriptionAgent (no subtitle requested); VideoExtendAgent (no video extension requested); HighlightAgent (not a highlight workflow); StyleTransferAgent (no style transfer requested); KeyFrameAgent (no keyframe planning required).

**plan:**
  - `IntakeImageAgent` — Ingest the uploaded image into the workspace with caption metadata.
  - `BriefEnricherAgent` — Fold image-reference descriptions into the brief to produce an enriched creative brief.
  - `NarrationAgent` — Author the narration script from the brief — paragraph-by-paragraph story text.
  - `IllustrationAgent` — Produce per-paragraph illustrations matching the narration.
  - `NarratorAgent` — Synthesize the narrator audio track from the narration script.
  - `MusicAgent` — Compose the BGM the user requested, matching the brief's emotional register.
  - `AmbienceAgent` — Produce the requested ambient atmosphere as an audio bed.
  - `AudioMixAgent` — Mix the available audio tracks into one final mixed wav.
  - `TranslationAgent` — Produce the second-language subtitle track from the source transcription.
  - `CompositorAgent` — Mux the final mp4, combining the rendered visual track with audio and any subtitle overlay.

## #12  (highlight_only, grpo_templated, grpo_tmpl_0639)
**user_goal** (101 chars):

> Got a 2.5-hour ice hockey final recording. Please pull just the goals and the goalie's biggest saves.

**rationale:** Highlight reel from an uploaded source video with no audio / subtitle overlays. Reject: AudioMixAgent (no audio tracks to mix); VideoExtendAgent (no video extension requested); CompositorAgent (no final mux required); VideoAgent (no NEW motion-clip generation requested); StyleTransferAgent (no style transfer requested); NarratorAgent (not a slideshow / illustrated-storytelling format); TranscriptionAgent (no subtitle requested); AmbienceAgent (no environmental layer requested); IntakeImageAgent (no image upload); MusicAgent (no BGM requested); StoryAgent (no NEW film authoring requested); NarrationAgent (not a slideshow / illustrated-storytelling format); IllustrationAgent (not a slideshow / illustrated-storytelling format); ScreenplayAgent (no NEW film scene-decomposition needed); BriefEnricherAgent (no image upload to enrich the brief with); TranslationAgent (no translation / second language requested); KeyFrameAgent (no keyframe planning required).

**plan:**
  - `IntakeVideoAgent` — Persist the uploaded video into the workspace as a captioned artifact.
  - `VideoAnalysisAgent` — Produce a scene-level analysis report of the source video for downstream reasoning.
  - `HighlightAgent` — Pick the top highlight clips from the source video using the analysis report.

## #13  (intake_img_cr, grpo_templated, grpo_tmpl_0453)
**user_goal** (147 chars):

> Here's a photo of me in Renaissance dress — produce a Renaissance-Florence mini-drama where I'm a young courtier uncovering a midnight-poison plot.

**rationale:** Cinematic mini-drama from a text brief + uploaded reference image; no overlays added. Excluded — IllustrationAgent (not a slideshow / illustrated-storytelling format); TranslationAgent (no translation / second language requested); AmbienceAgent (no environmental layer requested); HighlightAgent (not a highlight workflow); TranscriptionAgent (no subtitle requested); NarratorAgent (not a slideshow / illustrated-storytelling format); VideoAnalysisAgent (no source-video analysis required); StyleTransferAgent (no style transfer requested); AudioMixAgent (no audio tracks to mix); MusicAgent (no BGM requested); VideoExtendAgent (no video extension requested); NarrationAgent (not a slideshow / illustrated-storytelling format); IntakeVideoAgent (no source clip uploaded).

**plan:**
  - `IntakeImageAgent` — Ingest the uploaded image into the workspace with caption metadata.
  - `BriefEnricherAgent` — Augment the brief with the uploaded image's descriptive content.
  - `StoryAgent` — Outline the story blueprint per the brief — protagonist arc and pivot beats.
  - `ScreenplayAgent` — Break the drafted story into scene-by-scene units, preserving the brief's tonal register.
  - `KeyFrameAgent` — Design keyframes from the screenplay scene by scene.
  - `VideoAgent` — Render per-shot motion clips from the keyframes, preserving visual continuity.
  - `CompositorAgent` — Mux the final mp4, combining the rendered visual track with audio and any subtitle overlay.

## #14  (intake_img_cr, grpo_templated, grpo_tmpl_0464)
**user_goal** (172 chars):

> Here's a photo of my sister in Tang-dynasty robes — make a Tang-dynasty mini-drama where she's a young apprentice helping her dying master complete the imperial commission.

**rationale:** Cinematic mini-drama from a text brief + uploaded reference image with no audio / subtitle overlays. Reject: VideoAnalysisAgent (no source-video analysis required); IllustrationAgent (not a slideshow / illustrated-storytelling format); TranslationAgent (no translation / second language requested); AudioMixAgent (no audio tracks to mix); AmbienceAgent (no environmental layer requested); StyleTransferAgent (no style transfer requested); VideoExtendAgent (no video extension requested); IntakeVideoAgent (no source clip uploaded); NarrationAgent (not a slideshow / illustrated-storytelling format); MusicAgent (no BGM requested); HighlightAgent (not a highlight workflow); TranscriptionAgent (no subtitle requested); NarratorAgent (not a slideshow / illustrated-storytelling format).

**plan:**
  - `IntakeImageAgent` — Ingest the uploaded image into the workspace with caption metadata.
  - `BriefEnricherAgent` — Augment the brief with the uploaded image's descriptive content.
  - `StoryAgent` — Outline the story blueprint per the brief — protagonist arc and pivot beats.
  - `ScreenplayAgent` — Break the drafted story into scene-by-scene units, preserving the brief's tonal register.
  - `KeyFrameAgent` — Plan keyframes for the screenplay's settings, one per scene.
  - `VideoAgent` — Render per-shot motion clips from the keyframes, preserving visual continuity.
  - `CompositorAgent` — Output the final mp4 by composing the video, audio, and subtitle / transition elements.

## #15  (extend_music, grpo_templated, grpo_tmpl_0965)
**user_goal** (89 chars):

> Extend my Indian-village festival clip to ~30 seconds and add Indian sitar-and-tabla BGM.

**rationale:** Extended video cut from an uploaded source video with BGM as the only added overlays. Reject: NarrationAgent (not a slideshow / illustrated-storytelling format); StyleTransferAgent (no style transfer requested); VideoAnalysisAgent (no source-video analysis required); VideoAgent (no NEW motion-clip generation requested); TranscriptionAgent (no subtitle requested); KeyFrameAgent (no keyframe planning required); AmbienceAgent (no environmental layer requested); TranslationAgent (no translation / second language requested); HighlightAgent (not a highlight workflow); ScreenplayAgent (no NEW film scene-decomposition needed); IntakeImageAgent (no image upload); IllustrationAgent (not a slideshow / illustrated-storytelling format); NarratorAgent (not a slideshow / illustrated-storytelling format); StoryAgent (no NEW film authoring requested); BriefEnricherAgent (no image upload to enrich the brief with).

**plan:**
  - `IntakeVideoAgent` — Ingest the uploaded video into the workspace with caption metadata.
  - `VideoExtendAgent` — Generate continuation footage extending the source video.
  - `MusicAgent` — Compose the BGM the user requested, matching the brief's emotional register.
  - `AudioMixAgent` — Layer the available audio tracks into the final mixed wav.
  - `CompositorAgent` — Mux the final mp4, combining the rendered visual track with audio and any subtitle overlay.

## #16  (style_only, grpo_templated, grpo_tmpl_0499)
**user_goal** (76 chars):

> Restyle my baby's-first-steps clip in soft-watercolor children's-book style.

**rationale:** Style-transferred video cut from an uploaded source video with no audio / subtitle overlays. Reject: VideoAnalysisAgent (no source-video analysis required); StoryAgent (no NEW film authoring requested); KeyFrameAgent (no keyframe planning required); TranslationAgent (no translation / second language requested); IntakeImageAgent (no image upload); CompositorAgent (no final mux required); NarratorAgent (not a slideshow / illustrated-storytelling format); HighlightAgent (not a highlight workflow); AudioMixAgent (no audio tracks to mix); ScreenplayAgent (no NEW film scene-decomposition needed); BriefEnricherAgent (no image upload to enrich the brief with); MusicAgent (no BGM requested); AmbienceAgent (no environmental layer requested); NarrationAgent (not a slideshow / illustrated-storytelling format); VideoAgent (no NEW motion-clip generation requested); VideoExtendAgent (no video extension requested); TranscriptionAgent (no subtitle requested); IllustrationAgent (not a slideshow / illustrated-storytelling format).

**plan:**
  - `IntakeVideoAgent` — Ingest the uploaded video into the workspace with caption metadata.
  - `StyleTransferAgent` — Apply the requested style transfer to the source video.

## #17  (intake_img_cr, grpo_templated, grpo_tmpl_0475)
**user_goal** (155 chars):

> Here's a photo of my dad as a young intelligence officer — make a Cold-War KGB mini-drama where he's a handler running an asset's defection through Moscow.

**rationale:** Cinematic mini-drama produced from a text brief + uploaded reference image, nothing layered on top. Skipped: VideoExtendAgent (no video extension requested); NarrationAgent (not a slideshow / illustrated-storytelling format); VideoAnalysisAgent (no source-video analysis required); AudioMixAgent (no audio tracks to mix); NarratorAgent (not a slideshow / illustrated-storytelling format); IntakeVideoAgent (no source clip uploaded); HighlightAgent (not a highlight workflow); IllustrationAgent (not a slideshow / illustrated-storytelling format); TranslationAgent (no translation / second language requested); AmbienceAgent (no environmental layer requested); TranscriptionAgent (no subtitle requested); StyleTransferAgent (no style transfer requested); MusicAgent (no BGM requested).

**plan:**
  - `IntakeImageAgent` — Ingest the uploaded image into the workspace with caption metadata.
  - `BriefEnricherAgent` — Enrich the brief by integrating descriptions of the uploaded reference images.
  - `StoryAgent` — Author the story blueprint following the brief, with a clear arc and beat structure.
  - `ScreenplayAgent` — Decompose the story into scenes with mood progression aligned to the brief.
  - `KeyFrameAgent` — Design keyframes from the screenplay scene by scene.
  - `VideoAgent` — Render per-shot motion clips from the keyframes, preserving visual continuity.
  - `CompositorAgent` — Output the final mp4 by composing the video, audio, and subtitle / transition elements.

## #18  (cr_bilingual, grpo_templated, grpo_tmpl_0321)
**user_goal** (172 chars):

> Produce a Bhutanese archery-festival mini-drama about a young girl shooting in the royal festival against the men's-only archers — Dzongkha dialogue with English subtitles.

**rationale:** Cinematic mini-drama produced from a text brief, layered with bilingual subtitles. Skipped: AudioMixAgent (no audio tracks to mix); VideoAnalysisAgent (no source-video analysis required); MusicAgent (no BGM requested); StyleTransferAgent (no style transfer requested); IntakeImageAgent (no image upload); NarratorAgent (not a slideshow / illustrated-storytelling format); HighlightAgent (not a highlight workflow); NarrationAgent (not a slideshow / illustrated-storytelling format); AmbienceAgent (no environmental layer requested); IllustrationAgent (not a slideshow / illustrated-storytelling format); VideoExtendAgent (no video extension requested); IntakeVideoAgent (no source clip uploaded); BriefEnricherAgent (no image upload to enrich the brief with).

**plan:**
  - `StoryAgent` — Draft the story blueprint from the brief — character arc and act structure.
  - `ScreenplayAgent` — Break the drafted story into scene-by-scene units, preserving the brief's tonal register.
  - `KeyFrameAgent` — Design keyframes from the screenplay scene by scene.
  - `VideoAgent` — Render per-shot motion clips from the keyframes, preserving visual continuity.
  - `TranscriptionAgent` — Author the timestamped transcription of the spoken dialogue.
  - `TranslationAgent` — Produce the second-language subtitle track from the source transcription.
  - `CompositorAgent` — Output the final mp4 by composing the video, audio, and subtitle / transition elements.

## #19  (extend_style, grpo_templated, grpo_tmpl_1074)
**user_goal** (98 chars):

> Extend my amusement-park ride clip to ~30 seconds and re-render in Saturday-morning-cartoon style.

**rationale:** Style-transferred + extended video cut from an uploaded source video with no audio / subtitle overlays. Reject: BriefEnricherAgent (no image upload to enrich the brief with); KeyFrameAgent (no keyframe planning required); IntakeImageAgent (no image upload); AudioMixAgent (no audio tracks to mix); ScreenplayAgent (no NEW film scene-decomposition needed); NarratorAgent (not a slideshow / illustrated-storytelling format); IllustrationAgent (not a slideshow / illustrated-storytelling format); VideoAgent (no NEW motion-clip generation requested); StoryAgent (no NEW film authoring requested); NarrationAgent (not a slideshow / illustrated-storytelling format); VideoAnalysisAgent (no source-video analysis required); CompositorAgent (no final mux required); HighlightAgent (not a highlight workflow); AmbienceAgent (no environmental layer requested); MusicAgent (no BGM requested); TranslationAgent (no translation / second language requested); TranscriptionAgent (no subtitle requested).

**plan:**
  - `IntakeVideoAgent` — Persist the uploaded video into the workspace as a captioned artifact.
  - `VideoExtendAgent` — Generate continuation footage extending the source video.
  - `StyleTransferAgent` — Apply the requested style transfer to the source video.

## #20  (cr_ambience, grpo_templated, grpo_tmpl_0230)
**user_goal** (188 chars):

> Make a Cold-War submarine mini-drama about a young XO running silent at depth as a Soviet sub closes — every footfall could give away their position, with sonar-pinging-deep-ocean ambient.

**rationale:** Cinematic mini-drama from a text brief with ambient layer as the only added overlays. Reject: TranscriptionAgent (no subtitle requested); MusicAgent (no BGM requested); BriefEnricherAgent (no image upload to enrich the brief with); TranslationAgent (no translation / second language requested); IntakeVideoAgent (no source clip uploaded); VideoExtendAgent (no video extension requested); NarratorAgent (not a slideshow / illustrated-storytelling format); StyleTransferAgent (no style transfer requested); HighlightAgent (not a highlight workflow); IllustrationAgent (not a slideshow / illustrated-storytelling format); VideoAnalysisAgent (no source-video analysis required); IntakeImageAgent (no image upload); NarrationAgent (not a slideshow / illustrated-storytelling format).

**plan:**
  - `StoryAgent` — Author the story blueprint following the brief, with a clear arc and beat structure.
  - `ScreenplayAgent` — Decompose the story into scenes with mood progression aligned to the brief.
  - `KeyFrameAgent` — Lay out keyframes for the screenplay's settings, scene-by-scene.
  - `VideoAgent` — Render per-shot motion clips from the keyframes, preserving visual continuity.
  - `AmbienceAgent` — Generate the ambient sound bed the brief asks for.
  - `AudioMixAgent` — Layer the available audio tracks into the final mixed wav.
  - `CompositorAgent` — Composite the final mp4 — assemble video, audio, and any subtitle / transitions into the deliverable.

## #21  (story_pure, grpo_templated, grpo_tmpl_0135)
**user_goal** (922 chars):

> Here's my story I want to process — Brazilian-cordel-illustration style: Saci-Pererê is a small one-legged trickster spirit who appears in the back-country of Brazil. He wears a red cap and smokes a pipe. He moves through the world inside a small whirlwind. He braids the manes of horses into impossible knots and hides things and burns dinners. He cannot be beaten by force. The way to catch a Saci ... [+522 chars]

**rationale:** Illustrated storytelling slideshow from a text brief; no overlays added. Excluded — IntakeImageAgent (no image upload); StyleTransferAgent (no style transfer requested); AudioMixAgent (no audio tracks to mix); StoryAgent (no NEW film authoring requested); VideoAgent (no NEW motion-clip generation requested); ScreenplayAgent (no NEW film scene-decomposition needed); HighlightAgent (not a highlight workflow); TranslationAgent (no translation / second language requested); MusicAgent (no BGM requested); IntakeVideoAgent (no source clip uploaded); AmbienceAgent (no environmental layer requested); KeyFrameAgent (no keyframe planning required); TranscriptionAgent (no subtitle requested); VideoAnalysisAgent (no source-video analysis required); VideoExtendAgent (no video extension requested); BriefEnricherAgent (no image upload to enrich the brief with).

**plan:**
  - `NarrationAgent` — Draft the narration script per the brief, paragraph-by-paragraph.
  - `IllustrationAgent` — Generate one illustration image per paragraph of the narration.
  - `NarratorAgent` — Synthesize the narrator audio track from the narration script.
  - `CompositorAgent` — Output the final mp4 by composing the video, audio, and subtitle / transition elements.

## #22  (story_pure, grpo_templated, grpo_tmpl_0155)
**user_goal** (939 chars):

> Here's my story I want to process — classic-storybook style: La Befana was an old woman of Italy who, on a winter evening long ago, was sweeping her cottage when three travelers stopped at her door asking for directions. They were following a star, they said, to bring gifts to a newborn king. They invited her to come with them. La Befana said no, she was too busy with her sweeping. They went on wi... [+539 chars]

**rationale:** Illustrated storytelling slideshow from a text brief; no overlays added. Excluded — BriefEnricherAgent (no image upload to enrich the brief with); AmbienceAgent (no environmental layer requested); MusicAgent (no BGM requested); StyleTransferAgent (no style transfer requested); HighlightAgent (not a highlight workflow); KeyFrameAgent (no keyframe planning required); StoryAgent (no NEW film authoring requested); AudioMixAgent (no audio tracks to mix); IntakeVideoAgent (no source clip uploaded); VideoAgent (no NEW motion-clip generation requested); ScreenplayAgent (no NEW film scene-decomposition needed); VideoExtendAgent (no video extension requested); IntakeImageAgent (no image upload); TranscriptionAgent (no subtitle requested); VideoAnalysisAgent (no source-video analysis required); TranslationAgent (no translation / second language requested).

**plan:**
  - `NarrationAgent` — Write the narration script broken into reading paragraphs.
  - `IllustrationAgent` — Produce per-paragraph illustrations matching the narration.
  - `NarratorAgent` — Produce the spoken narrator track via TTS over the narration text.
  - `CompositorAgent` — Output the final mp4 by composing the video, audio, and subtitle / transition elements.

## #23  (cr_bilingual, grpo_templated, grpo_tmpl_0307)
**user_goal** (157 chars):

> Produce a Hebrew early-kibbutz mini-drama about a young founder defending a disputed field at the community meeting — Hebrew dialogue with English subtitles.

**rationale:** Cinematic mini-drama produced from a text brief, layered with bilingual subtitles. Skipped: AmbienceAgent (no environmental layer requested); AudioMixAgent (no audio tracks to mix); MusicAgent (no BGM requested); BriefEnricherAgent (no image upload to enrich the brief with); VideoExtendAgent (no video extension requested); StyleTransferAgent (no style transfer requested); NarratorAgent (not a slideshow / illustrated-storytelling format); IllustrationAgent (not a slideshow / illustrated-storytelling format); NarrationAgent (not a slideshow / illustrated-storytelling format); IntakeImageAgent (no image upload); IntakeVideoAgent (no source clip uploaded); VideoAnalysisAgent (no source-video analysis required); HighlightAgent (not a highlight workflow).

**plan:**
  - `StoryAgent` — Author the story blueprint following the brief, with a clear arc and beat structure.
  - `ScreenplayAgent` — Convert the story into a scene-by-scene screenplay matching the brief's register.
  - `KeyFrameAgent` — Lay out keyframes for the screenplay's settings, scene-by-scene.
  - `VideoAgent` — Render per-shot motion clips from the keyframes, preserving visual continuity.
  - `TranscriptionAgent` — Generate the subtitle track from the dialogue audio with per-line timestamps.
  - `TranslationAgent` — Render the bilingual translation of the subtitle track.
  - `CompositorAgent` — Output the final mp4 by composing the video, audio, and subtitle / transition elements.

## #24  (cr_music, grpo_templated, grpo_tmpl_0207)
**user_goal** (181 chars):

> Make an Egyptian mini-drama about a young high-priestess presiding over a Pharaoh's burial when she discovers tomb robbers among her own attendants, with Middle-Eastern-strings BGM.

**rationale:** Cinematic mini-drama from a text brief; overlays applied: BGM. Excluded — NarratorAgent (not a slideshow / illustrated-storytelling format); VideoExtendAgent (no video extension requested); TranscriptionAgent (no subtitle requested); TranslationAgent (no translation / second language requested); IntakeImageAgent (no image upload); HighlightAgent (not a highlight workflow); BriefEnricherAgent (no image upload to enrich the brief with); AmbienceAgent (no environmental layer requested); VideoAnalysisAgent (no source-video analysis required); IntakeVideoAgent (no source clip uploaded); StyleTransferAgent (no style transfer requested); NarrationAgent (not a slideshow / illustrated-storytelling format); IllustrationAgent (not a slideshow / illustrated-storytelling format).

**plan:**
  - `StoryAgent` — Draft the story blueprint from the brief — character arc and act structure.
  - `ScreenplayAgent` — Decompose the story into scenes with mood progression aligned to the brief.
  - `KeyFrameAgent` — Plan keyframes for the screenplay's settings, one per scene.
  - `VideoAgent` — Produce per-shot video clips from each keyframe, holding aesthetic continuity across cuts.
  - `MusicAgent` — Compose the BGM the user requested, matching the brief's emotional register.
  - `AudioMixAgent` — Mix the available audio tracks into one final mixed wav.
  - `CompositorAgent` — Mux the final mp4, combining the rendered visual track with audio and any subtitle overlay.

## #25  (highlight_bilingual_sub, grpo_templated, grpo_tmpl_1142)
**user_goal** (119 chars):

> Make a highlight reel of climactic arias from my Italian opera production with Italian-and-English bilingual subtitles.

**rationale:** Highlight reel from an uploaded source video; overlays applied: bilingual subtitles. Excluded — AmbienceAgent (no environmental layer requested); ScreenplayAgent (no NEW film scene-decomposition needed); VideoExtendAgent (no video extension requested); IntakeImageAgent (no image upload); StoryAgent (no NEW film authoring requested); NarrationAgent (not a slideshow / illustrated-storytelling format); IllustrationAgent (not a slideshow / illustrated-storytelling format); KeyFrameAgent (no keyframe planning required); BriefEnricherAgent (no image upload to enrich the brief with); MusicAgent (no BGM requested); NarratorAgent (not a slideshow / illustrated-storytelling format); AudioMixAgent (no audio tracks to mix); VideoAgent (no NEW motion-clip generation requested); StyleTransferAgent (no style transfer requested).

**plan:**
  - `IntakeVideoAgent` — Register the uploaded video as a captioned workspace artifact.
  - `VideoAnalysisAgent` — Produce a scene-level analysis report of the source video for downstream reasoning.
  - `HighlightAgent` — Select the highlight segments from the analyzed source video.
  - `TranscriptionAgent` — Generate the subtitle track from the dialogue audio with per-line timestamps.
  - `TranslationAgent` — Render the bilingual translation of the subtitle track.
  - `CompositorAgent` — Mux the final mp4, combining the rendered visual track with audio and any subtitle overlay.

## #26  (extend_style, grpo_templated, grpo_tmpl_1065)
**user_goal** (88 chars):

> Extend my wedding ceremony clip to ~30 seconds and restyle in vintage-1950s Technicolor.

**rationale:** Style-transferred + extended video cut produced from an uploaded source video, nothing layered on top. Skipped: TranslationAgent (no translation / second language requested); AmbienceAgent (no environmental layer requested); ScreenplayAgent (no NEW film scene-decomposition needed); NarrationAgent (not a slideshow / illustrated-storytelling format); VideoAnalysisAgent (no source-video analysis required); AudioMixAgent (no audio tracks to mix); NarratorAgent (not a slideshow / illustrated-storytelling format); StoryAgent (no NEW film authoring requested); KeyFrameAgent (no keyframe planning required); IntakeImageAgent (no image upload); HighlightAgent (not a highlight workflow); IllustrationAgent (not a slideshow / illustrated-storytelling format); CompositorAgent (no final mux required); VideoAgent (no NEW motion-clip generation requested); TranscriptionAgent (no subtitle requested); BriefEnricherAgent (no image upload to enrich the brief with); MusicAgent (no BGM requested).

**plan:**
  - `IntakeVideoAgent` — Persist the uploaded video into the workspace as a captioned artifact.
  - `VideoExtendAgent` — Extend the source video beyond its original duration.
  - `StyleTransferAgent` — Run style transfer on the source video to match the requested aesthetic.

## #27  (style_only, grpo_templated, grpo_tmpl_0533)
**user_goal** (58 chars):

> Re-render my street-art tour clip in Banksy stencil-style.

**rationale:** Style-transferred video cut from an uploaded source video; no overlays added. Excluded — CompositorAgent (no final mux required); VideoAgent (no NEW motion-clip generation requested); IllustrationAgent (not a slideshow / illustrated-storytelling format); IntakeImageAgent (no image upload); BriefEnricherAgent (no image upload to enrich the brief with); TranslationAgent (no translation / second language requested); NarrationAgent (not a slideshow / illustrated-storytelling format); AmbienceAgent (no environmental layer requested); StoryAgent (no NEW film authoring requested); HighlightAgent (not a highlight workflow); TranscriptionAgent (no subtitle requested); AudioMixAgent (no audio tracks to mix); ScreenplayAgent (no NEW film scene-decomposition needed); MusicAgent (no BGM requested); NarratorAgent (not a slideshow / illustrated-storytelling format); VideoExtendAgent (no video extension requested); KeyFrameAgent (no keyframe planning required); VideoAnalysisAgent (no source-video analysis required).

**plan:**
  - `IntakeVideoAgent` — Ingest the uploaded video into the workspace with caption metadata.
  - `StyleTransferAgent` — Re-render the source video under the requested visual style.

## #28  (style_music, grpo_templated, grpo_tmpl_0898)
**user_goal** (86 chars):

> Apply Renaissance-fresco style to my museum tour clip with gentle classical-piano BGM.

**rationale:** Style-transferred video cut from an uploaded source video; overlays applied: BGM. Excluded — VideoAgent (no NEW motion-clip generation requested); IllustrationAgent (not a slideshow / illustrated-storytelling format); StoryAgent (no NEW film authoring requested); TranslationAgent (no translation / second language requested); HighlightAgent (not a highlight workflow); NarrationAgent (not a slideshow / illustrated-storytelling format); ScreenplayAgent (no NEW film scene-decomposition needed); NarratorAgent (not a slideshow / illustrated-storytelling format); IntakeImageAgent (no image upload); BriefEnricherAgent (no image upload to enrich the brief with); TranscriptionAgent (no subtitle requested); VideoAnalysisAgent (no source-video analysis required); KeyFrameAgent (no keyframe planning required); AmbienceAgent (no environmental layer requested); VideoExtendAgent (no video extension requested).

**plan:**
  - `IntakeVideoAgent` — Ingest the uploaded video into the workspace with caption metadata.
  - `StyleTransferAgent` — Run style transfer on the source video to match the requested aesthetic.
  - `MusicAgent` — Generate the requested BGM, scored to the brief's mood.
  - `AudioMixAgent` — Mix the available audio tracks into one final mixed wav.
  - `CompositorAgent` — Output the final mp4 by composing the video, audio, and subtitle / transition elements.

## #29  (vid_bilingual_sub, grpo_templated, grpo_tmpl_0678)
**user_goal** (72 chars):

> Add Arabic-and-English bilingual subtitles to my Arabic news commentary.

**rationale:** Modified video cut produced from an uploaded source video, layered with bilingual subtitles. Skipped: ScreenplayAgent (no NEW film scene-decomposition needed); NarrationAgent (not a slideshow / illustrated-storytelling format); VideoAgent (no NEW motion-clip generation requested); HighlightAgent (not a highlight workflow); VideoExtendAgent (no video extension requested); AmbienceAgent (no environmental layer requested); BriefEnricherAgent (no image upload to enrich the brief with); VideoAnalysisAgent (no source-video analysis required); StyleTransferAgent (no style transfer requested); IllustrationAgent (not a slideshow / illustrated-storytelling format); MusicAgent (no BGM requested); KeyFrameAgent (no keyframe planning required); StoryAgent (no NEW film authoring requested); AudioMixAgent (no audio tracks to mix); NarratorAgent (not a slideshow / illustrated-storytelling format); IntakeImageAgent (no image upload).

**plan:**
  - `IntakeVideoAgent` — Persist the uploaded video into the workspace as a captioned artifact.
  - `TranscriptionAgent` — Generate the subtitle track from the dialogue audio with per-line timestamps.
  - `TranslationAgent` — Render the bilingual translation of the subtitle track.
  - `CompositorAgent` — Mux the final mp4, combining the rendered visual track with audio and any subtitle overlay.

## #30  (story_ambience, grpo_templated, grpo_tmpl_1181)
**user_goal** (184 chars):

> Make an illustrated audiobook about an Amazon jaguar cub learning to hunt with her mother, with tropical watercolor illustrations and a tropical-rainforest-bird-and-insect ambient bed.

**rationale:** Illustrated storytelling slideshow from a text brief with ambient layer as the only added overlays. Reject: VideoAnalysisAgent (no source-video analysis required); StyleTransferAgent (no style transfer requested); VideoExtendAgent (no video extension requested); IntakeImageAgent (no image upload); BriefEnricherAgent (no image upload to enrich the brief with); ScreenplayAgent (no NEW film scene-decomposition needed); StoryAgent (no NEW film authoring requested); VideoAgent (no NEW motion-clip generation requested); IntakeVideoAgent (no source clip uploaded); HighlightAgent (not a highlight workflow); KeyFrameAgent (no keyframe planning required); TranslationAgent (no translation / second language requested); MusicAgent (no BGM requested); TranscriptionAgent (no subtitle requested).

**plan:**
  - `NarrationAgent` — Write the narration script broken into reading paragraphs.
  - `IllustrationAgent` — Produce per-paragraph illustrations matching the narration.
  - `NarratorAgent` — Generate the TTS narrator audio track from the narration script.
  - `AmbienceAgent` — Author the environmental ambient layer per the brief.
  - `AudioMixAgent` — Layer the available audio tracks into the final mixed wav.
  - `CompositorAgent` — Mux the final mp4, combining the rendered visual track with audio and any subtitle overlay.
