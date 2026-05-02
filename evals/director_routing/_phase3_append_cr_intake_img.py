"""Phase 3: cr +42 + intake_img +37 (= 79 cases).

cr: 4 shapes (pure 25 / +Music 19 / +Ambience 19 / +M|A alt 17)
  longstory: 5 new (3 pure / 1 Music / 1 Ambience), maintains ~13% ratio.

intake_img: 5 shapes (pure 17 / +sub NEW 11 / +bilingual 10 / +Music NEW 8 / +sub+Music NEW 5)
  No longstory (original had 0).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

THIS = Path(__file__).resolve().parent
sys.path.insert(0, str(THIS))
from categorize import categorize  # noqa: E402

V4 = THIS / "eval_cases_v4_500.json"

# --- cr chains ---
CR_PURE = [["StoryAgent"], ["ScreenplayAgent"], ["KeyFrameAgent"], ["VideoAgent"], ["CompositorAgent"], ["done"]]
CR_MUSIC = [["StoryAgent"], ["ScreenplayAgent"], ["KeyFrameAgent"], ["VideoAgent"], ["MusicAgent"], ["AudioMixAgent"], ["CompositorAgent"], ["done"]]
CR_AMBIENCE = [["StoryAgent"], ["ScreenplayAgent"], ["KeyFrameAgent"], ["VideoAgent"], ["AmbienceAgent"], ["AudioMixAgent"], ["CompositorAgent"], ["done"]]
CR_ALT = [["StoryAgent"], ["ScreenplayAgent"], ["KeyFrameAgent"], ["VideoAgent"], ["MusicAgent", "AmbienceAgent"], ["AmbienceAgent", "MusicAgent"], ["AudioMixAgent"], ["CompositorAgent"], ["done"]]

# --- intake_img chains ---
IMG_PURE = [["IntakeImageAgent"], ["BriefEnricherAgent"], ["StoryAgent"], ["ScreenplayAgent"], ["KeyFrameAgent"], ["VideoAgent"], ["CompositorAgent"], ["done"]]
IMG_SUB = [["IntakeImageAgent"], ["BriefEnricherAgent"], ["StoryAgent"], ["ScreenplayAgent"], ["KeyFrameAgent"], ["VideoAgent"], ["TranscriptionAgent"], ["CompositorAgent"], ["done"]]
IMG_BILINGUAL = [["IntakeImageAgent"], ["BriefEnricherAgent"], ["StoryAgent"], ["ScreenplayAgent"], ["KeyFrameAgent"], ["VideoAgent"], ["TranscriptionAgent"], ["TranslationAgent"], ["CompositorAgent"], ["done"]]
IMG_MUSIC = [["IntakeImageAgent"], ["BriefEnricherAgent"], ["StoryAgent"], ["ScreenplayAgent"], ["KeyFrameAgent"], ["VideoAgent"], ["MusicAgent"], ["AudioMixAgent"], ["CompositorAgent"], ["done"]]
IMG_SUB_MUSIC = [["IntakeImageAgent"], ["BriefEnricherAgent"], ["StoryAgent"], ["ScreenplayAgent"], ["KeyFrameAgent"], ["VideoAgent"], ["TranscriptionAgent"], ["MusicAgent"], ["AudioMixAgent"], ["CompositorAgent"], ["done"]]


BATCHES = [
    # ===== cr pure +13 (3 longstory + 10 short) =====
    {"chain": CR_PURE, "bucket": "cr", "cases": [
        ("cr_039", "Here's my story I want to process: Ezra Caine had been the night janitor at the Wexler Pharmaceutical building for twenty-three years and could read every room by the smell it left in his bucket water. The seventh floor smelled like burnt coffee and ozone. The fourteenth floor smelled like new carpet and fear. On the night of November 11th he found a manila folder taped to the underside of a desk on the eleventh floor, addressed to him by name, in his late wife's handwriting."),
        ("cr_040", "Here's my story I want to process: Maeve Faolán had stopped speaking when she was four years old, after the fire, and her grandmother had stopped trying to make her by the time she was seven. They lived in a small whitewashed house on the cliffs above Black Strand Bay, where the wind made all the speaking that needed doing. On the morning of Maeve's twelfth birthday, the gulls flew inland, the tide pulled out farther than anyone could remember, and a boy in waterlogged clothes walked up the goat path holding a piece of slate with her old name written on it."),
        ("cr_041", "Here's my story I want to process: The Yu family had been bone-setters in the same alley off Yongkang Road in Taipei for four generations, and Yu An-Chen had been told her whole life she would be the fifth. She was thirty-one and unmarried and increasingly unable to look her father in the eye when he left the door of the clinic open after dinner. The night the old practitioner Master Tang collapsed across the threshold of their shop with three broken ribs and a man in a black coat trailing a paper trail of blood behind him, An-Chen finally understood why her family had been there so long."),
        ("cr_042", "Make an animated short about a retired ferry captain whose final crossing of the Bosphorus is interrupted by a passenger no one else can see."),
        ("cr_043", "Make a 4-minute animated drama about a Beijing forensic accountant who, while auditing a state-owned bank, finds her own father's name on a corruption ledger."),
        ("cr_044", "Create a noir mystery short about a 1940s San Francisco taxi dancer who realizes her best customer has been the same man wearing four different faces."),
        ("cr_045", "Make a 3-minute period drama about a young Persian astronomer in 11th-century Esfahan who is forced to disprove his own discovery to save his observatory."),
        ("cr_046", "Produce an animated mini-drama about an Irish peat-cutter who unearths a bog body that begins speaking to him in his late mother's voice."),
        ("cr_047", "Create a sci-fi short about the last librarian on a doomed orbital station deciding which thousand books humanity will keep."),
        ("cr_048", "Make a 5-minute animated drama about a Cuban cigar-roller in 1958 Havana who reads aloud forbidden newspapers to the women on her shop floor."),
        ("cr_049", "Create a coming-of-age short about a 14-year-old beekeeper's apprentice in rural Slovenia who must save her grandfather's hives during a sudden September frost."),
        ("cr_050", "Make a workplace drama short about a third-generation New York pawnshop owner who recognizes a wedding ring he sold thirty years ago come back across his counter."),
        ("cr_051", "Produce a 3-minute animated mystery about a Lagos street photographer who notices the same stranger appearing in the background of every photo she has taken in the past month."),
    ]},

    # ===== cr + Music +10 (1 longstory + 9 short) =====
    {"chain": CR_MUSIC, "bucket": "cr", "cases": [
        ("cr_052", "Here's my story I want to process: Tomás Aguirre had been the second violinist of the Buenos Aires Philharmonic for thirty-one seasons, and in all that time he had never once played a wrong note in public. He had also never, in all that time, been given a solo. The night the principal violinist collapsed during the second movement of a Tchaikovsky concerto and the conductor's eyes locked with his across the orchestra pit, Tomás finally understood what his teacher had meant when he said that some musicians spend their entire careers waiting for one particular Tuesday. Add a tense orchestral score that mirrors the unfolding solo."),
        ("cr_053", "Make a 3-minute animated period drama about a Romani fortune-teller in 1920s Vienna who reads cards for a young composer afraid of going deaf, scored with a dark waltz."),
        ("cr_054", "Create an animated mini-drama about a young female cellist who travels to her grandmother's wartime village to play the cello her grandmother buried before fleeing, with a slow string score."),
        ("cr_055", "Produce a noir mini-drama about a 1950s Paris cabaret singer who realizes her late lover's last song has been published under another woman's name, with a smoky jazz score."),
        ("cr_056", "Make a 4-minute coming-of-age animated drama about a teenage boy in rural Tennessee who learns his late father's bluegrass mandolin tunes by ear from old radio recordings, with an Appalachian-bluegrass underscore."),
        ("cr_057", "Create a romantic period drama about an Edinburgh organ-builder who falls in love with the deaf abbess he is restoring an instrument for, scored with cathedral organ and strings."),
        ("cr_058", "Make a fantasy mini-drama about a young dragon-rider whose bond with her dragon is interrupted by a rival who has stolen the song that calls them home, scored with epic orchestra."),
        ("cr_059", "Produce a 5-minute animated drama about an aging Cuban son-musician returning to the village where he last performed in 1959, with a son-cubano-and-tres underscore."),
        ("cr_060", "Make an animated mini-drama about a young female DJ in modern Tokyo who builds a final farewell mix from her late father's vinyl collection, with an ambient electronic score."),
        ("cr_061", "Create a 3-minute period thriller about a young French Resistance pianist in 1943 Paris transmitting coded messages through Chopin nocturnes, with a tense piano-and-strings score."),
    ]},

    # ===== cr + Ambience +10 (1 longstory + 9 short) =====
    {"chain": CR_AMBIENCE, "bucket": "cr", "cases": [
        ("cr_062", "Here's my story I want to process: Roisin McCready had moved to the Aran Islands in October because she could not afford anywhere else and because her brother had told her, on the night before he disappeared at sea, that she would understand him better if she lived where the wind never stopped. She rented a stone cottage with a slate roof and a single window that faced south. The wind, as he had promised, never did stop. On the seventh week she began to hear, between the lulls in the wind, a voice she could not quite place. Use constant Atlantic-coast ambience under the narration — wind across stone, distant surf, gulls."),
        ("cr_063", "Make a 4-minute animated drama about a forest-fire watchtower observer who slowly realizes the woman who left him last summer is still walking the trail below, with constant forest ambience."),
        ("cr_064", "Create a noir mini-drama about a Mumbai night-train conductor who hears the same impossible passenger announcement at every station, with constant rail-clatter and station ambience."),
        ("cr_065", "Make a coming-of-age animated short about a young girl learning to ride her first horse on her grandfather's Patagonian estancia, with constant pampa-wind ambience."),
        ("cr_066", "Produce a sci-fi mini-drama about the lone scientist on a Mars seismic monitoring outpost who hears something rhythmic and not seismic in the data, with constant Mars-wind-and-rover ambience."),
        ("cr_067", "Make a 3-minute period thriller about a young woman trapped on the night shift of a 1920s Liverpool textile mill during a labor uprising, with constant industrial-loom ambience."),
        ("cr_068", "Create an animated drama about a Vietnamese cave-explorer trying to map a section his late father failed to finish, with constant cave-water-drip ambience."),
        ("cr_069", "Produce a 4-minute animated drama about an Inuit hunter following caribou tracks across the spring tundra and finding his missing brother's snow knife, with constant wind-across-snow ambience."),
        ("cr_070", "Make a romance short about two strangers waiting out a blizzard in a small Vermont diner overnight, with constant blizzard-howl and diner-coffee-machine ambience."),
        ("cr_071", "Create an animated mystery short about a Japanese onsen-keeper whose night-bath guests have left increasingly strange things behind, with constant hot-spring-water-and-cicada ambience."),
    ]},

    # ===== cr + Music|Ambience alt +9 (0 longstory) =====
    {"chain": CR_ALT, "bucket": "cr", "cases": [
        ("cr_072", "Make a 4-minute animated war drama about a Senegalese tirailleur in WWI trenches writing letters home to his daughter, score with a brass-and-strings march under battlefield ambience."),
        ("cr_073", "Create a coming-of-age animated drama about a young Bolivian llama-herder discovering an Inca ruin during a winter migration, with a wooden-flute score under high-altitude wind ambience."),
        ("cr_074", "Produce a 5-minute animated drama about a 1970s Kenyan rangefinder photographing the Great Migration alongside a poacher she's tracking, score with African-percussion under savannah ambience."),
        ("cr_075", "Make a romance mini-drama about an Italian glassblower in 1930s Murano teaching his blind apprentice by sound and heat alone, with delicate strings under furnace and water ambience."),
        ("cr_076", "Create a mystery animated drama about a Welsh coal-miner's daughter in 1860s Aberdare investigating a string of accidents at her father's pit, with a sad string score under mine-shaft ambience."),
        ("cr_077", "Make a 3-minute fantasy drama about a young witch's apprentice in old Russia gathering nine impossible ingredients for a sick noblewoman, score with balalaika under forest ambience."),
        ("cr_078", "Produce a sci-fi short about the last lighthouse keeper on a flooded coast filming his final logbook entry for an unborn grandchild, with melancholic piano under crashing-surf ambience."),
        ("cr_079", "Make an animated period drama about a young Chinese herbalist in 1840s Macao supplying medicine to prisoners during the First Opium War, with erhu-and-strings under harbor ambience."),
        ("cr_080", "Create a thriller mini-drama about a Norwegian glacier guide leading a German expedition that has gone too far and refuses to turn back, with tense low strings under glacier-creak ambience."),
    ]},

    # ===== intake_img pure +9 =====
    {"chain": IMG_PURE, "bucket": "intake_img", "cases": [
        ("intake_img_014", "Using this uploaded portrait of a stoic samurai woman with a notched katana, make a 4-minute animated drama about her last duel against the lord who ordered her family executed."),
        ("intake_img_015", "Here's a watercolor of a young female aviator standing beside a 1920s biplane on a grass airstrip. Make an animated period drama about her solo crossing of the Andes."),
        ("intake_img_016", "I've uploaded a sketch of a Russian ballerina in worn rehearsal clothes. Make an animated coming-of-age mini-drama about her last audition before the company is liquidated."),
        ("intake_img_017", "Use this uploaded character ref of a heavily tattooed Yakuza accountant. Make a 3-minute neo-noir animated drama about his attempt to leave the syndicate after his daughter is born."),
        ("intake_img_018", "Here's a portrait of a 1860s Crimean War battlefield nurse with bloodied apron and a copper kettle. Make an animated period drama about the night she chose between two dying soldiers."),
        ("intake_img_019", "I've attached a concept painting of a half-flooded medieval cathedral lit by candle. Use it as the setting and make a fantasy mini-drama about a heretic priest hiding the last copy of a forbidden gospel."),
        ("intake_img_020", "Use this uploaded portrait of a Maasai elder warrior in red shuka. Make an animated drama about his return to his tribe's ancestral lands as the seasonal rains fail for the third year."),
        ("intake_img_021", "Here's a watercolor of a Kazakh eagle-huntress on horseback in winter steppe. Make an animated mini-drama about her bond with her aging eagle as it loses its sight."),
        ("intake_img_022", "I've uploaded a sketch of a 1920s Paris perfumer's daughter at a brass workbench surrounded by glass vials. Make an animated period drama about her secret formula that distills her late mother's last day."),
    ]},

    # ===== intake_img + sub NEW +11 =====
    {"chain": IMG_SUB, "bucket": "intake_img", "cases": [
        ("intake_img_023", "Using this uploaded portrait of a Korean female detective in a 1990s Seoul precinct, make a 4-minute neo-noir mini-drama about her last case before her promotion, with English subtitles."),
        ("intake_img_024", "Here's concept art of a mid-19th-century Brazilian sugar plantation. Make an animated period drama about a young house slave's escape with the master's son, with English subtitles."),
        ("intake_img_025", "I've uploaded a portrait of a Filipino karate instructor with a worn black belt. Make an animated mini-drama about his last student finally challenging him, with English subtitles."),
        ("intake_img_026", "Use this uploaded sketch of a young female Israeli paramedic at the back of an ambulance. Make a contemporary drama about her shift the night her brother was caught in a bombing, with English subtitles."),
        ("intake_img_027", "Here's a portrait of a Polish ironworker in worn leather apron at a forge. Make a 4-minute period drama about his last commission for the underground in 1944 Warsaw, with English subtitles."),
        ("intake_img_028", "I've attached a watercolor of a young Berber woman with kohl-lined eyes weaving a carpet. Make an animated drama about the day she weaves a forbidden message into a noble's wedding rug, with English subtitles."),
        ("intake_img_029", "Using this uploaded portrait of an aging Greek shipowner staring out at the harbor, make an animated mini-drama about his decision to sell the last family vessel, with English subtitles."),
        ("intake_img_030", "Here's a sketch of a young female Indonesian shadow-puppet master backstage with her gamelan orchestra. Make a 3-minute period drama about her last performance before a colonial governor, with English subtitles."),
        ("intake_img_031", "I've uploaded a portrait of a Quebecois lumberjack in winter wool, holding an axe. Make an animated drama about his return to the forest where his crew was lost in a winter avalanche, with English subtitles."),
        ("intake_img_032", "Use this uploaded character ref of a Mongolian female contortionist in red costume. Make an animated mini-drama about her audition for a foreign circus that won't take her aging mother, with English subtitles."),
        ("intake_img_033", "Here's a portrait of a Sicilian widow in mourning black holding a brass key. Make an animated mystery short about the door this key unlocks at her late husband's old vineyard, with English subtitles."),
    ]},

    # ===== intake_img + bilingual +5 =====
    {"chain": IMG_BILINGUAL, "bucket": "intake_img", "cases": [
        ("intake_img_034", "Using this uploaded portrait of a 1930s Shanghai jazz singer in a beaded qipao, make a period mini-drama about her last performance before fleeing for Hong Kong, with English-Chinese bilingual subtitles."),
        ("intake_img_035", "Here's a watercolor of an aging French chef at a Provencal market stall. Make an animated drama about his decision to teach his estranged daughter the family recipes, with English-French bilingual subtitles."),
        ("intake_img_036", "I've uploaded a sketch of a young Cuban revolutionary woman with a rifle on her shoulder in 1958 Sierra Maestra. Make an animated period drama about her last march before the city falls, with English-Spanish bilingual subtitles."),
        ("intake_img_037", "Use this uploaded portrait of a Hokkaido Ainu elder fisherman holding a salmon. Make an animated coming-of-age mini-drama about his teaching his half-Japanese grandson their ancestral fishing rites, with English-Japanese bilingual subtitles."),
        ("intake_img_038", "Here's concept art of a 17th-century Mughal court astrologer at a brass observatory. Make an animated period drama about his refusal to lie about an unfavorable horoscope for the heir, with English-Hindi bilingual subtitles."),
    ]},

    # ===== intake_img + Music NEW +8 =====
    {"chain": IMG_MUSIC, "bucket": "intake_img", "cases": [
        ("intake_img_039", "Using this uploaded portrait of a young female Spanish flamenco guitarist with calloused fingers, make a 4-minute period drama about her audition for a Sevillan tablao her late father played at, with a flamenco-guitar-and-cajón score."),
        ("intake_img_040", "Here's a sketch of an aging Russian conductor in a frayed tailcoat. Make an animated mini-drama about his final symphony performance before retirement, with a sweeping symphonic score."),
        ("intake_img_041", "I've uploaded a portrait of a young Tuareg desert musician with an electric guitar slung across his back. Make an animated drama about his first city performance after his nomad caravan settles, with a desert-blues guitar score."),
        ("intake_img_042", "Use this uploaded character ref of a 1950s American bobby-soxer with a transistor radio. Make a romance mini-drama about her secret broadcasts of forbidden rock-and-roll songs to her listening neighborhood, with a doo-wop-and-rock score."),
        ("intake_img_043", "Here's concept art of a Shaolin monastery courtyard at dawn. Make an animated kung-fu period drama about a young monk's final test before leaving the order, with a meditative wood-flute-and-percussion score."),
        ("intake_img_044", "I've attached a portrait of a French chanteuse in 1940s smoky cabaret light. Make a noir mini-drama about her last performance the night the resistance bombs the theater, with a chanson-piano-and-accordion score."),
        ("intake_img_045", "Using this uploaded watercolor of a young African djembe master in a Senegalese village, make an animated coming-of-age drama about his first solo performance at his uncle's wedding, with a polyrhythmic djembe-and-balafon score."),
        ("intake_img_046", "Here's a sketch of a young female Andean panpipe player in a high mountain village. Make an animated mini-drama about her invitation to perform at a state festival in Lima, with an Andean panpipe-and-charango score."),
    ]},

    # ===== intake_img + sub + Music NEW +5 =====
    {"chain": IMG_SUB_MUSIC, "bucket": "intake_img", "cases": [
        ("intake_img_047", "Using this uploaded portrait of a young female Japanese taiko drummer in white kimono, make a 4-minute period drama about her audition for a temple festival ensemble, with English subtitles and a taiko-and-shakuhachi underscore."),
        ("intake_img_048", "Here's a sketch of a Galician bagpiper at a coastal festival. Make an animated mini-drama about his last performance before emigrating to Buenos Aires, with English subtitles and a Galician-pipe-and-pandeireta underscore."),
        ("intake_img_049", "I've uploaded a portrait of a Greek bouzouki player at a 1950s rebetiko taverna. Make a noir period drama about his role in a dockworker's strike, with English subtitles and a smoky bouzouki-and-baglama underscore."),
        ("intake_img_050", "Use this uploaded character ref of a young female Chinese guzheng player at a Tang-dynasty court. Make an animated period drama about her composition that secretly mocks the chancellor, with English subtitles and a guzheng-and-pipa underscore."),
        ("intake_img_051", "Here's concept art of a 1960s New Orleans funeral march led by a brass band. Make an animated drama about a young trumpeter playing his mentor's funeral procession, with English subtitles and a New-Orleans brass underscore."),
    ]},
]


def main() -> None:
    existing = json.loads(V4.read_text(encoding="utf-8"))
    existing_names = {c["name"] for c in existing}

    new_entries: list[dict] = []
    for batch in BATCHES:
        chain = batch["chain"]
        bucket_expected = batch["bucket"]
        bucket = categorize(chain)
        if bucket != bucket_expected:
            raise SystemExit(f"chain mismatch: expected {bucket_expected}, got {bucket} for {chain}")
        for name, goal in batch["cases"]:
            if name in existing_names:
                raise SystemExit(f"duplicate: {name}")
            new_entries.append({
                "name": name,
                "category": bucket_expected,
                "user_goal": goal,
                "expected_chain": chain,
            })

    print(f"prepared {len(new_entries)} new cases")

    merged = existing + new_entries
    V4.write_text(
        json.dumps(merged, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"appended -> {V4}")
    print(f"total cases now: {len(merged)}")

    from collections import Counter
    from categorize import BUCKET_ORDER
    buckets = Counter(c["category"] for c in merged)
    for b in BUCKET_ORDER:
        print(f"  {b:<14} {buckets.get(b, 0)}")


if __name__ == "__main__":
    main()
