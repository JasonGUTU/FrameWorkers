# Templated SFT spot check — 50 of 1417 samples

Variation comes from: 3 rationale skeletons × per-sample shuffled reject list × 3 intent variants per agent (md5-hash picked).

---

## #1
**user_goal** (1269 chars):

> Here's my story I want to process: A very old oak tree named Ember had stood at the corner of a schoolyard for two hundred and thirty years. She had watched generations of children climb her branches, eat their lunches in her shade, carve their initials into her bark. She had seen two world wars, a dozen coronations, and more snowfalls than she could count. Ember was tired. She could feel her root... [+869 chars]

**rationale:** Illustrated storytelling slideshow from a text brief with no audio / subtitle overlays. Reject: VideoAnalysisAgent (no source-video analysis required); IntakeImageAgent (no image upload); StoryAgent (no NEW film authoring requested); MusicAgent (no BGM requested); AmbienceAgent (no environmental layer requested); VideoExtendAgent (no video extension requested); KeyFrameAgent (no keyframe planning required); TranscriptionAgent (no subtitle requested); ScreenplayAgent (no NEW film scene-decomposition needed); AudioMixAgent (no audio tracks to mix); BriefEnricherAgent (no image upload to enrich the brief with); StyleTransferAgent (no style transfer requested); HighlightAgent (not a highlight workflow); IntakeVideoAgent (no source clip uploaded); TranslationAgent (no translation / second language requested); VideoAgent (no NEW motion-clip generation requested).

**plan:**
  - `NarrationAgent` — Draft the narration script per the brief, paragraph-by-paragraph.
  - `IllustrationAgent` — Render one still illustration per narration paragraph.
  - `NarratorAgent` — Generate the TTS narrator audio track from the narration script.
  - `CompositorAgent` — Composite the final mp4 — assemble video, audio, and any subtitle / transitions into the deliverable.

## #2
**user_goal** (122 chars):

> Please apply a 1970s disco-funk look to this 5-second rollerskating clip, extend to 15 seconds, and add a funky disco BGM.

**rationale:** Style-transferred + extended video cut from an uploaded source video with BGM as the only added overlays. Reject: StoryAgent (no NEW film authoring requested); IntakeImageAgent (no image upload); IllustrationAgent (not a slideshow / illustrated-storytelling format); ScreenplayAgent (no NEW film scene-decomposition needed); TranslationAgent (no translation / second language requested); VideoAnalysisAgent (no source-video analysis required); VideoAgent (no NEW motion-clip generation requested); KeyFrameAgent (no keyframe planning required); TranscriptionAgent (no subtitle requested); NarrationAgent (not a slideshow / illustrated-storytelling format); BriefEnricherAgent (no image upload to enrich the brief with); HighlightAgent (not a highlight workflow); NarratorAgent (not a slideshow / illustrated-storytelling format); AmbienceAgent (no environmental layer requested).

**plan:**
  - `IntakeVideoAgent` — Ingest the uploaded video into the workspace with caption metadata.
  - `StyleTransferAgent` — Apply the requested style transfer to the source video.
  - `VideoExtendAgent` — Produce extended footage that continues the source video.
  - `MusicAgent` — Write the requested BGM, aligned to the brief's tonal cue.
  - `AudioMixAgent` — Combine the produced audio layers into a single mixed wav.
  - `CompositorAgent` — Output the final mp4 by composing the video, audio, and subtitle / transition elements.

## #3
**user_goal** (122 chars):

> Make an illustrated audiobook of this mountain-goat fable about climbing above the clouds, with mountain-wind ambient bed.

**rationale:** Illustrated storytelling slideshow from a text brief; overlays applied: ambient layer. Excluded — IntakeImageAgent (no image upload); BriefEnricherAgent (no image upload to enrich the brief with); TranscriptionAgent (no subtitle requested); KeyFrameAgent (no keyframe planning required); ScreenplayAgent (no NEW film scene-decomposition needed); StoryAgent (no NEW film authoring requested); VideoAgent (no NEW motion-clip generation requested); HighlightAgent (not a highlight workflow); StyleTransferAgent (no style transfer requested); VideoExtendAgent (no video extension requested); TranslationAgent (no translation / second language requested); VideoAnalysisAgent (no source-video analysis required); IntakeVideoAgent (no source clip uploaded); MusicAgent (no BGM requested).

**plan:**
  - `NarrationAgent` — Write the narration script broken into reading paragraphs.
  - `IllustrationAgent` — Generate one illustration image per paragraph of the narration.
  - `NarratorAgent` — Produce the spoken narrator track via TTS over the narration text.
  - `AmbienceAgent` — Generate the ambient sound bed the brief asks for.
  - `AudioMixAgent` — Combine the produced audio layers into a single mixed wav.
  - `CompositorAgent` — Output the final mp4 by composing the video, audio, and subtitle / transition elements.

## #4
**user_goal** (285 chars):

> Using this uploaded portrait of a little stargazer, make a bilingual English-Arabic illustrated audiobook of the folk tale where the stargazer maps new constellations for lost sailors, with a dreamy ambient-harp and night-sky ambient (gentle wind, distant crickets) under the narrator.

**rationale:** Illustrated storytelling slideshow from a text brief + uploaded reference image; overlays applied: BGM + ambient layer + bilingual narration track. Excluded — StoryAgent (no NEW film authoring requested); TranscriptionAgent (no subtitle requested); VideoExtendAgent (no video extension requested); VideoAnalysisAgent (no source-video analysis required); KeyFrameAgent (no keyframe planning required); IntakeVideoAgent (no source clip uploaded); VideoAgent (no NEW motion-clip generation requested); HighlightAgent (not a highlight workflow); StyleTransferAgent (no style transfer requested); ScreenplayAgent (no NEW film scene-decomposition needed).

**plan:**
  - `IntakeImageAgent` — Register the uploaded image as a captioned workspace artifact.
  - `BriefEnricherAgent` — Fold image-reference descriptions into the brief to produce an enriched creative brief.
  - `NarrationAgent` — Write the narration script broken into reading paragraphs.
  - `IllustrationAgent` — Render one still illustration per narration paragraph.
  - `NarratorAgent` — Synthesize the narrator audio track from the narration script.
  - `MusicAgent` — Write the requested BGM, aligned to the brief's tonal cue.
  - `AmbienceAgent` — Generate the ambient sound bed the brief asks for.
  - `AudioMixAgent` — Combine the produced audio layers into a single mixed wav.
  - `TranslationAgent` — Render the bilingual translation of the subtitle track.
  - `CompositorAgent` — Mux the final mp4, combining the rendered visual track with audio and any subtitle overlay.

## #5
**user_goal** (94 chars):

> Using this uploaded image of a space-station interior, make a sci-fi first-contact mini-drama.

**rationale:** Cinematic mini-drama from a text brief + uploaded reference image; no overlays added. Excluded — VideoExtendAgent (no video extension requested); HighlightAgent (not a highlight workflow); TranslationAgent (no translation / second language requested); NarratorAgent (not a slideshow / illustrated-storytelling format); NarrationAgent (not a slideshow / illustrated-storytelling format); TranscriptionAgent (no subtitle requested); IllustrationAgent (not a slideshow / illustrated-storytelling format); MusicAgent (no BGM requested); IntakeVideoAgent (no source clip uploaded); StyleTransferAgent (no style transfer requested); VideoAnalysisAgent (no source-video analysis required); AudioMixAgent (no audio tracks to mix); AmbienceAgent (no environmental layer requested).

**plan:**
  - `IntakeImageAgent` — Ingest the uploaded image into the workspace with caption metadata.
  - `BriefEnricherAgent` — Fold image-reference descriptions into the brief to produce an enriched creative brief.
  - `StoryAgent` — Author the story blueprint following the brief, with a clear arc and beat structure.
  - `ScreenplayAgent` — Decompose the story into scenes with mood progression aligned to the brief.
  - `KeyFrameAgent` — Lay out keyframes for the screenplay's settings, scene-by-scene.
  - `VideoAgent` — Animate each keyframe into a per-shot motion clip.
  - `CompositorAgent` — Mux the final mp4, combining the rendered visual track with audio and any subtitle overlay.

## #6
**user_goal** (122 chars):

> Take this short 6-second shot of a bird in flight, extend to 20 seconds, and restyle as a Japanese woodblock nature print.

**rationale:** Style-transferred + extended video cut produced from an uploaded source video, nothing layered on top. Skipped: NarrationAgent (not a slideshow / illustrated-storytelling format); IllustrationAgent (not a slideshow / illustrated-storytelling format); VideoAgent (no NEW motion-clip generation requested); ScreenplayAgent (no NEW film scene-decomposition needed); BriefEnricherAgent (no image upload to enrich the brief with); CompositorAgent (no final mux required); IntakeImageAgent (no image upload); KeyFrameAgent (no keyframe planning required); NarratorAgent (not a slideshow / illustrated-storytelling format); StoryAgent (no NEW film authoring requested); TranscriptionAgent (no subtitle requested); AudioMixAgent (no audio tracks to mix); AmbienceAgent (no environmental layer requested); TranslationAgent (no translation / second language requested); HighlightAgent (not a highlight workflow); VideoAnalysisAgent (no source-video analysis required); MusicAgent (no BGM requested).

**plan:**
  - `IntakeVideoAgent` — Ingest the uploaded video into the workspace with caption metadata.
  - `VideoExtendAgent` — Generate continuation footage extending the source video.
  - `StyleTransferAgent` — Run style transfer on the source video to match the requested aesthetic.

## #7
**user_goal** (1061 chars):

