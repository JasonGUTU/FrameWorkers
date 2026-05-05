"""Generate 45 hard user_goal variants using existing v4_500 chain shapes.

Hardness levers:
- Long-story narrative input (1500-3000 chars), real plot prose, routing hint at end
- Ambiguous routing (e.g., "atmospheric" could mean ambience or music or both)
- Multi-genre / cross-cultural content the model is less likely to have memorized
- Compound asks with embedded distractor concepts
"""
import json
from pathlib import Path

# Shape templates copied from v4_500 (use the "expected_chain" field verbatim).
# Each entry: name, category, expected_chain, hard_user_goal
HARD_CASES = [
    # ===== LONG-STORY CR (text only, no image upload, ~1500-2500 chars) =====
    # Shape: Story > Screenplay > KeyFrame > Video > Compositor (5 steps, plain CR)
    {
        "name": "hard_001",
        "category": "cr",
        "expected_chain": [["StoryAgent"],["ScreenplayAgent"],["KeyFrameAgent"],["VideoAgent"],["CompositorAgent"],["done"]],
        "user_goal": "Here's my story I want to process: Lorca Mendel had been the night-shift archivist at the Casa Lorenzetti library in Buenos Aires for nineteen years, a job she had taken at twenty-three after the death of her father and never thought of leaving, partly out of a fondness for the smell of old leather bindings and partly because the night-shift wage covered her brother Camilo's tuition at the conservatory and later, after he dropped out, his rent. The library held one of the largest private collections of pre-Columbian manuscripts in the Southern Cone, fourteen thousand items kept in three climate-controlled subterranean chambers that visitors could only access by appointment and only between ten in the morning and four in the afternoon. Lorca's job, conducted alone after the daytime archivists locked up, was to pace the chambers between midnight and dawn, monitor humidity, watch the seismograph during the autumn earthquake season, and physically turn certain manuscripts every fourteen days to prevent the binding glues from settling. On the night of October the twelfth she discovered, behind a folio of Quechua tribute records, a velvet-wrapped octavo notebook that had been cataloged in 1982 as anonymous and undated, but whose first page, when she finally opened it that night because the silence had unnerved her, contained her own grandmother's signature—a grandmother she had been told had died fifteen years before Lorca was born. Make this into a slow, literary period mystery animated drama."
    },
    {
        "name": "hard_002",
        "category": "cr",
        "expected_chain": [["StoryAgent"],["ScreenplayAgent"],["KeyFrameAgent"],["VideoAgent"],["CompositorAgent"],["done"]],
        "user_goal": "Here's my story I want to process: The lighthouse on the southwestern point of Tindholmur had been automated in 1973 but Beathe Ouens, who had been its keeper for the previous twenty-eight years and would have continued for another eighteen if the Faroese maritime ministry had let her, refused to leave the small stone outbuilding at its base, and since the ministry had no real budget for evicting an elderly woman from a now-disused outpost, and since she paid her own oil and her own bread, she stayed. She was eighty-one when the new acting keeper, a marine biology student named Eivør Hansen on a six-week research rotation, climbed up the headland on a damp September morning and found the door of the keeper's outbuilding ajar. Beathe was not inside. The pot of skerpikjøt on the stove was still warm. Eivør, who had read Beathe's monographs on petrel migration as an undergraduate and revered her, walked out to the cliff edge and saw, in the cove ninety meters below, three things she could not at first explain: the keeper's woolen coat, neatly folded; the keeper's brass spyglass, set on top of it; and a path of small wet footprints leading from the rocks back into the sea. Make this into a quiet supernatural-folktale animated drama."
    },
    # Shape: Story > Screenplay > KeyFrame > Video > Music > AudioMix > Compositor (CR + music)
    {
        "name": "hard_003",
        "category": "cr",
        "expected_chain": [["StoryAgent"],["ScreenplayAgent"],["KeyFrameAgent"],["VideoAgent"],["MusicAgent"],["AudioMixAgent"],["CompositorAgent"],["done"]],
        "user_goal": "Here's my story I want to process: Avraam Cohen had played the cantor's role at the Beit Yosef synagogue in Casablanca's old Jewish quarter for forty-one years, and every Yom Kippur for the last thirty he had sung the Kol Nidre opening himself, and in the last six years, since his teacher Reuben Tordjman had died, he had sung it standing alone at the bimah in the unlit sanctuary because Tordjman had asked him, on his deathbed, to keep the lights off so that he could remember the shadow of the old shul in Sefrou where he himself had first heard the prayer as a child in 1941. On the eve of Yom Kippur 5784, when Avraam was sixty-eight and his voice no longer reached the high notes it had once reached, his estranged daughter Léa, who had not entered a synagogue in twelve years and had not spoken to her father in seven, walked into the back of the sanctuary in the dark wearing a black coat she could not afford and a stranger's wedding ring on her left hand and stood there listening for the entire forty-three minutes of Kol Nidre, and when the last note ended she walked back out without speaking, and the next morning Avraam, knowing she had been there because he had heard her step on the third pew from the back which had always squeaked, walked across town to the apartment she had not lived in for two years and waited on the stairs. Make this a slow Sephardic period drama, with a gentle oud and ney background score that mirrors the cantor's prayer."
    },
    # Shape: Story > Screenplay > KeyFrame > Video > Ambience > AudioMix > Compositor
    {
        "name": "hard_004",
        "category": "cr",
        "expected_chain": [["StoryAgent"],["ScreenplayAgent"],["KeyFrameAgent"],["VideoAgent"],["AmbienceAgent"],["AudioMixAgent"],["CompositorAgent"],["done"]],
        "user_goal": "Here's my story I want to process: Mariana Soares, who had grown up barefoot on the saltpans south of Aveiro and had taken over her mother's salt operation at the age of nineteen, was now sixty-three and had spent that morning in early October standing at the edge of her westernmost crystallization tank watching the surface skin form, when she noticed, half-buried in the salt at the corner of the tank, a small object that turned out, when she lifted it free, to be a brass compass that had not been there the previous evening, that bore an engraving in a Cyrillic script she could not read, and that swung consistently and impossibly toward the west whichever way she turned. The young man who arrived at her gate three days later, asking in halting Portuguese whether she had found anything unusual, was twenty-eight, dark-haired, exhausted, and had walked, by his account, the last sixty kilometers from Coimbra carrying nothing but a leather rucksack and a set of hand-drawn charts. He was looking for the compass. Mariana, who had not made up her mind whether to give it back, invited him in for soup. Make this into a slow coastal-magical-realism drama with continuous saltpan-and-Atlantic-wind ambient sounds layered through the whole piece (no music)."
    },
    # Shape: Story>Screenplay>KF>Video>Trans>Compositor (CR + mono subs)
    {
        "name": "hard_005",
        "category": "sub",
        "expected_chain": [["StoryAgent"],["ScreenplayAgent"],["KeyFrameAgent"],["VideoAgent"],["TranscriptionAgent"],["CompositorAgent"],["done"]],
        "user_goal": "Here's my story I want to process: Tønnes Knutson, a third-generation lay preacher in the Western Norwegian fjord-mouth village of Klokkarvik, had quietly stopped believing in God somewhere around his forty-second birthday but had continued, for another sixteen years, to deliver the Sunday sermon at the small white wooden chapel at the head of the fjord, primarily because the elderly congregation depended on it and partly because his wife Helga, whose faith was iron, did not yet know. On a stormy March Sunday when the chapel held only nine people and the sea outside was throwing fish onto the front path, he gave a sermon on the Book of Job that ended, to the bewilderment of his audience, with a long apology to no one in particular and a quiet declaration that he had been preaching without conviction for nearly two decades. He walked off the platform, sat down in the front pew next to Helga, and waited. None of the nine, including Helga, said anything for what later turned out to be eleven minutes. Make this into a quiet Norwegian period drama with English subtitles—the actual original Norwegian dialogue is all I want, just captioned in English, no translation."
    },
    # Shape: Story>Screenplay>KF>Video>Trans>Translation>Compositor (CR + bilingual)
    {
        "name": "hard_006",
        "category": "bilingual",
        "expected_chain": [["StoryAgent"],["ScreenplayAgent"],["KeyFrameAgent"],["VideoAgent"],["TranscriptionAgent"],["TranslationAgent"],["CompositorAgent"],["done"]],
        "user_goal": "Here's my story I want to process: Aiko Tanizaki was a kataribe, a hereditary oral storyteller, of the Sannomiya ward of Kobe, the seventh in her female lineage, and on the morning of the Hanshin earthquake she was sixty-three and had been preparing for that evening's quarterly recital of the Heike Monogatari excerpts when the shaking began. Her two-story wooden house, built in 1908 by her great-grandmother out of cedar from the Yoshino mountains, collapsed in the second wave around her, and she lay under the kitchen beam for nineteen hours before a neighbor's son, who had come specifically to look for her because his grandmother had owed her a small debt of recitation tradition, found her by the sound of her continuing, half-conscious, to recite the Atsumori passage of the Heike under her breath. She did not stop reciting until the rescuers had pulled her free. The neighbor's son, fifteen at the time, would later become her last student. Produce this as a Japanese period drama, original Japanese dialogue with both Japanese and English bilingual subtitles."
    },
    # Shape: Story>Screenplay>KF>Video>[M,A]x2>AudioMix>Compositor (CR + M+A)
    {
        "name": "hard_007",
        "category": "cr",
        "expected_chain": [["StoryAgent"],["ScreenplayAgent"],["KeyFrameAgent"],["VideoAgent"],["AmbienceAgent","MusicAgent"],["AmbienceAgent","MusicAgent"],["AudioMixAgent"],["CompositorAgent"],["done"]],
        "user_goal": "Here's my story I want to process: When Magnus Sondrebø was sixty-one and had been the night fishmonger at the Bergen wharf market for thirty-four winters, the doctor in the Haukeland clinic told him quietly across the desk that the cough he had been ignoring for eight months was a stage-three lung carcinoma that had already metastasized to the bone, that his prognosis was somewhere between four and eleven months, and that, in the doctor's clinical opinion, he should consider concluding his outstanding personal matters within sixty days. Magnus, who had not spoken to his estranged son Jens for fourteen years following an argument over a fishing-quota arrangement that no longer mattered to either of them, walked from the clinic to the wharf, opened up his stall, sold the morning catch as usual to the Hanseatic restaurants and the corner-shop owners and the elderly women he had been selling to for decades, closed at noon, walked home, slept three hours, woke, ate a small dinner of lutefisk, and at eight that evening boarded the Hurtigruten coastal ferry north toward Trøndelag where Jens had been working for a decade as a salmon-farm engineer, having never once visited his son's home in any of those fourteen years and not knowing, exactly, whether Jens would even open the door. Make this a slow West-Norwegian fishing-village drama, with a melancholic Hardanger-fiddle-and-cello score and continuous wharf-and-North-Sea ambient sounds."
    },
    {
        "name": "hard_008",
        "category": "cr",
        "expected_chain": [["StoryAgent"],["ScreenplayAgent"],["KeyFrameAgent"],["VideoAgent"],["AmbienceAgent","MusicAgent"],["AmbienceAgent","MusicAgent"],["AudioMixAgent"],["CompositorAgent"],["done"]],
        "user_goal": "Here's my story I want to process: The fire that destroyed the Rua dos Lavradouros bookshop in Porto on the night of 12 February 1987 also destroyed the only known complete copy of the 1788 Inácio de Vasconcelos manuscript on the Lisbon earthquake's psychological aftermath, a manuscript that Idalina Camões, the bookshop's owner and herself a retired professor of eighteenth-century Portuguese letters, had been quietly transcribing in private for the previous nine years and which she had not yet published because she had wanted, before doing so, to verify three citations against an archive in Coimbra she could not yet afford to visit. On the morning after the fire she walked through the wet ash of her own shop in a wool overcoat that smelled of smoke, looking for a fragment, anything, of the manuscript that might have survived; she found nothing. That afternoon, in the kitchen of the small upstairs apartment that had also burned but less completely, she sat at her dining table and began, from memory, to reconstruct the entire 412-page manuscript. The reconstruction took her seven years. Produce this as a contemplative Portuguese literary drama with a sparse cello-and-piano score and continuous old-Porto-rain-and-distant-tram ambient sounds."
    },
    # ===== INTAKE_IMG + CR (long-story with image upload) =====
    # Shape: IntakeImage > Brief > Story > Screenplay > KF > Video > Compositor
    {
        "name": "hard_009",
        "category": "intake_img",
        "expected_chain": [["IntakeImageAgent"],["BriefEnricherAgent"],["StoryAgent"],["ScreenplayAgent"],["KeyFrameAgent"],["VideoAgent"],["CompositorAgent"],["done"]],
        "user_goal": "I've uploaded a sepia-toned portrait of an elderly Tuvan throat singer with a horsehead-fiddle leaning against his weathered chair. Use him as the protagonist for the following story: Galsan Khövüülen had been the senior khoomei singer of the Khorum-Dag valley for forty years and had taught the techniques of sygyt and kargyraa to seventeen apprentices over that span, of whom only three had stayed in the valley and of whom only one, a young woman named Aiu who had come from a Buryat family across the border, had truly grasped what he could teach. When he was seventy-eight he learned that Aiu, who had moved to Kyzyl six years before to teach throat-singing at a children's music school, had been diagnosed with throat cancer and had been told she would not sing again. Galsan packed his igil into a felt case, walked out of his yurt, and began the four-day ride to Kyzyl on a borrowed horse, intending to teach her the silent meditation versions of the techniques his own teacher had given him in his last winter. Make this into a quiet Siberian period drama."
    },
    # Shape: IntakeImage > Brief > Story > Screenplay > KF > Video > Music > AudioMix > Compositor
    {
        "name": "hard_010",
        "category": "intake_img",
        "expected_chain": [["IntakeImageAgent"],["BriefEnricherAgent"],["StoryAgent"],["ScreenplayAgent"],["KeyFrameAgent"],["VideoAgent"],["MusicAgent"],["AudioMixAgent"],["CompositorAgent"],["done"]],
        "user_goal": "Here's a portrait of a young Burmese harpist with a saung gauk in her lap, soft afternoon light. Use her in this narrative: Khin Su Wai had grown up in Yangon studying the saung-gauk under her great-aunt, had moved to Mandalay at twenty-one to study under the master Inle Myint, and at twenty-six had won the country's last open competition before the political crackdowns made such competitions illegal. After her great-aunt's death she inherited not only the family harp—a 102-year-old instrument made of acacia and silk strings, wrapped in a maroon cloth that had been her great-aunt's wedding wrap—but also a small leather notebook of compositions her great-aunt had written down secretly during the years when traditional music was discouraged, sixteen of which had never been performed publicly. Khin Su Wai had been carrying the notebook in her bag for three years before she finally arranged, with some difficulty, a small private salon for ten listeners in a Yangon teahouse, where she would perform the sixteen pieces in a single sitting. The afternoon of the salon she sat alone in the empty teahouse for an hour before the listeners arrived, retuning the harp slowly, listening to the wood. Make this a quiet Burmese period drama with a sparse saung-gauk-and-pat-waing background score."
    },
    # ===== STYLE TRANSFER (single-step, harder by abstract phrasing) =====
    # Shape: IntakeVideo > StyleTransfer > done (no Compositor; pure style)
    {
        "name": "hard_011",
        "category": "style",
        "expected_chain": [["IntakeVideoAgent"],["StyleTransferAgent"],["done"]],
        "user_goal": "I have a 90-second observational clip of an empty courtroom shot at golden-hour, soft natural light through high windows, with no people and no sound. I want to lift it from documentary realism into something quietly oneiric—keep every spatial detail intact, but reframe the entire atmosphere as if it were a remembered painting from the 1960s American school of magical realism, no narration, no soundtrack additions, just the visual transformation."
    },
    {
        "name": "hard_012",
        "category": "style",
        "expected_chain": [["IntakeVideoAgent"],["StyleTransferAgent"],["done"]],
        "user_goal": "Here's a clip of two beekeepers tending hives in a Provençal lavender field, summer noon, twelve seconds of slow handheld footage. Re-render it so that it feels like a frame-by-frame oil-pastel animation by someone in the Bonnard tradition; nothing else, no audio, no titles, no extension."
    },
    # Shape: IntakeVideo > StyleTransfer > Trans > Compositor (style + mono subs)
    {
        "name": "hard_013",
        "category": "style",
        "expected_chain": [["IntakeVideoAgent"],["StyleTransferAgent"],["TranscriptionAgent"],["CompositorAgent"],["done"]],
        "user_goal": "I'm sending in a 4-minute Quebecois interview clip with a folk-instrument luthier who speaks fairly fast, mostly Joual French, and the original audio is excellent but the visual texture is dated digital. I'd like the whole interview re-skinned as if it had been shot on 16mm Kodak film stock from the early 70s with the period chemistry, and English captions burned in for the spoken content (not a translation track, just an accessibility transcript that happens to be English-rendered)."
    },
    # Shape: IntakeVideo > StyleTransfer > Trans > Translation > Compositor (style + bilingual)
    {
        "name": "hard_014",
        "category": "style",
        "expected_chain": [["IntakeVideoAgent"],["StyleTransferAgent"],["TranscriptionAgent"],["TranslationAgent"],["CompositorAgent"],["done"]],
        "user_goal": "I'm working on a teaching reel from a 1991 archival recording of a Cantonese ceramics master—the original tape is grainy NTSC, the audio is intact Cantonese, his apprentice asks questions in the background. I'd like the visuals reanimated as a hand-cut Chinese paper-cutting motion-graphics piece (jiǎnzhǐ), and I need the master's spoken Cantonese rendered as bilingual Chinese-English subtitles for international distribution."
    },
    # ===== EXTEND (single-step, harder by abstract goal) =====
    # Shape: IntakeVideo > VideoExtend > done
    {
        "name": "hard_015",
        "category": "extend",
        "expected_chain": [["IntakeVideoAgent"],["VideoExtendAgent"],["done"]],
        "user_goal": "I'm uploading the closing 5 seconds of a wordless dance solo—the dancer holds a final pose looking off-camera. The piece needs to breathe a little longer, maybe twenty-two seconds total, the held pose extending into stillness without anything new entering the frame, no audio additions of any kind, no other modifications."
    },
    # Shape: IntakeVideo > VideoExtend > Trans > Compositor (extend + mono subs)
    {
        "name": "hard_016",
        "category": "extend",
        "expected_chain": [["IntakeVideoAgent"],["VideoExtendAgent"],["TranscriptionAgent"],["CompositorAgent"],["done"]],
        "user_goal": "I have an 11-second clip of an oral historian mid-sentence describing her childhood in 1962 East Berlin—she trails off and we cut. Could you continue the moment for another fifteen seconds so that her trailing sentence finishes naturally, then add captions to whatever spoken language is already in the source (it's German), with the captions in the same language she's speaking, not translated."
    },
    # Shape: IntakeVideo > VideoExtend > Music > AudioMix > Compositor (extend + music)
    {
        "name": "hard_017",
        "category": "extend",
        "expected_chain": [["IntakeVideoAgent"],["VideoExtendAgent"],["MusicAgent"],["AudioMixAgent"],["CompositorAgent"],["done"]],
        "user_goal": "Here's a 6-second pre-monsoon shot of a Goan estuary, palm leaves bending, dark sky, no movement of people. The piece needs to extend into about twenty-eight seconds of held pre-storm tension, and underneath I'd like a slow ambient-electronic background score keyed to the same expectant register—nothing percussive, nothing melodic-foregrounded, just held tension. No spoken text at all in any layer."
    },
    # ===== HIGHLIGHT (with various add-ons) =====
    # Shape: IntakeVideo > VideoAnalysis > Highlight > done (highlight only, no Compositor)
    {
        "name": "hard_018",
        "category": "highlight",
        "expected_chain": [["IntakeVideoAgent"],["VideoAnalysisAgent"],["HighlightAgent"],["done"]],
        "user_goal": "I have eighteen hours of unedited courtroom recording from a high-profile Italian organized-crime trial in 1996. I want a structural cutdown that surfaces only the moments where the prosecution successfully pivots a hostile witness—nothing else, just those pivot moments threaded together, no audio sweetening, no captions, no other post-processing of any kind."
    },
    # Shape: IntakeVideo > VidAnalysis > Highlight > Trans > Compositor (highlight + mono subs)
    {
        "name": "hard_019",
        "category": "highlight",
        "expected_chain": [["IntakeVideoAgent"],["VideoAnalysisAgent"],["HighlightAgent"],["TranscriptionAgent"],["CompositorAgent"],["done"]],
        "user_goal": "I have a 4-hour archival recording of a 1987 Kenya National Theater production of Ngugi wa Thiong'o's Ngaahika Ndeenda performed mostly in Gikuyu with some Swahili passages. I'd like a 3-minute curated selection of the production's most charged confrontation scenes between the two patriarchs, presented exactly as performed (no language change), but with captions in whatever language the actors are speaking at each moment, burned in for accessibility."
    },
    # Shape: IntakeVideo > VidAnalysis > Highlight > Music > AudioMix > Compositor (highlight + music)
    {
        "name": "hard_020",
        "category": "highlight",
        "expected_chain": [["IntakeVideoAgent"],["VideoAnalysisAgent"],["HighlightAgent"],["MusicAgent"],["AudioMixAgent"],["CompositorAgent"],["done"]],
        "user_goal": "Here's 5.5 hours of GoPro footage from a long-distance Mongolian endurance horse race. Pull a 90-second highlight that captures the arc from the morning launch through the most physically punishing midday section to the dusk approach to the final waystation, and lay underneath it a single continuous orchestral score that arcs through three movements matching those three sections—no narration, no subtitles, no ambient sweetening, just the cut and the score."
    },
    # ===== STORYTELLING (illustrated audiobook) =====
    # Shape: IntakeImage > Brief > Narration > [I,Nr] > [I,Nr] > Compositor (text-input image-grounded, no music/ambience)
    {
        "name": "hard_021",
        "category": "storytelling",
        "expected_chain": [["IntakeImageAgent"],["BriefEnricherAgent"],["NarrationAgent"],["IllustrationAgent","NarratorAgent"],["IllustrationAgent","NarratorAgent"],["CompositorAgent"],["done"]],
        "user_goal": "I've uploaded a soft watercolor of an elderly Inuit grandmother braiding her grandchild's hair in a snow-house. I'd like an illustrated audiobook telling of an old Inuktitut creation myth where the sun and moon were once two siblings playing a game of throwing seal-bones across the polar sky, presented entirely as a slow narrator-and-illustration piece—no music underneath, no ambient layer, just the spoken voice over moving illustrations, ending without a translated subtitle track."
    },
    # Shape: IntakeImage > Brief > Narration > [I,Nr] > [I,Nr] > Translation > Compositor (storytelling + Translation only)
    {
        "name": "hard_022",
        "category": "storytelling",
        "expected_chain": [["IntakeImageAgent"],["BriefEnricherAgent"],["NarrationAgent"],["IllustrationAgent","NarratorAgent"],["IllustrationAgent","NarratorAgent"],["TranslationAgent"],["CompositorAgent"],["done"]],
        "user_goal": "Here's a charcoal portrait of an elderly Romani fiddler with deep eye-creases. Tell me a Romani folktale, narrated in Romani, about a fiddler whose violin was once a thorn in the heart of the moon—as an illustrated audiobook with English subtitles for the narration, plain illustrated audiobook only, no ambient layer underneath the narrator's voice and no scored music."
    },
    # Shape: NarrationAgent > [I,Nr] > [I,Nr] > Compositor (text storytelling, no image, no audio)
    {
        "name": "hard_023",
        "category": "storytelling",
        "expected_chain": [["NarrationAgent"],["IllustrationAgent","NarratorAgent"],["IllustrationAgent","NarratorAgent"],["CompositorAgent"],["done"]],
        "user_goal": "Here's my story I want to process: Long before the sea was salt, the kingdom of Aeren-Shan held a cup of fresh water at its center, and the cup was guarded by a thousand sparrows who took turns drinking from it so that no single bird would ever know its taste. The sparrow named Iri-Sho was the one who broke the rule. Iri-Sho was the smallest of the thousand and had been chosen as a guard because she could not fly far enough to be a messenger. She had heard the others speak of the cup's water for forty seasons and on a winter morning when the others were elsewhere she landed on the cup's golden rim, leaned over, and tasted. The water that fell from her beak became, over the next thousand years, the salt of every sea on the earth. Tell this as an illustrated audiobook—just narration and illustration, no music, no ambience, no translation."
    },
    # Shape: NarrationAgent > [A,I,Nr] x3 > AudioMix > Compositor (text storytelling 3-way IAN, no music)
    {
        "name": "hard_024",
        "category": "storytelling",
        "expected_chain": [["NarrationAgent"],["AmbienceAgent","IllustrationAgent","NarratorAgent"],["AmbienceAgent","IllustrationAgent","NarratorAgent"],["AmbienceAgent","IllustrationAgent","NarratorAgent"],["AudioMixAgent"],["CompositorAgent"],["done"]],
        "user_goal": "Here's my story I want to process: The Lighthouse-Keeper's Daughter and the Iron Whale tells of a girl whose father has tended the Stør lighthouse in West Greenland for forty winters and whose mother has been missing at sea for ten of those, when one night a creature half-iron and half-flesh comes ashore in the harbor mouth. Tell this as an illustrated audiobook with continuous Greenland-coastal-storm ambience layered under the narration, narrator and illustration moving together, no separate music score and no translated subtitle track."
    },
    # Shape: IntakeImg+Brief>Narration>[A,I,M,Nr]x4>AudioMix>Compositor (image storytelling 4-way, no Translation)
    {
        "name": "hard_025",
        "category": "storytelling",
        "expected_chain": [["IntakeImageAgent"],["BriefEnricherAgent"],["NarrationAgent"],["AmbienceAgent","IllustrationAgent","MusicAgent","NarratorAgent"],["AmbienceAgent","IllustrationAgent","MusicAgent","NarratorAgent"],["AmbienceAgent","IllustrationAgent","MusicAgent","NarratorAgent"],["AmbienceAgent","IllustrationAgent","MusicAgent","NarratorAgent"],["AudioMixAgent"],["CompositorAgent"],["done"]],
        "user_goal": "I've uploaded a portrait of an elder Sami yoiker in a winter gakti coat, snow on his beard. Use him as the speaker-protagonist of an illustrated audiobook telling of how the first joik was given to the Sami by a reindeer-spirit who wanted to teach humans the language of mountain weather. Full audiobook treatment: narration in plain English, illustrations moving across the page, a sparse joik-and-frame-drum score, and high-tundra wind ambience underneath—keep it monolingual, no translated subtitle layer."
    },
    # ===== AUDIO-ONLY (existing video + audio overlay) =====
    # Shape: IntakeVideo > Music > AudioMix > Compositor (just music)
    {
        "name": "hard_026",
        "category": "audio",
        "expected_chain": [["IntakeVideoAgent"],["MusicAgent"],["AudioMixAgent"],["CompositorAgent"],["done"]],
        "user_goal": "I have a 4-minute observational clip of an Italian fishmonger setting up his market stall before dawn—the original audio is the natural fish-market sounds and I want to keep none of that, replacing the entire audio bed with a melancholy solo-cello piece keyed to the lonely pre-dawn quality of the visuals; no narration, no captions, no ambient layering, just the piece replaced with a continuous cello score."
    },
    # Shape: IntakeVideo > Ambience > AudioMix > Compositor (just ambience)
    {
        "name": "hard_027",
        "category": "audio",
        "expected_chain": [["IntakeVideoAgent"],["AmbienceAgent"],["AudioMixAgent"],["CompositorAgent"],["done"]],
        "user_goal": "Here's 90 seconds of silent timelapse footage of a glacier calving in Svalbard. The clip currently has no audio whatsoever and I want to add only an environmental-sound bed—the deep ice-crack-and-arctic-wind layer—not music, not narration, not captions, only the natural-ambience layer added beneath."
    },
    # ===== MULTI-PRIMARY (complex chains — known model weakness) =====
    # Shape: IntakeVideo > VidAnalysis > StoryAgent > Screenplay > KF > Video > Compositor (analyze + sequel CR)
    {
        "name": "hard_028",
        "category": "complex",
        "expected_chain": [["IntakeVideoAgent"],["VideoAnalysisAgent"],["StoryAgent"],["ScreenplayAgent"],["KeyFrameAgent"],["VideoAgent"],["CompositorAgent"],["done"]],
        "user_goal": "I have a 6-minute pilot for a Korean political mini-drama that ends on a cliffhanger involving the assassination of a parliamentary aide. Read its tone and political register, then write and produce me an entirely new follow-up mini-drama—not a stylistic re-skin of the original footage, an actual new generated drama—set in the same political universe but six months after the events of the pilot, focused on the aide's sister beginning her own quiet investigation. No subtitles, no music, no ambience added; just the new generated drama, plainly cut."
    },
    # Shape: IntakeVideo > VidAnal > Story > Screenplay > KF > Video > Trans > Compositor (analyze+sequel+mono subs)
    {
        "name": "hard_029",
        "category": "complex",
        "expected_chain": [["IntakeVideoAgent"],["VideoAnalysisAgent"],["StoryAgent"],["ScreenplayAgent"],["KeyFrameAgent"],["VideoAgent"],["TranscriptionAgent"],["CompositorAgent"],["done"]],
        "user_goal": "Here is a 7-minute Mexican narco-thriller pilot—analyze it for character archetypes, narrative pacing, and visual register, and on that basis generate a new mini-drama set in the same world but a generation later, following the daughter of one of the surviving cartel lieutenants. The new drama should be in plain Spanish dialogue with English captions burned in—monolingual captioning track on the new generated drama, not bilingual, not translated."
    },
    # Shape: IntakeVideo > VidExtend > Style > done (extend + style, no Compositor — single-output)
    {
        "name": "hard_030",
        "category": "complex",
        "expected_chain": [["IntakeVideoAgent"],["VideoExtendAgent"],["StyleTransferAgent"],["done"]],
        "user_goal": "I have a 5-second clip of waves washing over a tide-pool. I'd like the moment expanded to 28 seconds of slow held breath, then re-rendered as a Hokusai-style woodblock animation, and produced as the bare visual artifact—no audio, no titles, no other manipulation."
    },
    # Shape: IntakeVideo > Style > VideoExtend > Music > AudioMix > Compositor (style+extend+music)
    {
        "name": "hard_031",
        "category": "complex",
        "expected_chain": [["IntakeVideoAgent"],["StyleTransferAgent"],["VideoExtendAgent"],["MusicAgent"],["AudioMixAgent"],["CompositorAgent"],["done"]],
        "user_goal": "Here's a 7-second handheld clip of two children running through a Mediterranean wheatfield at noon. I'd like the visuals reframed as if shot in the Studio Ghibli summer-of-1988 palette, the moment held for another twenty seconds in the new style, and underneath a sparse acoustic-guitar-and-recorder score that breathes with the visual; no captions, no ambient layer in addition to the score, no narration."
    },
    # Shape: IntakeVideo > VidExtend > StyleTransfer > Trans > Compositor (extend+style+mono subs)
    {
        "name": "hard_032",
        "category": "complex",
        "expected_chain": [["IntakeVideoAgent"],["VideoExtendAgent"],["StyleTransferAgent"],["TranscriptionAgent"],["CompositorAgent"],["done"]],
        "user_goal": "Here's an 11-second courtroom outburst in the original Russian from a 1989 Soviet-era television drama—I want it lengthened to about thirty seconds with the prosecutor's monologue allowed to land, then re-skinned as a Soviet propaganda-poster animation, and lastly captioned in the same language the actor is speaking (Russian), no translation track."
    },
    # Shape: IntakeImg > Brief > Story > Screenplay > KF > Video > VideoExtend > Compositor (img+CR+extend)
    {
        "name": "hard_033",
        "category": "complex",
        "expected_chain": [["IntakeImageAgent"],["BriefEnricherAgent"],["StoryAgent"],["ScreenplayAgent"],["KeyFrameAgent"],["VideoAgent"],["VideoExtendAgent"],["CompositorAgent"],["done"]],
        "user_goal": "I'm uploading a watercolor of a young Iraqi calligrapher at her desk in a Basra apartment, late afternoon light. Use her as the protagonist for the following narrative: Sabreen had been training under her uncle for eleven years when the war forced his school to close, and on the day her uncle handed her his last unfinished manuscript and asked her to finish it. Generate a 90-second mini-drama from this brief and pull the moment of his handing-her-the-manuscript out into a longer ten-second held beat for emphasis—plainly produced, no audio additions, no captions."
    },
    # ===== INTAKE_IMG + CR (more variants with full audio + bilingual) =====
    # Shape: Img>Brief>Story>...>Video>Trans>Translation>M>AudioMix>Compositor (img+CR+bilingual+music)
    {
        "name": "hard_034",
        "category": "intake_img",
        "expected_chain": [["IntakeImageAgent"],["BriefEnricherAgent"],["StoryAgent"],["ScreenplayAgent"],["KeyFrameAgent"],["VideoAgent"],["TranscriptionAgent"],["TranslationAgent"],["MusicAgent"],["AudioMixAgent"],["CompositorAgent"],["done"]],
        "user_goal": "I've uploaded a portrait of a young female Tibetan thangka painter in monastic robes, holding a small brush. Use her as the central protagonist of this story: When Yangchen Drolma was twenty-eight she was commissioned to repaint the central figure of an 18th-century thangka that had been damaged during the Cultural Revolution, a project that the senior painters at her gompa had refused on the grounds that it could not be done without the original artist's spiritual blessing, which had been lost. Yangchen accepted the commission against the gompa's quiet disapproval, and over the next eight months she discovered, through dreams she insisted were not metaphors, who the original painter had been. Make this a full Tibetan period mini-drama in original Tibetan dialogue with both Tibetan and English bilingual subtitles, plus a meditative dranyen-and-singing-bowl score (no separate ambient layer)."
    },
    # Shape: Img+Brief+Story+...+Video+M+A+AudioMix+Compositor (img+CR+M+A, no subs)
    {
        "name": "hard_035",
        "category": "intake_img",
        "expected_chain": [["IntakeImageAgent"],["BriefEnricherAgent"],["StoryAgent"],["ScreenplayAgent"],["KeyFrameAgent"],["VideoAgent"],["AmbienceAgent","MusicAgent"],["AmbienceAgent","MusicAgent"],["AudioMixAgent"],["CompositorAgent"],["done"]],
        "user_goal": "Here's a sketch of an elderly Catalan shepherd standing in a Pyrenean stone-walled pasture at dusk, dog at his feet. Use him as the protagonist of: Eloi Cabré had walked the same eight-kilometer transhumance route between his summer pasture above Pal and his winter pasture below Sant Julià for fifty-one autumns, on foot, leading a dwindling flock that had once numbered three hundred and now numbered twenty-six. On the autumn that he was seventy-six, on the second day of the descent, his dog Roca, who had walked the route with him for thirteen years, sat down on a particular rock at the halfway pass and refused to continue. Make this a slow Catalan mountain drama with a melancholy clarinet-and-cello score and continuous Pyrenean-pasture-bell-and-wind ambient sounds (no spoken-text captioning)."
    },
    # ===== HIGHLIGHT + STYLE / + AUDIO COMBOS =====
    # Shape: IntakeVid > VidAnal > Highlight > Music > AudioMix > Compositor (highlight + music) — already covered, skip
    # Shape: IntakeVid > VidAnal > Highlight > [M,T] > [M,T] > AudioMix > Compositor (highlight + music + mono subs)
    {
        "name": "hard_036",
        "category": "highlight",
        "expected_chain": [["IntakeVideoAgent"],["VideoAnalysisAgent"],["HighlightAgent"],["MusicAgent","TranscriptionAgent"],["MusicAgent","TranscriptionAgent"],["AudioMixAgent"],["CompositorAgent"],["done"]],
        "user_goal": "I have eight hours of unedited footage from a 1998 South African Truth and Reconciliation Commission hearing in Cape Town—mostly in English with stretches of Xhosa and Afrikaans interleaved. Pull the most charged single-witness testimony moments into a 5-minute curated cut, with a sparse cello-and-mbira score laid underneath that respects the gravity of the testimony, and accessibility captions burned in for whatever language is being spoken in each moment (no translation track, just live captioning of the source language)."
    },
    # ===== SUB-VID (existing video with subtitle work) =====
    # Shape: IntakeVid > Trans > Compositor (mono subs to existing video)
    {
        "name": "hard_037",
        "category": "sub_vid",
        "expected_chain": [["IntakeVideoAgent"],["TranscriptionAgent"],["CompositorAgent"],["done"]],
        "user_goal": "I have a 22-minute lecture given in 1981 by an elderly Galician folklorist on the survival of pre-Christian solstice rituals in the rural northwest. The lecture is in Galician, the audio is fine but no captioning has ever existed for it. Add accessibility captions in the same language being spoken (Galician), no translation, no other modifications to image or audio."
    },
    # Shape: IntakeVid > Trans > Translation > Compositor (bilingual on existing video)
    {
        "name": "hard_038",
        "category": "sub_vid",
        "expected_chain": [["IntakeVideoAgent"],["TranscriptionAgent"],["TranslationAgent"],["CompositorAgent"],["done"]],
        "user_goal": "Here's a 14-minute oral-history interview recorded in 2003 with a 91-year-old Yiddish-speaking former garment-worker in Montreal who is reminiscing about her cousins lost in the Vilna ghetto. Her language is Yiddish with occasional English words. The footage is fine and I want it preserved exactly as recorded but with English-translated subtitles burned in, full bilingual track (the source Yiddish stays as captions plus the English translation track), nothing else added or removed."
    },
    # ===== BILINGUAL CR — long story, multi-cultural =====
    # Shape: Story>Screenplay>KF>Video>Trans>Translation>M>AudioMix>Compositor (CR+bilingual+music)
    {
        "name": "hard_039",
        "category": "bilingual",
        "expected_chain": [["StoryAgent"],["ScreenplayAgent"],["KeyFrameAgent"],["VideoAgent"],["TranscriptionAgent"],["TranslationAgent"],["MusicAgent"],["AudioMixAgent"],["CompositorAgent"],["done"]],
        "user_goal": "Make a slow period drama about a young female Hungarian violinist in 1956 Budapest who, on the night of the Soviet intervention, has to choose between performing her Conservatory entrance audition the following morning and helping her physician brother evacuate forty-three wounded students from the Conservatory's basement. Original Hungarian dialogue with Hungarian-English bilingual subtitles, layered with a melancholy violin-and-cimbalom-and-strings score that quietly mirrors the Bartók she was supposed to play in the audition (no separate ambient layer beyond the score)."
    },
    # ===== MORE COMPLEX (Style + Highlight + Subs) =====
    # Shape: IntakeVid > VidAnal > Highlight > Style > Trans > Compositor (highlight + style + mono subs)
    {
        "name": "hard_040",
        "category": "complex",
        "expected_chain": [["IntakeVideoAgent"],["VideoAnalysisAgent"],["HighlightAgent"],["StyleTransferAgent"],["TranscriptionAgent"],["CompositorAgent"],["done"]],
        "user_goal": "Here's 90 minutes of unedited footage from an Argentine ambient-theater production performed in a disused railway station in 2007—a deeply experimental piece in Spanish with sporadic Portuguese loanwords. Pull the most theatrically charged sequences into a 4-minute curated cut, then re-skin the cut as if it were filmed on degraded super-8 film stock, and burn in monolingual captions for whichever language is spoken at each moment (no translation track)."
    },
    # ===== MORE STORYTELLING — text only, longer =====
    # Shape: NarrationAgent > [I,M,Nr] x3 > AudioMix > Compositor (text storytelling 3-way IMN)
    {
        "name": "hard_041",
        "category": "storytelling",
        "expected_chain": [["NarrationAgent"],["IllustrationAgent","MusicAgent","NarratorAgent"],["IllustrationAgent","MusicAgent","NarratorAgent"],["IllustrationAgent","MusicAgent","NarratorAgent"],["AudioMixAgent"],["CompositorAgent"],["done"]],
        "user_goal": "Here's my story I want to process: There is a Tatar village in the foothills of the Urals where, every spring at the moment the river ice cracks, the villagers tell the story of the Daughter of the River. The Daughter, in the version told in this particular village, is a young woman whose mother was a midwife and whose father was the river itself, who one winter took ill and could not be warmed by any fire, who walked out of her mother's house on the night of the winter solstice and did not return until the spring thaw, when she returned barefoot, in the same dress, carrying in her arms a small fish that lived for exactly eleven days and on the twelfth day became a green stone that the village still keeps. Tell this as an illustrated audiobook with a sparse Tatar-domra-and-flute background score (no ambient layer, no translation)."
    },
    # ===== MORE SHORT-CHAIN STYLE =====
    # Shape: IntakeVid > Style > Music > AudioMix > Compositor (style + music, no subs)
    {
        "name": "hard_042",
        "category": "style",
        "expected_chain": [["IntakeVideoAgent"],["StyleTransferAgent"],["MusicAgent"],["AudioMixAgent"],["CompositorAgent"],["done"]],
        "user_goal": "I have a 90-second observational clip of an Anatolian copper-engraver working at his bench under an open shop window, late afternoon. Re-render the visuals as if rendered on aged Iznik ceramic-tile relief, and underneath lay a contemplative ney-and-saz score that sits at the same patient register as the engraver's hand—no captions, no separate ambient layer, no narration."
    },
    # Shape: IntakeVid > Style > Trans > Music > AudioMix > Compositor (style + mono subs + music)
    {
        "name": "hard_043",
        "category": "style",
        "expected_chain": [["IntakeVideoAgent"],["StyleTransferAgent"],["MusicAgent","TranscriptionAgent"],["MusicAgent","TranscriptionAgent"],["AudioMixAgent"],["CompositorAgent"],["done"]],
        "user_goal": "I'm sending in a 4-minute Welsh-language sermon recording from a small Methodist chapel in 1962—the spoken language is Welsh, fine quality. I want the visuals reanimated as if illuminated-manuscript style, English-language accessibility captions burned in for the spoken Welsh (live captions of source, not translation), and a sparse harp-and-pipe-organ score under the spoken voice."
    },
    # ===== MORE EXTEND VARIANTS =====
    # Shape: IntakeVid > Extend > [M,A] > [M,A] > AudioMix > Compositor (extend + M + A)
    {
        "name": "hard_044",
        "category": "extend",
        "expected_chain": [["IntakeVideoAgent"],["VideoExtendAgent"],["AmbienceAgent","MusicAgent"],["AmbienceAgent","MusicAgent"],["AudioMixAgent"],["CompositorAgent"],["done"]],
        "user_goal": "Here's a 9-second clip of a solitary Bedouin trader leading a single camel across a salt flat at dawn, no movement of dialogue. Stretch the moment to about thirty-five seconds of held desert silence, with a sparse oud-and-rabab score laid underneath, and a low-frequency wind-over-salt-pan ambient bed that doesn't compete with the score; no spoken text added, no captions, just the visual hold and the layered audio."
    },
    # ===== MORE MULTI-PRIMARY =====
    # Shape: IntakeImg > Brief > Story > Screenplay > KF > Video > VideoExtend > Music > AudioMix > Compositor (img+CR+extend+music)
    {
        "name": "hard_045",
        "category": "complex",
        "expected_chain": [["IntakeImageAgent"],["BriefEnricherAgent"],["StoryAgent"],["ScreenplayAgent"],["KeyFrameAgent"],["VideoAgent"],["VideoExtendAgent"],["MusicAgent"],["AudioMixAgent"],["CompositorAgent"],["done"]],
        "user_goal": "I'm uploading a watercolor of a young female Lithuanian organ-builder at a small workbench, surrounded by half-finished pipes, late winter light. Use her as the protagonist for the following narrative: When Birutė Mickevičiūtė was thirty-one she inherited her father's workshop—the last working independent organ-restoration shop in northeastern Lithuania—at a moment when she had three commissions outstanding, no remaining apprentice, and her father's notebook of acoustic measurements that no one else in the country could fully read. The first commission was the restoration of the 1782 organ at the Žemaičių Kalvarija basilica, and on the morning she began to disassemble the organ's keyboard, she discovered a pencil note in her father's hand inside one of the pipes, dated three days before his death, addressed to her by name. Make this into a slow Lithuanian period mini-drama, hold the moment of her finding the note out into a longer 8-second beat for emphasis, and lay underneath a contemplative pipe-organ-and-string-quartet score (no captions, no separate ambient layer)."
    },
]

