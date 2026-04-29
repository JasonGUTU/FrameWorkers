# GRPO (templated) spot check — 30 of 30 samples

**Track A (templated chain-free).** Variation: 3 rationale skeletons × per-sample shuffled reject list × 3 intent variants per agent (md5-hash picked).
Sister track: samples_grpo_v1.jsonl (with-chain flow narrative).

---

## #1  (extend_only, grpo_templated, grpo_tmpl_0018)
**user_goal** (137 chars):

> I have an 11-second hot-air-balloon launch clip. Could you extend it out to ~40 seconds so the balloon visibly rises higher into the sky?

**rationale:** Extended video cut from an uploaded source video with no audio / subtitle overlays. Reject: ScreenplayAgent (no NEW film scene-decomposition needed); NarrationAgent (not a slideshow / illustrated-storytelling format); HighlightAgent (not a highlight workflow); AudioMixAgent (no audio tracks to mix); VideoAgent (no NEW motion-clip generation requested); BriefEnricherAgent (no image upload to enrich the brief with); StyleTransferAgent (no style transfer requested); MusicAgent (no BGM requested); StoryAgent (no NEW film authoring requested); NarratorAgent (not a slideshow / illustrated-storytelling format); VideoAnalysisAgent (no source-video analysis required); TranscriptionAgent (no subtitle requested); IntakeImageAgent (no image upload); AmbienceAgent (no environmental layer requested); KeyFrameAgent (no keyframe planning required); TranslationAgent (no translation / second language requested); IllustrationAgent (not a slideshow / illustrated-storytelling format); CompositorAgent (no final mux required).

**plan:**
  - `IntakeVideoAgent` — Register the uploaded video as a captioned workspace artifact.
  - `VideoExtendAgent` — Produce extended footage that continues the source video.

## #2  (vid_subtitle, grpo_templated, grpo_tmpl_0027)
**user_goal** (133 chars):

> Got a gym tutorial video I shot of myself doing deadlift form. Please add English subtitles so my online clients can follow the cues.

**rationale:** Modified video cut from an uploaded source video with subtitles as the only added overlays. Reject: VideoAnalysisAgent (no source-video analysis required); MusicAgent (no BGM requested); AudioMixAgent (no audio tracks to mix); VideoExtendAgent (no video extension requested); NarrationAgent (not a slideshow / illustrated-storytelling format); ScreenplayAgent (no NEW film scene-decomposition needed); StyleTransferAgent (no style transfer requested); VideoAgent (no NEW motion-clip generation requested); AmbienceAgent (no environmental layer requested); HighlightAgent (not a highlight workflow); BriefEnricherAgent (no image upload to enrich the brief with); IllustrationAgent (not a slideshow / illustrated-storytelling format); TranslationAgent (no translation / second language requested); IntakeImageAgent (no image upload); KeyFrameAgent (no keyframe planning required); StoryAgent (no NEW film authoring requested); NarratorAgent (not a slideshow / illustrated-storytelling format).

**plan:**
  - `IntakeVideoAgent` — Register the uploaded video as a captioned workspace artifact.
  - `TranscriptionAgent` — Generate the subtitle track from the dialogue audio with per-line timestamps.
  - `CompositorAgent` — Mux the final mp4, combining the rendered visual track with audio and any subtitle overlay.

## #3  (highlight_only, grpo_templated, grpo_tmpl_0020)
**user_goal** (116 chars):

> Please extract only the elimination rounds and judge tasting moments from this 4-hour cooking competition recording.

**rationale:** Highlight reel from an uploaded source video; no overlays added. Excluded — NarratorAgent (not a slideshow / illustrated-storytelling format); StoryAgent (no NEW film authoring requested); TranscriptionAgent (no subtitle requested); TranslationAgent (no translation / second language requested); KeyFrameAgent (no keyframe planning required); ScreenplayAgent (no NEW film scene-decomposition needed); StyleTransferAgent (no style transfer requested); IllustrationAgent (not a slideshow / illustrated-storytelling format); AmbienceAgent (no environmental layer requested); NarrationAgent (not a slideshow / illustrated-storytelling format); VideoExtendAgent (no video extension requested); VideoAgent (no NEW motion-clip generation requested); BriefEnricherAgent (no image upload to enrich the brief with); AudioMixAgent (no audio tracks to mix); CompositorAgent (no final mux required); MusicAgent (no BGM requested); IntakeImageAgent (no image upload).

**plan:**
  - `IntakeVideoAgent` — Register the uploaded video as a captioned workspace artifact.
  - `VideoAnalysisAgent` — Generate a structured scene-level report of the source video.
  - `HighlightAgent` — Select the highlight segments from the analyzed source video.

## #4  (vid_subtitle, grpo_templated, grpo_tmpl_0025)
**user_goal** (144 chars):

> Add Spanish subtitles to this cooking class recording — the chef is already teaching in Spanish, I just need the captions burned onto the video.

**rationale:** Modified video cut produced from an uploaded source video, layered with subtitles. Skipped: StyleTransferAgent (no style transfer requested); BriefEnricherAgent (no image upload to enrich the brief with); IntakeImageAgent (no image upload); NarrationAgent (not a slideshow / illustrated-storytelling format); AudioMixAgent (no audio tracks to mix); VideoAnalysisAgent (no source-video analysis required); HighlightAgent (not a highlight workflow); ScreenplayAgent (no NEW film scene-decomposition needed); VideoExtendAgent (no video extension requested); StoryAgent (no NEW film authoring requested); VideoAgent (no NEW motion-clip generation requested); AmbienceAgent (no environmental layer requested); NarratorAgent (not a slideshow / illustrated-storytelling format); TranslationAgent (no translation / second language requested); KeyFrameAgent (no keyframe planning required); IllustrationAgent (not a slideshow / illustrated-storytelling format); MusicAgent (no BGM requested).

