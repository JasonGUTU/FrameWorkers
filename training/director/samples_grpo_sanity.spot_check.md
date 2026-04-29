# GRPO (handwritten) spot check — 30 of 30 samples

**Track B (handwritten raw_samples_grpo).** Style: with-chain flow narrative + reject list.
Sister track: samples_grpo_v1.templated.jsonl (chain-free).

---

## #1  (extend_only, grpo_handwritten, grpo_0018)
**user_goal** (137 chars):

> I have an 11-second hot-air-balloon launch clip. Could you extend it out to ~40 seconds so the balloon visibly rises higher into the sky?

**rationale:** 11-second hot-air-balloon-launch clip + extend-to-40s of continued ascent. IntakeVideoAgent loads the launch clip; VideoExtendAgent generates additional ascent frames so the balloon visibly rises higher. Raw extended clip is the deliverable — no overlay, audio, subtitle, or restyle requested.

**plan:**
  - `IntakeVideoAgent` — Ingest the 11-second hot-air-balloon launch clip into the workspace.
  - `VideoExtendAgent` — Extend the balloon-launch clip from 11 seconds out to ~40 seconds of continued ascent into the sky.

## #2  (vid_subtitle, grpo_handwritten, grpo_0027)
**user_goal** (133 chars):

> Got a gym tutorial video I shot of myself doing deadlift form. Please add English subtitles so my online clients can follow the cues.

**rationale:** User-recorded English deadlift gym tutorial + same-language English subtitle overlay. IntakeVideoAgent loads the tutorial; TranscriptionAgent transcribes the English form cues into timestamped SRT; CompositorAgent overlays the captions. Reject TranslationAgent (English-only, not bilingual), MusicAgent / AmbienceAgent / AudioMixAgent (no audio overlay), VideoAnalysisAgent / HighlightAgent (no analysis or trim), StyleTransferAgent / VideoExtendAgent (no restyle / length change).

**plan:**
  - `IntakeVideoAgent` — Ingest the deadlift gym-tutorial recording into the workspace.
  - `TranscriptionAgent` — Transcribe the English form cues into timestamped SRT lines.
  - `CompositorAgent` — Burn the English captions onto the deadlift tutorial and output the final captioned video.

## #3  (highlight_only, grpo_handwritten, grpo_0020)
**user_goal** (116 chars):

> Please extract only the elimination rounds and judge tasting moments from this 4-hour cooking competition recording.

**rationale:** 4-hour cooking competition + elimination-rounds and judge-tasting highlight only. IntakeVideoAgent loads the long recording; VideoAnalysisAgent identifies elimination announcements and judge-tasting reactions; HighlightAgent cuts those moments out as a segmented cut list. Reject CompositorAgent (raw cuts ARE the deliverable, no overlay), TranscriptionAgent / TranslationAgent (no subtitles), MusicAgent / AmbienceAgent / AudioMixAgent (no audio overlay), StyleTransferAgent / VideoExtendAgent (no restyle / length change).

**plan:**
  - `IntakeVideoAgent` — Ingest the 4-hour cooking-competition recording into the workspace.
  - `VideoAnalysisAgent` — Analyze the cooking competition to locate elimination rounds and judge-tasting moments.
  - `HighlightAgent` — Extract the elimination rounds and judge-tasting moments as highlight segments.

## #4  (vid_subtitle, grpo_handwritten, grpo_0025)
**user_goal** (144 chars):

> Add Spanish subtitles to this cooking class recording — the chef is already teaching in Spanish, I just need the captions burned onto the video.

**rationale:** Spanish-spoken cooking class + monolingual Spanish subtitle overlay. IntakeVideoAgent ingests the recording; TranscriptionAgent produces timestamped Spanish SRT segments from the chef's instruction; CompositorAgent burns the SRT onto the frames. Reject TranslationAgent (same-language ask, not bilingual), MusicAgent / AmbienceAgent / AudioMixAgent (no audio overlay), VideoAnalysisAgent / HighlightAgent (no analysis or trim), StyleTransferAgent / VideoExtendAgent (no restyle / length change).