> Here's my story I want to process: On an island where the forest grew so thick that the sun barely reached the forest floor, there lived a shy cat-sized creature called a Wim. Wims were nocturnal. They were quiet. They were very hard to see. One particular Wim, named Parsimony, had been noticed by a visiting naturalist, who had published a book about her and made her, briefly, the most famous Wim ... [+661 chars]

**rationale:** Illustrated storytelling slideshow from a text brief; no overlays added. Excluded — KeyFrameAgent (no keyframe planning required); AudioMixAgent (no audio tracks to mix); VideoExtendAgent (no video extension requested); VideoAnalysisAgent (no source-video analysis required); VideoAgent (no NEW motion-clip generation requested); TranslationAgent (no translation / second language requested); TranscriptionAgent (no subtitle requested); IntakeImageAgent (no image upload); StyleTransferAgent (no style transfer requested); AmbienceAgent (no environmental layer requested); ScreenplayAgent (no NEW film scene-decomposition needed); BriefEnricherAgent (no image upload to enrich the brief with); StoryAgent (no NEW film authoring requested); HighlightAgent (not a highlight workflow); IntakeVideoAgent (no source clip uploaded); MusicAgent (no BGM requested).

**plan:**
  - `NarrationAgent` — Write the narration script broken into reading paragraphs.
  - `IllustrationAgent` — Generate one illustration image per paragraph of the narration.
  - `NarratorAgent` — Produce the spoken narrator track via TTS over the narration text.
  - `CompositorAgent` — Composite the final mp4 — assemble video, audio, and any subtitle / transitions into the deliverable.

## #8
**user_goal** (124 chars):

> Make a mini-drama about a woman walking the old Camino pilgrimage alone after her mother's death, with Camino-trail ambient.

**rationale:** Cinematic mini-drama from a text brief; overlays applied: ambient layer. Excluded — BriefEnricherAgent (no image upload to enrich the brief with); IntakeImageAgent (no image upload); IllustrationAgent (not a slideshow / illustrated-storytelling format); StyleTransferAgent (no style transfer requested); TranscriptionAgent (no subtitle requested); TranslationAgent (no translation / second language requested); VideoAnalysisAgent (no source-video analysis required); NarrationAgent (not a slideshow / illustrated-storytelling format); VideoExtendAgent (no video extension requested); NarratorAgent (not a slideshow / illustrated-storytelling format); MusicAgent (no BGM requested); IntakeVideoAgent (no source clip uploaded); HighlightAgent (not a highlight workflow).

**plan:**
  - `StoryAgent` — Draft the story blueprint from the brief — character arc and act structure.
  - `ScreenplayAgent` — Decompose the story into scenes with mood progression aligned to the brief.
  - `KeyFrameAgent` — Design keyframes from the screenplay scene by scene.
  - `VideoAgent` — Animate each keyframe into a per-shot motion clip.
  - `AmbienceAgent` — Generate the ambient sound bed the brief asks for.
  - `AudioMixAgent` — Combine the produced audio layers into a single mixed wav.
  - `CompositorAgent` — Composite the final mp4 — assemble video, audio, and any subtitle / transitions into the deliverable.

## #9
**user_goal** (123 chars):

> Please apply a retro pixel-art arcade style to this 4-second basketball-dunk, extend to 12 seconds, and add a chiptune BGM.

**rationale:** Style-transferred + extended video cut from an uploaded source video; overlays applied: BGM. Excluded — NarrationAgent (not a slideshow / illustrated-storytelling format); ScreenplayAgent (no NEW film scene-decomposition needed); NarratorAgent (not a slideshow / illustrated-storytelling format); TranscriptionAgent (no subtitle requested); AmbienceAgent (no environmental layer requested); HighlightAgent (not a highlight workflow); VideoAgent (no NEW motion-clip generation requested); IllustrationAgent (not a slideshow / illustrated-storytelling format); VideoAnalysisAgent (no source-video analysis required); BriefEnricherAgent (no image upload to enrich the brief with); TranslationAgent (no translation / second language requested); KeyFrameAgent (no keyframe planning required); StoryAgent (no NEW film authoring requested); IntakeImageAgent (no image upload).

**plan:**
  - `IntakeVideoAgent` — Ingest the uploaded video into the workspace with caption metadata.
  - `StyleTransferAgent` — Apply the requested style transfer to the source video.
  - `VideoExtendAgent` — Extend the source video beyond its original duration.
  - `MusicAgent` — Compose the BGM the user requested, matching the brief's emotional register.
  - `AudioMixAgent` — Layer the available audio tracks into the final mixed wav.
  - `CompositorAgent` — Composite the final mp4 — assemble video, audio, and any subtitle / transitions into the deliverable.

## #10
**user_goal** (113 chars):

> Please extract the best moments from this 3-hour Hindi cricket match and add Hindi + English bilingual subtitles.

**rationale:** Highlight reel from an uploaded source video with bilingual subtitles as the only added overlays. Reject: ScreenplayAgent (no NEW film scene-decomposition needed); NarrationAgent (not a slideshow / illustrated-storytelling format); IllustrationAgent (not a slideshow / illustrated-storytelling format); VideoExtendAgent (no video extension requested); StoryAgent (no NEW film authoring requested); KeyFrameAgent (no keyframe planning required); AudioMixAgent (no audio tracks to mix); NarratorAgent (not a slideshow / illustrated-storytelling format); IntakeImageAgent (no image upload); MusicAgent (no BGM requested); AmbienceAgent (no environmental layer requested); BriefEnricherAgent (no image upload to enrich the brief with); VideoAgent (no NEW motion-clip generation requested); StyleTransferAgent (no style transfer requested).

**plan:**
  - `IntakeVideoAgent` — Ingest the uploaded video into the workspace with caption metadata.
  - `VideoAnalysisAgent` — Analyze the source video into a scene-by-scene report (genre, mood, beats, entities).
  - `HighlightAgent` — Extract the highlight moments from the analyzed video.
  - `TranscriptionAgent` — Transcribe the spoken dialogue into a timestamped subtitle track.
  - `TranslationAgent` — Produce the second-language subtitle track from the source transcription.
  - `CompositorAgent` — Mux the final mp4, combining the rendered visual track with audio and any subtitle overlay.

## #11
**user_goal** (1271 chars):

> Here's my story I want to process: In a coastal town where the houses leaned toward each other like friends sharing a secret, there lived a young mail-carrier named Rivka. Rivka was twenty-four years old, new to the job, and she took her route very seriously. She delivered every letter directly into the proper hand whenever she could — she did not believe in slot-delivery when the recipient was ho... [+871 chars]

**rationale:** Illustrated storytelling slideshow produced from a text brief, nothing layered on top. Skipped: StyleTransferAgent (no style transfer requested); VideoAgent (no NEW motion-clip generation requested); TranslationAgent (no translation / second language requested); TranscriptionAgent (no subtitle requested); ScreenplayAgent (no NEW film scene-decomposition needed); AudioMixAgent (no audio tracks to mix); BriefEnricherAgent (no image upload to enrich the brief with); IntakeVideoAgent (no source clip uploaded); VideoExtendAgent (no video extension requested); KeyFrameAgent (no keyframe planning required); MusicAgent (no BGM requested); AmbienceAgent (no environmental layer requested); HighlightAgent (not a highlight workflow); StoryAgent (no NEW film authoring requested); VideoAnalysisAgent (no source-video analysis required); IntakeImageAgent (no image upload).

**plan:**
  - `NarrationAgent` — Write the narration script broken into reading paragraphs.
  - `IllustrationAgent` — Generate one illustration image per paragraph of the narration.
  - `NarratorAgent` — Generate the TTS narrator audio track from the narration script.
  - `CompositorAgent` — Composite the final mp4 — assemble video, audio, and any subtitle / transitions into the deliverable.

## #12
**user_goal** (124 chars):

> Extend this 4-second Turkish bazaar-walkthrough to 12 seconds, restyle as Matisse cutout-collage, and add Turkish subtitles.

**rationale:** Style-transferred + extended video cut from an uploaded source video with subtitles as the only added overlays. Reject: IntakeImageAgent (no image upload); NarrationAgent (not a slideshow / illustrated-storytelling format); StoryAgent (no NEW film authoring requested); MusicAgent (no BGM requested); ScreenplayAgent (no NEW film scene-decomposition needed); IllustrationAgent (not a slideshow / illustrated-storytelling format); KeyFrameAgent (no keyframe planning required); HighlightAgent (not a highlight workflow); TranslationAgent (no translation / second language requested); NarratorAgent (not a slideshow / illustrated-storytelling format); AudioMixAgent (no audio tracks to mix); BriefEnricherAgent (no image upload to enrich the brief with); AmbienceAgent (no environmental layer requested); VideoAgent (no NEW motion-clip generation requested); VideoAnalysisAgent (no source-video analysis required).

**plan:**
  - `IntakeVideoAgent` — Persist the uploaded video into the workspace as a captioned artifact.
  - `VideoExtendAgent` — Generate continuation footage extending the source video.
  - `StyleTransferAgent` — Run style transfer on the source video to match the requested aesthetic.
  - `TranscriptionAgent` — Generate the subtitle track from the dialogue audio with per-line timestamps.
  - `CompositorAgent` — Composite the final mp4 — assemble video, audio, and any subtitle / transitions into the deliverable.

## #13
**user_goal** (1237 chars):

> Here's my story I want to process: A lonely paper crane named Origami lived on the top shelf of a little girl's bedroom for eleven years before anyone noticed her. The girl had folded her out of a square of red paper when she was six and placed her on the shelf and, the next week, forgotten about her. Origami watched the girl grow — learning to read, learning to play piano, learning to cry, learni... [+837 chars]