**plan:**
  - `IntakeVideoAgent` — Ingest the uploaded video into the workspace with caption metadata.
  - `TranscriptionAgent` — Generate the subtitle track from the dialogue audio with per-line timestamps.
  - `CompositorAgent` — Output the final mp4 by composing the video, audio, and subtitle / transition elements.

## #5  (cr_music, grpo_templated, grpo_tmpl_0012)
**user_goal** (159 chars):

> Make a Regency-era costume mini-drama about a poor governess who unwittingly falls for the duke whose estate she's tutoring at, with elegant chamber-music BGM.

**rationale:** Cinematic mini-drama from a text brief with BGM as the only added overlays. Reject: IllustrationAgent (not a slideshow / illustrated-storytelling format); TranscriptionAgent (no subtitle requested); VideoExtendAgent (no video extension requested); HighlightAgent (not a highlight workflow); NarrationAgent (not a slideshow / illustrated-storytelling format); StyleTransferAgent (no style transfer requested); BriefEnricherAgent (no image upload to enrich the brief with); NarratorAgent (not a slideshow / illustrated-storytelling format); IntakeVideoAgent (no source clip uploaded); TranslationAgent (no translation / second language requested); AmbienceAgent (no environmental layer requested); VideoAnalysisAgent (no source-video analysis required); IntakeImageAgent (no image upload).

**plan:**
  - `StoryAgent` — Draft the story blueprint from the brief — character arc and act structure.
  - `ScreenplayAgent` — Break the drafted story into scene-by-scene units, preserving the brief's tonal register.
  - `KeyFrameAgent` — Design keyframes from the screenplay scene by scene.
  - `VideoAgent` — Produce per-shot video clips from each keyframe, holding aesthetic continuity across cuts.
  - `MusicAgent` — Write the requested BGM, aligned to the brief's tonal cue.
  - `AudioMixAgent` — Combine the produced audio layers into a single mixed wav.
  - `CompositorAgent` — Mux the final mp4, combining the rendered visual track with audio and any subtitle overlay.

## #6  (extend_only, grpo_templated, grpo_tmpl_0013)
**user_goal** (145 chars):

> Got a 15-second clip of jellyfish floating in an aquarium tank. Could you stretch it to about 60 seconds? Want it as a calming desk-monitor loop.

**rationale:** Extended video cut produced from an uploaded source video, nothing layered on top. Skipped: IntakeImageAgent (no image upload); AudioMixAgent (no audio tracks to mix); IllustrationAgent (not a slideshow / illustrated-storytelling format); TranslationAgent (no translation / second language requested); StoryAgent (no NEW film authoring requested); NarratorAgent (not a slideshow / illustrated-storytelling format); StyleTransferAgent (no style transfer requested); KeyFrameAgent (no keyframe planning required); AmbienceAgent (no environmental layer requested); HighlightAgent (not a highlight workflow); TranscriptionAgent (no subtitle requested); VideoAgent (no NEW motion-clip generation requested); BriefEnricherAgent (no image upload to enrich the brief with); CompositorAgent (no final mux required); ScreenplayAgent (no NEW film scene-decomposition needed); MusicAgent (no BGM requested); NarrationAgent (not a slideshow / illustrated-storytelling format); VideoAnalysisAgent (no source-video analysis required).

**plan:**
  - `IntakeVideoAgent` — Persist the uploaded video into the workspace as a captioned artifact.
  - `VideoExtendAgent` — Generate continuation footage extending the source video.

## #7  (cr_music, grpo_templated, grpo_tmpl_0008)
**user_goal** (161 chars):

> I want a 1940s film-noir detective mini-drama where a private eye investigating a senator's murder discovers his own partner is the killer — with smoky jazz BGM.

**rationale:** Cinematic mini-drama from a text brief with BGM as the only added overlays. Reject: IntakeVideoAgent (no source clip uploaded); TranslationAgent (no translation / second language requested); HighlightAgent (not a highlight workflow); TranscriptionAgent (no subtitle requested); AmbienceAgent (no environmental layer requested); IllustrationAgent (not a slideshow / illustrated-storytelling format); NarratorAgent (not a slideshow / illustrated-storytelling format); StyleTransferAgent (no style transfer requested); BriefEnricherAgent (no image upload to enrich the brief with); VideoAnalysisAgent (no source-video analysis required); VideoExtendAgent (no video extension requested); IntakeImageAgent (no image upload); NarrationAgent (not a slideshow / illustrated-storytelling format).

**plan:**
  - `StoryAgent` — Draft the story blueprint from the brief — character arc and act structure.
  - `ScreenplayAgent` — Convert the story into a scene-by-scene screenplay matching the brief's register.
  - `KeyFrameAgent` — Design keyframes from the screenplay scene by scene.
  - `VideoAgent` — Animate each keyframe into a per-shot motion clip.
  - `MusicAgent` — Write the requested BGM, aligned to the brief's tonal cue.
  - `AudioMixAgent` — Mix the available audio tracks into one final mixed wav.
  - `CompositorAgent` — Mux the final mp4, combining the rendered visual track with audio and any subtitle overlay.

## #8  (highlight_only, grpo_templated, grpo_tmpl_0023)
**user_goal** (111 chars):

> Got an 8-hour video-game tournament stream archive — please cut out only the boss-kill and final-round moments.

