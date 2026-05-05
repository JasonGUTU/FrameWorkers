"""Generate 20 ADDITIONAL hard user_goals (hard_046-hard_065) targeting
known failure anti-patterns from the smoke test:
  P1. Long-story → CR pipeline (LoRA mis-routes to storytelling NarrationAgent)
  P2. "Held for X seconds" → implicit VideoExtend (LoRA tends to drop)
  P3. "Captioned in source language" → Trans only, LoRA tends to add Translation
  P4. Audio-only abstract → LoRA over-routes with VideoAnalysis
  P5. Multi-transform abstract → LoRA drops one transform
All shapes verified in v4_500.
"""
import json
from pathlib import Path

NEW_CASES = [
    # ============ P1: Long-story → CR pipeline (4 cases) ============
    {
        "name": "hard_046",
        "category": "cr",
        "expected_chain": [["StoryAgent"],["ScreenplayAgent"],["KeyFrameAgent"],["VideoAgent"],["CompositorAgent"],["done"]],
        "user_goal": "Here's my story I want to process: When Halldór Þórarinsson was eleven, his grandfather, who had been a herring fisherman in Siglufjörður for forty-six winters, took him out for the first time on the family boat the morning before the herring run, in a fog so thick that the lighthouse on the headland was only intermittently visible, and told him, in the small wooden cabin while they waited for the fog to lift, the story of how his own great-grandfather had once lost the boat to the sea-king for an entire night and won it back at dawn by reciting the names of all the village's drowned. Halldór, who had been told the story partially three times before by his mother and once in a different version by an aunt, now heard it complete for the first time, and when his grandfather finished he understood, with the early-onset clarity of a child who has been waiting unconsciously for the truth, that the story was true and that he was being told it because his grandfather did not expect to come back from the season's end run. He was seventy-eight, his hands shook, and he was, his daughter would later say at the funeral, the best fisherman the fjord had produced in his generation. Make this a slow Icelandic mini-drama."
    },
    {
        "name": "hard_047",
        "category": "cr",
        "expected_chain": [["StoryAgent"],["ScreenplayAgent"],["KeyFrameAgent"],["VideoAgent"],["MusicAgent"],["AudioMixAgent"],["CompositorAgent"],["done"]],
        "user_goal": "Here's my story I want to process: Adamantia Vasilakou had been the second cellist of the Athens Philharmonic for thirty-one years and the principal teacher of cello at the conservatory for nineteen of those, and over the long arc of her career she had taught seventy-three students, of whom four had become professional cellists abroad, twelve had become gifted amateur players who would perform at family weddings into their old age, and one, a quiet boy named Stefanos who had stopped playing entirely in his second year of conservatory and disappeared from her life, had become, by every account she could find, the greatest performing cellist of his generation, but performed only in private, only for one or two listeners at a time, only by personal invitation, and never recorded. On her sixty-eighth birthday, two months after she retired from the Philharmonic, an unmarked package arrived at her apartment in Kolonaki containing a single hand-pressed CD, no liner notes, no sender address, and on the disc, when she played it that night with the lamp dimmed and the windows open to the street, was Stefanos performing the entire Bach cello suites from memory in what she could tell was a single uninterrupted recording session in the empty interior of the small Byzantine chapel where she had taken him on a school trip when he was sixteen years old. Make this a slow Greek period mini-drama, scored throughout with a delicate solo cello plus distant piano underlay (no spoken-text captioning, no environmental ambient layer)."
    },
    {
        "name": "hard_048",
        "category": "sub",
        "expected_chain": [["StoryAgent"],["ScreenplayAgent"],["KeyFrameAgent"],["VideoAgent"],["TranscriptionAgent"],["CompositorAgent"],["done"]],
        "user_goal": "Here's my story I want to process: Tewodros Bekele had been the chief brewer at the Saint Gabriel Tella house in Addis Ababa's old Piazza district for forty-one years, ever since taking over from his uncle Yilma in 1978, and over those forty-one years he had quietly modified, in increments measurable only by the most experienced of his customers, the family recipe for tej that the uncle had inherited from his grandmother, by introducing first a particular wild yeast he cultured himself from honey traded down from the Bale highlands and then, over the course of fifteen years, a slowly increasing proportion of a specific gesho varietal he had been propagating in a small enclosed garden behind the brewery. On the morning of his sixty-fifth birthday, when his daughter Hirut, who had been quietly studying biochemistry at Addis Ababa University and had recently begun, with his permission, to sample the various stages of fermentation in his fermenting vessels, sat him down at the kitchen table and presented him with a meticulously prepared written analysis of his recipe modifications and a graph showing how the wild-yeast cultures had drifted in eight measurable directions over the past two decades, Tewodros sat very still and said nothing for the longest time, then asked her in the smallest possible voice whether she thought it was time he should retire and let her take over. Make this an Ethiopian period drama in original Amharic dialogue with English transcription captions only (single-language transcript captions of the source Amharic, not a translation track)."
    },
    {
        "name": "hard_049",
        "category": "cr",
        "expected_chain": [["StoryAgent"],["ScreenplayAgent"],["KeyFrameAgent"],["VideoAgent"],["AmbienceAgent","MusicAgent"],["AmbienceAgent","MusicAgent"],["AudioMixAgent"],["CompositorAgent"],["done"]],
        "user_goal": "Here's my story I want to process: Margrét Jónsdóttir, who had been the only Icelandic-language teacher in the village school of Stöðvarfjörður for thirty-nine years, lived alone after her husband's death in a small turf-roofed house on the slope above the harbor with a single Icelandic sheepdog named Skuggi, and she had been, for the past eleven years and increasingly to her quiet alarm, forgetting words. The condition had been diagnosed as a slow-onset frontotemporal dementia six years before, but she had not told anyone in the village. On the morning of the autumn equinox in her seventy-seventh year, when the first heavy snow of the season fell unexpectedly two months early, she walked out of her house in her wool overcoat without telling Skuggi, climbed the path that led up the southern slope of the fjord, and sat down on a rock she had been sitting on since she was a girl, intending to stay there until the snow buried her. Three hours later, Skuggi, who had pushed open the kitchen door and tracked her, lay down beside her on the rock and growled softly until she stood up and walked back home with him. Make this a contemplative Icelandic period drama, with a haunting Hardanger-fiddle-and-piano score and continuous high-fjord-wind-and-distant-sea ambience layered through the entire piece."
    },
    # ============ P2: "Hold for X seconds" → implicit VideoExtend (4 cases) ============
    {
        "name": "hard_050",
        "category": "extend",
        "expected_chain": [["IntakeVideoAgent"],["VideoExtendAgent"],["done"]],
        "user_goal": "I'm uploading a 4-second clip of a kestrel hovering motionless over a hayfield at golden hour, the only movement in the frame being the bird's slow wingbeat against the still grass below. The moment as it stands cuts off too abruptly. I'd like the held suspension allowed to continue—roughly twenty more seconds of the same hovering, no other change to the scene, the bird and its shadow alone in the field, no audio additions of any kind, no captions, no other modification."
    },
    {
        "name": "hard_051",
        "category": "extend",
        "expected_chain": [["IntakeVideoAgent"],["VideoExtendAgent"],["MusicAgent"],["AudioMixAgent"],["CompositorAgent"],["done"]],
        "user_goal": "Here's an 8-second handheld shot of an elderly Andalusian olive picker resting on a low stone wall at the end of a long day, the western sun behind him, no movement of dialogue. The fatigue of the moment isn't fully landing in the cut as it stands—I want the rest beat allowed to breathe, perhaps about thirty seconds total runtime, and beneath the held visual a single quiet acoustic-guitar piece in the cante hondo register that doesn't intrude. No captions, no other audio layers, no environmental sweetening."
    },
    {
        "name": "hard_052",
        "category": "complex",
        "expected_chain": [["IntakeImageAgent"],["BriefEnricherAgent"],["StoryAgent"],["ScreenplayAgent"],["KeyFrameAgent"],["VideoAgent"],["VideoExtendAgent"],["CompositorAgent"],["done"]],
        "user_goal": "I'm uploading a watercolor portrait of a middle-aged Polish glass-engraver in a leather apron working at a small bench, late winter afternoon light through a high north-facing window. Use her as the protagonist of: Dorota Wiśniewski had been engraving crystal at the Krosno glassworks for twenty-eight years and had recently been laid off in a corporate restructuring along with seventeen of her colleagues, and on her last day in the workshop she sat alone at her bench for the final hour of her shift before the gates closed for good, completing one last private engraving on a single piece of crystal she had brought from home. Make a 90-second Polish period mini-drama from this brief, and please draw out the moment of her finishing the final cut into a longer held-breath beat for emphasis—no audio, no captions."
    },
    {
        "name": "hard_053",
        "category": "complex",
        "expected_chain": [["IntakeImageAgent"],["BriefEnricherAgent"],["StoryAgent"],["ScreenplayAgent"],["KeyFrameAgent"],["VideoAgent"],["VideoExtendAgent"],["MusicAgent"],["AudioMixAgent"],["CompositorAgent"],["done"]],
        "user_goal": "I'm sending a portrait of a young Vietnamese fishing-boat painter standing barefoot on a pier in Hội An, brushes in hand, a half-finished prow design visible. Use her as the protagonist for: Nguyễn Linh had grown up watching her grandfather paint the protective eyes onto the prows of new fishing boats and had, after his death, become the only person under fifty in three coastal villages who could still execute the traditional ritual brushwork in the original style, and on the day of the launching of her first independent commission—a 14-meter trawler for a family who had lost their previous boat in a typhoon—she stood on the pier for forty minutes alone before the ceremony making the final eye-strokes. Produce this as a 75-second Vietnamese period mini-drama; let the moment of her completing the final eye-stroke linger in a longer held beat, and lay underneath a sparse đàn tranh and bamboo-flute score (no captions, no separate ambient layer)."
    },
    # ============ P3: "Captioned in source language" — Trans only, NOT Translation (4 cases) ============
    {
        "name": "hard_054",
        "category": "sub_vid",
        "expected_chain": [["IntakeVideoAgent"],["TranscriptionAgent"],["CompositorAgent"],["done"]],
        "user_goal": "I'm sending in 17 minutes of unedited home-video footage from a 2003 family reunion in rural Hokkaido—six elderly relatives speaking Hokkaido-dialect Japanese (which has its own distinctive vocabulary and intonation) interspersed with standard Japanese from the younger family members. The audio is fine. I'd like the spoken content captioned exactly as spoken, in the same language being spoken, for accessibility purposes only—not a translation track, just a transcript caption layer in the source language."
    },
    {
        "name": "hard_055",
        "category": "style",
        "expected_chain": [["IntakeVideoAgent"],["StyleTransferAgent"],["TranscriptionAgent"],["CompositorAgent"],["done"]],
        "user_goal": "I have a 6-minute interview clip with a Polish-speaking carpentry master from a regional television documentary aired in 1988, the audio is well-preserved Polish, the visuals are dated. I'd like the visuals reanimated as if rendered in a Polish woodcut-illustration style from the inter-war period, and for accessibility I want captions of the spoken content in the same language being spoken—no English translation involved, just a transcript-caption track in the source Polish."
    },
    {
        "name": "hard_056",
        "category": "extend",
        "expected_chain": [["IntakeVideoAgent"],["VideoExtendAgent"],["TranscriptionAgent"],["CompositorAgent"],["done"]],
        "user_goal": "I have a 9-second clip of an elderly Faroese sweater-knitter narrating, in Faroese, the origin of a particular regional pattern—the narration is mid-sentence and cuts off too quickly. Could you let her finish the sentence naturally, perhaps stretching to twenty-two or so seconds total, and add captions of her speech in her own language (Faroese), no translation track, no other modifications."
    },
    {
        "name": "hard_057",
        "category": "highlight",
        "expected_chain": [["IntakeVideoAgent"],["VideoAnalysisAgent"],["HighlightAgent"],["TranscriptionAgent"],["CompositorAgent"],["done"]],
        "user_goal": "I have 4.5 hours of unedited recording from a 1991 Catalan-language workshop on traditional sardana dance composition, conducted entirely in Catalan with regional inflection. Pull out the 5 most pedagogically rich segments where the master is teaching specific compositional techniques, and add transcript captions in the same language he's speaking (Catalan, source-language only) for accessibility purposes; no translation, no audio sweetening, no other modifications."
    },
    # ============ P4: Audio-only abstract → trip up over-routing (4 cases) ============
    {
        "name": "hard_058",
        "category": "audio",
        "expected_chain": [["IntakeVideoAgent"],["MusicAgent"],["AudioMixAgent"],["CompositorAgent"],["done"]],
        "user_goal": "I have a 3-minute observational clip of a Sufi calligrapher working at his desk in his home studio in Konya, slow contemplative work with no spoken dialogue, the original audio is mostly the soft scratching of his pen and ambient room sound which I'd like entirely replaced. The new audio bed should be a slow ney-and-rebab piece keyed to the meditative pace of his hand, replacing the original audio entirely; no captions, no other audio layers, no preserved environmental sounds."
    },
    {
        "name": "hard_059",
        "category": "audio",
        "expected_chain": [["IntakeVideoAgent"],["MusicAgent"],["AudioMixAgent"],["CompositorAgent"],["done"]],
        "user_goal": "Here's 90 seconds of silent timelapse footage of mist rolling in over a Pacific Northwest old-growth forest at dawn—the clip has no native audio of any kind. I want only a continuous solo-piano piece laid underneath that arcs with the visual breathing of the mist; no spoken voice, no captions, no separate environmental sound layer."
    },
    {
        "name": "hard_060",
        "category": "audio",
        "expected_chain": [["IntakeVideoAgent"],["AmbienceAgent","MusicAgent"],["AmbienceAgent","MusicAgent"],["AudioMixAgent"],["CompositorAgent"],["done"]],
        "user_goal": "I have a 2-minute silent observational shot of a Mongolian eagle hunter and his bird at rest on a winter steppe outcrop, no movement of speech. Build a layered audio bed that pairs (1) a sparse morin-khuur-and-throat-singing piece keyed to the patient quality of the rest, and (2) underneath, the wind-and-distant-eagle-cry environmental layer that rooms the visuals in their place. Both layers laid in together, no captions, no narration."
    },
    {
        "name": "hard_061",
        "category": "style",
        "expected_chain": [["IntakeVideoAgent"],["StyleTransferAgent"],["MusicAgent"],["AudioMixAgent"],["CompositorAgent"],["done"]],
        "user_goal": "I have a 70-second observational clip of an old Korean potter centering clay on a slow kick-wheel, the original audio is the soft natural workshop sound which I'd like entirely replaced. Render the visuals as if lifted into the aesthetic of a 16th-century Joseon-era ink scroll, and underneath lay a sparse gayageum solo piece that breathes with the throwing rhythm—no captions, no separate environmental audio layer."
    },
    # ============ P5: Multi-transform abstract → LoRA drops one transform (4 cases) ============
    {
        "name": "hard_062",
        "category": "complex",
        "expected_chain": [["IntakeVideoAgent"],["VideoExtendAgent"],["StyleTransferAgent"],["TranscriptionAgent"],["CompositorAgent"],["done"]],
        "user_goal": "I have a 9-second clip of an elderly Greek woman in black mourning dress speaking quietly in modern Greek about her late husband's olive grove. The moment cuts off too suddenly—I want her trailing speech allowed to land for another fifteen-or-so seconds, the visuals re-rendered as if shot on grainy black-and-white 16mm film stock from the early 1970s, and accessibility captions burned in for whatever Greek she's speaking (source-language transcript captions, no translation involved)."
    },
    {
        "name": "hard_063",
        "category": "complex",
        "expected_chain": [["IntakeVideoAgent"],["StyleTransferAgent"],["VideoExtendAgent"],["MusicAgent"],["AudioMixAgent"],["CompositorAgent"],["done"]],
        "user_goal": "Here's a 6-second handheld shot of a Yemeni woman drawing water from a courtyard well at noon, the visual quality is observational realism. Reframe the visuals as if rendered in mid-century Yemeni miniature-painting style, let the moment of her pulling the bucket up complete and breathe in a longer held beat—roughly twenty seconds total—and lay underneath a sparse oud-and-rebab score that doesn't compete with the held visual. No captions, no other audio layers."
    },
    {
        "name": "hard_064",
        "category": "complex",
        "expected_chain": [["IntakeVideoAgent"],["VideoExtendAgent"],["StyleTransferAgent"],["done"]],
        "user_goal": "I have a 4-second clip of incense smoke curling above a small ceramic bowl in a Japanese temple antechamber. The held breath of the moment needs more time, perhaps twenty-four or so seconds, and the visuals reframed as if drawn in the linework of a late-Edo-period sumi-e ink wash. No audio of any kind, no captions, no other manipulation."
    },
    {
        "name": "hard_065",
        "category": "complex",
        "expected_chain": [["IntakeVideoAgent"],["StyleTransferAgent"],["VideoExtendAgent"],["MusicAgent"],["AudioMixAgent"],["CompositorAgent"],["done"]],
        "user_goal": "Here's a 5-second handheld clip of an elderly Quechua weaver standing in the morning sun above her loom, sun-line slanted across the half-finished textile. Reframe the visuals as if rendered in the visual register of pre-Columbian Andean ceramic painting, allow the moment of her gaze across the textile to extend in a longer held breath, perhaps about twenty-five seconds total, and lay underneath a contemplative quena-and-charango piece that breathes with the still posture. No captions, no separate ambient layer."
    },
]

