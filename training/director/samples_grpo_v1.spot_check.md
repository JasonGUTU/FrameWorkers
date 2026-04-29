# GRPO (handwritten) spot check — 30 of 1375 samples

**Track B (handwritten raw_samples_grpo).** Style: with-chain flow narrative + reject list.
Sister track: samples_grpo_v1.templated.jsonl (chain-free).

---

## #1  (story_music_bilingual, grpo_handwritten, grpo_1336)
**user_goal** (168 chars):

> Make an illustrated bedtime audiobook of a forest-rabbit tale with soft watercolor illustrations and soft-piano lullaby BGM, narrated in Spanish with English subtitles.

**rationale:** Bilingual bedtime forest-tale + soft watercolor illustrations + slideshow narration with soft-piano lullaby BGM and Spanish-and-English bilingual subtitles.

**plan:**
  - `NarrationAgent` — Write the narration script from the forest-rabbit bedtime tale.
  - `IllustrationAgent` — Generate one soft watercolor illustration per forest-rabbit bedtime tale scene.
  - `NarratorAgent` — Produce a measured Spanish TTS narrator track for the forest-rabbit bedtime tale.
  - `MusicAgent` — Compose the soft-piano lullaby BGM the user requested.
  - `AudioMixAgent` — Layer the soft-piano lullaby BGM under the narrator track into one final mixed wav.
  - `TranslationAgent` — Translate the Spanish narrator track into English for the second-language subtitle overlay.
  - `CompositorAgent` — Compose the final slideshow pairing soft watercolor illustrations with mixed narrator-and-BGM audio and bilingual Spanish-and-English subtitles overlaid.

## #2  (cr_bilingual, grpo_handwritten, grpo_0315)
**user_goal** (154 chars):

> Produce an Argentine pampas-rancher mini-drama about a young gaucha refusing the drought-buyout offer — Argentine-Spanish dialogue with English subtitles.

**rationale:** Argentine pampas-rancher mini-drama from a text brief + Argentine Spanish-and-English bilingual subtitles. StoryAgent drafts the young-gaucha / drought / land-baron-confrontation blueprint. ScreenplayAgent breaks it into Argentine pampas-rancher scenes. KeyFrameAgent plans keyframes for the ranch homestead / dry pampa / land-baron's estancia settings from text alone. VideoAgent assembles the multi-shot film. TranscriptionAgent extracts Argentine Spanish subtitles from the dialogue. TranslationAgent renders English subtitles from the Argentine Spanish track. CompositorAgent muxes the final mp4 with bilingual subtitle overlay. Reject VideoAnalysisAgent / IntakeVideoAgent / StyleTransferAgent / VideoExtendAgent / HighlightAgent (no video uploaded), NarrationAgent / IllustrationAgent / NarratorAgent (not a slideshow / illustrated-storytelling format). Chain: Story → Screenplay → KeyFrame → Video → Transcription → Translation → Compositor → done.

**plan:**
  - `StoryAgent` — Draft the Argentine pampas-rancher story blueprint — young-gaucha / drought / land-baron-confrontation arc.
  - `ScreenplayAgent` — Decompose the young-gaucha / drought / land-baron-confrontation arc into Argentine pampas-rancher scenes.
  - `KeyFrameAgent` — Plan keyframes for the ranch homestead / dry pampa / land-baron's estancia settings; text-only generation, no reference images supplied.
  - `VideoAgent` — Render per-shot clips preserving Argentine pampas-rancher visual continuity.
  - `TranscriptionAgent` — Transcribe the Argentine Spanish dialogue into timestamped source-language subtitle segments.
  - `TranslationAgent` — Translate the Argentine Spanish subtitle track into English as the second-language overlay.
  - `CompositorAgent` — Composite the final Argentine pampas-rancher mini-drama mp4 with mixed audio and bilingual Argentine Spanish-and-English subtitles overlaid.

## #3  (extend_only, grpo_handwritten, grpo_0429)
**user_goal** (118 chars):

> Got a 7-second clip of a plane taking off down a runway. Extend to ~25 seconds with the climb continuing into the sky.

**rationale:** 7-second plane-takeoff clip + extend-to-25s with continuing climb. IntakeVideoAgent loads the clip; VideoExtendAgent generates additional frames of the plane's ascent. Output is the raw extended footage.

**plan:**
  - `IntakeVideoAgent` — Ingest the 7-second plane-takeoff clip into the workspace.
  - `VideoExtendAgent` — Extend the plane-takeoff footage from 7 seconds to ~25 seconds with the climb continuing into the sky.

## #4  (style_only, grpo_handwritten, grpo_0503)
**user_goal** (76 chars):

> Apply a Salvador-Dalí surrealist style transfer to my coastal drone footage.

**rationale:** coastal drone footage clip + Salvador-Dalí surrealist style-transfer request. Raw style-transferred output is the deliverable — no audio overlay, no subtitle, no length change.

**plan:**
  - `IntakeVideoAgent` — Ingest the user's uploaded coastal drone footage clip into the workspace.
  - `StyleTransferAgent` — Apply Salvador-Dalí surrealist style transfer to the coastal drone footage clip and output the restyled video.