**plan:**
  - `IntakeVideoAgent` — Ingest the Spanish-spoken cooking-class recording into the workspace.
  - `TranscriptionAgent` — Transcribe the chef's Spanish-language instruction into timestamped SRT segments.
  - `CompositorAgent` — Burn the Spanish SRT subtitles onto the cooking video and output the final captioned file.

## #5  (cr_music, grpo_handwritten, grpo_0012)
**user_goal** (159 chars):

> Make a Regency-era costume mini-drama about a poor governess who unwittingly falls for the duke whose estate she's tutoring at, with elegant chamber-music BGM.

**rationale:** Regency-era governess-and-duke costume mini-drama from a text brief + elegant chamber-music BGM. StoryAgent drafts the poor-governess / duke / estate-romance blueprint. ScreenplayAgent breaks it into Regency romance scenes. KeyFrameAgent plans keyframes for the country-estate / library-tutoring / ballroom-climax settings from text alone. VideoAgent assembles the multi-shot film. MusicAgent composes the chamber-music score. AudioMixAgent layers it under the dialogue+foley. CompositorAgent muxes the final mp4. Reject AmbienceAgent, Transcription/Translation, VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight, Narration/Illustration/Narrator.

**plan:**
  - `StoryAgent` — Draft the Regency-era costume story blueprint — governess-and-duke estate-romance arc.
  - `ScreenplayAgent` — Decompose the Regency romance arc into estate-arrival / tutoring / ballroom-confession scenes.
  - `KeyFrameAgent` — Plan keyframes for the country-estate / library-tutoring / ballroom-climax settings; text-only generation, no reference images supplied.
  - `VideoAgent` — Render per-shot clips preserving Regency-costume visual continuity across the estate-romance cuts.
  - `MusicAgent` — Compose the elegant chamber-music BGM the user requested, matching the Regency-romance register.
  - `AudioMixAgent` — Layer the chamber-music BGM under the clip's baked dialogue+foley track into one final mixed wav.
  - `CompositorAgent` — Composite the final Regency costume mini-drama mp4 with mixed audio and inter-shot transitions.

## #6  (extend_only, grpo_handwritten, grpo_0013)
**user_goal** (145 chars):

> Got a 15-second clip of jellyfish floating in an aquarium tank. Could you stretch it to about 60 seconds? Want it as a calming desk-monitor loop.

**rationale:** 15-second aquarium jellyfish clip + extend-to-60s for desk-monitor loop. IntakeVideoAgent ingests the clip; VideoExtendAgent generates additional coherent jellyfish-drift frames. Raw extended clip is the deliverable — no audio, no SRT, no restyle.

**plan:**
  - `IntakeVideoAgent` — Ingest the 15-second jellyfish aquarium clip into the workspace as the source video.
  - `VideoExtendAgent` — Extend the jellyfish clip from 15 seconds out to ~60 seconds of seamless aquarium drift footage.

## #7  (cr_music, grpo_handwritten, grpo_0008)
**user_goal** (161 chars):

> I want a 1940s film-noir detective mini-drama where a private eye investigating a senator's murder discovers his own partner is the killer — with smoky jazz BGM.

**rationale:** 1940s film-noir detective mini-drama from a text brief + smoky jazz BGM. StoryAgent drafts the private-eye / partner-as-killer-reveal blueprint. ScreenplayAgent breaks it into 1940s noir scenes. KeyFrameAgent plans keyframes for the rain-slick alley / smoke-filled office / partner-confrontation settings from text alone. VideoAgent assembles the multi-shot film. MusicAgent composes the smoky jazz score. AudioMixAgent layers it under the dialogue+foley. CompositorAgent muxes the final mp4. Reject AmbienceAgent, Transcription/Translation, VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight, Narration/Illustration/Narrator.

**plan:**
  - `StoryAgent` — Draft the 1940s film-noir story blueprint — private-eye senator-murder investigation arc with the partner-as-killer reveal.
  - `ScreenplayAgent` — Decompose the investigation arc into 1940s noir scenes with smoky-back-alley pacing.
  - `KeyFrameAgent` — Plan keyframes for the rain-slick alley / smoke-filled office / partner-confrontation settings; text-only generation, no reference images supplied.
  - `VideoAgent` — Render per-shot clips preserving 1940s noir visual continuity across the betrayal cuts.
  - `MusicAgent` — Compose the smoky jazz BGM the user requested, matching the noir-detective register.
  - `AudioMixAgent` — Layer the jazz BGM under the clip's baked dialogue+foley track into one final mixed wav.
  - `CompositorAgent` — Composite the final noir-detective mini-drama mp4 with mixed audio and inter-shot transitions.

