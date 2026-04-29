"""Long-story variant of cr_ambience — same chain as shape_cr_ambience.py but
user_goal is novella-length prose. 11 samples.

PER-SAMPLE TAILORED design (matching highlight_subtitle.py quality bar):
each sample's rationale references its own user-stated genre / theme +
specific ambient ask + names what each agent does for THIS user_goal.
Intents reference user_goal's protagonist / setting / theme keywords.
Reject MusicAgent because user asked atmospheric / environmental sound,
not music. AmbienceAgent step uses ambience-class verbs (Generate / Lay /
Synthesize), NOT music verbs.
"""
from __future__ import annotations


SAMPLES: list[dict] = [
    {
        "user_goal": "Here's my story I want to process: When Claire Delacroix was eleven years old her mother married into the Havenwood family and Claire was taken to live in a house she would grow to hate. Havenwood was a tall gray Victorian on a Louisiana bayou, built by a family of cane planters in 1871, with wrought-iron galleries and shuttered rooms and a long history of quiet dying. The housekeeper, Mrs. Peltier, had served three generations of Havenwoods and she liked Claire's mother and disliked Claire. This is the story of the eight years Claire spent planning to leave that house, and the one night she came back, and what she found waiting for her in the music room where her mother had died. — add haunted Southern-Gothic mansion (creaking floors, distant whispers, wind through shutters) ambient sounds.",
        "rationale": (
            "Long-form Southern-Gothic novella + haunted-mansion ambient sounds (creaking "
            "floors, distant whispers, wind through shutters) as audio layer. StoryAgent "
            "drafts the Claire / Havenwood / Mrs. Peltier blueprint from the user's prose. "
            "ScreenplayAgent breaks it into Southern-Gothic scenes. KeyFrameAgent plans "
            "keyframes for the 1871 Louisiana-bayou Victorian settings from text alone. "
            "VideoAgent assembles the multi-shot film. AmbienceAgent generates the "
            "haunted-Havenwood room-tone bed. AudioMixAgent layers it under the dialogue+"
            "foley. CompositorAgent muxes the final mp4. Reject MusicAgent (user asked "
            "environmental atmosphere, not a music score), Transcription/Translation (no "
            "subtitle ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight "
            "(prose-only brief, no source clip), Narration/Illustration/Narrator."
        ),
        "intents": [
            "Polish the Southern-Gothic long-form prose into a story blueprint — Claire's eight years at Havenwood, the night she returns, and the music room arc.",
            "Decompose the Havenwood arc into Southern-Gothic scenes with quiet-dread pacing.",
            "Plan keyframes for the 1871 Louisiana-bayou Victorian / wrought-iron-gallery / music-room settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving Southern-Gothic visual continuity across the Havenwood cuts.",
            "Generate the haunted Southern-Gothic mansion ambient bed (creaking floors, distant whispers, wind through shutters) the user requested, matching the Havenwood environment.",
            "Layer the haunted-mansion ambience bed under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final Southern-Gothic mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Here's my story I want to process: Dr. Siena Okafor was thirty-nine when her research grant in marine neuroscience ran out and she took, reluctantly, a contract job as head naturalist on a small research vessel tracking sperm-whale pods in the Sea of Cortez. The boat was old. The crew was short. The previous naturalist had disappeared from the deck one night and no one had ever found out how. Siena was supposed to be there six weeks. In the first week she heard something recorded on the vessel's hydrophones that made no biological sense, and a copy of the file went missing from the ship's server the next day. This is the story of the three weeks that followed, the decisions Siena made in a radio room at three in the morning, and the report she eventually refused to sign. — add deep-Pacific ocean ambient (hull creaks, distant whale calls, wind) ambient sounds.",
        "rationale": (
            "Long-form deep-sea-mystery novella + deep-Pacific ocean ambient (hull creaks, "
            "distant whale calls, wind) as audio layer. StoryAgent drafts the Siena Okafor / "
            "Sea-of-Cortez / sperm-whale-research-vessel blueprint. ScreenplayAgent breaks "
            "it into deep-sea-mystery scenes. KeyFrameAgent plans keyframes for the research-"
            "vessel / radio-room settings from text alone. VideoAgent assembles the multi-shot "
            "film. AmbienceAgent generates the deep-Pacific room-tone bed. AudioMixAgent "
            "layers it under the dialogue+foley. CompositorAgent muxes the final mp4. Reject "
            "MusicAgent, Transcription/Translation, VideoAnalysis/IntakeVideo/StyleTransfer/"
            "VideoExtend/Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Polish the deep-sea-mystery long-form prose into a story blueprint — Siena's six-week contract, the missing hydrophone file, and the report she refuses to sign.",
            "Decompose the research-vessel mystery arc into deep-sea-mystery scenes.",
            "Plan keyframes for the research-vessel-deck / radio-room settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving deep-sea-mystery visual continuity.",
            "Generate the deep-Pacific ocean ambient bed (hull creaks, distant whale calls, wind) the user requested, matching the Sea-of-Cortez vessel environment.",
            "Layer the deep-Pacific ambience bed under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final deep-sea-mystery mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Here's my story I want to process: At fifty-one Louise Bergeron was the chef-owner of a two-star bistro in the 11th arrondissement of Paris when she received, on an ordinary Wednesday in November, a phone call from a woman who identified herself as Louise's half-sister. Louise had not known she had a half-sister. Her mother, a chain-smoking actress who had died in 1998, had a great deal to answer for, but another child had not been on the list. Adelaide, who lived in Nice, was forty-four, and had a daughter named Camille who was dying, very slowly, of a rare marrow disease that only a sibling could donate the cure for. This is the story of the winter Louise closed her bistro, drove to Nice, and tried to save a girl she did not yet love. — add Parisian-bistro and seaside-Nice layered ambient (distant kitchen, Mediterranean waves, gull cries) ambient sounds.",
        "rationale": (
            "Long-form family-discovery novella + layered Parisian-bistro / seaside-Nice "
            "ambient sounds (distant kitchen, Mediterranean waves, gull cries) as audio layer. "
            "StoryAgent drafts the Louise / Adelaide / Camille / Paris-to-Nice blueprint. "
            "ScreenplayAgent breaks it into family-discovery scenes spanning two cities. "
            "KeyFrameAgent plans keyframes for the Paris-bistro / Nice-coast settings from "
            "text alone. VideoAgent assembles the multi-shot film. AmbienceAgent generates "
            "the layered Paris/Nice room-tone bed. AudioMixAgent layers it under the dialogue+"
            "foley. CompositorAgent muxes the final mp4. Reject MusicAgent, Transcription/"
            "Translation, VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight, "
            "Narration/Illustration/Narrator."
        ),
        "intents": [
            "Polish the family-discovery long-form prose into a story blueprint — Louise's half-sister phone call, Paris bistro closure, and Nice-winter-rescue arc.",
            "Decompose the family-discovery arc into Paris-to-Nice scenes.",
            "Plan keyframes for the 11th-arrondissement-bistro / Nice-coast settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving the Paris-to-Nice transition visual continuity.",
            "Generate the layered Parisian-bistro and seaside-Nice ambient bed (distant kitchen, Mediterranean waves, gull cries) the user requested, matching the two-city environment.",
            "Layer the Paris-Nice layered ambience bed under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final family-discovery mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Here's my story I want to process: Tomás Hernández, forty-two, had been a firefighter in the Sonoran Desert for nineteen years when the worst wildfire in the region's history bore down on the small town where he had grown up and where his elderly mother still lived. Tomás was in another county when the call came in; by the time he reached home the fire had already jumped the highway and the evacuation order was six hours old. His mother was not in the shelter. She had refused to leave without her dogs. What follows is the story of the twenty-three hours Tomás spent looking for her, the people he found along the way, and the moment at dawn when he finally understood what she had been waiting for. — add wildfire / high-desert ambient (crackling fire at distance, dry wind, distant sirens) ambient sounds.",
        "rationale": (
            "Long-form wildfire-rescue novella + wildfire / high-desert ambient sounds "
            "(crackling fire at distance, dry wind, distant sirens) as audio layer. "
            "StoryAgent drafts the Tomás / Sonoran-Desert / mother-and-dogs blueprint. "
            "ScreenplayAgent breaks it into wildfire-rescue scenes. KeyFrameAgent plans "
            "keyframes for the high-desert / fire-jump-highway / mother's-house settings "
            "from text alone. VideoAgent assembles the multi-shot film. AmbienceAgent "
            "generates the wildfire / high-desert room-tone bed. AudioMixAgent layers it "
            "under the dialogue+foley. CompositorAgent muxes the final mp4. Reject "
            "MusicAgent, Transcription/Translation, VideoAnalysis/IntakeVideo/StyleTransfer/"
            "VideoExtend/Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Polish the wildfire-rescue long-form prose into a story blueprint — Tomás's nineteen-year firefighter tenure, twenty-three-hour search, and dawn realization arc.",
            "Decompose the wildfire-rescue arc into Sonoran-Desert wildfire scenes with rising tension.",
            "Plan keyframes for the high-desert / fire-jump-highway / mother's-house settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving wildfire-rescue visual continuity.",
            "Generate the wildfire / high-desert ambient bed (crackling fire at distance, dry wind, distant sirens) the user requested, matching the Sonoran-Desert wildfire environment.",
            "Layer the wildfire ambience bed under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final wildfire-rescue mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Here's my story I want to process: Hans-Erik Lindqvist had been shepherd of the Jokkmokk reindeer herd for forty-one years when his daughter Ida moved back from Stockholm to tell him that the mining consortium had been approved to dig under their traditional grazing land, and that he had three months to move the herd or lose it. Hans-Erik was sixty-seven. Ida was thirty-six. Neither of them had spoken about Ida's mother in twenty years, since the day of the funeral in 2005. This is the story of the year the Lindqvists lost their land, won a Supreme Court injunction, and rebuilt a relationship neither of them had known how to repair. — add Lapland tundra ambient (howling wind, distant reindeer bells, snow crunch) ambient sounds.",
        "rationale": (
            "Long-form Sami-tundra family novella + Lapland tundra ambient sounds (howling "
            "wind, distant reindeer bells, snow crunch) as audio layer. StoryAgent drafts the "
            "Hans-Erik / Ida / Jokkmokk-reindeer-herd / mining-consortium blueprint. "
            "ScreenplayAgent breaks it into Sami-tundra family scenes. KeyFrameAgent plans "
            "keyframes for the Lapland-tundra / herd-grazing settings from text alone. "
            "VideoAgent assembles the multi-shot film. AmbienceAgent generates the Lapland-"
            "tundra room-tone bed. AudioMixAgent layers it under the dialogue+foley. "
            "CompositorAgent muxes the final mp4. Reject MusicAgent, Transcription/"
            "Translation, VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight, "
            "Narration/Illustration/Narrator."
        ),
        "intents": [
            "Polish the Sami-tundra family long-form prose into a story blueprint — Hans-Erik's forty-one-year reindeer-shepherd tenure, the mining-consortium injunction year, and father-daughter rebuild.",
            "Decompose the tundra arc into Sami-family scenes spanning a year.",
            "Plan keyframes for the Jokkmokk-tundra / Lapland herd-grazing settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving Sami-tundra visual continuity.",
            "Generate the Lapland tundra ambient bed (howling wind, distant reindeer bells, snow crunch) the user requested, matching the Jokkmokk-tundra environment.",
            "Layer the Lapland-tundra ambience bed under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final Sami-tundra mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Here's my story I want to process: Maeve O'Brien had lived her entire life in the same three-bedroom cottage on the Atlantic coast of County Kerry when, at the age of seventy-two, she received a letter from a solicitor in Dublin informing her that her late husband, a quiet and gentle postmaster named Seamus who had died of a heart attack in the potato garden eleven years earlier, had left her a bank account in the Cayman Islands containing a little over one million Euro. Maeve had never been to the Cayman Islands. Seamus had never, to her knowledge, been outside of Ireland. This is the story of the summer Maeve hired a private investigator from Cork and uncovered the version of her husband he had spent his entire married life protecting her from. — add Irish-coastal cottage ambient (waves, distant gulls, wind through the chimney) ambient sounds.",
        "rationale": (
            "Long-form Irish-coastal-mystery novella + Irish-coastal cottage ambient sounds "
            "(waves, distant gulls, wind through the chimney) as audio layer. StoryAgent "
            "drafts the Maeve O'Brien / County-Kerry-cottage / Cayman-account blueprint. "
            "ScreenplayAgent breaks it into Irish-coastal mystery scenes. KeyFrameAgent plans "
            "keyframes for the Atlantic-coast cottage / Cork-investigator settings from text "
            "alone. VideoAgent assembles the multi-shot film. AmbienceAgent generates the "
            "Irish-coastal cottage room-tone bed. AudioMixAgent layers it under the dialogue+"
            "foley. CompositorAgent muxes the final mp4. Reject MusicAgent, Transcription/"
            "Translation, VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight, "
            "Narration/Illustration/Narrator."
        ),
        "intents": [
            "Polish the Irish-coastal-mystery long-form prose into a story blueprint — Maeve's seventy-two-year cottage life, Cayman-account letter, and summer-investigation arc.",
            "Decompose the late-husband-mystery arc into Irish-coastal scenes.",
            "Plan keyframes for the Atlantic-coast cottage / Cork-investigator settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving Irish-coastal-mystery visual continuity.",
            "Generate the Irish-coastal cottage ambient bed (waves, distant gulls, wind through the chimney) the user requested, matching the County-Kerry coastal environment.",
            "Layer the Irish-coastal ambience bed under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final Irish-coastal-mystery mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Here's my story I want to process: When Dr. Faye Marlowe arrived at the Westcott Institute in the autumn of 2031 she was thirty-eight years old, the youngest neuroscientist ever tenured at her previous university, and she was carrying a small portable cooler that contained what she believed to be the solution to Alzheimer's disease. On her first day, in the basement lab of the east wing, she met the building's caretaker, a very old man named Bernard who told her, with a small careful smile, that the wing she would be working in had housed a researcher named Margaret Yu who had made the same breakthrough in 1987 — and then had not been heard from again. This is the story of what happened to Margaret Yu and what the Westcott wanted Faye to keep from the world. — add old-institute basement ambient (HVAC hum, distant footsteps in stone halls, flickering light buzz) ambient sounds.",
        "rationale": (
            "Long-form scientific-conspiracy novella + old-institute basement ambient sounds "
            "(HVAC hum, distant footsteps in stone halls, flickering light buzz) as audio "
            "layer. StoryAgent drafts the Faye Marlowe / Westcott Institute / Margaret Yu / "
            "Bernard blueprint. ScreenplayAgent breaks it into scientific-conspiracy scenes. "
            "KeyFrameAgent plans keyframes for the Westcott-basement-lab / east-wing settings "
            "from text alone. VideoAgent assembles the multi-shot film. AmbienceAgent "
            "generates the old-institute basement room-tone bed. AudioMixAgent layers it "
            "under the dialogue+foley. CompositorAgent muxes the final mp4. Reject MusicAgent, "
            "Transcription/Translation, VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/"
            "Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Polish the scientific-conspiracy long-form prose into a story blueprint — Faye's Westcott arrival, Bernard's warning, and Margaret Yu disappearance arc.",
            "Decompose the conspiracy arc into scientific-conspiracy scenes.",
            "Plan keyframes for the Westcott-Institute basement-lab / east-wing settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving scientific-conspiracy visual continuity.",
            "Generate the old-institute basement ambient bed (HVAC hum, distant footsteps in stone halls, flickering light buzz) the user requested, matching the Westcott basement environment.",
            "Layer the old-institute basement ambience bed under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final scientific-conspiracy mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Here's my story I want to process: At forty-one Helena Thorvald had been a pediatric oncologist at Karolinska for fourteen years when she lost a six-year-old patient named Lena to a cancer that had taken Helena's own daughter eight years earlier. Helena walked out of the hospital that afternoon and did not come back for seven months. She rented a cabin in northern Lapland with no internet, no mobile phone coverage, and a roof that leaked in April. This is the story of the seven months in the cabin, the twelve months after she came home, and the morning three years later when the clinical trial she had finally written down on paper opened for enrolment at eight hospitals across Europe. — add Lapland-cabin ambient (wind, distant wolves, fire crackles, dripping roof) ambient sounds.",
        "rationale": (
            "Long-form doctor-grief-and-rebuilding novella + Lapland-cabin ambient sounds "
            "(wind, distant wolves, fire crackles, dripping roof) as audio layer. StoryAgent "
            "drafts the Helena Thorvald / Karolinska / Lena / Lapland-cabin blueprint. "
            "ScreenplayAgent breaks it into doctor-grief scenes. KeyFrameAgent plans keyframes "
            "for the Karolinska-hospital / Lapland-cabin settings from text alone. VideoAgent "
            "assembles the multi-shot film. AmbienceAgent generates the Lapland-cabin "
            "room-tone bed. AudioMixAgent layers it under the dialogue+foley. CompositorAgent "
            "muxes the final mp4. Reject MusicAgent, Transcription/Translation, VideoAnalysis/"
            "IntakeVideo/StyleTransfer/VideoExtend/Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Polish the doctor-grief long-form prose into a story blueprint — Helena's Karolinska tenure, Lapland-cabin retreat, and clinical-trial-launch arc.",
            "Decompose the grief-and-rebuilding arc into doctor-drama scenes.",
            "Plan keyframes for the Karolinska-hospital / northern-Lapland-cabin settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving doctor-grief visual continuity.",
            "Generate the Lapland-cabin ambient bed (wind, distant wolves, fire crackles, dripping roof) the user requested, matching the northern-Lapland-cabin environment.",
            "Layer the Lapland-cabin ambience bed under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final doctor-grief mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Here's my story I want to process: Rosario Delgado, fifty-four, had been a park ranger at Redwood National Park for thirty-one years. She was the third generation of her family to work in the park; her grandmother had been one of the first Mexican-American women hired by the National Park Service, in 1961. In the spring of 2031 the Department of the Interior announced that a hundred and eighty square miles of the park would be released for commercial logging. This is the story of the nine months she spent coordinating twenty-two park rangers, three retired federal attorneys, a lobbyist her mother had once shared an office with, and a coalition of tribal nations — to get the order reversed before the first chainsaw arrived. — add old-growth redwood forest ambient (dripping canopy, distant hush of wind, occasional crackle of branches) ambient sounds.",
        "rationale": (
            "Long-form park-ranger-resistance novella + old-growth redwood forest ambient "
            "sounds (dripping canopy, distant hush of wind, occasional crackle of branches) "
            "as audio layer. StoryAgent drafts the Rosario Delgado / Redwood National Park / "
            "Department-of-Interior-logging-reversal blueprint. ScreenplayAgent breaks it "
            "into park-ranger-resistance scenes. KeyFrameAgent plans keyframes for the "
            "Redwood-park / coalition-meetings settings from text alone. VideoAgent assembles "
            "the multi-shot film. AmbienceAgent generates the old-growth redwood forest "
            "room-tone bed. AudioMixAgent layers it under the dialogue+foley. CompositorAgent "
            "muxes the final mp4. Reject MusicAgent, Transcription/Translation, VideoAnalysis/"
            "IntakeVideo/StyleTransfer/VideoExtend/Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Polish the park-ranger-resistance long-form prose into a story blueprint — Rosario's third-generation tenure, nine-month coalition-building, and logging-reversal arc.",
            "Decompose the resistance arc into park-ranger-resistance scenes.",
            "Plan keyframes for the Redwood-National-Park / coalition-meeting settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving park-ranger-resistance visual continuity.",
            "Generate the old-growth redwood forest ambient bed (dripping canopy, distant hush of wind, occasional crackle of branches) the user requested, matching the redwood-grove environment.",
            "Layer the redwood-forest ambience bed under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final park-ranger-resistance mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Here's my story I want to process: Edith Carruthers, fifty-eight, had run the Cedarbrook Public Library for twenty-six years when the town council decided that Cedarbrook no longer needed a library. The council member who delivered the news, a man named Teddy Harrow, had twice lost his library card when he was a teenager and he had never really liked books. He told Edith, in a fluorescent meeting room that smelled of coffee, that the building would be torn down for a new parking garage. The next morning Edith woke before dawn, put on the same gray cardigan she had worn for forty years, and went down to the library, where she sat at her desk and began to write what she would later call 'the campaign'. — add quiet-library after-hours ambient (ticking clock, distant steam pipes, occasional book settling on a shelf) ambient sounds.",
        "rationale": (
            "Long-form library-resistance novella + quiet-library after-hours ambient sounds "
            "(ticking clock, distant steam pipes, occasional book settling on a shelf) as "
            "audio layer. StoryAgent drafts the Edith Carruthers / Cedarbrook / Teddy Harrow "
            "blueprint. ScreenplayAgent breaks it into library-resistance scenes. "
            "KeyFrameAgent plans keyframes for the Cedarbrook-library / council-meeting-room "
            "settings from text alone. VideoAgent assembles the multi-shot film. AmbienceAgent "
            "generates the quiet-library after-hours room-tone bed. AudioMixAgent layers it "
            "under the dialogue+foley. CompositorAgent muxes the final mp4. Reject MusicAgent, "
            "Transcription/Translation, VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/"
            "Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Polish the library-resistance long-form prose into a story blueprint — Edith's twenty-six-year tenure, council demolition decision, and 'the campaign' arc.",
            "Decompose the resistance arc into library-resistance scenes.",
            "Plan keyframes for the Cedarbrook-library / fluorescent council-meeting-room settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving library-resistance visual continuity.",
            "Generate the quiet-library after-hours ambient bed (ticking clock, distant steam pipes, occasional book settling on a shelf) the user requested, matching the Cedarbrook-library environment.",
            "Layer the quiet-library ambience bed under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final library-resistance mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Here's my story I want to process: Benedict Tran was twenty-four years old when his older sister Thuy was killed in a hit-and-run in Oakland on a Thursday night in April. The driver was never found. The police said, with kindness, that these cases rarely were. Benedict, who had just finished law school at Berkeley and had accepted an offer from a firm in Los Angeles, declined the job and moved back into his parents' house in Richmond instead. He spent ten months teaching himself how to be an investigator. In the eleventh month he found the driver, whose name meant nothing to him, and then he found the reason, and the reason was that his sister had seen something she had not realized she had seen. — add rain-on-Oakland ambient (distant traffic, rain on pavement, occasional siren) ambient sounds.",
        "rationale": (
            "Long-form sibling-vengeance / amateur-investigator novella + rain-on-Oakland "
            "ambient sounds (distant traffic, rain on pavement, occasional siren) as audio "
            "layer. StoryAgent drafts the Benedict Tran / Thuy / Oakland hit-and-run / "
            "eleven-month-investigation blueprint. ScreenplayAgent breaks it into amateur-"
            "investigator scenes. KeyFrameAgent plans keyframes for the Oakland-streets / "
            "Richmond-house / Berkeley-law settings from text alone. VideoAgent assembles "
            "the multi-shot film. AmbienceAgent generates the rain-on-Oakland room-tone bed. "
            "AudioMixAgent layers it under the dialogue+foley. CompositorAgent muxes the "
            "final mp4. Reject MusicAgent, Transcription/Translation, VideoAnalysis/"
            "IntakeVideo/StyleTransfer/VideoExtend/Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Polish the amateur-investigator long-form prose into a story blueprint — Benedict's law-school decline, ten-month self-taught investigation, and driver-discovery arc.",
            "Decompose the investigation arc into amateur-investigator scenes.",
            "Plan keyframes for the Oakland-streets / Richmond-house / Berkeley-law-school settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving amateur-investigator visual continuity.",
            "Generate the rain-on-Oakland ambient bed (distant traffic, rain on pavement, occasional siren) the user requested, matching the Oakland-rain environment.",
            "Layer the rain-on-Oakland ambience bed under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final amateur-investigator mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
]