## #5  (cr_compositor_only, grpo_handwritten, grpo_0034)
**user_goal** (186 chars):

> Produce a forensic mini-drama about a scientist reopening her grandmother's unsolved 1972 case using techniques that didn't exist then — and walking into the suspect's still-living door.

**rationale:** Forensic-scientist cold-case mini-drama from a text brief, no audio overlay. StoryAgent drafts the forensic-scientist / decades-old cold-case / decisive-evidence blueprint. ScreenplayAgent breaks it into forensic cold-case scenes. KeyFrameAgent plans keyframes for the forensic lab / archive evidence-vault / suspect-confrontation interview room settings from text alone. VideoAgent assembles the multi-shot film. CompositorAgent muxes the final mp4 with inter-shot transitions. Reject MusicAgent / AmbienceAgent / AudioMixAgent (no audio overlay requested), TranscriptionAgent / TranslationAgent (no subtitles), VideoAnalysisAgent / IntakeVideoAgent / StyleTransferAgent / VideoExtendAgent / HighlightAgent (no video uploaded), NarrationAgent / IllustrationAgent / NarratorAgent (not a slideshow / illustrated-storytelling format).

**plan:**
  - `StoryAgent` — Draft the Forensic-scientist cold-case story blueprint — forensic-scientist / decades-old cold-case / decisive-evidence arc.
  - `ScreenplayAgent` — Decompose the forensic-scientist / decades-old cold-case / decisive-evidence arc into forensic cold-case scenes.
  - `KeyFrameAgent` — Plan keyframes for the forensic lab / archive evidence-vault / suspect-confrontation interview room settings; text-only generation, no reference images supplied.
  - `VideoAgent` — Render per-shot clips preserving forensic cold-case visual continuity.
  - `CompositorAgent` — Composite the final forensic cold-case mini-drama mp4 with inter-shot transitions.

## #6  (cr_bilingual, grpo_handwritten, grpo_0321)
**user_goal** (172 chars):

> Produce a Bhutanese archery-festival mini-drama about a young girl shooting in the royal festival against the men's-only archers — Dzongkha dialogue with English subtitles.

**rationale:** Bhutanese archery-festival mini-drama from a text brief + Dzongkha-and-English bilingual subtitles. StoryAgent drafts the young-archer-girl / royal-archery festival / final-arrow standoff blueprint. ScreenplayAgent breaks it into Bhutanese archery-festival scenes. KeyFrameAgent plans keyframes for the village archery field / royal-pavilion / final-target line settings from text alone. VideoAgent assembles the multi-shot film. TranscriptionAgent extracts Dzongkha subtitles from the dialogue. TranslationAgent renders English subtitles from the Dzongkha track. CompositorAgent muxes the final mp4 with bilingual subtitle overlay. Reject VideoAnalysisAgent / IntakeVideoAgent / StyleTransferAgent / VideoExtendAgent / HighlightAgent (no video uploaded), NarrationAgent / IllustrationAgent / NarratorAgent (not a slideshow / illustrated-storytelling format). Chain: Story → Screenplay → KeyFrame → Video → Transcription → Translation → Compositor → done.

**plan:**
  - `StoryAgent` — Draft the Bhutanese archery-festival story blueprint — young-archer-girl / royal-archery festival / final-arrow standoff arc.
  - `ScreenplayAgent` — Decompose the young-archer-girl / royal-archery festival / final-arrow standoff arc into Bhutanese archery-festival scenes.
  - `KeyFrameAgent` — Plan keyframes for the village archery field / royal-pavilion / final-target line settings; text-only generation, no reference images supplied.
  - `VideoAgent` — Render per-shot clips preserving Bhutanese archery-festival visual continuity.
  - `TranscriptionAgent` — Transcribe the Dzongkha dialogue into timestamped source-language subtitle segments.
  - `TranslationAgent` — Translate the Dzongkha subtitle track into English as the second-language overlay.
  - `CompositorAgent` — Composite the final Bhutanese archery-festival mini-drama mp4 with mixed audio and bilingual Dzongkha-and-English subtitles overlaid.

## #7  (cr_compositor_only, grpo_handwritten, grpo_0036)
**user_goal** (189 chars):

> Produce a redemption mini-drama about a surgeon who lost her license after a malpractice scandal, volunteers in a war-zone clinic, and saves a life that costs her former accuser everything.

**rationale:** War-zone redemption surgeon mini-drama from a text brief, no audio overlay. StoryAgent drafts the disgraced-surgeon / volunteer-clinic in-war-zone / final-surgery-redemption blueprint. ScreenplayAgent breaks it into war-zone surgeon scenes. KeyFrameAgent plans keyframes for the bombed clinic / front-line tent / city under shellfire settings from text alone. VideoAgent assembles the multi-shot film. CompositorAgent muxes the final mp4 with inter-shot transitions. Reject MusicAgent / AmbienceAgent / AudioMixAgent (no audio overlay requested), TranscriptionAgent / TranslationAgent (no subtitles), VideoAnalysisAgent / IntakeVideoAgent / StyleTransferAgent / VideoExtendAgent / HighlightAgent (no video uploaded), NarrationAgent / IllustrationAgent / NarratorAgent (not a slideshow / illustrated-storytelling format).