**rationale:** Illustrated storytelling slideshow from a text brief with no audio / subtitle overlays. Reject: AmbienceAgent (no environmental layer requested); HighlightAgent (not a highlight workflow); BriefEnricherAgent (no image upload to enrich the brief with); ScreenplayAgent (no NEW film scene-decomposition needed); MusicAgent (no BGM requested); IntakeImageAgent (no image upload); IntakeVideoAgent (no source clip uploaded); TranscriptionAgent (no subtitle requested); StoryAgent (no NEW film authoring requested); TranslationAgent (no translation / second language requested); VideoAnalysisAgent (no source-video analysis required); AudioMixAgent (no audio tracks to mix); VideoAgent (no NEW motion-clip generation requested); VideoExtendAgent (no video extension requested); StyleTransferAgent (no style transfer requested); KeyFrameAgent (no keyframe planning required).

**plan:**
  - `NarrationAgent` — Write the narration script broken into reading paragraphs.
  - `IllustrationAgent` — Generate one illustration image per paragraph of the narration.
  - `NarratorAgent` — Generate the TTS narrator audio track from the narration script.
  - `CompositorAgent` — Composite the final mp4 — assemble video, audio, and any subtitle / transitions into the deliverable.

## #14
**user_goal** (141 chars):

> Make a Japanese-inspired mini-drama about a young woman tending her dying grandfather's tea garden, with traditional Japanese-garden ambient.

**rationale:** Cinematic mini-drama from a text brief with ambient layer as the only added overlays. Reject: IntakeVideoAgent (no source clip uploaded); HighlightAgent (not a highlight workflow); VideoAnalysisAgent (no source-video analysis required); IllustrationAgent (not a slideshow / illustrated-storytelling format); TranslationAgent (no translation / second language requested); IntakeImageAgent (no image upload); TranscriptionAgent (no subtitle requested); NarratorAgent (not a slideshow / illustrated-storytelling format); StyleTransferAgent (no style transfer requested); NarrationAgent (not a slideshow / illustrated-storytelling format); VideoExtendAgent (no video extension requested); MusicAgent (no BGM requested); BriefEnricherAgent (no image upload to enrich the brief with).

**plan:**
  - `StoryAgent` — Draft the story blueprint from the brief — character arc and act structure.
  - `ScreenplayAgent` — Decompose the story into scenes with mood progression aligned to the brief.
  - `KeyFrameAgent` — Plan keyframes for the screenplay's settings, one per scene.
  - `VideoAgent` — Animate each keyframe into a per-shot motion clip.
  - `AmbienceAgent` — Author the environmental ambient layer per the brief.
  - `AudioMixAgent` — Layer the available audio tracks into the final mixed wav.
  - `CompositorAgent` — Mux the final mp4, combining the rendered visual track with audio and any subtitle overlay.

## #15
**user_goal** (96 chars):

> Extend this 4-second autumn-maple-falling clip to 12 seconds and add a gentle clarinet-solo BGM.

**rationale:** Extended video cut produced from an uploaded source video, layered with BGM. Skipped: VideoAnalysisAgent (no source-video analysis required); AmbienceAgent (no environmental layer requested); NarrationAgent (not a slideshow / illustrated-storytelling format); StyleTransferAgent (no style transfer requested); VideoAgent (no NEW motion-clip generation requested); ScreenplayAgent (no NEW film scene-decomposition needed); StoryAgent (no NEW film authoring requested); BriefEnricherAgent (no image upload to enrich the brief with); TranscriptionAgent (no subtitle requested); IntakeImageAgent (no image upload); TranslationAgent (no translation / second language requested); NarratorAgent (not a slideshow / illustrated-storytelling format); IllustrationAgent (not a slideshow / illustrated-storytelling format); HighlightAgent (not a highlight workflow); KeyFrameAgent (no keyframe planning required).

**plan:**
  - `IntakeVideoAgent` — Ingest the uploaded video into the workspace with caption metadata.
  - `VideoExtendAgent` — Extend the source video beyond its original duration.
  - `MusicAgent` — Write the requested BGM, aligned to the brief's tonal cue.
  - `AudioMixAgent` — Combine the produced audio layers into a single mixed wav.
  - `CompositorAgent` — Composite the final mp4 — assemble video, audio, and any subtitle / transitions into the deliverable.

## #16
**user_goal** (96 chars):

> Please put some Baroque-style harpsichord music under this antique-book-store walking-tour clip.

**rationale:** Modified video cut from an uploaded source video; overlays applied: BGM. Excluded — NarrationAgent (not a slideshow / illustrated-storytelling format); TranscriptionAgent (no subtitle requested); IllustrationAgent (not a slideshow / illustrated-storytelling format); StyleTransferAgent (no style transfer requested); ScreenplayAgent (no NEW film scene-decomposition needed); NarratorAgent (not a slideshow / illustrated-storytelling format); StoryAgent (no NEW film authoring requested); AmbienceAgent (no environmental layer requested); VideoExtendAgent (no video extension requested); TranslationAgent (no translation / second language requested); HighlightAgent (not a highlight workflow); IntakeImageAgent (no image upload); VideoAnalysisAgent (no source-video analysis required); KeyFrameAgent (no keyframe planning required); BriefEnricherAgent (no image upload to enrich the brief with); VideoAgent (no NEW motion-clip generation requested).

**plan:**
  - `IntakeVideoAgent` — Register the uploaded video as a captioned workspace artifact.
  - `MusicAgent` — Compose the BGM the user requested, matching the brief's emotional register.
  - `AudioMixAgent` — Layer the available audio tracks into the final mixed wav.
  - `CompositorAgent` — Output the final mp4 by composing the video, audio, and subtitle / transition elements.

## #17
**user_goal** (196 chars):

> Make a train-thriller mini-drama where a passenger on an overnight sleeper realizes mid-journey that her cabin-mate is plotting an assassination at the next major station, with tense ostinato BGM.

**rationale:** Cinematic mini-drama from a text brief with BGM as the only added overlays. Reject: TranscriptionAgent (no subtitle requested); BriefEnricherAgent (no image upload to enrich the brief with); VideoAnalysisAgent (no source-video analysis required); IntakeVideoAgent (no source clip uploaded); StyleTransferAgent (no style transfer requested); HighlightAgent (not a highlight workflow); NarratorAgent (not a slideshow / illustrated-storytelling format); IllustrationAgent (not a slideshow / illustrated-storytelling format); VideoExtendAgent (no video extension requested); TranslationAgent (no translation / second language requested); IntakeImageAgent (no image upload); NarrationAgent (not a slideshow / illustrated-storytelling format); AmbienceAgent (no environmental layer requested).

**plan:**
  - `StoryAgent` — Author the story blueprint following the brief, with a clear arc and beat structure.
  - `ScreenplayAgent` — Break the drafted story into scene-by-scene units, preserving the brief's tonal register.
  - `KeyFrameAgent` — Plan keyframes for the screenplay's settings, one per scene.
  - `VideoAgent` — Produce per-shot video clips from each keyframe, holding aesthetic continuity across cuts.
  - `MusicAgent` — Compose the BGM the user requested, matching the brief's emotional register.
  - `AudioMixAgent` — Combine the produced audio layers into a single mixed wav.
  - `CompositorAgent` — Output the final mp4 by composing the video, audio, and subtitle / transition elements.

## #18
**user_goal** (104 chars):

> Please apply a Dali surrealist dreamscape style to this Persian poetry-reading and add Persian captions.

**rationale:** Style-transferred video cut from an uploaded source video; overlays applied: subtitles. Excluded — NarratorAgent (not a slideshow / illustrated-storytelling format); IllustrationAgent (not a slideshow / illustrated-storytelling format); HighlightAgent (not a highlight workflow); BriefEnricherAgent (no image upload to enrich the brief with); IntakeImageAgent (no image upload); VideoAnalysisAgent (no source-video analysis required); KeyFrameAgent (no keyframe planning required); VideoExtendAgent (no video extension requested); StoryAgent (no NEW film authoring requested); AmbienceAgent (no environmental layer requested); VideoAgent (no NEW motion-clip generation requested); ScreenplayAgent (no NEW film scene-decomposition needed); AudioMixAgent (no audio tracks to mix); TranslationAgent (no translation / second language requested); NarrationAgent (not a slideshow / illustrated-storytelling format); MusicAgent (no BGM requested).

**plan:**
  - `IntakeVideoAgent` — Persist the uploaded video into the workspace as a captioned artifact.
  - `StyleTransferAgent` — Apply the requested style transfer to the source video.
  - `TranscriptionAgent` — Transcribe the spoken dialogue into a timestamped subtitle track.
  - `CompositorAgent` — Composite the final mp4 — assemble video, audio, and any subtitle / transitions into the deliverable.

## #19
**user_goal** (105 chars):

> Make a Polish-subtitled Krakow mini-drama about a young Jewish cellist surviving WWII in the underground.

**rationale:** Cinematic mini-drama from a text brief; overlays applied: subtitles. Excluded — NarratorAgent (not a slideshow / illustrated-storytelling format); StyleTransferAgent (no style transfer requested); BriefEnricherAgent (no image upload to enrich the brief with); IllustrationAgent (not a slideshow / illustrated-storytelling format); AudioMixAgent (no audio tracks to mix); IntakeImageAgent (no image upload); AmbienceAgent (no environmental layer requested); IntakeVideoAgent (no source clip uploaded); VideoAnalysisAgent (no source-video analysis required); TranslationAgent (no translation / second language requested); MusicAgent (no BGM requested); VideoExtendAgent (no video extension requested); NarrationAgent (not a slideshow / illustrated-storytelling format); HighlightAgent (not a highlight workflow).

