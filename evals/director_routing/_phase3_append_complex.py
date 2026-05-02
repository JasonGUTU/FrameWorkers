"""Phase 3 batch 1-8: append 73 new complex cases to eval_cases_v4_500.json.

Adds complex_023..complex_095 across 8 chain shapes.
- 6 existing shapes get filled to target n
- 2 NEW shapes added (VA+cr+Music; imgref+cr+Extend+Music)

Chain shapes are validated against categorize() to confirm bucket=complex.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

THIS = Path(__file__).resolve().parent
sys.path.insert(0, str(THIS))
from categorize import categorize  # noqa: E402

V4 = THIS / "eval_cases_v4_500.json"

# Chain shape -> list of (new_name, user_goal) tuples
BATCHES = [
    # Batch 1: imgref + cr + VideoExtend (existing shape, +8)
    {
        "chain": [
            ["IntakeImageAgent"], ["BriefEnricherAgent"],
            ["StoryAgent"], ["ScreenplayAgent"], ["KeyFrameAgent"], ["VideoAgent"],
            ["VideoExtendAgent"], ["CompositorAgent"], ["done"],
        ],
        "cases": [
            ("complex_023", "Here's a concept sketch of a ruined gothic cathedral at twilight. Build a possession-horror mini-drama where a young exorcist confronts her possessed sister at the altar, and extend the final candle-extinguishing climax shot by 12 seconds with slow shadow shifts."),
            ("complex_024", "I've uploaded a portrait of a wuxia heroine standing on a cliffside in tattered black robes. Make a vengeance mini-drama where she infiltrates the imperial court disguised as a dancer to expose the high official who poisoned her clan. Extend the unmasking-in-the-throne-room moment by 12 seconds with a slow camera arc."),
            ("complex_025", "I've uploaded a 1940s photo of a war correspondent woman standing in front of a half-destroyed railway station. Make a war-drama mini-series where she covers the liberation of an occupied village. Extend the moment a hidden child reunites with his mother on the rubble by 12 seconds."),
            ("complex_026", "Here's a digital painting of a steampunk airship docking at a sky-port at dusk. Produce a steampunk arranged-marriage romance mini-drama where the captain meets her suitor for the first time at the dock. Extend the first-eye-contact moment by 10 seconds."),
            ("complex_027", "Using this uploaded character portrait of a Tang-dynasty palace concubine, produce a court-intrigue mini-drama where she rises from the Cold Palace to become Empress Dowager and secretly pulls strings across three emperors. Extend the moment she removes her ceremonial mask in the throne room by 8 seconds."),
            ("complex_028", "Using this uploaded portrait of a tech founder in a glass-walled office, make a corporate-thriller mini-drama where his AI assistant turns out to be his murdered cofounder's uploaded consciousness. Extend the security-camera realization moment by 10 seconds."),
            ("complex_029", "I've attached a black-and-white photo of a young Mongolian eagle-hunter with her golden eagle on a stone outcrop. Make an animated coming-of-age drama about her training the bird through three seasons of harsh weather. Extend the final-release flight scene by 15 seconds with sweeping aerial shots."),
            ("complex_030", "Here's a concept painting of an abandoned Soviet-era diving suit lying on a deep sea floor. Build a cold-war mystery mini-drama where modern-day divers discover the body inside contains a sealed message about a buried operation. Extend the helmet-opening reveal by 12 seconds with rising bubble sound design."),
        ],
    },
    # Batch 2: VA + cr + Transcription (existing, +8)
    {
        "chain": [
            ["IntakeVideoAgent"], ["VideoAnalysisAgent"],
            ["StoryAgent"], ["ScreenplayAgent"], ["KeyFrameAgent"], ["VideoAgent"],
            ["TranscriptionAgent"], ["CompositorAgent"], ["done"],
        ],
        "cases": [
            ("complex_031", "Take this 5-minute trailer of a finished mystery-thriller mini-drama. Analyze its core conceit and pacing, then generate a wholly new prequel mini-drama set 10 years earlier, with English subtitles burned in."),
            ("complex_032", "Here's a 90-second clip of a documentary about underwater volcanoes. Read it as inspiration and produce a sci-fi animated mini-drama about a deep-sea geologist who discovers an alien intelligence in the magma plumes, with English subtitles."),
            ("complex_033", "I've uploaded a 3-minute segment of a 1980s Hong Kong crime film. Study its visual rhythm and street-noir mood, then write and produce a new English-subtitled animated mini-drama set in modern Tokyo's underground."),
            ("complex_034", "Here's a 4-minute reel of cooking-show highlights. Analyze its character chemistry and turn it into an animated workplace-romance mini-drama between two rival chefs in Paris, with English subtitles."),
            ("complex_035", "I've attached a 2-minute clip of a vintage talent-show audition. Analyze the contestant arcs and produce an animated underdog-rises mini-drama where a small-town singer climbs to stardom, with English subtitles."),
            ("complex_036", "Take this 6-minute episode of a finished court-drama mini-series. Study its political tensions, then build a fresh animated mini-drama set in a fictional Tang-era kingdom with similar power-play themes, English subtitles included."),
            ("complex_037", "Here's a 90-second nature montage of arctic wolves hunting. Analyze the predator-prey rhythm and produce an animated wilderness-survival mini-drama where a researcher gets stranded with a wolf pack, with English subtitles."),
            ("complex_038", "I've uploaded a 4-minute travel vlog through Istanbul's bazaars. Study its cultural texture and produce an animated romance mini-drama about a Turkish carpet weaver and a foreign archaeologist, with English subtitles."),
        ],
    },
    # Batch 3: VA + cr (pure) (existing, +9)
    {
        "chain": [
            ["IntakeVideoAgent"], ["VideoAnalysisAgent"],
            ["StoryAgent"], ["ScreenplayAgent"], ["KeyFrameAgent"], ["VideoAgent"],
            ["CompositorAgent"], ["done"],
        ],
        "cases": [
            ("complex_039", "Here's a 4-minute Korean revenge-thriller trailer. Analyze its escalating-stakes structure and produce a wholly new animated mini-drama in the same genre about a small-town doctor seeking justice for his daughter."),
            ("complex_040", "Take this 90-second epic-fantasy battle scene. Read its visual scale and produce a new animated mini-drama about a kingdom's last knight defending a mountain pass against an invading army."),
            ("complex_041", "I've uploaded a 5-minute segment from a Spanish-language telenovela. Study its emotional pacing and create a new animated romance mini-drama set in a 1920s ranch with similar passion-and-betrayal beats."),
            ("complex_042", "Here's a 3-minute action scene from a Hong Kong wuxia movie. Analyze its choreography and produce a new animated mini-drama about a young swordswoman avenging her master in feudal Japan."),
            ("complex_043", "Take this 2-minute scene of a hospital ICU drama. Analyze the character dynamics and produce a new animated medical mini-drama about a burned-out trauma surgeon who befriends a terminal patient."),
            ("complex_044", "I've attached a 5-minute clip of a vintage British detective show. Analyze its mystery-puzzle structure and produce a new animated mystery mini-drama set in 1930s Shanghai with a female private investigator."),
            ("complex_045", "Here's a 4-minute compilation from a survival reality show. Study its tension and produce a new animated post-apocalyptic mini-drama where strangers form an alliance to cross a radiation zone."),
            ("complex_046", "Take this 6-minute period-drama wedding scene. Analyze its visual composition and produce a new animated mini-drama about an ill-fated arranged marriage in Victorian England."),
            ("complex_047", "I've uploaded a 3-minute clip from a samurai film's duel sequence. Read its blade-work pacing and produce a new animated mini-drama about a ronin protecting a village from bandits."),
        ],
    },
    # Batch 4: Style + Extend (pure) (existing, +9)
    {
        "chain": [
            ["IntakeVideoAgent"], ["VideoExtendAgent"], ["StyleTransferAgent"], ["done"],
        ],
        "cases": [
            ("complex_048", "Extend this 8-second street fight clip by 15 seconds, then convert the whole thing to a comic-book line-art style."),
            ("complex_049", "Take this 12-second sunset time-lapse and extend it to 40 seconds, then restyle it into a Ukiyo-e woodblock aesthetic."),
            ("complex_050", "Extend this 10-second drone clip of a snowy mountain range by 20 seconds and apply a 1940s film-noir black-and-white treatment."),
            ("complex_051", "Take this 6-second clip of a chef plating dessert and stretch it to 25 seconds with extra detail shots, then restyle it as a watercolor animation."),
            ("complex_052", "Extend this 8-second ballet leap by 15 seconds in slow-motion, then convert the whole thing into a charcoal-sketch animation."),
            ("complex_053", "Take this 10-second wave-crashing footage and extend it to 35 seconds, then transform it into an Edo-period ink-painting style."),
            ("complex_054", "Extend this 5-second campfire-flame loop to 30 seconds and apply a Studio Ghibli watercolor-style treatment."),
            ("complex_055", "Take this 12-second underwater reef footage and extend it to 40 seconds, then restyle it as a 1920s art-deco mosaic."),
            ("complex_056", "Extend this 8-second horseback ride scene by 15 seconds and convert it into a traditional Chinese ink-wash animation."),
        ],
    },
    # Batch 5: Style + Extend + Transcription (existing, +9)
    {
        "chain": [
            ["IntakeVideoAgent"], ["VideoExtendAgent"], ["StyleTransferAgent"],
            ["TranscriptionAgent"], ["CompositorAgent"], ["done"],
        ],
        "cases": [
            ("complex_057", "Extend this 10-second café argument scene by 15 seconds, restyle it as a noir comic, and burn in English subtitles."),
            ("complex_058", "Take this 6-second dorm-room confession and extend it to 25 seconds, convert to anime-style animation, then add English subtitles."),
            ("complex_059", "Extend this 12-second Renaissance-painting tableau-vivant by 20 seconds, restyle it into a Caravaggio chiaroscuro style, and burn in subtitles."),
            ("complex_060", "Take this 8-second courtroom outburst and extend it to 25 seconds, convert it to graphic-novel style, then add English subtitles."),
            ("complex_061", "Extend this 5-second silent-film slapstick clip by 15 seconds, restyle it into a 3D Pixar animation, and add modern English subtitles."),
            ("complex_062", "Take this 10-second street-busker performance and extend it to 30 seconds, convert it into a watercolor-illustrated animation, then add English subtitles."),
            ("complex_063", "Extend this 8-second wedding-vow exchange by 15 seconds, restyle it as a stained-glass window animation, and burn in English subtitles."),
            ("complex_064", "Take this 7-second emergency-room operation and extend it to 25 seconds, convert it into a hand-drawn medical-illustration style, then add English subtitles."),
            ("complex_065", "Extend this 6-second telephone-booth phone call by 18 seconds, convert it into a 1970s rotoscope animation, and add English subtitles."),
        ],
    },
    # Batch 6: Style + Extend + Music (existing, +9)
    {
        "chain": [
            ["IntakeVideoAgent"], ["StyleTransferAgent"], ["VideoExtendAgent"],
            ["MusicAgent"], ["AudioMixAgent"], ["CompositorAgent"], ["done"],
        ],
        "cases": [
            ("complex_066", "First convert this 10-second swordfight scene to ink-painting style, then extend the climax by 15 seconds, and finally add a guqin-driven traditional score."),
            ("complex_067", "Take this 8-second street-skating clip, restyle it as a 1990s graffiti aesthetic, then extend it to 25 seconds, and layer in a hip-hop beat."),
            ("complex_068", "Convert this 12-second farmhouse-window scene to a Van Gogh impressionist style, then extend it to 35 seconds, and overlay a melancholic violin score."),
            ("complex_069", "Restyle this 7-second train-platform farewell into a charcoal-sketch animation, then extend the final embrace by 15 seconds, and add an emotional cello-and-piano duet."),
            ("complex_070", "Take this 8-second cathedral-interior shot, convert it to a stained-glass animated style, then extend it to 28 seconds, and underlay reverent organ music."),
            ("complex_071", "Convert this 10-second nighttime city skyline to a synthwave neon look, then extend it to 30 seconds, and layer in an 80s synthwave track."),
            ("complex_072", "First restyle this 6-second sword-draw moment as a samurai-anime illustration, then extend it to 22 seconds in slow-motion, and add a taiko-and-shakuhachi score."),
            ("complex_073", "Take this 8-second forest-stream footage, restyle it as a Studio Ghibli watercolor scene, then extend it to 30 seconds, and overlay a soft acoustic-guitar melody."),
            ("complex_074", "Convert this 9-second ballroom-waltz clip to a Belle Époque oil-painting aesthetic, then extend the climactic spin by 18 seconds, and add a sweeping waltz score."),
        ],
    },
    # Batch 7: VA + cr + Music (NEW shape, +11)
    {
        "chain": [
            ["IntakeVideoAgent"], ["VideoAnalysisAgent"],
            ["StoryAgent"], ["ScreenplayAgent"], ["KeyFrameAgent"], ["VideoAgent"],
            ["MusicAgent"], ["AudioMixAgent"], ["CompositorAgent"], ["done"],
        ],
        "cases": [
            ("complex_075", "Take this 5-minute clip of a finished crime-thriller pilot. Analyze its tension structure and produce a new animated mini-drama in the same genre about a young hacker uncovering financial corruption, with a tense electronic score."),
            ("complex_076", "Here's a 3-minute reel from a Western-style cowboy movie. Analyze its frontier mood and produce a new animated mini-drama about a sheriff facing a returning outlaw, with a sweeping orchestral Western score."),
            ("complex_077", "I've uploaded a 4-minute clip from a 1960s spy film. Study its cool tone and produce a new animated mini-drama about a double-agent in Cold War Berlin, with a brassy spy-jazz score."),
            ("complex_078", "Take this 6-minute period-drama courtship scene. Analyze its restraint and produce a new animated romance mini-drama set in 1900s Vienna with a Strauss-style waltz score."),
            ("complex_079", "Here's a 90-second clip of an action-anime sword fight. Read its kinetic energy and produce a new animated mini-drama about a samurai protecting a village, with a taiko-and-strings score."),
            ("complex_080", "I've attached a 4-minute compilation from a horror-mystery TV pilot. Analyze its atmospheric build and produce a new animated mini-drama about a small-town journalist investigating disappearances, with a creepy ambient-electronic score."),
            ("complex_081", "Take this 3-minute travel documentary on the Sahara. Read its desolate vastness and produce a new animated mini-drama about a caravan trader betrayed by his own brother, with a percussive desert score."),
            ("complex_082", "Here's a 5-minute heist-movie planning sequence. Analyze its caper rhythm and produce a new animated mini-drama about a museum theft in modern Berlin, with a propulsive electronic-jazz score."),
            ("complex_083", "I've uploaded a 4-minute clip of a wuxia mountaintop confrontation. Study its martial poise and produce a new animated mini-drama about a hidden master training a reluctant disciple, with a guzheng-led score."),
            ("complex_084", "Take this 90-second clip of a sci-fi space chase. Analyze its kinetic visuals and produce a new animated mini-drama about smugglers escaping a corporate fleet, with a synth-orchestral score."),
            ("complex_085", "Here's a 5-minute supernatural-mystery TV pilot opener. Analyze its slow-burn dread and produce a new animated mini-drama about a folklorist investigating a haunted Cornish village, with an eerie folk-instrumental score."),
        ],
    },
    # Batch 8: imgref + cr + VideoExtend + Music (NEW shape, +10)
    {
        "chain": [
            ["IntakeImageAgent"], ["BriefEnricherAgent"],
            ["StoryAgent"], ["ScreenplayAgent"], ["KeyFrameAgent"], ["VideoAgent"],
            ["VideoExtendAgent"], ["MusicAgent"], ["AudioMixAgent"],
            ["CompositorAgent"], ["done"],
        ],
        "cases": [
            ("complex_086", "Using this uploaded portrait of a young female opera singer, make a 1920s Paris music-drama about her rise from a streetwalker to a celebrated diva. Extend her debut-night performance by 15 seconds with sweeping camera moves, and add a romantic orchestral score."),
            ("complex_087", "Here's a concept painting of a futuristic Mars colony. Build a sci-fi mini-drama about a botanist discovering a contagion in the colony's hydroponics. Extend the contamination-reveal moment by 12 seconds, and underlay a tense ambient-electronic score."),
            ("complex_088", "I've uploaded a character portrait of a Victorian governess. Make a gothic-mystery mini-drama where she discovers her young charges are communicating with a dead aunt. Extend the séance climactic flicker by 10 seconds, and add a haunting harpsichord score."),
            ("complex_089", "Use this uploaded photo of a Gibson Les Paul guitar with the strap of a famous deceased rocker. Produce a music-biopic mini-drama about a young guitarist haunted by his idol's ghost. Extend the on-stage breakdown moment by 15 seconds, and add a heavy blues-rock track."),
            ("complex_090", "Here's a digital painting of a samurai standing in autumn leaves. Make a wuxia mini-drama about an aging warrior teaching his last student. Extend the final-bow sword-laydown moment by 12 seconds, and add a shakuhachi-and-strings elegy."),
            ("complex_091", "I've uploaded a portrait of a 1940s Black jazz pianist at a smoky club piano. Make a biographical mini-drama about his rise from a Mississippi farm to Carnegie Hall. Extend his Carnegie debut intro by 12 seconds, and underlay a swelling Gershwin-style score."),
            ("complex_092", "Use this uploaded character ref of a starship captain in a worn flight suit. Produce a space-opera mini-drama about her last mission to evacuate a doomed colony. Extend the colony-evacuation departure shot by 18 seconds, and add a triumphant-but-tragic orchestral score."),
            ("complex_093", "Here's a concept painting of a flooded Venice street with gondolas reflecting in the moonlight. Make a romance mini-drama about a glassmaker and a foreign poet who meet during high water. Extend the moonlit-canoe goodbye scene by 15 seconds, and add a melancholic accordion-and-strings piece."),
            ("complex_094", "I've attached a portrait of a Harlem Renaissance dancer in 1925 stage costume. Produce a music-drama mini-series about her career and a forbidden romance with a white club owner. Extend the final performance reveal by 15 seconds, and underlay a Duke-Ellington-style swing track."),
            ("complex_095", "Use this uploaded character portrait of a frostbitten polar explorer. Make a survival-drama mini-series about his return from a failed expedition where his crew died. Extend the moment he sees his wife at the dock by 12 seconds, and add a piercing melancholic violin score."),
        ],
    },
]


def main() -> None:
    existing = json.loads(V4.read_text(encoding="utf-8"))
    existing_names = {c["name"] for c in existing}

    new_entries: list[dict] = []
    for batch in BATCHES:
        chain = batch["chain"]
        # Validate chain -> complex
        bucket = categorize(chain)
        if bucket != "complex":
            raise SystemExit(f"chain does not categorize to complex: {chain}")
        for name, goal in batch["cases"]:
            if name in existing_names:
                raise SystemExit(f"duplicate name with existing: {name}")
            new_entries.append({
                "name": name,
                "category": "complex",
                "user_goal": goal,
                "expected_chain": chain,
            })

    print(f"prepared {len(new_entries)} new complex cases")

    # Sanity: name uniqueness within batch
    new_names = [e["name"] for e in new_entries]
    if len(new_names) != len(set(new_names)):
        raise SystemExit("duplicate names within new batch")

    # Sanity: every new entry's category is consistent with categorize()
    for e in new_entries:
        actual = categorize(e["expected_chain"])
        if actual != e["category"]:
            raise SystemExit(f"category mismatch: {e['name']} {actual} != {e['category']}")

    merged = existing + new_entries
    V4.write_text(
        json.dumps(merged, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"appended -> {V4}")
    print(f"total cases now: {len(merged)}")

    # Per-bucket summary
    from collections import Counter
    buckets = Counter(c["category"] for c in merged)
    from categorize import BUCKET_ORDER
    for b in BUCKET_ORDER:
        print(f"  {b:<14} {buckets.get(b, 0)}")


if __name__ == "__main__":
    main()