**plan:**
  - `StoryAgent` — Draft the War-zone redemption surgeon story blueprint — disgraced-surgeon / volunteer-clinic in-war-zone / final-surgery-redemption arc.
  - `ScreenplayAgent` — Decompose the disgraced-surgeon / volunteer-clinic in-war-zone / final-surgery-redemption arc into war-zone surgeon scenes.
  - `KeyFrameAgent` — Plan keyframes for the bombed clinic / front-line tent / city under shellfire settings; text-only generation, no reference images supplied.
  - `VideoAgent` — Render per-shot clips preserving war-zone surgeon visual continuity.
  - `CompositorAgent` — Composite the final war-zone surgeon mini-drama mp4 with inter-shot transitions.

## #8  (highlight_subtitle, grpo_handwritten, grpo_0983)
**user_goal** (95 chars):

> Pull just the guest-performance segments from my Mandarin variety show with Mandarin subtitles.

**rationale:** Mandarin variety show + guest-performance highlight + same-language Mandarin subtitles. Reject MusicAgent / AmbienceAgent / AudioMixAgent (no audio overlay), TranslationAgent (no bilingual), StyleTransfer/VideoExtend (no restyle / length change).

**plan:**
  - `IntakeVideoAgent` — Ingest the user's uploaded Mandarin variety show recording into the workspace.
  - `VideoAnalysisAgent` — Analyze the Mandarin variety show to locate guest-performance moments.
  - `HighlightAgent` — Extract the guest-performance as highlight segments.
  - `TranscriptionAgent` — Transcribe the highlight-segment Mandarin dialogue into timestamped subtitle segments.
  - `CompositorAgent` — Composite the final highlight reel mp4 with Mandarin subtitles overlaid.

## #9  (cr_music_ambience, grpo_handwritten, grpo_0338)
**user_goal** (190 chars):

> Make a wuxia mini-drama about a junior disciple defending her mountain temple from a rival sect's blade-master, with epic erhu-and-percussion BGM and mountain-wind-and-bamboo-rustle ambient.

**rationale:** Wuxia mountain-temple mini-drama from a text brief + epic erhu-and-percussion BGM + mountain-wind-and-bamboo-rustle ambient bed. StoryAgent drafts the junior-disciple / temple-defense / final-blade duel blueprint. ScreenplayAgent breaks it into wuxia mountain-temple scenes. KeyFrameAgent plans keyframes for the mountain temple courtyard / bamboo grove / cliff-side duel platform settings from text alone. VideoAgent assembles the multi-shot film. MusicAgent composes the epic erhu-and-percussion score. AmbienceAgent generates the mountain-wind-and-bamboo-rustle ambient bed. AudioMixAgent layers both under the dialogue+foley. CompositorAgent muxes the final mp4. Reject Transcription/Translation (no subtitles), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no video uploaded), Narration/Illustration/Narrator (not a slideshow / illustrated-storytelling format).

**plan:**
  - `StoryAgent` — Draft the Wuxia mountain-temple story blueprint — junior-disciple / temple-defense / final-blade duel arc.
  - `ScreenplayAgent` — Decompose the junior-disciple / temple-defense / final-blade duel arc into wuxia mountain-temple scenes.
  - `KeyFrameAgent` — Plan keyframes for the mountain temple courtyard / bamboo grove / cliff-side duel platform settings; text-only generation, no reference images supplied.
  - `VideoAgent` — Render per-shot clips preserving wuxia mountain-temple visual continuity.
  - `MusicAgent` — Compose the epic erhu-and-percussion BGM the user requested, matching the wuxia mountain-temple register.
  - `AmbienceAgent` — Generate the mountain-wind-and-bamboo-rustle ambient atmosphere as the audio bed.
  - `AudioMixAgent` — Layer the epic erhu-and-percussion BGM and mountain-wind-and-bamboo-rustle ambient bed under the clip's baked dialogue+foley track into one final mixed wav.
  - `CompositorAgent` — Composite the final wuxia mountain-temple mini-drama mp4 with mixed audio and inter-shot transitions.

## #10  (extend_only, grpo_handwritten, grpo_0420)
**user_goal** (120 chars):

> Please extend this 6-second clip of a hammock swaying in the backyard — to about 25 seconds with continuing gentle sway.

**rationale:** 6-second hammock-sway clip + extend-to-25s with continuing gentle sway. IntakeVideoAgent ingests the clip; VideoExtendAgent generates additional frames of the hammock's pendulum motion. Raw extended clip is the deliverable.

**plan:**
  - `IntakeVideoAgent` — Ingest the 6-second hammock-sway clip into the workspace.
  - `VideoExtendAgent` — Extend the hammock-sway footage from 6 seconds to ~25 seconds preserving the gentle pendulum motion.

