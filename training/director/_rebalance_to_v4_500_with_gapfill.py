"""Rebalance training jsonl files to match eval_cases_v4_500 chain-shape distribution,
filling gaps with fresh user_goals (option B — clean, no train/eval contamination).

For each input file:
  1. Drop samples with chain shapes NOT in eval (training-only synthetic).
  2. Per-(bucket, shape) rebalance to match eval per-shape proportions.
  3. For eval shapes with 0 training samples, generate fresh training samples from
     49 hand-written user_goals and upsample with replacement.
  4. Output to <stem>.v4_500.jsonl (originals untouched).

Usage: python _rebalance_to_v4_500_with_gapfill.py
"""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path
from collections import defaultdict

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "evals" / "director_routing"))
sys.path.insert(0, str(REPO_ROOT))
from categorize import categorize, BUCKET_ORDER  # noqa: E402

THIS = Path(__file__).resolve().parent
EVAL_FILE = REPO_ROOT / "evals" / "director_routing" / "eval_cases_v4_500.json"

# Try to import render_rationale + INTENT_VARIANTS; minimal fallbacks if unavailable.
try:
    from training.director.build_templated_sft_jsonl import render_rationale, INTENT_VARIANTS  # type: ignore
    HAVE_RATIONALE = True
except Exception:
    HAVE_RATIONALE = False
    INTENT_VARIANTS = {}

INPUTS = [
    THIS / "samples_sft_full.jsonl",
    THIS / "samples_sft_full.no_rationale.jsonl",
    THIS / "samples_sft_full.templated.jsonl",
    THIS / "samples_grpo_v1.jsonl",
    THIS / "samples_grpo_v1.no_rationale.jsonl",
    THIS / "samples_grpo_v1.templated.jsonl",
]

RANDOM_SEED = 42

