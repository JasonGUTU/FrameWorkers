# Spot check — 50 of 1417 SFT samples

**Checklist:**
1. rationale explicitly justifies every agent in the chain AND names 2-4 agents that were NOT included with a reason.
2. intents are agent-specific (mention the user_goal's topic), not generic.
3. long-story samples preserve the full story verbatim in user_goal.

---

## #1
**user_goal** (54 chars):

> Make an English-subtitled cyberpunk hacker mini-drama.

**rationale:** Cyberpunk hacker drama + English subs. Chain: Story → Screenplay → KeyFrame → Video → Transcription → Compositor → done.

**plan:**
  - `StoryAgent` — Write the cyberpunk-hacker story.
  - `ScreenplayAgent` — Break the story into cyberpunk-hacker scenes.
  - `KeyFrameAgent` — Design key frames for the neon cyberpunk city.
  - `VideoAgent` — Render motion-video clips preserving cyberpunk continuity.
  - `TranscriptionAgent` — Transcribe the English dialogue into timestamped SRT.
  - `CompositorAgent` — Compose the final cyberpunk mini-drama with English captions and mixed audio.

## #2
**user_goal** (125 chars):

> From this 2-hour Vietnamese travel-documentary, pull the best scenic moments and add Vietnamese + English bilingual captions.

**rationale:** Vietnamese travel doc + best-scenic highlight + Vietnamese+English bilingual captions. IntakeVideoAgent → VideoAnalysisAgent → HighlightAgent → TranscriptionAgent (Vietnamese) → TranslationAgent (to English) → CompositorAgent.

**plan:**
  - `IntakeVideoAgent` — Ingest the 2-hour Vietnamese travel-documentary into the workspace.
  - `VideoAnalysisAgent` — Analyze the documentary to locate the most scenic / highlight moments.
  - `HighlightAgent` — Extract those scenic moments as highlight segments.
  - `TranscriptionAgent` — Transcribe the Vietnamese narration on the segments into SRT.
  - `TranslationAgent` — Translate the Vietnamese SRT segments into English subtitles.
  - `CompositorAgent` — Compose the highlight reel with bilingual Vietnamese-English captions burned onto the cuts.

## #3
**user_goal** (108 chars):

> From this 90-minute boxing match, extract the knockdown moments and add English captions from the broadcast.

**rationale:** Boxing match + knockdown highlight + English broadcast captions. IntakeVideoAgent → VideoAnalysisAgent → HighlightAgent → TranscriptionAgent → CompositorAgent.

**plan:**
  - `IntakeVideoAgent` — Ingest the 90-minute boxing-match recording into the workspace.
  - `VideoAnalysisAgent` — Analyze the match to locate knockdown events.
  - `HighlightAgent` — Extract the knockdowns as highlight segments.
  - `TranscriptionAgent` — Transcribe the English broadcast commentary on the knockdown segments into SRT.
  - `CompositorAgent` — Compose the highlight reel with English captions burned onto the knockdown cuts.

## #4
**user_goal** (124 chars):

> Add Thai subtitles on this Muay Thai training video. The trainer speaks Thai — match the Thai captions to his coaching cues.

**rationale:** Thai-coached Muay Thai training video + Thai-on-Thai captioning. IntakeVideoAgent loads the training clip. TranscriptionAgent transcribes Thai coaching cues into timestamped SRT. CompositorAgent renders Thai captions onto the training footage. No translation, no audio overlay, no analysis or highlight reel, no style transfer.

**plan:**
  - `IntakeVideoAgent` — Ingest the Thai Muay Thai training video into the workspace.
  - `TranscriptionAgent` — Transcribe the trainer's Thai coaching cues into timestamped SRT segments.
  - `CompositorAgent` — Burn Thai captions onto the training clip and export the final captioned footage.

## #5
**user_goal** (111 chars):

> Using this uploaded image of a Tokyo shoutengai street, make an extended-length ramen-shop-daughter mini-drama.

**rationale:** Image-referenced Tokyo-shoutengai ramen-shop daughter extended + bossa-nova-japan-fusion. Chain: IntakeImage → BriefEnricher → Story → Screenplay → KeyFrame → Video → VideoExtend → Compositor → done.

**plan:**
  - `IntakeImageAgent` — Ingest the uploaded Tokyo shoutengai image as the visual reference.
  - `BriefEnricherAgent` — Enrich the setting brief combining shoutengai atmosphere with ramen-shop-daughter concept.
  - `StoryAgent` — Write the ramen-shop-daughter story.
  - `ScreenplayAgent` — Break the story into ramen-shop scenes.
  - `KeyFrameAgent` — Design key frames matching the uploaded shoutengai street.
  - `VideoAgent` — Render motion-video clips preserving the shoutengai continuity.
  - `VideoExtendAgent` — Extend the clips to the longer requested runtime.
  - `CompositorAgent` — Compose the extended shoutengai mini-drama with all layers assembled.

## #6
**user_goal** (110 chars):

> Using this uploaded image of a volcanic island, make an extended scientist-racing-against-eruption mini-drama.

**rationale:** Image-referenced volcanic-island scientist-thriller extended + tense cinematic. Chain: IntakeImage → BriefEnricher → Story → Screenplay → KeyFrame → Video → VideoExtend → Compositor → done.

**plan:**
  - `IntakeImageAgent` — Ingest the uploaded volcanic-island image as the visual reference.
  - `BriefEnricherAgent` — Enrich the setting brief combining island atmosphere with scientist-eruption concept.
  - `StoryAgent` — Write the scientist-racing-eruption story.
  - `ScreenplayAgent` — Break the story into eruption thriller scenes.
  - `KeyFrameAgent` — Design key frames matching the uploaded island topology.
  - `VideoAgent` — Render motion-video clips preserving the volcanic-island continuity.
  - `VideoExtendAgent` — Extend the clips to the longer requested runtime.
  - `CompositorAgent` — Compose the extended volcanic mini-drama with all layers assembled.

## #7
**user_goal** (142 chars):

> Make a mini-drama about an aging astronomer pursuing an anomalous radio signal from her small-hill observatory, with hill-observatory ambient.

**rationale:** Mini-drama from a text brief + hill-observatory ambient. StoryAgent drafts the aging-astronomer / anomalous-radio-signal / hill-observatory blueprint. ScreenplayAgent breaks it into astronomy-drama scenes. KeyFrameAgent plans keyframes for the hill-observatory settings from text alone. VideoAgent assembles the multi-shot film. AmbienceAgent generates the hill-observatory room-tone bed. AudioMixAgent layers it under the dialogue+foley. CompositorAgent muxes the final mp4. Reject MusicAgent, Transcription/Translation, VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight, Narration/Illustration/Narrator.

**plan:**
  - `StoryAgent` — Draft the astronomer story blueprint — aging-astronomer pursuing anomalous radio signal from hill observatory arc.
  - `ScreenplayAgent` — Decompose the signal-pursuit arc into astronomy-drama scenes.
  - `KeyFrameAgent` — Plan keyframes for the small-hill observatory settings; text-only generation, no reference images supplied.
  - `VideoAgent` — Render per-shot clips preserving astronomy-drama visual continuity.
  - `AmbienceAgent` — Generate the hill-observatory ambient bed the user requested, matching the hill-observatory environment.
  - `AudioMixAgent` — Layer the hill-observatory ambience bed under the clip's baked dialogue+foley track into one final mixed wav.
  - `CompositorAgent` — Composite the final astronomer mini-drama mp4 with mixed audio and inter-shot transitions.

## #8
**user_goal** (90 chars):

> Please extend this 4-second Czech theater-scene clip to 15 seconds and add Czech captions.

**rationale:** Czech theater scene + extend + Czech (monolingual) captions. IntakeVideoAgent → VideoExtendAgent (~15s) → TranscriptionAgent (Czech) → CompositorAgent (Czech SRT).

**plan:**
  - `IntakeVideoAgent` — Ingest the 4-second Czech theater-scene clip into the workspace.
  - `VideoExtendAgent` — Extend the scene clip to ~15 seconds continuing the performers' dialogue.
  - `TranscriptionAgent` — Transcribe the extended Czech dialogue into timestamped SRT.
  - `CompositorAgent` — Compose the extended scene with Czech captions burned onto the theater footage.

## #9
**user_goal** (117 chars):

> Make a Hawaiian-English bilingual Oahu mini-drama about a young hula dancer competing in the Merrie Monarch festival.

**rationale:** Oahu hula dancer Merrie Monarch drama + Hawaiian+English bilingual + traditional hula-chant. Chain: Story → Screenplay → KeyFrame → Video → Transcription → Translation → Compositor → done.

**plan:**
  - `StoryAgent` — Write the Oahu Merrie Monarch hula dancer story.
  - `ScreenplayAgent` — Break the story into hula-dance scenes.
  - `KeyFrameAgent` — Design key frames for Oahu and the Merrie Monarch stage.
  - `VideoAgent` — Render motion-video clips preserving Oahu continuity.
  - `TranscriptionAgent` — Transcribe the Hawaiian dialogue into timestamped SRT.
  - `TranslationAgent` — Translate the Hawaiian SRT into English subtitles.
  - `CompositorAgent` — Compose the Oahu mini-drama with bilingual Hawaiian-English captions and mixed audio.

## #10
**user_goal** (95 chars):

> Using this uploaded image of a snow-covered lighthouse, make a keeper's-last-winter mini-drama.

**rationale:** Snow-covered-lighthouse image + keeper's-last-winter drama. Chain: IntakeImage → BriefEnricher → Story → Screenplay → KeyFrame → Video → Compositor → done.

**plan:**
  - `IntakeImageAgent` — Ingest the uploaded snow-covered-lighthouse image into the workspace as the visual reference.
  - `BriefEnricherAgent` — Enrich the setting brief combining the lighthouse atmosphere with the keeper concept.
  - `StoryAgent` — Write a keeper's-last-winter mini-drama set at the lighthouse.
  - `ScreenplayAgent` — Break the story into keeper-drama scenes inside and around the lighthouse.
  - `KeyFrameAgent` — Design key frames matching the uploaded lighthouse architecture.
  - `VideoAgent` — Render motion-video clips preserving the lighthouse's visual identity.
  - `CompositorAgent` — Compose the final keeper mini-drama with all layers assembled.

## #11
**user_goal** (165 chars):

> Make an illustrated audiobook of this arctic-fox winter tale, with a gentle celesta playing under the narrator AND arctic ambient (howling wind, distant ice cracks).

**rationale:** Long-form illustrated-storytelling brief — the protagonist's arc + dual audio layers (music score + environmental ambience). NarrationAgent writes the narrator script split into picture-aligned segments. IllustrationAgent generates one illustration per segment. NarratorAgent renders the script as voiceover wav. MusicAgent composes the music score the user specified. AmbienceAgent generates the ambient bed the user specified. AudioMixAgent combines narrator + music + ambience into one final mixed wav. CompositorAgent muxes the slideshow video. Reject Transcription/Translation (no subtitle / multilingual ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow voiceover, not multi-shot film), IntakeImage/BriefEnricher (no image upload).

**plan:**
  - `NarrationAgent` — Outline the user's storytelling brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with per-segment image_prompt + per-line TTS text.
  - `IllustrationAgent` — Plan one illustration per narrator segment in picture-book style, depicting the protagonist's setting and key moments.
  - `NarratorAgent` — Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level SRT + per-segment timing.
  - `MusicAgent` — Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.
  - `AmbienceAgent` — Generate the ambient sound bed the user requested, matching the the protagonist story's environmental setting.
  - `AudioMixAgent` — Combine narrator wav + music score + ambient bed into one final mixed wav.
  - `CompositorAgent` — Composite the final illustrated-audiobook slideshow — segment illustrations timed to the mixed audio (narrator + music + ambience).

## #12
**user_goal** (137 chars):

> Create an English-Thai bilingual illustrated audiobook of this Thai folktale about the rice grandmother with a gentle khaen-and-khim BGM.

**rationale:** Long-form illustrated-storytelling brief — the protagonist's arc + music score + bilingual / foreign-language subtitle ask. NarrationAgent writes the narrator script split into picture-aligned segments. IllustrationAgent generates one illustration per segment. NarratorAgent renders the script as voiceover wav + source-language SRT (timed). MusicAgent composes the music score the user specified. AudioMixAgent layers the music under the narrator wav. TranslationAgent translates the source SRT into the target language preserving timing. CompositorAgent muxes the slideshow with mixed audio + both subtitle tracks. Reject AmbienceAgent (no environmental ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow, not multi-shot film), IntakeImage/BriefEnricher (no image upload). Reject TranscriptionAgent — narrator already produces a timed SRT.

**plan:**
  - `NarrationAgent` — Outline the user's storytelling brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with per-segment image_prompt + per-line TTS text.
  - `IllustrationAgent` — Plan one illustration per narrator segment in picture-book style, depicting the protagonist's setting and key moments.
  - `NarratorAgent` — Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level source-language SRT + per-segment timing.
  - `MusicAgent` — Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.
  - `AudioMixAgent` — Layer the music score under the narrator wav into one final mixed wav.
  - `TranslationAgent` — Translate the narrator SRT into the user-specified target language, preserving every segment's timing intact.
  - `CompositorAgent` — Composite the final illustrated-audiobook slideshow — segment illustrations timed to the mixed audio, both source and translated subtitles burned in.

## #13
**user_goal** (126 chars):

> Using this uploaded image of a Tibetan monastery at dusk, make a pilgrim-child mini-drama about finding an unexpected teacher.

**rationale:** Tibetan-monastery-at-dusk image + pilgrim-child drama. Chain: IntakeImage → BriefEnricher → Story → Screenplay → KeyFrame → Video → Compositor → done.

**plan:**
  - `IntakeImageAgent` — Ingest the uploaded Tibetan-monastery-at-dusk image into the workspace as the visual reference.
  - `BriefEnricherAgent` — Enrich the setting brief combining the monastery atmosphere with the pilgrim-child concept.
  - `StoryAgent` — Write a pilgrim-child mini-drama about finding an unexpected teacher at the monastery.
  - `ScreenplayAgent` — Break the story into pilgrim scenes at the monastery.
  - `KeyFrameAgent` — Design key frames matching the uploaded monastery architecture.
  - `VideoAgent` — Render motion-video clips preserving the monastery's dusk lighting.
  - `CompositorAgent` — Compose the final pilgrim mini-drama with all layers assembled.

## #14
**user_goal** (125 chars):

> Make an illustrated audiobook of this Hans Christian Andersen fairytale with a warm harp-and-celesta BGM under the narration.

**rationale:** Andersen fairytale + harp-and-celesta BGM.

**plan:**
  - `NarrationAgent` — Write the narration script from the Andersen fairytale.
  - `IllustrationAgent` — Generate one soft-pastel illustration per scene.
  - `NarratorAgent` — Produce a warm TTS narrator track for the fairytale.
  - `MusicAgent` — Compose a warm harp-and-celesta BGM fitting the Andersen tone.
  - `AudioMixAgent` — Mix the harp BGM softly under the narrator track.
  - `CompositorAgent` — Compose the final slideshow pairing illustrations with mixed audio.

## #15
**user_goal** (88 chars):

> Please put some dramatic film-score-style music under this slow-motion skate-trick clip.

**rationale:** Slow-mo skate trick + request for dramatic film-score BGM. IntakeVideoAgent ingests the trick clip. MusicAgent composes a dramatic cinematic cue matching the slow-motion climax. AudioMixAgent mixes it with the clip's audio. CompositorAgent muxes the audio track.

**plan:**
  - `IntakeVideoAgent` — Ingest the slow-motion skate-trick clip into the workspace.
  - `MusicAgent` — Compose a dramatic film-score BGM with a climax that matches the slow-motion trick.
  - `AudioMixAgent` — Mix the dramatic BGM with the skate clip's baked audio.
  - `CompositorAgent` — Compose the skate clip with the mixed dramatic BGM overlaid on the footage.

## #16
**user_goal** (111 chars):

> Please add a dramatic film-score BGM AND howling-arctic-wind ambient to this polar-expedition documentary clip.

**rationale:** Polar-expedition doc + dramatic film-score BGM + howling-arctic-wind ambient. IntakeVideoAgent → MusicAgent (dramatic film score) → AmbienceAgent (arctic wind: howling, distant ice cracks) → AudioMixAgent → CompositorAgent.

**plan:**
  - `IntakeVideoAgent` — Ingest the polar-expedition documentary clip into the workspace.
  - `MusicAgent` — Compose a dramatic film-score BGM fitting the polar expedition's scale.
  - `AmbienceAgent` — Generate an arctic-wind ambient bed (howling wind, distant ice cracks).
  - `AudioMixAgent` — Mix the film-score BGM, arctic ambience, and the documentary's baked audio.
  - `CompositorAgent` — Compose the documentary with the mixed music + ambience overlaid on the polar footage.

## #17
**user_goal** (116 chars):

> Pull the dramatic moments from this 2-hour reality-TV episode, add English captions, and add a tension-building BGM.

**rationale:** Reality-TV episode + dramatic moments + English captions + tension-building BGM.

**plan:**
  - `IntakeVideoAgent` — Ingest the 2-hour reality-TV episode into the workspace.
  - `VideoAnalysisAgent` — Analyze the episode to locate dramatic / emotional-peak moments.
  - `HighlightAgent` — Extract the dramatic moments as highlight segments.
  - `MusicAgent` — Compose a tension-building BGM fitting the reality-TV reel.
  - `TranscriptionAgent` — Transcribe the English cast dialogue on the segments into SRT.
  - `AudioMixAgent` — Mix the tension BGM with the highlight reel's baked audio.
  - `CompositorAgent` — Compose the reel with English captions and mixed BGM overlaid on the cuts.

## #18
**user_goal** (99 chars):

> Using this uploaded image of a Galápagos beach, make an extended-length young-biologist mini-drama.

**rationale:** Image-referenced Galápagos-beach biologist extended. Chain: IntakeImage → BriefEnricher → Story → Screenplay → KeyFrame → Video → VideoExtend → Compositor → done.

**plan:**
  - `IntakeImageAgent` — Ingest the uploaded Galápagos-beach image as the visual reference.
  - `BriefEnricherAgent` — Enrich the setting brief combining beach atmosphere with young-biologist concept.
  - `StoryAgent` — Write the young-biologist story on the Galápagos.
  - `ScreenplayAgent` — Break the story into biologist-field scenes.
  - `KeyFrameAgent` — Design key frames matching the uploaded beach landscape.
  - `VideoAgent` — Render motion-video clips preserving the Galápagos continuity.
  - `VideoExtendAgent` — Extend the clips to the longer requested runtime.
  - `CompositorAgent` — Compose the extended Galápagos mini-drama with all layers assembled.

## #19
**user_goal** (129 chars):

> Analyze this Bavarian Christmas-market clip and make a holiday-miracle mini-drama about siblings reuniting, and German subtitles.

**rationale:** Bavarian Christmas market reference + holiday-miracle remake + German subtitles. Chain: IntakeVideo → VideoAnalysis → Story → Screenplay → KeyFrame → Video → Transcription → Compositor → done.

**plan:**
  - `IntakeVideoAgent` — Ingest the Bavarian Christmas-market clip into the workspace as the reference.
  - `VideoAnalysisAgent` — Analyze the clip to extract market atmosphere and festive mood.
  - `StoryAgent` — Write a holiday-miracle reunion mini-drama at the market.
  - `ScreenplayAgent` — Break the story into reunion scenes across the market.
  - `KeyFrameAgent` — Design key frames inspired by the Christmas-market layout.
  - `VideoAgent` — Render motion-video clips preserving the market's festive identity.
  - `TranscriptionAgent` — Transcribe the German dialogue across the scenes into timestamped SRT.
  - `CompositorAgent` — Compose the final holiday mini-drama with German subtitles and mixed audio.

## #20
**user_goal** (173 chars):

> Make a pirate-adventure mini-drama where the captain's daughter takes over her dead father's ship to hunt the rival crew, with adventure music and ocean-wind ambient sounds.

**rationale:** Pirate-revenge daughter-captain drama + adventure music + ocean-wind ambient.

**plan:**
  - `StoryAgent` — Write the pirate story of the daughter taking over her father's ship.
  - `ScreenplayAgent` — Break the story into pirate-adventure scenes with revenge beats.
  - `KeyFrameAgent` — Design key frames for the pirate ship and daughter-captain.
  - `VideoAgent` — Render motion-video clips preserving pirate-adventure continuity.
  - `MusicAgent` — Compose an adventure BGM fitting the pirate-revenge tone.
  - `AmbienceAgent` — Generate ocean-wind ambient (wind, sail creaks, seagulls).
  - `AudioMixAgent` — Mix the adventure BGM, ocean ambient, and baked-in audio.
  - `CompositorAgent` — Compose the final pirate mini-drama with all layers assembled.

## #21
**user_goal** (99 chars):

> Restyle this underwater reef clip as a neon bioluminescence abstract and add an ethereal synth BGM.

**rationale:** Underwater reef + neon bioluminescence abstract style + ethereal synth BGM. IntakeVideoAgent → StyleTransferAgent (neon bioluminescence) → MusicAgent (ethereal synth) → AudioMixAgent → CompositorAgent.

**plan:**
  - `IntakeVideoAgent` — Ingest the underwater reef clip into the workspace.
  - `StyleTransferAgent` — Restyle the reef footage into a neon-bioluminescence abstract aesthetic.
  - `MusicAgent` — Compose an ethereal synth BGM fitting the neon underwater mood.
  - `AudioMixAgent` — Mix the synth BGM with the styled reef clip's baked audio.
  - `CompositorAgent` — Compose the styled clip with the mixed synth BGM overlaid on the neon-reef frames.

## #22
**user_goal** (133 chars):

> Please extend this 5-second clip of a tea being poured from a kettle. Stretch to 15 seconds — the pour continues steadily into a cup.

**rationale:** 5-second tea-pour clip + extend-to-15s with steady continuation into the cup. IntakeVideoAgent ingests the clip. VideoExtendAgent continues the pour motion until the cup reaches a natural filling point. Output is the raw extended clip.

**plan:**
  - `IntakeVideoAgent` — Ingest the 5-second tea-pouring-from-kettle clip into the workspace.
  - `VideoExtendAgent` — Extend the tea-pour footage to ~15 seconds with the pour continuing steadily into the cup.

## #23
**user_goal** (194 chars):

> Make a workplace-revenge mini-drama where an analyst dismissed for whistleblowing rebuilds her career at a rival firm and dismantles her old boss's insider-trading ring, with tense thriller BGM.

**rationale:** Workplace-revenge mini-drama from a text brief + tense thriller BGM. StoryAgent drafts the analyst-whistleblower / corporate-revenge blueprint. ScreenplayAgent breaks it into workplace-thriller scenes. KeyFrameAgent plans keyframes for the corporate settings from text alone. VideoAgent assembles the multi-shot film. MusicAgent composes the thriller score. AudioMixAgent layers it under the dialogue+foley. CompositorAgent muxes the final mp4. Reject AmbienceAgent (no environmental ask), Transcription/Translation (no subtitle), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Narration/Illustration/Narrator (cinematic film, not slideshow).

**plan:**
  - `StoryAgent` — Draft the workplace-revenge story blueprint — analyst-whistleblower arc and corporate-takedown progression.
  - `ScreenplayAgent` — Decompose the revenge arc into workplace-thriller scenes with escalating tension.
  - `KeyFrameAgent` — Plan keyframes for the corporate settings; text-only generation, no reference images supplied.
  - `VideoAgent` — Render per-shot clips preserving workplace-thriller visual continuity across the corporate cuts.
  - `MusicAgent` — Compose the tense thriller BGM the user requested, matching the corporate-revenge register.
  - `AudioMixAgent` — Layer the thriller score under the clip's baked dialogue+foley track into one final mixed wav.
  - `CompositorAgent` — Composite the final workplace-revenge mini-drama mp4 with mixed audio and inter-shot transitions.

## #24
**user_goal** (102 chars):

> Using this uploaded image of a foggy English moor, make an extended-length Brontë-style romance drama.

**rationale:** Image-referenced English-moor Brontë-romance extended + lush period-strings. Chain: IntakeImage → BriefEnricher → Story → Screenplay → KeyFrame → Video → VideoExtend → Compositor → done.

**plan:**
  - `IntakeImageAgent` — Ingest the uploaded foggy English-moor image as the visual reference.
  - `BriefEnricherAgent` — Enrich the setting brief combining moor atmosphere with Brontë-romance concept.
  - `StoryAgent` — Write the Brontë-style romance story on the moor.
  - `ScreenplayAgent` — Break the story into Brontë-moor romance scenes.
  - `KeyFrameAgent` — Design key frames matching the uploaded moor landscape.
  - `VideoAgent` — Render motion-video clips preserving the moor continuity.
  - `VideoExtendAgent` — Extend the moor-romance clips to the longer requested runtime.
  - `CompositorAgent` — Compose the extended Brontë mini-drama with all layers assembled.

## #25
**user_goal** (138 chars):

> Extend this 8-second clip of a train passing through a station. Please stretch to about 25 seconds as the train continues to roll through.

**rationale:** 8-second train-at-station clip + extend-to-25s with train continuing through. IntakeVideoAgent loads the clip. VideoExtendAgent extrapolates additional coach passes preserving the motion and perspective. Output is the raw extended clip.

**plan:**
  - `IntakeVideoAgent` — Ingest the 8-second train-passing-station clip into the workspace.
  - `VideoExtendAgent` — Extend the train-passing footage to ~25 seconds with the train continuing to roll through.

## #26
**user_goal** (89 chars):

> From this 2-hour basketball game, pull the best dunks and add some energetic hip-hop BGM.

**rationale:** Basketball game + dunks highlight + energetic hip-hop BGM. IntakeVideoAgent ingests. VideoAnalysisAgent identifies dunks. HighlightAgent extracts the dunks. MusicAgent composes the hip-hop cue. AudioMixAgent mixes BGM with the highlight audio. CompositorAgent muxes onto the reel. Reject Ambience (music only), Transcription / Translation (no subtitle), Style / Extend (no visual / length change).

**plan:**
  - `IntakeVideoAgent` — Ingest the 2-hour basketball-game recording into the workspace.
  - `VideoAnalysisAgent` — Analyze the game to locate dunk events.
  - `HighlightAgent` — Extract the dunks as highlight segments.
  - `MusicAgent` — Compose an energetic hip-hop BGM cue fitting the dunk highlight reel.
  - `AudioMixAgent` — Mix the hip-hop BGM with the highlight reel's baked audio.
  - `CompositorAgent` — Compose the dunk highlight reel with the mixed BGM overlaid on the cuts.

## #27
**user_goal** (177 chars):

> Make an angel-mortal romance mini-drama where a fallen angel takes a job at a bookstore and meets the human she once visited as a guardian decades ago, with ethereal choral BGM.

**rationale:** Angel-mortal romance mini-drama from a text brief + ethereal choral BGM. StoryAgent drafts the fallen-angel / bookstore / guardian-recognition blueprint. ScreenplayAgent breaks it into angel-mortal romance scenes. KeyFrameAgent plans keyframes for the bookstore / coffee-shop / rooftop settings from text alone. VideoAgent assembles the multi-shot film. MusicAgent composes the choral score. AudioMixAgent layers it under the dialogue+foley. CompositorAgent muxes the final mp4. Reject AmbienceAgent, Transcription/Translation, VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight, Narration/Illustration/Narrator.

**plan:**
  - `StoryAgent` — Draft the angel-mortal romance story blueprint — fallen-angel bookstore-job and guardian-recognition arc.
  - `ScreenplayAgent` — Decompose the angel-mortal arc into ethereal romance scenes.
  - `KeyFrameAgent` — Plan keyframes for the bookstore / coffee-shop / rooftop settings; text-only generation, no reference images supplied.
  - `VideoAgent` — Render per-shot clips preserving angel-mortal romance visual continuity.
  - `MusicAgent` — Compose the ethereal choral BGM the user requested, matching the angel-mortal register.
  - `AudioMixAgent` — Layer the choral score under the clip's baked dialogue+foley track into one final mixed wav.
  - `CompositorAgent` — Composite the final angel-mortal romance mini-drama mp4 with mixed audio and inter-shot transitions.

## #28
**user_goal** (1307 chars):

> Here's my story I want to process: In the high mountains of a country whose name has been forgotten, there once lived a tiny snow-cat named Kiri. Kiri was smaller than any of her siblings — so small that when her mother counted her kittens at the end of each night, she sometimes missed Kiri and had to count again. Kiri was also the quietest. She did not meow much. But she watched everything. She w... [+907 chars]

**rationale:** Long-form children's-fable / illustrated-storytelling brief — Kiri's arc as narrated by the user's prose. NarrationAgent writes the narrator script split into picture-aligned segments with per-segment image_prompt and per-line TTS text. IllustrationAgent generates one illustration per segment. NarratorAgent renders the script as a narrator wav + line-level SRT + per-segment timing for slideshow alignment. CompositorAgent muxes the illustrated-audiobook slideshow as a polished mp4. Reject MusicAgent / AmbienceAgent / AudioMixAgent (no audio overlay layer asked beyond narrator), TranscriptionAgent / TranslationAgent (no subtitle / multilingual ask), VideoAnalysisAgent / IntakeVideoAgent / StyleTransferAgent / VideoExtendAgent / HighlightAgent (story is pasted prose, no source clip), StoryAgent / ScreenplayAgent / KeyFrameAgent / VideoAgent (slideshow voiceover, not multi-shot camera-driven film), IntakeImageAgent / BriefEnricherAgent (no image upload to ingest).

**plan:**
  - `NarrationAgent` — Outline the user's long-form fable into a narrator script tracing Kiri's arc — split into illustration-aligned segments with per-segment image_prompt and per-line TTS text.
  - `IllustrationAgent` — Plan one illustration per narrator segment in picture-book style, depicting Kiri's setting and key moments described in the user's prose.
  - `NarratorAgent` — Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level SRT + per-segment timing for slideshow alignment.
  - `CompositorAgent` — Composite the final illustrated-audiobook slideshow — segment illustrations timed to the narrator wav, encoded as a polished mp4.

## #29
**user_goal** (75 chars):

> Please extract the most intense fight scenes from this 2-hour boxing match.

**rationale:** 2-hour boxing match + request for intense fight scenes only. IntakeVideoAgent ingests the match. VideoAnalysisAgent identifies high-intensity exchanges (combo flurries, knockdowns). HighlightAgent cuts those segments. Raw cut list delivered.

**plan:**
  - `IntakeVideoAgent` — Ingest the 2-hour boxing-match recording into the workspace.
  - `VideoAnalysisAgent` — Analyze the boxing match to locate the most-intense exchange and knockdown moments.
  - `HighlightAgent` — Extract the intense fight-scene moments as highlight segments.

## #30
**user_goal** (137 chars):

> From this 3-hour Portuguese soccer broadcast, extract the goals, add Portuguese + English bilingual subs, and add a heroic cinematic BGM.

**rationale:** Portuguese soccer broadcast + goals + Portuguese+English bilingual + heroic cinematic BGM.

**plan:**
  - `IntakeVideoAgent` — Ingest the 3-hour Portuguese soccer-commentary broadcast into the workspace.
  - `VideoAnalysisAgent` — Analyze the broadcast to locate goal events.
  - `HighlightAgent` — Extract the goals as highlight segments.
  - `TranscriptionAgent` — Transcribe the Portuguese commentary on the segments into SRT.
  - `TranslationAgent` — Translate the Portuguese SRT segments into English subtitles.
  - `MusicAgent` — Compose a heroic cinematic BGM fitting the goal highlight reel.
  - `AudioMixAgent` — Mix the cinematic BGM with the highlight reel's baked audio.
  - `CompositorAgent` — Compose the reel with bilingual Portuguese-English captions and cinematic BGM overlaid on the cuts.

## #31
**user_goal** (111 chars):

> Please analyze this Polish historical-drama clip, add Polish subtitles, and swap in a haunting folk-violin BGM.

**rationale:** Polish historical drama + analysis + Polish subtitles + haunting folk-violin BGM. IntakeVideoAgent → VideoAnalysisAgent → TranscriptionAgent (Polish) → MusicAgent (haunting folk violin) → AudioMixAgent → CompositorAgent.

**plan:**
  - `IntakeVideoAgent` — Ingest the Polish historical-drama clip into the workspace.
  - `VideoAnalysisAgent` — Analyze the clip for dialogue structure and historical-scene content.
  - `TranscriptionAgent` — Transcribe the Polish dialogue into timestamped SRT segments.
  - `MusicAgent` — Compose a haunting folk-violin BGM fitting the Polish historical mood.
  - `AudioMixAgent` — Mix the violin BGM with the dialogue audio.
  - `CompositorAgent` — Compose the clip with Polish captions and mixed violin BGM overlaid on the footage.

## #32
**user_goal** (131 chars):

> Make a mini-drama about an ornithologist tracking the last known wild whooping crane through a misty wetland, with wetland ambient.

**rationale:** Mini-drama from a text brief + wetland ambient. StoryAgent drafts the ornithologist / last-wild-whooping-crane / misty-wetland blueprint. ScreenplayAgent breaks it into nature-tracking scenes. KeyFrameAgent plans keyframes for the misty-wetland settings from text alone. VideoAgent assembles the multi-shot film. AmbienceAgent generates the wetland room-tone bed. AudioMixAgent layers it under the dialogue+foley. CompositorAgent muxes the final mp4. Reject MusicAgent, Transcription/Translation, VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight, Narration/Illustration/Narrator.

**plan:**
  - `StoryAgent` — Draft the ornithologist story blueprint — tracking last wild whooping-crane through misty wetland arc.
  - `ScreenplayAgent` — Decompose the tracking arc into nature-drama scenes.
  - `KeyFrameAgent` — Plan keyframes for the misty-wetland settings; text-only generation, no reference images supplied.
  - `VideoAgent` — Render per-shot clips preserving nature-drama visual continuity.
  - `AmbienceAgent` — Generate the wetland ambient bed the user requested, matching the misty-wetland environment.
  - `AudioMixAgent` — Layer the wetland ambience bed under the clip's baked dialogue+foley track into one final mixed wav.
  - `CompositorAgent` — Composite the final ornithologist mini-drama mp4 with mixed audio and inter-shot transitions.

## #33
**user_goal** (88 chars):

> I have a 2-hour hockey game recording. Please just cut out the goals, saves, and fights.

**rationale:** 2-hour hockey game + request for goals / saves / fights highlight. IntakeVideoAgent ingests the game. VideoAnalysisAgent identifies scoring, big saves, and fights through content cues. HighlightAgent cuts those segments. Raw cut list delivered.

**plan:**
  - `IntakeVideoAgent` — Ingest the 2-hour hockey-game recording into the workspace.
  - `VideoAnalysisAgent` — Analyze the hockey game to locate goals, big saves, and fights.
  - `HighlightAgent` — Extract the hockey highlights as segments.

## #34
**user_goal** (126 chars):

> Make a Thai-English bilingual Chiang Mai mini-drama about a young monk-novice returning to the temple after a crisis of faith.

**rationale:** Chiang Mai monk-novice drama + Thai+English bilingual. Chain: Story → Screenplay → KeyFrame → Video → Transcription → Translation → Compositor → done.

**plan:**
  - `StoryAgent` — Write the Chiang Mai monk-novice return story.
  - `ScreenplayAgent` — Break the story into temple-return scenes.
  - `KeyFrameAgent` — Design key frames for the Chiang Mai temple.
  - `VideoAgent` — Render motion-video clips preserving Chiang Mai continuity.
  - `TranscriptionAgent` — Transcribe the Thai dialogue into timestamped SRT.
  - `TranslationAgent` — Translate the Thai SRT into English subtitles.
  - `CompositorAgent` — Compose the Chiang Mai mini-drama with bilingual Thai-English captions and mixed audio.

## #35
**user_goal** (121 chars):

> Using this uploaded image of a Nairobi rooftop, make a young-entrepreneur mini-drama with Swahili+English bilingual subs.

**rationale:** Image-referenced Nairobi-rooftop entrepreneur + Swahili+English bilingual + Afrobeats. Chain: IntakeImage → BriefEnricher → Story → Screenplay → KeyFrame → Video → Transcription → Translation → Compositor → done.

**plan:**
  - `IntakeImageAgent` — Ingest the uploaded Nairobi-rooftop image as the visual reference.
  - `BriefEnricherAgent` — Enrich the setting brief combining rooftop atmosphere with entrepreneur concept.
  - `StoryAgent` — Write the young-entrepreneur story at the Nairobi rooftop.
  - `ScreenplayAgent` — Break the story into entrepreneur scenes.
  - `KeyFrameAgent` — Design key frames matching the uploaded Nairobi-rooftop view.
  - `VideoAgent` — Render motion-video clips preserving the Nairobi continuity.
  - `TranscriptionAgent` — Transcribe the Swahili dialogue into timestamped SRT.
  - `TranslationAgent` — Translate the Swahili SRT into English subtitles.
  - `CompositorAgent` — Compose the Nairobi mini-drama with bilingual Swahili-English captions and all audio layers.

## #36
**user_goal** (127 chars):

> Could you add German subtitles to this kitchen-tutorial I shot for my YouTube channel? The instructor speaks German throughout.

**rationale:** German-spoken kitchen tutorial + request for German captions to aid viewers. The flow is IntakeVideoAgent → TranscriptionAgent → CompositorAgent. TranscriptionAgent handles German speech natively into a timestamped SRT; CompositorAgent renders those captions onto the tutorial. Translation is not needed since the author wants German captions on German audio. No audio, style, or length modification was asked for, so Music / Ambience / AudioMix / StyleTransfer / VideoExtend stay out.

**plan:**
  - `IntakeVideoAgent` — Ingest the German-spoken kitchen tutorial into the workspace.
  - `TranscriptionAgent` — Transcribe the instructor's German speech into timestamped SRT caption lines.
  - `CompositorAgent` — Compose the final tutorial with German captions burned onto the footage.

## #37
**user_goal** (113 chars):

> Using this uploaded image of an Indian palace, make a Rajput princess mini-drama about defying a forced alliance.

**rationale:** Indian-palace image + Rajput princess drama. Chain: IntakeImage → BriefEnricher → Story → Screenplay → KeyFrame → Video → Compositor → done.

**plan:**
  - `IntakeImageAgent` — Ingest the uploaded Indian-palace image into the workspace as the visual reference.
  - `BriefEnricherAgent` — Enrich the setting brief combining the palace atmosphere with the Rajput-princess concept.
  - `StoryAgent` — Write a Rajput princess mini-drama about defying a forced alliance.
  - `ScreenplayAgent` — Break the story into princess-drama scenes across the palace.
  - `KeyFrameAgent` — Design key frames matching the uploaded palace architecture.
  - `VideoAgent` — Render motion-video clips preserving the palace's visual identity.
  - `CompositorAgent` — Compose the final Rajput mini-drama with all layers assembled.

## #38
**user_goal** (143 chars):

> Create an English-Hawaiian bilingual illustrated audiobook of this Hawaiian legend about the rainbow sister with a gentle slack-key guitar BGM.

**rationale:** Long-form illustrated-storytelling brief — the protagonist's arc + music score + bilingual / foreign-language subtitle ask. NarrationAgent writes the narrator script split into picture-aligned segments. IllustrationAgent generates one illustration per segment. NarratorAgent renders the script as voiceover wav + source-language SRT (timed). MusicAgent composes the music score the user specified. AudioMixAgent layers the music under the narrator wav. TranslationAgent translates the source SRT into the target language preserving timing. CompositorAgent muxes the slideshow with mixed audio + both subtitle tracks. Reject AmbienceAgent (no environmental ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow, not multi-shot film), IntakeImage/BriefEnricher (no image upload). Reject TranscriptionAgent — narrator already produces a timed SRT.

**plan:**
  - `NarrationAgent` — Draft the user's storytelling brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with per-segment image_prompt + per-line TTS text.
  - `IllustrationAgent` — Render one illustration per narrator segment in picture-book style, depicting the protagonist's setting and key moments.
  - `NarratorAgent` — Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level source-language SRT + per-segment timing.
  - `MusicAgent` — Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.
  - `AudioMixAgent` — Layer the music score under the narrator wav into one final mixed wav.
  - `TranslationAgent` — Translate the narrator SRT into the user-specified target language, preserving every segment's timing intact.
  - `CompositorAgent` — Composite the final illustrated-audiobook slideshow — segment illustrations timed to the mixed audio, both source and translated subtitles burned in.

## #39
**user_goal** (132 chars):

> Make a survival mini-drama about a hiker lost in a snowstorm who takes shelter in an abandoned cabin, with snowstorm ambient sounds.

**rationale:** Survival mini-drama from a text brief + snowstorm ambient sounds. StoryAgent drafts the lost-hiker / abandoned-cabin shelter blueprint. ScreenplayAgent breaks it into survival-drama scenes. KeyFrameAgent plans keyframes for the snowstorm / cabin settings from text alone. VideoAgent assembles the multi-shot film. AmbienceAgent generates the snowstorm room-tone bed. AudioMixAgent layers it under the dialogue+foley. CompositorAgent muxes the final mp4. Reject MusicAgent, Transcription/Translation, VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight, Narration/Illustration/Narrator.

**plan:**
  - `StoryAgent` — Draft the survival story blueprint — lost-hiker snowstorm-shelter in abandoned-cabin arc.
  - `ScreenplayAgent` — Decompose the survival arc into snowstorm-shelter scenes.
  - `KeyFrameAgent` — Plan keyframes for the snowstorm / abandoned-cabin settings; text-only generation, no reference images supplied.
  - `VideoAgent` — Render per-shot clips preserving survival-drama visual continuity.
  - `AmbienceAgent` — Generate the snowstorm ambient bed the user requested, matching the snowstorm-and-cabin environment.
  - `AudioMixAgent` — Layer the snowstorm ambience bed under the clip's baked dialogue+foley track into one final mixed wav.
  - `CompositorAgent` — Composite the final survival mini-drama mp4 with mixed audio and inter-shot transitions.

## #40
**user_goal** (106 chars):

> Make a monster-hunter mini-drama about a scarred huntress who tracks a cursed wolf through a misty forest.

**rationale:** Monster-hunter fantasy drama, no audio requested.

**plan:**
  - `StoryAgent` — Write the monster-hunter story of the huntress tracking the cursed wolf.
  - `ScreenplayAgent` — Break the story into hunter-track-and-confront scenes.
  - `KeyFrameAgent` — Design key frames for the misty forest and cursed wolf.
  - `VideoAgent` — Render motion-video clips preserving monster-hunter continuity.
  - `CompositorAgent` — Compose the final monster-hunter mini-drama assembly.

## #41
**user_goal** (103 chars):

> I have a 5-hour marathon race recording. Please pull the race-leader overtakes and finish-line moments.

**rationale:** 5-hour marathon race + request for overtakes + finish-line moments highlight. IntakeVideoAgent ingests the race. VideoAnalysisAgent identifies lead-change events and finish-line crossings. HighlightAgent cuts those. Raw cut list delivered.

**plan:**
  - `IntakeVideoAgent` — Ingest the 5-hour marathon-race recording into the workspace.
  - `VideoAnalysisAgent` — Analyze the marathon to locate lead-change overtakes and finish-line moments.
  - `HighlightAgent` — Extract those race-leader overtakes and finish-line moments as highlight segments.

## #42
**user_goal** (129 chars):

> Make a mini-drama about a young monk spending her first winter alone in a remote mountain cave meditating, with ice-cave ambient.

**rationale:** Mini-drama from a text brief + ice-cave ambient. StoryAgent drafts the young-monk / first-winter-alone / remote-mountain-cave-meditation blueprint. ScreenplayAgent breaks it into solitary-meditation scenes. KeyFrameAgent plans keyframes for the ice-cave settings from text alone. VideoAgent assembles the multi-shot film. AmbienceAgent generates the ice-cave room-tone bed. AudioMixAgent layers it under the dialogue+foley. CompositorAgent muxes the final mp4. Reject MusicAgent, Transcription/Translation, VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight, Narration/Illustration/Narrator.

**plan:**
  - `StoryAgent` — Draft the young-monk story blueprint — first winter alone in remote mountain ice-cave meditation arc.
  - `ScreenplayAgent` — Decompose the meditation arc into solitary-meditation scenes.
  - `KeyFrameAgent` — Plan keyframes for the ice-cave settings; text-only generation, no reference images supplied.
  - `VideoAgent` — Render per-shot clips preserving solitary-meditation visual continuity.
  - `AmbienceAgent` — Generate the ice-cave ambient bed the user requested, matching the icy-cave environment.
  - `AudioMixAgent` — Layer the ice-cave ambience bed under the clip's baked dialogue+foley track into one final mixed wav.
  - `CompositorAgent` — Composite the final young-monk mini-drama mp4 with mixed audio and inter-shot transitions.

## #43
**user_goal** (1105 chars):

> Here's my story I want to process: When Claire Delacroix was eleven years old her mother married into the Havenwood family and Claire was taken to live in a house she would grow to hate. Havenwood was a tall gray Victorian on a Louisiana bayou, built by a family of cane planters in 1871, with wrought-iron galleries and shuttered rooms and a long history of quiet dying. The housekeeper, Mrs. Peltie... [+705 chars]

**rationale:** Long-form cinematic creative-film brief — the protagonist's arc as outlined in the user's prose. No audio overlay, no subtitles, no image upload, no source video. StoryAgent drafts the story blueprint. ScreenplayAgent decomposes it into scene/shot structure. KeyFrameAgent plans keyframes from text alone (no reference images). VideoAgent renders per-shot clips with baked dialogue+foley audio (sufficient on its own — no extra audio layer requested). CompositorAgent muxes the final mp4 with the video's existing audio. Reject MusicAgent / AmbienceAgent / AudioMixAgent (no BGM or environmental layer asked), Transcription/Translation (no subtitle / multilingual ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (story is pasted prose, not source clip), Narration/Illustration/Narrator (cinematic multi-shot film, not slideshow voiceover), IntakeImage/BriefEnricher (no image upload to ingest).

**plan:**
  - `StoryAgent` — Draft the user's long-form cinematic prose into a story blueprint capturing the protagonist's arc, characters, locations, and tonal beats.
  - `ScreenplayAgent` — Decompose the the protagonist story blueprint into a scene/shot screenplay with per-scene mood and estimated duration.
  - `KeyFrameAgent` — Render per-shot keyframes from the screenplay; text-only generation, no reference images supplied.
  - `VideoAgent` — Render per-shot motion clips from the keyframes via image-to-video synthesis; the assembled film carries baked dialogue+foley per clip.
  - `CompositorAgent` — Composite the final cinematic mp4 by muxing the video's existing dialogue+foley track with inter-shot transitions and final encoding.

## #44
**user_goal** (85 chars):

> Add some Appalachian banjo folk music to this Smoky-Mountains fall-foliage timelapse.

**rationale:** Smoky-Mountains fall-foliage timelapse + request for Appalachian banjo folk BGM. IntakeVideoAgent loads the timelapse. MusicAgent composes an Appalachian banjo folk cue. AudioMixAgent mixes it with the timelapse's ambient audio. CompositorAgent muxes the final audio.

**plan:**
  - `IntakeVideoAgent` — Ingest the Smoky-Mountains fall-foliage timelapse into the workspace.
  - `MusicAgent` — Compose an Appalachian banjo folk BGM fitting the mountain-foliage vibe.
  - `AudioMixAgent` — Mix the banjo folk BGM with the timelapse's ambient audio.
  - `CompositorAgent` — Compose the timelapse with the mixed banjo BGM overlaid on the foliage footage.

## #45
**user_goal** (156 chars):

> Extend this monsoon-rooftop-tea scene by 10 seconds, adding heavy monsoon rain on the tin roof, rolling thunder, and the kettle whistling as ambient sounds.

**rationale:** Monsoon-rooftop extension + rain+thunder+kettle ambient. Chain: IntakeVideo → VideoExtend → Ambience → AudioMix → Compositor → done.

**plan:**
  - `IntakeVideoAgent` — Ingest the monsoon-rooftop-tea clip into the workspace.
  - `VideoExtendAgent` — Extend the tea scene by 10 seconds with the rain intensifying.
  - `AmbienceAgent` — Generate monsoon ambient: heavy rain on tin roof, distant thunder, kettle whistling.
  - `AudioMixAgent` — Mix the monsoon ambient with the extended clip's baked audio.
  - `CompositorAgent` — Composite the final extended tea scene with the ambient overlay.

## #46
**user_goal** (113 chars):

> Extend this 4-second Thai street-food clip to 15 seconds, restyle as Ghibli slice-of-life, and add Thai captions.

**rationale:** Thai street-food + extend-to-15s + Ghibli slice-of-life + Thai (monolingual) captions. IntakeVideoAgent → VideoExtendAgent (~15s) → StyleTransferAgent (Ghibli slice-of-life) → TranscriptionAgent (Thai) → CompositorAgent.

**plan:**
  - `IntakeVideoAgent` — Ingest the 4-second Thai street-food clip into the workspace.
  - `VideoExtendAgent` — Extend the street-food clip to ~15 seconds continuing the cooking action.
  - `StyleTransferAgent` — Restyle the extended clip into a Studio Ghibli slice-of-life aesthetic.
  - `TranscriptionAgent` — Transcribe the extended Thai narration into timestamped SRT.
  - `CompositorAgent` — Compose the styled-extended clip with Thai captions burned onto the Ghibli frames.

## #47
**user_goal** (1129 chars):

> Here's my story I want to process: A colony of ants lived under the front step of a small cottage on a quiet lane. They had been there for generations. Their queen was wise. Their tunnels ran very deep. One rainy spring, a great storm washed out part of the cottage's foundation, and a human carpenter came to repair it. The carpenter was a quiet young man named Jon. He noticed the ant colony while ... [+729 chars]

**rationale:** Long-form children's-fable / illustrated-storytelling brief — Jon's arc as narrated by the user's prose. NarrationAgent writes the narrator script split into picture-aligned segments with per-segment image_prompt and per-line TTS text. IllustrationAgent generates one illustration per segment. NarratorAgent renders the script as a narrator wav + line-level SRT + per-segment timing for slideshow alignment. CompositorAgent muxes the illustrated-audiobook slideshow as a polished mp4. Reject MusicAgent / AmbienceAgent / AudioMixAgent (no audio overlay layer asked beyond narrator), TranscriptionAgent / TranslationAgent (no subtitle / multilingual ask), VideoAnalysisAgent / IntakeVideoAgent / StyleTransferAgent / VideoExtendAgent / HighlightAgent (story is pasted prose, no source clip), StoryAgent / ScreenplayAgent / KeyFrameAgent / VideoAgent (slideshow voiceover, not multi-shot camera-driven film), IntakeImageAgent / BriefEnricherAgent (no image upload to ingest).

**plan:**
  - `NarrationAgent` — Compose the user's long-form fable into a narrator script tracing Jon's arc — split into illustration-aligned segments with per-segment image_prompt and per-line TTS text.
  - `IllustrationAgent` — Design one illustration per narrator segment in picture-book style, depicting Jon's setting and key moments described in the user's prose.
  - `NarratorAgent` — Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level SRT + per-segment timing for slideshow alignment.
  - `CompositorAgent` — Composite the final illustrated-audiobook slideshow — segment illustrations timed to the narrator wav, encoded as a polished mp4.

## #48
**user_goal** (96 chars):

> Make an Arabic-subtitled Bedouin desert-drama about a young woman saving her tribe from a rival.

**rationale:** Bedouin desert-heroine drama + Arabic subs. Chain: Story → Screenplay → KeyFrame → Video → Transcription → Compositor → done.

**plan:**
  - `StoryAgent` — Write the Bedouin desert-heroine story.
  - `ScreenplayAgent` — Break the story into Bedouin-desert scenes.
  - `KeyFrameAgent` — Design key frames for the Bedouin desert camp and heroine.
  - `VideoAgent` — Render motion-video clips preserving the Bedouin-drama continuity.
  - `TranscriptionAgent` — Transcribe the Arabic dialogue into timestamped SRT.
  - `CompositorAgent` — Compose the final Bedouin mini-drama with Arabic captions and mixed audio.

## #49
**user_goal** (211 chars):

> Using this uploaded portrait of a rainbow-scaled sea-dragon, turn this short myth into an illustrated audiobook where the appearance stays consistent, with a gentle waterphone-and-harp score under the narration.

**rationale:** Rainbow-scaled sea-dragon + illustrated audiobook + gentle-waterphone-and-harp BGM. Chain: IntakeImage → BriefEnricher → Narration → Illustration → Narrator → Music → AudioMix → Compositor. Reject AmbienceAgent (music only asked), TranslationAgent (no bilingual ask), Story/Screenplay/KeyFrame/Video (those belong to live-action mini-drama, not illustrated-audiobook slideshow).

**plan:**
  - `IntakeImageAgent` — Ingest the uploaded sea-dragon portrait as the visual reference.
  - `BriefEnricherAgent` — Enrich the sea-dragon brief for consistent illustration.
  - `NarrationAgent` — Write the narration script about the sea-dragon carrying sunken letters back to grieving mothers.
  - `IllustrationAgent` — Generate one illustration per scene preserving the sea-dragon's reference likeness.
  - `NarratorAgent` — Produce a tender TTS narrator track for the sea-dragon myth.
  - `MusicAgent` — Compose a gentle waterphone-and-harp BGM fitting the sea-dragon tone.
  - `AudioMixAgent` — Mix the BGM softly under the narrator track.
  - `CompositorAgent` — Compose the slideshow with reference-consistent illustrations and mixed narrator+music audio.

## #50
**user_goal** (112 chars):

> Please turn this 6-second drone clip into Ghibli-watercolor, extend it to 20 seconds, and add a gentle folk BGM.

**rationale:** User uploaded a 6-second drone clip, asks for Ghibli watercolor style + extend to 20s + gentle folk BGM. IntakeVideoAgent ingests. StyleTransferAgent applies the Ghibli-watercolor first (so the extension inherits the styled baseline). VideoExtendAgent extends the styled clip to 20 seconds. MusicAgent composes the folk BGM. AudioMixAgent mixes BGM with baked audio. CompositorAgent muxes the audio onto the styled-extended clip.

**plan:**
  - `IntakeVideoAgent` — Ingest the 6-second drone clip into the workspace.
  - `StyleTransferAgent` — Restyle the drone footage into a Studio Ghibli watercolor aesthetic.
  - `VideoExtendAgent` — Extend the styled drone clip to ~20 seconds preserving the watercolor look.
  - `MusicAgent` — Compose a gentle folk BGM covering the extended ~20-second length.
  - `AudioMixAgent` — Mix the folk BGM with the styled-extended clip's baked audio.
  - `CompositorAgent` — Compose the final clip with the mixed folk BGM overlaid on the styled-extended drone footage.