## #8  (highlight_only, grpo_handwritten, grpo_0023)
**user_goal** (111 chars):

> Got an 8-hour video-game tournament stream archive — please cut out only the boss-kill and final-round moments.

**rationale:** 8-hour video-game tournament archive + boss-kill / final-round highlight only. IntakeVideoAgent ingests the long stream; VideoAnalysisAgent locates the boss-kill moments and final-round footage; HighlightAgent extracts those segments. Raw cut list is the deliverable. Reject CompositorAgent (no overlay), TranscriptionAgent / TranslationAgent (no subtitles), MusicAgent / AmbienceAgent / AudioMixAgent (no audio overlay), StyleTransferAgent / VideoExtendAgent (no restyle / length change).

**plan:**
  - `IntakeVideoAgent` — Ingest the 8-hour video-game tournament stream archive into the workspace.
  - `VideoAnalysisAgent` — Analyze the tournament stream to locate boss-kill and final-round moments.
  - `HighlightAgent` — Extract the boss-kill and final-round moments as highlight segments.

## #9  (story_pure, grpo_handwritten, grpo_0004)
**user_goal** (178 chars):

> Could you turn this short bedtime story I wrote about a forgetful old wizard who lost his beard into a narrated picture book? One whimsical cartoon illustration per scene please.

**rationale:** Forgetful-wizard-and-lost-beard bedtime tale + whimsical cartoon illustrations + slideshow narration.

**plan:**
  - `NarrationAgent` — Write the narration script adapted from the user's bedtime tale of the forgetful wizard.
  - `IllustrationAgent` — Generate one whimsical cartoon illustration per wizard-tale scene.
  - `NarratorAgent` — Produce a soothing TTS narrator track for the wizard bedtime story.
  - `CompositorAgent` — Compose the final illustrated bedtime audiobook pairing wizard cartoons with the narrator audio.

## #10  (extend_only, grpo_handwritten, grpo_0014)
**user_goal** (134 chars):

> I shot 8 seconds of a lava lamp on my desk. Please extend it out to a one-minute version so I can use it as a chill stream background.

**rationale:** 8-second lava-lamp clip + extend-to-60s for chill stream background. IntakeVideoAgent loads the clip; VideoExtendAgent produces additional frames preserving the slow undulating wax motion. Raw extended footage is the output — no overlay, audio, or restyle requested.

**plan:**
  - `IntakeVideoAgent` — Ingest the 8-second lava-lamp clip into the workspace.
  - `VideoExtendAgent` — Extend the lava-lamp clip from 8 seconds to ~60 seconds preserving the slow undulating wax motion.

## #11  (cr_music, grpo_handwritten, grpo_0011)
**user_goal** (170 chars):

> I want an espionage thriller mini-drama where a CIA analyst uncovers a mole inside her own task-force during a Berlin extraction op, with pulsing electronic-thriller BGM.

**rationale:** Berlin-extraction espionage thriller mini-drama from a text brief + pulsing electronic-thriller BGM. StoryAgent drafts the CIA-analyst / Berlin-op / in-task-force-mole-reveal blueprint. ScreenplayAgent breaks it into espionage scenes. KeyFrameAgent plans keyframes for the CIA-war-room / Berlin-alley-extraction / mole-confrontation settings from text alone. VideoAgent assembles the multi-shot film. MusicAgent composes the electronic-thriller score. AudioMixAgent layers it under the dialogue+foley. CompositorAgent muxes the final mp4. Reject AmbienceAgent, Transcription/Translation, VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight, Narration/Illustration/Narrator.

