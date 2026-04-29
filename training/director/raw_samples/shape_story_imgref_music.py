"""Shape: story_imgref_music —
    IntakeImage → BriefEnricher → Narration → Illustration → Narrator → Music → AudioMix → Compositor.

Storytelling with reference image + BGM (no ambient, no bilingual).
"""
from __future__ import annotations

_CHAIN_SUMMARY = (
    "Chain: IntakeImage → BriefEnricher → Narration → Illustration → Narrator → Music → "
    "AudioMix → Compositor. Reject AmbienceAgent (music only asked), TranslationAgent (no "
    "bilingual ask), Story/Screenplay/KeyFrame/Video (those belong to live-action mini-drama, "
    "not illustrated-audiobook slideshow)."
)

SAMPLES: list[dict] = [
    {
        "user_goal": "Using this uploaded portrait of a dragon-protagonist, turn this short myth into an illustrated audiobook where the appearance stays consistent, with a soft guzheng score under the narration.",
        "rationale": (
            "Dragon-protagonist portrait + illustrated audiobook + soft-guzheng BGM (no "
            "ambient / no bilingual). " + _CHAIN_SUMMARY
        ),
        "intents": [
            "Ingest the uploaded dragon-protagonist portrait as the visual reference.",
            "Enrich the dragon brief so every illustration keeps the dragon consistent.",
            "Write the narration script for the myth where the dragon guards the last human child of a forgotten kingdom.",
            "Generate one illustration per scene preserving the dragon's reference likeness.",
            "Produce a warm TTS narrator track for the myth.",
            "Compose a soft guzheng BGM fitting the dragon-myth tone.",
            "Mix the guzheng BGM softly under the narrator track.",
            "Compose the slideshow pairing the reference-consistent illustrations with mixed narrator+music audio.",
        ],
    },
    {
        "user_goal": "Using this uploaded portrait of a samurai child, turn this short myth into an illustrated audiobook where the appearance stays consistent, with a gentle shakuhachi score under the narration.",
        "rationale": (
            "Samurai-child portrait + illustrated audiobook + gentle-shakuhachi BGM. " + _CHAIN_SUMMARY
        ),
        "intents": [
            "Ingest the uploaded samurai-child portrait as the visual reference.",
            "Enrich the samurai-child brief for consistent illustration.",
            "Write the narration script for the myth where the samurai-child learns swordplay from his ancestors' ghosts.",
            "Generate one illustration per scene preserving the samurai-child's reference likeness.",
            "Produce a warm TTS narrator track for the samurai myth.",
            "Compose a gentle shakuhachi BGM fitting the samurai-myth tone.",
            "Mix the shakuhachi BGM softly under the narrator track.",
            "Compose the slideshow with reference-consistent illustrations and mixed narrator+music audio.",
        ],
    },
    {
        "user_goal": "Using this uploaded portrait of a little elf-princess, turn this short myth into an illustrated audiobook where the appearance stays consistent, with a Celtic harp score under the narration.",
        "rationale": (
            "Elf-princess portrait + illustrated audiobook + Celtic-harp BGM. " + _CHAIN_SUMMARY
        ),
        "intents": [
            "Ingest the uploaded elf-princess portrait as the visual reference.",
            "Enrich the elf-princess brief for consistent illustration.",
            "Write the narration script about the elf-princess befriending a wounded deer in the winter wood.",
            "Generate one illustration per scene preserving the elf-princess's reference likeness.",
            "Produce a warm TTS narrator track for the elf-princess myth.",
            "Compose a Celtic harp BGM fitting the elf-princess tone.",
            "Mix the Celtic harp BGM softly under the narrator track.",
            "Compose the slideshow with reference-consistent illustrations and mixed narrator+music audio.",
        ],
    },
    {
        "user_goal": "Using this uploaded portrait of an owl-mentor, turn this short myth into an illustrated audiobook where the appearance stays consistent, with a gentle piano score under the narration.",
        "rationale": (
            "Owl-mentor portrait + illustrated audiobook + gentle-piano BGM. " + _CHAIN_SUMMARY
        ),
        "intents": [
            "Ingest the uploaded owl-mentor portrait as the visual reference.",
            "Enrich the owl-mentor brief for consistent illustration.",
            "Write the narration script about the owl mentoring a fledgling phoenix learning to fly.",
            "Generate one illustration per scene preserving the owl's reference likeness.",
            "Produce a warm TTS narrator track for the owl-mentor myth.",
            "Compose a gentle piano BGM fitting the owl-mentor tone.",
            "Mix the piano BGM softly under the narrator track.",
            "Compose the slideshow with reference-consistent illustrations and mixed narrator+music audio.",
        ],
    },
    {
        "user_goal": "Using this uploaded portrait of a Viking girl-warrior, turn this short myth into an illustrated audiobook where the appearance stays consistent, with a Nordic-folk lyre score under the narration.",
        "rationale": (
            "Viking girl-warrior + illustrated audiobook + Nordic-folk-lyre BGM. " + _CHAIN_SUMMARY
        ),
        "intents": [
            "Ingest the uploaded Viking girl-warrior portrait as the visual reference.",
            "Enrich the warrior brief for consistent illustration.",
            "Write the narration script about the warrior facing a sea-troll with only a wooden sword.",
            "Generate one illustration per scene preserving the warrior's reference likeness.",
            "Produce a warm TTS narrator track for the Viking myth.",
            "Compose a Nordic-folk lyre BGM fitting the Viking-warrior tone.",
            "Mix the lyre BGM softly under the narrator track.",
            "Compose the slideshow with reference-consistent illustrations and mixed narrator+music audio.",
        ],
    },
    {
        "user_goal": "Using this uploaded portrait of a sea-witch, turn this short myth into an illustrated audiobook where the appearance stays consistent, with a haunting celesta score under the narration.",
        "rationale": (
            "Sea-witch + illustrated audiobook + haunting-celesta BGM. " + _CHAIN_SUMMARY
        ),
        "intents": [
            "Ingest the uploaded sea-witch portrait as the visual reference.",
            "Enrich the sea-witch brief for consistent illustration.",
            "Write the narration script about the sea-witch returning lost memories to widowed fishermen.",
            "Generate one illustration per scene preserving the sea-witch's reference likeness.",
            "Produce a contemplative TTS narrator track for the sea-witch myth.",
            "Compose a haunting celesta BGM fitting the sea-witch tone.",
            "Mix the celesta BGM softly under the narrator track.",
            "Compose the slideshow with reference-consistent illustrations and mixed narrator+music audio.",
        ],
    },
    {
        "user_goal": "Using this uploaded portrait of a fox in a snow-kimono, turn this short myth into an illustrated audiobook where the appearance stays consistent, with a gentle koto score under the narration.",
        "rationale": (
            "Snow-kimono fox + illustrated audiobook + gentle-koto BGM. " + _CHAIN_SUMMARY
        ),
        "intents": [
            "Ingest the uploaded snow-kimono fox portrait as the visual reference.",
            "Enrich the fox brief for consistent illustration.",
            "Write the narration script about the fox teaching a lost traveler the way back through the cedars.",
            "Generate one illustration per scene preserving the fox's reference likeness.",
            "Produce a warm TTS narrator track for the fox myth.",
            "Compose a gentle koto BGM fitting the snow-kimono-fox tone.",
            "Mix the koto BGM softly under the narrator track.",
            "Compose the slideshow with reference-consistent illustrations and mixed narrator+music audio.",
        ],
    },
    {
        "user_goal": "Using this uploaded portrait of a lantern-carrier, turn this short myth into an illustrated audiobook where the appearance stays consistent, with a tender harp-and-flute score under the narration.",
        "rationale": (
            "Lantern-carrier + illustrated audiobook + tender-harp-and-flute BGM. " + _CHAIN_SUMMARY
        ),
        "intents": [
            "Ingest the uploaded lantern-carrier portrait as the visual reference.",
            "Enrich the lantern-carrier brief for consistent illustration.",
            "Write the narration script about the lantern-carrier lighting the paths of wandering souls home.",
            "Generate one illustration per scene preserving the lantern-carrier's reference likeness.",
            "Produce a tender TTS narrator track for the myth.",
            "Compose a tender harp-and-flute BGM fitting the lantern-carrier tone.",
            "Mix the harp-flute BGM softly under the narrator track.",
            "Compose the slideshow with reference-consistent illustrations and mixed narrator+music audio.",
        ],
    },
    {
        "user_goal": "Using this uploaded portrait of a girl riding a giant moth, turn this short myth into an illustrated audiobook where the appearance stays consistent, with a dreamy ambient-harp score under the narration.",
        "rationale": (
            "Girl-riding-moth + illustrated audiobook + dreamy-ambient-harp BGM (music genre, "
            "not environmental sound). " + _CHAIN_SUMMARY
        ),
        "intents": [
            "Ingest the uploaded girl-on-moth portrait as the visual reference.",
            "Enrich the brief so girl and moth stay consistent across scenes.",
            "Write the narration script about the moth-rider bringing dreams to a sleeping city.",
            "Generate one illustration per scene preserving girl and moth reference likenesses.",
            "Produce a dreamy TTS narrator track for the myth.",
            "Compose a dreamy ambient-harp BGM fitting the moth-rider tone.",
            "Mix the ambient-harp BGM softly under the narrator track.",
            "Compose the slideshow with reference-consistent illustrations and mixed narrator+music audio.",
        ],
    },
    {
        "user_goal": "Using this uploaded portrait of an old turtle, turn this short myth into an illustrated audiobook where the appearance stays consistent, with a contemplative piano score under the narration.",
        "rationale": (
            "Old turtle + illustrated audiobook + contemplative-piano BGM. " + _CHAIN_SUMMARY
        ),
        "intents": [
            "Ingest the uploaded old-turtle portrait as the visual reference.",
            "Enrich the turtle brief for consistent illustration.",
            "Write the narration script about the turtle carrying the world on his back through an ocean of stars.",
            "Generate one illustration per scene preserving the turtle's reference likeness.",
            "Produce a contemplative TTS narrator track for the turtle myth.",
            "Compose a contemplative piano BGM fitting the turtle tone.",
            "Mix the piano BGM softly under the narrator track.",
            "Compose the slideshow with reference-consistent illustrations and mixed narrator+music audio.",
        ],
    },
    {
        "user_goal": "Using this uploaded portrait of a young forest-spirit, turn this short myth into an illustrated audiobook where the appearance stays consistent, with a soft woodwind quartet score under the narration.",
        "rationale": (
            "Forest-spirit + illustrated audiobook + soft-woodwind-quartet BGM. " + _CHAIN_SUMMARY
        ),
        "intents": [
            "Ingest the uploaded forest-spirit portrait as the visual reference.",
            "Enrich the forest-spirit brief for consistent illustration.",
            "Write the narration script about the spirit teaching children how to hear trees speak.",
            "Generate one illustration per scene preserving the spirit's reference likeness.",
            "Produce a warm TTS narrator track for the forest-spirit myth.",
            "Compose a soft woodwind-quartet BGM fitting the forest-spirit tone.",
            "Mix the woodwind BGM softly under the narrator track.",
            "Compose the slideshow with reference-consistent illustrations and mixed narrator+music audio.",
        ],
    },
    {
        "user_goal": "Using this uploaded portrait of a lonely moon, turn this short myth into an illustrated audiobook where the appearance stays consistent, with a gentle solo cello score under the narration.",
        "rationale": (
            "Lonely moon + illustrated audiobook + gentle-solo-cello BGM. " + _CHAIN_SUMMARY
        ),
        "intents": [
            "Ingest the uploaded lonely-moon portrait as the visual reference.",
            "Enrich the moon brief for consistent illustration.",
            "Write the narration script about the moon coming down to meet the child who wished on her.",
            "Generate one illustration per scene preserving the moon's reference likeness.",
            "Produce a tender TTS narrator track for the lonely-moon myth.",
            "Compose a gentle solo-cello BGM fitting the lonely-moon tone.",
            "Mix the cello BGM softly under the narrator track.",
            "Compose the slideshow with reference-consistent illustrations and mixed narrator+music audio.",
        ],
    },
    {
        "user_goal": "Using this uploaded portrait of a wise crane, turn this short myth into an illustrated audiobook where the appearance stays consistent, with a soft shakuhachi score under the narration.",
        "rationale": (
            "Wise crane + illustrated audiobook + soft-shakuhachi BGM. " + _CHAIN_SUMMARY
        ),
        "intents": [
            "Ingest the uploaded wise-crane portrait as the visual reference.",
            "Enrich the crane brief for consistent illustration.",
            "Write the narration script about the crane carrying grandparents' lullabies across centuries.",
            "Generate one illustration per scene preserving the crane's reference likeness.",
            "Produce a warm TTS narrator track for the crane myth.",
            "Compose a soft shakuhachi BGM fitting the crane tone.",
            "Mix the shakuhachi BGM softly under the narrator track.",
            "Compose the slideshow with reference-consistent illustrations and mixed narrator+music audio.",
        ],
    },
    {
        "user_goal": "Using this uploaded portrait of a tiny fire-sprite, turn this short myth into an illustrated audiobook where the appearance stays consistent, with a warm acoustic guitar score under the narration.",
        "rationale": (
            "Fire-sprite + illustrated audiobook + warm-acoustic-guitar BGM. " + _CHAIN_SUMMARY
        ),
        "intents": [
            "Ingest the uploaded fire-sprite portrait as the visual reference.",
            "Enrich the sprite brief for consistent illustration.",
            "Write the narration script about the sprite finding a home inside a village woodstove.",
            "Generate one illustration per scene preserving the sprite's reference likeness.",
            "Produce a warm TTS narrator track for the fire-sprite myth.",
            "Compose a warm acoustic-guitar BGM fitting the sprite tone.",
            "Mix the guitar BGM softly under the narrator track.",
            "Compose the slideshow with reference-consistent illustrations and mixed narrator+music audio.",
        ],
    },
    {
        "user_goal": "Using this uploaded portrait of an island-hopping sailor-girl, turn this short myth into an illustrated audiobook where the appearance stays consistent, with an Irish pennywhistle score under the narration.",
        "rationale": (
            "Island-hopping sailor-girl + illustrated audiobook + Irish-pennywhistle BGM. "
            + _CHAIN_SUMMARY
        ),
        "intents": [
            "Ingest the uploaded sailor-girl portrait as the visual reference.",
            "Enrich the sailor brief for consistent illustration.",
            "Write the narration script about the sailor charting new constellations with seashell maps.",
            "Generate one illustration per scene preserving the sailor's reference likeness.",
            "Produce an adventurous TTS narrator track for the sailor myth.",
            "Compose an Irish pennywhistle BGM fitting the sailor tone.",
            "Mix the pennywhistle BGM softly under the narrator track.",
            "Compose the slideshow with reference-consistent illustrations and mixed narrator+music audio.",
        ],
    },
    {
        "user_goal": "Using this uploaded portrait of a shy tiger-cub, turn this short myth into an illustrated audiobook where the appearance stays consistent, with a gentle cello-and-piano score under the narration.",
        "rationale": (
            "Shy tiger-cub + illustrated audiobook + gentle-cello-and-piano BGM. " + _CHAIN_SUMMARY
        ),
        "intents": [
            "Ingest the uploaded tiger-cub portrait as the visual reference.",
            "Enrich the cub brief for consistent illustration.",
            "Write the narration script about the cub learning to roar by echoing the mountain itself.",
            "Generate one illustration per scene preserving the cub's reference likeness.",
            "Produce a warm TTS narrator track for the cub myth.",
            "Compose a gentle cello-and-piano BGM fitting the cub tone.",
            "Mix the BGM softly under the narrator track.",
            "Compose the slideshow with reference-consistent illustrations and mixed narrator+music audio.",
        ],
    },
    {
        "user_goal": "Using this uploaded portrait of a cave-painting bison, turn this short myth into an illustrated audiobook where the appearance stays consistent, with an ancient-sounding bone-flute score under the narration.",
        "rationale": (
            "Cave-painting bison + illustrated audiobook + ancient-bone-flute BGM. " + _CHAIN_SUMMARY
        ),
        "intents": [
            "Ingest the uploaded cave-painting bison portrait as the visual reference.",
            "Enrich the bison brief for consistent illustration.",
            "Write the narration script about the bison coming alive after the painter finally speaks her name.",
            "Generate one illustration per scene preserving the bison's reference likeness.",
            "Produce a reverent TTS narrator track for the bison myth.",
            "Compose an ancient-sounding bone-flute BGM fitting the bison tone.",
            "Mix the bone-flute BGM softly under the narrator track.",
            "Compose the slideshow with reference-consistent illustrations and mixed narrator+music audio.",
        ],
    },
    {
        "user_goal": "Using this uploaded portrait of a young sorceress, turn this short myth into an illustrated audiobook where the appearance stays consistent, with a soft chamber-strings score under the narration.",
        "rationale": (
            "Young sorceress + illustrated audiobook + soft-chamber-strings BGM. " + _CHAIN_SUMMARY
        ),
        "intents": [
            "Ingest the uploaded sorceress portrait as the visual reference.",
            "Enrich the sorceress brief for consistent illustration.",
            "Write the narration script about the sorceress turning her tears into silver fish for the village's starving.",
            "Generate one illustration per scene preserving the sorceress's reference likeness.",
            "Produce a warm TTS narrator track for the sorceress myth.",
            "Compose a soft chamber-strings BGM fitting the sorceress tone.",
            "Mix the strings BGM softly under the narrator track.",
            "Compose the slideshow with reference-consistent illustrations and mixed narrator+music audio.",
        ],
    },
    {
        "user_goal": "Using this uploaded portrait of an ink-painter monk, turn this short myth into an illustrated audiobook where the appearance stays consistent, with a delicate koto-and-flute score under the narration.",
        "rationale": (
            "Ink-painter monk + illustrated audiobook + delicate-koto-and-flute BGM. "
            + _CHAIN_SUMMARY
        ),
        "intents": [
            "Ingest the uploaded ink-painter monk portrait as the visual reference.",
            "Enrich the monk brief for consistent illustration.",
            "Write the narration script about the monk's brush painting mountains that grow real by moonlight.",
            "Generate one illustration per scene preserving the monk's reference likeness.",
            "Produce a contemplative TTS narrator track for the monk myth.",
            "Compose a delicate koto-and-flute BGM fitting the monk tone.",
            "Mix the koto-flute BGM softly under the narrator track.",
            "Compose the slideshow with reference-consistent illustrations and mixed narrator+music audio.",
        ],
    },
    {
        "user_goal": "Using this uploaded portrait of a rainbow-scaled sea-dragon, turn this short myth into an illustrated audiobook where the appearance stays consistent, with a gentle waterphone-and-harp score under the narration.",
        "rationale": (
            "Rainbow-scaled sea-dragon + illustrated audiobook + gentle-waterphone-and-harp "
            "BGM. " + _CHAIN_SUMMARY
        ),
        "intents": [
            "Ingest the uploaded sea-dragon portrait as the visual reference.",
            "Enrich the sea-dragon brief for consistent illustration.",
            "Write the narration script about the sea-dragon carrying sunken letters back to grieving mothers.",
            "Generate one illustration per scene preserving the sea-dragon's reference likeness.",
            "Produce a tender TTS narrator track for the sea-dragon myth.",
            "Compose a gentle waterphone-and-harp BGM fitting the sea-dragon tone.",
            "Mix the BGM softly under the narrator track.",
            "Compose the slideshow with reference-consistent illustrations and mixed narrator+music audio.",
        ],
    },
]