**rationale:** Highlight reel produced from an uploaded source video, nothing layered on top. Skipped: KeyFrameAgent (no keyframe planning required); NarratorAgent (not a slideshow / illustrated-storytelling format); VideoExtendAgent (no video extension requested); IllustrationAgent (not a slideshow / illustrated-storytelling format); TranslationAgent (no translation / second language requested); AudioMixAgent (no audio tracks to mix); TranscriptionAgent (no subtitle requested); VideoAgent (no NEW motion-clip generation requested); MusicAgent (no BGM requested); StoryAgent (no NEW film authoring requested); StyleTransferAgent (no style transfer requested); NarrationAgent (not a slideshow / illustrated-storytelling format); IntakeImageAgent (no image upload); ScreenplayAgent (no NEW film scene-decomposition needed); BriefEnricherAgent (no image upload to enrich the brief with); AmbienceAgent (no environmental layer requested); CompositorAgent (no final mux required).

**plan:**
  - `IntakeVideoAgent` — Ingest the uploaded video into the workspace with caption metadata.
  - `VideoAnalysisAgent` — Analyze the source video into a scene-by-scene report (genre, mood, beats, entities).
  - `HighlightAgent` — Extract the highlight moments from the analyzed video.

## #9  (story_pure, grpo_templated, grpo_tmpl_0004)
**user_goal** (178 chars):

> Could you turn this short bedtime story I wrote about a forgetful old wizard who lost his beard into a narrated picture book? One whimsical cartoon illustration per scene please.

**rationale:** Illustrated storytelling slideshow from a text brief; no overlays added. Excluded — VideoAgent (no NEW motion-clip generation requested); StyleTransferAgent (no style transfer requested); HighlightAgent (not a highlight workflow); VideoAnalysisAgent (no source-video analysis required); IntakeImageAgent (no image upload); IntakeVideoAgent (no source clip uploaded); KeyFrameAgent (no keyframe planning required); VideoExtendAgent (no video extension requested); StoryAgent (no NEW film authoring requested); ScreenplayAgent (no NEW film scene-decomposition needed); BriefEnricherAgent (no image upload to enrich the brief with); MusicAgent (no BGM requested); AmbienceAgent (no environmental layer requested); AudioMixAgent (no audio tracks to mix); TranscriptionAgent (no subtitle requested); TranslationAgent (no translation / second language requested).

**plan:**
  - `NarrationAgent` — Author the narration script from the brief — paragraph-by-paragraph story text.
  - `IllustrationAgent` — Render one still illustration per narration paragraph.
  - `NarratorAgent` — Synthesize the narrator audio track from the narration script.
  - `CompositorAgent` — Output the final mp4 by composing the video, audio, and subtitle / transition elements.

## #10  (extend_only, grpo_templated, grpo_tmpl_0014)
**user_goal** (134 chars):

> I shot 8 seconds of a lava lamp on my desk. Please extend it out to a one-minute version so I can use it as a chill stream background.

**rationale:** Extended video cut produced from an uploaded source video, nothing layered on top. Skipped: BriefEnricherAgent (no image upload to enrich the brief with); NarratorAgent (not a slideshow / illustrated-storytelling format); StoryAgent (no NEW film authoring requested); TranscriptionAgent (no subtitle requested); KeyFrameAgent (no keyframe planning required); IntakeImageAgent (no image upload); IllustrationAgent (not a slideshow / illustrated-storytelling format); TranslationAgent (no translation / second language requested); VideoAnalysisAgent (no source-video analysis required); StyleTransferAgent (no style transfer requested); CompositorAgent (no final mux required); MusicAgent (no BGM requested); HighlightAgent (not a highlight workflow); AudioMixAgent (no audio tracks to mix); VideoAgent (no NEW motion-clip generation requested); ScreenplayAgent (no NEW film scene-decomposition needed); NarrationAgent (not a slideshow / illustrated-storytelling format); AmbienceAgent (no environmental layer requested).

**plan:**
  - `IntakeVideoAgent` — Ingest the uploaded video into the workspace with caption metadata.
  - `VideoExtendAgent` — Produce extended footage that continues the source video.

## #11  (cr_music, grpo_templated, grpo_tmpl_0011)
**user_goal** (170 chars):

> I want an espionage thriller mini-drama where a CIA analyst uncovers a mole inside her own task-force during a Berlin extraction op, with pulsing electronic-thriller BGM.

**rationale:** Cinematic mini-drama produced from a text brief, layered with BGM. Skipped: BriefEnricherAgent (no image upload to enrich the brief with); NarratorAgent (not a slideshow / illustrated-storytelling format); VideoAnalysisAgent (no source-video analysis required); StyleTransferAgent (no style transfer requested); IllustrationAgent (not a slideshow / illustrated-storytelling format); TranslationAgent (no translation / second language requested); VideoExtendAgent (no video extension requested); IntakeVideoAgent (no source clip uploaded); AmbienceAgent (no environmental layer requested); HighlightAgent (not a highlight workflow); TranscriptionAgent (no subtitle requested); NarrationAgent (not a slideshow / illustrated-storytelling format); IntakeImageAgent (no image upload).

**plan:**
  - `StoryAgent` — Outline the story blueprint per the brief — protagonist arc and pivot beats.
  - `ScreenplayAgent` — Decompose the story into scenes with mood progression aligned to the brief.
  - `KeyFrameAgent` — Lay out keyframes for the screenplay's settings, scene-by-scene.
  - `VideoAgent` — Render per-shot motion clips from the keyframes, preserving visual continuity.
  - `MusicAgent` — Write the requested BGM, aligned to the brief's tonal cue.
  - `AudioMixAgent` — Mix the available audio tracks into one final mixed wav.
  - `CompositorAgent` — Output the final mp4 by composing the video, audio, and subtitle / transition elements.

## #12  (highlight_only, grpo_templated, grpo_tmpl_0019)
**user_goal** (97 chars):