**plan:**
  - `StoryAgent` — Draft the espionage thriller story blueprint — CIA-analyst Berlin-extraction arc uncovering the in-task-force mole.
  - `ScreenplayAgent` — Decompose the espionage arc into briefing / Berlin-op / mole-reveal scenes.
  - `KeyFrameAgent` — Plan keyframes for the CIA-war-room / Berlin-alley-extraction / mole-confrontation-climax settings; text-only generation, no reference images supplied.
  - `VideoAgent` — Render per-shot clips preserving espionage thriller visual continuity across the extraction cuts.
  - `MusicAgent` — Compose the pulsing electronic-thriller BGM the user requested, matching the Berlin-op register.
  - `AudioMixAgent` — Layer the electronic-thriller BGM under the clip's baked dialogue+foley track into one final mixed wav.
  - `CompositorAgent` — Composite the final Berlin espionage thriller mp4 with mixed audio and inter-shot transitions.

## #12  (highlight_only, grpo_handwritten, grpo_0019)
**user_goal** (97 chars):

> I have a 3-hour NBA game recording. Please pull out just the dunks, blocks, and game-tying shots.

**rationale:** 3-hour NBA game + dunks / blocks / game-tying-shots highlight only. IntakeVideoAgent ingests the game recording; VideoAnalysisAgent surfaces the dunk, block, and game-tying-shot moments; HighlightAgent extracts those segments as a cut list. Raw highlight clips ARE the deliverable. Reject CompositorAgent (no overlay), TranscriptionAgent / TranslationAgent (no subtitles), MusicAgent / AmbienceAgent / AudioMixAgent (no audio overlay), StyleTransferAgent / VideoExtendAgent (no restyle / length change).

**plan:**
  - `IntakeVideoAgent` — Ingest the 3-hour NBA game recording into the workspace.
  - `VideoAnalysisAgent` — Analyze the NBA game to locate dunks, blocks, and game-tying-shot moments.
  - `HighlightAgent` — Extract the dunks, blocks, and game-tying shots as a highlight-segment cut list.

## #13  (highlight_only, grpo_handwritten, grpo_0022)
**user_goal** (178 chars):

> Please pull just the keynote-question moments out of this 6-hour academic conference recording — speakers were asked questions after their talks, I want only those Q&A exchanges.

**rationale:** 6-hour academic conference + post-talk Q&A-exchange highlight only. IntakeVideoAgent ingests the conference recording; VideoAnalysisAgent identifies the post-talk Q&A exchanges between speakers and audience; HighlightAgent extracts those exchanges as cut segments. Raw segmented Q&A cuts are the final deliverable. Reject CompositorAgent (no overlay), TranscriptionAgent / TranslationAgent (no subtitle ask), MusicAgent / AmbienceAgent / AudioMixAgent (no BGM / ambient / mix asked), StyleTransferAgent / VideoExtendAgent (no restyle / length change).

**plan:**
  - `IntakeVideoAgent` — Ingest the 6-hour academic-conference recording into the workspace.
  - `VideoAnalysisAgent` — Analyze the conference recording to locate post-talk Q&A exchanges.
  - `HighlightAgent` — Extract the keynote-question Q&A exchanges as highlight segments.

## #14  (extend_only, grpo_handwritten, grpo_0015)
**user_goal** (126 chars):

> Here's a 12-second time-lapse of city traffic at dusk — please grow it to roughly 45 seconds, keeping the same flow direction.

**rationale:** 12-second dusk city-traffic time-lapse + extend-to-45s preserving flow direction. IntakeVideoAgent ingests the clip; VideoExtendAgent generates additional frames continuing the same vehicular flow. Raw extended clip is the deliverable.

**plan:**
  - `IntakeVideoAgent` — Ingest the 12-second dusk city-traffic time-lapse into the workspace as the source video.
  - `VideoExtendAgent` — Extend the dusk-traffic time-lapse from 12 seconds to ~45 seconds keeping the original flow direction.

## #15  (story_pure, grpo_handwritten, grpo_0001)
**user_goal** (191 chars):

> Make an illustrated audiobook of this West African Anansi-the-spider folktale about how Anansi tricked the sky god to bring stories to humans, with one warm earth-tone illustration per scene.

**rationale:** West African Anansi-and-sky-god folktale + warm earth-tone illustrations + slideshow narration.

**plan:**
  - `NarrationAgent` — Write the narration script from the West African Anansi-and-sky-god folktale.
  - `IllustrationAgent` — Generate one warm earth-tone illustration per Anansi-folktale scene.
  - `NarratorAgent` — Produce a measured TTS narrator track for the Anansi folktale.
  - `CompositorAgent` — Compose the final slideshow pairing earth-tone Anansi illustrations with the narrator audio.