**plan:**
  - `StoryAgent` — Outline the story blueprint per the brief — protagonist arc and pivot beats.
  - `ScreenplayAgent` — Convert the story into a scene-by-scene screenplay matching the brief's register.
  - `KeyFrameAgent` — Plan keyframes for the screenplay's settings, one per scene.
  - `VideoAgent` — Animate each keyframe into a per-shot motion clip.
  - `TranscriptionAgent` — Transcribe the spoken dialogue into a timestamped subtitle track.
  - `CompositorAgent` — Mux the final mp4, combining the rendered visual track with audio and any subtitle overlay.

## #20
**user_goal** (144 chars):

> From this 2-hour French cooking competition, pull the plating reveals, add French + English bilingual captions, and add a smooth jazz-piano BGM.

**rationale:** Highlight reel produced from an uploaded source video, layered with BGM + bilingual subtitles. Skipped: NarratorAgent (not a slideshow / illustrated-storytelling format); IllustrationAgent (not a slideshow / illustrated-storytelling format); StoryAgent (no NEW film authoring requested); IntakeImageAgent (no image upload); KeyFrameAgent (no keyframe planning required); VideoExtendAgent (no video extension requested); StyleTransferAgent (no style transfer requested); NarrationAgent (not a slideshow / illustrated-storytelling format); AmbienceAgent (no environmental layer requested); ScreenplayAgent (no NEW film scene-decomposition needed); VideoAgent (no NEW motion-clip generation requested); BriefEnricherAgent (no image upload to enrich the brief with).

**plan:**
  - `IntakeVideoAgent` — Ingest the uploaded video into the workspace with caption metadata.
  - `VideoAnalysisAgent` — Analyze the source video into a scene-by-scene report (genre, mood, beats, entities).
  - `HighlightAgent` — Pick the top highlight clips from the source video using the analysis report.
  - `TranscriptionAgent` — Generate the subtitle track from the dialogue audio with per-line timestamps.
  - `TranslationAgent` — Translate the source-language subtitles into the requested target language.
  - `MusicAgent` — Compose the BGM the user requested, matching the brief's emotional register.
  - `AudioMixAgent` — Mix the available audio tracks into one final mixed wav.
  - `CompositorAgent` — Output the final mp4 by composing the video, audio, and subtitle / transition elements.

## #21
**user_goal** (1265 chars):

> Here's my story I want to process: In a forest older than any map, there ran a small clear river called Ibi. It was not a great river. It was only as wide as a child could jump across. But the old women of the nearest village said, and had said for many generations, that Ibi listened. If you whispered a wish over its moving water, and if your wish was honest, Ibi would sometimes grant it — not in ... [+865 chars]

**rationale:** Illustrated storytelling slideshow from a text brief with no audio / subtitle overlays. Reject: BriefEnricherAgent (no image upload to enrich the brief with); KeyFrameAgent (no keyframe planning required); ScreenplayAgent (no NEW film scene-decomposition needed); AmbienceAgent (no environmental layer requested); StoryAgent (no NEW film authoring requested); IntakeImageAgent (no image upload); IntakeVideoAgent (no source clip uploaded); VideoAnalysisAgent (no source-video analysis required); AudioMixAgent (no audio tracks to mix); MusicAgent (no BGM requested); TranslationAgent (no translation / second language requested); VideoAgent (no NEW motion-clip generation requested); StyleTransferAgent (no style transfer requested); VideoExtendAgent (no video extension requested); HighlightAgent (not a highlight workflow); TranscriptionAgent (no subtitle requested).

**plan:**
  - `NarrationAgent` — Author the narration script from the brief — paragraph-by-paragraph story text.
  - `IllustrationAgent` — Render one still illustration per narration paragraph.
  - `NarratorAgent` — Produce the spoken narrator track via TTS over the narration text.
  - `CompositorAgent` — Composite the final mp4 — assemble video, audio, and any subtitle / transitions into the deliverable.

## #22
**user_goal** (204 chars):

> Make an animated drama about a kingdom of forest animals overthrowing a corrupt fox dynasty after the youngest mouse-prince returns from exile with a hidden human ally, with cinematic full orchestral BGM.

**rationale:** Cinematic mini-drama from a text brief; overlays applied: BGM. Excluded — BriefEnricherAgent (no image upload to enrich the brief with); NarratorAgent (not a slideshow / illustrated-storytelling format); VideoAnalysisAgent (no source-video analysis required); IntakeImageAgent (no image upload); TranscriptionAgent (no subtitle requested); IllustrationAgent (not a slideshow / illustrated-storytelling format); HighlightAgent (not a highlight workflow); IntakeVideoAgent (no source clip uploaded); NarrationAgent (not a slideshow / illustrated-storytelling format); TranslationAgent (no translation / second language requested); StyleTransferAgent (no style transfer requested); AmbienceAgent (no environmental layer requested); VideoExtendAgent (no video extension requested).

**plan:**
  - `StoryAgent` — Draft the story blueprint from the brief — character arc and act structure.
  - `ScreenplayAgent` — Decompose the story into scenes with mood progression aligned to the brief.
  - `KeyFrameAgent` — Plan keyframes for the screenplay's settings, one per scene.
  - `VideoAgent` — Render per-shot motion clips from the keyframes, preserving visual continuity.
  - `MusicAgent` — Compose the BGM the user requested, matching the brief's emotional register.
  - `AudioMixAgent` — Layer the available audio tracks into the final mixed wav.
  - `CompositorAgent` — Composite the final mp4 — assemble video, audio, and any subtitle / transitions into the deliverable.

## #23
**user_goal** (1117 chars):

> Here's my story I want to process: A small fishing boat named Halla had been sailing the cold northern fjords for thirty-two years. Her paint was worn. Her engine coughed. Her hull creaked. The young captain who owned her, Einar, was told by everyone that he should retire her and buy a new boat. Einar refused. He said Halla had seen every storm the coast could throw at her, and she had brought him... [+717 chars]

**rationale:** Illustrated storytelling slideshow from a text brief; no overlays added. Excluded — VideoExtendAgent (no video extension requested); IntakeVideoAgent (no source clip uploaded); AudioMixAgent (no audio tracks to mix); AmbienceAgent (no environmental layer requested); ScreenplayAgent (no NEW film scene-decomposition needed); TranslationAgent (no translation / second language requested); KeyFrameAgent (no keyframe planning required); VideoAgent (no NEW motion-clip generation requested); StoryAgent (no NEW film authoring requested); VideoAnalysisAgent (no source-video analysis required); BriefEnricherAgent (no image upload to enrich the brief with); MusicAgent (no BGM requested); TranscriptionAgent (no subtitle requested); StyleTransferAgent (no style transfer requested); HighlightAgent (not a highlight workflow); IntakeImageAgent (no image upload).

**plan:**
  - `NarrationAgent` — Write the narration script broken into reading paragraphs.
  - `IllustrationAgent` — Produce per-paragraph illustrations matching the narration.
  - `NarratorAgent` — Generate the TTS narrator audio track from the narration script.
  - `CompositorAgent` — Composite the final mp4 — assemble video, audio, and any subtitle / transitions into the deliverable.

## #24
**user_goal** (166 chars):

> Make an illustrated audiobook of this Irish folktale about the selkie who left her seal-skin on the shore, with Celtic-knot-border watercolor illustrations per scene.

**rationale:** Illustrated storytelling slideshow from a text brief with no audio / subtitle overlays. Reject: StoryAgent (no NEW film authoring requested); VideoExtendAgent (no video extension requested); BriefEnricherAgent (no image upload to enrich the brief with); MusicAgent (no BGM requested); StyleTransferAgent (no style transfer requested); VideoAnalysisAgent (no source-video analysis required); AmbienceAgent (no environmental layer requested); AudioMixAgent (no audio tracks to mix); IntakeVideoAgent (no source clip uploaded); ScreenplayAgent (no NEW film scene-decomposition needed); IntakeImageAgent (no image upload); KeyFrameAgent (no keyframe planning required); VideoAgent (no NEW motion-clip generation requested); TranslationAgent (no translation / second language requested); HighlightAgent (not a highlight workflow); TranscriptionAgent (no subtitle requested).

**plan:**
  - `NarrationAgent` — Draft the narration script per the brief, paragraph-by-paragraph.
  - `IllustrationAgent` — Produce per-paragraph illustrations matching the narration.
  - `NarratorAgent` — Produce the spoken narrator track via TTS over the narration text.
  - `CompositorAgent` — Composite the final mp4 — assemble video, audio, and any subtitle / transitions into the deliverable.

## #25
**user_goal** (117 chars):

> Restyle this Romanian folk-music performance as an art-nouveau Mucha ornamental aesthetic and add Romanian subtitles.

**rationale:** Style-transferred video cut produced from an uploaded source video, layered with subtitles. Skipped: VideoExtendAgent (no video extension requested); NarrationAgent (not a slideshow / illustrated-storytelling format); KeyFrameAgent (no keyframe planning required); IntakeImageAgent (no image upload); AmbienceAgent (no environmental layer requested); TranslationAgent (no translation / second language requested); HighlightAgent (not a highlight workflow); AudioMixAgent (no audio tracks to mix); VideoAgent (no NEW motion-clip generation requested); VideoAnalysisAgent (no source-video analysis required); StoryAgent (no NEW film authoring requested); BriefEnricherAgent (no image upload to enrich the brief with); IllustrationAgent (not a slideshow / illustrated-storytelling format); ScreenplayAgent (no NEW film scene-decomposition needed); MusicAgent (no BGM requested); NarratorAgent (not a slideshow / illustrated-storytelling format).

**plan:**
  - `IntakeVideoAgent` — Register the uploaded video as a captioned workspace artifact.
  - `StyleTransferAgent` — Re-render the source video under the requested visual style.
  - `TranscriptionAgent` — Author the timestamped transcription of the spoken dialogue.
  - `CompositorAgent` — Output the final mp4 by composing the video, audio, and subtitle / transition elements.

