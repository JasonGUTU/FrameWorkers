"""Shape: story_imgref_bilingual —
    IntakeImage → BriefEnricher → Narration → Illustration → Narrator → Translation → Compositor.

Storytelling with reference image + bilingual subtitles (no music, no ambient).
"""
from __future__ import annotations

SAMPLES: list[dict] = [
    {
        "user_goal": "Using this uploaded portrait of a storyteller grandmother, produce an English-Spanish bilingual illustrated audiobook of a folk tale where she teaches her grandchildren the old tales.",
        "rationale": (
            "User uploaded a grandmother portrait + asks for illustrated audiobook with "
            "English-Spanish bilingual subtitles. IntakeImageAgent ingests the portrait. "
            "BriefEnricherAgent synthesizes a consistent-character brief so illustrations keep "
            "the grandmother's appearance steady. NarrationAgent writes the narration script. "
            "IllustrationAgent generates one image per scene following the reference. "
            "NarratorAgent produces the English TTS track. TranslationAgent translates the "
            "narration script to Spanish. CompositorAgent assembles the slideshow with bilingual "
            "subtitle burn-in. Reject Music / Ambience (neither requested), Story/Screenplay/"
            "KeyFrame/Video (those are for live-action mini-drama, not illustrated-audiobook "
            "slideshow)."
        ),
        "intents": [
            "Ingest the uploaded grandmother portrait as the visual reference.",
            "Enrich the character brief so illustrations keep the grandmother's appearance consistent.",
            "Write the narration script from the folk tale where the grandmother teaches her grandchildren.",
            "Generate one illustration per scene preserving the grandmother's reference likeness.",
            "Produce an English TTS narrator track for the folk tale.",
            "Translate the narration script into Spanish subtitle segments.",
            "Compose the final slideshow pairing illustrations with English narrator and bilingual English+Spanish captions.",
        ],
    },
    {
        "user_goal": "Using this uploaded river-otter portrait, produce an English-French bilingual illustrated audiobook of a fable where the otter mediates peace between the fish tribes.",
        "rationale": (
            "Otter portrait + English-French bilingual illustrated audiobook. IntakeImageAgent "
            "→ BriefEnricherAgent (consistent-otter brief) → NarrationAgent → IllustrationAgent "
            "(otter preserved per scene) → NarratorAgent (English TTS) → TranslationAgent "
            "(French) → CompositorAgent (bilingual burn-in). Reject Music / Ambience (neither "
            "requested), Story/Screenplay/KeyFrame/Video (live-action only)."
        ),
        "intents": [
            "Ingest the uploaded river-otter portrait as the visual reference.",
            "Enrich the otter brief so every illustration keeps its appearance consistent.",
            "Write the narration script about the otter mediating peace between the fish tribes.",
            "Generate one illustration per scene preserving the otter's reference likeness.",
            "Produce an English TTS narrator track for the fable.",
            "Translate the narration script into French subtitle segments.",
            "Compose the slideshow with English narrator audio and bilingual English+French captions.",
        ],
    },
    {
        "user_goal": "Using this uploaded portrait of a little girl, produce an English-Japanese bilingual illustrated audiobook of a tale where the girl discovers a portal in her grandmother's attic.",
        "rationale": (
            "Little-girl portrait + English-Japanese bilingual storytelling. "
            "IntakeImageAgent → BriefEnricherAgent → NarrationAgent → IllustrationAgent → "
            "NarratorAgent (English) → TranslationAgent (Japanese) → CompositorAgent. No "
            "Music / Ambience / live-action agents requested."
        ),
        "intents": [
            "Ingest the uploaded little-girl portrait as the visual reference.",
            "Enrich the little-girl brief for consistent illustration across scenes.",
            "Write the narration script about the girl discovering the attic portal.",
            "Generate one illustration per scene preserving the girl's reference likeness.",
            "Produce an English TTS narrator track for the attic-portal tale.",
            "Translate the narration script into Japanese subtitle segments.",
            "Compose the slideshow with English narrator audio and bilingual English+Japanese captions.",
        ],
    },
    {
        "user_goal": "Using this uploaded portrait of a wise tortoise, produce an English-Mandarin bilingual illustrated audiobook of a tale where the tortoise crosses seven kingdoms to find the garden of patience.",
        "rationale": (
            "Wise tortoise portrait + English-Mandarin bilingual. IntakeImageAgent → "
            "BriefEnricherAgent (tortoise consistency) → NarrationAgent → IllustrationAgent → "
            "NarratorAgent (English) → TranslationAgent (Mandarin) → CompositorAgent."
        ),
        "intents": [
            "Ingest the uploaded wise-tortoise portrait as the visual reference.",
            "Enrich the tortoise brief so every scene keeps its shell pattern consistent.",
            "Write the narration script about the tortoise crossing seven kingdoms to find the garden of patience.",
            "Generate one illustration per scene preserving the tortoise's reference likeness.",
            "Produce an English TTS narrator track for the tortoise quest.",
            "Translate the narration script into Mandarin subtitle segments.",
            "Compose the slideshow with English narrator audio and bilingual English+Mandarin captions.",
        ],
    },
    {
        "user_goal": "Using this uploaded snow-leopard portrait, produce an English-Russian bilingual illustrated audiobook of a tale where the leopard learns the mountain's oldest song.",
        "rationale": (
            "Snow leopard + English-Russian bilingual storytelling, no audio overlay."
        ),
        "intents": [
            "Ingest the uploaded snow-leopard portrait as the visual reference.",
            "Enrich the snow-leopard brief for consistent illustration.",
            "Write the narration script about the snow-leopard learning the mountain's oldest song.",
            "Generate one illustration per scene preserving the leopard's reference likeness.",
            "Produce an English TTS narrator track for the snow-leopard tale.",
            "Translate the narration script into Russian subtitle segments.",
            "Compose the slideshow with English narrator audio and bilingual English+Russian captions.",
        ],
    },
    {
        "user_goal": "Using this uploaded portrait of a humble tailor, produce an English-German bilingual illustrated audiobook of a tale where the tailor sews a coat of courage for a frightened prince.",
        "rationale": (
            "Humble tailor + English-German bilingual. IntakeImageAgent → BriefEnricherAgent → "
            "Narration → Illustration → Narrator (English) → Translation (German) → Compositor."
        ),
        "intents": [
            "Ingest the uploaded humble-tailor portrait as the visual reference.",
            "Enrich the tailor brief for consistent illustration across scenes.",
            "Write the narration script about the tailor sewing a coat of courage for the frightened prince.",
            "Generate one illustration per scene preserving the tailor's reference likeness.",
            "Produce an English TTS narrator track for the tailor tale.",
            "Translate the narration script into German subtitle segments.",
            "Compose the slideshow with English narrator audio and bilingual English+German captions.",
        ],
    },
    {
        "user_goal": "Using this uploaded rabbit portrait, produce an English-Korean bilingual illustrated audiobook of a tale where the rabbit finds the moon's lost keys.",
        "rationale": (
            "Curious rabbit + English-Korean bilingual storytelling, no audio overlay."
        ),
        "intents": [
            "Ingest the uploaded rabbit portrait as the visual reference.",
            "Enrich the rabbit brief for consistent illustration.",
            "Write the narration script about the rabbit finding the moon's lost keys.",
            "Generate one illustration per scene preserving the rabbit's reference likeness.",
            "Produce an English TTS narrator track for the rabbit tale.",
            "Translate the narration script into Korean subtitle segments.",
            "Compose the slideshow with English narrator audio and bilingual English+Korean captions.",
        ],
    },
    {
        "user_goal": "Using this uploaded beekeeper portrait, produce an English-Italian bilingual illustrated audiobook of a tale where the beekeeper's hive grants three honey-wishes.",
        "rationale": (
            "Cheerful beekeeper + English-Italian bilingual. No music/ambient asked."
        ),
        "intents": [
            "Ingest the uploaded beekeeper portrait as the visual reference.",
            "Enrich the beekeeper brief for consistent illustration.",
            "Write the narration script about the beekeeper's three honey-wishes.",
            "Generate one illustration per scene preserving the beekeeper's reference likeness.",
            "Produce an English TTS narrator track for the beekeeper tale.",
            "Translate the narration script into Italian subtitle segments.",
            "Compose the slideshow with English narrator audio and bilingual English+Italian captions.",
        ],
    },
    {
        "user_goal": "Using this uploaded portrait of a singing whale, produce an English-Portuguese bilingual illustrated audiobook of a tale where the whale sings a lullaby that calms every sea-storm.",
        "rationale": (
            "Singing whale + English-Portuguese bilingual storytelling, no Music layer "
            "(the lullaby is described inside the narration, not added as a BGM track)."
        ),
        "intents": [
            "Ingest the uploaded singing-whale portrait as the visual reference.",
            "Enrich the whale brief for consistent illustration across scenes.",
            "Write the narration script about the whale's storm-calming lullaby.",
            "Generate one illustration per scene preserving the whale's reference likeness.",
            "Produce an English TTS narrator track for the whale tale.",
            "Translate the narration script into Portuguese subtitle segments.",
            "Compose the slideshow with English narrator audio and bilingual English+Portuguese captions.",
        ],
    },
    {
        "user_goal": "Using this uploaded night-owl portrait, produce an English-Arabic bilingual illustrated audiobook of a tale where the owl delivers letters between the dreaming and waking worlds.",
        "rationale": (
            "Night owl + English-Arabic bilingual. No audio overlay requested."
        ),
        "intents": [
            "Ingest the uploaded night-owl portrait as the visual reference.",
            "Enrich the owl brief for consistent illustration.",
            "Write the narration script about the owl's letter-delivery between worlds.",
            "Generate one illustration per scene preserving the owl's reference likeness.",
            "Produce an English TTS narrator track for the owl tale.",
            "Translate the narration script into Arabic subtitle segments.",
            "Compose the slideshow with English narrator audio and bilingual English+Arabic captions.",
        ],
    },
    {
        "user_goal": "Using this uploaded shepherdess portrait, produce an English-Hindi bilingual illustrated audiobook of a tale where the shepherdess befriends a cloud who teaches her to rain.",
        "rationale": (
            "Young shepherdess + cloud-friend + English-Hindi bilingual, no audio overlay."
        ),
        "intents": [
            "Ingest the uploaded shepherdess portrait as the visual reference.",
            "Enrich the shepherdess brief for consistent illustration.",
            "Write the narration script about the shepherdess and the cloud-friend.",
            "Generate one illustration per scene preserving the shepherdess's reference likeness.",
            "Produce an English TTS narrator track for the shepherdess tale.",
            "Translate the narration script into Hindi subtitle segments.",
            "Compose the slideshow with English narrator audio and bilingual English+Hindi captions.",
        ],
    },
    {
        "user_goal": "Using this uploaded gentle-bear portrait, produce an English-Thai bilingual illustrated audiobook of a tale where the bear shares his honey with every hungry creature of the forest.",
        "rationale": (
            "Gentle bear + English-Thai bilingual, no music/ambient/live-action agents needed."
        ),
        "intents": [
            "Ingest the uploaded gentle-bear portrait as the visual reference.",
            "Enrich the bear brief for consistent illustration across scenes.",
            "Write the narration script about the bear sharing honey with the forest creatures.",
            "Generate one illustration per scene preserving the bear's reference likeness.",
            "Produce an English TTS narrator track for the bear tale.",
            "Translate the narration script into Thai subtitle segments.",
            "Compose the slideshow with English narrator audio and bilingual English+Thai captions.",
        ],
    },
    {
        "user_goal": "Using this uploaded old-lighthouse-keeper portrait, produce an English-Vietnamese bilingual illustrated audiobook of a tale where the keeper guides ghost ships to their final resting place.",
        "rationale": (
            "Old lighthouse keeper + English-Vietnamese bilingual, no audio overlay asked."
        ),
        "intents": [
            "Ingest the uploaded lighthouse-keeper portrait as the visual reference.",
            "Enrich the keeper brief for consistent illustration.",
            "Write the narration script about the keeper guiding ghost ships home.",
            "Generate one illustration per scene preserving the keeper's reference likeness.",
            "Produce an English TTS narrator track for the keeper tale.",
            "Translate the narration script into Vietnamese subtitle segments.",
            "Compose the slideshow with English narrator audio and bilingual English+Vietnamese captions.",
        ],
    },
    {
        "user_goal": "Using this uploaded merry-fox portrait, produce an English-Dutch bilingual illustrated audiobook of a tale where the fox tricks the autumn into staying a little longer.",
        "rationale": (
            "Merry fox + English-Dutch bilingual storytelling, no audio overlay."
        ),
        "intents": [
            "Ingest the uploaded merry-fox portrait as the visual reference.",
            "Enrich the fox brief for consistent illustration.",
            "Write the narration script about the fox tricking autumn into staying.",
            "Generate one illustration per scene preserving the fox's reference likeness.",
            "Produce an English TTS narrator track for the fox tale.",
            "Translate the narration script into Dutch subtitle segments.",
            "Compose the slideshow with English narrator audio and bilingual English+Dutch captions.",
        ],
    },
    {
        "user_goal": "Using this uploaded golden-carp portrait, produce an English-Cantonese bilingual illustrated audiobook of the legend where the carp climbs the waterfall to become a dragon.",
        "rationale": (
            "Golden carp-becomes-dragon legend + English-Cantonese bilingual, no audio."
        ),
        "intents": [
            "Ingest the uploaded golden-carp portrait as the visual reference.",
            "Enrich the carp brief for consistent illustration as it climbs.",
            "Write the narration script about the carp climbing the waterfall to become a dragon.",
            "Generate one illustration per scene preserving the carp's reference likeness.",
            "Produce an English TTS narrator track for the legend.",
            "Translate the narration script into Cantonese subtitle segments.",
            "Compose the slideshow with English narrator audio and bilingual English+Cantonese captions.",
        ],
    },
    {
        "user_goal": "Using this uploaded clever-raven portrait, produce an English-Norwegian bilingual illustrated audiobook of a tale where the raven wins a bargain with the winter wind.",
        "rationale": (
            "Clever raven-and-winter-wind + English-Norwegian bilingual, no music/ambient."
        ),
        "intents": [
            "Ingest the uploaded clever-raven portrait as the visual reference.",
            "Enrich the raven brief for consistent illustration.",
            "Write the narration script about the raven winning a bargain with the winter wind.",
            "Generate one illustration per scene preserving the raven's reference likeness.",
            "Produce an English TTS narrator track for the raven tale.",
            "Translate the narration script into Norwegian subtitle segments.",
            "Compose the slideshow with English narrator audio and bilingual English+Norwegian captions.",
        ],
    },
    {
        "user_goal": "Using this uploaded dreaming-shepherd portrait, produce an English-Swedish bilingual illustrated audiobook of a tale where the shepherd's dreams grow into real wildflowers.",
        "rationale": (
            "Dreaming shepherd + English-Swedish bilingual, no audio overlay."
        ),
        "intents": [
            "Ingest the uploaded dreaming-shepherd portrait as the visual reference.",
            "Enrich the shepherd brief for consistent illustration.",
            "Write the narration script about the shepherd's dreams growing into wildflowers.",
            "Generate one illustration per scene preserving the shepherd's reference likeness.",
            "Produce an English TTS narrator track for the shepherd tale.",
            "Translate the narration script into Swedish subtitle segments.",
            "Compose the slideshow with English narrator audio and bilingual English+Swedish captions.",
        ],
    },
    {
        "user_goal": "Using this uploaded barefoot-poet portrait, produce an English-Greek bilingual illustrated audiobook of a tale where the poet writes poems into the sand that the tide keeps safe.",
        "rationale": (
            "Barefoot poet + English-Greek bilingual storytelling, no audio overlay."
        ),
        "intents": [
            "Ingest the uploaded barefoot-poet portrait as the visual reference.",
            "Enrich the poet brief for consistent illustration.",
            "Write the narration script about the poet's tide-kept sand poems.",
            "Generate one illustration per scene preserving the poet's reference likeness.",
            "Produce an English TTS narrator track for the poet tale.",
            "Translate the narration script into Greek subtitle segments.",
            "Compose the slideshow with English narrator audio and bilingual English+Greek captions.",
        ],
    },
    {
        "user_goal": "Using this uploaded hummingbird portrait, produce an English-Hebrew bilingual illustrated audiobook of a tale where the hummingbird carries water, drop by drop, to save the forest.",
        "rationale": (
            "Hummingbird forest-savior + English-Hebrew bilingual, no audio overlay."
        ),
        "intents": [
            "Ingest the uploaded tiny-hummingbird portrait as the visual reference.",
            "Enrich the hummingbird brief for consistent illustration.",
            "Write the narration script about the hummingbird carrying water drop by drop to save the forest.",
            "Generate one illustration per scene preserving the hummingbird's reference likeness.",
            "Produce an English TTS narrator track for the hummingbird tale.",
            "Translate the narration script into Hebrew subtitle segments.",
            "Compose the slideshow with English narrator audio and bilingual English+Hebrew captions.",
        ],
    },
    {
        "user_goal": "Using this uploaded wandering-minstrel portrait, produce an English-Turkish bilingual illustrated audiobook of a tale where the minstrel's song wakes the sleeping town.",
        "rationale": (
            "Wandering minstrel + English-Turkish bilingual storytelling, no audio overlay."
        ),
        "intents": [
            "Ingest the uploaded wandering-minstrel portrait as the visual reference.",
            "Enrich the minstrel brief for consistent illustration.",
            "Write the narration script about the minstrel's town-waking song.",
            "Generate one illustration per scene preserving the minstrel's reference likeness.",
            "Produce an English TTS narrator track for the minstrel tale.",
            "Translate the narration script into Turkish subtitle segments.",
            "Compose the slideshow with English narrator audio and bilingual English+Turkish captions.",
        ],
    },
]
