"""Long-story variant of cr_music — same chain as shape_cr_music.py but
user_goal is novella-length prose. 10 samples target.

PER-SAMPLE TAILORED design (matching highlight_subtitle.py quality bar):
each sample's rationale references its own user-stated genre / theme +
audio ask + names what each agent does for THIS user_goal. Intents reference
user_goal's specific protagonist / setting / theme keywords (which are user-
authored prose, not invented narrative). 10 distinct long-form briefs.
"""
from __future__ import annotations


SAMPLES: list[dict] = [
    {
        "user_goal": "Here's my story I want to process: Adaora Okonkwo had spent nine years being the smartest person in every conference room at Meridian Equity without anyone quite noticing. She was hired out of business school as an equity analyst; at twenty-nine she is still an equity analyst. The men she graduated with are now directors. Her boss, Richard Voss, is a charming tyrant who has built his reputation on her research, her models, her weekend all-nighters. He takes her to client dinners to show her off, not to include her. When a headhunter from a rival firm reaches out to Adaora with an offer — one that would make her the firm's first Black female managing director — she has six weeks to decide, six weeks during which she must quietly prove Voss has been plagiarising her work. What follows is how she does it, and what happens the morning she walks into his office with the evidence. — add a tense orchestral BGM.",
        "rationale": (
            "Long-form corporate-revenge novella + tense orchestral BGM. StoryAgent drafts "
            "the Adaora / Voss / Meridian-Equity revenge blueprint from the user's prose. "
            "ScreenplayAgent breaks it into corporate-thriller scenes. KeyFrameAgent plans "
            "keyframes for the corporate / boardroom settings from text alone (no reference "
            "images). VideoAgent assembles the multi-shot film. MusicAgent composes the tense "
            "orchestral score. AudioMixAgent layers it under the dialogue+foley. "
            "CompositorAgent muxes the final mp4. Reject AmbienceAgent (no environmental "
            "ask), Transcription/Translation (no subtitle ask), VideoAnalysis/IntakeVideo/"
            "StyleTransfer/VideoExtend/Highlight (story is pasted prose, not source clip), "
            "Narration/Illustration/Narrator (cinematic film, not slideshow voiceover)."
        ),
        "intents": [
            "Polish the user's long-form corporate-revenge prose into a story blueprint — Adaora's nine-year analyst arc, Voss's plagiarism, and the six-week proof-gathering.",
            "Decompose the corporate-revenge arc into scenes spanning the Meridian-Equity offices, headhunter approach, and confrontation morning.",
            "Plan keyframes for the corporate / boardroom settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving corporate-thriller visual continuity across the office cuts.",
            "Compose the tense orchestral BGM the user requested, matching the corporate-revenge register.",
            "Layer the orchestral score under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final corporate-revenge mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Here's my story I want to process: Young Master Xue Yan was born with a cultivator's body — slender, clear-eyed, impossibly attuned to the flow of spirit energy — but his family had been destroyed when he was seven years old, and he remembered nothing of it except fire. For twelve years he lived as a servant at Azure Cloud Mountain Sect, sweeping the courtyards of elders who would never teach him. On the night of his nineteenth birthday, while he was scrubbing the old meditation hall under a moon that was red, the iron bell his mother had tied to his wrist the night she died rang on its own. What opened inside him was not a cultivation realm he had ever heard named. It was older. It was darker. Three days later, when the elders descended to ask how a servant boy had broken a Sixth Rank warded threshold with his bare palm, Xue Yan could only say that the bell had told him to. — add an epic Chinese-orchestral BGM.",
        "rationale": (
            "Long-form cultivation-fantasy novella + epic Chinese-orchestral BGM. StoryAgent "
            "drafts the Xue Yan / Azure Cloud Mountain Sect / iron-bell-awakening blueprint. "
            "ScreenplayAgent breaks it into cultivation-fantasy scenes. KeyFrameAgent plans "
            "keyframes for the sect / meditation-hall settings from text alone. VideoAgent "
            "assembles the multi-shot film. MusicAgent composes the Chinese-orchestral score. "
            "AudioMixAgent layers it under the dialogue+foley. CompositorAgent muxes the "
            "final mp4. Reject AmbienceAgent, Transcription/Translation, VideoAnalysis/"
            "IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), "
            "Narration/Illustration/Narrator."
        ),
        "intents": [
            "Polish the cultivation-fantasy long-form brief into a story blueprint — Xue Yan's twelve servant years, the iron-bell awakening, and the warded-threshold breaking.",
            "Decompose the bloodline-awakening arc into cultivation-fantasy scenes with Chinese-mythos pacing.",
            "Plan keyframes for the Azure Cloud Mountain Sect / meditation-hall settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving cultivation-fantasy visual continuity.",
            "Compose the epic Chinese-orchestral BGM the user requested, matching the cultivation-awakening register.",
            "Layer the Chinese-orchestral score under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final cultivation-fantasy mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Here's my story I want to process: Ingrid Lin died the first time on a Tuesday afternoon at thirty-four, pushed from a seventh-floor balcony by her husband of eleven years at the end of what she had believed was an ordinary argument about money. She opened her eyes and was seventeen again — standing in a Westbridge Academy hallway in the gray pleated uniform she had not worn in nearly two decades, holding a chemistry textbook she remembered the way one remembers a distant relative. A bell rang somewhere far away. Ingrid, who had bled to death on a sidewalk minutes before, stood very still in that hallway for what must have been a long time. Then she walked into the chemistry classroom, sat down, and began to plan. This is the story of how one woman used a second life to end the man who had ended her first one — and how she discovered, along the way, that she had not been his only victim. — add a tense piano-and-strings BGM.",
        "rationale": (
            "Long-form rebirth-revenge novella + tense piano-and-strings BGM. StoryAgent "
            "drafts the Ingrid Lin / Westbridge Academy / second-life-revenge blueprint. "
            "ScreenplayAgent breaks it into rebirth-thriller scenes. KeyFrameAgent plans "
            "keyframes for the academy-hallway / chemistry-classroom settings from text "
            "alone. VideoAgent assembles the multi-shot film. MusicAgent composes the "
            "piano-and-strings score. AudioMixAgent layers it under the dialogue+foley. "
            "CompositorAgent muxes the final mp4. Reject AmbienceAgent, Transcription/"
            "Translation, VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight, "
            "Narration/Illustration/Narrator."
        ),
        "intents": [
            "Polish the rebirth-revenge long-form brief into a story blueprint — Ingrid's seventh-floor death, seventeen-year-old rebirth, and second-life plan.",
            "Decompose the rebirth-revenge arc into rebirth-thriller scenes.",
            "Plan keyframes for the Westbridge Academy hallway / chemistry-classroom / sidewalk settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving rebirth-thriller visual continuity.",
            "Compose the tense piano-and-strings BGM the user requested, matching the rebirth-revenge register.",
            "Layer the piano-and-strings score under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final rebirth-revenge mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Here's my story I want to process: Beatrice Wu was sixty-three years old when she walked into the boardroom of the Meridian Trust and resigned from its board, the same board she had chaired for nineteen years, because she had finally confirmed that her own nephew had been embezzling from a foundation she had set up in honour of her late husband. Nobody on the board had believed her the first three times she had raised concerns. She had hired an outside forensic accountant on her own dime and waited six months to have the file airtight. At the meeting, after she resigned, she slid the report across the table. The nephew was arrested that evening. What follows is how Beatrice, for the first time in forty years, decided what she actually wanted the rest of her life to look like. — add a dignified chamber-strings BGM.",
        "rationale": (
            "Long-form late-career-reinvention novella + dignified chamber-strings BGM. "
            "StoryAgent drafts the Beatrice Wu / Meridian-Trust / nephew-embezzlement / "
            "post-resignation blueprint. ScreenplayAgent breaks it into reinvention-drama "
            "scenes. KeyFrameAgent plans keyframes for the boardroom / forensic-office "
            "settings from text alone. VideoAgent assembles the multi-shot film. MusicAgent "
            "composes the chamber-strings score. AudioMixAgent layers it under the dialogue+"
            "foley. CompositorAgent muxes the final mp4. Reject AmbienceAgent, Transcription/"
            "Translation, VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight, "
            "Narration/Illustration/Narrator."
        ),
        "intents": [
            "Polish the late-career-reinvention long-form brief into a story blueprint — Beatrice's six-month forensic file, board resignation, and post-resignation life-rebuild.",
            "Decompose the reinvention arc into corporate / personal scenes.",
            "Plan keyframes for the Meridian-Trust boardroom / forensic-accountant office settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving reinvention-drama visual continuity.",
            "Compose the dignified chamber-strings BGM the user requested, matching the late-career-reinvention register.",
            "Layer the chamber-strings score under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final reinvention mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Here's my story I want to process: Eleanor Voss had been the first woman to conduct the Philharmonic of Vienna for seventeen years when the new music director, a thirty-two-year-old conductor with a famous surname, told the orchestra — without consulting her — that she would be stepping back to 'principal conductor emeritus' and taking only four concerts a season. Eleanor was fifty-eight. She had, by common agreement, three more good years in her. She went home that night, poured herself a glass of wine, and took out every recording she had ever made with the orchestra. By morning she had decided that she would accept the demotion, and that in the remaining four concerts she would conduct the pieces no one else wanted to, and she would make them the most talked-about concerts of the season. What follows is the year Eleanor spent planning, rehearsing, and finally delivering those four concerts — and the one phone call she took the week after the last one. — add a sweeping Romantic-orchestral BGM.",
        "rationale": (
            "Long-form artistic-reclamation novella + sweeping Romantic-orchestral BGM. "
            "StoryAgent drafts the Eleanor Voss / Vienna-Philharmonic / four-concerts-defiance "
            "blueprint. ScreenplayAgent breaks it into reclamation-drama scenes. "
            "KeyFrameAgent plans keyframes for the Philharmonic-stage / rehearsal-room / "
            "living-room settings from text alone. VideoAgent assembles the multi-shot film. "
            "MusicAgent composes the Romantic-orchestral score. AudioMixAgent layers it under "
            "the dialogue+foley. CompositorAgent muxes the final mp4. Reject AmbienceAgent, "
            "Transcription/Translation, VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/"
            "Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Polish the artistic-reclamation long-form brief into a story blueprint — Eleanor's demotion, four-concert defiance, and post-final-concert phone call.",
            "Decompose the reclamation arc into Philharmonic-rehearsal-and-concert scenes.",
            "Plan keyframes for the Philharmonic-stage / rehearsal-room / Eleanor's-living-room settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving reclamation-drama visual continuity.",
            "Compose the sweeping Romantic-orchestral BGM the user requested, matching the artistic-reclamation register.",
            "Layer the Romantic-orchestral score under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final artistic-reclamation mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Here's my story I want to process: Jun Park, thirty-six, had been a pediatric oncologist at Seoul Asan Medical for thirteen years when a family she had treated ten years earlier wrote to thank her for the life their son had gotten to live — and to let her know he had died the previous Tuesday from a complication of his treatment. Jun had not remembered the boy's name until she read it in the letter. She had saved other children since. She had retired early at sixty-one in her head, the way doctors do. But that night she sat in the empty hospital chapel and wrote, on the back of a discharge form, a list of the thirty-two children she had lost over thirteen years. Each name took a breath to write. What follows is the year Jun spent tracing every family on the list and asking what they had wished, back then, that the hospital had done differently — and what she built out of their answers. — add a tender piano-and-cello BGM.",
        "rationale": (
            "Long-form doctor-and-grief novella + tender piano-and-cello BGM. StoryAgent "
            "drafts the Jun Park / Seoul-Asan / thirty-two-names-list / family-tracing "
            "blueprint. ScreenplayAgent breaks it into grief-drama scenes. KeyFrameAgent "
            "plans keyframes for the Seoul-Asan hospital / chapel / family-interview settings "
            "from text alone. VideoAgent assembles the multi-shot film. MusicAgent composes "
            "the piano-and-cello score. AudioMixAgent layers it under the dialogue+foley. "
            "CompositorAgent muxes the final mp4. Reject AmbienceAgent, Transcription/"
            "Translation, VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight, "
            "Narration/Illustration/Narrator."
        ),
        "intents": [
            "Polish the doctor-and-grief long-form brief into a story blueprint — Jun's family-letter, chapel-list-writing, and year of family interviews.",
            "Decompose the grief arc into grief-drama scenes.",
            "Plan keyframes for the Seoul-Asan hospital / chapel / family-interview settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving grief-drama visual continuity.",
            "Compose the tender piano-and-cello BGM the user requested, matching the doctor-and-grief register.",
            "Layer the piano-and-cello score under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final doctor-and-grief mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Here's my story I want to process: When Fatima al-Rashid was thirty-one years old her husband of six years left her, without warning, on a Thursday afternoon in March, while she was picking up their daughter from pre-school. He had rented a flat in the city. He had taken most of their shared savings. He had left a note that said, simply, that he was sorry. Fatima had been a junior architect for eight years and had given up a promotion to move to the city where he worked. On the first Monday after the note she went back to the architecture practice and told them she was ready to take the promotion now. She got it. What follows is the five years during which she made partner, learned to raise her daughter alone, and finally — in a restaurant in Dubai where he had asked to meet — said the things she had been rehearsing for five years. — add a poised neo-classical piano BGM.",
        "rationale": (
            "Long-form single-mother-reinvention novella + poised neo-classical piano BGM. "
            "StoryAgent drafts the Fatima / husband-leaves / five-year-partner-track blueprint. "
            "ScreenplayAgent breaks it into reinvention-drama scenes. KeyFrameAgent plans "
            "keyframes for the architecture-practice / pre-school / Dubai-restaurant settings "
            "from text alone. VideoAgent assembles the multi-shot film. MusicAgent composes "
            "the neo-classical piano score. AudioMixAgent layers it under the dialogue+foley. "
            "CompositorAgent muxes the final mp4. Reject AmbienceAgent, Transcription/"
            "Translation, VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight, "
            "Narration/Illustration/Narrator."
        ),
        "intents": [
            "Polish the single-mother-reinvention long-form brief into a story blueprint — Fatima's husband-leaves Thursday, partner-track climb, and Dubai restaurant confrontation.",
            "Decompose the reinvention arc into reinvention-drama scenes.",
            "Plan keyframes for the architecture-practice / pre-school / Dubai-restaurant settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving reinvention-drama visual continuity.",
            "Compose the poised neo-classical piano BGM the user requested, matching the single-mother-reinvention register.",
            "Layer the neo-classical piano score under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final reinvention mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Here's my story I want to process: Dr. Hiroshi Tanaka, sixty-seven, was the last practicing katana swordsmith in Kagoshima when his only apprentice of twenty-two years, a thirty-five-year-old American named Sarah, told him she had to go home because her father was dying. Hiroshi had planned on retiring at seventy. He had planned to hand the forge to Sarah. Without her, the tradition would die with him in a handful of years. He bowed when she told him, as was the custom, and said the right things, and gave her a small tanto he had made in 1994 as a gift. Three months later she was gone. This is the story of the year Hiroshi spent re-learning how to teach, travelling three times to Ohio, and finally — at her father's funeral in late November — offering Sarah a proposal neither of them had expected. — add a traditional shakuhachi-and-koto BGM.",
        "rationale": (
            "Long-form master-apprentice-tradition novella + traditional shakuhachi-and-koto "
            "BGM. StoryAgent drafts the Hiroshi / Sarah / Kagoshima-forge / Ohio-funeral "
            "blueprint. ScreenplayAgent breaks it into tradition-drama scenes. KeyFrameAgent "
            "plans keyframes for the Kagoshima-forge / Ohio-kitchen / funeral-hall settings "
            "from text alone. VideoAgent assembles the multi-shot film. MusicAgent composes "
            "the shakuhachi-and-koto score. AudioMixAgent layers it under the dialogue+foley. "
            "CompositorAgent muxes the final mp4. Reject AmbienceAgent, Transcription/"
            "Translation, VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight, "
            "Narration/Illustration/Narrator."
        ),
        "intents": [
            "Polish the master-apprentice-tradition long-form brief into a story blueprint — Hiroshi's Kagoshima forge, Sarah's departure, and Ohio-funeral proposal.",
            "Decompose the tradition arc into master-apprentice scenes spanning Japan and Ohio.",
            "Plan keyframes for the Kagoshima-forge / Ohio-kitchen / November-funeral-hall settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving tradition-drama visual continuity across the cross-cultural cuts.",
            "Compose the traditional shakuhachi-and-koto BGM the user requested, matching the master-apprentice register.",
            "Layer the shakuhachi-and-koto score under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final master-apprentice mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Here's my story I want to process: Siobhán Byrne had been a detective sergeant with the Garda for nineteen years when, in the autumn of her forty-third year, she found herself assigned, quietly, to a cold-case reopened after an anonymous tip: the disappearance of a fourteen-year-old girl from a small town in County Wexford in 1994. Siobhán had grown up in that town. She had known that fourteen-year-old girl. The tip was credible enough that the national team decided the case needed a detective from outside with no obvious tie to anyone still living there — and then, because Siobhán had asked to be kept off the file, they gave it to her by mistake. She read the first ten pages and walked out of the office and did not come back for three days. When she did, she asked for the case. This is the story of the winter she spent solving it. — add an atmospheric Celtic-strings BGM.",
        "rationale": (
            "Long-form cold-case-detective novella + atmospheric Celtic-strings BGM. "
            "StoryAgent drafts the Siobhán / Garda / County-Wexford / 1994-cold-case "
            "blueprint. ScreenplayAgent breaks it into cold-case-detective scenes. "
            "KeyFrameAgent plans keyframes for the Garda-office / County-Wexford-village "
            "settings from text alone. VideoAgent assembles the multi-shot film. MusicAgent "
            "composes the Celtic-strings score. AudioMixAgent layers it under the dialogue+"
            "foley. CompositorAgent muxes the final mp4. Reject AmbienceAgent, Transcription/"
            "Translation, VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight, "
            "Narration/Illustration/Narrator."
        ),
        "intents": [
            "Polish the cold-case-detective long-form brief into a story blueprint — Siobhán's mis-assigned 1994 County-Wexford cold case and winter investigation.",
            "Decompose the cold-case arc into Garda-detective scenes.",
            "Plan keyframes for the Garda-office / County-Wexford coastal-village settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving cold-case-detective visual continuity.",
            "Compose the atmospheric Celtic-strings BGM the user requested, matching the cold-case-detective register.",
            "Layer the Celtic-strings score under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final cold-case-detective mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Here's my story I want to process: Clara Montenegro, forty-nine, had run a small bookstore in the Chueca district of Madrid for sixteen years — the kind of bookstore that sold mostly second-hand literature, put out a chair for a regular cat, and ran a reading group for retirees on Wednesday afternoons — when a large American chain opened a flagship three blocks away and offered to buy her lease. The offer was generous. The neighbours were mostly sympathetic; the neighbourhood had changed. Clara said no, went home, and told her partner she planned to make the bookstore the most interesting bookstore in Madrid by spring. She had no plan. This is the story of the six months Clara spent putting one together — and the Saturday in May when the American chain's CEO flew in to talk to her personally. — add a warm Spanish-guitar BGM.",
        "rationale": (
            "Long-form small-business-resistance novella + warm Spanish-guitar BGM. "
            "StoryAgent drafts the Clara / Chueca-Madrid bookstore / American-chain blueprint. "
            "ScreenplayAgent breaks it into bookstore-drama scenes. KeyFrameAgent plans "
            "keyframes for the Chueca-bookstore / six-month-transformation / Saturday-CEO-"
            "visit settings from text alone. VideoAgent assembles the multi-shot film. "
            "MusicAgent composes the Spanish-guitar score. AudioMixAgent layers it under the "
            "dialogue+foley. CompositorAgent muxes the final mp4. Reject AmbienceAgent, "
            "Transcription/Translation, VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/"
            "Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Polish the small-business-resistance long-form brief into a story blueprint — Clara's Chueca bookstore, lease-offer refusal, and Saturday CEO visit.",
            "Decompose the resistance arc into bookstore-drama scenes.",
            "Plan keyframes for the Chueca-Madrid-bookstore / six-month-transformation / Saturday-meeting settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving bookstore-drama visual continuity.",
            "Compose the warm Spanish-guitar BGM the user requested, matching the small-business-resistance register.",
            "Layer the Spanish-guitar score under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final small-business-resistance mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
]