## #16  (story_pure, grpo_handwritten, grpo_0002)
**user_goal** (161 chars):

> Make a children's nature picture-book video about how humpback whales migrate from Alaska to Hawaii every year — one watercolor illustration per migration stage.

**rationale:** Humpback-whale Alaska-to-Hawaii migration storytime + watercolor illustrations + slideshow narration.

**plan:**
  - `NarrationAgent` — Write the narration script tracing humpback whale migration from Alaska to Hawaii.
  - `IllustrationAgent` — Generate one watercolor illustration per whale-migration stage.
  - `NarratorAgent` — Produce a friendly TTS narrator track for the whale-migration story.
  - `CompositorAgent` — Compose the final picture-book slideshow pairing whale-migration watercolors with the narrator audio.

## #17  (vid_subtitle, grpo_handwritten, grpo_0029)
**user_goal** (104 chars):

> I have a French-language travel vlog from my Provence trip. Add French captions to it for accessibility.

**rationale:** French-language Provence travel vlog + French accessibility-caption overlay in the same language. IntakeVideoAgent ingests the vlog; TranscriptionAgent produces timestamped French SRT segments from the narration; CompositorAgent burns the captions onto the video. Reject TranslationAgent (single-language ask), MusicAgent / AmbienceAgent / AudioMixAgent (no audio overlay), VideoAnalysisAgent / HighlightAgent (no trim or content analysis), StyleTransferAgent / VideoExtendAgent (no restyle / length change).

**plan:**
  - `IntakeVideoAgent` — Ingest the French-language Provence travel vlog into the workspace.
  - `TranscriptionAgent` — Transcribe the French narration into timestamped accessibility-caption segments.
  - `CompositorAgent` — Burn the French captions onto the travel vlog and output the final captioned file.

## #18  (highlight_only, grpo_handwritten, grpo_0021)
**user_goal** (120 chars):

> I have a 2-hour fashion-week runway show recording. Can you pull only the finale walk and designer takes-a-bow segments?

**rationale:** 2-hour fashion-week runway show + finale-walk and designer-bow highlight only. IntakeVideoAgent ingests the show; VideoAnalysisAgent locates the finale-walk and designer-bow moments; HighlightAgent extracts those segments. Raw highlight clips are the deliverable. Reject CompositorAgent (no overlay), TranscriptionAgent / TranslationAgent (no subtitles), MusicAgent / AmbienceAgent / AudioMixAgent (no audio overlay), StyleTransferAgent / VideoExtendAgent (no restyle / length change).

**plan:**
  - `IntakeVideoAgent` — Ingest the 2-hour fashion-week runway show recording into the workspace.
  - `VideoAnalysisAgent` — Analyze the runway show to locate the finale walk and designer-bow moments.
  - `HighlightAgent` — Extract the finale walk and designer-bow moments as highlight segments.

## #19  (cr_music, grpo_handwritten, grpo_0009)
**user_goal** (164 chars):

> Produce a sci-fi survival mini-drama about the last botanist on a dying Mars colony racing to engineer crops before the dome fails, with synth-driven cinematic BGM.

**rationale:** Sci-fi survival Mars-botanist mini-drama from a text brief + synth-driven cinematic BGM. StoryAgent drafts the last-botanist / dying-Mars-colony / dome-failure blueprint. ScreenplayAgent breaks it into Mars-survival scenes. KeyFrameAgent plans keyframes for the failing-greenhouse-dome / Martian-dust-storm / lab-climax settings from text alone. VideoAgent assembles the multi-shot film. MusicAgent composes the synth cinematic score. AudioMixAgent layers it under the dialogue+foley. CompositorAgent muxes the final mp4. Reject AmbienceAgent, Transcription/Translation, VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight, Narration/Illustration/Narrator.