> I have a 3-hour NBA game recording. Please pull out just the dunks, blocks, and game-tying shots.

**rationale:** Highlight reel from an uploaded source video with no audio / subtitle overlays. Reject: MusicAgent (no BGM requested); VideoExtendAgent (no video extension requested); IntakeImageAgent (no image upload); KeyFrameAgent (no keyframe planning required); TranscriptionAgent (no subtitle requested); IllustrationAgent (not a slideshow / illustrated-storytelling format); NarrationAgent (not a slideshow / illustrated-storytelling format); AudioMixAgent (no audio tracks to mix); StoryAgent (no NEW film authoring requested); CompositorAgent (no final mux required); BriefEnricherAgent (no image upload to enrich the brief with); ScreenplayAgent (no NEW film scene-decomposition needed); TranslationAgent (no translation / second language requested); NarratorAgent (not a slideshow / illustrated-storytelling format); VideoAgent (no NEW motion-clip generation requested); AmbienceAgent (no environmental layer requested); StyleTransferAgent (no style transfer requested).

**plan:**
  - `IntakeVideoAgent` — Register the uploaded video as a captioned workspace artifact.
  - `VideoAnalysisAgent` — Produce a scene-level analysis report of the source video for downstream reasoning.
  - `HighlightAgent` — Pick the top highlight clips from the source video using the analysis report.

## #13  (highlight_only, grpo_templated, grpo_tmpl_0022)
**user_goal** (178 chars):

> Please pull just the keynote-question moments out of this 6-hour academic conference recording — speakers were asked questions after their talks, I want only those Q&A exchanges.

**rationale:** Highlight reel produced from an uploaded source video, nothing layered on top. Skipped: ScreenplayAgent (no NEW film scene-decomposition needed); TranslationAgent (no translation / second language requested); NarrationAgent (not a slideshow / illustrated-storytelling format); VideoAgent (no NEW motion-clip generation requested); StoryAgent (no NEW film authoring requested); KeyFrameAgent (no keyframe planning required); TranscriptionAgent (no subtitle requested); BriefEnricherAgent (no image upload to enrich the brief with); MusicAgent (no BGM requested); AudioMixAgent (no audio tracks to mix); AmbienceAgent (no environmental layer requested); IntakeImageAgent (no image upload); NarratorAgent (not a slideshow / illustrated-storytelling format); StyleTransferAgent (no style transfer requested); IllustrationAgent (not a slideshow / illustrated-storytelling format); VideoExtendAgent (no video extension requested); CompositorAgent (no final mux required).

**plan:**
  - `IntakeVideoAgent` — Persist the uploaded video into the workspace as a captioned artifact.
  - `VideoAnalysisAgent` — Generate a structured scene-level report of the source video.
  - `HighlightAgent` — Select the highlight segments from the analyzed source video.

## #14  (extend_only, grpo_templated, grpo_tmpl_0015)
**user_goal** (126 chars):

> Here's a 12-second time-lapse of city traffic at dusk — please grow it to roughly 45 seconds, keeping the same flow direction.

**rationale:** Extended video cut from an uploaded source video with no audio / subtitle overlays. Reject: KeyFrameAgent (no keyframe planning required); AudioMixAgent (no audio tracks to mix); IntakeImageAgent (no image upload); VideoAgent (no NEW motion-clip generation requested); MusicAgent (no BGM requested); StyleTransferAgent (no style transfer requested); VideoAnalysisAgent (no source-video analysis required); BriefEnricherAgent (no image upload to enrich the brief with); NarrationAgent (not a slideshow / illustrated-storytelling format); StoryAgent (no NEW film authoring requested); TranscriptionAgent (no subtitle requested); TranslationAgent (no translation / second language requested); HighlightAgent (not a highlight workflow); ScreenplayAgent (no NEW film scene-decomposition needed); AmbienceAgent (no environmental layer requested); NarratorAgent (not a slideshow / illustrated-storytelling format); CompositorAgent (no final mux required); IllustrationAgent (not a slideshow / illustrated-storytelling format).

**plan:**
  - `IntakeVideoAgent` — Register the uploaded video as a captioned workspace artifact.
  - `VideoExtendAgent` — Extend the source video beyond its original duration.

## #15  (story_pure, grpo_templated, grpo_tmpl_0001)
**user_goal** (191 chars):

> Make an illustrated audiobook of this West African Anansi-the-spider folktale about how Anansi tricked the sky god to bring stories to humans, with one warm earth-tone illustration per scene.

**rationale:** Illustrated storytelling slideshow produced from a text brief, nothing layered on top. Skipped: VideoAnalysisAgent (no source-video analysis required); StyleTransferAgent (no style transfer requested); VideoAgent (no NEW motion-clip generation requested); AudioMixAgent (no audio tracks to mix); VideoExtendAgent (no video extension requested); AmbienceAgent (no environmental layer requested); ScreenplayAgent (no NEW film scene-decomposition needed); KeyFrameAgent (no keyframe planning required); StoryAgent (no NEW film authoring requested); IntakeImageAgent (no image upload); HighlightAgent (not a highlight workflow); IntakeVideoAgent (no source clip uploaded); TranslationAgent (no translation / second language requested); MusicAgent (no BGM requested); TranscriptionAgent (no subtitle requested); BriefEnricherAgent (no image upload to enrich the brief with).

**plan:**
  - `NarrationAgent` — Draft the narration script per the brief, paragraph-by-paragraph.
  - `IllustrationAgent` — Render one still illustration per narration paragraph.
  - `NarratorAgent` — Produce the spoken narrator track via TTS over the narration text.
  - `CompositorAgent` — Output the final mp4 by composing the video, audio, and subtitle / transition elements.

