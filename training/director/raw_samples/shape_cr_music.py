"""Shape: cr_music —
    Story → Screenplay → KeyFrame → Video → Music → AudioMix → Compositor.

Cinematic mini-drama WITH BGM, NO ambient, NO subtitles, NO image upload.
Target 60; this file holds 50 short-brief samples. Long-story variants
in shape_cr_music_long.py.

PER-SAMPLE TAILORED design (matching highlight_subtitle.py quality bar):
  - Each sample's rationale references its own user-stated genre / format /
    audio ask, names what each agent does for THIS user_goal, and lists
    rejected agents with routing-relevant reasons.
  - Each sample's intents reference user-stated genre / setting keywords
    drawn from the user_goal text — not invented narrative (no fictional
    character names, no fabricated plot beats not in user_goal).
  - 50 samples are genuinely distinct: same skeleton structure, but the
    content of every rationale and every intent is sample-specific.
"""
from __future__ import annotations


SAMPLES: list[dict] = [
    {
        "user_goal": "Make a cultivation-fantasy mini-drama about a washed-up disciple who awakens an ancient bloodline and climbs back through his sect's ranks, scored with epic orchestral music.",
        "rationale": (
            "Cultivation-fantasy mini-drama from a text brief + epic orchestral BGM. "
            "StoryAgent drafts the bloodline-awakening / sect-rise blueprint. ScreenplayAgent "
            "breaks the arc into cultivation-fantasy scenes. KeyFrameAgent plans sect / combat "
            "keyframes from text alone (no reference images). VideoAgent assembles the "
            "multi-shot film. MusicAgent composes the orchestral score. AudioMixAgent layers "
            "it under the baked dialogue+foley. CompositorAgent muxes the final mp4. Reject "
            "AmbienceAgent (no environmental layer asked), Transcription/Translation (no "
            "subtitle ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight "
            "(no source clip), Narration/Illustration/Narrator (multi-shot film, not slideshow)."
        ),
        "intents": [
            "Draft the cultivation-fantasy story blueprint — washed-up-disciple bloodline-awakening arc and sect-rise progression.",
            "Decompose the bloodline-rise arc into scenes with cultivation-fantasy mood progression.",
            "Plan keyframes for the sect setting and bloodline-rise visuals; text-only generation, no reference images supplied.",
            "Render per-shot motion clips from the keyframes preserving cultivation-fantasy aesthetic continuity.",
            "Compose the epic orchestral BGM the user requested, matching the cultivation-rise heroic register.",
            "Layer the orchestral score under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final cultivation-fantasy mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a CEO-romance mini-drama where a struggling diner waitress slowly recognizes her brusque regular as the billionaire she saved from a hit-and-run years ago, with a gentle piano theme.",
        "rationale": (
            "CEO-romance mini-drama from a text brief + gentle piano theme as audio layer. "
            "StoryAgent drafts the diner-recognition romance blueprint. ScreenplayAgent breaks "
            "it into CEO-romance scenes. KeyFrameAgent plans diner / corporate keyframes from "
            "text alone. VideoAgent assembles the multi-shot film. MusicAgent composes the "
            "piano theme. AudioMixAgent layers it under the dialogue+foley. CompositorAgent "
            "muxes the final mp4. Reject AmbienceAgent (no environmental ask), Transcription/"
            "Translation (no subtitle ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/"
            "Highlight (no source clip), Narration/Illustration/Narrator (cinematic film, not slideshow)."
        ),
        "intents": [
            "Draft the CEO-romance story blueprint — diner-waitress recognition arc and billionaire-recall progression.",
            "Decompose the recognition arc into scenes with CEO-romance emotional register.",
            "Plan keyframes for the diner / corporate settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving CEO-romance visual continuity across the diner-to-corporate cuts.",
            "Compose the gentle piano theme the user requested, matching the CEO-romance tender register.",
            "Layer the piano theme under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final CEO-romance mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "I want a romance mini-drama where a young woman wins a dating-app lottery and ends up in a contractual fake marriage with a reclusive tech founder, with light acoustic indie BGM.",
        "rationale": (
            "Fake-marriage romance mini-drama from a text brief + light acoustic indie BGM. "
            "StoryAgent drafts the dating-app-lottery / contractual-marriage blueprint. "
            "ScreenplayAgent breaks it into romance scenes. KeyFrameAgent plans keyframes for "
            "the romance settings from text alone. VideoAgent assembles the multi-shot film. "
            "MusicAgent composes the acoustic indie score. AudioMixAgent layers it under the "
            "dialogue+foley. CompositorAgent muxes the final mp4. Reject AmbienceAgent (no "
            "environmental ask), Transcription/Translation (no subtitle), VideoAnalysis/"
            "IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), "
            "Narration/Illustration/Narrator (cinematic film, not slideshow)."
        ),
        "intents": [
            "Draft the romance story blueprint — dating-app-lottery and fake-marriage arc with the user's tech-founder premise.",
            "Decompose the fake-marriage arc into romance scenes with light slow-burn pacing.",
            "Plan keyframes for the romance settings from the screenplay; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving romance visual continuity across the cohabitation cuts.",
            "Compose the light acoustic indie BGM the user requested, matching the romance gentle register.",
            "Layer the acoustic indie score under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final romance mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a workplace-revenge mini-drama where an analyst dismissed for whistleblowing rebuilds her career at a rival firm and dismantles her old boss's insider-trading ring, with tense thriller BGM.",
        "rationale": (
            "Workplace-revenge mini-drama from a text brief + tense thriller BGM. StoryAgent "
            "drafts the analyst-whistleblower / corporate-revenge blueprint. ScreenplayAgent "
            "breaks it into workplace-thriller scenes. KeyFrameAgent plans keyframes for the "
            "corporate settings from text alone. VideoAgent assembles the multi-shot film. "
            "MusicAgent composes the thriller score. AudioMixAgent layers it under the "
            "dialogue+foley. CompositorAgent muxes the final mp4. Reject AmbienceAgent (no "
            "environmental ask), Transcription/Translation (no subtitle), VideoAnalysis/"
            "IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), "
            "Narration/Illustration/Narrator (cinematic film, not slideshow)."
        ),
        "intents": [
            "Draft the workplace-revenge story blueprint — analyst-whistleblower arc and corporate-takedown progression.",
            "Decompose the revenge arc into workplace-thriller scenes with escalating tension.",
            "Plan keyframes for the corporate settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving workplace-thriller visual continuity across the corporate cuts.",
            "Compose the tense thriller BGM the user requested, matching the corporate-revenge register.",
            "Layer the thriller score under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final workplace-revenge mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make an underdog-comeback mini-drama where a live-in son-in-law thrown out by his rich in-laws turns out to be the secret heir of a top conglomerate, scored with uplifting strings.",
        "rationale": (
            "Underdog-comeback mini-drama from a text brief + uplifting strings score. "
            "StoryAgent drafts the live-in son-in-law / hidden-heir blueprint. ScreenplayAgent "
            "breaks it into underdog-comeback scenes. KeyFrameAgent plans keyframes for the "
            "in-laws / conglomerate settings from text alone. VideoAgent assembles the "
            "multi-shot film. MusicAgent composes the uplifting strings score. AudioMixAgent "
            "layers it under the dialogue+foley. CompositorAgent muxes the final mp4. "
            "Reject AmbienceAgent, Transcription/Translation, VideoAnalysis/IntakeVideo/"
            "StyleTransfer/VideoExtend/Highlight (no source clip), Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the underdog-comeback story blueprint — live-in son-in-law eviction and hidden-heir reveal arc.",
            "Decompose the comeback arc into scenes with underdog-rise pacing.",
            "Plan keyframes for the rich-in-laws / conglomerate settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving underdog-comeback visual continuity through the eviction-to-reveal cuts.",
            "Compose the uplifting strings score the user requested, matching the comeback heroic register.",
            "Layer the strings score under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final underdog-comeback mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a time-travel romance mini-drama where a contemporary archaeologist falls into the Tang dynasty and falls for a banished prince, with lush orchestral period-style music.",
        "rationale": (
            "Time-travel romance mini-drama from a text brief + lush orchestral period-style "
            "music. StoryAgent drafts the modern-archaeologist / Tang-dynasty time-slip "
            "blueprint. ScreenplayAgent breaks it into time-travel romance scenes. "
            "KeyFrameAgent plans keyframes for modern dig-site / Tang palace settings from "
            "text alone. VideoAgent assembles the multi-shot film. MusicAgent composes the "
            "period-orchestral score. AudioMixAgent layers it under the dialogue+foley. "
            "CompositorAgent muxes the final mp4. Reject AmbienceAgent, Transcription/"
            "Translation, VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight, "
            "Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the time-travel romance story blueprint — archaeologist time-slip into Tang and banished-prince arc.",
            "Decompose the time-travel arc into scenes with romance and period-court pacing.",
            "Plan keyframes for the modern-dig-site and Tang-palace settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving the modern-to-Tang aesthetic transition.",
            "Compose the lush orchestral period-style music the user requested, matching the time-travel romance register.",
            "Layer the period-orchestral score under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final time-travel romance mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a vampire-romance vertical short about a graveyard-shift nurse who falls for a centuries-old vampire seeking redemption, with dark gothic strings.",
        "rationale": (
            "Vampire-romance vertical short from a text brief + dark gothic strings score. "
            "StoryAgent drafts the graveyard-shift-nurse / vampire-redemption blueprint. "
            "ScreenplayAgent breaks it into vertical-format romance scenes. KeyFrameAgent "
            "plans portrait-aspect keyframes for hospital / gothic settings from text alone. "
            "VideoAgent assembles the vertical multi-shot film. MusicAgent composes the gothic "
            "strings score. AudioMixAgent layers it under the dialogue+foley. CompositorAgent "
            "muxes the final mp4. Reject AmbienceAgent, Transcription/Translation, "
            "VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight, "
            "Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the vampire-romance story blueprint — graveyard-shift-nurse and centuries-old-vampire redemption arc.",
            "Decompose the vampire-romance arc into vertical-format scenes with gothic tone.",
            "Plan portrait-aspect keyframes for the hospital and gothic settings; text-only generation, no reference images supplied.",
            "Render per-shot vertical clips preserving the gothic-romance aesthetic.",
            "Compose the dark gothic strings the user requested, matching the vampire-romance register.",
            "Layer the gothic strings score under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final vampire-romance vertical short with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a wuxia mini-drama about an orphan swordsman avenging his master at the hands of a corrupt sect leader, with traditional erhu-and-drum scoring.",
        "rationale": (
            "Wuxia mini-drama from a text brief + traditional erhu-and-drum scoring. "
            "StoryAgent drafts the orphan-swordsman / master-revenge blueprint. ScreenplayAgent "
            "breaks it into wuxia scenes with duel pacing. KeyFrameAgent plans keyframes for "
            "wuxia settings from text alone. VideoAgent assembles the multi-shot film. "
            "MusicAgent composes the erhu-and-drum traditional score. AudioMixAgent layers it "
            "under the dialogue+foley. CompositorAgent muxes the final mp4. Reject "
            "AmbienceAgent, Transcription/Translation, VideoAnalysis/IntakeVideo/StyleTransfer/"
            "VideoExtend/Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the wuxia story blueprint — orphan-swordsman master-revenge arc with sect-leader confrontation.",
            "Decompose the revenge arc into wuxia scenes with traditional pacing.",
            "Plan keyframes for the wuxia settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving wuxia visual continuity across the duel cuts.",
            "Compose the traditional erhu-and-drum scoring the user requested, matching the wuxia register.",
            "Layer the traditional score under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final wuxia mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a mecha-military mini-drama where a rookie pilot's debut mission turns into a desperate solo defense after her squadron is wiped out, with brassy military fanfare.",
        "rationale": (
            "Mecha-military mini-drama from a text brief + brassy military fanfare. "
            "StoryAgent drafts the rookie-pilot / squadron-loss blueprint. ScreenplayAgent "
            "breaks it into mecha-combat scenes. KeyFrameAgent plans keyframes for cockpit / "
            "battlefield settings from text alone. VideoAgent assembles the multi-shot film. "
            "MusicAgent composes the brass fanfare score. AudioMixAgent layers it under the "
            "dialogue+foley. CompositorAgent muxes the final mp4. Reject AmbienceAgent, "
            "Transcription/Translation, VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/"
            "Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the mecha-military story blueprint — rookie-pilot debut and solo-defense arc after squadron loss.",
            "Decompose the solo-defense arc into mecha-combat scenes with escalating tension.",
            "Plan keyframes for the cockpit and battlefield settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving mecha-military visual continuity across the combat cuts.",
            "Compose the brassy military fanfare the user requested, matching the mecha-defense register.",
            "Layer the fanfare under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final mecha-military mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make an idol-fan mini-drama where an ordinary college student wins a contest dinner with her favorite K-pop idol and a real connection forms, with bright J-pop synth.",
        "rationale": (
            "Idol-fan mini-drama from a text brief + bright J-pop synth BGM. StoryAgent drafts "
            "the contest-dinner / idol-fan-bond blueprint. ScreenplayAgent breaks it into "
            "idol-fan scenes. KeyFrameAgent plans keyframes for fan-dorm / restaurant / "
            "green-room settings from text alone. VideoAgent assembles the multi-shot film. "
            "MusicAgent composes the J-pop synth score. AudioMixAgent layers it under the "
            "dialogue+foley. CompositorAgent muxes the final mp4. Reject AmbienceAgent, "
            "Transcription/Translation, VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/"
            "Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the idol-fan story blueprint — contest-winning college student and K-pop idol connection arc.",
            "Decompose the contest-dinner arc into idol-fan scenes with K-pop emotional register.",
            "Plan keyframes for the fan-dorm / restaurant / green-room settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving the idol-fan aesthetic across cuts.",
            "Compose the bright J-pop synth the user requested, matching the idol-fan register.",
            "Layer the J-pop synth under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final idol-fan mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a noir-detective mini-drama set in 1990s Shanghai about an aging inspector taking one last cold case — the dancer murder that made his career — with a smoky jazz score.",
        "rationale": (
            "1990s-Shanghai noir-detective mini-drama from a text brief + smoky jazz score. "
            "StoryAgent drafts the aging-inspector / cold-case blueprint. ScreenplayAgent "
            "breaks it into noir scenes. KeyFrameAgent plans period-Shanghai keyframes for "
            "precinct / dance-hall / alley settings from text alone. VideoAgent assembles "
            "the multi-shot film. MusicAgent composes the smoky jazz score. AudioMixAgent "
            "layers it under the dialogue+foley. CompositorAgent muxes the final mp4. Reject "
            "AmbienceAgent, Transcription/Translation, VideoAnalysis/IntakeVideo/StyleTransfer/"
            "VideoExtend/Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the noir-detective story blueprint — aging-inspector cold-case arc with the dancer-murder thread.",
            "Decompose the cold-case arc into 1990s-Shanghai noir scenes.",
            "Plan period-Shanghai keyframes for the precinct / dance-hall / alley settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving the 1990s-Shanghai noir aesthetic.",
            "Compose the smoky jazz score the user requested, matching the noir-detective register.",
            "Layer the jazz score under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final noir-detective mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a horror mini-drama about a young family that moves into a discounted countryside mansion only to discover the previous owner's ghost still keeps house, with dissonant string horror cues.",
        "rationale": (
            "Horror mini-drama from a text brief + dissonant string horror cues. StoryAgent "
            "drafts the family-haunted-mansion blueprint. ScreenplayAgent breaks it into "
            "horror scenes. KeyFrameAgent plans keyframes for the countryside-mansion settings "
            "from text alone. VideoAgent assembles the multi-shot film. MusicAgent composes "
            "the dissonant string cues. AudioMixAgent layers them under the dialogue+foley. "
            "CompositorAgent muxes the final mp4. Reject AmbienceAgent (the user labelled "
            "their ask as horror cues / score, not environmental ambient bed), Transcription/"
            "Translation, VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight, "
            "Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the horror story blueprint — young family in haunted countryside mansion and ghost-revelation arc.",
            "Decompose the haunted-mansion arc into horror scenes with escalating dread.",
            "Plan keyframes for the countryside-mansion settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving horror visual continuity across the haunting cuts.",
            "Compose the dissonant string horror cues the user requested, matching the haunted-mansion register.",
            "Layer the horror cues under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final horror mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a sci-fi dystopia mini-drama where a junior data analyst discovers her city's mood-monitoring grid is fabricating dissident profiles and goes off-grid, with cold electronic synthwave.",
        "rationale": (
            "Sci-fi dystopia mini-drama from a text brief + cold electronic synthwave. "
            "StoryAgent drafts the analyst / mood-monitoring-grid / off-grid blueprint. "
            "ScreenplayAgent breaks it into sci-fi dystopia scenes. KeyFrameAgent plans "
            "keyframes for the corporate / underground settings from text alone. VideoAgent "
            "assembles the multi-shot film. MusicAgent composes the synthwave score. "
            "AudioMixAgent layers it under the dialogue+foley. CompositorAgent muxes the "
            "final mp4. Reject AmbienceAgent, Transcription/Translation, VideoAnalysis/"
            "IntakeVideo/StyleTransfer/VideoExtend/Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the sci-fi dystopia story blueprint — junior-analyst grid-discovery and off-grid arc.",
            "Decompose the off-grid arc into sci-fi dystopia scenes.",
            "Plan keyframes for the corporate-analytics and underground settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving sci-fi dystopia visual continuity.",
            "Compose the cold electronic synthwave the user requested, matching the dystopia register.",
            "Layer the synthwave score under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final sci-fi dystopia mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a family-secret mini-drama where two estranged adult sisters discover at their mother's funeral that they have a long-lost twin sister raised abroad, with melancholy piano-and-cello.",
        "rationale": (
            "Family-secret mini-drama from a text brief + melancholy piano-and-cello score. "
            "StoryAgent drafts the estranged-sisters / long-lost-twin / funeral blueprint. "
            "ScreenplayAgent breaks it into family-secret scenes. KeyFrameAgent plans "
            "keyframes for the funeral / family-home / arrival settings from text alone. "
            "VideoAgent assembles the multi-shot film. MusicAgent composes the piano-and-cello "
            "score. AudioMixAgent layers it under the dialogue+foley. CompositorAgent muxes "
            "the final mp4. Reject AmbienceAgent, Transcription/Translation, VideoAnalysis/"
            "IntakeVideo/StyleTransfer/VideoExtend/Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the family-secret story blueprint — estranged-sisters funeral discovery and long-lost-twin arc.",
            "Decompose the family-secret arc into scenes with quiet emotional register.",
            "Plan keyframes for the funeral / family-home / arrival settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving family-drama visual continuity across the reunion cuts.",
            "Compose the melancholy piano-and-cello the user requested, matching the family-secret register.",
            "Layer the piano-and-cello score under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final family-secret mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a sports-comeback mini-drama about a 38-year-old retired heavyweight boxer convinced by his estranged son to mount a comeback for one last belt, with anthemic brass-and-drums.",
        "rationale": (
            "Sports-comeback mini-drama from a text brief + anthemic brass-and-drums score. "
            "StoryAgent drafts the retired-boxer / son-estrangement / comeback blueprint. "
            "ScreenplayAgent breaks it into sports-comeback scenes with title-fight pacing. "
            "KeyFrameAgent plans keyframes for the gym / training / ring settings from text "
            "alone. VideoAgent assembles the multi-shot film. MusicAgent composes the "
            "brass-and-drums anthem. AudioMixAgent layers it under the dialogue+foley. "
            "CompositorAgent muxes the final mp4. Reject AmbienceAgent, Transcription/"
            "Translation, VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight, "
            "Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the sports-comeback story blueprint — retired-boxer comeback arc with the estranged-son thread.",
            "Decompose the comeback arc into training-and-fight scenes with anthemic pacing.",
            "Plan keyframes for the gym / training / ring settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving sports-comeback visual continuity across the training-to-title cuts.",
            "Compose the anthemic brass-and-drums the user requested, matching the comeback register.",
            "Layer the brass-and-drums anthem under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final sports-comeback mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a prodigy mini-drama about a 12-year-old violinist whose stage-mother pressure leads her to sabotage her own competition until a kind judge sees through it, with classical solo violin.",
        "rationale": (
            "Prodigy mini-drama from a text brief + classical solo violin score. StoryAgent "
            "drafts the 12-year-violinist / stage-mother / competition-sabotage blueprint. "
            "ScreenplayAgent breaks it into prodigy-drama scenes. KeyFrameAgent plans keyframes "
            "for the dressing-room / stage / judge-office settings from text alone. VideoAgent "
            "assembles the multi-shot film. MusicAgent composes the solo violin score. "
            "AudioMixAgent layers it under the dialogue+foley. CompositorAgent muxes the "
            "final mp4. Reject AmbienceAgent, Transcription/Translation, VideoAnalysis/"
            "IntakeVideo/StyleTransfer/VideoExtend/Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the prodigy story blueprint — 12-year-violinist stage-mother-pressure and competition-sabotage arc.",
            "Decompose the prodigy arc into competition-drama scenes.",
            "Plan keyframes for the dressing-room / stage / judge-office settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving prodigy-drama visual continuity across the competition cuts.",
            "Compose the classical solo violin the user requested, matching the prodigy register.",
            "Layer the solo violin score under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final prodigy mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a pirate-adventure mini-drama about an orphan stowaway on a privateer's brig who turns out to know the location of the lost treasure the captain has hunted his whole career, with swashbuckling orchestral.",
        "rationale": (
            "Pirate-adventure mini-drama from a text brief + swashbuckling orchestral score. "
            "StoryAgent drafts the orphan-stowaway / privateer / lost-treasure blueprint. "
            "ScreenplayAgent breaks it into pirate-adventure scenes. KeyFrameAgent plans "
            "keyframes for the cargo-hold / cabin / lagoon settings from text alone. "
            "VideoAgent assembles the multi-shot film. MusicAgent composes the swashbuckling "
            "orchestral score. AudioMixAgent layers it under the dialogue+foley. "
            "CompositorAgent muxes the final mp4. Reject AmbienceAgent, Transcription/"
            "Translation, VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight, "
            "Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the pirate-adventure story blueprint — orphan-stowaway treasure-secret arc on the privateer's brig.",
            "Decompose the adventure arc into pirate-adventure scenes with high-seas pacing.",
            "Plan keyframes for the cargo-hold / cabin / lagoon settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving pirate-adventure visual continuity across the high-seas cuts.",
            "Compose the swashbuckling orchestral the user requested, matching the pirate-adventure register.",
            "Layer the orchestral score under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final pirate-adventure mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a spy-thriller vertical short about a deep-cover agent extracted minutes before discovery and forced to choose between mission and the cover-family she has come to love, with propulsive electronic.",
        "rationale": (
            "Spy-thriller vertical short from a text brief + propulsive electronic score. "
            "StoryAgent drafts the deep-cover-agent / extraction / cover-family blueprint. "
            "ScreenplayAgent breaks it into vertical-format spy-thriller scenes. KeyFrameAgent "
            "plans portrait-aspect keyframes for the family / exfil settings from text alone. "
            "VideoAgent assembles the vertical multi-shot film. MusicAgent composes the "
            "propulsive electronic score. AudioMixAgent layers it under the dialogue+foley. "
            "CompositorAgent muxes the final mp4. Reject AmbienceAgent, Transcription/"
            "Translation, VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight, "
            "Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the spy-thriller story blueprint — deep-cover-agent extraction dilemma and cover-family arc.",
            "Decompose the extraction-dilemma arc into vertical-format spy-thriller scenes.",
            "Plan portrait-aspect keyframes for the family / exfil settings; text-only generation, no reference images supplied.",
            "Render per-shot vertical clips preserving the spy-thriller aesthetic.",
            "Compose the propulsive electronic the user requested, matching the spy-thriller register.",
            "Layer the electronic score under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final spy-thriller vertical short with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a Tang-dynasty palace mini-drama about a junior consort who survives an assassination attempt and quietly rebuilds her standing through court intrigue, with silk-and-bamboo period scoring.",
        "rationale": (
            "Tang-dynasty palace mini-drama from a text brief + silk-and-bamboo period scoring. "
            "StoryAgent drafts the junior-consort / assassination-attempt / court-intrigue "
            "blueprint. ScreenplayAgent breaks it into Tang-palace scenes. KeyFrameAgent plans "
            "keyframes for the period palace settings from text alone. VideoAgent assembles "
            "the multi-shot film. MusicAgent composes the silk-and-bamboo period score. "
            "AudioMixAgent layers it under the dialogue+foley. CompositorAgent muxes the "
            "final mp4. Reject AmbienceAgent, Transcription/Translation, VideoAnalysis/"
            "IntakeVideo/StyleTransfer/VideoExtend/Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the Tang-palace story blueprint — junior-consort assassination-survival and court-intrigue arc.",
            "Decompose the court-intrigue arc into period-palace scenes.",
            "Plan keyframes for the Tang-palace settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving the Tang-period aesthetic.",
            "Compose the silk-and-bamboo period scoring the user requested, matching the Tang-court register.",
            "Layer the period score under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final Tang-palace mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a heist-comedy mini-drama where a mismatched team of small-time grifters tries to rob a casino vault that turns out to belong to one of their own estranged fathers, with jaunty jazz BGM.",
        "rationale": (
            "Heist-comedy mini-drama from a text brief + jaunty jazz BGM. StoryAgent drafts "
            "the mismatched-grifters / casino-vault / father-twist blueprint. ScreenplayAgent "
            "breaks it into heist-comedy scenes. KeyFrameAgent plans keyframes for the diner / "
            "rehearsal / vault settings from text alone. VideoAgent assembles the multi-shot "
            "film. MusicAgent composes the jaunty jazz score. AudioMixAgent layers it under "
            "the dialogue+foley. CompositorAgent muxes the final mp4. Reject AmbienceAgent, "
            "Transcription/Translation, VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/"
            "Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the heist-comedy story blueprint — mismatched-grifters casino-vault job and father-twist arc.",
            "Decompose the heist arc into comedy-paced scenes.",
            "Plan keyframes for the diner / rehearsal / vault settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving heist-comedy visual continuity.",
            "Compose the jaunty jazz BGM the user requested, matching the heist-comedy register.",
            "Layer the jazz score under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final heist-comedy mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a post-apocalyptic mini-drama where two strangers cross a radioactive wasteland to deliver a sealed package whose contents could end the war or restart it, with droning ambient-electronic BGM.",
        "rationale": (
            "Post-apocalyptic mini-drama from a text brief + droning ambient-electronic BGM. "
            "Note: the user labels this audio layer as BGM (music-style ambient electronica), "
            "not an environmental ambience bed — so MusicAgent handles it. StoryAgent drafts "
            "the strangers / wasteland / sealed-package blueprint. ScreenplayAgent breaks it "
            "into post-apocalyptic scenes. KeyFrameAgent plans keyframes for the wasteland / "
            "depot / gate settings from text alone. VideoAgent assembles the multi-shot film. "
            "MusicAgent composes the ambient-electronic BGM. AudioMixAgent layers it under the "
            "dialogue+foley. CompositorAgent muxes the final mp4. Reject AmbienceAgent (user's "
            "phrase is BGM-classified, not environmental sound bed), Transcription/Translation, "
            "VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight, "
            "Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the post-apocalyptic story blueprint — wasteland-courier sealed-package crossing arc.",
            "Decompose the crossing arc into post-apocalyptic scenes with sparse pacing.",
            "Plan keyframes for the wasteland / depot / gate settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving post-apocalyptic visual continuity.",
            "Compose the droning ambient-electronic BGM the user requested, matching the wasteland register.",
            "Layer the ambient-electronic score under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final post-apocalyptic mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a magic-school animated drama about a student cursed to lose her memory each midnight finding a classmate willing to remind her every morning who she is, with whimsical fairy strings.",
        "rationale": (
            "Magic-school animated drama from a text brief + whimsical fairy strings score. "
            "StoryAgent drafts the cursed-memory / classmate-reminder blueprint. "
            "ScreenplayAgent breaks it into magic-school animated scenes. KeyFrameAgent plans "
            "animation-style keyframes for the magic-school settings from text alone. "
            "VideoAgent assembles the animated multi-shot film. MusicAgent composes the fairy "
            "strings score. AudioMixAgent layers it under the dialogue+foley. CompositorAgent "
            "muxes the final mp4. Reject AmbienceAgent, Transcription/Translation, "
            "VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight, "
            "Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the magic-school story blueprint — cursed-memory student and classmate-reminder arc.",
            "Decompose the cursed-memory arc into magic-school animated scenes.",
            "Plan animation-style keyframes for the magic-school settings; text-only generation, no reference images supplied.",
            "Render per-shot animated clips preserving the magic-school aesthetic.",
            "Compose the whimsical fairy strings the user requested, matching the magic-school register.",
            "Layer the fairy strings score under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final magic-school animated drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a yakuza-redemption mini-drama where an aging enforcer takes one last assignment — escorting a witness to court — and chooses to protect her over his oath, with melancholy shamisen.",
        "rationale": (
            "Yakuza-redemption mini-drama from a text brief + melancholy shamisen score. "
            "StoryAgent drafts the aging-enforcer / witness-escort / oath-breaking blueprint. "
            "ScreenplayAgent breaks it into yakuza-drama scenes. KeyFrameAgent plans keyframes "
            "for the tatami-room / safe-house / alley settings from text alone. VideoAgent "
            "assembles the multi-shot film. MusicAgent composes the shamisen score. "
            "AudioMixAgent layers it under the dialogue+foley. CompositorAgent muxes the "
            "final mp4. Reject AmbienceAgent, Transcription/Translation, VideoAnalysis/"
            "IntakeVideo/StyleTransfer/VideoExtend/Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the yakuza-redemption story blueprint — aging-enforcer witness-escort and oath-breaking arc.",
            "Decompose the redemption arc into yakuza-drama scenes.",
            "Plan keyframes for the tatami-room / safe-house / alley settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving yakuza-drama visual continuity.",
            "Compose the melancholy shamisen the user requested, matching the yakuza-redemption register.",
            "Layer the shamisen score under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final yakuza-redemption mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make an office-comedy mini-drama where a temp intern accidentally sends the CEO her diary instead of the quarterly report and her week of dread becomes an unexpected promotion, with quirky pizzicato BGM.",
        "rationale": (
            "Office-comedy mini-drama from a text brief + quirky pizzicato BGM. StoryAgent "
            "drafts the temp-intern / diary-misfire / promotion blueprint. ScreenplayAgent "
            "breaks it into office-comedy scenes. KeyFrameAgent plans keyframes for the "
            "intern-desk / hallway / corner-office settings from text alone. VideoAgent "
            "assembles the multi-shot film. MusicAgent composes the pizzicato score. "
            "AudioMixAgent layers it under the dialogue+foley. CompositorAgent muxes the "
            "final mp4. Reject AmbienceAgent, Transcription/Translation, VideoAnalysis/"
            "IntakeVideo/StyleTransfer/VideoExtend/Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the office-comedy story blueprint — temp-intern diary-misfire and unexpected-promotion arc.",
            "Decompose the diary-misfire arc into office-comedy scenes with comedic pacing.",
            "Plan keyframes for the intern-desk / hallway / corner-office settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving office-comedy visual continuity.",
            "Compose the quirky pizzicato BGM the user requested, matching the office-comedy register.",
            "Layer the pizzicato score under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final office-comedy mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a reverse-isekai mini-drama where the demon-king of a fantasy kingdom is sent to modern Tokyo as part of a magical exchange and ends up working a part-time job at a convenience store, with comedic synth.",
        "rationale": (
            "Reverse-isekai mini-drama from a text brief + comedic synth BGM. StoryAgent "
            "drafts the demon-king / Tokyo-exchange / convenience-store blueprint. "
            "ScreenplayAgent breaks it into reverse-isekai comedy scenes. KeyFrameAgent plans "
            "keyframes for the apartment / convenience-store settings from text alone. "
            "VideoAgent assembles the multi-shot film. MusicAgent composes the comedic synth "
            "score. AudioMixAgent layers it under the dialogue+foley. CompositorAgent muxes "
            "the final mp4. Reject AmbienceAgent, Transcription/Translation, VideoAnalysis/"
            "IntakeVideo/StyleTransfer/VideoExtend/Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the reverse-isekai story blueprint — demon-king Tokyo-exchange and convenience-store arc.",
            "Decompose the reverse-isekai arc into modern-Tokyo comedy scenes.",
            "Plan keyframes for the apartment / convenience-store settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving reverse-isekai visual continuity.",
            "Compose the comedic synth the user requested, matching the reverse-isekai register.",
            "Layer the comedic synth under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final reverse-isekai mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a cyberpunk mini-drama about a neon-noir hacker hired to wipe a corporate executive's daughter from the surveillance grid before her birthday party gets her killed, with dark synthwave.",
        "rationale": (
            "Cyberpunk neon-noir mini-drama from a text brief + dark synthwave score. "
            "StoryAgent drafts the hacker / executive's-daughter / surveillance-wipe blueprint. "
            "ScreenplayAgent breaks it into cyberpunk scenes. KeyFrameAgent plans keyframes "
            "for the neon-alley / server-farm / rooftop settings from text alone. VideoAgent "
            "assembles the multi-shot film. MusicAgent composes the dark synthwave score. "
            "AudioMixAgent layers it under the dialogue+foley. CompositorAgent muxes the "
            "final mp4. Reject AmbienceAgent, Transcription/Translation, VideoAnalysis/"
            "IntakeVideo/StyleTransfer/VideoExtend/Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the cyberpunk story blueprint — neon-noir-hacker daughter-wipe surveillance arc.",
            "Decompose the wipe arc into cyberpunk scenes.",
            "Plan keyframes for the neon-alley / server-farm / rooftop settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving cyberpunk visual continuity.",
            "Compose the dark synthwave the user requested, matching the cyberpunk register.",
            "Layer the synthwave score under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final cyberpunk mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a cooking-rivalry mini-drama where two former co-cooks who haven't spoken in years end up competing for the lead spot at a restaurant they once dreamed of opening together, with dramatic culinary brass-and-strings.",
        "rationale": (
            "Cooking-rivalry mini-drama from a text brief + dramatic culinary brass-and-strings. "
            "StoryAgent drafts the former-co-cooks / restaurant-competition blueprint. "
            "ScreenplayAgent breaks it into cooking-rivalry scenes. KeyFrameAgent plans "
            "keyframes for the announcement / prep-stations / plating settings from text "
            "alone. VideoAgent assembles the multi-shot film. MusicAgent composes the "
            "brass-and-strings score. AudioMixAgent layers it under the dialogue+foley. "
            "CompositorAgent muxes the final mp4. Reject AmbienceAgent, Transcription/"
            "Translation, VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight, "
            "Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the cooking-rivalry story blueprint — former-co-cooks restaurant-competition arc.",
            "Decompose the rivalry arc into cooking-rivalry scenes with prestige pacing.",
            "Plan keyframes for the announcement / prep-stations / plating settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving cooking-rivalry visual continuity across the prep-and-plating cuts.",
            "Compose the dramatic culinary brass-and-strings the user requested, matching the cooking-rivalry register.",
            "Layer the brass-and-strings score under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final cooking-rivalry mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a K-pop trainee mini-drama about a fifteenth-year trainee finally given a debut slot only to learn she'll replace her best friend, with bright dance-pop BGM.",
        "rationale": (
            "K-pop trainee mini-drama from a text brief + bright dance-pop BGM. StoryAgent "
            "drafts the long-term-trainee / debut-replacement blueprint. ScreenplayAgent "
            "breaks it into K-pop trainee scenes. KeyFrameAgent plans keyframes for the "
            "agency-hallway / practice-room / debut-stage settings from text alone. "
            "VideoAgent assembles the multi-shot film. MusicAgent composes the dance-pop "
            "score. AudioMixAgent layers it under the dialogue+foley. CompositorAgent muxes "
            "the final mp4. Reject AmbienceAgent, Transcription/Translation, VideoAnalysis/"
            "IntakeVideo/StyleTransfer/VideoExtend/Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the K-pop trainee story blueprint — fifteenth-year-trainee debut-replacement arc.",
            "Decompose the trainee arc into K-pop debut scenes.",
            "Plan keyframes for the agency-hallway / practice-room / debut-stage settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving K-pop trainee visual continuity.",
            "Compose the bright dance-pop BGM the user requested, matching the K-pop register.",
            "Layer the dance-pop score under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final K-pop trainee mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a pet-and-owner mini-drama about a teen and her terminally ill dog crossing the country to a rumored healer the dog seems to have known, with tender folk-acoustic.",
        "rationale": (
            "Pet-and-owner mini-drama from a text brief + tender folk-acoustic score. "
            "StoryAgent drafts the teen / terminally-ill-dog / cross-country-healer blueprint. "
            "ScreenplayAgent breaks it into pet-bond scenes. KeyFrameAgent plans keyframes for "
            "the vet-office / road-trip / healer-cottage settings from text alone. VideoAgent "
            "assembles the multi-shot film. MusicAgent composes the folk-acoustic score. "
            "AudioMixAgent layers it under the dialogue+foley. CompositorAgent muxes the "
            "final mp4. Reject AmbienceAgent, Transcription/Translation, VideoAnalysis/"
            "IntakeVideo/StyleTransfer/VideoExtend/Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the pet-and-owner story blueprint — teen and terminally-ill dog cross-country-healer arc.",
            "Decompose the pet-bond arc into road-trip scenes with quiet emotional register.",
            "Plan keyframes for the vet-office / road-trip / healer-cottage settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving pet-bond visual continuity across the road-trip cuts.",
            "Compose the tender folk-acoustic the user requested, matching the pet-bond register.",
            "Layer the folk-acoustic score under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final pet-and-owner mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make an angel-mortal romance mini-drama where a fallen angel takes a job at a bookstore and meets the human she once visited as a guardian decades ago, with ethereal choral BGM.",
        "rationale": (
            "Angel-mortal romance mini-drama from a text brief + ethereal choral BGM. "
            "StoryAgent drafts the fallen-angel / bookstore / guardian-recognition blueprint. "
            "ScreenplayAgent breaks it into angel-mortal romance scenes. KeyFrameAgent plans "
            "keyframes for the bookstore / coffee-shop / rooftop settings from text alone. "
            "VideoAgent assembles the multi-shot film. MusicAgent composes the choral score. "
            "AudioMixAgent layers it under the dialogue+foley. CompositorAgent muxes the "
            "final mp4. Reject AmbienceAgent, Transcription/Translation, VideoAnalysis/"
            "IntakeVideo/StyleTransfer/VideoExtend/Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the angel-mortal romance story blueprint — fallen-angel bookstore-job and guardian-recognition arc.",
            "Decompose the angel-mortal arc into ethereal romance scenes.",
            "Plan keyframes for the bookstore / coffee-shop / rooftop settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving angel-mortal romance visual continuity.",
            "Compose the ethereal choral BGM the user requested, matching the angel-mortal register.",
            "Layer the choral score under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final angel-mortal romance mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a boxing-underdog mini-drama where an unlicensed street fighter is offered a sanctioned bout but only if he reveals the prison-yard secret he made trading freedom for his sister, with gritty hip-hop urban BGM.",
        "rationale": (
            "Boxing-underdog mini-drama from a text brief + gritty hip-hop urban BGM. "
            "StoryAgent drafts the unlicensed-fighter / prison-yard-secret / sanctioned-bout "
            "blueprint. ScreenplayAgent breaks it into boxing-underdog scenes. KeyFrameAgent "
            "plans keyframes for the back-alley / sister's-apartment / ring settings from "
            "text alone. VideoAgent assembles the multi-shot film. MusicAgent composes the "
            "hip-hop urban score. AudioMixAgent layers it under the dialogue+foley. "
            "CompositorAgent muxes the final mp4. Reject AmbienceAgent, Transcription/"
            "Translation, VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight, "
            "Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the boxing-underdog story blueprint — unlicensed-fighter prison-yard-secret and sanctioned-bout arc.",
            "Decompose the underdog arc into boxing-drama scenes with urban-grit pacing.",
            "Plan keyframes for the back-alley / sister's-apartment / ring settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving boxing-underdog visual continuity.",
            "Compose the gritty hip-hop urban BGM the user requested, matching the boxing-underdog register.",
            "Layer the hip-hop urban score under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final boxing-underdog mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a royal-imposter period mini-drama where a kitchen girl must masquerade as a visiting princess after the real one's sudden illness threatens a fragile alliance, with baroque period BGM.",
        "rationale": (
            "Royal-imposter period mini-drama from a text brief + baroque period BGM. "
            "StoryAgent drafts the kitchen-girl / princess-masquerade / alliance blueprint. "
            "ScreenplayAgent breaks it into period-drama scenes. KeyFrameAgent plans keyframes "
            "for the sickroom / tutoring / banquet settings from text alone. VideoAgent "
            "assembles the multi-shot film. MusicAgent composes the baroque period score. "
            "AudioMixAgent layers it under the dialogue+foley. CompositorAgent muxes the "
            "final mp4. Reject AmbienceAgent, Transcription/Translation, VideoAnalysis/"
            "IntakeVideo/StyleTransfer/VideoExtend/Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the royal-imposter story blueprint — kitchen-girl princess-masquerade and fragile-alliance arc.",
            "Decompose the imposter arc into period-drama scenes.",
            "Plan keyframes for the sickroom / tutoring / banquet settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving period-drama visual continuity.",
            "Compose the baroque period BGM the user requested, matching the royal-imposter register.",
            "Layer the baroque score under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final royal-imposter mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a train-thriller mini-drama where a passenger on an overnight sleeper realizes mid-journey that her cabin-mate is plotting an assassination at the next major station, with tense ostinato BGM.",
        "rationale": (
            "Train-thriller mini-drama from a text brief + tense ostinato BGM. StoryAgent "
            "drafts the sleeper-passenger / cabin-mate-plot / station-confrontation blueprint. "
            "ScreenplayAgent breaks it into train-thriller scenes. KeyFrameAgent plans keyframes "
            "for the bunk / dining-car / platform settings from text alone. VideoAgent "
            "assembles the multi-shot film. MusicAgent composes the tense ostinato score. "
            "AudioMixAgent layers it under the dialogue+foley. CompositorAgent muxes the "
            "final mp4. Reject AmbienceAgent, Transcription/Translation, VideoAnalysis/"
            "IntakeVideo/StyleTransfer/VideoExtend/Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the train-thriller story blueprint — sleeper-passenger plot-discovery and station-confrontation arc.",
            "Decompose the thriller arc into train-set scenes with escalating tension.",
            "Plan keyframes for the bunk / dining-car / platform settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving train-thriller visual continuity.",
            "Compose the tense ostinato BGM the user requested, matching the train-thriller register.",
            "Layer the ostinato score under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final train-thriller mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a forbidden-love period mini-drama where a noblewoman's arranged marriage is interrupted by the return of the soldier she once loved who was presumed dead at war, with sweeping romantic strings.",
        "rationale": (
            "Forbidden-love period mini-drama from a text brief + sweeping romantic strings. "
            "StoryAgent drafts the noblewoman / returned-soldier / arranged-marriage blueprint. "
            "ScreenplayAgent breaks it into period-romance scenes. KeyFrameAgent plans keyframes "
            "for the wedding-chamber / courtyard / balcony settings from text alone. VideoAgent "
            "assembles the multi-shot film. MusicAgent composes the romantic-strings score. "
            "AudioMixAgent layers it under the dialogue+foley. CompositorAgent muxes the "
            "final mp4. Reject AmbienceAgent, Transcription/Translation, VideoAnalysis/"
            "IntakeVideo/StyleTransfer/VideoExtend/Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the forbidden-love story blueprint — noblewoman arranged-marriage and returned-soldier arc.",
            "Decompose the period-romance arc into wedding-day-and-balcony scenes.",
            "Plan keyframes for the wedding-chamber / courtyard / balcony settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving period-romance visual continuity.",
            "Compose the sweeping romantic strings the user requested, matching the forbidden-love register.",
            "Layer the romantic-strings score under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final forbidden-love mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a rags-to-riches mini-drama about a street-vendor selling roasted chestnuts who inherits a textile empire from a customer who was secretly her uncle, with soulful R&B underlay.",
        "rationale": (
            "Rags-to-riches mini-drama from a text brief + soulful R&B underlay. StoryAgent "
            "drafts the street-vendor / textile-empire / hidden-uncle blueprint. "
            "ScreenplayAgent breaks it into rags-to-riches scenes. KeyFrameAgent plans "
            "keyframes for the chestnut-stand / lawyer-office / boardroom settings from text "
            "alone. VideoAgent assembles the multi-shot film. MusicAgent composes the soulful "
            "R&B score. AudioMixAgent layers it under the dialogue+foley. CompositorAgent "
            "muxes the final mp4. Reject AmbienceAgent, Transcription/Translation, "
            "VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight, "
            "Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the rags-to-riches story blueprint — street-vendor inheritance and hidden-uncle arc.",
            "Decompose the inheritance arc into rags-to-riches scenes.",
            "Plan keyframes for the chestnut-stand / lawyer-office / boardroom settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving the rags-to-riches transformation aesthetic.",
            "Compose the soulful R&B underlay the user requested, matching the rags-to-riches register.",
            "Layer the R&B score under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final rags-to-riches mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a werewolf-pack mini-drama where the alpha's ailing successor must beat his exiled brother in single combat to keep the pack from splintering during the next full-moon hunt, with primal drum-and-percussion BGM.",
        "rationale": (
            "Werewolf-pack mini-drama from a text brief + primal drum-and-percussion BGM. "
            "StoryAgent drafts the successor / exiled-brother / full-moon-duel blueprint. "
            "ScreenplayAgent breaks it into werewolf-pack scenes. KeyFrameAgent plans keyframes "
            "for the pack-clearing / training / duel-ground settings from text alone. "
            "VideoAgent assembles the multi-shot film. MusicAgent composes the primal "
            "drum-and-percussion score. AudioMixAgent layers it under the dialogue+foley. "
            "CompositorAgent muxes the final mp4. Reject AmbienceAgent, Transcription/"
            "Translation, VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight, "
            "Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the werewolf-pack story blueprint — successor and exiled-brother full-moon-duel arc.",
            "Decompose the duel arc into werewolf-pack scenes.",
            "Plan keyframes for the pack-clearing / training / duel-ground settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving werewolf-pack visual continuity.",
            "Compose the primal drum-and-percussion BGM the user requested, matching the werewolf-duel register.",
            "Layer the drum-and-percussion score under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final werewolf-pack mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make an animated drama about a kingdom of forest animals overthrowing a corrupt fox dynasty after the youngest mouse-prince returns from exile with a hidden human ally, with cinematic full orchestral BGM.",
        "rationale": (
            "Animated forest-animal drama from a text brief + cinematic full orchestral BGM. "
            "StoryAgent drafts the mouse-prince / fox-dynasty / forest-revolution blueprint. "
            "ScreenplayAgent breaks it into animated-drama scenes. KeyFrameAgent plans "
            "animation-style keyframes for the warren / meadow / palace settings from text "
            "alone. VideoAgent assembles the animated multi-shot film. MusicAgent composes "
            "the full orchestral score. AudioMixAgent layers it under the dialogue+foley. "
            "CompositorAgent muxes the final mp4. Reject AmbienceAgent, Transcription/"
            "Translation, VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight, "
            "Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the animated forest-animal story blueprint — mouse-prince exile and fox-dynasty overthrow arc.",
            "Decompose the revolution arc into animated-drama scenes.",
            "Plan animation-style keyframes for the warren / meadow / palace settings; text-only generation, no reference images supplied.",
            "Render per-shot animated clips preserving the forest-animal aesthetic.",
            "Compose the cinematic full orchestral BGM the user requested, matching the revolution register.",
            "Layer the orchestral score under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final animated forest-animal drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make an indigenous-fable mini-drama about a young shaman's journey to wake an ancestral spirit dormant since her grandmother's exile from the village, with world-music flutes-and-percussion.",
        "rationale": (
            "Indigenous-fable mini-drama from a text brief + world-music flutes-and-percussion. "
            "StoryAgent drafts the young-shaman / ancestral-spirit / grandmother-exile blueprint. "
            "ScreenplayAgent breaks it into fable scenes. KeyFrameAgent plans keyframes for "
            "the village / sacred-grove / spirit-pool settings from text alone. VideoAgent "
            "assembles the multi-shot film. MusicAgent composes the world-music score. "
            "AudioMixAgent layers it under the dialogue+foley. CompositorAgent muxes the "
            "final mp4. Reject AmbienceAgent, Transcription/Translation, VideoAnalysis/"
            "IntakeVideo/StyleTransfer/VideoExtend/Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the indigenous-fable story blueprint — young-shaman ancestral-spirit-wake arc with grandmother-exile thread.",
            "Decompose the spirit-wake arc into fable scenes with reverent pacing.",
            "Plan keyframes for the village / sacred-grove / spirit-pool settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving the indigenous-fable visual register.",
            "Compose the world-music flutes-and-percussion the user requested, matching the fable register.",
            "Layer the world-music score under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final indigenous-fable mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a coming-of-age mini-drama about a high-school senior whose first real love arrives weeks before he leaves for college on a different continent, with indie pop BGM.",
        "rationale": (
            "Coming-of-age mini-drama from a text brief + indie pop BGM. StoryAgent drafts "
            "the high-school-senior / first-love / college-departure blueprint. ScreenplayAgent "
            "breaks it into coming-of-age scenes. KeyFrameAgent plans keyframes for the "
            "high-school / boardwalk-summer / airport settings from text alone. VideoAgent "
            "assembles the multi-shot film. MusicAgent composes the indie pop score. "
            "AudioMixAgent layers it under the dialogue+foley. CompositorAgent muxes the "
            "final mp4. Reject AmbienceAgent, Transcription/Translation, VideoAnalysis/"
            "IntakeVideo/StyleTransfer/VideoExtend/Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the coming-of-age story blueprint — high-school-senior first-love and college-departure arc.",
            "Decompose the coming-of-age arc into nostalgic summer scenes.",
            "Plan keyframes for the high-school / boardwalk-summer / airport settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving coming-of-age visual continuity.",
            "Compose the indie pop BGM the user requested, matching the coming-of-age register.",
            "Layer the indie pop score under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final coming-of-age mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a submarine-disaster mini-drama where a routine training dive becomes a sealed-compartment survival ordeal as oxygen runs out and the youngest crewman must make the calculation, with brass-and-sonar-electronic BGM.",
        "rationale": (
            "Submarine-disaster mini-drama from a text brief + brass-and-sonar-electronic BGM. "
            "StoryAgent drafts the training-dive / sealed-compartment / oxygen-crisis blueprint. "
            "ScreenplayAgent breaks it into submarine-disaster scenes. KeyFrameAgent plans "
            "keyframes for the bridge / chart-table / airlock settings from text alone. "
            "VideoAgent assembles the multi-shot film. MusicAgent composes the brass-and-sonar "
            "score. AudioMixAgent layers it under the dialogue+foley. CompositorAgent muxes "
            "the final mp4. Reject AmbienceAgent, Transcription/Translation, VideoAnalysis/"
            "IntakeVideo/StyleTransfer/VideoExtend/Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the submarine-disaster story blueprint — training-dive sealed-compartment survival arc.",
            "Decompose the survival arc into submarine-disaster scenes with claustrophobic tension.",
            "Plan keyframes for the bridge / chart-table / airlock settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving submarine-disaster visual continuity.",
            "Compose the brass-and-sonar-electronic BGM the user requested, matching the submarine-disaster register.",
            "Layer the brass-and-sonar score under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final submarine-disaster mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a mountain-climbing mini-drama about a solo climber's K2 ascent disrupted by a storm and her decision to attempt rescue of a stranded amateur with no oxygen left, with sweeping wind-and-strings BGM.",
        "rationale": (
            "Mountain-climbing mini-drama from a text brief + sweeping wind-and-strings BGM. "
            "StoryAgent drafts the solo-climber / K2-storm / rescue-decision blueprint. "
            "ScreenplayAgent breaks it into mountain-climbing scenes. KeyFrameAgent plans "
            "keyframes for the predawn-ridge / storm-shelter / oxygen-share settings from "
            "text alone. VideoAgent assembles the multi-shot film. MusicAgent composes the "
            "wind-and-strings score. AudioMixAgent layers it under the dialogue+foley. "
            "CompositorAgent muxes the final mp4. Reject AmbienceAgent, Transcription/"
            "Translation, VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight, "
            "Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the mountain-climbing story blueprint — solo K2 ascent and rescue-decision arc.",
            "Decompose the climbing arc into mountain-disaster scenes with sweeping pacing.",
            "Plan keyframes for the predawn-ridge / storm-shelter / oxygen-share settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving mountain-climbing visual continuity.",
            "Compose the sweeping wind-and-strings BGM the user requested, matching the mountain-climbing register.",
            "Layer the wind-and-strings score under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final mountain-climbing mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a WW2-resistance mini-drama where a French farm girl smuggles a downed Allied airman across occupied territory in a hay-cart, with French accordion-and-strings BGM.",
        "rationale": (
            "WW2-resistance mini-drama from a text brief + French accordion-and-strings BGM. "
            "StoryAgent drafts the French-farm-girl / Allied-airman / hay-cart-smuggling "
            "blueprint. ScreenplayAgent breaks it into WW2-resistance scenes. KeyFrameAgent "
            "plans keyframes for the barn-loft / village-checkpoint / wood-line settings from "
            "text alone. VideoAgent assembles the multi-shot film. MusicAgent composes the "
            "accordion-and-strings score. AudioMixAgent layers it under the dialogue+foley. "
            "CompositorAgent muxes the final mp4. Reject AmbienceAgent, Transcription/"
            "Translation, VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight, "
            "Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the WW2-resistance story blueprint — French-farm-girl Allied-airman hay-cart-smuggling arc.",
            "Decompose the smuggling arc into WW2-resistance scenes.",
            "Plan keyframes for the barn-loft / village-checkpoint / wood-line settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving WW2-resistance visual continuity.",
            "Compose the French accordion-and-strings BGM the user requested, matching the WW2-resistance register.",
            "Layer the accordion-and-strings score under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final WW2-resistance mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a Polynesian-myth animated drama about a young navigator's voyage to wake the sleeping ocean spirit who once guarded her ancestors before vanishing under colonial conquest, with tribal percussion-and-vocals.",
        "rationale": (
            "Polynesian-myth animated drama from a text brief + tribal percussion-and-vocals. "
            "StoryAgent drafts the young-navigator / ocean-spirit / colonial-vanishing "
            "blueprint. ScreenplayAgent breaks it into Polynesian-myth animated scenes. "
            "KeyFrameAgent plans animation-style keyframes for the beach / outrigger / "
            "spirit-pool settings from text alone. VideoAgent assembles the animated multi-shot "
            "film. MusicAgent composes the tribal percussion-and-vocals score. AudioMixAgent "
            "layers it under the dialogue+foley. CompositorAgent muxes the final mp4. Reject "
            "AmbienceAgent, Transcription/Translation, VideoAnalysis/IntakeVideo/StyleTransfer/"
            "VideoExtend/Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the Polynesian-myth story blueprint — young-navigator ocean-spirit-wake voyage arc.",
            "Decompose the voyage arc into Polynesian-myth animated scenes.",
            "Plan animation-style keyframes for the beach / outrigger / spirit-pool settings; text-only generation, no reference images supplied.",
            "Render per-shot animated clips preserving the Polynesian-myth aesthetic.",
            "Compose the tribal percussion-and-vocals the user requested, matching the Polynesian-myth register.",
            "Layer the tribal score under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final Polynesian-myth animated drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a Bollywood-styled musical mini-drama about a brilliant astrophysics student rebelling against her arranged marriage to elope with the family driver who shares her star-gazing obsession, with Indian classical fusion BGM.",
        "rationale": (
            "Bollywood-styled musical mini-drama from a text brief + Indian classical fusion BGM. "
            "StoryAgent drafts the astrophysics-student / arranged-marriage / driver-elopement "
            "blueprint. ScreenplayAgent breaks it into Bollywood-musical scenes. KeyFrameAgent "
            "plans keyframes for the engagement-courtyard / rooftop / train-station settings "
            "from text alone. VideoAgent assembles the multi-shot film. MusicAgent composes "
            "the Indian classical fusion score. AudioMixAgent layers it under the dialogue+"
            "foley. CompositorAgent muxes the final mp4. Reject AmbienceAgent, Transcription/"
            "Translation, VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight, "
            "Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the Bollywood-musical story blueprint — astrophysics-student arranged-marriage and driver-elopement arc.",
            "Decompose the elopement arc into Bollywood-musical scenes.",
            "Plan keyframes for the engagement-courtyard / rooftop / train-station settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving Bollywood-musical visual continuity.",
            "Compose the Indian classical fusion BGM the user requested, matching the Bollywood-musical register.",
            "Layer the fusion score under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final Bollywood-musical mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a Mars-astronaut mini-drama about a stranded geologist racing to assemble a solar-still before her water reserves run out, recording video letters home that she may never send, with intimate solo-piano BGM.",
        "rationale": (
            "Mars-astronaut mini-drama from a text brief + intimate solo-piano BGM. StoryAgent "
            "drafts the stranded-geologist / solar-still / video-letters blueprint. "
            "ScreenplayAgent breaks it into Mars-astronaut scenes. KeyFrameAgent plans keyframes "
            "for the rover-interior / regolith / first-drop settings from text alone. "
            "VideoAgent assembles the multi-shot film. MusicAgent composes the solo-piano "
            "score. AudioMixAgent layers it under the dialogue+foley. CompositorAgent muxes "
            "the final mp4. Reject AmbienceAgent, Transcription/Translation, VideoAnalysis/"
            "IntakeVideo/StyleTransfer/VideoExtend/Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the Mars-astronaut story blueprint — stranded-geologist solar-still and video-letters arc.",
            "Decompose the survival arc into Mars-astronaut scenes with solitary register.",
            "Plan keyframes for the rover-interior / regolith / first-drop settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving Mars-astronaut visual continuity.",
            "Compose the intimate solo-piano BGM the user requested, matching the Mars-astronaut register.",
            "Layer the solo-piano score under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final Mars-astronaut mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a Cold-War-spy mini-drama about a Russian translator at the British embassy choosing whether to defect after discovering her brother's name on a deportation list, with balalaika-and-strings BGM.",
        "rationale": (
            "Cold-War-spy mini-drama from a text brief + balalaika-and-strings BGM. StoryAgent "
            "drafts the Russian-translator / British-embassy / brother-deportation / defection "
            "blueprint. ScreenplayAgent breaks it into Cold-War-spy scenes. KeyFrameAgent plans "
            "keyframes for the records-room / embassy-bathroom / midnight-bridge settings from "
            "text alone. VideoAgent assembles the multi-shot film. MusicAgent composes the "
            "balalaika-and-strings score. AudioMixAgent layers it under the dialogue+foley. "
            "CompositorAgent muxes the final mp4. Reject AmbienceAgent, Transcription/"
            "Translation, VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight, "
            "Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the Cold-War-spy story blueprint — Russian-translator British-embassy defection-decision arc.",
            "Decompose the defection arc into Cold-War-spy scenes.",
            "Plan keyframes for the records-room / embassy-bathroom / midnight-bridge settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving Cold-War-spy visual continuity.",
            "Compose the balalaika-and-strings BGM the user requested, matching the Cold-War-spy register.",
            "Layer the balalaika-and-strings score under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final Cold-War-spy mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a Victorian-mystery mini-drama about a governess in a wealthy household solving the disappearance of the youngest daughter using only the family's drawing-room records, with harpsichord-and-strings BGM.",
        "rationale": (
            "Victorian-mystery mini-drama from a text brief + harpsichord-and-strings BGM. "
            "StoryAgent drafts the governess / wealthy-household / disappearance blueprint. "
            "ScreenplayAgent breaks it into Victorian-mystery scenes. KeyFrameAgent plans "
            "keyframes for the drawing-room / pantry / conservatory settings from text alone. "
            "VideoAgent assembles the multi-shot film. MusicAgent composes the harpsichord-and-"
            "strings score. AudioMixAgent layers it under the dialogue+foley. CompositorAgent "
            "muxes the final mp4. Reject AmbienceAgent, Transcription/Translation, "
            "VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight, "
            "Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the Victorian-mystery story blueprint — governess investigation of the youngest-daughter's disappearance.",
            "Decompose the mystery arc into Victorian-period investigative scenes.",
            "Plan keyframes for the drawing-room / pantry / conservatory settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving Victorian-period visual continuity.",
            "Compose the harpsichord-and-strings BGM the user requested, matching the Victorian-mystery register.",
            "Layer the harpsichord-and-strings score under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final Victorian-mystery mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make an action-film trailer about a former special-forces operator dragged back in for one last extraction when her younger sister is taken in a banking-cartel kidnapping, with climactic trailer-hits BGM.",
        "rationale": (
            "Action-film trailer (cinematic chain, trailer-pace deliverable) from a text brief "
            "+ climactic trailer-hits BGM. StoryAgent drafts the former-operator / sister-"
            "kidnapping / extraction blueprint. ScreenplayAgent breaks it into trailer-pace "
            "action scenes. KeyFrameAgent plans keyframes for the kidnapping / gear-up / "
            "breach settings from text alone. VideoAgent assembles the trailer-style film. "
            "MusicAgent composes the trailer-hits score. AudioMixAgent layers it under the "
            "dialogue+foley. CompositorAgent muxes the final mp4. Reject AmbienceAgent, "
            "Transcription/Translation, VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/"
            "Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the action-film trailer story blueprint — former-operator extraction and sister-kidnapping arc.",
            "Decompose the extraction arc into trailer-pace action scenes.",
            "Plan keyframes for the kidnapping / gear-up / breach settings; text-only generation, no reference images supplied.",
            "Render per-shot trailer clips preserving action-film visual continuity.",
            "Compose the climactic trailer-hits BGM the user requested, matching the action-film register.",
            "Layer the trailer-hits score under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final action-film trailer with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a 60-second vertical-short influencer-drama where a beauty creator's sponsored video accidentally exposes a co-creator's plagiarism the morning of their joint launch, with viral-pop electronic BGM.",
        "rationale": (
            "60-second vertical-short influencer-drama from a text brief + viral-pop electronic "
            "BGM. StoryAgent drafts the beauty-creator / sponsored-video / plagiarism-exposure "
            "blueprint. ScreenplayAgent breaks it into vertical-format influencer-drama scenes. "
            "KeyFrameAgent plans portrait-aspect keyframes for the ring-light shoot / playback "
            "/ confrontation settings from text alone. VideoAgent assembles the vertical "
            "multi-shot film. MusicAgent composes the viral-pop electronic score. AudioMixAgent "
            "layers it under the dialogue+foley. CompositorAgent muxes the final mp4. Reject "
            "AmbienceAgent, Transcription/Translation, VideoAnalysis/IntakeVideo/StyleTransfer/"
            "VideoExtend/Highlight, Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the influencer-drama story blueprint — beauty-creator sponsored-video and plagiarism-exposure arc.",
            "Decompose the exposure arc into vertical-format influencer-drama scenes.",
            "Plan portrait-aspect keyframes for the ring-light shoot / playback / confrontation settings; text-only generation, no reference images supplied.",
            "Render per-shot vertical clips preserving the influencer-drama aesthetic.",
            "Compose the viral-pop electronic BGM the user requested, matching the influencer-drama register.",
            "Layer the viral-pop score under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final influencer-drama vertical short with mixed audio and inter-shot transitions.",
        ],
    },
    {
        "user_goal": "Make a manhua-style isekai mini-drama about a Tokyo salaryman reborn as the villain of a webnovel he once read, who must outmaneuver the original protagonist before the canon-set execution date, with dramatic synth-orchestral BGM.",
        "rationale": (
            "Manhua-style isekai mini-drama from a text brief + dramatic synth-orchestral BGM. "
            "StoryAgent drafts the salaryman-reborn-as-villain / canon-execution / outmaneuver "
            "blueprint. ScreenplayAgent breaks it into manhua-isekai scenes. KeyFrameAgent "
            "plans manhua-style keyframes for the rebirth / library / balcony-confrontation "
            "settings from text alone. VideoAgent assembles the multi-shot film. MusicAgent "
            "composes the synth-orchestral score. AudioMixAgent layers it under the dialogue+"
            "foley. CompositorAgent muxes the final mp4. Reject AmbienceAgent, Transcription/"
            "Translation, VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight, "
            "Narration/Illustration/Narrator."
        ),
        "intents": [
            "Draft the manhua-isekai story blueprint — salaryman-reborn-as-villain canon-execution outmaneuver arc.",
            "Decompose the outmaneuver arc into manhua-isekai scenes.",
            "Plan manhua-style keyframes for the rebirth / library / balcony-confrontation settings; text-only generation, no reference images supplied.",
            "Render per-shot clips preserving manhua-isekai visual continuity.",
            "Compose the dramatic synth-orchestral BGM the user requested, matching the manhua-isekai register.",
            "Layer the synth-orchestral score under the clip's baked dialogue+foley track into one final mixed wav.",
            "Composite the final manhua-isekai mini-drama mp4 with mixed audio and inter-shot transitions.",
        ],
    },
]