**plan:**
  - `StoryAgent` — Draft the sci-fi survival story blueprint — last-Mars-botanist dome-failure crop-engineering race.
  - `ScreenplayAgent` — Decompose the survival arc into Mars-colony scenes with desperate-deadline pacing.
  - `KeyFrameAgent` — Plan keyframes for the failing-greenhouse-dome / Martian-dust-storm / lab-climax settings; text-only generation, no reference images supplied.
  - `VideoAgent` — Render per-shot clips preserving sci-fi survival visual continuity across the dome-deterioration cuts.
  - `MusicAgent` — Compose the synth-driven cinematic BGM the user requested, matching the dying-colony register.
  - `AudioMixAgent` — Layer the synth BGM under the clip's baked dialogue+foley track into one final mixed wav.
  - `CompositorAgent` — Composite the final Mars-survival mini-drama mp4 with mixed audio and inter-shot transitions.

## #20  (extend_only, grpo_handwritten, grpo_0016)
**user_goal** (127 chars):

> 10-second clip of a campfire crackling, can you make it about 2 minutes long? It's for a relaxation video I'm putting together.

**rationale:** 10-second campfire-crackling clip + extend-to-2-minutes for a separate relaxation video the user is assembling elsewhere. IntakeVideoAgent ingests the source; VideoExtendAgent grows the clip to ~120 seconds preserving the flame motion. Raw extended footage is the final asset — no compositor, audio, or subtitle work requested here.

**plan:**
  - `IntakeVideoAgent` — Ingest the 10-second campfire-crackling clip into the workspace.
  - `VideoExtendAgent` — Extend the campfire clip from 10 seconds out to ~2 minutes of continuous crackling-flames footage.

## #21  (vid_subtitle, grpo_handwritten, grpo_0028)
**user_goal** (136 chars):

> Please add Mandarin subtitles to this DIY craft tutorial I filmed. The host speaks Mandarin throughout, I just need the words on screen.

**rationale:** Mandarin-spoken DIY craft tutorial + same-language Mandarin subtitle overlay. IntakeVideoAgent ingests the tutorial; TranscriptionAgent transcribes the Mandarin host narration into timestamped SRT; CompositorAgent burns the Mandarin captions onto the frames. Reject TranslationAgent (no bilingual ask), MusicAgent / AmbienceAgent / AudioMixAgent (no audio overlay), HighlightAgent / VideoAnalysisAgent (no trim), StyleTransferAgent / VideoExtendAgent (no restyle / length change).

**plan:**
  - `IntakeVideoAgent` — Ingest the Mandarin DIY craft tutorial into the workspace.
  - `TranscriptionAgent` — Transcribe the Mandarin host narration into timestamped SRT segments.
  - `CompositorAgent` — Burn the Mandarin captions onto the craft tutorial and deliver the final captioned video.

## #22  (vid_subtitle, grpo_handwritten, grpo_0026)
**user_goal** (114 chars):

> I recorded a 90-minute podcast interview, please add English captions to it. Same language, no translation needed.

**rationale:** 90-minute English-spoken podcast interview + monolingual English captions. IntakeVideoAgent loads the recording; TranscriptionAgent produces timestamped English SRT lines; CompositorAgent burns the captions onto the video. Reject TranslationAgent (no bilingual ask), HighlightAgent / VideoAnalysisAgent (full interview wanted, not trimmed), MusicAgent / AmbienceAgent / AudioMixAgent (no audio overlay), StyleTransferAgent / VideoExtendAgent (no restyle / length change).

**plan:**
  - `IntakeVideoAgent` — Ingest the 90-minute podcast interview recording into the workspace.
  - `TranscriptionAgent` — Transcribe the English podcast dialogue into timestamped caption segments.
  - `CompositorAgent` — Burn the English captions onto the podcast video and deliver the captioned final cut.

## #23  (vid_subtitle, grpo_handwritten, grpo_0030)
**user_goal** (123 chars):

> Add English captions to this 5-minute startup pitch I recorded for the demo day. Just the captions burned in, nothing else.

**rationale:** 5-minute English-spoken startup pitch + English captions burned in. IntakeVideoAgent loads the pitch recording; TranscriptionAgent transcribes the English pitch speech into timestamped SRT; CompositorAgent burns the captions onto the frames. Reject TranslationAgent (single language asked), HighlightAgent / VideoAnalysisAgent (full pitch wanted, not trimmed), MusicAgent / AmbienceAgent / AudioMixAgent (no BGM / ambient / audio mixing), StyleTransferAgent / VideoExtendAgent (user explicitly said 'nothing else').