# === 7 gap shapes × ~5-8 fresh user_goals each ===
# Each gap shape: (slug, chain_agents, [user_goals])
GAP_SHAPES = [
    {
        "slug": "intake_img_cr_subtitle",
        "chain": ["IntakeImageAgent", "BriefEnricherAgent", "StoryAgent", "ScreenplayAgent", "KeyFrameAgent", "VideoAgent", "TranscriptionAgent", "CompositorAgent"],
        "user_goals": [
            "I've uploaded a portrait of a Mexican luchador in his signature mask. Make a 3-minute drama about his last match before retirement, with English subtitles.",
            "Here's a sketch of a young female lighthouse keeper at the Cape of Good Hope in oilskin coat. Build a maritime mystery mini-drama, with English subtitles.",
            "Use this concept art of a cyberpunk Tokyo back-alley as the setting. Make a sci-fi noir mini-drama about a memory-broker, with English subtitles.",
            "I've attached a portrait of a Tibetan nun with prayer beads on a high mountain pass. Make a coming-of-age mini-drama about her pilgrimage, with English subtitles.",
            "Here's a watercolor of a 1920s Detroit assembly-line foreman in soot-stained coveralls. Make a workplace drama about his last day before the union strike, with English subtitles.",
            "Use this character ref of a Jamaican reggae singer with dreadlocks at a Trenchtown studio. Make a music-biopic mini-drama, with English subtitles.",
            "I've uploaded a sketch of an Ethiopian Olympic distance runner in qualifying-race kit. Make a sports drama about her hometown training, with English subtitles.",
            "Use this uploaded portrait of a Roma fortune-teller in carnival-era headscarf. Make a 1900s European-fairground mini-drama about a fugitive who recognizes his own future in her cards, with English subtitles.",
            "Here's a watercolor of a Quebecois fur-trapper at his river cabin. Make an 18th-century New-France mini-drama about his last winter before he's forced to choose sides in a colonial war, with English subtitles.",
            "I've attached a concept painting of an underwater Mediterranean shipwreck. Use it as the setting and make a thriller about a marine archaeologist racing rival treasure-hunters to a Roman amphora cache, with English subtitles.",
            "Use this character ref of a Lithuanian forest-witch in pagan ritual garb. Make a 16th-century Baltic mini-drama about her resistance against the new Catholic priest sent to convert her village, with English subtitles.",
            "Here's a portrait of a young female Algerian mountain-fighter in 1954 Maquis kit. Make a war drama about her sabotage mission in a French colonial supply depot, with English subtitles.",
            "I've uploaded a sketch of an elderly Chinese herbalist with his ginseng root collection. Make a 1930s Yunnan mini-drama about his refusal to sell a cure to a warlord whose son is dying, with English subtitles.",
            "Use this concept art of a Dust-Bowl Oklahoma farmhouse in 1934. Make a Depression-era family drama about a daughter who steals a tin of seeds to plant in California, with English subtitles.",
            "Here's a portrait of a Senegalese tirailleur in WWI Verdun trench kit. Make a war mini-drama about his correspondence with a French nurse he befriended during recovery, with English subtitles.",
            "I've attached a watercolor of a young Indonesian batik master at her wax-pot. Make a Javanese-court mini-drama about her secret pattern that encodes a sultan's enemy list, with English subtitles.",
            "Use this character ref of a Roman gladiatrix in arena armor. Make a 1st-century-Rome mini-drama about her refusal to kill the friend she trained with in the Ludus Magnus, with English subtitles.",
            "Here's a sketch of an Afghan rug-weaver girl at her loom. Make a 1980s Kabul-occupation mini-drama about a hidden message woven into her latest carpet bound for a foreign embassy, with English subtitles.",
            "I've uploaded a portrait of a 1920s Chicago bootlegger in pinstripe suit. Make a Prohibition-era crime drama about his rivalry with a federal agent who shares his Italian neighborhood, with English subtitles.",
            "Use this concept painting of a Babylonian ziggurat at sunset. Make a Mesopotamian mini-drama about a young scribe forging a tablet to save her brother from temple sacrifice, with English subtitles.",
            "Here's a portrait of a Khmer Rouge survivor as a contemporary woman. Make a Cambodian-recovery mini-drama about her return to Phnom Penh and confrontation with a former classmate now running a charity, with English subtitles.",
            "I've attached a sketch of a Norwegian Viking-era shieldmaiden in scale armor. Make a 9th-century Scandinavia mini-drama about her last shield-wall stand against an English garrison, with English subtitles.",
            "Use this character ref of a 1970s Tehran female poet at a clandestine reading. Make a pre-revolutionary mini-drama about her decision to publish under her dead brother's name to evade SAVAK, with English subtitles.",
            "Here's a watercolor of a Hong Kong neon-sign painter on a bamboo scaffold. Make a 1980s Kowloon mini-drama about his last commission before urban-renewal demolition, with English subtitles.",
            "I've uploaded a portrait of a young Ojibwe rice-harvester in a birchbark canoe. Make a Great-Lakes mini-drama about her granddaughter who returns home for the harvest after a decade in the city, with English subtitles.",
            "Use this concept art of a Soviet-era Leningrad communal apartment. Make a 1970s domestic mini-drama about three families crammed in shared kitchen who discover one of them is informing on the others, with English subtitles.",
            "Here's a sketch of a Caribbean obeah priestess in moonlit ceremony. Make a 19th-century plantation mini-drama about her rescue of a runaway slave through a blood-pact ritual, with English subtitles.",
            "I've attached a portrait of a young female Korean haenyeo diver in wetsuit and goggles. Make a Jeju-island mini-drama about her quitting the diving collective to study marine biology in Seoul, with English subtitles.",
            "Use this character ref of an Italian futurist painter in 1910s Milan. Make a pre-WWI avant-garde mini-drama about his rivalry with the woman painter who refuses to sign the manifesto, with English subtitles.",
            "Here's a portrait of a young female Iraqi marsh-Arab in a reed boat. Make a 1990s Mesopotamian-marshes mini-drama about her family fleeing the regime's drainage program, with English subtitles.",
        ],
    },
    {
        "slug": "intake_img_cr_music",
        "chain": ["IntakeImageAgent", "BriefEnricherAgent", "StoryAgent", "ScreenplayAgent", "KeyFrameAgent", "VideoAgent", "MusicAgent", "AudioMixAgent", "CompositorAgent"],
        "user_goals": [
            "Use this uploaded portrait of an Argentine bandoneón player in a smoky milonga. Make a tango-romance mini-drama with a bandoneón-and-violin score.",
            "I've attached a sketch of a Vietnamese đàn bầu monochord master at his low table. Make a period drama about his last student with a đàn bầu solo score.",
            "Here's a watercolor of a Mongolian throat-singer in deel robes on the open steppe. Make an animated drama about his journey through the steppes with a khoomei-and-morin-khuur score.",
            "Use this character ref of a young Turkish nay-flute player at a Sufi tekke. Make a Sufi-mystic mini-drama with a nay-and-frame-drum score.",
            "I've uploaded a portrait of a Romani violinist in a 1930s Budapest café. Make a coming-of-age drama with a Romani fiddle-and-cimbalom score.",
            "Here's a sketch of a Haitian voodoo drummer at a midnight ceremony. Make a supernatural mini-drama with a tanbou-and-conch-shell score.",
            "Use this concept art of a Korean court gayageum musician in Joseon-era costume. Make a court mini-drama with a gayageum-and-haegeum score.",
            "Use this uploaded portrait of an ancient-Greek lyre player on a temple step. Make a Hellenistic mini-drama about his rivalry with a court musician for the queen's patronage, with a lyre-and-aulos score.",
            "I've attached a sketch of a young Indian sitar master in a Mughal-era courtyard. Make a 17th-century mini-drama about his exile from the imperial court for a forbidden raga, with a sitar-and-tabla score.",
            "Here's a watercolor of a West African djembe player at a village ceremony. Make a coming-of-age mini-drama about his initiation into the master drummer lineage, with a djembe-and-balafon score.",
            "Use this character ref of a Russian balalaika street performer in a 1900s St. Petersburg square. Make a pre-revolution mini-drama about his bond with a runaway aristocrat's daughter, with a balalaika-and-accordion score.",
            "I've uploaded a portrait of a Persian santur master in a Qajar-era teahouse. Make a 19th-century Tehran mini-drama about his secret performance for a forbidden Sufi gathering, with a santur-and-tar score.",
            "Here's a sketch of a Caribbean steel-drum band leader on a Trinidad parade float. Make a 1950s carnival mini-drama about his rivalry with a rival pan-yard, with a steel-pan-and-soca score.",
            "Use this concept art of an Indonesian gamelan master at a Yogyakarta court. Make a Mataram-era mini-drama about his composition for a sultan's funeral, with a gamelan-gong-kebyar score.",
            "I've attached a portrait of a Spanish flamenco guitarist in 1930s Andalusia. Make a Civil-War-era mini-drama about his refusal to play for a fascist general, with a flamenco-guitar-and-cajón score.",
            "Here's a watercolor of a Welsh harpist in a Druid grove circle. Make a Celtic mini-drama about her invocation summoning a long-dead bard, with a Welsh-harp-and-strings score.",
            "Use this character ref of a Lakota cedar-flute player on a winter prairie. Make a Plains mini-drama about his vision-song for a wounded warrior, with a Native-American flute-and-frame-drum score.",
            "I've uploaded a portrait of an Egyptian oud master in a 1920s Cairo coffeehouse. Make an inter-war mini-drama about his composition for a banished king's homecoming, with an oud-and-qanun score.",
            "Here's a sketch of a Norwegian hardanger-fiddle player at a stave-church wedding. Make a 1880s village mini-drama about his folk-magic playing that summons a returning sailor, with a hardanger-fiddle-and-mouth-harp score.",
            "Use this concept art of a Mongolian morin-khuur player on horseback at sunset. Make a steppe mini-drama about his lament for a fallen wolf-companion, with a morin-khuur-and-throat-singing score.",
            "I've attached a portrait of an Aztec teponaztli-drum priest in jade ceremonial dress. Make a Tenochtitlán-era mini-drama about his last ceremony before the Spanish arrival, with a teponaztli-and-conch score.",
            "Here's a watercolor of a 1900s Parisian street accordionist on a Montmartre staircase. Make a Belle-Époque mini-drama about his improvised serenade for a runaway debutante, with an accordion-and-violin musette score.",
        ],
    },
    {
        "slug": "intake_img_cr_subtitle_music",
        "chain": ["IntakeImageAgent", "BriefEnricherAgent", "StoryAgent", "ScreenplayAgent", "KeyFrameAgent", "VideoAgent", "TranscriptionAgent", "MusicAgent", "AudioMixAgent", "CompositorAgent"],
        "user_goals": [
            "Use this uploaded portrait of a Moroccan rai singer in red djellaba. Make a music-drama about her smuggled album with English subtitles and a rai-and-darbuka score.",
            "I've attached a sketch of a young Cuban son-cubano singer at a 1959 Havana club. Make a revolution-era romance with English subtitles and a tres-and-claves score.",
            "Here's a watercolor of a Jewish klezmer clarinetist in a 1930s shtetl square. Make a coming-of-age drama with English subtitles and a klezmer clarinet-and-fiddle score.",
            "Use this character ref of a Brazilian capoeirista with a berimbau in a Bahia roda. Make an animated drama about her first championship with English subtitles and a berimbau-and-pandeiro score.",
            "I've uploaded a portrait of a Roma flamenco cantaora at a Sevilla tablao. Make a period drama about her last performance with English subtitles and a flamenco cante-and-guitar score.",
            "Here's a sketch of a Portuguese fado singer in 1930s Lisbon Bairro Alto. Make a Salazar-era mini-drama about her censored cabaret act, with English subtitles and a fado-guitarra-and-violão score.",
            "Use this character ref of an Iranian setar player in a Qajar-era court. Make a 19th-century Tehran mini-drama about her clandestine performance for the Shah's exiled daughter, with English subtitles and a setar-and-daf score.",
            "I've uploaded a portrait of an Andean panpipe player on a high-altitude pampa. Make a 1920s Bolivian mining mini-drama about his protest song for indigenous miners, with English subtitles and a quena-and-charango score.",
            "Here's a watercolor of a Hawaiian slack-key guitarist on a Maui porch. Make a 1970s Aloha-renaissance mini-drama about her career-defining chant composition, with English subtitles and a slack-key-and-ukulele score.",
            "Use this concept art of an Argentine tango bandoneón player in 1940s Buenos Aires. Make a Peronist-era mini-drama about his banned tango composition, with English subtitles and a bandoneón-and-violin score.",
            "I've attached a sketch of a Russian Cossack singer at a Don river ataman ceremony. Make a 19th-century mini-drama about his dirge for a fallen brother, with English subtitles and a Cossack-male-choir score.",
            "Here's a portrait of a Tamil-Nadu nadaswaram master at a temple festival. Make a 1950s Madras mini-drama about his rivalry with a foreign violinist, with English subtitles and a nadaswaram-and-tavil score.",
            "Use this character ref of a Brazilian samba-school drummer at a Mangueira rehearsal. Make a 1970s Rio mini-drama about his composition for the carnival's controversial protest theme, with English subtitles and a samba-batucada score.",
        ],
    },
    {
        "slug": "cr_subtitle_music",
        "chain": ["StoryAgent", "ScreenplayAgent", "KeyFrameAgent", "VideoAgent", "TranscriptionAgent", "MusicAgent", "AudioMixAgent", "CompositorAgent"],
        "user_goals": [
            "Make a 4-minute period drama about a Belle Époque Parisian magician's assistant who uncovers a real haunting on stage, with English subtitles and an eerie music-box-and-strings score.",
            "Create an animated thriller about a 1958 Bombay film noir detective chasing a missing starlet through the docks, with English subtitles and a noir saxophone-and-strings score.",
            "Make a coming-of-age short about a young Kenyan marathon hopeful training in the Rift Valley, with English subtitles and an uplifting orchestral score.",
            "Produce a 3-minute fantasy drama about a young Korean shaman bargaining with an ancient mountain spirit, with English subtitles and a shamanic gong-and-strings score.",
            "Make a romance mini-drama about a Welsh sheep-farmer's daughter and an English literature scholar trapped together by a snowstorm, with English subtitles and a Celtic harp-and-fiddle score.",
            "Create a period crime drama about a 1970s East Berlin underground graffiti artist evading the Stasi, with English subtitles and a krautrock electronic score.",
            "Make a sci-fi mini-drama about a cargo-ship engineer discovering an unauthorized passenger in the engine room, with English subtitles and a tense industrial-electronic score.",
            "Make a 4-minute period drama about an Italian partisan radio operator in 1944 Tuscany broadcasting coded messages to British supply drops, with English subtitles and a tense-strings-and-piano score.",
            "Create a Vietnamese boat-people refugee mini-drama about a teenage girl steering her family's fishing boat through a 1979 South China Sea storm, with English subtitles and an erhu-and-strings score.",
            "Make a 3-minute coming-of-age short about a Moroccan henna artist apprentice secretly painting her sister's hands the night before a forced wedding, with English subtitles and an oud-and-qanun score.",
            "Produce a period drama about a 1880s Tula samovar craftsman whose hand is crushed by a steam-press the day his son comes home with a railway-engineer's diploma, with English subtitles and a Russian-balalaika-and-strings score.",
            "Make a Greek shepherd mini-drama about an old man on Mount Pelion teaching his deaf grandson to read sheep behavior in a thunderstorm, with English subtitles and a clarinet-and-bouzouki folk score.",
            "Create a Brazilian samba composer mini-drama about a 1965 Rio favela musician who finishes his masterpiece the night before military police arrest him, with English subtitles and a samba-pagode score.",
            "Make a 4-minute period drama about a Persian rug weaver in 1870s Isfahan secretly weaving her own protest message into a carpet bound for a foreign embassy, with English subtitles and a santur-and-tar score.",
            "Produce a Norwegian fisherman mini-drama about a Lofoten cod-trawler captain refusing to abandon a frozen-in fishing partner during a winter storm, with English subtitles and a hardanger-fiddle-and-strings score.",
            "Make a 1930s Mexican muralist mini-drama about a Diego-Rivera-era apprentice painter whose secret panel of a striking miner is revealed at the inauguration, with English subtitles and a son-jarocho-and-strings score.",
            "Create a Caribbean sailor mini-drama about a 1950s Barbadian merchant-seaman who returns to a wife who's remarried, with English subtitles and a calypso-steel-pan score.",
            "Make a Tibetan monk coming-of-age mini-drama about a young novice tasked with delivering a dying lama's last text across a snowed-in mountain pass, with English subtitles and a Tibetan-bowls-and-throat-singing score.",
            "Produce a 1980s South African mining drama about a young Xhosa miner organizing a wildcat strike with a coded labor-song, with English subtitles and an mbira-and-vocal-harmony score.",
            "Make a contemporary Iceland glacier-guide mini-drama about a young woman leading a tourist into a crevasse rescue she can't perform alone, with English subtitles and a haunting Sigur-Rós-style ambient score.",
            "Create a 1900s Egyptian dragoman mini-drama about a Cairo bilingual translator caught between a British archaeologist and a local antiquities dealer, with English subtitles and an oud-and-strings score.",
            "Make an Indonesian wood-carver mini-drama about a Balinese mask-carver fulfilling a final commission for his estranged son's wedding troupe, with English subtitles and a Balinese-gamelan score.",
        ],
    },
    {
        "slug": "cr_bilingual_music",
        "chain": ["StoryAgent", "ScreenplayAgent", "KeyFrameAgent", "VideoAgent", "TranscriptionAgent", "TranslationAgent", "MusicAgent", "AudioMixAgent", "CompositorAgent"],
        "user_goals": [
            "Make a 4-minute Italian-American period drama about a 1920s Brooklyn opera prodigy auditioning at the Met, with English-Italian bilingual subtitles and a tenor-aria-and-orchestra score.",
            "Create a romance mini-drama about a Quebecois lumber-camp cook who falls for a French-Canadian poet, with English-French bilingual subtitles and a fiddle-and-accordion score.",
            "Make a coming-of-age short about a young Russian ballet student auditioning for the Mariinsky in 1975 Leningrad, with English-Russian bilingual subtitles and a Tchaikovsky-style strings score.",
            "Produce a 3-minute period drama about a young Filipino nurse migrating to 1960s Saudi Arabia, with English-Tagalog bilingual subtitles and a kundiman-and-kulintang score.",
            "Make a thriller mini-drama about a Korean defector smuggled across the DMZ in winter, with English-Korean bilingual subtitles and a tense haegeum-and-strings score.",
            "Create a romance period drama about a Mexican muralist's apprentice falling for a foreign journalist in 1940s Coyoacán, with English-Spanish bilingual subtitles and a son-jarocho-and-strings score.",
            "Make a 4-minute war drama about a young Greek partisan radio operator broadcasting BBC bulletins in 1943 Athens, with English-Greek bilingual subtitles and a bouzouki-and-strings score.",
            "Make a 1970s Iranian poet mini-drama about a Tehran café gathering broken up by SAVAK after a banned verse is recited, with English-Farsi bilingual subtitles and a santur-and-tar score.",
            "Create a Vietnamese village singer mini-drama about a 1965 Mekong-delta woman performing for both wartime sides without their knowing, with English-Vietnamese bilingual subtitles and a đàn-tranh-and-flute score.",
            "Make a Mongolian throat-singer coming-of-age mini-drama about a young herder's first competition at the Naadam festival, with English-Mongolian bilingual subtitles and a khoomei-and-morin-khuur score.",
            "Produce a Cuban son musician mini-drama about a 1958 Havana club's last night when a famous musician chooses to stay rather than leave for Miami, with English-Spanish bilingual subtitles and a tres-and-conga son-cubano score.",
            "Make a Hindi storyteller mini-drama about an old Banaras dastangoi performer mentoring his last student during the 1970s emergency, with English-Hindi bilingual subtitles and a sarangi-and-tabla score.",
            "Create a Polish jazz musician mini-drama about a 1960s Krakow saxophonist secretly recording sessions for Radio Free Europe, with English-Polish bilingual subtitles and a cool-jazz-quartet score.",
            "Make a Ukrainian folk dancer mini-drama about a 1933 Holodomor village schoolteacher organizing a festival in defiance of Soviet quotas, with English-Ukrainian bilingual subtitles and a bandura-and-violin score.",
            "Produce a Tamil weaver mini-drama about a 1920s Madras silk-weaver organizing a workers' strike against a British mill, with English-Tamil bilingual subtitles and a nadaswaram-and-mridangam score.",
            "Make a Senegalese griot mini-drama about a 1990s Dakar village historian whose memorized lineage saves a family from a colonial-era property dispute, with English-Wolof bilingual subtitles and a kora-and-balafon score.",
            "Create an Andean panpipe mini-drama about a 1980s Bolivian Aymara quena master refusing to play for a foreign mining executive, with English-Quechua bilingual subtitles and a quena-and-charango score.",
            "Make a Yemeni oud poet mini-drama about a 1950s Aden coffee-house musician whose verses become a resistance anthem against British rule, with English-Arabic bilingual subtitles and an oud-and-qanun score.",
            "Produce an Indonesian gamelan mini-drama about a 1965 Yogyakarta court orchestra leader caught between rival sultans during the political upheaval, with English-Indonesian bilingual subtitles and a Javanese-gamelan score.",
            "Make a Mongolian dancer mini-drama about a Chinggis-era court contortionist performing the Khan's death-rite, with English-Mongolian bilingual subtitles and a horsehair-fiddle-and-throat-singing score.",
            "Create a Chinese opera singer mini-drama about a 1930s Shanghai dan performer whose last role veils a secret message to her exiled lover, with English-Chinese bilingual subtitles and a Peking-opera jinghu-and-yueqin score.",
            "Make a Norwegian skald mini-drama about a Viking-era court poet improvising a saga the night a foreign envoy is poisoned, with English-Old-Norse bilingual subtitles and a tagelharpa-and-frame-drum score.",
        ],
    },
    {
        "slug": "vid_analysis_cr_music",
        "chain": ["IntakeVideoAgent", "VideoAnalysisAgent", "StoryAgent", "ScreenplayAgent", "KeyFrameAgent", "VideoAgent", "MusicAgent", "AudioMixAgent", "CompositorAgent"],
        "user_goals": [
            "Take this 4-minute clip of a vintage Bollywood musical. Analyze its emotional pacing and produce a new animated mini-drama about a young female playback singer's rise to fame, with a Bollywood orchestra score.",
            "Here's a 3-minute reel from a Korean revenge drama. Study its cold-tension build and produce a new animated mini-drama about a corrupt CEO and his estranged daughter, with a tense piano-and-strings score.",
            "I've uploaded a 5-minute clip from a 1970s blaxploitation film. Analyze its style and produce a new animated mini-drama about a 1970s Detroit private investigator, with a wah-wah-funk score.",
            "Take this 90-second clip of an Argentine tango competition. Read its passion and produce a new animated romance mini-drama about a tango partner who returns after fifteen years, with a bandoneón-and-violin score.",
            "Here's a 4-minute documentary segment about Maori haka warriors. Analyze its raw energy and produce a new animated mini-drama about a young warrior facing his first ceremony, with a haka-and-poi score.",
            "Take this 3-minute clip of a modernist ballet rehearsal. Study its severity and produce a new animated mini-drama about a choreographer's last work before her diagnosis, with a Ravel-style impressionist score.",
            "I've uploaded a 6-minute Cuban son-cubano festival recording. Analyze its rhythm and produce a new animated mini-drama about a Havana club's last night before nationalization in 1960, with a son-cubano-and-tres score.",
            "Here's a 90-second clip of a Sufi whirling-dervish ceremony. Read its spiritual focus and produce a new animated mini-drama about a young dervish's first khilwa retreat, with a ney-and-daf score.",
            "Take this 4-minute clip of a French New Wave film. Read its handheld restlessness and produce a new animated mini-drama about a 1968 Sorbonne student who falls for a fellow protester she suspects is a police informant, with a yé-yé pop score.",
            "Here's a 3-minute Mexican lucha libre match clip. Analyze its theatricality and produce a new animated mini-drama about a young masked wrestler whose mask is stolen the night before his retirement bout, with a mariachi-and-electric-guitar score.",
            "I've uploaded a 5-minute documentary segment on Egyptian belly dance. Study its center-of-gravity precision and produce a new animated mini-drama about a 1950s Cairo nightclub dancer hiding her connection to the resistance, with an oud-and-tabla score.",
            "Take this 90-second Hindustani classical concert clip. Read its slow-build raga structure and produce a new animated mini-drama about a young woman secretly learning a forbidden masculine raga from her dying father, with a sitar-and-tabla score.",
            "Here's a 4-minute Senegalese griot performance recording. Analyze its oral-history rhythm and produce a new animated mini-drama about a village's last apprentice griot whose memory is failing, with a kora-and-balafon score.",
            "I've attached a 3-minute Russian ballet rehearsal clip. Study its discipline-under-pressure mood and produce a new animated mini-drama about a Bolshoi soloist plotting her defection from a 1980s tour in Vienna, with a strings-and-piano score.",
            "Take this 5-minute Cuban son festival recording. Analyze its layered polyrhythm and produce a new animated mini-drama about a Havana club bandleader on the night the revolutionary government nationalizes his venue, with a tres-and-conga son-cubano score.",
            "Here's a 90-second Vietnamese water-puppet show clip. Read its mythic scale and produce a new animated mini-drama about a young puppeteer reviving a forbidden ancient legend her uncle was executed for staging, with an đàn-tranh-and-flute score.",
            "I've uploaded a 4-minute Tuareg desert music documentary. Study its lonesome trance and produce a new animated mini-drama about a trans-Saharan caravan trader's daughter who picks up her dead father's guitar, with a desert-blues electric-guitar score.",
            "Take this 3-minute Korean pansori epic-singer clip. Read its operatic stamina and produce a new animated mini-drama about a Joseon-court pansori singer mocking the chancellor through coded lyrics, with a pansori buk-drum score.",
            "Here's a 4-minute Argentine tango milonga recording. Analyze its grief-edged eroticism and produce a new animated mini-drama about a 1930s Buenos Aires couple's last dance before he leaves to fight in a foreign war, with a bandoneón-and-violin score.",
            "I've attached a 3-minute Hawaiian slack-key guitar performance. Study its Pacific calm and produce a new animated mini-drama about a young Oahu musician torn between staying with his family and signing with a Mainland label, with a slack-key-and-ukulele score.",
            "Take this 5-minute Spanish flamenco tablao show clip. Read its raw catharsis and produce a new animated mini-drama about a Roma cantaora exiled from her family's flamenco lineage for marrying outside the Romani community, with a flamenco cante-and-guitar score.",
            "Here's a 90-second Mongolian throat-singing performance. Analyze its overtone harmonics and produce a new animated mini-drama about a young steppe warrior chanting his ancestors' praise-songs across a snow-covered battlefield, with a khoomei-and-morin-khuur score.",
            "I've uploaded a 4-minute Norwegian fjord folk-music festival reel. Study its midnight-sun eeriness and produce a new animated mini-drama about a village fiddler whose final harvest-festival performance summons something he didn't expect, with a nyckelharpa-and-frame-drum score.",
            "Take this 3-minute Brazilian bossa nova jazz club recording. Read its 1962 Rio sophistication and produce a new animated mini-drama about a young guitarist navigating the romance between his American producer and her engaged Brazilian songwriter, with a bossa-nova-and-soft-jazz score.",
            "Here's a 4-minute Persian dastan storyteller performance. Analyze its epic-scale narration and produce a new animated mini-drama based on a Shahnameh warrior's exile through ancient Khorasan, with a santur-and-tar score.",
            "I've attached a 3-minute Greek rebetiko taverna performance. Study its dockside dissident energy and produce a new animated mini-drama about a 1920s Piraeus dockworker organizing a strike under the cover of a smoky rebetiko bar, with a bouzouki-and-baglama score.",
            "Take this 90-second Thai khon dance theater clip. Read its sculptural masked precision and produce a new animated mini-drama retelling a court-intrigue chapter from the Ramakien, with a piphat ensemble score.",
            "Here's a 4-minute Inuit drum-dance ceremony recording. Analyze its slow communal trance and produce a new animated mini-drama about an Arctic shaman undertaking a vision-quest journey to find a missing village child, with a frame-drum-and-throat-singing score.",
            "I've uploaded a 3-minute Andean panpipe festival video. Study its sky-altitude solemnity and produce a new animated mini-drama about a high-altitude village's water-rights conflict with a copper-mining concession, with a quena-and-charango score.",
            "Take this 5-minute Yemeni oud music performance. Read its melancholy modality and produce a new animated mini-drama about a 1970s Sana'a poet driven into exile after his verses are read at a banned political rally, with an oud-and-qanun score.",
        ],
    },
    # ── topup: existing complex Style+Extend+Music (training avail ~20, target ~33) ──
    {
        "slug": "complex_style_extend_music_topup",
        "chain": ["IntakeVideoAgent", "StyleTransferAgent", "VideoExtendAgent", "MusicAgent", "AudioMixAgent", "CompositorAgent"],
        "user_goals": [
            "First convert this 8-second cathedral-organ-recital clip to a stained-glass animated style, then extend the chord-resolution by 18 seconds, and finally add a Bach-fugue-style organ score.",
            "Take this 7-second 1990s arcade-game footage, restyle it as a vector pixel-art aesthetic, then extend the boss-fight finale by 20 seconds, and layer in a chiptune track.",
            "Convert this 10-second mountain-summit drone shot to a Caspar David Friedrich oil-painting style, then extend it to 35 seconds, and overlay a romantic-era piano solo.",
            "Take this 6-second café-window clip, restyle it as a Hopper Nighthawks aesthetic, then extend the patron-leaning-on-counter moment by 18 seconds, and add a melancholy alto-saxophone-and-piano score.",
            "Restyle this 9-second street-tango couple clip as a black-and-white photo-essay aesthetic, then extend the dip-and-hold moment by 15 seconds, and add a bandoneón-and-violin tango score.",
            "Convert this 8-second Buddhist-temple bell-ringing clip to a Hokusai woodblock style, then extend the bronze-resonance moment by 20 seconds, and add a shakuhachi-and-bell drone score.",
            "Take this 5-second fencing-touche moment, restyle it as a charcoal-sketch animation, then extend the riposte by 16 seconds in slow-motion, and add an orchestral-strings duel score.",
            "First restyle this 10-second mariachi-band performance to a 1940s Mexican-poster lithograph aesthetic, then extend the trumpet-solo by 14 seconds, and add a mariachi-fanfare score.",
            "Convert this 7-second campfire-storytelling clip to a folk-paper-cut-out style, then extend the child-leaning-in moment by 12 seconds, and add a soft fingerpicked-acoustic-guitar score.",
            "Take this 8-second Caribbean fisherman casting-a-net moment, restyle it as a Gauguin Tahitian-painting aesthetic, then extend the net-arc by 14 seconds, and add a steel-drum-and-conch-shell score.",
            "First restyle this 6-second falconry-hood-removal moment as a Persian-miniature painting, then extend the eye-meeting moment by 18 seconds, and add a santur-and-tar score.",
            "Convert this 9-second train-station-clock close-up to a German-Expressionist film style, then extend the second-hand sweeping by 22 seconds, and add a tense brass-and-strings noir score.",
            "Take this 8-second Polynesian outrigger-canoe-launch moment, restyle it as a contemporary Polynesian tapa-cloth pattern aesthetic, then extend the wave-crossing by 18 seconds, and add a pahu-drum-and-conch score.",
        ],
    },
    # ── topup: existing complex imgref+cr+Extend (training avail ~30, target ~35) ──
    {
        "slug": "complex_imgref_cr_extend_topup",
        "chain": ["IntakeImageAgent", "BriefEnricherAgent", "StoryAgent", "ScreenplayAgent", "KeyFrameAgent", "VideoAgent", "VideoExtendAgent", "CompositorAgent"],
        "user_goals": [
            "Use this uploaded portrait of a young Bedouin caravan leader. Make a Sahara crossing mini-drama about her last journey before settling in a new oasis, extend the dust-storm-passing-by moment by 14 seconds.",
            "I've attached a watercolor of a 1960s Saigon street-photographer with his Leica. Make a Vietnam War-era mini-drama about his exposure of a corrupt official, extend the darkroom-developing reveal moment by 12 seconds.",
            "Here's a concept painting of a Soviet collective-farm matriarch in headscarf. Make a 1950s Ukraine drama about her hidden grain stash during the famine, extend the cellar-discovery moment by 15 seconds.",
            "Use this character ref of a 19th-century Japanese geisha apprentice. Make a Meiji-era mini-drama about her debut performance for a foreign diplomat, extend the kanzashi-pin-falling moment by 10 seconds.",
            "I've uploaded a digital painting of a Haitian voodoo priestess in ceremonial white. Make a 1791 Saint-Domingue revolution mini-drama about her invocation that sparks the uprising, extend the candle-circle ignition moment by 14 seconds.",
            "Use this uploaded portrait of a young Sami reindeer-herder woman bundled in winter wool. Make a 1920s Norwegian-Lapland mini-drama about her last solo migration before the family settles, extend the lone-reindeer-glance moment by 13 seconds.",
            "I've attached a sketch of a 1920s Brooklyn dockworker in newsboy cap. Make a Prohibition-era mini-drama about his refusal to unload a contraband shipment, extend the silent-crew-stand moment by 12 seconds.",
        ],
    },
    # ── topup: existing complex VA+cr+sub (training avail ~30, target ~35) ──
    {
        "slug": "complex_vid_analysis_cr_subtitle_topup",
        "chain": ["IntakeVideoAgent", "VideoAnalysisAgent", "StoryAgent", "ScreenplayAgent", "KeyFrameAgent", "VideoAgent", "TranscriptionAgent", "CompositorAgent"],
        "user_goals": [
            "Take this 4-minute Norwegian Arctic-expedition documentary. Analyze its silent-cold tension and produce a new animated mini-drama about a polar explorer hiding a deadly diary entry from his crew, with English subtitles burned in.",
            "Here's a 3-minute clip from a 1950s American film-noir trailer. Read its rain-soaked moral ambiguity and produce a new animated mini-drama about a corrupt tax-investigator falling for the widow he's auditing, with English subtitles.",
            "I've uploaded a 5-minute Egyptian melodrama segment. Study its emotional excess and produce a new animated mini-drama about a Cairo flautist torn between his wife and the visiting Italian diva, with English subtitles.",
            "Take this 90-second clip from a Bollywood dance-number scene. Analyze its joyful choreography and produce a new animated mini-drama about a wedding-band drummer who falls for the bride's sister, with English subtitles.",
            "Here's a 4-minute Polish 1960s art-house drama. Read its existential weight and produce a new animated mini-drama about a Warsaw chess prodigy abandoning his career to chase a defected lover, with English subtitles.",
        ],
    },
    # ── topup: existing complex Style+Extend pure (training avail ~20, target ~32) ──
    {
        "slug": "complex_style_extend_topup",
        "chain": ["IntakeVideoAgent", "VideoExtendAgent", "StyleTransferAgent", "done"],
        "user_goals": [
            "Extend this 5-second clip of a child blowing dandelion seeds by 20 seconds, then convert the whole thing into a Studio Ghibli watercolor.",
            "Take this 10-second clip of waves on a basalt beach and extend it to 35 seconds, then restyle as a Sōtatsu Edo-era ink-wash painting.",
            "Extend this 8-second neon-arcade interior clip by 18 seconds and convert it into a 1980s Hong Kong cyberpunk aesthetic.",
            "Take this 6-second clip of a horse rearing at sunset and extend it to 25 seconds, then restyle as a Frederic Remington Western oil painting.",
            "Extend this 5-second cellist-tuning moment by 22 seconds, then transform it into a Vermeer-style chiaroscuro oil painting.",
            "Take this 7-second monk-sweeping-temple-courtyard footage and stretch it to 30 seconds, then restyle as a traditional Korean ink-wash painting.",
            "Extend this 9-second blacksmith-hammering scene by 18 seconds and convert it into a 1930s WPA-mural lithograph aesthetic.",
            "Take this 6-second alpine-shepherdess-with-flock clip and extend it to 28 seconds, then restyle as a Heidi-era Swiss children's-book illustration.",
            "Extend this 8-second street-musician violin clip by 15 seconds and convert it into a Marc Chagall stained-glass aesthetic.",
            "Take this 5-second clip of a kid skateboarding off a ramp and extend it to 22 seconds, then restyle as a 2000s graffiti-skate-magazine aesthetic.",
            "Extend this 10-second hawk-circling-above-canyon clip by 25 seconds, then transform it into a Native American ledger-art style.",
            "Take this 7-second clip of a glass-blower shaping a bulb and stretch it to 28 seconds, then restyle as a Murano-Renaissance illustration.",
        ],
    },
    # ── topup: existing complex Style+Extend+sub (training avail ~20, target ~32) ──
    {
        "slug": "complex_style_extend_subtitle_topup",
        "chain": ["IntakeVideoAgent", "VideoExtendAgent", "StyleTransferAgent", "TranscriptionAgent", "CompositorAgent"],
        "user_goals": [
            "Extend this 8-second jury-foreperson-reading-verdict moment by 18 seconds, restyle it as a courtroom-sketch animation, and burn in English subtitles.",
            "Take this 6-second small-town-mayor speech moment and extend it to 25 seconds, convert to a 1950s pulp-magazine illustration style, then add English subtitles.",
            "Extend this 7-second lecture-hall heckling exchange by 20 seconds, restyle into a Soviet-era poster aesthetic, and burn in English subtitles.",
            "Take this 9-second hospital-ICU bedside conversation and extend it to 28 seconds, convert to a Edward Hopper realist painting style, then add English subtitles.",
            "Extend this 5-second auctioneer-gavel-drop moment by 16 seconds, restyle it as a Norman Rockwell Saturday Evening Post illustration, and burn in English subtitles.",
            "Take this 8-second talk-show interview moment and extend it to 26 seconds, convert it to a Roy Lichtenstein pop-art aesthetic, then add English subtitles.",
            "Extend this 6-second debate-stage cross-examination by 22 seconds, restyle as a 1930s Mexican muralist aesthetic, and burn in English subtitles.",
            "Take this 7-second karaoke-bar singing moment and extend it to 24 seconds, convert to a 1980s Tokyo neon-lit illustration style, then add English subtitles.",
            "Extend this 10-second street-corner protest speech by 18 seconds, restyle it as a Banksy stencil aesthetic, and burn in English subtitles.",
            "Take this 8-second backyard-barbecue toast moment and extend it to 28 seconds, convert it to a Suburban-Americana watercolor, then add English subtitles.",
            "Extend this 6-second bedtime-storytelling moment by 20 seconds, restyle it as a Beatrix Potter children's-book illustration, and burn in English subtitles.",
            "Take this 9-second couples'-therapy session breakthrough moment and extend it to 26 seconds, convert it to a graphic-novel ink-wash style, then add English subtitles.",
        ],
    },
    # ── topup: existing highlight + Music (training avail ~20, target ~30) ──
    {
        "slug": "highlight_music_topup",
        "chain": ["IntakeVideoAgent", "VideoAnalysisAgent", "HighlightAgent", "MusicAgent", "AudioMixAgent", "CompositorAgent"],
        "user_goals": [
            "I've uploaded an 80-minute amateur-rugby tournament. Cut me a highlight reel of the best plays and add a triumphant Welsh-male-choir score.",
            "Here's a 90-minute drag-show pageant recording. Pull a highlight reel of the showstopper numbers with a glittery dance-pop score.",
            "Take this 60-minute kids' karate-belt-test ceremony and cut a highlight reel of the best performances with an inspiring orchestral score.",
            "I have a 2-hour breakdance battle. Cut me a highlight reel of the cleanest power-moves and layer in a hip-hop-and-funk score.",
            "Here's a 45-minute amateur-archery-tournament recording. Pull a highlight reel of the closest bullseyes with a meditative Japanese-flute score.",
            "I've uploaded a 90-minute Highland-games footage. Cut me a highlight reel of the caber-toss attempts with a bagpipe-and-drum score.",
            "Take this 60-minute swing-dance social. Pull a highlight reel of the wildest Lindy hops with a 1940s big-band score.",
            "Here's a 75-minute kids'-spelling-bee final. Cut a highlight reel of the dramatic-elimination moments with a charming tinkling-piano score.",
            "I've recorded a 50-minute rodeo-clown show. Cut a highlight reel of the funniest bull-distraction moments with a circus-brass score.",
            "Take this 90-minute drone-racing championship. Pull a highlight reel of the closest finishes with an electronic synthwave score.",
        ],
    },
    {
        "slug": "intake_img_cr_extend_music",
        "chain": ["IntakeImageAgent", "BriefEnricherAgent", "StoryAgent", "ScreenplayAgent", "KeyFrameAgent", "VideoAgent", "VideoExtendAgent", "MusicAgent", "AudioMixAgent", "CompositorAgent"],
        "user_goals": [
            "Use this uploaded portrait of a Cossack horseman in 1800s steppe regalia. Make an action mini-drama about his last raid before retiring, extend the cavalry charge moment by 12 seconds, and add a thundering brass-and-strings score.",
            "I've attached a watercolor of a Maori tā moko warrior with chest tattoos. Make a coming-of-age mini-drama about his first hunt, extend the prey-confrontation moment by 10 seconds, and add a bone-flute-and-frame-drum score.",
            "Here's a digital painting of a Norse völva seer with rune sticks. Make a Viking-era mini-drama about her prophecy that splits a clan, extend the prophecy-vision sequence by 12 seconds, and add a bowed-tagelharpa-and-throat-singing score.",
            "Use this concept art of a Berber mountain horseman in indigo robes. Make a desert mini-drama about his last journey across the Sahara, extend the dust-storm scene by 15 seconds, and add an oud-and-bendir score.",
            "I've uploaded a portrait of a Manchu princess in elaborate court regalia. Make a Qing-dynasty palace mini-drama about her secret correspondence with a Russian envoy, extend the secret-message-burning moment by 10 seconds, and add a yangqin-and-erhu score.",
            "Here's a sketch of a young Ainu fisher woman from Hokkaido in winter robes. Make a coming-of-age mini-drama about her first solo ice-fishing season, extend the bear-encounter moment by 12 seconds, and add a tonkori-and-mukkuri score.",
            "Use this character ref of an Andean condor-keeper in a Paracas weave. Make a mini-drama about her last solitary year on the high plateau, extend the condor-flight finale by 18 seconds, and add a quena-and-charango score.",
            "I've attached a portrait of a young Mayan jaguar-priestess in jade jewelry. Make a Classical-period mini-drama about her ascending rite, extend the temple-summit moment by 12 seconds, and add a teponaztli-and-conch-shell score.",
            "Use this uploaded portrait of a 1920s Harlem jazz trumpeter in a sharkskin suit. Make a music-biopic mini-drama about his last performance at the Cotton Club before crossing the colour line. Extend the spotlight-cuts-out moment by 12 seconds, and add a Duke-Ellington-style swing score.",
            "I've uploaded a sketch of a Sami reindeer-herder woman in winter regalia. Make a coming-of-age mini-drama about her first solo migration across the Norwegian Lapland tundra. Extend the lone-wolf-encounter moment by 14 seconds, and add a joik-and-frame-drum score.",
            "Here's a watercolor of a young Iberian falconer with his hooded peregrine. Make a 16th-century Spanish-court mini-drama about his refusal to surrender his bird to the Inquisition. Extend the unhooding-on-the-cliff moment by 12 seconds, and add a vihuela-and-dulzaina score.",
            "Use this character ref of a Dutch Golden Age portraitist with paint-stained sleeves. Make a 1660s Amsterdam mini-drama about his sitter who reveals she's pregnant by the man who paid for the portrait. Extend the brush-pause-mid-stroke moment by 10 seconds, and add a viola-da-gamba-and-harpsichord score.",
            "I've attached a portrait of a Bedouin oud-player in a desert-tent encampment. Make a 1930s Hejaz mini-drama about his caravan crossing a contested border with a stowaway British officer. Extend the dawn-on-the-dunes moment by 15 seconds, and add an oud-and-rababa score.",
            "Use this concept art of an Inca chasqui-runner in mountain-relay regalia. Make a pre-Columbian mini-drama about her last sprint across Andean rope-bridges to deliver word of an invading Spanish column. Extend the bridge-crossing moment by 12 seconds, and add a quena-and-tinya score.",
            "Here's a sketch of a Geisha apprentice in winter Kyoto. Make a Meiji-era mini-drama about her final rite of passage performance for a foreign diplomat. Extend the kanzashi-falling moment by 10 seconds, and add a koto-and-shamisen score.",
            "I've uploaded a portrait of a young Maasai morani warrior with his ochre body-paint. Make a coming-of-age mini-drama about his first lion-tracking solo. Extend the savannah-confrontation moment by 14 seconds, and add a kudu-horn-and-drum score.",
            "Use this character ref of an Ottoman miniaturist hunched over a folio. Make a 1590s Topkapi-court mini-drama about his discovery of a heretical detail painted into a royal manuscript. Extend the magnifying-loupe-zoom moment by 10 seconds, and add a ney-and-kanun score.",
            "Here's a digital painting of a Inuit kayak hunter in the iceberg fields. Make an Arctic mini-drama about his family awaiting his return through a closing storm. Extend the thawing-ice-crack moment by 14 seconds, and add a throat-singing-and-water-drum score.",
            "I've attached a watercolor of a Sicilian volcano-quarry worker. Make a 1908 Etna eruption mini-drama about his rescue of his foreman's daughter. Extend the lava-flow-glow moment by 15 seconds, and add a folk-mandolin-and-cello score.",
            "Use this uploaded portrait of a young female Chinese pirate captain in Ming-era armor. Make a high-seas mini-drama about her last raid against a treasure junk that turns out to be carrying her brother. Extend the boarding-jump moment by 12 seconds, and add a guzheng-and-suona score.",
            "Here's a sketch of a Persian apothecary measuring saffron in a Qajar-era pharmacy. Make a 19th-century Tehran mini-drama about her secret prescription that may have poisoned the Shah. Extend the mortar-and-pestle moment by 10 seconds, and add a santur-and-tar score.",
            "I've uploaded concept art of a Polynesian wayfinder navigating by stars on a double-hulled canoe. Make a pre-contact Pacific mini-drama about her crossing to a new island with three reluctant elders aboard. Extend the dawn-landfall moment by 16 seconds, and add a pahu-and-ipu score.",
            "Use this character ref of a Roma fortune-teller in 1900s carnival garb. Make a turn-of-the-century mini-drama about her reading the cards for a fugitive who recognizes himself in the deck. Extend the card-flip moment by 10 seconds, and add a Romani fiddle-and-cimbalom score.",
            "Here's a portrait of a Chinese emperor's eunuch official in Ming court robes. Make a Forbidden-City mini-drama about his attempt to smuggle a child heir out of the palace before a coup. Extend the lantern-corridor escape moment by 12 seconds, and add a guzheng-and-pipa score.",
            "I've attached a sketch of a young Welsh coal-mining canary keeper. Make a 1880s Aberdare mini-drama about her warning the men below ground when the canary stops singing. Extend the bird-falls-silent moment by 10 seconds, and add a Welsh-harp-and-strings score.",
            "Use this concept art of a Tibetan monk-painter completing a sand mandala. Make a Himalayan mini-drama about his decision to destroy his masterwork a day early to save his village. Extend the wind-blowing-the-sand moment by 14 seconds, and add a Tibetan-bowl-and-chant score.",
            "Use this uploaded portrait of an aged Pacific-island fire-dancer in coral and lava-stone jewelry. Make a 1920s Polynesia mini-drama about her last torch-routine before colonial authorities ban the ritual, extend the embers-fading moment by 12 seconds, and add a pahu-and-conch score.",
            "I've attached a watercolor of an 1880s Vienna patisserie chef in starched whites at her marble counter. Make a Belle-Époque mini-drama about her secret recipe stolen by a rival before the imperial-court tasting, extend the cake-being-cut moment by 10 seconds, and add a Strauss-waltz-and-piano score.",
        ],
    },
    {
        # GRPO data is missing this shape entirely; SFT has it.
        # Add as gap-fill so both formats can hit target.
        "slug": "vid_analysis_cr",
        "chain": ["IntakeVideoAgent", "VideoAnalysisAgent", "StoryAgent", "ScreenplayAgent", "KeyFrameAgent", "VideoAgent", "CompositorAgent"],
        "user_goals": [
            "Take this 4-minute clip of a finished Brazilian telenovela pilot. Analyze its dramatic pacing and produce a wholly new animated mini-drama in the same emotional register about a small-town nurse uncovering a hospital scandal.",
            "Here's a 90-second reel from a Hong Kong wuxia film. Study its choreography and produce a new animated mini-drama about a young swordswoman avenging her teacher across three provinces.",
            "I've uploaded a 5-minute scene from a Russian war film. Analyze its bleak realism and produce a new animated mini-drama about a Soviet field-radio operator pinned down on the eastern front.",
            "Take this 3-minute clip from a 1970s Italian giallo thriller. Read its lurid mood and produce a new animated mystery mini-drama about a Milan model investigating her sister's disappearance.",
            "Here's a 4-minute reel from a vintage Bombay detective serial. Analyze its visual rhythm and produce a new animated mini-drama about a 1960s Calcutta journalist exposing a tea-plantation conspiracy.",
            "Take this 90-second clip of a Chinese revolutionary opera. Study its theatricality and produce a new animated mini-drama about a young rebel actress smuggling messages between troupes.",
            "Take this 4-minute Cantonese opera performance. Analyze its theatrical conventions and produce a new animated mini-drama about a young triad enforcer torn between his oath to the brotherhood and saving his estranged sister.",
            "Here's a 90-second clip from a Civil War battle reenactment. Read its claustrophobic chaos and produce a new animated mini-drama about a Confederate deserter trying to cross the Appalachians on foot to find his pregnant wife.",
            "I've uploaded a 5-minute clip from a 1968 Polish jazz festival. Study its defiance under censorship and produce a new animated mini-drama about a saxophone player smuggling banned manuscripts inside his instrument case.",
            "Take this 4-minute Bollywood wedding documentary. Analyze its multi-day ritual structure and produce a new animated mini-drama about a 1970s Mumbai bride who runs away the night before her arranged ceremony.",
            "Here's a 3-minute clip of restored Soviet cosmonaut training footage. Read its institutional rigor and produce a new animated mini-drama about two cosmonaut candidates competing for the same Vostok seat.",
            "I've uploaded a 4-minute Australian outback survival documentary. Analyze its empty-landscape pacing and produce a new animated mini-drama about an Aboriginal tracker hired to find a disappeared mining heir.",
            "Take this 5-minute Egyptian pyramid documentary. Read its sense of buried history and produce a new animated mini-drama about a 1920s archaeologist convinced she's uncovering a tomb that doesn't want to be found.",
            "Here's a 90-second clip of a New Orleans jazz funeral procession. Study its dirge-to-celebration arc and produce a new animated mini-drama about a blues guitarist mourning the band-mate he abandoned twenty years ago.",
            "I've attached a 4-minute clip of a Korean War MASH-unit drama. Analyze its dark-humor pacing and produce a new animated mini-drama about a battlefield surgeon hiding a romance with the camp's Korean translator.",
            "Take this 3-minute Peruvian Andes climbing documentary. Read its altitude-sickness fatigue and produce a new animated mini-drama about an indigenous porter who realizes the expedition leader is willing to sacrifice him.",
            "Here's a 4-minute kabuki theater rehearsal recording. Study its ritualized gesture and produce a new animated mini-drama about an Edo-period onnagata performer who breaks character on opening night to reveal a poisoning plot.",
            "I've uploaded a 5-minute Tibetan monastery ceremony video. Analyze its meditative slowness and produce a new animated mini-drama about a young monk tasked with bringing a dying lama's last vision down the mountain to his successor.",
            "Take this 3-minute clip from a 1990s Berlin reunification documentary. Read its uncertain euphoria and produce a new animated mini-drama about an East and a West Berliner who realize they're falling for each other across the demolished Wall.",
            "Here's a 90-second Argentine gaucho rodeo clip. Study its physical brutality and produce a new animated mini-drama about a ranch hand plotting revenge against the corrupt landowner who fired his father.",
            "I've attached a 4-minute Antarctic research-station documentary. Analyze its claustrophobic isolation and produce a new animated mini-drama about a glaciologist whose grip on reality fractures during the polar night.",
            "Take this 3-minute clip from a Vietnam jungle-warfare documentary. Read its tense quiet and produce a new animated mini-drama about a Hmong scout caught between his villagers and the U.S. unit he's supposed to lead.",
            "Here's a 5-minute documentary on Mongolian eagle-hunting tradition. Study its stillness-before-flight and produce a new animated mini-drama about a young huntress refusing to give up her aging eagle when the elders demand it.",
            "I've uploaded a 4-minute archive reel of New York harbor in 1908. Analyze its immigrant-arrival energy and produce a new animated mini-drama about an Italian dockhand secretly running a translation racket at Ellis Island.",
            "Take this 3-minute alpine-ski-racing competition recording. Read its kinetic precision and produce a new animated mini-drama about an Olympic hopeful sabotaged by a teammate the night before her qualifying run.",
            "Here's a 90-second Pacific-island volcano-eruption documentary. Study its slow-rising menace and produce a new animated mini-drama about a chief who must convince a skeptical anthropologist that her grandmother's prophecy is about to come true.",
            "I've attached a 4-minute Moroccan medina spice-market documentary. Analyze its sensory overload and produce a new animated mini-drama about a young merchant's daughter who overhears a poisoning plot in three languages.",
            "Take this 3-minute Yorkshire moor mystery TV pilot. Read its atmospheric dread and produce a new animated mini-drama about a Victorian governess who realizes the children she teaches may have killed their mother.",
            "Here's a 5-minute Brazilian rainforest expedition reel. Study its damp-canopy claustrophobia and produce a new animated mini-drama about a biologist who finds a lost researcher's notebook and starts repeating his footsteps.",
            "I've uploaded a 4-minute clip of a Greek island fishing village documentary. Analyze its weathered patience and produce a new animated mini-drama about an octopus hunter who returns one day with a ring he didn't have when he left.",
            "Take this 3-minute Tibetan-plateau yak-herders documentary. Read its windswept solitude and produce a new animated mini-drama about a young herder pursuing a yak-rustler band across two contested borders.",
            "Here's a 4-minute restored 1880s London foggy-night silent reel. Study its fog-and-gaslight noir mood and produce a new animated mini-drama about a Whitechapel detective hunting the copycat killer who's mimicking case files only the police should have.",
        ],
    },
    # ── topup: existing storytelling +Ambience (no imgref, training avail ~20, target ~22) ──
    {
        "slug": "storytelling_ambience_topup",
        "chain": ["NarrationAgent", "IllustrationAgent", "NarratorAgent", "AmbienceAgent", "AudioMixAgent", "CompositorAgent"],
        "user_goals": [
            "Tell me an illustrated coastal-village folktale about a Pacific-island fisher who follows a glowing octopus into a hidden lagoon, with constant ocean-wave-and-distant-sea-bird ambience.",
            "Make an illustrated harvest-season story about a rural Italian olive farmer's last picking before retiring, with constant cicada-and-mountain-wind ambience.",
            "Tell an illustrated winter-fjord legend about a Norwegian girl hearing her dead grandmother sing through the cracking ice, with constant creaking-ice-and-wind ambience.",
        ],
    },
    # ── topup: existing storytelling +Music (no imgref) ──
    {
        "slug": "storytelling_music_topup",
        "chain": ["NarrationAgent", "IllustrationAgent", "NarratorAgent", "MusicAgent", "AudioMixAgent", "CompositorAgent"],
        "user_goals": [
            "Tell me an illustrated West-African folktale about a young griot apprentice whose first praise-song saves her village from drought, with a soft kora-and-talking-drum underscore.",
            "Make an illustrated Tibetan-monastery story about a young monk who hears a long-dead lama's chants in his meditation, with a Tibetan-singing-bowl-and-bamboo-flute underscore.",
            "Tell an illustrated Argentine-pampas legend about a gaucho who teaches his orphaned grandson to read the wind across the grasslands, with a soft bandoneón-and-strings underscore.",
        ],
    },
    # ── topup: existing storytelling +imgref+Music ──
    {
        "slug": "storytelling_imgref_music_topup",
        "chain": ["IntakeImageAgent", "BriefEnricherAgent", "NarrationAgent", "IllustrationAgent", "NarratorAgent", "MusicAgent", "AudioMixAgent", "CompositorAgent"],
        "user_goals": [
            "Use this uploaded portrait of a Sufi dervish in white robes mid-spin. Tell me an illustrated story about his journey to the master who taught him the original turn, with a ney-and-daf whirling-tradition underscore.",
            "I've uploaded a watercolor of a Mongolian eagle huntress on horseback with her bird hooded. Tell me an illustrated steppe story about her three-winter pursuit of a wolf that killed her father, with a khoomei-throat-singing-and-morin-khuur underscore.",
            "Here's a sketch of an Andean weaver woman threading alpaca yarn at her backstrap loom. Tell me an illustrated story about her last carpet, woven for her granddaughter's wedding, with a charango-and-quena underscore.",
        ],
    },
    # ── topup: existing storytelling +Music+Translation (no imgref) ──
    {
        "slug": "storytelling_music_translation_topup",
        "chain": ["NarrationAgent", "IllustrationAgent", "NarratorAgent", "MusicAgent", "AudioMixAgent", "TranslationAgent", "CompositorAgent"],
        "user_goals": [
            "Tell me a Spanish folktale about an Andalusian shepherd who learns the old wolf's grief-song one winter, narrate in Spanish with English subtitles, with a soft Spanish-classical-guitar-and-castanet underscore.",
            "Make an illustrated Russian folktale about Baba Yaga's reluctant goddaughter learning to walk through forests by listening to the trees, narrate in Russian with English subtitles, with a balalaika-and-domra underscore.",
            "Tell an illustrated Vietnamese folktale about a fisherman's daughter who discovers her grandfather's last fishing net is woven with hidden poems, narrate in Vietnamese with English subtitles, with a đàn-tranh-and-flute underscore.",
        ],
    },
    # ── topup: existing storytelling +imgref+Music+Translation (full) ──
    {
        "slug": "storytelling_imgref_full_topup",
        "chain": ["IntakeImageAgent", "BriefEnricherAgent", "NarrationAgent", "IllustrationAgent", "NarratorAgent", "MusicAgent", "AudioMixAgent", "TranslationAgent", "CompositorAgent"],
        "user_goals": [
            "Use this uploaded portrait of a Moroccan rural-village storyteller with a worn leather-bound book. Tell me a Berber tale about her grandmother who taught her to read smoke patterns, narrate in Arabic with English subtitles, with an oud-and-darbuka underscore.",
            "I've uploaded a sketch of a Bengali bard at his monsoon-night gathering. Tell me a Bengali folktale about a riverboat captain who outwits a tiger-spirit, narrate in Bengali with English subtitles, with a sitar-and-tabla underscore.",
            "Here's a watercolor of a Cuban son storyteller in his Havana courtyard. Tell me a Cuban folktale about a slave musician whose drum could only be heard by his ancestors, narrate in Spanish with English subtitles, with a tres-and-conga son-cubano underscore.",
        ],
    },
    # ── topup: existing storytelling imgref pure (infra-only display) ──
    {
        "slug": "storytelling_imgref_pure_topup",
        "chain": ["IntakeImageAgent", "BriefEnricherAgent", "NarrationAgent", "IllustrationAgent", "NarratorAgent", "CompositorAgent"],
        "user_goals": [
            "Use this uploaded portrait of a Maasai elder in red shuka holding a long staff. Tell me an illustrated coming-of-age tale about a young initiate's first lion encounter as he tells it.",
            "I've uploaded a sketch of a Highland-Scotland piper in tartan kilt at a stone outcrop. Tell me an illustrated clan-history story about how his great-grandfather's pipe-tune saved a regiment.",
            "Here's a watercolor of a Dutch tulip-farmer in 1637 wooden clogs holding a single bulb. Tell me an illustrated story about his family's ruin during the tulip-mania crash.",
        ],
    },
    # ── topup: existing storytelling +bilingual / Translation only (no imgref) ──
    {
        "slug": "storytelling_bilingual_topup",
        "chain": ["NarrationAgent", "IllustrationAgent", "NarratorAgent", "TranslationAgent", "CompositorAgent"],
        "user_goals": [
            "Tell me a French folktale about a Brittany lighthouse-keeper who befriends a stranded selkie, narrate in French with English subtitles.",
            "Make an illustrated Hindi folktale about a Banaras flower-seller who finds a misplaced love-letter inside a marigold garland, narrate in Hindi with English subtitles.",
            "Tell me a Greek folktale about an Athenian potter whose clay starts revealing forgotten Mycenaean songs, narrate in Greek with English subtitles.",
        ],
    },
    # ── topup: existing storytelling +imgref+bilingual ──
    {
        "slug": "storytelling_imgref_bilingual_topup",
        "chain": ["IntakeImageAgent", "BriefEnricherAgent", "NarrationAgent", "IllustrationAgent", "NarratorAgent", "TranslationAgent", "CompositorAgent"],
        "user_goals": [
            "Use this uploaded portrait of a Persian poet writing on a saffron-tinted page. Tell me an illustrated story about his unrequited love for a Shiraz garden-singer, narrate in Persian with English subtitles.",
            "I've uploaded a sketch of an Inuit elder weaving a sealskin in winter dwelling. Tell me an illustrated story about his three-night storm-vision predicting a returning whale-pod, narrate in Inuktitut with English subtitles.",
            "Here's a watercolor of a Welsh bard with a triple-stringed harp at a coastal village. Tell me an illustrated tale about how his ballad found a lost fisherman's body in the cliffs, narrate in Welsh with English subtitles.",
        ],
    },
]


