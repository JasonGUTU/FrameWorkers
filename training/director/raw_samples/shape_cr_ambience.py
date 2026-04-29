"""Shape: cr_ambience —
    Story → Screenplay → KeyFrame → Video → Ambience → AudioMix → Compositor.

Cinematic mini-drama WITH ambient sound, NO BGM, NO subtitles, NO image
upload. 49 short-brief samples; long variants in shape_cr_ambience_long.py.

PER-SAMPLE TAILORED design:
  - rationale: per-sample, references user-stated genre / setting + specific
    ambient ask + names what each agent does for THIS user_goal + lists
    rejects with routing-relevant reasons. Reject MusicAgent because user
    asked atmospheric / environmental sound, not music.
  - intents: per-sample, reference user_goal genre and setting keywords.
    AmbienceAgent step uses ambience-class verbs (Generate / Lay / Synthesize),
    NOT music-class verbs (Compose / Score). No invented narrative.
"""
from __future__ import annotations


SAMPLES: list[dict] = [
    {
        "user_goal": "Make a supernatural-thriller mini-drama where the female lead moves into a haunted house and finds a videotape left by the previous tenant revealing an unsolved murder, with creepy haunted-house ambient sounds.",
        "rationale": (
            "Supernatural-thriller mini-drama from a text brief + creepy haunted-house ambient "
            "sounds as audio layer. StoryAgent drafts the haunted-house / videotape / murder "
            "blueprint. ScreenplayAgent breaks it into supernatural-thriller scenes. "
            "KeyFrameAgent plans keyframes for the haunted-house settings from text alone. "
            "VideoAgent assembles the multi-shot film. AmbienceAgent generates the haunted-"
            "house room-tone bed. AudioMixAgent layers it under the dialogue+foley. "
            "CompositorAgent muxes the final mp4. Reject MusicAgent (user asked environmental "
            "ambient, not a music score), Transcription/Translation (no subtitle ask), "
            "VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), "
            "Narration/Illustration/Narrator (cinematic film, not slideshow)."
        ),
        "intents": [
            "Draft the supernatural-thriller story blueprint — haunted-house move-in, videotape discovery, and unsolved-murder arc.",
            "Decompose the haunted-house arc into supernatural-thriller scenes with escalating dread.",
            "Plan keyframes for the haunted-house settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving supernatural-thriller visual continuity.",
            "Generate the creepy haunted-house ambient bed the user requested, matching the haunted-house environment.",
            "Layer the haunted-house ambience bed under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final supernatural-thriller mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a sweet costume-drama about a female lead transmigrating into a chancellor's legitimate daughter who moves from mutual loathing to mutual redemption with a cold prince, with palace ambient atmosphere.",
        "rationale": (
            "Sweet costume-drama mini-drama from a text brief + palace ambient atmosphere. "
            "StoryAgent drafts the transmigration / chancellor's-daughter / cold-prince "
            "redemption blueprint. ScreenplayAgent breaks it into costume-drama scenes. "
            "KeyFrameAgent plans keyframes for the palace settings from text alone. VideoAgent "
            "assembles the multi-shot film. AmbienceAgent generates the palace room-tone bed. "
            "AudioMixAgent layers it under the dialogue+foley. CompositorAgent muxes the final "
            "mp4. Reject MusicAgent (user asked atmospheric layer, not a music score), "
            "Transcription/Translation, VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/"
            "Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the costume-drama story blueprint — transmigration into chancellor's daughter and cold-prince redemption arc.",
            "Decompose the redemption arc into costume-drama scenes with sweet emotional progression.",
            "Plan keyframes for the palace settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving costume-drama visual continuity across the palace cuts.",
            "Generate the palace ambient atmosphere the user requested, matching the period-palace environment.",
            "Layer the palace ambience bed under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final costume-drama mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a sci-fi animated drama about the last awakened AI falling in love with the only human engineer left, with spaceship ambient sounds.",
        "rationale": (
            "Sci-fi animated drama from a text brief + spaceship ambient sounds. StoryAgent "
            "drafts the awakened-AI / human-engineer love blueprint. ScreenplayAgent breaks "
            "it into sci-fi animated scenes. KeyFrameAgent plans animation-style keyframes "
            "for the spaceship settings from text alone. VideoAgent assembles the animated "
            "multi-shot film. AmbienceAgent generates the spaceship room-tone bed. "
            "AudioMixAgent layers it under the dialogue+foley. CompositorAgent muxes the "
            "final mp4. Reject MusicAgent (user asked environmental ambient, not music), "
            "Transcription/Translation, VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/"
            "Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the sci-fi animated story blueprint — awakened-AI and last-human-engineer love arc.",
            "Decompose the AI-human arc into sci-fi animated scenes.",
            "Plan animation-style keyframes for the spaceship settings; text-only generation, no reference images supplied.",
            "Render per-shot animated clips preserving the sci-fi spaceship aesthetic.",
            "Generate the spaceship ambient bed the user requested, matching the deep-space spacecraft environment.",
            "Layer the spaceship ambience bed under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final sci-fi animated drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make an urban-romance mini-drama where the female lead runs into her missing-for-five-years ex-boyfriend in a rainy Paris café, with rainy-café ambient sounds.",
        "rationale": (
            "Urban-romance mini-drama from a text brief + rainy-café ambient sounds. "
            "StoryAgent drafts the missing-ex / Paris-café reunion blueprint. ScreenplayAgent "
            "breaks it into urban-romance scenes. KeyFrameAgent plans keyframes for the "
            "Paris-café settings from text alone. VideoAgent assembles the multi-shot film. "
            "AmbienceAgent generates the rainy-café room-tone bed. AudioMixAgent layers it "
            "under the dialogue+foley. CompositorAgent muxes the final mp4. Reject MusicAgent, "
            "Transcription/Translation, VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/"
            "Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the urban-romance story blueprint — missing-ex Paris-café reunion arc.",
            "Decompose the reunion arc into urban-romance scenes.",
            "Plan keyframes for the rainy Paris-café settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving urban-romance visual continuity.",
            "Generate the rainy-café ambient bed the user requested, matching the Paris-rain café environment.",
            "Layer the rainy-café ambience bed under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final urban-romance mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a suspense-twist mini-drama where a therapist realizes her new patient is her sister's killer, with tense office ambient sounds.",
        "rationale": (
            "Suspense-twist mini-drama from a text brief + tense office ambient sounds. "
            "StoryAgent drafts the therapist / patient-killer-recognition blueprint. "
            "ScreenplayAgent breaks it into suspense-twist scenes. KeyFrameAgent plans "
            "keyframes for the therapy-office settings from text alone. VideoAgent assembles "
            "the multi-shot film. AmbienceAgent generates the tense-office room-tone bed. "
            "AudioMixAgent layers it under the dialogue+foley. CompositorAgent muxes the "
            "final mp4. Reject MusicAgent, Transcription/Translation, VideoAnalysis/"
            "IntakeVideo/StyleTransfer/VideoExtend/Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the suspense-twist story blueprint — therapist recognition of sister's killer arc.",
            "Decompose the recognition arc into suspense-twist scenes with escalating tension.",
            "Plan keyframes for the therapy-office settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving suspense-twist visual continuity.",
            "Generate the tense office ambient bed the user requested, matching the therapy-office environment.",
            "Layer the tense-office ambience bed under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final suspense-twist mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a fantasy mini-drama about a witch returning to her ancestral swamp cabin to reclaim forgotten magic, with deep-swamp ambient sounds.",
        "rationale": (
            "Fantasy mini-drama from a text brief + deep-swamp ambient sounds. StoryAgent "
            "drafts the witch / ancestral-swamp-cabin / magic-reclaim blueprint. "
            "ScreenplayAgent breaks it into fantasy scenes. KeyFrameAgent plans keyframes "
            "for the swamp-cabin settings from text alone. VideoAgent assembles the "
            "multi-shot film. AmbienceAgent generates the deep-swamp room-tone bed. "
            "AudioMixAgent layers it under the dialogue+foley. CompositorAgent muxes the "
            "final mp4. Reject MusicAgent, Transcription/Translation, VideoAnalysis/"
            "IntakeVideo/StyleTransfer/VideoExtend/Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the fantasy story blueprint — witch returning to ancestral swamp-cabin and reclaiming magic arc.",
            "Decompose the reclaim-magic arc into fantasy scenes.",
            "Plan keyframes for the ancestral swamp-cabin settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving fantasy visual continuity.",
            "Generate the deep-swamp ambient bed the user requested, matching the swamp-cabin environment.",
            "Layer the deep-swamp ambience bed under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final fantasy mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a period mini-drama about a Parisian opera singer in the 1890s preparing for her last performance, with opera-house-backstage ambient.",
        "rationale": (
            "1890s Parisian period mini-drama from a text brief + opera-house-backstage "
            "ambient. StoryAgent drafts the opera-singer / last-performance blueprint. "
            "ScreenplayAgent breaks it into period-drama scenes. KeyFrameAgent plans keyframes "
            "for the 1890s opera-house backstage settings from text alone. VideoAgent assembles "
            "the multi-shot film. AmbienceAgent generates the opera-house-backstage room-tone "
            "bed. AudioMixAgent layers it under the dialogue+foley. CompositorAgent muxes the "
            "final mp4. Reject MusicAgent, Transcription/Translation, VideoAnalysis/IntakeVideo/"
            "StyleTransfer/VideoExtend/Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the period story blueprint — 1890s Parisian opera-singer last-performance arc.",
            "Decompose the last-performance arc into 1890s period-drama scenes.",
            "Plan keyframes for the opera-house-backstage settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving 1890s Parisian period aesthetic.",
            "Generate the opera-house-backstage ambient bed the user requested, matching the backstage environment.",
            "Layer the opera-backstage ambience bed under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final 1890s-period mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a hospital-drama mini-drama about a pediatric-ICU nurse on the night shift handling a crisis, with ICU-ambient sounds.",
        "rationale": (
            "Hospital-drama mini-drama from a text brief + ICU-ambient sounds. StoryAgent "
            "drafts the pediatric-ICU-nurse / night-shift-crisis blueprint. ScreenplayAgent "
            "breaks it into hospital-drama scenes. KeyFrameAgent plans keyframes for the "
            "ICU settings from text alone. VideoAgent assembles the multi-shot film. "
            "AmbienceAgent generates the ICU room-tone bed. AudioMixAgent layers it under "
            "the dialogue+foley. CompositorAgent muxes the final mp4. Reject MusicAgent, "
            "Transcription/Translation, VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/"
            "Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the hospital-drama story blueprint — pediatric-ICU-nurse night-shift crisis arc.",
            "Decompose the night-shift-crisis arc into hospital-drama scenes.",
            "Plan keyframes for the pediatric-ICU settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving hospital-drama visual continuity.",
            "Generate the ICU ambient bed the user requested, matching the pediatric-ICU environment.",
            "Layer the ICU ambience bed under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final hospital-drama mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a survival mini-drama about a hiker lost in a snowstorm who takes shelter in an abandoned cabin, with snowstorm ambient sounds.",
        "rationale": (
            "Survival mini-drama from a text brief + snowstorm ambient sounds. StoryAgent "
            "drafts the lost-hiker / abandoned-cabin shelter blueprint. ScreenplayAgent breaks "
            "it into survival-drama scenes. KeyFrameAgent plans keyframes for the snowstorm "
            "/ cabin settings from text alone. VideoAgent assembles the multi-shot film. "
            "AmbienceAgent generates the snowstorm room-tone bed. AudioMixAgent layers it "
            "under the dialogue+foley. CompositorAgent muxes the final mp4. Reject MusicAgent, "
            "Transcription/Translation, VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/"
            "Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the survival story blueprint — lost-hiker snowstorm-shelter in abandoned-cabin arc.",
            "Decompose the survival arc into snowstorm-shelter scenes.",
            "Plan keyframes for the snowstorm / abandoned-cabin settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving survival-drama visual continuity.",
            "Generate the snowstorm ambient bed the user requested, matching the snowstorm-and-cabin environment.",
            "Layer the snowstorm ambience bed under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final survival mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a horror mini-drama about a young researcher trapped in an abandoned sanatorium overnight, with abandoned-sanatorium ambient.",
        "rationale": (
            "Horror mini-drama from a text brief + abandoned-sanatorium ambient. StoryAgent "
            "drafts the researcher / abandoned-sanatorium / overnight-trap blueprint. "
            "ScreenplayAgent breaks it into horror scenes. KeyFrameAgent plans keyframes for "
            "the abandoned-sanatorium settings from text alone. VideoAgent assembles the "
            "multi-shot film. AmbienceAgent generates the abandoned-sanatorium room-tone bed. "
            "AudioMixAgent layers it under the dialogue+foley. CompositorAgent muxes the "
            "final mp4. Reject MusicAgent, Transcription/Translation, VideoAnalysis/"
            "IntakeVideo/StyleTransfer/VideoExtend/Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the horror story blueprint — researcher trapped in abandoned-sanatorium overnight arc.",
            "Decompose the trap arc into horror scenes with escalating dread.",
            "Plan keyframes for the abandoned-sanatorium settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving horror visual continuity.",
            "Generate the abandoned-sanatorium ambient bed the user requested, matching the eerie sanatorium environment.",
            "Layer the sanatorium ambience bed under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final horror mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a Japanese-inspired mini-drama about a young woman tending her dying grandfather's tea garden, with traditional Japanese-garden ambient.",
        "rationale": (
            "Japanese-inspired mini-drama from a text brief + traditional Japanese-garden "
            "ambient. StoryAgent drafts the young-woman / dying-grandfather / tea-garden "
            "blueprint. ScreenplayAgent breaks it into Japanese-inspired scenes. KeyFrameAgent "
            "plans keyframes for the tea-garden settings from text alone. VideoAgent assembles "
            "the multi-shot film. AmbienceAgent generates the Japanese-garden room-tone bed. "
            "AudioMixAgent layers it under the dialogue+foley. CompositorAgent muxes the "
            "final mp4. Reject MusicAgent, Transcription/Translation, VideoAnalysis/IntakeVideo/"
            "StyleTransfer/VideoExtend/Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the Japanese-inspired story blueprint — young-woman tending dying-grandfather's tea-garden arc.",
            "Decompose the tea-garden arc into Japanese-inspired scenes with quiet emotional register.",
            "Plan keyframes for the traditional Japanese tea-garden settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving Japanese-inspired visual continuity.",
            "Generate the traditional Japanese-garden ambient bed the user requested, matching the tea-garden environment.",
            "Layer the Japanese-garden ambience bed under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final Japanese-inspired mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a coastal mini-drama about a retired lighthouse keeper sharing his final secret with his granddaughter, with coastal-lighthouse ambient.",
        "rationale": (
            "Coastal mini-drama from a text brief + coastal-lighthouse ambient. StoryAgent "
            "drafts the retired-lighthouse-keeper / granddaughter / final-secret blueprint. "
            "ScreenplayAgent breaks it into coastal-drama scenes. KeyFrameAgent plans keyframes "
            "for the lighthouse settings from text alone. VideoAgent assembles the multi-shot "
            "film. AmbienceAgent generates the coastal-lighthouse room-tone bed. AudioMixAgent "
            "layers it under the dialogue+foley. CompositorAgent muxes the final mp4. Reject "
            "MusicAgent, Transcription/Translation, VideoAnalysis/IntakeVideo/StyleTransfer/"
            "VideoExtend/Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the coastal story blueprint — retired-lighthouse-keeper and granddaughter final-secret arc.",
            "Decompose the secret-sharing arc into coastal-drama scenes.",
            "Plan keyframes for the coastal-lighthouse settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving coastal-drama visual continuity.",
            "Generate the coastal-lighthouse ambient bed the user requested, matching the lighthouse-and-sea environment.",
            "Layer the coastal-lighthouse ambience bed under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final coastal mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a thriller mini-drama about a meteorologist monitoring a once-in-a-century hurricane as it bears down on her coastal town, with hurricane ambient.",
        "rationale": (
            "Thriller mini-drama from a text brief + hurricane ambient. StoryAgent drafts the "
            "meteorologist / once-in-a-century-hurricane / coastal-town blueprint. "
            "ScreenplayAgent breaks it into thriller scenes with rising-storm pacing. "
            "KeyFrameAgent plans keyframes for the meteorology / coastal-town settings from "
            "text alone. VideoAgent assembles the multi-shot film. AmbienceAgent generates "
            "the hurricane room-tone bed. AudioMixAgent layers it under the dialogue+foley. "
            "CompositorAgent muxes the final mp4. Reject MusicAgent, Transcription/Translation, "
            "VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight, "
            "Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the thriller story blueprint — meteorologist monitoring hurricane bearing down on coastal town.",
            "Decompose the hurricane-monitoring arc into thriller scenes with rising-storm tension.",
            "Plan keyframes for the meteorology / coastal-town settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving thriller visual continuity.",
            "Generate the hurricane ambient bed the user requested, matching the once-in-a-century-storm environment.",
            "Layer the hurricane ambience bed under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final thriller mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a period war mini-drama about two WWII nurses in a bombed-out French village, with war-torn-village ambient.",
        "rationale": (
            "Period war mini-drama from a text brief + war-torn-village ambient. StoryAgent "
            "drafts the two-WWII-nurses / bombed-French-village blueprint. ScreenplayAgent "
            "breaks it into period-war scenes. KeyFrameAgent plans keyframes for the WWII "
            "French village settings from text alone. VideoAgent assembles the multi-shot "
            "film. AmbienceAgent generates the war-torn-village room-tone bed. AudioMixAgent "
            "layers it under the dialogue+foley. CompositorAgent muxes the final mp4. Reject "
            "MusicAgent, Transcription/Translation, VideoAnalysis/IntakeVideo/StyleTransfer/"
            "VideoExtend/Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the period-war story blueprint — two WWII nurses in bombed-out French village arc.",
            "Decompose the WWII-village arc into period-war scenes.",
            "Plan keyframes for the bombed-out French village settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving period-war visual continuity.",
            "Generate the war-torn-village ambient bed the user requested, matching the bombed-village environment.",
            "Layer the war-torn-village ambience bed under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final period-war mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a coming-of-age mini-drama about a young fisherman's daughter learning to sail solo in her dead father's skiff, with coastal-sail ambient.",
        "rationale": (
            "Coming-of-age coastal mini-drama from a text brief + coastal-sail ambient. "
            "StoryAgent drafts the fisherman's-daughter / dead-father's-skiff / solo-sail "
            "blueprint. ScreenplayAgent breaks it into coming-of-age coastal scenes. "
            "KeyFrameAgent plans keyframes for the harbor / sail settings from text alone. "
            "VideoAgent assembles the multi-shot film. AmbienceAgent generates the coastal-sail "
            "room-tone bed. AudioMixAgent layers it under the dialogue+foley. CompositorAgent "
            "muxes the final mp4. Reject MusicAgent, Transcription/Translation, VideoAnalysis/"
            "IntakeVideo/StyleTransfer/VideoExtend/Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the coming-of-age coastal story blueprint — fisherman's-daughter solo-sailing dead-father's-skiff arc.",
            "Decompose the solo-sail arc into coming-of-age coastal scenes.",
            "Plan keyframes for the harbor / open-water sail settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving coming-of-age coastal visual continuity.",
            "Generate the coastal-sail ambient bed the user requested, matching the open-water sailing environment.",
            "Layer the coastal-sail ambience bed under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final coming-of-age coastal mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a desert-drama mini-drama about a nomad guide leading a lost traveler across the Sahara, with desert-wind ambient.",
        "rationale": (
            "Desert-drama mini-drama from a text brief + desert-wind ambient. StoryAgent "
            "drafts the nomad-guide / lost-traveler / Sahara-crossing blueprint. ScreenplayAgent "
            "breaks it into desert-drama scenes. KeyFrameAgent plans keyframes for the Sahara "
            "settings from text alone. VideoAgent assembles the multi-shot film. AmbienceAgent "
            "generates the desert-wind room-tone bed. AudioMixAgent layers it under the "
            "dialogue+foley. CompositorAgent muxes the final mp4. Reject MusicAgent, "
            "Transcription/Translation, VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/"
            "Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the desert-drama story blueprint — nomad-guide leading lost-traveler across the Sahara arc.",
            "Decompose the crossing arc into desert-drama scenes.",
            "Plan keyframes for the Sahara settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving desert-drama visual continuity.",
            "Generate the desert-wind ambient bed the user requested, matching the Sahara-wind environment.",
            "Layer the desert-wind ambience bed under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final desert-drama mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a period mini-drama about a Regency-era lady's maid uncovering a plot against her mistress at a grand ball, with Regency-ball ambient.",
        "rationale": (
            "Regency-era period mini-drama from a text brief + Regency-ball ambient. "
            "StoryAgent drafts the lady's-maid / plot-against-mistress / grand-ball blueprint. "
            "ScreenplayAgent breaks it into Regency-period scenes. KeyFrameAgent plans "
            "keyframes for the Regency ballroom settings from text alone. VideoAgent assembles "
            "the multi-shot film. AmbienceAgent generates the Regency-ball room-tone bed. "
            "AudioMixAgent layers it under the dialogue+foley. CompositorAgent muxes the "
            "final mp4. Reject MusicAgent, Transcription/Translation, VideoAnalysis/IntakeVideo/"
            "StyleTransfer/VideoExtend/Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the Regency-period story blueprint — lady's-maid uncovering plot at grand ball arc.",
            "Decompose the plot-uncovering arc into Regency-period scenes.",
            "Plan keyframes for the Regency-ball settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving Regency-period visual continuity.",
            "Generate the Regency-ball ambient bed the user requested, matching the grand-ball environment.",
            "Layer the Regency-ball ambience bed under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final Regency-period mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a mini-drama about a young monk in a misty mountain temple struggling with his first visions, with mountain-temple ambient.",
        "rationale": (
            "Mini-drama from a text brief + mountain-temple ambient. StoryAgent drafts the "
            "young-monk / misty-mountain-temple / first-visions blueprint. ScreenplayAgent "
            "breaks it into mountain-temple scenes. KeyFrameAgent plans keyframes for the "
            "misty-mountain-temple settings from text alone. VideoAgent assembles the "
            "multi-shot film. AmbienceAgent generates the mountain-temple room-tone bed. "
            "AudioMixAgent layers it under the dialogue+foley. CompositorAgent muxes the "
            "final mp4. Reject MusicAgent, Transcription/Translation, VideoAnalysis/"
            "IntakeVideo/StyleTransfer/VideoExtend/Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the mountain-temple story blueprint — young-monk first-visions in misty mountain-temple arc.",
            "Decompose the first-visions arc into mountain-temple scenes.",
            "Plan keyframes for the misty mountain-temple settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving mountain-temple visual continuity.",
            "Generate the mountain-temple ambient bed the user requested, matching the misty-mountain-temple environment.",
            "Layer the mountain-temple ambience bed under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final mountain-temple mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a conspiracy thriller mini-drama about a journalist receiving an anonymous thumb drive in a hotel elevator, with corporate-hotel ambient.",
        "rationale": (
            "Conspiracy thriller mini-drama from a text brief + corporate-hotel ambient. "
            "StoryAgent drafts the journalist / anonymous-thumb-drive / hotel-elevator "
            "blueprint. ScreenplayAgent breaks it into conspiracy-thriller scenes. "
            "KeyFrameAgent plans keyframes for the corporate-hotel settings from text alone. "
            "VideoAgent assembles the multi-shot film. AmbienceAgent generates the "
            "corporate-hotel room-tone bed. AudioMixAgent layers it under the dialogue+foley. "
            "CompositorAgent muxes the final mp4. Reject MusicAgent, Transcription/Translation, "
            "VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight, "
            "Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the conspiracy-thriller story blueprint — journalist anonymous-thumb-drive hotel-elevator arc.",
            "Decompose the conspiracy arc into thriller scenes.",
            "Plan keyframes for the corporate-hotel settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving conspiracy-thriller visual continuity.",
            "Generate the corporate-hotel ambient bed the user requested, matching the corporate-hotel environment.",
            "Layer the corporate-hotel ambience bed under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final conspiracy-thriller mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a mini-drama about an elderly widow caring for her dying husband's prized garden through one last season, with garden-seasonal ambient.",
        "rationale": (
            "Mini-drama from a text brief + garden-seasonal ambient. StoryAgent drafts the "
            "elderly-widow / dying-husband's-prized-garden / one-last-season blueprint. "
            "ScreenplayAgent breaks it into garden-care scenes. KeyFrameAgent plans keyframes "
            "for the garden-seasonal settings from text alone. VideoAgent assembles the "
            "multi-shot film. AmbienceAgent generates the garden-seasonal room-tone bed. "
            "AudioMixAgent layers it under the dialogue+foley. CompositorAgent muxes the "
            "final mp4. Reject MusicAgent, Transcription/Translation, VideoAnalysis/"
            "IntakeVideo/StyleTransfer/VideoExtend/Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the elderly-widow story blueprint — caring for dying-husband's prized garden one last season arc.",
            "Decompose the garden-care arc into seasonal scenes with quiet emotional register.",
            "Plan keyframes for the prized-garden settings across seasons; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving garden-care visual continuity.",
            "Generate the garden-seasonal ambient bed the user requested, matching the garden-through-seasons environment.",
            "Layer the garden-seasonal ambience bed under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final elderly-widow mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a mini-drama about two Coast-Guard rescue swimmers responding to a capsized fishing trawler in a storm, with open-ocean-storm ambient.",
        "rationale": (
            "Coast-Guard rescue mini-drama from a text brief + open-ocean-storm ambient. "
            "StoryAgent drafts the two-rescue-swimmers / capsized-trawler / storm-rescue "
            "blueprint. ScreenplayAgent breaks it into rescue-drama scenes. KeyFrameAgent "
            "plans keyframes for the open-ocean-storm settings from text alone. VideoAgent "
            "assembles the multi-shot film. AmbienceAgent generates the open-ocean-storm "
            "room-tone bed. AudioMixAgent layers it under the dialogue+foley. CompositorAgent "
            "muxes the final mp4. Reject MusicAgent, Transcription/Translation, VideoAnalysis/"
            "IntakeVideo/StyleTransfer/VideoExtend/Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the Coast-Guard rescue story blueprint — two rescue swimmers and capsized fishing-trawler in storm arc.",
            "Decompose the rescue arc into Coast-Guard scenes with high-tension pacing.",
            "Plan keyframes for the open-ocean-storm settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving rescue-drama visual continuity.",
            "Generate the open-ocean-storm ambient bed the user requested, matching the violent-storm-at-sea environment.",
            "Layer the open-ocean-storm ambience bed under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final Coast-Guard rescue mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a mini-drama about a forensic scientist re-examining a 30-year-old cold case from her small lab, with forensic-lab ambient.",
        "rationale": (
            "Forensic mini-drama from a text brief + forensic-lab ambient. StoryAgent drafts "
            "the forensic-scientist / 30-year-cold-case blueprint. ScreenplayAgent breaks it "
            "into forensic-investigation scenes. KeyFrameAgent plans keyframes for the small "
            "forensic-lab settings from text alone. VideoAgent assembles the multi-shot film. "
            "AmbienceAgent generates the forensic-lab room-tone bed. AudioMixAgent layers it "
            "under the dialogue+foley. CompositorAgent muxes the final mp4. Reject MusicAgent, "
            "Transcription/Translation, VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/"
            "Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the forensic story blueprint — forensic-scientist re-examining 30-year-old cold case arc.",
            "Decompose the cold-case arc into forensic-investigation scenes.",
            "Plan keyframes for the small forensic-lab settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving forensic-investigation visual continuity.",
            "Generate the forensic-lab ambient bed the user requested, matching the small-lab environment.",
            "Layer the forensic-lab ambience bed under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final forensic mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a mini-drama about a prisoner-rehabilitation group meeting in an empty chapel once a week, with empty-chapel ambient.",
        "rationale": (
            "Mini-drama from a text brief + empty-chapel ambient. StoryAgent drafts the "
            "prisoner-rehabilitation-group / empty-chapel / weekly-meeting blueprint. "
            "ScreenplayAgent breaks it into rehabilitation-drama scenes. KeyFrameAgent plans "
            "keyframes for the empty-chapel settings from text alone. VideoAgent assembles "
            "the multi-shot film. AmbienceAgent generates the empty-chapel room-tone bed. "
            "AudioMixAgent layers it under the dialogue+foley. CompositorAgent muxes the "
            "final mp4. Reject MusicAgent, Transcription/Translation, VideoAnalysis/"
            "IntakeVideo/StyleTransfer/VideoExtend/Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the prisoner-rehabilitation story blueprint — group meeting weekly in empty chapel arc.",
            "Decompose the meeting arc into rehabilitation-drama scenes.",
            "Plan keyframes for the empty-chapel settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving rehabilitation-drama visual continuity.",
            "Generate the empty-chapel ambient bed the user requested, matching the empty-chapel environment.",
            "Layer the empty-chapel ambience bed under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final rehabilitation mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a mini-drama about an ornithologist tracking the last known wild whooping crane through a misty wetland, with wetland ambient.",
        "rationale": (
            "Mini-drama from a text brief + wetland ambient. StoryAgent drafts the "
            "ornithologist / last-wild-whooping-crane / misty-wetland blueprint. "
            "ScreenplayAgent breaks it into nature-tracking scenes. KeyFrameAgent plans "
            "keyframes for the misty-wetland settings from text alone. VideoAgent assembles "
            "the multi-shot film. AmbienceAgent generates the wetland room-tone bed. "
            "AudioMixAgent layers it under the dialogue+foley. CompositorAgent muxes the "
            "final mp4. Reject MusicAgent, Transcription/Translation, VideoAnalysis/"
            "IntakeVideo/StyleTransfer/VideoExtend/Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the ornithologist story blueprint — tracking last wild whooping-crane through misty wetland arc.",
            "Decompose the tracking arc into nature-drama scenes.",
            "Plan keyframes for the misty-wetland settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving nature-drama visual continuity.",
            "Generate the wetland ambient bed the user requested, matching the misty-wetland environment.",
            "Layer the wetland ambience bed under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final ornithologist mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a horror mini-drama about a lone night-shift security guard at a strange new museum that keeps changing its exhibits, with empty-museum ambient.",
        "rationale": (
            "Horror mini-drama from a text brief + empty-museum ambient. StoryAgent drafts "
            "the night-shift-security-guard / shifting-exhibits museum blueprint. "
            "ScreenplayAgent breaks it into horror scenes. KeyFrameAgent plans keyframes for "
            "the strange-museum settings from text alone. VideoAgent assembles the multi-shot "
            "film. AmbienceAgent generates the empty-museum room-tone bed. AudioMixAgent "
            "layers it under the dialogue+foley. CompositorAgent muxes the final mp4. Reject "
            "MusicAgent, Transcription/Translation, VideoAnalysis/IntakeVideo/StyleTransfer/"
            "VideoExtend/Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the horror story blueprint — night-shift security-guard and shifting-exhibits museum arc.",
            "Decompose the shifting-exhibits arc into horror scenes with mounting unease.",
            "Plan keyframes for the strange-museum settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving horror visual continuity.",
            "Generate the empty-museum ambient bed the user requested, matching the after-hours museum environment.",
            "Layer the empty-museum ambience bed under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final horror mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a mini-drama about a female park ranger investigating strange lights in the redwoods, with redwood-forest ambient.",
        "rationale": (
            "Mini-drama from a text brief + redwood-forest ambient. StoryAgent drafts the "
            "park-ranger / strange-lights / redwoods blueprint. ScreenplayAgent breaks it "
            "into investigation scenes. KeyFrameAgent plans keyframes for the redwood-forest "
            "settings from text alone. VideoAgent assembles the multi-shot film. AmbienceAgent "
            "generates the redwood-forest room-tone bed. AudioMixAgent layers it under the "
            "dialogue+foley. CompositorAgent muxes the final mp4. Reject MusicAgent, "
            "Transcription/Translation, VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/"
            "Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the park-ranger story blueprint — investigating strange lights in the redwoods arc.",
            "Decompose the investigation arc into mystery-drama scenes.",
            "Plan keyframes for the redwood-forest settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving mystery-drama visual continuity.",
            "Generate the redwood-forest ambient bed the user requested, matching the redwood-grove environment.",
            "Layer the redwood-forest ambience bed under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final park-ranger mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a mini-drama about a young woman starting her first shift at a 24-hour diner in a deserted highway rest stop, with deserted-diner ambient.",
        "rationale": (
            "Mini-drama from a text brief + deserted-diner ambient. StoryAgent drafts the "
            "young-woman / first-shift / 24-hour-diner / deserted-rest-stop blueprint. "
            "ScreenplayAgent breaks it into diner-drama scenes. KeyFrameAgent plans keyframes "
            "for the 24-hour-diner settings from text alone. VideoAgent assembles the "
            "multi-shot film. AmbienceAgent generates the deserted-diner room-tone bed. "
            "AudioMixAgent layers it under the dialogue+foley. CompositorAgent muxes the "
            "final mp4. Reject MusicAgent, Transcription/Translation, VideoAnalysis/"
            "IntakeVideo/StyleTransfer/VideoExtend/Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the young-woman story blueprint — first shift at 24-hour diner in deserted rest-stop arc.",
            "Decompose the first-shift arc into diner-drama scenes.",
            "Plan keyframes for the 24-hour-diner / highway-rest-stop settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving diner-drama visual continuity.",
            "Generate the deserted-diner ambient bed the user requested, matching the late-night-diner environment.",
            "Layer the deserted-diner ambience bed under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final young-woman mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a mini-drama about a librarian closing up her small-town library on a stormy evening when a stranger walks in, with stormy-library ambient.",
        "rationale": (
            "Mini-drama from a text brief + stormy-library ambient. StoryAgent drafts the "
            "librarian / closing-night / stranger blueprint. ScreenplayAgent breaks it into "
            "library-drama scenes. KeyFrameAgent plans keyframes for the small-town-library "
            "settings from text alone. VideoAgent assembles the multi-shot film. AmbienceAgent "
            "generates the stormy-library room-tone bed. AudioMixAgent layers it under the "
            "dialogue+foley. CompositorAgent muxes the final mp4. Reject MusicAgent, "
            "Transcription/Translation, VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/"
            "Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the librarian story blueprint — closing-night small-town library and stranger arc.",
            "Decompose the closing-night arc into library-drama scenes.",
            "Plan keyframes for the small-town-library settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving library-drama visual continuity.",
            "Generate the stormy-library ambient bed the user requested, matching the stormy-library environment.",
            "Layer the stormy-library ambience bed under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final librarian mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a mini-drama about a young zoologist spending a month alone in an African grassland research post, with African-grassland ambient.",
        "rationale": (
            "Mini-drama from a text brief + African-grassland ambient. StoryAgent drafts the "
            "young-zoologist / month-alone / African-grassland-research-post blueprint. "
            "ScreenplayAgent breaks it into solitary-research scenes. KeyFrameAgent plans "
            "keyframes for the African-grassland-research-post settings from text alone. "
            "VideoAgent assembles the multi-shot film. AmbienceAgent generates the African-"
            "grassland room-tone bed. AudioMixAgent layers it under the dialogue+foley. "
            "CompositorAgent muxes the final mp4. Reject MusicAgent, Transcription/"
            "Translation, VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight, "
            "Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the young-zoologist story blueprint — month alone at African-grassland research post arc.",
            "Decompose the solitary-research arc into nature-drama scenes.",
            "Plan keyframes for the African-grassland-research-post settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving nature-drama visual continuity.",
            "Generate the African-grassland ambient bed the user requested, matching the savanna environment.",
            "Layer the African-grassland ambience bed under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final young-zoologist mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a mini-drama about a young woman returning alone to her childhood farmhouse after her parents' death to sort through their belongings, with quiet-farmhouse ambient.",
        "rationale": (
            "Mini-drama from a text brief + quiet-farmhouse ambient. StoryAgent drafts the "
            "young-woman / childhood-farmhouse / parents'-death / sort-belongings blueprint. "
            "ScreenplayAgent breaks it into grief-drama scenes. KeyFrameAgent plans keyframes "
            "for the childhood-farmhouse settings from text alone. VideoAgent assembles the "
            "multi-shot film. AmbienceAgent generates the quiet-farmhouse room-tone bed. "
            "AudioMixAgent layers it under the dialogue+foley. CompositorAgent muxes the "
            "final mp4. Reject MusicAgent, Transcription/Translation, VideoAnalysis/"
            "IntakeVideo/StyleTransfer/VideoExtend/Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the grief-drama story blueprint — young-woman returning to childhood farmhouse to sort parents' belongings arc.",
            "Decompose the sorting arc into grief-drama scenes with quiet emotional register.",
            "Plan keyframes for the childhood-farmhouse settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving grief-drama visual continuity.",
            "Generate the quiet-farmhouse ambient bed the user requested, matching the empty-farmhouse environment.",
            "Layer the quiet-farmhouse ambience bed under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final grief-drama mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a mini-drama about a young monk spending her first winter alone in a remote mountain cave meditating, with ice-cave ambient.",
        "rationale": (
            "Mini-drama from a text brief + ice-cave ambient. StoryAgent drafts the young-"
            "monk / first-winter-alone / remote-mountain-cave-meditation blueprint. "
            "ScreenplayAgent breaks it into solitary-meditation scenes. KeyFrameAgent plans "
            "keyframes for the ice-cave settings from text alone. VideoAgent assembles the "
            "multi-shot film. AmbienceAgent generates the ice-cave room-tone bed. AudioMixAgent "
            "layers it under the dialogue+foley. CompositorAgent muxes the final mp4. Reject "
            "MusicAgent, Transcription/Translation, VideoAnalysis/IntakeVideo/StyleTransfer/"
            "VideoExtend/Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the young-monk story blueprint — first winter alone in remote mountain ice-cave meditation arc.",
            "Decompose the meditation arc into solitary-meditation scenes.",
            "Plan keyframes for the ice-cave settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving solitary-meditation visual continuity.",
            "Generate the ice-cave ambient bed the user requested, matching the icy-cave environment.",
            "Layer the ice-cave ambience bed under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final young-monk mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a mini-drama about a reluctant funeral director preparing for a small-town's most difficult burial, with funeral-home ambient.",
        "rationale": (
            "Mini-drama from a text brief + funeral-home ambient. StoryAgent drafts the "
            "reluctant-funeral-director / small-town / most-difficult-burial blueprint. "
            "ScreenplayAgent breaks it into funeral-drama scenes. KeyFrameAgent plans keyframes "
            "for the funeral-home settings from text alone. VideoAgent assembles the multi-shot "
            "film. AmbienceAgent generates the funeral-home room-tone bed. AudioMixAgent layers "
            "it under the dialogue+foley. CompositorAgent muxes the final mp4. Reject "
            "MusicAgent, Transcription/Translation, VideoAnalysis/IntakeVideo/StyleTransfer/"
            "VideoExtend/Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the funeral-drama story blueprint — reluctant funeral-director preparing small-town's most difficult burial arc.",
            "Decompose the funeral-prep arc into funeral-drama scenes with somber register.",
            "Plan keyframes for the funeral-home settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving funeral-drama visual continuity.",
            "Generate the funeral-home ambient bed the user requested, matching the funeral-home environment.",
            "Layer the funeral-home ambience bed under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final funeral-drama mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a mini-drama about a mountaineer trapped in an avalanche-survivor snow cave waiting for rescue, with snow-cave ambient.",
        "rationale": (
            "Survival mini-drama from a text brief + snow-cave ambient. StoryAgent drafts the "
            "mountaineer / avalanche-survivor / snow-cave / waiting-rescue blueprint. "
            "ScreenplayAgent breaks it into survival-drama scenes. KeyFrameAgent plans "
            "keyframes for the snow-cave settings from text alone. VideoAgent assembles the "
            "multi-shot film. AmbienceAgent generates the snow-cave room-tone bed. "
            "AudioMixAgent layers it under the dialogue+foley. CompositorAgent muxes the "
            "final mp4. Reject MusicAgent, Transcription/Translation, VideoAnalysis/"
            "IntakeVideo/StyleTransfer/VideoExtend/Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the survival story blueprint — mountaineer avalanche-survivor in snow-cave waiting-rescue arc.",
            "Decompose the survival arc into snow-cave drama scenes.",
            "Plan keyframes for the snow-cave settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving survival-drama visual continuity.",
            "Generate the snow-cave ambient bed the user requested, matching the snow-cave environment.",
            "Layer the snow-cave ambience bed under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final survival mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a mini-drama about a 1970s radio DJ on his last overnight shift at a local station, with radio-studio ambient.",
        "rationale": (
            "1970s mini-drama from a text brief + radio-studio ambient. StoryAgent drafts the "
            "1970s-radio-DJ / last-overnight-shift / local-station blueprint. ScreenplayAgent "
            "breaks it into 1970s-period scenes. KeyFrameAgent plans keyframes for the "
            "1970s-radio-studio settings from text alone. VideoAgent assembles the multi-shot "
            "film. AmbienceAgent generates the radio-studio room-tone bed. AudioMixAgent "
            "layers it under the dialogue+foley. CompositorAgent muxes the final mp4. Reject "
            "MusicAgent, Transcription/Translation, VideoAnalysis/IntakeVideo/StyleTransfer/"
            "VideoExtend/Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the 1970s story blueprint — radio DJ last overnight shift at local station arc.",
            "Decompose the last-shift arc into 1970s-period scenes.",
            "Plan keyframes for the 1970s-radio-studio settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving 1970s-period visual continuity.",
            "Generate the radio-studio ambient bed the user requested, matching the 1970s-radio-studio environment.",
            "Layer the radio-studio ambience bed under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final 1970s mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a mini-drama about a freediver exploring an underwater cave system to find her missing brother's last dive location, with underwater-cave ambient.",
        "rationale": (
            "Underwater mini-drama from a text brief + underwater-cave ambient. StoryAgent "
            "drafts the freediver / underwater-cave-system / missing-brother's-last-dive "
            "blueprint. ScreenplayAgent breaks it into underwater-drama scenes. KeyFrameAgent "
            "plans keyframes for the underwater-cave-system settings from text alone. "
            "VideoAgent assembles the multi-shot film. AmbienceAgent generates the underwater-"
            "cave room-tone bed. AudioMixAgent layers it under the dialogue+foley. "
            "CompositorAgent muxes the final mp4. Reject MusicAgent, Transcription/Translation, "
            "VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight, "
            "Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the underwater story blueprint — freediver exploring cave system for missing brother's last dive location arc.",
            "Decompose the cave-exploration arc into underwater-drama scenes.",
            "Plan keyframes for the underwater-cave-system settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving underwater-drama visual continuity.",
            "Generate the underwater-cave ambient bed the user requested, matching the submerged-cave environment.",
            "Layer the underwater-cave ambience bed under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final underwater mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a mini-drama about a Tibetan yak-herder family navigating their first winter after the matriarch's death, with Tibetan-winter ambient.",
        "rationale": (
            "Tibetan-family mini-drama from a text brief + Tibetan-winter ambient. StoryAgent "
            "drafts the yak-herder-family / first-winter / matriarch's-death blueprint. "
            "ScreenplayAgent breaks it into family-drama scenes. KeyFrameAgent plans keyframes "
            "for the Tibetan-winter settings from text alone. VideoAgent assembles the "
            "multi-shot film. AmbienceAgent generates the Tibetan-winter room-tone bed. "
            "AudioMixAgent layers it under the dialogue+foley. CompositorAgent muxes the "
            "final mp4. Reject MusicAgent, Transcription/Translation, VideoAnalysis/"
            "IntakeVideo/StyleTransfer/VideoExtend/Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the Tibetan-family story blueprint — yak-herder family first winter after matriarch's death arc.",
            "Decompose the first-winter arc into family-drama scenes.",
            "Plan keyframes for the Tibetan-winter herder settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving Tibetan-family visual continuity.",
            "Generate the Tibetan-winter ambient bed the user requested, matching the high-altitude winter environment.",
            "Layer the Tibetan-winter ambience bed under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final Tibetan-family mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a mini-drama about a young composer walking through empty concert halls at night to hear her own inner melodies, with empty-concert-hall ambient.",
        "rationale": (
            "Mini-drama from a text brief + empty-concert-hall ambient. StoryAgent drafts the "
            "young-composer / empty-concert-halls / inner-melodies blueprint. ScreenplayAgent "
            "breaks it into composer-drama scenes. KeyFrameAgent plans keyframes for the "
            "empty-concert-hall settings from text alone. VideoAgent assembles the multi-shot "
            "film. AmbienceAgent generates the empty-concert-hall room-tone bed. AudioMixAgent "
            "layers it under the dialogue+foley. CompositorAgent muxes the final mp4. Reject "
            "MusicAgent (user asked environmental ambient — the silent concert-hall room-tone "
            "— not a melodic score), Transcription/Translation, VideoAnalysis/IntakeVideo/"
            "StyleTransfer/VideoExtend/Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the young-composer story blueprint — walking through empty concert halls hearing inner melodies arc.",
            "Decompose the inner-melody arc into composer-drama scenes.",
            "Plan keyframes for the empty-concert-hall settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving composer-drama visual continuity.",
            "Generate the empty-concert-hall ambient bed the user requested, matching the after-hours concert-hall environment.",
            "Layer the empty-concert-hall ambience bed under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final young-composer mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a mini-drama about a cold-war spy in a snowbound dacha receiving an impossible order, with snowbound-dacha ambient.",
        "rationale": (
            "Cold-war spy mini-drama from a text brief + snowbound-dacha ambient. StoryAgent "
            "drafts the cold-war-spy / snowbound-dacha / impossible-order blueprint. "
            "ScreenplayAgent breaks it into cold-war-spy scenes. KeyFrameAgent plans keyframes "
            "for the snowbound-dacha settings from text alone. VideoAgent assembles the "
            "multi-shot film. AmbienceAgent generates the snowbound-dacha room-tone bed. "
            "AudioMixAgent layers it under the dialogue+foley. CompositorAgent muxes the "
            "final mp4. Reject MusicAgent, Transcription/Translation, VideoAnalysis/"
            "IntakeVideo/StyleTransfer/VideoExtend/Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the cold-war-spy story blueprint — spy in snowbound dacha receiving impossible order arc.",
            "Decompose the impossible-order arc into cold-war-spy scenes.",
            "Plan keyframes for the snowbound-dacha settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving cold-war-spy visual continuity.",
            "Generate the snowbound-dacha ambient bed the user requested, matching the isolated-snowy-dacha environment.",
            "Layer the snowbound-dacha ambience bed under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final cold-war-spy mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a mini-drama about a young cartographer charting a route through an uncharted jungle, with deep-jungle ambient.",
        "rationale": (
            "Mini-drama from a text brief + deep-jungle ambient. StoryAgent drafts the "
            "young-cartographer / uncharted-jungle / route-charting blueprint. ScreenplayAgent "
            "breaks it into adventure-drama scenes. KeyFrameAgent plans keyframes for the "
            "deep-jungle settings from text alone. VideoAgent assembles the multi-shot film. "
            "AmbienceAgent generates the deep-jungle room-tone bed. AudioMixAgent layers it "
            "under the dialogue+foley. CompositorAgent muxes the final mp4. Reject MusicAgent, "
            "Transcription/Translation, VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/"
            "Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the cartographer story blueprint — charting route through uncharted jungle arc.",
            "Decompose the route-charting arc into adventure-drama scenes.",
            "Plan keyframes for the deep-jungle settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving adventure-drama visual continuity.",
            "Generate the deep-jungle ambient bed the user requested, matching the deep-jungle environment.",
            "Layer the deep-jungle ambience bed under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final cartographer mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a mini-drama about a Coast-Watcher station volunteer spending a stormy night alone tracking a missing vessel, with stormy-coast-station ambient.",
        "rationale": (
            "Mini-drama from a text brief + stormy-coast-station ambient. StoryAgent drafts "
            "the Coast-Watcher-volunteer / stormy-night / missing-vessel blueprint. "
            "ScreenplayAgent breaks it into Coast-Watcher scenes. KeyFrameAgent plans keyframes "
            "for the stormy-coast-station settings from text alone. VideoAgent assembles the "
            "multi-shot film. AmbienceAgent generates the stormy-coast-station room-tone bed. "
            "AudioMixAgent layers it under the dialogue+foley. CompositorAgent muxes the "
            "final mp4. Reject MusicAgent, Transcription/Translation, VideoAnalysis/"
            "IntakeVideo/StyleTransfer/VideoExtend/Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the Coast-Watcher story blueprint — volunteer stormy-night tracking missing vessel arc.",
            "Decompose the tracking arc into Coast-Watcher scenes.",
            "Plan keyframes for the stormy-coast-station settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving Coast-Watcher visual continuity.",
            "Generate the stormy-coast-station ambient bed the user requested, matching the storm-night-station environment.",
            "Layer the stormy-coast-station ambience bed under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final Coast-Watcher mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a mini-drama about a young widow spending her first winter alone in her grandmother's Catskills cabin, with winter-cabin ambient.",
        "rationale": (
            "Mini-drama from a text brief + winter-cabin ambient. StoryAgent drafts the "
            "young-widow / first-winter-alone / grandmother's-Catskills-cabin blueprint. "
            "ScreenplayAgent breaks it into grief-drama scenes. KeyFrameAgent plans keyframes "
            "for the Catskills-winter-cabin settings from text alone. VideoAgent assembles "
            "the multi-shot film. AmbienceAgent generates the winter-cabin room-tone bed. "
            "AudioMixAgent layers it under the dialogue+foley. CompositorAgent muxes the "
            "final mp4. Reject MusicAgent, Transcription/Translation, VideoAnalysis/"
            "IntakeVideo/StyleTransfer/VideoExtend/Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the young-widow story blueprint — first winter alone in grandmother's Catskills cabin arc.",
            "Decompose the winter-alone arc into grief-drama scenes with quiet register.",
            "Plan keyframes for the Catskills-winter-cabin settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving grief-drama visual continuity.",
            "Generate the winter-cabin ambient bed the user requested, matching the snowed-in cabin environment.",
            "Layer the winter-cabin ambience bed under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final young-widow mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a mini-drama about a young archivist inspecting a collapsing castle archive before a storm, with crumbling-archive ambient.",
        "rationale": (
            "Mini-drama from a text brief + crumbling-archive ambient. StoryAgent drafts the "
            "young-archivist / collapsing-castle-archive / pre-storm-inspection blueprint. "
            "ScreenplayAgent breaks it into archive-drama scenes. KeyFrameAgent plans keyframes "
            "for the collapsing-castle-archive settings from text alone. VideoAgent assembles "
            "the multi-shot film. AmbienceAgent generates the crumbling-archive room-tone bed. "
            "AudioMixAgent layers it under the dialogue+foley. CompositorAgent muxes the "
            "final mp4. Reject MusicAgent, Transcription/Translation, VideoAnalysis/"
            "IntakeVideo/StyleTransfer/VideoExtend/Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the archivist story blueprint — inspecting collapsing castle archive before storm arc.",
            "Decompose the archive-inspection arc into archive-drama scenes.",
            "Plan keyframes for the collapsing-castle-archive settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving archive-drama visual continuity.",
            "Generate the crumbling-archive ambient bed the user requested, matching the decaying-castle-archive environment.",
            "Layer the crumbling-archive ambience bed under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final archivist mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a mini-drama about an aging astronomer pursuing an anomalous radio signal from her small-hill observatory, with hill-observatory ambient.",
        "rationale": (
            "Mini-drama from a text brief + hill-observatory ambient. StoryAgent drafts the "
            "aging-astronomer / anomalous-radio-signal / hill-observatory blueprint. "
            "ScreenplayAgent breaks it into astronomy-drama scenes. KeyFrameAgent plans "
            "keyframes for the hill-observatory settings from text alone. VideoAgent assembles "
            "the multi-shot film. AmbienceAgent generates the hill-observatory room-tone bed. "
            "AudioMixAgent layers it under the dialogue+foley. CompositorAgent muxes the "
            "final mp4. Reject MusicAgent, Transcription/Translation, VideoAnalysis/"
            "IntakeVideo/StyleTransfer/VideoExtend/Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the astronomer story blueprint — aging-astronomer pursuing anomalous radio signal from hill observatory arc.",
            "Decompose the signal-pursuit arc into astronomy-drama scenes.",
            "Plan keyframes for the small-hill observatory settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving astronomy-drama visual continuity.",
            "Generate the hill-observatory ambient bed the user requested, matching the hill-observatory environment.",
            "Layer the hill-observatory ambience bed under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final astronomer mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a mini-drama about a lighthouse-keeper's apprentice starting her first winter shift alone on an island, with island-winter ambient.",
        "rationale": (
            "Mini-drama from a text brief + island-winter ambient. StoryAgent drafts the "
            "lighthouse-keeper's-apprentice / first-winter-shift-alone / island blueprint. "
            "ScreenplayAgent breaks it into solitary-watch scenes. KeyFrameAgent plans "
            "keyframes for the island-winter-lighthouse settings from text alone. VideoAgent "
            "assembles the multi-shot film. AmbienceAgent generates the island-winter "
            "room-tone bed. AudioMixAgent layers it under the dialogue+foley. CompositorAgent "
            "muxes the final mp4. Reject MusicAgent, Transcription/Translation, VideoAnalysis/"
            "IntakeVideo/StyleTransfer/VideoExtend/Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the lighthouse-apprentice story blueprint — first winter shift alone on island arc.",
            "Decompose the first-shift arc into solitary-watch scenes.",
            "Plan keyframes for the island-winter-lighthouse settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving solitary-watch visual continuity.",
            "Generate the island-winter ambient bed the user requested, matching the winter-island-lighthouse environment.",
            "Layer the island-winter ambience bed under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final lighthouse-apprentice mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a mini-drama about a young seismologist monitoring a suddenly active volcano on a remote island, with active-volcano ambient.",
        "rationale": (
            "Mini-drama from a text brief + active-volcano ambient. StoryAgent drafts the "
            "young-seismologist / active-volcano / remote-island blueprint. ScreenplayAgent "
            "breaks it into seismology-drama scenes. KeyFrameAgent plans keyframes for the "
            "active-volcano remote-island settings from text alone. VideoAgent assembles the "
            "multi-shot film. AmbienceAgent generates the active-volcano room-tone bed. "
            "AudioMixAgent layers it under the dialogue+foley. CompositorAgent muxes the "
            "final mp4. Reject MusicAgent, Transcription/Translation, VideoAnalysis/"
            "IntakeVideo/StyleTransfer/VideoExtend/Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the seismologist story blueprint — young-seismologist monitoring active volcano on remote island arc.",
            "Decompose the volcano-monitoring arc into seismology-drama scenes with rising tension.",
            "Plan keyframes for the active-volcano remote-island settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving seismology-drama visual continuity.",
            "Generate the active-volcano ambient bed the user requested, matching the volcanic-island environment.",
            "Layer the active-volcano ambience bed under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final seismologist mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a mini-drama about a woman walking the old Camino pilgrimage alone after her mother's death, with Camino-trail ambient.",
        "rationale": (
            "Mini-drama from a text brief + Camino-trail ambient. StoryAgent drafts the "
            "woman / Camino-pilgrimage-alone / mother's-death blueprint. ScreenplayAgent "
            "breaks it into pilgrimage-drama scenes. KeyFrameAgent plans keyframes for the "
            "Camino-trail settings from text alone. VideoAgent assembles the multi-shot film. "
            "AmbienceAgent generates the Camino-trail room-tone bed. AudioMixAgent layers it "
            "under the dialogue+foley. CompositorAgent muxes the final mp4. Reject MusicAgent, "
            "Transcription/Translation, VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/"
            "Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the pilgrimage-drama story blueprint — woman walking old Camino alone after mother's death arc.",
            "Decompose the pilgrimage arc into trail-drama scenes with quiet emotional register.",
            "Plan keyframes for the Camino-trail settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving pilgrimage-drama visual continuity.",
            "Generate the Camino-trail ambient bed the user requested, matching the pilgrimage-trail environment.",
            "Layer the Camino-trail ambience bed under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final pilgrimage mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a mini-drama about a mother pacing an empty airport terminal waiting for her overseas son to arrive, with empty-airport ambient.",
        "rationale": (
            "Mini-drama from a text brief + empty-airport ambient. StoryAgent drafts the "
            "mother / empty-airport-terminal / overseas-son-arrival blueprint. ScreenplayAgent "
            "breaks it into family-drama scenes. KeyFrameAgent plans keyframes for the "
            "empty-airport-terminal settings from text alone. VideoAgent assembles the "
            "multi-shot film. AmbienceAgent generates the empty-airport room-tone bed. "
            "AudioMixAgent layers it under the dialogue+foley. CompositorAgent muxes the "
            "final mp4. Reject MusicAgent, Transcription/Translation, VideoAnalysis/"
            "IntakeVideo/StyleTransfer/VideoExtend/Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the family-drama story blueprint — mother pacing empty airport terminal waiting for overseas son arc.",
            "Decompose the waiting arc into family-drama scenes with quiet anticipation register.",
            "Plan keyframes for the empty-airport-terminal settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving family-drama visual continuity.",
            "Generate the empty-airport ambient bed the user requested, matching the late-night-airport-terminal environment.",
            "Layer the empty-airport ambience bed under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final family-drama mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a mini-drama about a solo astronaut orbiting Earth on her last mission before retirement, with spacecraft-cabin ambient.",
        "rationale": (
            "Mini-drama from a text brief + spacecraft-cabin ambient. StoryAgent drafts the "
            "solo-astronaut / orbiting-Earth / last-mission blueprint. ScreenplayAgent breaks "
            "it into astronaut-drama scenes. KeyFrameAgent plans keyframes for the "
            "spacecraft-cabin settings from text alone. VideoAgent assembles the multi-shot "
            "film. AmbienceAgent generates the spacecraft-cabin room-tone bed. AudioMixAgent "
            "layers it under the dialogue+foley. CompositorAgent muxes the final mp4. Reject "
            "MusicAgent, Transcription/Translation, VideoAnalysis/IntakeVideo/StyleTransfer/"
            "VideoExtend/Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the astronaut story blueprint — solo astronaut on last mission before retirement arc.",
            "Decompose the last-mission arc into astronaut-drama scenes with quiet reflective register.",
            "Plan keyframes for the spacecraft-cabin settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving astronaut-drama visual continuity.",
            "Generate the spacecraft-cabin ambient bed the user requested, matching the orbital-spacecraft environment.",
            "Layer the spacecraft-cabin ambience bed under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final astronaut mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a mini-drama about a night-shift ER triage nurse handling a multi-vehicle crash, with ER-triage ambient.",
        "rationale": (
            "Hospital-drama mini-drama from a text brief + ER-triage ambient. StoryAgent "
            "drafts the night-shift-ER-triage-nurse / multi-vehicle-crash blueprint. "
            "ScreenplayAgent breaks it into ER-drama scenes with high-tension pacing. "
            "KeyFrameAgent plans keyframes for the ER-triage settings from text alone. "
            "VideoAgent assembles the multi-shot film. AmbienceAgent generates the ER-triage "
            "room-tone bed. AudioMixAgent layers it under the dialogue+foley. CompositorAgent "
            "muxes the final mp4. Reject MusicAgent, Transcription/Translation, VideoAnalysis/"
            "IntakeVideo/StyleTransfer/VideoExtend/Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the ER story blueprint — night-shift ER-triage nurse handling multi-vehicle crash arc.",
            "Decompose the crash-triage arc into ER-drama scenes with high-tension pacing.",
            "Plan keyframes for the ER-triage settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving ER-drama visual continuity.",
            "Generate the ER-triage ambient bed the user requested, matching the ER-triage environment.",
            "Layer the ER-triage ambience bed under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final ER mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
]
