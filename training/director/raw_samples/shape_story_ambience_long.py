"""Long-story variant of story_ambience — Narration → Illustration → Narrator → Ambience → AudioMix → Compositor.

Illustrated storytelling WITH ambient sound, NO music, NO subtitle, NO image upload.
Per-sample tailored: each rationale and each intent references the user_goal's protagonist + ambience ask."""
from __future__ import annotations


SAMPLES: list[dict] = [
    {
        "user_goal": "Here's my story I want to process: In a forest older than any map, there ran a small clear river called Ibi. The old women of the nearest village said, and had said for generations, that Ibi listened — if you whispered a wish over its moving water and your wish was honest, Ibi would sometimes grant it. One summer, a boy named Nico came to Ibi. His mother was very sick. He knelt at the bank and whispered, 'Please let her get better.' Ibi did not answer. Nico came back every day. On the seventh day his mother slept through the night without pain. By autumn she was teaching him to plant tomatoes again. Nico never told anyone about the river. But every spring of his life, when the ice thawed, he went back to Ibi and sat by its bank for a whole afternoon, quietly, saying thank you. — add forest-stream ambient (running water, distant birds, wind through leaves) under the narrator.",
        "rationale": (
            "Long-form illustrated-storytelling brief — Nico's arc as narrated by the user's prose + forest-stream ambient (running water, distant birds, wind through leaves) under the narrator as audio layer. NarrationAgent writes the narrator script split into picture-aligned segments. IllustrationAgent generates one illustration per segment. NarratorAgent renders the script as voiceover wav. AmbienceAgent generates the forest-stream ambient (running water, distant birds, wind through leaves) under the narrator bed for environmental texture under the narrator. AudioMixAgent layers the ambience bed under the narrator wav into one final mixed wav. CompositorAgent muxes the slideshow video. Reject MusicAgent (user asked atmospheric / environmental sound, not a music score), Transcription/Translation (no subtitle / multilingual ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow voiceover, not multi-shot film), IntakeImage/BriefEnricher (no image upload)."
        ),
        "intents": [
            "Polish the user's long-form fable into a narrator script tracing Nico's arc — split into illustration-aligned segments with per-segment image_prompt and per-line TTS text.",
            "Generate one illustration per narrator segment in picture-book style, depicting Nico's setting and key moments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level SRT + per-segment timing.',
            "Generate the forest-stream ambient (running water, distant birds, wind through leaves) under the narrator bed the user requested, matching the story's environmental setting.",
            'Layer the ambience bed under the narrator wav into one final mixed wav.',
            'Composite the final illustrated-audiobook slideshow with mixed audio (narrator + ambience) and per-segment timing.',
        ],
    },
    {
        "user_goal": "Here's my story I want to process: Once there was a little star named Tess who had fallen out of the sky. An old badger found her on the path and carried her home. In his burrow, by the warm stove, he wrapped her in a handkerchief and gave her a saucer of cream. Tess slept for three days. When she woke she missed the sky. The badger climbed the tallest mountain in the valley with Tess in his pocket, and under a brilliant night sky he lifted her out and held her up to the stars. Tess drifted upward gently, like a dandelion puff, and found her old place among the constellations. Every winter after that, when the old badger climbed out of his burrow and looked up, he could see her shining, a little brighter than the rest, just to say hello. — add mountain-peak winter ambient (soft wind, distant owl, snow crunch) under the narrator.",
        "rationale": (
            "Long-form illustrated-storytelling brief — Tess's arc as narrated by the user's prose + mountain-peak winter ambient (soft wind, distant owl, snow crunch) under the narrator as audio layer. NarrationAgent writes the narrator script split into picture-aligned segments. IllustrationAgent generates one illustration per segment. NarratorAgent renders the script as voiceover wav. AmbienceAgent generates the mountain-peak winter ambient (soft wind, distant owl, snow crunch) under the narrator bed for environmental texture under the narrator. AudioMixAgent layers the ambience bed under the narrator wav into one final mixed wav. CompositorAgent muxes the slideshow video. Reject MusicAgent (user asked atmospheric / environmental sound, not a music score), Transcription/Translation (no subtitle / multilingual ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow voiceover, not multi-shot film), IntakeImage/BriefEnricher (no image upload)."
        ),
        "intents": [
            "Outline the user's long-form fable into a narrator script tracing Tess's arc — split into illustration-aligned segments with per-segment image_prompt and per-line TTS text.",
            "Plan one illustration per narrator segment in picture-book style, depicting Tess's setting and key moments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level SRT + per-segment timing.',
            "Generate the mountain-peak winter ambient (soft wind, distant owl, snow crunch) under the narrator bed the user requested, matching the story's environmental setting.",
            'Layer the ambience bed under the narrator wav into one final mixed wav.',
            'Composite the final illustrated-audiobook slideshow with mixed audio (narrator + ambience) and per-segment timing.',
        ],
    },
    {
        "user_goal": "Here's my story I want to process: A very old oak tree named Ember had stood at the corner of a schoolyard for two hundred and thirty years. She had watched generations of children climb her branches, eat their lunches in her shade, carve their initials into her bark. Ember could feel her roots loosening, and she knew her time was coming. She was not sad. But she was worried about the swing that hung from her lowest branch — a small girl named Imogen came to use it every day. So Ember concentrated all her last strength into growing one particular acorn. In autumn it rolled to Imogen's feet. Imogen planted it. That winter Ember fell in a great wind. In spring a new oak began to grow in the schoolyard, and Ember's swing lived on in the small green twig. — add schoolyard-autumn ambient (distant children's laughter at recess, wind through branches, rustling leaves) under the narrator.",
        "rationale": (
            "Long-form illustrated-storytelling brief — Ember's arc as narrated by the user's prose + schoolyard-autumn ambient (distant children's laughter at recess, wind through branches, rustling leaves) under the narrator as audio layer. NarrationAgent writes the narrator script split into picture-aligned segments. IllustrationAgent generates one illustration per segment. NarratorAgent renders the script as voiceover wav. AmbienceAgent generates the schoolyard-autumn ambient (distant children's laughter at recess, wind through branches, rustling leaves) under the narrator bed for environmental texture under the narrator. AudioMixAgent layers the ambience bed under the narrator wav into one final mixed wav. CompositorAgent muxes the slideshow video. Reject MusicAgent (user asked atmospheric / environmental sound, not a music score), Transcription/Translation (no subtitle / multilingual ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow voiceover, not multi-shot film), IntakeImage/BriefEnricher (no image upload)."
        ),
        "intents": [
            "Draft the user's long-form fable into a narrator script tracing Ember's arc — split into illustration-aligned segments with per-segment image_prompt and per-line TTS text.",
            "Render one illustration per narrator segment in picture-book style, depicting Ember's setting and key moments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level SRT + per-segment timing.',
            "Generate the schoolyard-autumn ambient (distant children's laughter at recess, wind through branches, rustling leaves) under the narrator bed the user requested, matching the story's environmental setting.",
            'Layer the ambience bed under the narrator wav into one final mixed wav.',
            'Composite the final illustrated-audiobook slideshow with mixed audio (narrator + ambience) and per-segment timing.',
        ],
    },
    {
        "user_goal": "Here's my story I want to process: Beneath the crooked stone arch of an old city alleyway, a young violinist named Jude played every afternoon for whatever coins passersby would drop. He played with the seriousness of someone who believed music could make the city a better place. Most days, almost no one stopped. One cold Thursday afternoon a small old woman stopped at the arch and listened. 'My husband used to play that on his violin,' she said. 'He passed in April.' The next day she came back with a stool. The day after that, she brought a friend. Within a month, Jude had a small, quiet audience of old people who came every afternoon to listen to him play under the arch, each of them carrying their own memory of music. — add rainy-alleyway ambient (distant traffic, rain on cobblestones, muffled footsteps) under the narrator.",
        "rationale": (
            "Long-form illustrated-storytelling brief — Jude's arc as narrated by the user's prose + rainy-alleyway ambient (distant traffic, rain on cobblestones, muffled footsteps) under the narrator as audio layer. NarrationAgent writes the narrator script split into picture-aligned segments. IllustrationAgent generates one illustration per segment. NarratorAgent renders the script as voiceover wav. AmbienceAgent generates the rainy-alleyway ambient (distant traffic, rain on cobblestones, muffled footsteps) under the narrator bed for environmental texture under the narrator. AudioMixAgent layers the ambience bed under the narrator wav into one final mixed wav. CompositorAgent muxes the slideshow video. Reject MusicAgent (user asked atmospheric / environmental sound, not a music score), Transcription/Translation (no subtitle / multilingual ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow voiceover, not multi-shot film), IntakeImage/BriefEnricher (no image upload)."
        ),
        "intents": [
            "Compose the user's long-form fable into a narrator script tracing Jude's arc — split into illustration-aligned segments with per-segment image_prompt and per-line TTS text.",
            "Design one illustration per narrator segment in picture-book style, depicting Jude's setting and key moments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level SRT + per-segment timing.',
            "Generate the rainy-alleyway ambient (distant traffic, rain on cobblestones, muffled footsteps) under the narrator bed the user requested, matching the story's environmental setting.",
            'Layer the ambience bed under the narrator wav into one final mixed wav.',
            'Composite the final illustrated-audiobook slideshow with mixed audio (narrator + ambience) and per-segment timing.',
        ],
    },
    {
        "user_goal": "Here's my story I want to process: Deep in the midnight ocean lived a small moon-jellyfish named Lumi who could not glow. Her brothers and sisters glowed with soft pearly light and drifted past in shimmering parades, while Lumi tucked herself behind kelp and waited for them to pass. One night a little lantern-fish named Pim got lost in the cold currents. Lumi — who knew the kelp forest better than any of her siblings — offered to guide him home. Through tangled weeds and past sleeping crabs, Lumi led the way by memory alone. When they arrived at Pim's family, his little sisters cheered. Pim whispered, 'You don't need to glow, Lumi. You already shine.' That night, for the first time, a soft pearly light bloomed inside Lumi's bell. — add deep-ocean ambient (muffled bubbles, distant whale-song, slow water) under the narrator.",
        "rationale": (
            "Long-form illustrated-storytelling brief — Lumi's arc as narrated by the user's prose + deep-ocean ambient (muffled bubbles, distant whale-song, slow water) under the narrator as audio layer. NarrationAgent writes the narrator script split into picture-aligned segments. IllustrationAgent generates one illustration per segment. NarratorAgent renders the script as voiceover wav. AmbienceAgent generates the deep-ocean ambient (muffled bubbles, distant whale-song, slow water) under the narrator bed for environmental texture under the narrator. AudioMixAgent layers the ambience bed under the narrator wav into one final mixed wav. CompositorAgent muxes the slideshow video. Reject MusicAgent (user asked atmospheric / environmental sound, not a music score), Transcription/Translation (no subtitle / multilingual ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow voiceover, not multi-shot film), IntakeImage/BriefEnricher (no image upload)."
        ),
        "intents": [
            "Polish the user's long-form fable into a narrator script tracing Lumi's arc — split into illustration-aligned segments with per-segment image_prompt and per-line TTS text.",
            "Generate one illustration per narrator segment in picture-book style, depicting Lumi's setting and key moments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level SRT + per-segment timing.',
            "Generate the deep-ocean ambient (muffled bubbles, distant whale-song, slow water) under the narrator bed the user requested, matching the story's environmental setting.",
            'Layer the ambience bed under the narrator wav into one final mixed wav.',
            'Composite the final illustrated-audiobook slideshow with mixed audio (narrator + ambience) and per-segment timing.',
        ],
    },
    {
        "user_goal": "Here's my story I want to process: High in a lighthouse on a storm-battered coast lived a keeper named Magnus. Magnus had been at the lighthouse for forty-seven years. He had never married. He had one chair, one teapot, and one very fat cat named Admiral, who had been with him for nineteen of those years. When Magnus was seventy-three his eyes began to fail, and the lighthouse board would soon retire him. Magnus did not want to leave. One winter evening, Admiral climbed up onto the lamp platform and sat very still, as if listening. The next night he did it again. By the third night, Magnus understood — the cat could see the horizon better than he could now. So Magnus began to climb the platform with Admiral on his shoulder every dusk. Together they kept the light. They kept it for three more years, and no ship wrecked on the coast. — add stormy-coast lighthouse ambient (distant waves, howling wind, foghorn) under the narrator.",
        "rationale": (
            "Long-form illustrated-storytelling brief — Magnus's arc as narrated by the user's prose + stormy-coast lighthouse ambient (distant waves, howling wind, foghorn) under the narrator as audio layer. NarrationAgent writes the narrator script split into picture-aligned segments. IllustrationAgent generates one illustration per segment. NarratorAgent renders the script as voiceover wav. AmbienceAgent generates the stormy-coast lighthouse ambient (distant waves, howling wind, foghorn) under the narrator bed for environmental texture under the narrator. AudioMixAgent layers the ambience bed under the narrator wav into one final mixed wav. CompositorAgent muxes the slideshow video. Reject MusicAgent (user asked atmospheric / environmental sound, not a music score), Transcription/Translation (no subtitle / multilingual ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow voiceover, not multi-shot film), IntakeImage/BriefEnricher (no image upload)."
        ),
        "intents": [
            "Outline the user's long-form fable into a narrator script tracing Magnus's arc — split into illustration-aligned segments with per-segment image_prompt and per-line TTS text.",
            "Plan one illustration per narrator segment in picture-book style, depicting Magnus's setting and key moments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level SRT + per-segment timing.',
            "Generate the stormy-coast lighthouse ambient (distant waves, howling wind, foghorn) under the narrator bed the user requested, matching the story's environmental setting.",
            'Layer the ambience bed under the narrator wav into one final mixed wav.',
            'Composite the final illustrated-audiobook slideshow with mixed audio (narrator + ambience) and per-segment timing.',
        ],
    },
    {
        "user_goal": "Here's my story I want to process: A little girl named Amaya sat at her desk by the window and folded a paper bird with great care. When she was done, the bird sat in her palm — small, cream-colored, with two crisp wings. Amaya named her Momo and set Momo on the windowsill. That night, under a thin moon, Momo discovered she could fly. Every night Momo explored a little more of the town. She learned where the owl lived, where the stray cats gathered at midnight, where the old baker started his oven before dawn. Every morning before Amaya woke, Momo landed back on the windowsill and folded her paper wings neatly against her body, as if she had never moved. Amaya never suspected a thing. Momo kept her secret, and she was happy. — add sleeping-town nighttime ambient (distant owl, wind in chimneys, soft cat footsteps) under the narrator.",
        "rationale": (
            "Long-form illustrated-storytelling brief — Amaya's arc as narrated by the user's prose + sleeping-town nighttime ambient (distant owl, wind in chimneys, soft cat footsteps) under the narrator as audio layer. NarrationAgent writes the narrator script split into picture-aligned segments. IllustrationAgent generates one illustration per segment. NarratorAgent renders the script as voiceover wav. AmbienceAgent generates the sleeping-town nighttime ambient (distant owl, wind in chimneys, soft cat footsteps) under the narrator bed for environmental texture under the narrator. AudioMixAgent layers the ambience bed under the narrator wav into one final mixed wav. CompositorAgent muxes the slideshow video. Reject MusicAgent (user asked atmospheric / environmental sound, not a music score), Transcription/Translation (no subtitle / multilingual ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow voiceover, not multi-shot film), IntakeImage/BriefEnricher (no image upload)."
        ),
        "intents": [
            "Draft the user's long-form fable into a narrator script tracing Amaya's arc — split into illustration-aligned segments with per-segment image_prompt and per-line TTS text.",
            "Render one illustration per narrator segment in picture-book style, depicting Amaya's setting and key moments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level SRT + per-segment timing.',
            "Generate the sleeping-town nighttime ambient (distant owl, wind in chimneys, soft cat footsteps) under the narrator bed the user requested, matching the story's environmental setting.",
            'Layer the ambience bed under the narrator wav into one final mixed wav.',
            'Composite the final illustrated-audiobook slideshow with mixed audio (narrator + ambience) and per-segment timing.',
        ],
    },
    {
        "user_goal": "Here's my story I want to process: In the attic of a seaside house lived a very old clockmaker named Vesper. For forty years he had built clocks for the village — grandfather clocks, mantel clocks, pocket watches that ticked so quietly you had to hold them to your ear. One evening a small boy named Nils arrived at the attic carrying the pieces of his grandfather's broken pocket watch. His grandfather had died the week before. Vesper took the pieces in his palm and said, 'Come back in seven days.' When Nils returned, the watch ticked again. Nils asked what it had cost to fix, and Vesper said, 'Come sit with me once a week and tell me a story about your grandfather. That is the cost.' For the rest of Vesper's life, Nils came to the attic every Wednesday evening and told stories, and Vesper listened, and the watch kept ticking. — add seaside-attic ambient (distant waves, ticking clocks in ensemble, wind through eaves) under the narrator.",
        "rationale": (
            "Long-form illustrated-storytelling brief — Vesper's arc as narrated by the user's prose + seaside-attic ambient (distant waves, ticking clocks in ensemble, wind through eaves) under the narrator as audio layer. NarrationAgent writes the narrator script split into picture-aligned segments. IllustrationAgent generates one illustration per segment. NarratorAgent renders the script as voiceover wav. AmbienceAgent generates the seaside-attic ambient (distant waves, ticking clocks in ensemble, wind through eaves) under the narrator bed for environmental texture under the narrator. AudioMixAgent layers the ambience bed under the narrator wav into one final mixed wav. CompositorAgent muxes the slideshow video. Reject MusicAgent (user asked atmospheric / environmental sound, not a music score), Transcription/Translation (no subtitle / multilingual ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow voiceover, not multi-shot film), IntakeImage/BriefEnricher (no image upload)."
        ),
        "intents": [
            "Compose the user's long-form fable into a narrator script tracing Vesper's arc — split into illustration-aligned segments with per-segment image_prompt and per-line TTS text.",
            "Design one illustration per narrator segment in picture-book style, depicting Vesper's setting and key moments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level SRT + per-segment timing.',
            "Generate the seaside-attic ambient (distant waves, ticking clocks in ensemble, wind through eaves) under the narrator bed the user requested, matching the story's environmental setting.",
            'Layer the ambience bed under the narrator wav into one final mixed wav.',
            'Composite the final illustrated-audiobook slideshow with mixed audio (narrator + ambience) and per-segment timing.',
        ],
    },
    {
        "user_goal": "Here's my story I want to process: In a village at the edge of a great misty forest, there lived a girl named Luna who was afraid of the dark. Her grandmother said, 'The dark is only a room you have not yet learned the shape of. Come with me, child. We will learn it together.' Luna took her grandmother's hand. They stepped outside into the cold dark, grandmother's cane tapping the path, Luna's heart pounding. They walked slowly, listening. Luna learned how the forest sounded: owls, wind, the creak of branches. After a long while she heard something else — a small frightened sobbing — and she followed it to the base of a great oak, where her little brother was curled, lost. Carrying her brother home, Luna understood that the dark had been a shape all along; she had just needed to walk through it. — add misty-forest night ambient (distant owl, creaking branches, soft wind through pines) under the narrator.",
        "rationale": (
            "Long-form illustrated-storytelling brief — Luna's arc as narrated by the user's prose + misty-forest night ambient (distant owl, creaking branches, soft wind through pines) under the narrator as audio layer. NarrationAgent writes the narrator script split into picture-aligned segments. IllustrationAgent generates one illustration per segment. NarratorAgent renders the script as voiceover wav. AmbienceAgent generates the misty-forest night ambient (distant owl, creaking branches, soft wind through pines) under the narrator bed for environmental texture under the narrator. AudioMixAgent layers the ambience bed under the narrator wav into one final mixed wav. CompositorAgent muxes the slideshow video. Reject MusicAgent (user asked atmospheric / environmental sound, not a music score), Transcription/Translation (no subtitle / multilingual ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow voiceover, not multi-shot film), IntakeImage/BriefEnricher (no image upload)."
        ),
        "intents": [
            "Polish the user's long-form fable into a narrator script tracing Luna's arc — split into illustration-aligned segments with per-segment image_prompt and per-line TTS text.",
            "Generate one illustration per narrator segment in picture-book style, depicting Luna's setting and key moments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level SRT + per-segment timing.',
            "Generate the misty-forest night ambient (distant owl, creaking branches, soft wind through pines) under the narrator bed the user requested, matching the story's environmental setting.",
            'Layer the ambience bed under the narrator wav into one final mixed wav.',
            'Composite the final illustrated-audiobook slideshow with mixed audio (narrator + ambience) and per-segment timing.',
        ],
    },
    {
        "user_goal": "Here's my story I want to process: An old woman named Hildi had spent her whole life mending nets. Every morning she walked down to the harbor with her basket of needles and twine and sat on the seawall while the fishing boats came home. Hildi was very good at her work — she could mend a net so cleanly the fish never noticed a seam. But what the sailors liked best was that Hildi was a good listener. She heard every story — the storms they had survived, the strange lights they had seen, the songs from deep below the waves — and she remembered every word. When Hildi was very old and could no longer mend, the sailors built her a bench right at the end of the dock. When Hildi passed, the village put a new net in the harbor, and every fisherman tied a small knot in it — one knot for each story Hildi had ever heard. — add harbor ambient (lapping waves against boats, distant gulls, soft rigging clinks) under the narrator.",
        "rationale": (
            "Long-form illustrated-storytelling brief — Hildi's arc as narrated by the user's prose + harbor ambient (lapping waves against boats, distant gulls, soft rigging clinks) under the narrator as audio layer. NarrationAgent writes the narrator script split into picture-aligned segments. IllustrationAgent generates one illustration per segment. NarratorAgent renders the script as voiceover wav. AmbienceAgent generates the harbor ambient (lapping waves against boats, distant gulls, soft rigging clinks) under the narrator bed for environmental texture under the narrator. AudioMixAgent layers the ambience bed under the narrator wav into one final mixed wav. CompositorAgent muxes the slideshow video. Reject MusicAgent (user asked atmospheric / environmental sound, not a music score), Transcription/Translation (no subtitle / multilingual ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow voiceover, not multi-shot film), IntakeImage/BriefEnricher (no image upload)."
        ),
        "intents": [
            "Outline the user's long-form fable into a narrator script tracing Hildi's arc — split into illustration-aligned segments with per-segment image_prompt and per-line TTS text.",
            "Plan one illustration per narrator segment in picture-book style, depicting Hildi's setting and key moments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level SRT + per-segment timing.',
            "Generate the harbor ambient (lapping waves against boats, distant gulls, soft rigging clinks) under the narrator bed the user requested, matching the story's environmental setting.",
            'Layer the ambience bed under the narrator wav into one final mixed wav.',
            'Composite the final illustrated-audiobook slideshow with mixed audio (narrator + ambience) and per-segment timing.',
        ],
    },
]