## #26
**user_goal** (110 chars):

> Using this uploaded image of a volcanic island, make an extended scientist-racing-against-eruption mini-drama.

**rationale:** Extended-runtime cinematic mini-drama from a text brief + uploaded reference image; no overlays added. Excluded — StyleTransferAgent (no style transfer requested); HighlightAgent (not a highlight workflow); IllustrationAgent (not a slideshow / illustrated-storytelling format); TranslationAgent (no translation / second language requested); NarratorAgent (not a slideshow / illustrated-storytelling format); IntakeVideoAgent (no source clip uploaded); AmbienceAgent (no environmental layer requested); MusicAgent (no BGM requested); AudioMixAgent (no audio tracks to mix); VideoAnalysisAgent (no source-video analysis required); TranscriptionAgent (no subtitle requested); NarrationAgent (not a slideshow / illustrated-storytelling format).

**plan:**
  - `IntakeImageAgent` — Ingest the uploaded image into the workspace with caption metadata.
  - `BriefEnricherAgent` — Fold image-reference descriptions into the brief to produce an enriched creative brief.
  - `StoryAgent` — Draft the story blueprint from the brief — character arc and act structure.
  - `ScreenplayAgent` — Convert the story into a scene-by-scene screenplay matching the brief's register.
  - `KeyFrameAgent` — Lay out keyframes for the screenplay's settings, scene-by-scene.
  - `VideoAgent` — Produce per-shot video clips from each keyframe, holding aesthetic continuity across cuts.
  - `VideoExtendAgent` — Produce extended footage that continues the source video.
  - `CompositorAgent` — Output the final mp4 by composing the video, audio, and subtitle / transition elements.

## #27
**user_goal** (113 chars):

> Make a Croatian-English bilingual Dubrovnik mini-drama about a young historian documenting a medieval manuscript.

**rationale:** Cinematic mini-drama from a text brief with bilingual subtitles as the only added overlays. Reject: HighlightAgent (not a highlight workflow); NarrationAgent (not a slideshow / illustrated-storytelling format); MusicAgent (no BGM requested); VideoExtendAgent (no video extension requested); IntakeVideoAgent (no source clip uploaded); AmbienceAgent (no environmental layer requested); AudioMixAgent (no audio tracks to mix); IllustrationAgent (not a slideshow / illustrated-storytelling format); NarratorAgent (not a slideshow / illustrated-storytelling format); StyleTransferAgent (no style transfer requested); IntakeImageAgent (no image upload); VideoAnalysisAgent (no source-video analysis required); BriefEnricherAgent (no image upload to enrich the brief with).

**plan:**
  - `StoryAgent` — Author the story blueprint following the brief, with a clear arc and beat structure.
  - `ScreenplayAgent` — Decompose the story into scenes with mood progression aligned to the brief.
  - `KeyFrameAgent` — Plan keyframes for the screenplay's settings, one per scene.
  - `VideoAgent` — Animate each keyframe into a per-shot motion clip.
  - `TranscriptionAgent` — Author the timestamped transcription of the spoken dialogue.
  - `TranslationAgent` — Produce the second-language subtitle track from the source transcription.
  - `CompositorAgent` — Output the final mp4 by composing the video, audio, and subtitle / transition elements.

## #28
**user_goal** (103 chars):

> Using this uploaded image of an ancient Egyptian tomb, make an extended-length Egyptologist mini-drama.

**rationale:** Extended-runtime cinematic mini-drama from a text brief + uploaded reference image; no overlays added. Excluded — NarratorAgent (not a slideshow / illustrated-storytelling format); NarrationAgent (not a slideshow / illustrated-storytelling format); IllustrationAgent (not a slideshow / illustrated-storytelling format); TranscriptionAgent (no subtitle requested); MusicAgent (no BGM requested); VideoAnalysisAgent (no source-video analysis required); IntakeVideoAgent (no source clip uploaded); AudioMixAgent (no audio tracks to mix); AmbienceAgent (no environmental layer requested); TranslationAgent (no translation / second language requested); StyleTransferAgent (no style transfer requested); HighlightAgent (not a highlight workflow).

**plan:**
  - `IntakeImageAgent` — Register the uploaded image as a captioned workspace artifact.
  - `BriefEnricherAgent` — Enrich the brief by integrating descriptions of the uploaded reference images.
  - `StoryAgent` — Author the story blueprint following the brief, with a clear arc and beat structure.
  - `ScreenplayAgent` — Decompose the story into scenes with mood progression aligned to the brief.
  - `KeyFrameAgent` — Design keyframes from the screenplay scene by scene.
  - `VideoAgent` — Animate each keyframe into a per-shot motion clip.
  - `VideoExtendAgent` — Generate continuation footage extending the source video.
  - `CompositorAgent` — Output the final mp4 by composing the video, audio, and subtitle / transition elements.

## #29
**user_goal** (143 chars):

> Take this 5-second clip of a blooming flower, extend to 15 seconds (fully open on camera), and restyle as a Georgia O'Keeffe close-up painting.

**rationale:** Style-transferred + extended video cut from an uploaded source video; no overlays added. Excluded — MusicAgent (no BGM requested); TranslationAgent (no translation / second language requested); NarrationAgent (not a slideshow / illustrated-storytelling format); AmbienceAgent (no environmental layer requested); BriefEnricherAgent (no image upload to enrich the brief with); IllustrationAgent (not a slideshow / illustrated-storytelling format); ScreenplayAgent (no NEW film scene-decomposition needed); CompositorAgent (no final mux required); StoryAgent (no NEW film authoring requested); KeyFrameAgent (no keyframe planning required); VideoAgent (no NEW motion-clip generation requested); HighlightAgent (not a highlight workflow); NarratorAgent (not a slideshow / illustrated-storytelling format); TranscriptionAgent (no subtitle requested); IntakeImageAgent (no image upload); AudioMixAgent (no audio tracks to mix); VideoAnalysisAgent (no source-video analysis required).

**plan:**
  - `IntakeVideoAgent` — Register the uploaded video as a captioned workspace artifact.
  - `VideoExtendAgent` — Extend the source video beyond its original duration.
  - `StyleTransferAgent` — Run style transfer on the source video to match the requested aesthetic.

## #30
**user_goal** (95 chars):

> Add a cozy folk-guitar BGM AND crackling-fireplace ambient to this winter-cabin-interior video.

**rationale:** Modified video cut from an uploaded source video with BGM + ambient layer as the only added overlays. Reject: VideoAnalysisAgent (no source-video analysis required); TranslationAgent (no translation / second language requested); IllustrationAgent (not a slideshow / illustrated-storytelling format); HighlightAgent (not a highlight workflow); VideoAgent (no NEW motion-clip generation requested); KeyFrameAgent (no keyframe planning required); TranscriptionAgent (no subtitle requested); NarrationAgent (not a slideshow / illustrated-storytelling format); StoryAgent (no NEW film authoring requested); IntakeImageAgent (no image upload); VideoExtendAgent (no video extension requested); ScreenplayAgent (no NEW film scene-decomposition needed); BriefEnricherAgent (no image upload to enrich the brief with); StyleTransferAgent (no style transfer requested); NarratorAgent (not a slideshow / illustrated-storytelling format).

**plan:**
  - `IntakeVideoAgent` — Persist the uploaded video into the workspace as a captioned artifact.
  - `MusicAgent` — Generate the requested BGM, scored to the brief's mood.
  - `AmbienceAgent` — Author the environmental ambient layer per the brief.
  - `AudioMixAgent` — Layer the available audio tracks into the final mixed wav.
  - `CompositorAgent` — Composite the final mp4 — assemble video, audio, and any subtitle / transitions into the deliverable.

## #31
**user_goal** (136 chars):

> Using this uploaded image of a Caribbean beach bar, make a sunset-romance mini-drama about two strangers finding each other on vacation.

**rationale:** Cinematic mini-drama from a text brief + uploaded reference image with no audio / subtitle overlays. Reject: MusicAgent (no BGM requested); TranscriptionAgent (no subtitle requested); IllustrationAgent (not a slideshow / illustrated-storytelling format); AmbienceAgent (no environmental layer requested); NarrationAgent (not a slideshow / illustrated-storytelling format); IntakeVideoAgent (no source clip uploaded); StyleTransferAgent (no style transfer requested); VideoAnalysisAgent (no source-video analysis required); VideoExtendAgent (no video extension requested); HighlightAgent (not a highlight workflow); AudioMixAgent (no audio tracks to mix); TranslationAgent (no translation / second language requested); NarratorAgent (not a slideshow / illustrated-storytelling format).

**plan:**
  - `IntakeImageAgent` — Register the uploaded image as a captioned workspace artifact.
  - `BriefEnricherAgent` — Augment the brief with the uploaded image's descriptive content.
  - `StoryAgent` — Author the story blueprint following the brief, with a clear arc and beat structure.
  - `ScreenplayAgent` — Convert the story into a scene-by-scene screenplay matching the brief's register.
  - `KeyFrameAgent` — Lay out keyframes for the screenplay's settings, scene-by-scene.
  - `VideoAgent` — Render per-shot motion clips from the keyframes, preserving visual continuity.
  - `CompositorAgent` — Composite the final mp4 — assemble video, audio, and any subtitle / transitions into the deliverable.

## #32
**user_goal** (130 chars):

> Using this uploaded image of a Buenos Aires tango salon, make a young-tango-dancer mini-drama with Spanish+English bilingual subs.