## #11  (style_only, grpo_handwritten, grpo_0494)
**user_goal** (69 chars):

> Restyle my wedding ceremony video in vintage-1950s Technicolor style.

**rationale:** wedding ceremony clip + vintage-1950s Technicolor style-transfer request. Raw style-transferred output is the deliverable — no audio overlay, no subtitle, no length change.

**plan:**
  - `IntakeVideoAgent` — Ingest the user's uploaded wedding ceremony clip into the workspace.
  - `StyleTransferAgent` — Apply vintage-1950s Technicolor style transfer to the wedding ceremony clip and output the restyled video.

## #12  (extend_only, grpo_handwritten, grpo_0413)
**user_goal** (118 chars):

> I have a 6-second clip of a street performer juggling. Please extend to about 22 seconds with the juggling continuing.

**rationale:** 6-second street-performer juggling clip + extend-to-22s with continuing juggling. IntakeVideoAgent loads the clip; VideoExtendAgent generates additional juggling-motion frames preserving the cadence. Output is the raw extended clip.

**plan:**
  - `IntakeVideoAgent` — Ingest the 6-second street-performer juggling clip into the workspace.
  - `VideoExtendAgent` — Extend the juggling footage from 6 seconds to ~22 seconds with the juggling cadence held steady.

## #13  (story_imgref_music, grpo_handwritten, grpo_1300)
**user_goal** (179 chars):

> Here's a photo of my best friend — make an illustrated audiobook of an epic quest tale where she's the warrior hero, with ink-and-color-wash illustrations and epic orchestral BGM.

**rationale:** Hero-tale with music + ink-and-color-wash illustrations + slideshow narration with young-woman-portrait reference image and epic orchestral BGM.

**plan:**
  - `IntakeImageAgent` — Register the user's uploaded young-woman-portrait reference image as a captioned workspace artifact.
  - `BriefEnricherAgent` — Enrich the brief by integrating the young-woman-portrait reference image's descriptive content.
  - `NarrationAgent` — Write the narration script from the young-warrior-hero quest, anchored to the young-woman-portrait reference.
  - `IllustrationAgent` — Generate one ink-and-color-wash illustration per young-warrior-hero quest scene, depicting the young-woman-portrait reference.
  - `NarratorAgent` — Produce a measured TTS narrator track for the young-warrior-hero quest.
  - `MusicAgent` — Compose the epic orchestral BGM the user requested.
  - `AudioMixAgent` — Layer the epic orchestral BGM under the narrator track into one final mixed wav.
  - `CompositorAgent` — Compose the final slideshow pairing ink-and-color-wash illustrations with mixed narrator-and-BGM audio.

## #14  (story_music, grpo_handwritten, grpo_1182)
**user_goal** (112 chars):

> Read this Japanese Momotaro peach-boy folktale aloud with ukiyo-e illustrations and Japanese koto-and-flute BGM.

**rationale:** Japanese Momotaro folktale + ukiyo-e illustrations + slideshow narration with Japanese koto-and-flute BGM.

**plan:**
  - `NarrationAgent` — Write the narration script from the Momotaro peach-boy folktale.
  - `IllustrationAgent` — Generate one ukiyo-e illustration per Momotaro peach-boy folktale scene.
  - `NarratorAgent` — Produce a measured TTS narrator track for the Momotaro peach-boy folktale.
  - `MusicAgent` — Compose the Japanese koto-and-flute BGM the user requested.
  - `AudioMixAgent` — Layer the Japanese koto-and-flute BGM under the narrator track into one final mixed wav.
  - `CompositorAgent` — Compose the final slideshow pairing ukiyo-e illustrations with mixed narrator-and-BGM audio.

## #15  (extend_style, grpo_handwritten, grpo_1050)
**user_goal** (89 chars):

> Extend my snowboarding video to ~45 seconds and apply Frank-Miller-comic-book noir style.

**rationale:** snowboarding clip + extend-to-45 seconds + comic-book Frank-Miller noir style transfer. Raw style-transferred extended output is the deliverable. Reject Compositor (no overlay), Music/Ambience/AudioMix, Transcription/Translation, VideoAnalysis/Highlight.

**plan:**
  - `IntakeVideoAgent` — Ingest the user's uploaded snowboarding clip into the workspace.
  - `VideoExtendAgent` — Extend the snowboarding clip to ~45 seconds duration.
  - `StyleTransferAgent` — Apply comic-book Frank-Miller noir style transfer to the extended snowboarding clip and output the restyled extended video.

## #16  (vid_music_ambience, grpo_handwritten, grpo_0836)
**user_goal** (99 chars):

> Add ambient-marimba BGM and an underwater-and-distant-bubble ambient bed to my aquarium visit clip.

**rationale:** aquarium visit clip + ambient marimba BGM + underwater-and-distant-bubble ambient bed. Reject Transcription/Translation, VideoAnalysis/Highlight, StyleTransfer/VideoExtend.