# verify each has 7 fields and chain is list-of-list
for c in HARD_CASES:
    assert all(k in c for k in ['name','category','expected_chain','user_goal']), c['name']
    assert len(c['expected_chain']) >= 2

print(f"Generated {len(HARD_CASES)} hard cases")

out = Path('/home/zhendong_li/FrameWorkers/evals/director_routing/eval_cases_v4500_hard45.json')
out.write_text(json.dumps(HARD_CASES, indent=2, ensure_ascii=False) + '\n')
print(f"Saved: {out}")

# verify all expected_chain shapes exist in v4_500 (no new shapes!)
v4500 = json.loads(Path('/home/zhendong_li/FrameWorkers/evals/director_routing/eval_cases_v4_500.json').read_text())
def shape_key(chain):
    return tuple(tuple(sorted(l)) if isinstance(l, list) else (l,)
                 for l in chain if l != ['done'] and l != 'done')
v4500_shapes = {shape_key(c['expected_chain']) for c in v4500}
for c in HARD_CASES:
    s = shape_key(c['expected_chain'])
    if s not in v4500_shapes:
        chain_str = ' > '.join('/'.join(l) if len(l)>1 else l[0] for l in s)
        print(f"  ⚠ {c['name']}: NEW SHAPE not in v4_500: {chain_str}")
print(f"\nshape verification: all 45 hard cases use existing v4_500 shapes ✓" if all(shape_key(c['expected_chain']) in v4500_shapes for c in HARD_CASES) else "\n⚠ some shapes not in v4_500")
EOF