**rationale:** Cinematic mini-drama produced from a text brief + uploaded reference image, layered with bilingual subtitles. Skipped: HighlightAgent (not a highlight workflow); IntakeVideoAgent (no source clip uploaded); VideoExtendAgent (no video extension requested); MusicAgent (no BGM requested); IllustrationAgent (not a slideshow / illustrated-storytelling format); StyleTransferAgent (no style transfer requested); NarratorAgent (not a slideshow / illustrated-storytelling format); AudioMixAgent (no audio tracks to mix); VideoAnalysisAgent (no source-video analysis required); NarrationAgent (not a slideshow / illustrated-storytelling format); AmbienceAgent (no environmental layer requested).

**plan:**
  - `IntakeImageAgent` — Ingest the uploaded image into the workspace with caption metadata.
  - `BriefEnricherAgent` — Fold image-reference descriptions into the brief to produce an enriched creative brief.
  - `StoryAgent` — Author the story blueprint following the brief, with a clear arc and beat structure.
  - `ScreenplayAgent` — Convert the story into a scene-by-scene screenplay matching the brief's register.
  - `KeyFrameAgent` — Design keyframes from the screenplay scene by scene.
  - `VideoAgent` — Produce per-shot video clips from each keyframe, holding aesthetic continuity across cuts.
  - `TranscriptionAgent` — Author the timestamped transcription of the spoken dialogue.
  - `TranslationAgent` — Render the bilingual translation of the subtitle track.
  - `CompositorAgent` — Composite the final mp4 — assemble video, audio, and any subtitle / transitions into the deliverable.

## #33
**user_goal** (110 chars):

> Add gentle lullaby BGM AND nighttime-bedroom ambient (soft crickets, distant owl) to this baby-sleeping video.

**rationale:** Modified video cut from an uploaded source video with BGM + ambient layer as the only added overlays. Reject: BriefEnricherAgent (no image upload to enrich the brief with); StyleTransferAgent (no style transfer requested); VideoAnalysisAgent (no source-video analysis required); TranscriptionAgent (no subtitle requested); KeyFrameAgent (no keyframe planning required); VideoExtendAgent (no video extension requested); NarratorAgent (not a slideshow / illustrated-storytelling format); ScreenplayAgent (no NEW film scene-decomposition needed); HighlightAgent (not a highlight workflow); NarrationAgent (not a slideshow / illustrated-storytelling format); TranslationAgent (no translation / second language requested); VideoAgent (no NEW motion-clip generation requested); StoryAgent (no NEW film authoring requested); IntakeImageAgent (no image upload); IllustrationAgent (not a slideshow / illustrated-storytelling format).

**plan:**
  - `IntakeVideoAgent` — Register the uploaded video as a captioned workspace artifact.
  - `MusicAgent` — Generate the requested BGM, scored to the brief's mood.
  - `AmbienceAgent` — Author the environmental ambient layer per the brief.
  - `AudioMixAgent` — Combine the produced audio layers into a single mixed wav.
  - `CompositorAgent` — Output the final mp4 by composing the video, audio, and subtitle / transition elements.

## #34
**user_goal** (196 chars):

> Using this uploaded portrait of a tiny fire-sprite, turn this short myth into an illustrated audiobook where the appearance stays consistent, with a warm acoustic guitar score under the narration.

**rationale:** Illustrated storytelling slideshow produced from a text brief + uploaded reference image, layered with BGM. Skipped: KeyFrameAgent (no keyframe planning required); VideoExtendAgent (no video extension requested); HighlightAgent (not a highlight workflow); AmbienceAgent (no environmental layer requested); StyleTransferAgent (no style transfer requested); ScreenplayAgent (no NEW film scene-decomposition needed); TranslationAgent (no translation / second language requested); VideoAgent (no NEW motion-clip generation requested); StoryAgent (no NEW film authoring requested); TranscriptionAgent (no subtitle requested); IntakeVideoAgent (no source clip uploaded); VideoAnalysisAgent (no source-video analysis required).

**plan:**
  - `IntakeImageAgent` — Persist the uploaded image into the workspace as a captioned artifact.
  - `BriefEnricherAgent` — Augment the brief with the uploaded image's descriptive content.
  - `NarrationAgent` — Write the narration script broken into reading paragraphs.
  - `IllustrationAgent` — Generate one illustration image per paragraph of the narration.
  - `NarratorAgent` — Generate the TTS narrator audio track from the narration script.
  - `MusicAgent` — Generate the requested BGM, scored to the brief's mood.
  - `AudioMixAgent` — Mix the available audio tracks into one final mixed wav.
  - `CompositorAgent` — Output the final mp4 by composing the video, audio, and subtitle / transition elements.

## #35
**user_goal** (202 chars):

> Make a spy-thriller vertical short about a deep-cover agent extracted minutes before discovery and forced to choose between mission and the cover-family she has come to love, with propulsive electronic.

**rationale:** Cinematic mini-drama from a text brief with BGM as the only added overlays. Reject: IntakeImageAgent (no image upload); IllustrationAgent (not a slideshow / illustrated-storytelling format); TranslationAgent (no translation / second language requested); VideoExtendAgent (no video extension requested); BriefEnricherAgent (no image upload to enrich the brief with); VideoAnalysisAgent (no source-video analysis required); IntakeVideoAgent (no source clip uploaded); StyleTransferAgent (no style transfer requested); NarrationAgent (not a slideshow / illustrated-storytelling format); AmbienceAgent (no environmental layer requested); TranscriptionAgent (no subtitle requested); HighlightAgent (not a highlight workflow); NarratorAgent (not a slideshow / illustrated-storytelling format).

**plan:**
  - `StoryAgent` — Draft the story blueprint from the brief — character arc and act structure.
  - `ScreenplayAgent` — Break the drafted story into scene-by-scene units, preserving the brief's tonal register.
  - `KeyFrameAgent` — Lay out keyframes for the screenplay's settings, scene-by-scene.
  - `VideoAgent` — Produce per-shot video clips from each keyframe, holding aesthetic continuity across cuts.
  - `MusicAgent` — Generate the requested BGM, scored to the brief's mood.
  - `AudioMixAgent` — Layer the available audio tracks into the final mixed wav.
  - `CompositorAgent` — Mux the final mp4, combining the rendered visual track with audio and any subtitle overlay.

## #36
**user_goal** (122 chars):

> Make an English-subtitled mini-drama about a retired fire-chief mentoring a rookie through her first major warehouse fire.

**rationale:** Cinematic mini-drama from a text brief with subtitles as the only added overlays. Reject: IntakeVideoAgent (no source clip uploaded); IllustrationAgent (not a slideshow / illustrated-storytelling format); StyleTransferAgent (no style transfer requested); VideoExtendAgent (no video extension requested); HighlightAgent (not a highlight workflow); TranslationAgent (no translation / second language requested); AudioMixAgent (no audio tracks to mix); BriefEnricherAgent (no image upload to enrich the brief with); NarrationAgent (not a slideshow / illustrated-storytelling format); AmbienceAgent (no environmental layer requested); IntakeImageAgent (no image upload); NarratorAgent (not a slideshow / illustrated-storytelling format); VideoAnalysisAgent (no source-video analysis required); MusicAgent (no BGM requested).

**plan:**
  - `StoryAgent` — Author the story blueprint following the brief, with a clear arc and beat structure.
  - `ScreenplayAgent` — Break the drafted story into scene-by-scene units, preserving the brief's tonal register.
  - `KeyFrameAgent` — Design keyframes from the screenplay scene by scene.
  - `VideoAgent` — Produce per-shot video clips from each keyframe, holding aesthetic continuity across cuts.
  - `TranscriptionAgent` — Generate the subtitle track from the dialogue audio with per-line timestamps.
  - `CompositorAgent` — Composite the final mp4 — assemble video, audio, and any subtitle / transitions into the deliverable.

## #37
**user_goal** (269 chars):

> Using the uploaded character portrait of a woodland unicorn, produce an English-Russian bilingual illustrated audiobook of a folk tale where the unicorn hides from greedy hunters in the starlit glade, narrated in English with a dreamy harp-and-strings background score.

**rationale:** Illustrated storytelling slideshow from a text brief + uploaded reference image with BGM + bilingual narration track as the only added overlays. Reject: VideoExtendAgent (no video extension requested); AmbienceAgent (no environmental layer requested); HighlightAgent (not a highlight workflow); StoryAgent (no NEW film authoring requested); KeyFrameAgent (no keyframe planning required); VideoAnalysisAgent (no source-video analysis required); IntakeVideoAgent (no source clip uploaded); ScreenplayAgent (no NEW film scene-decomposition needed); TranscriptionAgent (no subtitle requested); VideoAgent (no NEW motion-clip generation requested); StyleTransferAgent (no style transfer requested).

**plan:**
  - `IntakeImageAgent` — Register the uploaded image as a captioned workspace artifact.
  - `BriefEnricherAgent` — Enrich the brief by integrating descriptions of the uploaded reference images.
  - `NarrationAgent` — Draft the narration script per the brief, paragraph-by-paragraph.
  - `IllustrationAgent` — Generate one illustration image per paragraph of the narration.
  - `NarratorAgent` — Generate the TTS narrator audio track from the narration script.
  - `MusicAgent` — Generate the requested BGM, scored to the brief's mood.
  - `AudioMixAgent` — Layer the available audio tracks into the final mixed wav.
  - `TranslationAgent` — Render the bilingual translation of the subtitle track.
  - `CompositorAgent` — Composite the final mp4 — assemble video, audio, and any subtitle / transitions into the deliverable.

## #38
**user_goal** (135 chars):

> From this 2-hour Turkish drama, pull the emotional scenes, add Turkish + English bilingual subs, and add a haunting string-quartet BGM.