**plan:**
  - `IntakeVideoAgent` — Ingest the 5-minute startup-pitch recording into the workspace.
  - `TranscriptionAgent` — Transcribe the English pitch speech into timestamped caption segments.
  - `CompositorAgent` — Burn the English captions onto the pitch video and output the final captioned demo file.

## #24  (cr_music, grpo_handwritten, grpo_0007)
**user_goal** (157 chars):

> Make a K-pop industry mini-drama about a small-town backup dancer who replaces the injured main star at a Seoul concert, with high-energy electronic-pop BGM.

**rationale:** K-pop industry mini-drama from a text brief + high-energy electronic-pop BGM. StoryAgent drafts the small-town backup-dancer / Seoul-substitution blueprint. ScreenplayAgent breaks it into K-pop industry scenes. KeyFrameAgent plans keyframes for the practice-studio / backstage / Seoul-stadium-stage settings from text alone. VideoAgent assembles the multi-shot film. MusicAgent composes the electronic-pop score. AudioMixAgent layers it under the dialogue+foley. CompositorAgent muxes the final mp4. Reject AmbienceAgent, Transcription/Translation, VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight, Narration/Illustration/Narrator.

**plan:**
  - `StoryAgent` — Draft the K-pop industry story blueprint — small-town backup-dancer last-minute substitution arc at the Seoul concert.
  - `ScreenplayAgent` — Decompose the substitution arc into K-pop industry scenes with rehearsal-to-stage pacing.
  - `KeyFrameAgent` — Plan keyframes for the practice-studio / backstage / Seoul-stadium-stage settings; text-only generation, no reference images supplied.
  - `VideoAgent` — Render per-shot clips preserving K-pop industry visual continuity across the substitution cuts.
  - `MusicAgent` — Compose the high-energy electronic-pop BGM the user requested, matching the K-pop concert register.
  - `AudioMixAgent` — Layer the electronic-pop BGM under the clip's baked dialogue+foley track into one final mixed wav.
  - `CompositorAgent` — Composite the final K-pop mini-drama mp4 with mixed audio and inter-shot transitions.

## #25  (story_pure, grpo_handwritten, grpo_0006)
**user_goal** (177 chars):

> Turn this short essay about my grandmother's immigration journey from Vietnam to California in the 1970s into an illustrated narration with sepia-toned drawings, one per memory.

**rationale:** Vietnam-to-California grandmother immigration memoir + sepia-toned illustrations + slideshow narration.

**plan:**
  - `NarrationAgent` — Write the narration script adapted from the grandmother's Vietnam-to-California immigration essay.
  - `IllustrationAgent` — Generate one sepia-toned illustration per memory in the immigration journey.
  - `NarratorAgent` — Produce a tender TTS narrator track for the immigration memoir.
  - `CompositorAgent` — Compose the final memoir slideshow pairing sepia immigration drawings with the narrator audio.

## #26  (story_pure, grpo_handwritten, grpo_0005)
**user_goal** (173 chars):

> Make a slideshow audiobook of this Japanese folktale about Issun-bōshi the one-inch boy who fights an oni with his needle sword — one ukiyo-e style illustration per chapter.

**rationale:** Japanese Issun-bōshi one-inch-boy folktale + ukiyo-e illustrations + slideshow narration.

**plan:**
  - `NarrationAgent` — Write the narration script from the Japanese Issun-bōshi one-inch-boy folktale.
  - `IllustrationAgent` — Generate one ukiyo-e style illustration per Issun-bōshi chapter.
  - `NarratorAgent` — Produce a measured TTS narrator track for the Issun-bōshi folktale.
  - `CompositorAgent` — Compose the final slideshow pairing ukiyo-e Issun-bōshi illustrations with the narrator audio.

## #27  (highlight_only, grpo_handwritten, grpo_0024)
**user_goal** (119 chars):

> Pull just the headlining-act moments and crowd singalong segments from this 5-hour music festival main-stage recording.