**plan:**
  - `IntakeVideoAgent` — Ingest the user's uploaded aquarium visit clip into the workspace.
  - `MusicAgent` — Compose the ambient marimba BGM the user requested.
  - `AmbienceAgent` — Generate the underwater-and-distant-bubble ambient atmosphere as the audio bed.
  - `AudioMixAgent` — Layer the ambient marimba BGM and underwater-and-distant-bubble ambient bed under the clip's baked audio into one final mixed wav.
  - `CompositorAgent` — Composite the final aquarium visit mp4 with mixed audio.

## #17  (extend_only, grpo_handwritten, grpo_0398)
**user_goal** (135 chars):

> 8-second clip of autumn leaves spinning down to the ground. Could you extend to ~25 seconds with more leaves falling in the same scene?

**rationale:** 8-second autumn leaf-fall clip + extend-to-25s with continuing leaf drift. IntakeVideoAgent ingests the clip; VideoExtendAgent generates additional leaf-fall frames. Output is the extended clip only.

**plan:**
  - `IntakeVideoAgent` — Ingest the 8-second autumn leaf-fall clip into the workspace.
  - `VideoExtendAgent` — Extend the leaf-fall clip from 8 seconds to ~25 seconds with continuing autumn-leaf descent.

## #18  (story_music_bilingual, grpo_handwritten, grpo_1337)
**user_goal** (148 chars):

> Read a classical Tang-dynasty poem aloud with Chinese-ink-wash illustrations and classical guzheng BGM, narrated in Mandarin with English subtitles.

**rationale:** Bilingual Tang-poem recitation + Chinese-ink-wash illustrations + slideshow narration with classical guzheng BGM and Mandarin-and-English bilingual subtitles.

**plan:**
  - `NarrationAgent` — Write the narration script from the Tang-dynasty poem recitation.
  - `IllustrationAgent` — Generate one Chinese-ink-wash illustration per Tang-dynasty poem recitation scene.
  - `NarratorAgent` — Produce a measured Mandarin TTS narrator track for the Tang-dynasty poem recitation.
  - `MusicAgent` — Compose the classical guzheng BGM the user requested.
  - `AudioMixAgent` — Layer the classical guzheng BGM under the narrator track into one final mixed wav.
  - `TranslationAgent` — Translate the Mandarin narrator track into English for the second-language subtitle overlay.
  - `CompositorAgent` — Compose the final slideshow pairing Chinese-ink-wash illustrations with mixed narrator-and-BGM audio and bilingual Mandarin-and-English subtitles overlaid.

## #19  (cr_compositor_only, grpo_handwritten, grpo_0007)
**user_goal** (166 chars):

> Make a spy thriller mini-drama about a junior cultural attaché in a foreign embassy who realizes a suspected asset is leaking classified material to the host country.

**rationale:** Embassy-conspiracy spy thriller mini-drama from a text brief, no audio overlay. StoryAgent drafts the junior-cultural-attache / foreign-asset / leak-trail blueprint. ScreenplayAgent breaks it into embassy spy scenes. KeyFrameAgent plans keyframes for the embassy ballroom / dead-drop alley / interrogation room settings from text alone. VideoAgent assembles the multi-shot film. CompositorAgent muxes the final mp4 with inter-shot transitions. Reject MusicAgent / AmbienceAgent / AudioMixAgent (no audio overlay requested), TranscriptionAgent / TranslationAgent (no subtitles), VideoAnalysisAgent / IntakeVideoAgent / StyleTransferAgent / VideoExtendAgent / HighlightAgent (no video uploaded), NarrationAgent / IllustrationAgent / NarratorAgent (not a slideshow / illustrated-storytelling format).

**plan:**
  - `StoryAgent` — Draft the Embassy-conspiracy spy thriller story blueprint — junior-cultural-attache / foreign-asset / leak-trail arc.
  - `ScreenplayAgent` — Decompose the junior-cultural-attache / foreign-asset / leak-trail arc into embassy spy scenes.
  - `KeyFrameAgent` — Plan keyframes for the embassy ballroom / dead-drop alley / interrogation room settings; text-only generation, no reference images supplied.
  - `VideoAgent` — Render per-shot clips preserving embassy spy thriller visual continuity.
  - `CompositorAgent` — Composite the final embassy spy mini-drama mp4 with inter-shot transitions.

## #20  (story_pure, grpo_handwritten, grpo_0100)
**user_goal** (172 chars):

> Read this Greek myth about Daphne fleeing Apollo and being transformed into a laurel tree aloud, with one Greek-vase-painting-style illustration per scene, slideshow style.

**rationale:** Greek Daphne-and-Apollo myth + Greek-vase-painting illustrations + slideshow narration.

**plan:**
  - `NarrationAgent` — Write the narration script from the Daphne-and-Apollo myth.
  - `IllustrationAgent` — Generate one Greek-vase-painting illustration per Daphne-and-Apollo myth scene.
  - `NarratorAgent` — Produce a measured TTS narrator track for the Daphne-and-Apollo myth.
  - `CompositorAgent` — Compose the final slideshow pairing Greek-vase-painting illustrations with the narrator audio.