**rationale:** Highlight reel from an uploaded source video with BGM + bilingual subtitles as the only added overlays. Reject: IntakeImageAgent (no image upload); ScreenplayAgent (no NEW film scene-decomposition needed); NarratorAgent (not a slideshow / illustrated-storytelling format); StyleTransferAgent (no style transfer requested); VideoExtendAgent (no video extension requested); NarrationAgent (not a slideshow / illustrated-storytelling format); IllustrationAgent (not a slideshow / illustrated-storytelling format); AmbienceAgent (no environmental layer requested); StoryAgent (no NEW film authoring requested); KeyFrameAgent (no keyframe planning required); VideoAgent (no NEW motion-clip generation requested); BriefEnricherAgent (no image upload to enrich the brief with).

**plan:**
  - `IntakeVideoAgent` — Persist the uploaded video into the workspace as a captioned artifact.
  - `VideoAnalysisAgent` — Produce a scene-level analysis report of the source video for downstream reasoning.
  - `HighlightAgent` — Pick the top highlight clips from the source video using the analysis report.
  - `TranscriptionAgent` — Generate the subtitle track from the dialogue audio with per-line timestamps.
  - `TranslationAgent` — Translate the source-language subtitles into the requested target language.
  - `MusicAgent` — Compose the BGM the user requested, matching the brief's emotional register.
  - `AudioMixAgent` — Mix the available audio tracks into one final mixed wav.
  - `CompositorAgent` — Output the final mp4 by composing the video, audio, and subtitle / transition elements.

## #39
**user_goal** (121 chars):

> Using this uploaded portrait of a dragon, make an illustrated audiobook about the young dragon who couldn't breathe fire.

**rationale:** Illustrated storytelling slideshow from a text brief + uploaded reference image with no audio / subtitle overlays. Reject: TranslationAgent (no translation / second language requested); IntakeVideoAgent (no source clip uploaded); VideoExtendAgent (no video extension requested); StoryAgent (no NEW film authoring requested); TranscriptionAgent (no subtitle requested); StyleTransferAgent (no style transfer requested); VideoAnalysisAgent (no source-video analysis required); KeyFrameAgent (no keyframe planning required); ScreenplayAgent (no NEW film scene-decomposition needed); VideoAgent (no NEW motion-clip generation requested); AudioMixAgent (no audio tracks to mix); MusicAgent (no BGM requested); AmbienceAgent (no environmental layer requested); HighlightAgent (not a highlight workflow).

**plan:**
  - `IntakeImageAgent` — Register the uploaded image as a captioned workspace artifact.
  - `BriefEnricherAgent` — Enrich the brief by integrating descriptions of the uploaded reference images.
  - `NarrationAgent` — Draft the narration script per the brief, paragraph-by-paragraph.
  - `IllustrationAgent` — Render one still illustration per narration paragraph.
  - `NarratorAgent` — Produce the spoken narrator track via TTS over the narration text.
  - `CompositorAgent` — Mux the final mp4, combining the rendered visual track with audio and any subtitle overlay.

## #40
**user_goal** (108 chars):

> Make an English-subtitled mini-drama about a young Alaskan fisherwoman captaining her first solo salmon run.

**rationale:** Cinematic mini-drama produced from a text brief, layered with subtitles. Skipped: NarratorAgent (not a slideshow / illustrated-storytelling format); MusicAgent (no BGM requested); HighlightAgent (not a highlight workflow); VideoExtendAgent (no video extension requested); StyleTransferAgent (no style transfer requested); AudioMixAgent (no audio tracks to mix); AmbienceAgent (no environmental layer requested); VideoAnalysisAgent (no source-video analysis required); IntakeImageAgent (no image upload); IntakeVideoAgent (no source clip uploaded); TranslationAgent (no translation / second language requested); BriefEnricherAgent (no image upload to enrich the brief with); IllustrationAgent (not a slideshow / illustrated-storytelling format); NarrationAgent (not a slideshow / illustrated-storytelling format).

**plan:**
  - `StoryAgent` — Author the story blueprint following the brief, with a clear arc and beat structure.
  - `ScreenplayAgent` — Convert the story into a scene-by-scene screenplay matching the brief's register.
  - `KeyFrameAgent` — Design keyframes from the screenplay scene by scene.
  - `VideoAgent` — Animate each keyframe into a per-shot motion clip.
  - `TranscriptionAgent` — Author the timestamped transcription of the spoken dialogue.
  - `CompositorAgent` — Composite the final mp4 — assemble video, audio, and any subtitle / transitions into the deliverable.

## #41
**user_goal** (94 chars):

> Restyle this drone flyover of desert dunes as a minimalist Georgia O'Keeffe abstract painting.

**rationale:** Style-transferred video cut from an uploaded source video; no overlays added. Excluded — CompositorAgent (no final mux required); VideoAgent (no NEW motion-clip generation requested); IllustrationAgent (not a slideshow / illustrated-storytelling format); IntakeImageAgent (no image upload); BriefEnricherAgent (no image upload to enrich the brief with); TranslationAgent (no translation / second language requested); NarrationAgent (not a slideshow / illustrated-storytelling format); AmbienceAgent (no environmental layer requested); StoryAgent (no NEW film authoring requested); HighlightAgent (not a highlight workflow); TranscriptionAgent (no subtitle requested); AudioMixAgent (no audio tracks to mix); ScreenplayAgent (no NEW film scene-decomposition needed); MusicAgent (no BGM requested); NarratorAgent (not a slideshow / illustrated-storytelling format); VideoExtendAgent (no video extension requested); KeyFrameAgent (no keyframe planning required); VideoAnalysisAgent (no source-video analysis required).

**plan:**
  - `IntakeVideoAgent` — Ingest the uploaded video into the workspace with caption metadata.
  - `StyleTransferAgent` — Re-render the source video under the requested visual style.

## #42
**user_goal** (139 chars):

> Extract the best surfing tricks from this 2-hour surf competition, add English captions from the broadcast, and add a laid-back reggae BGM.

**rationale:** Highlight reel produced from an uploaded source video, layered with BGM + subtitles. Skipped: NarratorAgent (not a slideshow / illustrated-storytelling format); StoryAgent (no NEW film authoring requested); StyleTransferAgent (no style transfer requested); VideoAgent (no NEW motion-clip generation requested); AmbienceAgent (no environmental layer requested); ScreenplayAgent (no NEW film scene-decomposition needed); NarrationAgent (not a slideshow / illustrated-storytelling format); TranslationAgent (no translation / second language requested); KeyFrameAgent (no keyframe planning required); IllustrationAgent (not a slideshow / illustrated-storytelling format); VideoExtendAgent (no video extension requested); BriefEnricherAgent (no image upload to enrich the brief with); IntakeImageAgent (no image upload).

**plan:**
  - `IntakeVideoAgent` — Ingest the uploaded video into the workspace with caption metadata.
  - `VideoAnalysisAgent` — Produce a scene-level analysis report of the source video for downstream reasoning.
  - `HighlightAgent` — Select the highlight segments from the analyzed source video.
  - `MusicAgent` — Write the requested BGM, aligned to the brief's tonal cue.
  - `TranscriptionAgent` — Author the timestamped transcription of the spoken dialogue.
  - `AudioMixAgent` — Combine the produced audio layers into a single mixed wav.
  - `CompositorAgent` — Composite the final mp4 — assemble video, audio, and any subtitle / transitions into the deliverable.

## #43
**user_goal** (110 chars):

> Please extend this 8-second lecture clip to 25 seconds and add English subtitles. The lecturer speaks English.

**rationale:** Extended video cut produced from an uploaded source video, layered with subtitles. Skipped: AmbienceAgent (no environmental layer requested); NarratorAgent (not a slideshow / illustrated-storytelling format); KeyFrameAgent (no keyframe planning required); MusicAgent (no BGM requested); NarrationAgent (not a slideshow / illustrated-storytelling format); IllustrationAgent (not a slideshow / illustrated-storytelling format); StyleTransferAgent (no style transfer requested); AudioMixAgent (no audio tracks to mix); TranslationAgent (no translation / second language requested); IntakeImageAgent (no image upload); StoryAgent (no NEW film authoring requested); ScreenplayAgent (no NEW film scene-decomposition needed); VideoAnalysisAgent (no source-video analysis required); HighlightAgent (not a highlight workflow); BriefEnricherAgent (no image upload to enrich the brief with); VideoAgent (no NEW motion-clip generation requested).

**plan:**
  - `IntakeVideoAgent` — Register the uploaded video as a captioned workspace artifact.
  - `VideoExtendAgent` — Extend the source video beyond its original duration.
  - `TranscriptionAgent` — Author the timestamped transcription of the spoken dialogue.
  - `CompositorAgent` — Output the final mp4 by composing the video, audio, and subtitle / transition elements.

## #44
**user_goal** (141 chars):

> Extend this subway-platform reunion scene by 8 seconds, layering in train brake squeals, crowd footsteps, and PA announcement ambient sounds.

**rationale:** Extended video cut produced from an uploaded source video, layered with ambient layer. Skipped: VideoAgent (no NEW motion-clip generation requested); ScreenplayAgent (no NEW film scene-decomposition needed); BriefEnricherAgent (no image upload to enrich the brief with); HighlightAgent (not a highlight workflow); KeyFrameAgent (no keyframe planning required); VideoAnalysisAgent (no source-video analysis required); StoryAgent (no NEW film authoring requested); IllustrationAgent (not a slideshow / illustrated-storytelling format); TranscriptionAgent (no subtitle requested); IntakeImageAgent (no image upload); NarrationAgent (not a slideshow / illustrated-storytelling format); StyleTransferAgent (no style transfer requested); TranslationAgent (no translation / second language requested); MusicAgent (no BGM requested); NarratorAgent (not a slideshow / illustrated-storytelling format).