**rationale:** 5-hour music festival main-stage + headlining-act and crowd-singalong highlight only. IntakeVideoAgent ingests the stage recording; VideoAnalysisAgent identifies the headlining-act performance segments and crowd-singalong moments; HighlightAgent cuts those out. Raw cut clips are the deliverable. Reject CompositorAgent (no overlay), MusicAgent / AmbienceAgent / AudioMixAgent (no audio overlay needed — original festival audio is preserved by the highlight cuts themselves), TranscriptionAgent / TranslationAgent (no subtitle ask), StyleTransferAgent / VideoExtendAgent (no restyle / length change).

**plan:**
  - `IntakeVideoAgent` — Ingest the 5-hour music-festival main-stage recording into the workspace.
  - `VideoAnalysisAgent` — Analyze the festival recording to locate headlining-act performances and crowd-singalong moments.
  - `HighlightAgent` — Extract the headlining-act and crowd-singalong moments as highlight segments.

## #28  (cr_music, grpo_handwritten, grpo_0010)
**user_goal** (203 chars):

> Make a time-travel romance mini-drama where a 21st-century museum curator falls for a Tang-dynasty poet she keeps meeting on accidental trips through a haunted scroll, with sweeping romantic strings BGM.

**rationale:** Time-travel Tang-dynasty romance mini-drama from a text brief + sweeping romantic-strings BGM. StoryAgent drafts the museum-curator / Tang-poet / haunted-scroll blueprint. ScreenplayAgent breaks it into time-travel romance scenes. KeyFrameAgent plans keyframes for the museum-scroll-room / Tang-dynasty-courtyard / romantic-climax settings from text alone. VideoAgent assembles the multi-shot film. MusicAgent composes the romantic-strings score. AudioMixAgent layers it under the dialogue+foley. CompositorAgent muxes the final mp4. Reject AmbienceAgent, Transcription/Translation, VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight, Narration/Illustration/Narrator.

**plan:**
  - `StoryAgent` — Draft the time-travel romance story blueprint — 21st-century museum-curator and Tang-dynasty-poet bond arc via the haunted scroll.
  - `ScreenplayAgent` — Decompose the time-travel romance arc into modern-museum / accidental-trip / Tang-encounter scenes.
  - `KeyFrameAgent` — Plan keyframes for the museum-scroll-room / Tang-dynasty-courtyard / romantic-climax settings; text-only generation, no reference images supplied.
  - `VideoAgent` — Render per-shot clips preserving time-travel romance visual continuity across the era-shift cuts.
  - `MusicAgent` — Compose the sweeping romantic-strings BGM the user requested, matching the curator/Tang-poet bond register.
  - `AudioMixAgent` — Layer the romantic-strings BGM under the clip's baked dialogue+foley track into one final mixed wav.
  - `CompositorAgent` — Composite the final time-travel romance mini-drama mp4 with mixed audio and inter-shot transitions.

## #29  (extend_only, grpo_handwritten, grpo_0017)
**user_goal** (102 chars):

> Short 7-second clip of snow falling on pine branches — please extend to 30 seconds for a winter intro.

**rationale:** 7-second snow-on-pines clip + extend-to-30s for a winter intro. IntakeVideoAgent loads the clip; VideoExtendAgent produces ~23 more seconds of coherent snowfall frames. Output is the raw extended clip — no overlay, audio, or subtitle work requested.

**plan:**
  - `IntakeVideoAgent` — Ingest the 7-second snow-falling-on-pine-branches clip into the workspace.
  - `VideoExtendAgent` — Extend the snow-on-pines clip from 7 seconds to ~30 seconds of continuous snowfall.

## #30  (story_pure, grpo_handwritten, grpo_0003)
**user_goal** (173 chars):

> Read this Norse myth about Thor's stolen hammer and his journey disguised as a bride to recover it — show one bold woodcut-style illustration per plot beat, slideshow style.

**rationale:** Norse Thor-stolen-hammer-and-bride-disguise myth + bold woodcut-style illustrations + slideshow narration.

**plan:**
  - `NarrationAgent` — Write the narration script from the Norse myth of Thor's stolen hammer and bride disguise.
  - `IllustrationAgent` — Generate one bold woodcut-style illustration per plot beat in the Thor myth.
  - `NarratorAgent` — Produce a dramatic TTS narrator track for the Thor-stolen-hammer myth.
  - `CompositorAgent` — Compose the final slideshow pairing woodcut Thor illustrations with the narrator audio.