## #21  (story_pure, grpo_handwritten, grpo_0111)
**user_goal** (867 chars):

> Here's my story I want to process — soft watercolor please: There once was a small brown rabbit named Pip who lived in a meadow at the edge of a sleeping forest. One evening, just as the moon was rising, Pip found a seed that glowed like a tiny lantern. The other rabbits had all run home for the night, but Pip was curious. The seed was warm in his paw. He carried it home through the long grass and... [+467 chars]

**rationale:** Bedtime rabbit-and-seed tale from a user-provided story + soft watercolor illustrations + slideshow narration.

**plan:**
  - `NarrationAgent` — Write the narration script from the user's supplied rabbit-and-glowing-seed bedtime tale.
  - `IllustrationAgent` — Generate one soft watercolor illustration per scene of the rabbit-and-glowing-seed bedtime tale.
  - `NarratorAgent` — Produce a measured TTS narrator track for the rabbit-and-glowing-seed bedtime tale.
  - `CompositorAgent` — Compose the final slideshow pairing soft watercolor illustrations with the narrator audio.

## #22  (cr_music_ambience, grpo_handwritten, grpo_0384)
**user_goal** (246 chars):

> Make a Belle-Epoque Paris mini-drama about a young cabaret singer outmaneuvering a senior rival on the final-cabaret-night that decides next season's headliner, with Parisian-cafe-strings-and-accordion BGM and Belle-Epoque-Paris-and-rain ambient.

**rationale:** Belle-Epoque Paris cafe mini-drama from a text brief + Parisian-cafe-strings-and-accordion BGM + Belle-Epoque-Paris-and-rain ambient bed. StoryAgent drafts the young-singer / cabaret-rivalry / final-cabaret-night reveal blueprint. ScreenplayAgent breaks it into Belle-Epoque Paris cafe scenes. KeyFrameAgent plans keyframes for the Belle-Epoque cabaret stage / dressing-room mirror / cabaret-courtyard exchange settings from text alone. VideoAgent assembles the multi-shot film. MusicAgent composes the Parisian-cafe-strings-and-accordion score. AmbienceAgent generates the Belle-Epoque-Paris-and-rain ambient bed. AudioMixAgent layers both under the dialogue+foley. CompositorAgent muxes the final mp4. Reject Transcription/Translation (no subtitles), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no video uploaded), Narration/Illustration/Narrator (not a slideshow / illustrated-storytelling format).

**plan:**
  - `StoryAgent` — Draft the Belle-Epoque Paris cafe story blueprint — young-singer / cabaret-rivalry / final-cabaret-night reveal arc.
  - `ScreenplayAgent` — Decompose the young-singer / cabaret-rivalry / final-cabaret-night reveal arc into Belle-Epoque Paris cafe scenes.
  - `KeyFrameAgent` — Plan keyframes for the Belle-Epoque cabaret stage / dressing-room mirror / cabaret-courtyard exchange settings; text-only generation, no reference images supplied.
  - `VideoAgent` — Render per-shot clips preserving Belle-Epoque Paris cafe visual continuity.
  - `MusicAgent` — Compose the Parisian-cafe-strings-and-accordion BGM the user requested, matching the Belle-Epoque Paris cafe register.
  - `AmbienceAgent` — Generate the Belle-Epoque-Paris-and-rain ambient atmosphere as the audio bed.
  - `AudioMixAgent` — Layer the Parisian-cafe-strings-and-accordion BGM and Belle-Epoque-Paris-and-rain ambient bed under the clip's baked dialogue+foley track into one final mixed wav.
  - `CompositorAgent` — Composite the final Belle-Epoque Paris cafe mini-drama mp4 with mixed audio and inter-shot transitions.

## #23  (cr_subtitle, grpo_handwritten, grpo_0542)
**user_goal** (171 chars):

> Produce an Italian-language 1970s political thriller mini-drama about a young prosecutor uncovering the mafia pact behind a politician's kidnapping, and Italian subtitles.

**rationale:** Italian 1970s political-thriller mini-drama from a text brief + Italian monolingual subtitles. StoryAgent drafts the young-prosecutor / kidnapped-politician / mafia-pact discovery blueprint. ScreenplayAgent breaks it into Italian 1970s political-thriller scenes. KeyFrameAgent plans keyframes for the Rome courthouse / Naples-port stakeout / underground meeting settings from text alone. VideoAgent assembles the multi-shot film. TranscriptionAgent extracts Italian subtitles from the dialogue audio. CompositorAgent muxes the final mp4 with subtitle overlay. Reject TranslationAgent (monolingual subtitles, not bilingual), VideoAnalysisAgent / IntakeVideoAgent / StyleTransferAgent / VideoExtendAgent / HighlightAgent (no video uploaded), NarrationAgent / IllustrationAgent / NarratorAgent (not a slideshow / illustrated-storytelling format). Chain: Story → Screenplay → KeyFrame → Video → Transcription → Compositor → done.