def parse_chain(sample) -> list[str] | None:
    if "messages" in sample:
        for msg in sample["messages"]:
            if msg["role"] == "assistant":
                try:
                    return [step["agent_id"] for step in json.loads(msg["content"]).get("plan", [])]
                except Exception:
                    return None
        return None
    if "expected_chain" in sample:
        chain = sample["expected_chain"]
        if chain and isinstance(chain[0], dict):
            return [step["agent_id"] for step in chain]
        return chain
    return None


def shape_sig(chain) -> tuple[str, ...]:
    agents: set[str] = set()
    for step in chain:
        if isinstance(step, list):
            agents.update(step)
        else:
            agents.add(step)
    agents.discard("done")
    return tuple(sorted(agents))


def build_eval_shape_map() -> dict[tuple[str, tuple[str, ...]], int]:
    eval_cases = json.loads(EVAL_FILE.read_text(encoding="utf-8"))
    counts: dict[tuple[str, tuple[str, ...]], int] = defaultdict(int)
    for c in eval_cases:
        sig = shape_sig(c["expected_chain"])
        counts[(c["category"], sig)] += 1
    return counts


def extract_system_prompt(sample) -> str:
    for msg in sample["messages"]:
        if msg["role"] == "system":
            return msg["content"]
    raise ValueError("no system message")


