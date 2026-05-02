"""Phase 3: sub +17 + sub_vid +13 + bilingual +17 + audio +11 (= 58 cases).

sub: 2 shapes (cr+Trans 17 / cr+Trans+Music NEW 8)
sub_vid: 2 shapes (pure 11 / +Translation 14)
bilingual: 2 shapes (cr+Trans+Translation 17 / cr+Trans+Translation+Music NEW 8)
audio: 2 shapes (Music 11 / Music|Ambience 10)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

THIS = Path(__file__).resolve().parent
sys.path.insert(0, str(THIS))
from categorize import categorize  # noqa: E402

V4 = THIS / "eval_cases_v4_500.json"

SUB_CHAIN = [["StoryAgent"], ["ScreenplayAgent"], ["KeyFrameAgent"], ["VideoAgent"], ["TranscriptionAgent"], ["CompositorAgent"], ["done"]]
SUB_MUSIC_CHAIN = [["StoryAgent"], ["ScreenplayAgent"], ["KeyFrameAgent"], ["VideoAgent"], ["TranscriptionAgent"], ["MusicAgent"], ["AudioMixAgent"], ["CompositorAgent"], ["done"]]

SUBVID_PURE = [["IntakeVideoAgent"], ["TranscriptionAgent"], ["CompositorAgent"], ["done"]]
SUBVID_TRANS = [["IntakeVideoAgent"], ["TranscriptionAgent"], ["TranslationAgent"], ["CompositorAgent"], ["done"]]

BILINGUAL_CHAIN = [["StoryAgent"], ["ScreenplayAgent"], ["KeyFrameAgent"], ["VideoAgent"], ["TranscriptionAgent"], ["TranslationAgent"], ["CompositorAgent"], ["done"]]
BILINGUAL_MUSIC_CHAIN = [["StoryAgent"], ["ScreenplayAgent"], ["KeyFrameAgent"], ["VideoAgent"], ["TranscriptionAgent"], ["TranslationAgent"], ["MusicAgent"], ["AudioMixAgent"], ["CompositorAgent"], ["done"]]

AUDIO_MUSIC = [["IntakeVideoAgent"], ["MusicAgent"], ["AudioMixAgent"], ["CompositorAgent"], ["done"]]
AUDIO_ALT = [["IntakeVideoAgent"], ["MusicAgent", "AmbienceAgent"], ["AmbienceAgent", "MusicAgent"], ["AudioMixAgent"], ["CompositorAgent"], ["done"]]


BATCHES = [
    # ===== sub +9 (cr + Trans) =====
    {"chain": SUB_CHAIN, "bucket": "sub", "cases": [
        ("sub_009", "Make an animated drama about a young female stunt double in 1970s Hong Kong cinema risking her life for fame, with English subtitles."),
        ("sub_010", "Create a noir mystery short about a New Orleans Bourbon Street tarot reader who predicts a murder she ends up witnessing, with English subtitles."),
        ("sub_011", "Make a 4-minute period drama about a Russian samovar craftsman in 1880s Tula losing his hand to industrialization, with English subtitles."),
        ("sub_012", "Produce a coming-of-age short about a young female chess prodigy in Cold War Hungary defying her father to enter a tournament, with English subtitles."),
        ("sub_013", "Make a war drama about a young Vietnamese tunnel-runner during the war supplying medicine to underground field hospitals, with English subtitles."),
        ("sub_014", "Create a romance mini-drama about an American jazz pianist in postwar Tokyo falling for the deaf woman who runs the underground bar, with English subtitles."),
        ("sub_015", "Produce a 3-minute fantasy drama about a young Welsh hedge witch curing her village's plague using forbidden faerie bargains, with English subtitles."),
        ("sub_016", "Make a sci-fi short about the only awake astronaut on a multi-decade generation ship trying to compose a love letter for her sleeping wife, with English subtitles."),
        ("sub_017", "Create a thriller mini-drama about a Lima street magician who picks the wrong tourist's pocket and ends up with the diary of a kidnapped politician, with English subtitles."),
    ]},

    # ===== sub + Music NEW +8 =====
    {"chain": SUB_MUSIC_CHAIN, "bucket": "sub", "cases": [
        ("sub_018", "Make a coming-of-age animated short about a young female accordion player in 1960s Lisbon entering her first competition, with English subtitles and a fado-and-accordion score."),
        ("sub_019", "Create a 4-minute war drama about a Polish Resistance courier escorting children to safety, with English subtitles and a tense piano-and-strings score."),
        ("sub_020", "Produce a sci-fi mini-drama about an asteroid miner trapped on her last shift before retirement, with English subtitles and a brooding electronic score."),
        ("sub_021", "Make a romance period drama about an Andalusian flamenco dancer falling for the foreign painter who studies her every night, with English subtitles and a flamenco-guitar-and-cajón score."),
        ("sub_022", "Create a 3-minute animated mystery about a Buenos Aires tango master who suspects his new student of being his late wife reborn, with English subtitles and a bandoneón-and-violin score."),
        ("sub_023", "Make an animated thriller about a Korean hagwon teacher discovering one of her students is filming her after class, with English subtitles and a tense ambient-electronic score."),
        ("sub_024", "Produce a coming-of-age drama about a young Brazilian samba drummer trying to integrate her bloco's rhythms into a school orchestra, with English subtitles and a samba-and-strings score."),
        ("sub_025", "Make a fantasy mini-drama about a young Inuit storyteller learning the songs of her ancestors that summon the northern lights, with English subtitles and a throat-singing-and-frame-drum score."),
    ]},

    # ===== sub_vid pure +6 =====
    {"chain": SUBVID_PURE, "bucket": "sub_vid", "cases": [
        ("sub_vid_013", "I've uploaded a 90-second clip of my best friend's wedding toast. Please transcribe it and burn in English subtitles for a quote-able social-media version."),
        ("sub_vid_014", "Here's a 4-minute lecture clip from my anatomy class. Generate English subtitles and burn them onto the video so I can share it with my study group."),
        ("sub_vid_015", "I have a 2-minute video of my grandmother explaining how to make her dumplings — generate English subtitles for it."),
        ("sub_vid_016", "Take this 3-minute keynote excerpt from a tech conference and add English subtitles I can post on LinkedIn."),
        ("sub_vid_017", "I've recorded a 60-second testimonial from a customer about our product. Add English subtitles before I post it on the website."),
        ("sub_vid_018", "Here's a 5-minute interview clip with my dad about his immigration story. Generate English subtitles for an upcoming family reunion screening."),
    ]},

    # ===== sub_vid + Translation +7 =====
    {"chain": SUBVID_TRANS, "bucket": "sub_vid", "cases": [
        ("sub_vid_019", "Here's a 2-minute Italian-language interview I shot with a Sicilian farmer about olive harvesting. Translate to English and burn in subtitles."),
        ("sub_vid_020", "I have a 3-minute Mandarin clip of my grandfather's Cantonese opera performance. Generate Cantonese transcription, translate to English, and add subtitles."),
        ("sub_vid_021", "Take this 4-minute Russian street-vendor interview from St. Petersburg and produce an English-subtitled version."),
        ("sub_vid_022", "I've uploaded a 90-second Hindi cooking demo. Translate it into English subtitles and burn them onto the video."),
        ("sub_vid_023", "Here's a 2-minute Tagalog interview with a Filipino jeepney driver. Translate to English subtitles for our documentary."),
        ("sub_vid_024", "I have a 5-minute Swahili clip of a community-leader speech in Nairobi. Add English subtitles for international screening."),
        ("sub_vid_025", "Take this 3-minute Greek interview with an island potter and produce an English-subtitled version for the gallery's online catalogue."),
    ]},

    # ===== bilingual +9 =====
    {"chain": BILINGUAL_CHAIN, "bucket": "bilingual", "cases": [
        ("bilingual_009", "Make an animated period drama about a young Chinese telegraph operator in 1925 Shanghai who falls in love with a Russian émigré through coded messages, with English-Chinese bilingual subtitles."),
        ("bilingual_010", "Create a 4-minute coming-of-age short about a young Bavarian apprentice clockmaker in 1880s Munich, with English-German bilingual subtitles."),
        ("bilingual_011", "Produce a romance mini-drama about a young Spanish bullfighter losing her nerve before her last corrida in Madrid, with English-Spanish bilingual subtitles."),
        ("bilingual_012", "Make a thriller short about a young French Resistance courier in 1942 Lyon delivering smuggled documents, with English-French bilingual subtitles."),
        ("bilingual_013", "Create a period drama about a Korean hanji paper-maker in 1950s post-war Seoul, with English-Korean bilingual subtitles."),
        ("bilingual_014", "Make a coming-of-age short about a young Mexican charra horsewoman entering her first national rodeo, with English-Spanish bilingual subtitles."),
        ("bilingual_015", "Produce a 3-minute fantasy drama about a young Japanese onmyōji apprentice in Heian-era Kyoto exorcising her first tsukumogami, with English-Japanese bilingual subtitles."),
        ("bilingual_016", "Make an animated noir mini-drama about a 1970s São Paulo female private investigator searching for a missing samba star, with English-Portuguese bilingual subtitles."),
        ("bilingual_017", "Create a war drama short about a Greek partisan radio operator in 1943 occupied Athens broadcasting BBC bulletins, with English-Greek bilingual subtitles."),
    ]},

    # ===== bilingual + Music NEW +8 =====
    {"chain": BILINGUAL_MUSIC_CHAIN, "bucket": "bilingual", "cases": [
        ("bilingual_018", "Make a romance mini-drama about a young Austrian piano teacher in 1950s Vienna teaching a Soviet diplomat's daughter, with English-German bilingual subtitles and a Viennese-waltz score."),
        ("bilingual_019", "Create an animated coming-of-age drama about a young Senegalese kora player traveling to study at the Paris Conservatoire, with English-Wolof bilingual subtitles and a kora-and-strings score."),
        ("bilingual_020", "Produce a 4-minute period drama about a young Korean female pansori singer in late-Joseon Seoul, with English-Korean bilingual subtitles and a pansori buk-drum score."),
        ("bilingual_021", "Make an animated mystery short about a Veracruz son-jarocho musician investigating a stolen harp, with English-Spanish bilingual subtitles and a son-jarocho-and-marimbol score."),
        ("bilingual_022", "Create a thriller mini-drama about a young Vietnamese đàn tranh player in 1968 Saigon transmitting coded melodies to the resistance, with English-Vietnamese bilingual subtitles and a đàn tranh-and-flute score."),
        ("bilingual_023", "Make a 3-minute period romance about an Italian opera diva in 1880s Naples and a French composer, with English-Italian bilingual subtitles and an operatic strings-and-soprano score."),
        ("bilingual_024", "Produce a coming-of-age drama about a young Mongolian morin-khuur student auditioning at the State Conservatory, with English-Mongolian bilingual subtitles and a morin-khuur-and-throat-singing score."),
        ("bilingual_025", "Make a war drama about a Polish piano student in 1944 Kraków playing Chopin nocturnes for wounded soldiers, with English-Polish bilingual subtitles and a piano-and-strings score."),
    ]},

    # ===== audio Music +6 =====
    {"chain": AUDIO_MUSIC, "bucket": "audio", "cases": [
        ("audio_011", "I've uploaded 90 seconds of my morning jog through Central Park. Add an upbeat indie-rock track over it."),
        ("audio_012", "Take this 2-minute family video of my niece's first birthday party and add a soft acoustic-guitar background score."),
        ("audio_013", "I have a 60-second highlight reel from a friend's wedding ceremony. Add a romantic piano-and-strings track to it."),
        ("audio_014", "Here's a 3-minute drone shot over my local lake at sunset. Add a sweeping orchestral score."),
        ("audio_015", "I've shot 90 seconds of my apartment's renovation timelapse. Add an upbeat electronic track to make it shareable."),
        ("audio_016", "Take this 2-minute clip of my dog playing in the snow and add a playful ukulele-and-banjo track."),
    ]},

    # ===== audio Music|Ambience alt +5 =====
    {"chain": AUDIO_ALT, "bucket": "audio", "cases": [
        ("audio_017", "I've uploaded a 90-second clip of an empty subway station at midnight. Add gentle piano music with constant subway-tunnel ambience underneath."),
        ("audio_018", "Here's a 2-minute clip of a snowy Alaskan night campsite. Layer in an acoustic-guitar piece with constant howling-wind ambience."),
        ("audio_019", "Take this 90-second video of my grandmother's quiet kitchen at dawn and overlay a soft cello piece with constant kettle-and-clock ambience."),
        ("audio_020", "I've shot 2 minutes of an old library reading room. Add a contemplative violin score with constant page-turning and clock-tick ambience."),
        ("audio_021", "Here's 90 seconds of footage from a Greek monastery courtyard. Layer in a Byzantine-chant piece with constant cicada-and-fountain ambience."),
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