**plan:**
  - `StoryAgent` — Draft the Italian 1970s political-thriller story blueprint — young-prosecutor / kidnapped-politician / mafia-pact discovery arc.
  - `ScreenplayAgent` — Decompose the young-prosecutor / kidnapped-politician / mafia-pact discovery arc into Italian 1970s political-thriller scenes.
  - `KeyFrameAgent` — Plan keyframes for the Rome courthouse / Naples-port stakeout / underground meeting settings; text-only generation, no reference images supplied.
  - `VideoAgent` — Render per-shot clips preserving Italian 1970s political-thriller visual continuity.
  - `TranscriptionAgent` — Transcribe the Italian dialogue into timestamped subtitle segments.
  - `CompositorAgent` — Composite the final Italian 1970s political-thriller mini-drama mp4 with mixed audio and Italian subtitles overlaid.

## #24  (cr_music, grpo_handwritten, grpo_0197)
**user_goal** (191 chars):

> Make a Mayan-city-collapse mini-drama about the last priestess of a failing city performing a final rain ritual as her people prepare to abandon the temple plaza, with Mesoamerican-drums BGM.

**rationale:** Mayan-city collapse mini-drama from a text brief + ritualistic Mesoamerican drums BGM. StoryAgent drafts the last-priestess / failing-rains / ritual-final-night blueprint. ScreenplayAgent breaks it into Mayan-city collapse scenes. KeyFrameAgent plans keyframes for the stone temple plaza / drying farm-fields / ritual-pyramid summit settings from text alone. VideoAgent assembles the multi-shot film. MusicAgent composes the Mesoamerican drums score. AudioMixAgent layers it under the dialogue+foley. CompositorAgent muxes the final mp4. Reject AmbienceAgent, Transcription/Translation, VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight, Narration/Illustration/Narrator.

**plan:**
  - `StoryAgent` — Draft the Mayan-city collapse story blueprint — last-priestess / failing-rains / ritual-final-night arc.
  - `ScreenplayAgent` — Decompose the last-priestess / failing-rains / ritual-final-night arc into Mayan-city collapse scenes.
  - `KeyFrameAgent` — Plan keyframes for the stone temple plaza / drying farm-fields / ritual-pyramid summit settings; text-only generation, no reference images supplied.
  - `VideoAgent` — Render per-shot clips preserving Mayan-city collapse visual continuity.
  - `MusicAgent` — Compose the ritualistic Mesoamerican drums BGM the user requested, matching the Mayan-city collapse register.
  - `AudioMixAgent` — Layer the ritualistic Mesoamerican drums BGM under the clip's baked dialogue+foley track into one final mixed wav.
  - `CompositorAgent` — Composite the final Mayan-city collapse mini-drama mp4 with mixed audio and inter-shot transitions.

## #25  (story_bilingual, grpo_handwritten, grpo_1232)
**user_goal** (140 chars):

> Read the Tagalog Maria-Makiling forest-spirit tale aloud with Filipino-watercolor illustrations, narrated in Tagalog with English subtitles.

**rationale:** Tagalog Maria-Makiling forest-spirit tale + Filipino-watercolor illustrations + slideshow narration with Tagalog-and-English bilingual subtitles.

**plan:**
  - `NarrationAgent` — Write the narration script from the Maria-Makiling forest-spirit tale.
  - `IllustrationAgent` — Generate one Filipino-watercolor illustration per Maria-Makiling forest-spirit tale scene.
  - `NarratorAgent` — Produce a measured Tagalog TTS narrator track for the Maria-Makiling forest-spirit tale.
  - `TranslationAgent` — Translate the Tagalog narrator track into English for the second-language subtitle overlay.
  - `CompositorAgent` — Compose the final slideshow pairing Filipino-watercolor illustrations with the narrator audio and bilingual Tagalog-and-English subtitles overlaid.

## #26  (cr_subtitle, grpo_handwritten, grpo_0550)
**user_goal** (190 chars):

> Produce a Vietnamese-language postwar mini-drama about a young woman whose father's old wartime comrades visit and slowly reveal the family truth he never told her, and Vietnamese subtitles.

**rationale:** Vietnamese postwar family mini-drama from a text brief + Vietnamese monolingual subtitles. StoryAgent drafts the young-daughter / father's-old-comrades visit / family-truth reveal blueprint. ScreenplayAgent breaks it into Vietnamese postwar family scenes. KeyFrameAgent plans keyframes for the Saigon family home / pho-stall street-corner / ancestor-altar room settings from text alone. VideoAgent assembles the multi-shot film. TranscriptionAgent extracts Vietnamese subtitles from the dialogue audio. CompositorAgent muxes the final mp4 with subtitle overlay. Reject TranslationAgent (monolingual subtitles, not bilingual), VideoAnalysisAgent / IntakeVideoAgent / StyleTransferAgent / VideoExtendAgent / HighlightAgent (no video uploaded), NarrationAgent / IllustrationAgent / NarratorAgent (not a slideshow / illustrated-storytelling format). Chain: Story → Screenplay → KeyFrame → Video → Transcription → Compositor → done.