**plan:**
  - `IntakeVideoAgent` — Ingest the uploaded video into the workspace with caption metadata.
  - `VideoExtendAgent` — Extend the source video beyond its original duration.
  - `AmbienceAgent` — Author the environmental ambient layer per the brief.
  - `AudioMixAgent` — Combine the produced audio layers into a single mixed wav.
  - `CompositorAgent` — Composite the final mp4 — assemble video, audio, and any subtitle / transitions into the deliverable.

## #45
**user_goal** (141 chars):

> Create an English-Spanish bilingual illustrated audiobook of this Spanish folktale about the silver horseshoe with a soft Spanish guitar BGM.

**rationale:** Illustrated storytelling slideshow produced from a text brief, layered with BGM + bilingual narration track. Skipped: VideoExtendAgent (no video extension requested); VideoAgent (no NEW motion-clip generation requested); StoryAgent (no NEW film authoring requested); HighlightAgent (not a highlight workflow); IntakeVideoAgent (no source clip uploaded); KeyFrameAgent (no keyframe planning required); VideoAnalysisAgent (no source-video analysis required); TranscriptionAgent (no subtitle requested); IntakeImageAgent (no image upload); AmbienceAgent (no environmental layer requested); StyleTransferAgent (no style transfer requested); ScreenplayAgent (no NEW film scene-decomposition needed); BriefEnricherAgent (no image upload to enrich the brief with).

**plan:**
  - `NarrationAgent` — Write the narration script broken into reading paragraphs.
  - `IllustrationAgent` — Generate one illustration image per paragraph of the narration.
  - `NarratorAgent` — Produce the spoken narrator track via TTS over the narration text.
  - `MusicAgent` — Compose the BGM the user requested, matching the brief's emotional register.
  - `AudioMixAgent` — Combine the produced audio layers into a single mixed wav.
  - `TranslationAgent` — Translate the source-language subtitles into the requested target language.
  - `CompositorAgent` — Mux the final mp4, combining the rendered visual track with audio and any subtitle overlay.

## #46
**user_goal** (1123 chars):

> Here's my story I want to process: Ingrid Lin died the first time on a Tuesday afternoon at the age of thirty-four, pushed from a seventh-floor balcony by her husband of eleven years at the end of what she had only a few seconds earlier believed was an ordinary argument about money. She opened her eyes and was seventeen again. She was standing in the hallway of Westbridge Academy, where she had at... [+723 chars]

**rationale:** Cinematic mini-drama from a text brief; no overlays added. Excluded — NarratorAgent (not a slideshow / illustrated-storytelling format); StyleTransferAgent (no style transfer requested); MusicAgent (no BGM requested); IntakeImageAgent (no image upload); NarrationAgent (not a slideshow / illustrated-storytelling format); VideoExtendAgent (no video extension requested); AudioMixAgent (no audio tracks to mix); IntakeVideoAgent (no source clip uploaded); HighlightAgent (not a highlight workflow); BriefEnricherAgent (no image upload to enrich the brief with); AmbienceAgent (no environmental layer requested); TranslationAgent (no translation / second language requested); VideoAnalysisAgent (no source-video analysis required); IllustrationAgent (not a slideshow / illustrated-storytelling format); TranscriptionAgent (no subtitle requested).

**plan:**
  - `StoryAgent` — Author the story blueprint following the brief, with a clear arc and beat structure.
  - `ScreenplayAgent` — Decompose the story into scenes with mood progression aligned to the brief.
  - `KeyFrameAgent` — Lay out keyframes for the screenplay's settings, scene-by-scene.
  - `VideoAgent` — Animate each keyframe into a per-shot motion clip.
  - `CompositorAgent` — Mux the final mp4, combining the rendered visual track with audio and any subtitle overlay.

## #47
**user_goal** (85 chars):

> Please extract the funniest pet-animal moments from this 2-hour pet-vlog compilation.

**rationale:** Highlight reel from an uploaded source video; no overlays added. Excluded — IllustrationAgent (not a slideshow / illustrated-storytelling format); IntakeImageAgent (no image upload); CompositorAgent (no final mux required); VideoAgent (no NEW motion-clip generation requested); StyleTransferAgent (no style transfer requested); MusicAgent (no BGM requested); NarrationAgent (not a slideshow / illustrated-storytelling format); ScreenplayAgent (no NEW film scene-decomposition needed); VideoExtendAgent (no video extension requested); AudioMixAgent (no audio tracks to mix); TranslationAgent (no translation / second language requested); NarratorAgent (not a slideshow / illustrated-storytelling format); StoryAgent (no NEW film authoring requested); TranscriptionAgent (no subtitle requested); KeyFrameAgent (no keyframe planning required); BriefEnricherAgent (no image upload to enrich the brief with); AmbienceAgent (no environmental layer requested).

**plan:**
  - `IntakeVideoAgent` — Register the uploaded video as a captioned workspace artifact.
  - `VideoAnalysisAgent` — Analyze the source video into a scene-by-scene report (genre, mood, beats, entities).
  - `HighlightAgent` — Extract the highlight moments from the analyzed video.

## #48
**user_goal** (94 chars):

> Please extend this 6-second Polish stand-up comedy clip to 20 seconds and add Polish captions.

**rationale:** Extended video cut from an uploaded source video; overlays applied: subtitles. Excluded — IllustrationAgent (not a slideshow / illustrated-storytelling format); VideoAgent (no NEW motion-clip generation requested); StyleTransferAgent (no style transfer requested); KeyFrameAgent (no keyframe planning required); NarrationAgent (not a slideshow / illustrated-storytelling format); TranslationAgent (no translation / second language requested); HighlightAgent (not a highlight workflow); IntakeImageAgent (no image upload); BriefEnricherAgent (no image upload to enrich the brief with); ScreenplayAgent (no NEW film scene-decomposition needed); AudioMixAgent (no audio tracks to mix); StoryAgent (no NEW film authoring requested); AmbienceAgent (no environmental layer requested); NarratorAgent (not a slideshow / illustrated-storytelling format); VideoAnalysisAgent (no source-video analysis required); MusicAgent (no BGM requested).

**plan:**
  - `IntakeVideoAgent` — Ingest the uploaded video into the workspace with caption metadata.
  - `VideoExtendAgent` — Generate continuation footage extending the source video.
  - `TranscriptionAgent` — Generate the subtitle track from the dialogue audio with per-line timestamps.
  - `CompositorAgent` — Output the final mp4 by composing the video, audio, and subtitle / transition elements.

## #49
**user_goal** (85 chars):

> Extend this 4-second autumn-forest-walk clip to 12 seconds and add a celtic-harp BGM.

**rationale:** Extended video cut from an uploaded source video with BGM as the only added overlays. Reject: VideoAgent (no NEW motion-clip generation requested); NarrationAgent (not a slideshow / illustrated-storytelling format); NarratorAgent (not a slideshow / illustrated-storytelling format); IllustrationAgent (not a slideshow / illustrated-storytelling format); HighlightAgent (not a highlight workflow); TranslationAgent (no translation / second language requested); AmbienceAgent (no environmental layer requested); BriefEnricherAgent (no image upload to enrich the brief with); StyleTransferAgent (no style transfer requested); TranscriptionAgent (no subtitle requested); ScreenplayAgent (no NEW film scene-decomposition needed); IntakeImageAgent (no image upload); StoryAgent (no NEW film authoring requested); VideoAnalysisAgent (no source-video analysis required); KeyFrameAgent (no keyframe planning required).

**plan:**
  - `IntakeVideoAgent` — Ingest the uploaded video into the workspace with caption metadata.
  - `VideoExtendAgent` — Extend the source video beyond its original duration.
  - `MusicAgent` — Generate the requested BGM, scored to the brief's mood.
  - `AudioMixAgent` — Layer the available audio tracks into the final mixed wav.
  - `CompositorAgent` — Composite the final mp4 — assemble video, audio, and any subtitle / transitions into the deliverable.

## #50
**user_goal** (292 chars):

> Using this uploaded portrait of a forest-spirit child, make a bilingual English-Swedish illustrated audiobook of the folk tale where the spirit teaches children to hear trees speak, with a soft woodwind-quartet and ancient-forest ambient (wind through oaks, distant birds) under the narrator.

**rationale:** Illustrated storytelling slideshow from a text brief + uploaded reference image; overlays applied: BGM + ambient layer + bilingual narration track. Excluded — VideoAgent (no NEW motion-clip generation requested); HighlightAgent (not a highlight workflow); KeyFrameAgent (no keyframe planning required); VideoExtendAgent (no video extension requested); StoryAgent (no NEW film authoring requested); TranscriptionAgent (no subtitle requested); VideoAnalysisAgent (no source-video analysis required); StyleTransferAgent (no style transfer requested); IntakeVideoAgent (no source clip uploaded); ScreenplayAgent (no NEW film scene-decomposition needed).

**plan:**
  - `IntakeImageAgent` — Persist the uploaded image into the workspace as a captioned artifact.
  - `BriefEnricherAgent` — Fold image-reference descriptions into the brief to produce an enriched creative brief.
  - `NarrationAgent` — Author the narration script from the brief — paragraph-by-paragraph story text.
  - `IllustrationAgent` — Render one still illustration per narration paragraph.
  - `NarratorAgent` — Produce the spoken narrator track via TTS over the narration text.
  - `MusicAgent` — Compose the BGM the user requested, matching the brief's emotional register.
  - `AmbienceAgent` — Author the environmental ambient layer per the brief.
  - `AudioMixAgent` — Mix the available audio tracks into one final mixed wav.
  - `TranslationAgent` — Produce the second-language subtitle track from the source transcription.
  - `CompositorAgent` — Output the final mp4 by composing the video, audio, and subtitle / transition elements.