def short_shape(sig: tuple[str, ...]) -> str:
    INFRA = {
        "StoryAgent", "ScreenplayAgent", "KeyFrameAgent", "VideoAgent",
        "CompositorAgent", "AudioMixAgent", "BriefEnricherAgent",
        "IntakeImageAgent", "IntakeVideoAgent",
        "NarrationAgent", "IllustrationAgent", "NarratorAgent",
    }
    return "+".join(a.replace("Agent", "") for a in sig if a not in INFRA) or "(infra-only)"


def _pick_intent(agent: str, slug: str, idx: int, slot: int) -> str:
    """Generic intent for an agent slot; pick from INTENT_VARIANTS by hash."""
    pool = INTENT_VARIANTS.get(agent)
    if not pool:
        return f"Run {agent} for this step."
    import hashlib
    h = hashlib.md5(f"{slug}|{idx}|intent_{slot}".encode()).digest()[0]
    return pool[h % len(pool)]


def _simple_rich_rationale(chain: list[str], slug: str) -> str:
    """Brief tag-style rationale used by the rich SFT format."""
    chain_str = " → ".join(a.replace("Agent", "") for a in chain)
    return f"Pipeline shape: {slug}. Chain: {chain_str} → done."


def build_assistant_content(chain: list[str], rationale_mode: str, slug: str, idx: int) -> str:
    """rationale_mode: 'none' | 'templated' | 'rich'.

    - none: only {"plan": [{"agent_id":...}]}
    - templated: {"rationale": <render_rationale>, "plan": [{"agent_id":...}]}
    - rich: {"rationale": <simple>, "plan": [{"agent_id":..., "intent":...}]}
    """
    if rationale_mode == "rich":
        plan = [{"agent_id": a, "intent": _pick_intent(a, slug, idx, slot)}
                for slot, a in enumerate(chain)]
        return json.dumps({"rationale": _simple_rich_rationale(chain, slug), "plan": plan},
                          ensure_ascii=False)
    plan = [{"agent_id": a} for a in chain]
    if rationale_mode == "templated":
        if HAVE_RATIONALE:
            rationale = render_rationale(slug, idx, chain)
        else:
            rationale = f"Pipeline for {slug}; chain has {len(chain)} agents."
        return json.dumps({"rationale": rationale, "plan": plan}, ensure_ascii=False)
    return json.dumps({"plan": plan}, ensure_ascii=False)