**plan:**
  - `StoryAgent` — Draft the Vietnamese postwar family story blueprint — young-daughter / father's-old-comrades visit / family-truth reveal arc.
  - `ScreenplayAgent` — Decompose the young-daughter / father's-old-comrades visit / family-truth reveal arc into Vietnamese postwar family scenes.
  - `KeyFrameAgent` — Plan keyframes for the Saigon family home / pho-stall street-corner / ancestor-altar room settings; text-only generation, no reference images supplied.
  - `VideoAgent` — Render per-shot clips preserving Vietnamese postwar family visual continuity.
  - `TranscriptionAgent` — Transcribe the Vietnamese dialogue into timestamped subtitle segments.
  - `CompositorAgent` — Composite the final Vietnamese postwar family mini-drama mp4 with mixed audio and Vietnamese subtitles overlaid.

## #27  (cr_music, grpo_handwritten, grpo_0176)
**user_goal** (214 chars):

> Produce a post-pandemic survival mini-drama about an ER doctor escaping the outbreak zero zone with a vial of antibodies, racing to reach a safe-zone before infrastructure collapses, with cinematic synth-dread BGM.

**rationale:** Apocalyptic-virus survival mini-drama from a text brief + cinematic synth-dread BGM. StoryAgent drafts the ER-doctor / outbreak-zero / safe-zone race blueprint. ScreenplayAgent breaks it into post-virus survival scenes. KeyFrameAgent plans keyframes for the abandoned hospital / overrun freeway / makeshift safe-zone settings from text alone. VideoAgent assembles the multi-shot film. MusicAgent composes the synth-dread score. AudioMixAgent layers it under the dialogue+foley. CompositorAgent muxes the final mp4. Reject AmbienceAgent, Transcription/Translation, VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight, Narration/Illustration/Narrator.

**plan:**
  - `StoryAgent` — Draft the Apocalyptic-virus survival story blueprint — ER-doctor / outbreak-zero / safe-zone race arc.
  - `ScreenplayAgent` — Decompose the ER-doctor / outbreak-zero / safe-zone race arc into post-virus survival scenes.
  - `KeyFrameAgent` — Plan keyframes for the abandoned hospital / overrun freeway / makeshift safe-zone settings; text-only generation, no reference images supplied.
  - `VideoAgent` — Render per-shot clips preserving apocalyptic-virus survival visual continuity.
  - `MusicAgent` — Compose the cinematic synth-dread BGM the user requested, matching the apocalyptic-virus survival register.
  - `AudioMixAgent` — Layer the cinematic synth-dread BGM under the clip's baked dialogue+foley track into one final mixed wav.
  - `CompositorAgent` — Composite the final apocalyptic-virus survival mini-drama mp4 with mixed audio and inter-shot transitions.

## #28  (story_pure, grpo_handwritten, grpo_0088)
**user_goal** (180 chars):

> Produce a narrated picture-book video of this Cherokee creation story about Spider-Grandmother bringing fire to the people, with Cherokee-textile-pattern illustrations per episode.

**rationale:** Cherokee Spider-Grandmother creation story + Cherokee-textile-pattern illustrations + slideshow narration.

**plan:**
  - `NarrationAgent` — Write the narration script from the Spider-Grandmother creation story.
  - `IllustrationAgent` — Generate one Cherokee-textile-pattern illustration per Spider-Grandmother creation story scene.
  - `NarratorAgent` — Produce a measured TTS narrator track for the Spider-Grandmother creation story.
  - `CompositorAgent` — Compose the final slideshow pairing Cherokee-textile-pattern illustrations with the narrator audio.

## #29  (extend_style, grpo_handwritten, grpo_1055)
**user_goal** (100 chars):

> Extend my hiking-summit footage to ~45 seconds and restyle in Caspar-David-Friedrich Romantic style.

**rationale:** hiking summit clip + extend-to-45 seconds + Caspar-David-Friedrich Romantic style transfer. Raw style-transferred extended output is the deliverable. Reject Compositor (no overlay), Music/Ambience/AudioMix, Transcription/Translation, VideoAnalysis/Highlight.

**plan:**
  - `IntakeVideoAgent` — Ingest the user's uploaded hiking summit clip into the workspace.
  - `VideoExtendAgent` — Extend the hiking summit clip to ~45 seconds duration.
  - `StyleTransferAgent` — Apply Caspar-David-Friedrich Romantic style transfer to the extended hiking summit clip and output the restyled extended video.

## #30  (extend_only, grpo_handwritten, grpo_0427)
**user_goal** (113 chars):

> Got a 5-second clip of an ice skater spinning in the rink center. Extend to ~18 seconds with the spin continuing.

**rationale:** 5-second ice-skater rink-center spin clip + extend-to-18s with continuing spin. IntakeVideoAgent loads the clip; VideoExtendAgent generates additional spin frames preserving the rotation cadence. Output is the raw extended clip.

**plan:**
  - `IntakeVideoAgent` — Ingest the 5-second ice-skater rink-center spin clip into the workspace.
  - `VideoExtendAgent` — Extend the spin footage from 5 seconds to ~18 seconds preserving the rink-center rotation cadence.