## #16  (story_pure, grpo_templated, grpo_tmpl_0002)
**user_goal** (161 chars):

> Make a children's nature picture-book video about how humpback whales migrate from Alaska to Hawaii every year — one watercolor illustration per migration stage.

**rationale:** Illustrated storytelling slideshow from a text brief with no audio / subtitle overlays. Reject: StoryAgent (no NEW film authoring requested); TranscriptionAgent (no subtitle requested); VideoAnalysisAgent (no source-video analysis required); VideoExtendAgent (no video extension requested); VideoAgent (no NEW motion-clip generation requested); IntakeVideoAgent (no source clip uploaded); AudioMixAgent (no audio tracks to mix); BriefEnricherAgent (no image upload to enrich the brief with); MusicAgent (no BGM requested); HighlightAgent (not a highlight workflow); TranslationAgent (no translation / second language requested); StyleTransferAgent (no style transfer requested); AmbienceAgent (no environmental layer requested); IntakeImageAgent (no image upload); ScreenplayAgent (no NEW film scene-decomposition needed); KeyFrameAgent (no keyframe planning required).

**plan:**
  - `NarrationAgent` — Draft the narration script per the brief, paragraph-by-paragraph.
  - `IllustrationAgent` — Render one still illustration per narration paragraph.
  - `NarratorAgent` — Produce the spoken narrator track via TTS over the narration text.
  - `CompositorAgent` — Mux the final mp4, combining the rendered visual track with audio and any subtitle overlay.

## #17  (vid_subtitle, grpo_templated, grpo_tmpl_0029)
**user_goal** (104 chars):

> I have a French-language travel vlog from my Provence trip. Add French captions to it for accessibility.

**rationale:** Modified video cut from an uploaded source video with subtitles as the only added overlays. Reject: VideoAnalysisAgent (no source-video analysis required); StyleTransferAgent (no style transfer requested); MusicAgent (no BGM requested); ScreenplayAgent (no NEW film scene-decomposition needed); NarrationAgent (not a slideshow / illustrated-storytelling format); StoryAgent (no NEW film authoring requested); AudioMixAgent (no audio tracks to mix); BriefEnricherAgent (no image upload to enrich the brief with); IllustrationAgent (not a slideshow / illustrated-storytelling format); VideoAgent (no NEW motion-clip generation requested); NarratorAgent (not a slideshow / illustrated-storytelling format); IntakeImageAgent (no image upload); TranslationAgent (no translation / second language requested); AmbienceAgent (no environmental layer requested); KeyFrameAgent (no keyframe planning required); VideoExtendAgent (no video extension requested); HighlightAgent (not a highlight workflow).

**plan:**
  - `IntakeVideoAgent` — Persist the uploaded video into the workspace as a captioned artifact.
  - `TranscriptionAgent` — Transcribe the spoken dialogue into a timestamped subtitle track.
  - `CompositorAgent` — Output the final mp4 by composing the video, audio, and subtitle / transition elements.

## #18  (highlight_only, grpo_templated, grpo_tmpl_0021)
**user_goal** (120 chars):

> I have a 2-hour fashion-week runway show recording. Can you pull only the finale walk and designer takes-a-bow segments?

**rationale:** Highlight reel from an uploaded source video; no overlays added. Excluded — VideoExtendAgent (no video extension requested); AudioMixAgent (no audio tracks to mix); IntakeImageAgent (no image upload); TranscriptionAgent (no subtitle requested); KeyFrameAgent (no keyframe planning required); AmbienceAgent (no environmental layer requested); IllustrationAgent (not a slideshow / illustrated-storytelling format); NarratorAgent (not a slideshow / illustrated-storytelling format); ScreenplayAgent (no NEW film scene-decomposition needed); VideoAgent (no NEW motion-clip generation requested); NarrationAgent (not a slideshow / illustrated-storytelling format); MusicAgent (no BGM requested); CompositorAgent (no final mux required); TranslationAgent (no translation / second language requested); StyleTransferAgent (no style transfer requested); StoryAgent (no NEW film authoring requested); BriefEnricherAgent (no image upload to enrich the brief with).

**plan:**
  - `IntakeVideoAgent` — Persist the uploaded video into the workspace as a captioned artifact.
  - `VideoAnalysisAgent` — Produce a scene-level analysis report of the source video for downstream reasoning.
  - `HighlightAgent` — Extract the highlight moments from the analyzed video.

## #19  (cr_music, grpo_templated, grpo_tmpl_0009)
**user_goal** (164 chars):

> Produce a sci-fi survival mini-drama about the last botanist on a dying Mars colony racing to engineer crops before the dome fails, with synth-driven cinematic BGM.

**rationale:** Cinematic mini-drama from a text brief; overlays applied: BGM. Excluded — BriefEnricherAgent (no image upload to enrich the brief with); IntakeImageAgent (no image upload); IntakeVideoAgent (no source clip uploaded); AmbienceAgent (no environmental layer requested); VideoExtendAgent (no video extension requested); TranslationAgent (no translation / second language requested); IllustrationAgent (not a slideshow / illustrated-storytelling format); VideoAnalysisAgent (no source-video analysis required); NarratorAgent (not a slideshow / illustrated-storytelling format); NarrationAgent (not a slideshow / illustrated-storytelling format); TranscriptionAgent (no subtitle requested); StyleTransferAgent (no style transfer requested); HighlightAgent (not a highlight workflow).