# verify all use v4_500 shapes
hard_path = Path('/home/zhendong_li/FrameWorkers/evals/director_routing/eval_cases_v4500_hard45.json')
existing = json.loads(hard_path.read_text())
existing.extend(NEW_CASES)

# verify shape coverage
v4500 = json.loads(Path('/home/zhendong_li/FrameWorkers/evals/director_routing/eval_cases_v4_500.json').read_text())
def shape_key(chain):
    return tuple(tuple(sorted(l)) if isinstance(l, list) else (l,)
                 for l in chain if l != ['done'] and l != 'done')
v4500_shapes = {shape_key(c['expected_chain']) for c in v4500}
new_invalid = [c for c in NEW_CASES if shape_key(c['expected_chain']) not in v4500_shapes]
print(f"Generated {len(NEW_CASES)} new style-A cases (hard_046–hard_065)")
print(f"Shape coverage in v4_500: {len(NEW_CASES) - len(new_invalid)}/{len(NEW_CASES)}")
if new_invalid:
    for c in new_invalid:
        print(f"  ⚠ {c['name']}: shape NOT in v4_500")

# save merged file (45 + 20 = 65 hard cases)
merged_path = Path('/home/zhendong_li/FrameWorkers/evals/director_routing/eval_cases_v4500_hard65.json')
merged_path.write_text(json.dumps(existing, indent=2, ensure_ascii=False) + '\n')
print(f"\nSaved {len(existing)} hard cases to {merged_path}")