def make_sft_sample(system_prompt: str, user_goal: str, chain: list[str],
                    rationale_mode: str, slug: str, idx: int) -> dict:
    return {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_goal},
            {"role": "assistant", "content": build_assistant_content(chain, rationale_mode, slug, idx)},
        ],
    }


def make_grpo_sample(system_prompt: str, user_goal: str, chain: list[str],
                     rationale_mode: str, slug: str, idx: int, source_tag: str) -> dict:
    base = make_sft_sample(system_prompt, user_goal, chain, rationale_mode, slug, idx)
    base["shape_slug"] = slug
    base["source"] = source_tag
    base["gen_id"] = f"v4500_gap_{slug}_{idx}"
    base["long_story"] = False
    return base


def rebalance_file(in_path: Path, out_path: Path,
                   eval_shape_count: dict[tuple[str, tuple[str, ...]], int],
                   eval_total: int, rng: random.Random) -> None:
    print(f"\n=== {in_path.name} ===")

    # Detect format
    is_grpo = "grpo" in in_path.name
    is_templated = "templated" in in_path.name
    is_no_rationale = "no_rationale" in in_path.name
    # 'rich' = original format with per-agent intents (samples_sft_full.jsonl, samples_grpo_v1.jsonl)
    is_rich = (not is_templated) and (not is_no_rationale)
    if is_rich:
        rationale_mode = "rich"
    elif is_templated:
        rationale_mode = "templated"
    else:
        rationale_mode = "none"
    source_tag = f"v4500_gap_{'grpo' if is_grpo else 'sft'}_{rationale_mode}"

    samples: list[dict] = []
    with in_path.open(encoding="utf-8") as fh:
        for line in fh:
            samples.append(json.loads(line))
    original_total = len(samples)
    print(f"  original: {original_total}, format: grpo={is_grpo}, templated={is_templated}")

    # Extract system prompt for new gap-fill samples
    sys_prompt = extract_system_prompt(samples[0])

    # Group existing training samples by (bucket, shape)
    by_shape: dict[tuple[str, tuple[str, ...]], list[dict]] = defaultdict(list)
    train_only_shapes: dict[tuple[str, tuple[str, ...]], int] = defaultdict(int)
    bad = 0
    for s in samples:
        chain = parse_chain(s)
        if not chain:
            bad += 1
            continue
        sig = shape_sig(chain)
        bucket = categorize(chain)
        key = (bucket, sig)
        if key in eval_shape_count:
            by_shape[key].append(s)
        else:
            train_only_shapes[key] += 1

    train_only_total = sum(train_only_shapes.values())
    print(f"  drop train-only: {train_only_total} samples / {len(train_only_shapes)} shapes")
    print(f"  surviving in eval shapes: {sum(len(v) for v in by_shape.values())}")

    # Compute target counts per (bucket, shape) preserving original_total
    eval_props = {k: n / eval_total for k, n in eval_shape_count.items()}
    raw_targets = {k: original_total * p for k, p in eval_props.items()}
    targets: dict[tuple[str, tuple[str, ...]], int] = {k: int(v) for k, v in raw_targets.items()}
    remaining = original_total - sum(targets.values())
    fractional_order = sorted(raw_targets.items(), key=lambda x: -(x[1] - int(x[1])))
    for k, _ in fractional_order:
        if remaining <= 0:
            break
        targets[k] += 1
        remaining -= 1

    # Build gap-fill pools: for each gap shape, materialize SFT/GRPO samples from fresh user_goals
    gap_pools: dict[tuple[str, tuple[str, ...]], list[dict]] = {}
    for gap in GAP_SHAPES:
        chain = gap["chain"]
        slug = gap["slug"]
        sig = shape_sig(chain)
        bucket = categorize(chain)
        key = (bucket, sig)
        if key not in eval_shape_count:
            print(f"  ⚠️ gap shape {slug} not found in eval — skipping")
            continue
        pool = []
        for idx, ug in enumerate(gap["user_goals"]):
            if is_grpo:
                pool.append(make_grpo_sample(sys_prompt, ug, chain, rationale_mode, slug, idx, source_tag))
            else:
                pool.append(make_sft_sample(sys_prompt, ug, chain, rationale_mode, slug, idx))
        gap_pools[key] = pool

    rebalanced: list[dict] = []
    fill_summary: list[tuple[str, str, int, int, int, str]] = []
    for key in sorted(eval_shape_count.keys(), key=lambda k: (BUCKET_ORDER.index(k[0]), k[1])):
        bucket, sig = key
        target = targets[key]
        existing = by_shape.get(key, [])
        fresh_pool = gap_pools.get(key, [])
        # MERGE: existing + fresh pool — sample without replacement (NO duplication).
        # GAP_SHAPES list now serves both roles: cover-from-zero shapes AND topup
        # for under-target existing shapes.
        combined = list(existing) + fresh_pool
        if len(combined) < target:
            # NO-DUP CONTRACT: log gap and take all available (under-target).
            # After full audit, add user_goals for any shape with shortage > 0.
            print(f"  ⚠ SHORT: {bucket}/{short_shape(sig)} existing={len(existing)}+fresh={len(fresh_pool)}={len(combined)} < target={target} (need +{target - len(combined)})")
            picked = list(combined)
        else:
            picked = rng.sample(combined, k=target)
        rebalanced.extend(picked)
        action = f"sampled {target} from existing={len(existing)}+fresh={len(fresh_pool)} (no dup)"
        fill_summary.append((bucket, short_shape(sig), len(existing), len(fresh_pool), target, action))

    rng.shuffle(rebalanced)
    print(f"\n  per-shape:")
    for b, sh, e, f, t, action in fill_summary:
        print(f"    [{b}] {sh:<40} exist={e:>4} fresh={f:>4} target={t:>4}  {action}")

    print(f"\n  final total: {len(rebalanced)} (target was {original_total})")

    with out_path.open("w", encoding="utf-8") as fh:
        for s in rebalanced:
            fh.write(json.dumps(s, ensure_ascii=False))
            fh.write("\n")
    print(f"  wrote: {out_path.name}")


def main() -> None:
    eval_shape_count = build_eval_shape_map()
    eval_total = sum(eval_shape_count.values())
    print(f"Eval map: {len(eval_shape_count)} (bucket, shape) keys, total {eval_total}")
    print(f"Gap shapes hand-written: {len(GAP_SHAPES)}")
    for gap in GAP_SHAPES:
        sig = shape_sig(gap["chain"])
        bucket = categorize(gap["chain"])
        key = (bucket, sig)
        eval_n = eval_shape_count.get(key, 0)
        print(f"  {gap['slug']:<40} bucket={bucket:<14} eval_n={eval_n:>3}  user_goals={len(gap['user_goals'])}")

    if HAVE_RATIONALE:
        print("\n✓ render_rationale imported from build_templated_sft_jsonl")
    else:
        print("\n⚠️ render_rationale not importable — using stub")

    rng = random.Random(RANDOM_SEED)
    for in_path in INPUTS:
        if not in_path.exists():
            print(f"!!! missing: {in_path}")
            continue
        out_path = in_path.with_name(in_path.stem + ".v4_500.jsonl")
        rebalance_file(in_path, out_path, eval_shape_count, eval_total, rng)


if __name__ == "__main__":
    main()