**plan:**
  - `StoryAgent` — Draft the story blueprint from the brief — character arc and act structure.
  - `ScreenplayAgent` — Convert the story into a scene-by-scene screenplay matching the brief's register.
  - `KeyFrameAgent` — Plan keyframes for the screenplay's settings, one per scene.
  - `VideoAgent` — Produce per-shot video clips from each keyframe, holding aesthetic continuity across cuts.
  - `MusicAgent` — Write the requested BGM, aligned to the brief's tonal cue.
  - `AudioMixAgent` — Layer the available audio tracks into the final mixed wav.
  - `CompositorAgent` — Output the final mp4 by composing the video, audio, and subtitle / transition elements.

## #20  (extend_only, grpo_templated, grpo_tmpl_0016)
**user_goal** (127 chars):

> 10-second clip of a campfire crackling, can you make it about 2 minutes long? It's for a relaxation video I'm putting together.

**rationale:** Extended video cut from an uploaded source video with no audio / subtitle overlays. Reject: HighlightAgent (not a highlight workflow); IllustrationAgent (not a slideshow / illustrated-storytelling format); ScreenplayAgent (no NEW film scene-decomposition needed); TranslationAgent (no translation / second language requested); BriefEnricherAgent (no image upload to enrich the brief with); NarratorAgent (not a slideshow / illustrated-storytelling format); IntakeImageAgent (no image upload); KeyFrameAgent (no keyframe planning required); VideoAnalysisAgent (no source-video analysis required); CompositorAgent (no final mux required); TranscriptionAgent (no subtitle requested); StoryAgent (no NEW film authoring requested); StyleTransferAgent (no style transfer requested); AudioMixAgent (no audio tracks to mix); NarrationAgent (not a slideshow / illustrated-storytelling format); MusicAgent (no BGM requested); AmbienceAgent (no environmental layer requested); VideoAgent (no NEW motion-clip generation requested).

**plan:**
  - `IntakeVideoAgent` — Persist the uploaded video into the workspace as a captioned artifact.
  - `VideoExtendAgent` — Generate continuation footage extending the source video.

## #21  (vid_subtitle, grpo_templated, grpo_tmpl_0028)
**user_goal** (136 chars):

> Please add Mandarin subtitles to this DIY craft tutorial I filmed. The host speaks Mandarin throughout, I just need the words on screen.

**rationale:** Modified video cut from an uploaded source video; overlays applied: subtitles. Excluded — AmbienceAgent (no environmental layer requested); IntakeImageAgent (no image upload); AudioMixAgent (no audio tracks to mix); StoryAgent (no NEW film authoring requested); IllustrationAgent (not a slideshow / illustrated-storytelling format); HighlightAgent (not a highlight workflow); MusicAgent (no BGM requested); KeyFrameAgent (no keyframe planning required); BriefEnricherAgent (no image upload to enrich the brief with); NarrationAgent (not a slideshow / illustrated-storytelling format); VideoExtendAgent (no video extension requested); TranslationAgent (no translation / second language requested); StyleTransferAgent (no style transfer requested); NarratorAgent (not a slideshow / illustrated-storytelling format); VideoAnalysisAgent (no source-video analysis required); ScreenplayAgent (no NEW film scene-decomposition needed); VideoAgent (no NEW motion-clip generation requested).

**plan:**
  - `IntakeVideoAgent` — Register the uploaded video as a captioned workspace artifact.
  - `TranscriptionAgent` — Generate the subtitle track from the dialogue audio with per-line timestamps.
  - `CompositorAgent` — Output the final mp4 by composing the video, audio, and subtitle / transition elements.

## #22  (vid_subtitle, grpo_templated, grpo_tmpl_0026)
**user_goal** (114 chars):

> I recorded a 90-minute podcast interview, please add English captions to it. Same language, no translation needed.

**rationale:** Modified video cut from an uploaded source video; overlays applied: subtitles. Excluded — VideoAgent (no NEW motion-clip generation requested); TranslationAgent (no translation / second language requested); MusicAgent (no BGM requested); VideoExtendAgent (no video extension requested); IllustrationAgent (not a slideshow / illustrated-storytelling format); BriefEnricherAgent (no image upload to enrich the brief with); KeyFrameAgent (no keyframe planning required); IntakeImageAgent (no image upload); NarrationAgent (not a slideshow / illustrated-storytelling format); NarratorAgent (not a slideshow / illustrated-storytelling format); StyleTransferAgent (no style transfer requested); AudioMixAgent (no audio tracks to mix); HighlightAgent (not a highlight workflow); StoryAgent (no NEW film authoring requested); VideoAnalysisAgent (no source-video analysis required); ScreenplayAgent (no NEW film scene-decomposition needed); AmbienceAgent (no environmental layer requested).

**plan:**
  - `IntakeVideoAgent` — Ingest the uploaded video into the workspace with caption metadata.
  - `TranscriptionAgent` — Transcribe the spoken dialogue into a timestamped subtitle track.
  - `CompositorAgent` — Mux the final mp4, combining the rendered visual track with audio and any subtitle overlay.

## #23  (vid_subtitle, grpo_templated, grpo_tmpl_0030)
**user_goal** (123 chars):

> Add English captions to this 5-minute startup pitch I recorded for the demo day. Just the captions burned in, nothing else.

**rationale:** Modified video cut from an uploaded source video; overlays applied: subtitles. Excluded — VideoAnalysisAgent (no source-video analysis required); IntakeImageAgent (no image upload); StoryAgent (no NEW film authoring requested); AudioMixAgent (no audio tracks to mix); BriefEnricherAgent (no image upload to enrich the brief with); VideoAgent (no NEW motion-clip generation requested); MusicAgent (no BGM requested); NarrationAgent (not a slideshow / illustrated-storytelling format); NarratorAgent (not a slideshow / illustrated-storytelling format); IllustrationAgent (not a slideshow / illustrated-storytelling format); TranslationAgent (no translation / second language requested); AmbienceAgent (no environmental layer requested); KeyFrameAgent (no keyframe planning required); HighlightAgent (not a highlight workflow); ScreenplayAgent (no NEW film scene-decomposition needed); VideoExtendAgent (no video extension requested); StyleTransferAgent (no style transfer requested).

