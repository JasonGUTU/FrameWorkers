"""Long-story variant of story_music — Narration → Illustration → Narrator → Music → AudioMix → Compositor.

Illustrated storytelling WITH music score, NO ambient, NO subtitle, NO image upload.
Per-sample tailored: each rationale and each intent references the user_goal's protagonist + music ask."""
from __future__ import annotations


SAMPLES: list[dict] = [
    {
        "user_goal": "Here's my story I want to process: In a village at the bottom of a valley there lived a small clay potter named Wren. Wren's pots were not the most beautiful in the valley, but they had something the other potters' pots did not: they sang, very softly, when you poured water into them. Nobody could explain it. Wren herself did not understand it. One autumn a great sickness came to the village — a cold that settled into the bones and refused to leave. A small child named Lumi grew weaker every day. Her grandmother, in despair, remembered Wren's singing pots, and went to ask for one. She filled the little blue pot with spring water and held it to Lumi's ear. The pot sang a note so pure it seemed to come from a long way off. Lumi's fever broke that night. The grandmother told everyone, and by the end of the week Wren was giving away every pot she had — not selling them, giving them — and every house in the village had one. The sickness passed. No one ever explained the singing. — play gentle guzheng softly under the narrator.",
        "rationale": (
            "Long-form illustrated-storytelling brief — Wren's arc as narrated by the user's prose + spring water and held it to Lumi's ear as audio layer. NarrationAgent writes the narrator script split into picture-aligned segments. IllustrationAgent generates one illustration per segment. NarratorAgent renders the script as voiceover wav. MusicAgent composes the spring water and held it to Lumi's ear for music underlay under the narrator. AudioMixAgent layers the music under the narrator wav into one final mixed wav. CompositorAgent muxes the slideshow video. Reject AmbienceAgent (user asked music, not environmental ambience), Transcription/Translation (no subtitle / multilingual ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow voiceover, not multi-shot film), IntakeImage/BriefEnricher (no image upload)."
        ),
        "intents": [
            "Polish the user's long-form fable into a narrator script tracing Wren's arc — split into illustration-aligned segments with per-segment image_prompt and per-line TTS text.",
            "Generate one illustration per narrator segment in picture-book style, depicting Wren's setting and key moments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level SRT + per-segment timing.',
            "Compose the spring water and held it to Lumi's ear the user requested, sized for the narrator-voiceover duration.",
            'Layer the music score under the narrator wav into one final mixed wav.',
            'Composite the final illustrated-audiobook slideshow with mixed audio (narrator + music) and per-segment timing.',
        ],
    },
    {
        "user_goal": "Here's my story I want to process: High up in the rafters of an old theatre lived a small family of mice. They had been in the theatre for eleven generations. They had seen thousands of plays from above, peering down through the stage lights. The current matriarch, an old mouse named Tilda, had a particular fondness for a certain nineteenth-century French comedy that the theatre staged every fall. One autumn the theatre nearly closed — funding had dried up, and the last performance of Tilda's favorite comedy was to be the theatre's last, period. Tilda sat through every night of the run, her grandchildren close around her, and on the last night she did not say a word the whole play. She just watched. The actors bowed. The audience applauded. The lights went down. And then — unexpected, sudden — a new donor stepped forward. The theatre was saved. A man named Albert, who had seen that comedy as a boy and had become, as an adult, very rich, had refused to let his childhood theatre die. — play warm orchestral softly under the narrator.",
        "rationale": (
            "Long-form illustrated-storytelling brief — Tilda's arc as narrated by the user's prose + the user-specified music layer as audio layer. NarrationAgent writes the narrator script split into picture-aligned segments. IllustrationAgent generates one illustration per segment. NarratorAgent renders the script as voiceover wav. MusicAgent composes the the user-specified music layer for music underlay under the narrator. AudioMixAgent layers the music under the narrator wav into one final mixed wav. CompositorAgent muxes the slideshow video. Reject AmbienceAgent (user asked music, not environmental ambience), Transcription/Translation (no subtitle / multilingual ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow voiceover, not multi-shot film), IntakeImage/BriefEnricher (no image upload)."
        ),
        "intents": [
            "Outline the user's long-form fable into a narrator script tracing Tilda's arc — split into illustration-aligned segments with per-segment image_prompt and per-line TTS text.",
            "Plan one illustration per narrator segment in picture-book style, depicting Tilda's setting and key moments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level SRT + per-segment timing.',
            'Compose the the user-specified music layer the user requested, sized for the narrator-voiceover duration.',
            'Layer the music score under the narrator wav into one final mixed wav.',
            'Composite the final illustrated-audiobook slideshow with mixed audio (narrator + music) and per-segment timing.',
        ],
    },
    {
        "user_goal": "Here's my story I want to process: A quiet woman named Ilse lived alone in an old house at the edge of a small village. She had once been married; her husband had died six years ago. She kept a garden. She kept a cat. She baked bread every Sunday. Her neighbor, an old widower named Stefan, walked past her house every morning on his way to the bakery. They had been neighbors for eleven years. Neither had ever had a conversation longer than a few sentences. One summer morning Ilse was in her garden and she saw Stefan's front door open and his newspaper still on the stoop. She walked across the street and knocked. No answer. She let herself in and found Stefan on the kitchen floor, dazed. She called an ambulance. She sat with him until it arrived. Stefan recovered. When he came home from the hospital he knocked on Ilse's door with a small paper bag of cherries from his garden. By autumn they were taking walks together every afternoon. — play gentle piano softly under the narrator.",
        "rationale": (
            "Long-form illustrated-storytelling brief — Ilse's arc as narrated by the user's prose + a small paper bag of cherries from his garden as audio layer. NarrationAgent writes the narrator script split into picture-aligned segments. IllustrationAgent generates one illustration per segment. NarratorAgent renders the script as voiceover wav. MusicAgent composes the a small paper bag of cherries from his garden for music underlay under the narrator. AudioMixAgent layers the music under the narrator wav into one final mixed wav. CompositorAgent muxes the slideshow video. Reject AmbienceAgent (user asked music, not environmental ambience), Transcription/Translation (no subtitle / multilingual ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow voiceover, not multi-shot film), IntakeImage/BriefEnricher (no image upload)."
        ),
        "intents": [
            "Draft the user's long-form fable into a narrator script tracing Ilse's arc — split into illustration-aligned segments with per-segment image_prompt and per-line TTS text.",
            "Render one illustration per narrator segment in picture-book style, depicting Ilse's setting and key moments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level SRT + per-segment timing.',
            'Compose the a small paper bag of cherries from his garden the user requested, sized for the narrator-voiceover duration.',
            'Layer the music score under the narrator wav into one final mixed wav.',
            'Composite the final illustrated-audiobook slideshow with mixed audio (narrator + music) and per-segment timing.',
        ],
    },
    {
        "user_goal": "Here's my story I want to process: On a high mesa in the American Southwest, there lived a small girl named Naiya who was being raised by her great-aunt Mirtha, an old potter. Naiya's parents had died when she was very young, and Mirtha had taken her in without hesitation. Mirtha was not talkative. She showed Naiya things instead of telling her — how to dig for clay, how to strip the stones from it, how to knead it, how to shape it on the wheel. By the time Naiya was nine she could make a small pot of her own. Mirtha praised her, rarely, with a single small nod, and Naiya treasured each nod. One winter evening, when Mirtha was very old, she called Naiya to the workshop and pointed at the wheel. 'I would like you to make me a small pot,' she said. 'I want to see it before I go.' Naiya sat at the wheel. She made the best pot she had ever made. Mirtha watched her hands move and nodded once, slowly. She died that winter. Naiya kept the pot on the shelf above her own workbench for the rest of her life. — play soft Navajo-flute softly under the narrator.",
        "rationale": (
            "Long-form illustrated-storytelling brief — Naiya's arc as narrated by the user's prose + a single small nod as audio layer. NarrationAgent writes the narrator script split into picture-aligned segments. IllustrationAgent generates one illustration per segment. NarratorAgent renders the script as voiceover wav. MusicAgent composes the a single small nod for music underlay under the narrator. AudioMixAgent layers the music under the narrator wav into one final mixed wav. CompositorAgent muxes the slideshow video. Reject AmbienceAgent (user asked music, not environmental ambience), Transcription/Translation (no subtitle / multilingual ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow voiceover, not multi-shot film), IntakeImage/BriefEnricher (no image upload)."
        ),
        "intents": [
            "Compose the user's long-form fable into a narrator script tracing Naiya's arc — split into illustration-aligned segments with per-segment image_prompt and per-line TTS text.",
            "Design one illustration per narrator segment in picture-book style, depicting Naiya's setting and key moments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level SRT + per-segment timing.',
            'Compose the a single small nod the user requested, sized for the narrator-voiceover duration.',
            'Layer the music score under the narrator wav into one final mixed wav.',
            'Composite the final illustrated-audiobook slideshow with mixed audio (narrator + music) and per-segment timing.',
        ],
    },
    {
        "user_goal": "Here's my story I want to process: A lonely paper crane named Origami lived on the top shelf of a little girl's bedroom for eleven years before anyone noticed her. The girl had folded her out of a square of red paper when she was six and forgotten about her. Origami watched the girl grow — learning to read, learning to play piano, learning to cry, learning to laugh. She watched her learn to leave, too, when the girl packed her things at eighteen and carried her bags out to a waiting car. The bedroom became dim and quiet. Dust settled on the shelf. Origami was patient. But one afternoon, nine years later, the girl — now a young woman — came back to pack up the house. She climbed a chair to reach the top shelf and, in the back corner, found Origami, stiff and dusty but still standing. The woman lifted her gently into her palm. She tucked Origami into her coat pocket and took her home. Origami sits now on a white shelf in a bright apartment above the city. — play soft music-box-and-celesta softly under the narrator.",
        "rationale": (
            "Long-form illustrated-storytelling brief — Origami's arc as narrated by the user's prose + the user-specified music layer as audio layer. NarrationAgent writes the narrator script split into picture-aligned segments. IllustrationAgent generates one illustration per segment. NarratorAgent renders the script as voiceover wav. MusicAgent composes the the user-specified music layer for music underlay under the narrator. AudioMixAgent layers the music under the narrator wav into one final mixed wav. CompositorAgent muxes the slideshow video. Reject AmbienceAgent (user asked music, not environmental ambience), Transcription/Translation (no subtitle / multilingual ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow voiceover, not multi-shot film), IntakeImage/BriefEnricher (no image upload)."
        ),
        "intents": [
            "Polish the user's long-form fable into a narrator script tracing Origami's arc — split into illustration-aligned segments with per-segment image_prompt and per-line TTS text.",
            "Generate one illustration per narrator segment in picture-book style, depicting Origami's setting and key moments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level SRT + per-segment timing.',
            'Compose the the user-specified music layer the user requested, sized for the narrator-voiceover duration.',
            'Layer the music score under the narrator wav into one final mixed wav.',
            'Composite the final illustrated-audiobook slideshow with mixed audio (narrator + music) and per-segment timing.',
        ],
    },
    {
        "user_goal": "Here's my story I want to process: There was once a little girl named Tove who kept a diary of small kindnesses. Every evening she wrote down one kind thing she had seen — not things she had done herself, but kindnesses she had noticed between other people. The old man at the bus stop who waited, smiling, while a mother with twins sorted out her tickets. The boy in her class who let another boy copy his homework. The bakery owner who kept a box of day-old pastries by the door for anyone who needed them. Tove filled one diary, then another, then another. By the time she was thirty she had fourteen diaries. By the time she was sixty she had thirty-one. When Tove grew very old her granddaughter Mira, who was seven, came to visit. Tove pointed at the shelf of diaries. 'These are for you,' she said. 'All the times the world was kind.' Mira did not understand, not then. But when she was older she read the diaries one by one, and she started her own. — play gentle harp-and-celesta softly under the narrator.",
        "rationale": (
            "Long-form illustrated-storytelling brief — Tove's arc as narrated by the user's prose + twins sorted out her tickets as audio layer. NarrationAgent writes the narrator script split into picture-aligned segments. IllustrationAgent generates one illustration per segment. NarratorAgent renders the script as voiceover wav. MusicAgent composes the twins sorted out her tickets for music underlay under the narrator. AudioMixAgent layers the music under the narrator wav into one final mixed wav. CompositorAgent muxes the slideshow video. Reject AmbienceAgent (user asked music, not environmental ambience), Transcription/Translation (no subtitle / multilingual ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow voiceover, not multi-shot film), IntakeImage/BriefEnricher (no image upload)."
        ),
        "intents": [
            "Outline the user's long-form fable into a narrator script tracing Tove's arc — split into illustration-aligned segments with per-segment image_prompt and per-line TTS text.",
            "Plan one illustration per narrator segment in picture-book style, depicting Tove's setting and key moments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level SRT + per-segment timing.',
            'Compose the twins sorted out her tickets the user requested, sized for the narrator-voiceover duration.',
            'Layer the music score under the narrator wav into one final mixed wav.',
            'Composite the final illustrated-audiobook slideshow with mixed audio (narrator + music) and per-segment timing.',
        ],
    },
    {
        "user_goal": "Here's my story I want to process: In a fishing village on a cold northern sea, there lived a blind swordsmith named Iver who had made blades for forty years. His hands knew every grain of every metal he worked. Customers came from across the country. One winter a young woman walked into his workshop and asked him to forge a blade for her that could cut shadows. Iver listened. He said, 'Nobody can cut shadows.' The young woman said, 'I know. But try.' She left him a small bag of gold. Iver worked for three months on a blade he did not understand. On the day she came to collect it, he handed her the sword and said, 'I have done my best. I do not know what I have made.' The young woman unsheathed it once, gently, and a piece of her own shadow fell away and drifted to the floor like a leaf. She closed the sword back into its sheath, thanked Iver, and walked out into the snow. Iver never saw her again. He continued making ordinary blades for the rest of his life, but sometimes, at night, he wondered. — play haunting solo cello softly under the narrator.",
        "rationale": (
            "Long-form illustrated-storytelling brief — Iver's arc as narrated by the user's prose + the user-specified music layer as audio layer. NarrationAgent writes the narrator script split into picture-aligned segments. IllustrationAgent generates one illustration per segment. NarratorAgent renders the script as voiceover wav. MusicAgent composes the the user-specified music layer for music underlay under the narrator. AudioMixAgent layers the music under the narrator wav into one final mixed wav. CompositorAgent muxes the slideshow video. Reject AmbienceAgent (user asked music, not environmental ambience), Transcription/Translation (no subtitle / multilingual ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow voiceover, not multi-shot film), IntakeImage/BriefEnricher (no image upload)."
        ),
        "intents": [
            "Draft the user's long-form fable into a narrator script tracing Iver's arc — split into illustration-aligned segments with per-segment image_prompt and per-line TTS text.",
            "Render one illustration per narrator segment in picture-book style, depicting Iver's setting and key moments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level SRT + per-segment timing.',
            'Compose the the user-specified music layer the user requested, sized for the narrator-voiceover duration.',
            'Layer the music score under the narrator wav into one final mixed wav.',
            'Composite the final illustrated-audiobook slideshow with mixed audio (narrator + music) and per-segment timing.',
        ],
    },
    {
        "user_goal": "Here's my story I want to process: An old carpenter named Otilia and her apprentice Mira ran a small carpentry shop in an alley of an old city. Otilia had been a carpenter for fifty-one years. Mira had been her apprentice for three. They made simple things — chairs, tables, bookshelves, sometimes a wooden toy. One morning Otilia did not come to the shop. Mira walked to Otilia's house and found her in her armchair, not ill but very tired. Otilia smiled. 'Today I think I will not come to the shop. Today I think you should run it.' Mira protested. Otilia shook her head. 'You know how. You have always known how. I have only been watching you remember.' Mira walked back alone. She opened the shop. She served three customers that day. At dusk she went back to Otilia's house, and Otilia was asleep in the armchair with a small wooden bird on her lap she had carved that afternoon, with Mira's name on its underside. — play gentle acoustic guitar softly under the narrator.",
        "rationale": (
            "Long-form illustrated-storytelling brief — Otilia's arc as narrated by the user's prose + Mira's name on its underside as audio layer. NarrationAgent writes the narrator script split into picture-aligned segments. IllustrationAgent generates one illustration per segment. NarratorAgent renders the script as voiceover wav. MusicAgent composes the Mira's name on its underside for music underlay under the narrator. AudioMixAgent layers the music under the narrator wav into one final mixed wav. CompositorAgent muxes the slideshow video. Reject AmbienceAgent (user asked music, not environmental ambience), Transcription/Translation (no subtitle / multilingual ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow voiceover, not multi-shot film), IntakeImage/BriefEnricher (no image upload)."
        ),
        "intents": [
            "Compose the user's long-form fable into a narrator script tracing Otilia's arc — split into illustration-aligned segments with per-segment image_prompt and per-line TTS text.",
            "Design one illustration per narrator segment in picture-book style, depicting Otilia's setting and key moments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level SRT + per-segment timing.',
            "Compose the Mira's name on its underside the user requested, sized for the narrator-voiceover duration.",
            'Layer the music score under the narrator wav into one final mixed wav.',
            'Composite the final illustrated-audiobook slideshow with mixed audio (narrator + music) and per-segment timing.',
        ],
    },
    {
        "user_goal": "Here's my story I want to process: A very old oak tree named Ember had stood at the corner of a schoolyard for two hundred and thirty years. She had watched generations of children climb her branches, eat lunches in her shade, carve their initials into her bark. She could feel her roots loosening and her heartwood thinning, and she was not afraid. But she worried about the swing on her lowest branch — a small girl named Imogen came every day. Ember concentrated all her last strength into growing one particular acorn. In autumn it rolled to Imogen's feet. Imogen planted it. Ember fell that winter in a great wind. In spring a small new oak began to grow in the same schoolyard. Ember had passed on the swing, and the shade, and the long slow patience of old trees. — play soft chamber-strings softly under the narrator.",
        "rationale": (
            "Long-form illustrated-storytelling brief — Ember's arc as narrated by the user's prose + the user-specified music layer as audio layer. NarrationAgent writes the narrator script split into picture-aligned segments. IllustrationAgent generates one illustration per segment. NarratorAgent renders the script as voiceover wav. MusicAgent composes the the user-specified music layer for music underlay under the narrator. AudioMixAgent layers the music under the narrator wav into one final mixed wav. CompositorAgent muxes the slideshow video. Reject AmbienceAgent (user asked music, not environmental ambience), Transcription/Translation (no subtitle / multilingual ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow voiceover, not multi-shot film), IntakeImage/BriefEnricher (no image upload)."
        ),
        "intents": [
            "Polish the user's long-form fable into a narrator script tracing Ember's arc — split into illustration-aligned segments with per-segment image_prompt and per-line TTS text.",
            "Generate one illustration per narrator segment in picture-book style, depicting Ember's setting and key moments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level SRT + per-segment timing.',
            'Compose the the user-specified music layer the user requested, sized for the narrator-voiceover duration.',
            'Layer the music score under the narrator wav into one final mixed wav.',
            'Composite the final illustrated-audiobook slideshow with mixed audio (narrator + music) and per-segment timing.',
        ],
    },
    {
        "user_goal": "Here's my story I want to process: In a little house at the edge of a great field of lavender lived an old beekeeper named Ines. Ines had kept bees for fifty-three years, and her bees knew her by smell and by the particular way she hummed while she worked. She was very gentle with them. She never smoked them too heavily. She always thanked them when she took their honey, and always left them enough. One summer a great drought came to the valley. The lavender withered. The wildflowers shriveled. The bees grew hungry and began to starve. Ines, heartsick, mixed honey and water in shallow dishes and set them near the hives. Every morning at dawn she carried the dishes out, and every evening at dusk she carried empty ones back. She did this for forty-one days. When the drought finally ended and the meadow bloomed again, Ines walked out to the hives, and the bees rose up in a slow swirling cloud and circled her once, twice, three times before returning to their work. — play tender string-quartet softly under the narrator.",
        "rationale": (
            "Long-form illustrated-storytelling brief — Ines's arc as narrated by the user's prose + them as audio layer. NarrationAgent writes the narrator script split into picture-aligned segments. IllustrationAgent generates one illustration per segment. NarratorAgent renders the script as voiceover wav. MusicAgent composes the them for music underlay under the narrator. AudioMixAgent layers the music under the narrator wav into one final mixed wav. CompositorAgent muxes the slideshow video. Reject AmbienceAgent (user asked music, not environmental ambience), Transcription/Translation (no subtitle / multilingual ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow voiceover, not multi-shot film), IntakeImage/BriefEnricher (no image upload)."
        ),
        "intents": [
            "Outline the user's long-form fable into a narrator script tracing Ines's arc — split into illustration-aligned segments with per-segment image_prompt and per-line TTS text.",
            "Plan one illustration per narrator segment in picture-book style, depicting Ines's setting and key moments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level SRT + per-segment timing.',
            'Compose the them the user requested, sized for the narrator-voiceover duration.',
            'Layer the music score under the narrator wav into one final mixed wav.',
            'Composite the final illustrated-audiobook slideshow with mixed audio (narrator + music) and per-segment timing.',
        ],
    },
]