**plan:**
  - `IntakeVideoAgent` — Persist the uploaded video into the workspace as a captioned artifact.
  - `TranscriptionAgent` — Author the timestamped transcription of the spoken dialogue.
  - `CompositorAgent` — Mux the final mp4, combining the rendered visual track with audio and any subtitle overlay.

## #24  (cr_music, grpo_templated, grpo_tmpl_0007)
**user_goal** (157 chars):

> Make a K-pop industry mini-drama about a small-town backup dancer who replaces the injured main star at a Seoul concert, with high-energy electronic-pop BGM.

**rationale:** Cinematic mini-drama from a text brief with BGM as the only added overlays. Reject: StyleTransferAgent (no style transfer requested); IllustrationAgent (not a slideshow / illustrated-storytelling format); NarratorAgent (not a slideshow / illustrated-storytelling format); BriefEnricherAgent (no image upload to enrich the brief with); AmbienceAgent (no environmental layer requested); IntakeImageAgent (no image upload); TranslationAgent (no translation / second language requested); IntakeVideoAgent (no source clip uploaded); TranscriptionAgent (no subtitle requested); VideoExtendAgent (no video extension requested); NarrationAgent (not a slideshow / illustrated-storytelling format); VideoAnalysisAgent (no source-video analysis required); HighlightAgent (not a highlight workflow).

**plan:**
  - `StoryAgent` — Author the story blueprint following the brief, with a clear arc and beat structure.
  - `ScreenplayAgent` — Decompose the story into scenes with mood progression aligned to the brief.
  - `KeyFrameAgent` — Plan keyframes for the screenplay's settings, one per scene.
  - `VideoAgent` — Render per-shot motion clips from the keyframes, preserving visual continuity.
  - `MusicAgent` — Compose the BGM the user requested, matching the brief's emotional register.
  - `AudioMixAgent` — Layer the available audio tracks into the final mixed wav.
  - `CompositorAgent` — Output the final mp4 by composing the video, audio, and subtitle / transition elements.

## #25  (story_pure, grpo_templated, grpo_tmpl_0006)
**user_goal** (177 chars):

> Turn this short essay about my grandmother's immigration journey from Vietnam to California in the 1970s into an illustrated narration with sepia-toned drawings, one per memory.

**rationale:** Illustrated storytelling slideshow produced from a text brief, nothing layered on top. Skipped: HighlightAgent (not a highlight workflow); ScreenplayAgent (no NEW film scene-decomposition needed); AudioMixAgent (no audio tracks to mix); TranslationAgent (no translation / second language requested); IntakeVideoAgent (no source clip uploaded); VideoExtendAgent (no video extension requested); VideoAgent (no NEW motion-clip generation requested); TranscriptionAgent (no subtitle requested); VideoAnalysisAgent (no source-video analysis required); StyleTransferAgent (no style transfer requested); IntakeImageAgent (no image upload); MusicAgent (no BGM requested); StoryAgent (no NEW film authoring requested); BriefEnricherAgent (no image upload to enrich the brief with); AmbienceAgent (no environmental layer requested); KeyFrameAgent (no keyframe planning required).

**plan:**
  - `NarrationAgent` — Author the narration script from the brief — paragraph-by-paragraph story text.
  - `IllustrationAgent` — Produce per-paragraph illustrations matching the narration.
  - `NarratorAgent` — Generate the TTS narrator audio track from the narration script.
  - `CompositorAgent` — Mux the final mp4, combining the rendered visual track with audio and any subtitle overlay.

## #26  (story_pure, grpo_templated, grpo_tmpl_0005)
**user_goal** (173 chars):

> Make a slideshow audiobook of this Japanese folktale about Issun-bōshi the one-inch boy who fights an oni with his needle sword — one ukiyo-e style illustration per chapter.

**rationale:** Illustrated storytelling slideshow from a text brief with no audio / subtitle overlays. Reject: VideoAgent (no NEW motion-clip generation requested); IntakeImageAgent (no image upload); TranscriptionAgent (no subtitle requested); StyleTransferAgent (no style transfer requested); KeyFrameAgent (no keyframe planning required); StoryAgent (no NEW film authoring requested); BriefEnricherAgent (no image upload to enrich the brief with); MusicAgent (no BGM requested); AudioMixAgent (no audio tracks to mix); VideoAnalysisAgent (no source-video analysis required); AmbienceAgent (no environmental layer requested); IntakeVideoAgent (no source clip uploaded); TranslationAgent (no translation / second language requested); VideoExtendAgent (no video extension requested); HighlightAgent (not a highlight workflow); ScreenplayAgent (no NEW film scene-decomposition needed).

**plan:**
  - `NarrationAgent` — Author the narration script from the brief — paragraph-by-paragraph story text.
  - `IllustrationAgent` — Generate one illustration image per paragraph of the narration.
  - `NarratorAgent` — Synthesize the narrator audio track from the narration script.
  - `CompositorAgent` — Mux the final mp4, combining the rendered visual track with audio and any subtitle overlay.

## #27  (highlight_only, grpo_templated, grpo_tmpl_0024)
**user_goal** (119 chars):

> Pull just the headlining-act moments and crowd singalong segments from this 5-hour music festival main-stage recording.

**rationale:** Highlight reel from an uploaded source video with no audio / subtitle overlays. Reject: VideoExtendAgent (no video extension requested); NarrationAgent (not a slideshow / illustrated-storytelling format); CompositorAgent (no final mux required); KeyFrameAgent (no keyframe planning required); ScreenplayAgent (no NEW film scene-decomposition needed); AudioMixAgent (no audio tracks to mix); BriefEnricherAgent (no image upload to enrich the brief with); NarratorAgent (not a slideshow / illustrated-storytelling format); VideoAgent (no NEW motion-clip generation requested); TranscriptionAgent (no subtitle requested); MusicAgent (no BGM requested); StyleTransferAgent (no style transfer requested); IllustrationAgent (not a slideshow / illustrated-storytelling format); IntakeImageAgent (no image upload); TranslationAgent (no translation / second language requested); AmbienceAgent (no environmental layer requested); StoryAgent (no NEW film authoring requested).

**plan:**
  - `IntakeVideoAgent` — Ingest the uploaded video into the workspace with caption metadata.
  - `VideoAnalysisAgent` — Analyze the source video into a scene-by-scene report (genre, mood, beats, entities).
  - `HighlightAgent` — Select the highlight segments from the analyzed source video.

## #28  (cr_music, grpo_templated, grpo_tmpl_0010)
**user_goal** (203 chars):

> Make a time-travel romance mini-drama where a 21st-century museum curator falls for a Tang-dynasty poet she keeps meeting on accidental trips through a haunted scroll, with sweeping romantic strings BGM.

**rationale:** Cinematic mini-drama produced from a text brief, layered with BGM. Skipped: IllustrationAgent (not a slideshow / illustrated-storytelling format); AmbienceAgent (no environmental layer requested); TranslationAgent (no translation / second language requested); VideoAnalysisAgent (no source-video analysis required); VideoExtendAgent (no video extension requested); NarrationAgent (not a slideshow / illustrated-storytelling format); BriefEnricherAgent (no image upload to enrich the brief with); TranscriptionAgent (no subtitle requested); HighlightAgent (not a highlight workflow); IntakeImageAgent (no image upload); NarratorAgent (not a slideshow / illustrated-storytelling format); IntakeVideoAgent (no source clip uploaded); StyleTransferAgent (no style transfer requested).

**plan:**
  - `StoryAgent` — Outline the story blueprint per the brief — protagonist arc and pivot beats.
  - `ScreenplayAgent` — Decompose the story into scenes with mood progression aligned to the brief.
  - `KeyFrameAgent` — Plan keyframes for the screenplay's settings, one per scene.
  - `VideoAgent` — Animate each keyframe into a per-shot motion clip.
  - `MusicAgent` — Generate the requested BGM, scored to the brief's mood.
  - `AudioMixAgent` — Layer the available audio tracks into the final mixed wav.
  - `CompositorAgent` — Composite the final mp4 — assemble video, audio, and any subtitle / transitions into the deliverable.

## #29  (extend_only, grpo_templated, grpo_tmpl_0017)
**user_goal** (102 chars):

> Short 7-second clip of snow falling on pine branches — please extend to 30 seconds for a winter intro.

**rationale:** Extended video cut produced from an uploaded source video, nothing layered on top. Skipped: KeyFrameAgent (no keyframe planning required); HighlightAgent (not a highlight workflow); NarrationAgent (not a slideshow / illustrated-storytelling format); BriefEnricherAgent (no image upload to enrich the brief with); VideoAnalysisAgent (no source-video analysis required); MusicAgent (no BGM requested); VideoAgent (no NEW motion-clip generation requested); TranslationAgent (no translation / second language requested); AudioMixAgent (no audio tracks to mix); TranscriptionAgent (no subtitle requested); CompositorAgent (no final mux required); IntakeImageAgent (no image upload); NarratorAgent (not a slideshow / illustrated-storytelling format); StoryAgent (no NEW film authoring requested); IllustrationAgent (not a slideshow / illustrated-storytelling format); ScreenplayAgent (no NEW film scene-decomposition needed); AmbienceAgent (no environmental layer requested); StyleTransferAgent (no style transfer requested).

**plan:**
  - `IntakeVideoAgent` — Register the uploaded video as a captioned workspace artifact.
  - `VideoExtendAgent` — Produce extended footage that continues the source video.

## #30  (story_pure, grpo_templated, grpo_tmpl_0003)
**user_goal** (173 chars):

> Read this Norse myth about Thor's stolen hammer and his journey disguised as a bride to recover it — show one bold woodcut-style illustration per plot beat, slideshow style.

**rationale:** Illustrated storytelling slideshow from a text brief; no overlays added. Excluded — AudioMixAgent (no audio tracks to mix); TranscriptionAgent (no subtitle requested); VideoAgent (no NEW motion-clip generation requested); IntakeVideoAgent (no source clip uploaded); StoryAgent (no NEW film authoring requested); VideoAnalysisAgent (no source-video analysis required); HighlightAgent (not a highlight workflow); TranslationAgent (no translation / second language requested); IntakeImageAgent (no image upload); ScreenplayAgent (no NEW film scene-decomposition needed); StyleTransferAgent (no style transfer requested); BriefEnricherAgent (no image upload to enrich the brief with); VideoExtendAgent (no video extension requested); KeyFrameAgent (no keyframe planning required); MusicAgent (no BGM requested); AmbienceAgent (no environmental layer requested).

**plan:**
  - `NarrationAgent` — Author the narration script from the brief — paragraph-by-paragraph story text.
  - `IllustrationAgent` — Render one still illustration per narration paragraph.
  - `NarratorAgent` — Synthesize the narrator audio track from the narration script.
  - `CompositorAgent` — Composite the final mp4 — assemble video, audio, and any subtitle / transitions into the deliverable.
