"""Shape: story_pure —
    Narration → Illustration → Narrator → Compositor.

Illustrated audiobook / storybook slideshow. Target 80 (50 long-story +
30 short-brief). Here: 30 short-brief samples.
"""
from __future__ import annotations

SAMPLES: list[dict] = [
    {
        "user_goal": "Make an illustrated audiobook video of this children's bedtime tale about a little rabbit named Pip who finds a glowing seed in the meadow — calm narration with one soft watercolor picture per scene.",
        "rationale": (
            "Illustrated bedtime tale + slideshow narration. Chain: Narration → Illustration "
            "→ Narrator → Compositor. Reject Story/Screenplay/KeyFrame/Video (those are for "
            "live-action mini-drama, not slideshow)."
        ),
        "intents": [
            "Write the narration script from the Pip-and-glowing-seed bedtime tale.",
            "Generate one soft watercolor illustration per narrated scene.",
            "Produce a calm TTS narrator track for the Pip story.",
            "Compose the final illustrated-audiobook slideshow pairing illustrations with narrator audio.",
        ],
    },
    {
        "user_goal": "Read this classical Tang-dynasty poem aloud and show a matching ink-painting illustration for each verse, slideshow-style.",
        "rationale": (
            "Tang poem recitation + ink-painting per verse + slideshow narration."
        ),
        "intents": [
            "Write the narration script from the Tang-dynasty poem.",
            "Generate a matching ink-painting illustration for each verse.",
            "Produce a measured TTS narrator track for the Tang poem.",
            "Compose the final slideshow pairing ink-painting illustrations with narrator audio.",
        ],
    },
    {
        "user_goal": "Produce a narrated picture-book science storytime about how emperor penguins raise their chicks in Antarctica; one cute cartoon image per behavior.",
        "rationale": (
            "Science storytime picture-book + one cartoon image per behavior + slideshow "
            "narration."
        ),
        "intents": [
            "Write the narration script from the emperor-penguin science storytime.",
            "Generate one cute cartoon illustration per penguin behavior.",
            "Produce a friendly TTS narrator track for the penguin storytime.",
            "Compose the final slideshow pairing penguin illustrations with narrator audio.",
        ],
    },
    {
        "user_goal": "Make an illustrated audiobook of this Aesop fable about the Fox and the Crow, with one classic-style illustration per plot beat.",
        "rationale": (
            "Aesop fable illustrated audiobook + classic-style illustrations + slideshow "
            "narration."
        ),
        "intents": [
            "Write the narration script from the Aesop Fox-and-Crow fable.",
            "Generate one classic-style illustration per plot beat.",
            "Produce a measured TTS narrator track for the fable.",
            "Compose the final slideshow pairing classic illustrations with narrator audio.",
        ],
    },
    {
        "user_goal": "Make an illustrated storybook video of this Beatrix-Potter-style tale about a hedgehog named Mrs. Tiggywiggle sorting her forest laundry, with one watercolor illustration per scene.",
        "rationale": (
            "Beatrix-Potter-style hedgehog tale + watercolor illustration per scene + slideshow "
            "narration."
        ),
        "intents": [
            "Write the narration script from the Mrs.-Tiggywiggle hedgehog tale.",
            "Generate one Beatrix-Potter-style watercolor per scene.",
            "Produce a gentle TTS narrator track for the hedgehog tale.",
            "Compose the final slideshow pairing watercolors with narrator audio.",
        ],
    },
    {
        "user_goal": "Make an illustrated audiobook of this Norse myth about Thor retrieving his stolen hammer, with one woodcut-style illustration per chapter.",
        "rationale": (
            "Norse Thor myth + woodcut illustrations + slideshow narration."
        ),
        "intents": [
            "Write the narration script from the Thor-hammer-retrieval myth.",
            "Generate one woodcut-style illustration per chapter.",
            "Produce a booming TTS narrator track for the Thor myth.",
            "Compose the final slideshow pairing woodcut illustrations with narrator audio.",
        ],
    },
    {
        "user_goal": "Make an illustrated audiobook of this Hans Christian Andersen tale about the Little Match Girl, with one soft-pastel illustration per scene.",
        "rationale": (
            "Andersen Little Match Girl + soft-pastel illustrations + slideshow narration."
        ),
        "intents": [
            "Write the narration script from the Little-Match-Girl tale.",
            "Generate one soft-pastel illustration per scene.",
            "Produce a tender TTS narrator track for the Little-Match-Girl tale.",
            "Compose the final slideshow pairing pastel illustrations with narrator audio.",
        ],
    },
    {
        "user_goal": "Make an illustrated audiobook of this Indigenous North-American creation story about how the raven brought light to the world, with one totem-pole-style illustration per episode.",
        "rationale": (
            "Raven-brought-light creation story + totem-pole-style illustrations + slideshow "
            "narration."
        ),
        "intents": [
            "Write the narration script from the raven-creation story.",
            "Generate one totem-pole-style illustration per episode.",
            "Produce a reverent TTS narrator track for the raven myth.",
            "Compose the final slideshow pairing totem illustrations with narrator audio.",
        ],
    },
    {
        "user_goal": "Make an illustrated audiobook video of this Japanese fairytale about a crane-wife secretly weaving silk for her poor husband, with one ink-and-wash illustration per scene.",
        "rationale": (
            "Japanese crane-wife fairytale + ink-and-wash illustrations + slideshow narration."
        ),
        "intents": [
            "Write the narration script from the crane-wife fairytale.",
            "Generate one Japanese ink-and-wash illustration per scene.",
            "Produce a contemplative TTS narrator track for the crane-wife tale.",
            "Compose the final slideshow pairing ink-and-wash illustrations with narrator audio.",
        ],
    },
    {
        "user_goal": "Make a narrated picture-book storytime about how honeybees pollinate flowers for a preschool audience, with cheerful cartoon illustrations for each step.",
        "rationale": (
            "Honeybee preschool science storytime + cheerful cartoon illustrations + slideshow "
            "narration."
        ),
        "intents": [
            "Write the narration script from the honeybee-pollination storytime.",
            "Generate one cheerful cartoon illustration per pollination step.",
            "Produce a cheerful TTS narrator track for the honeybee storytime.",
            "Compose the final slideshow pairing cartoons with narrator audio.",
        ],
    },
    {
        "user_goal": "Make an illustrated audiobook video of this Russian folktale about Vasilisa the Beautiful and Baba Yaga's hut, with one Ivan-Bilibin-style illustration per scene.",
        "rationale": (
            "Vasilisa-Baba-Yaga Russian folktale + Ivan-Bilibin illustrations + slideshow "
            "narration."
        ),
        "intents": [
            "Write the narration script from the Vasilisa-and-Baba-Yaga folktale.",
            "Generate one Ivan-Bilibin-style illustration per scene.",
            "Produce a mystical TTS narrator track for the folktale.",
            "Compose the final slideshow pairing Bilibin-style illustrations with narrator audio.",
        ],
    },
    {
        "user_goal": "Make an illustrated bedtime-story video of this fable about a turtle who befriends a cloud, with soft-pastel watercolor illustrations for each scene.",
        "rationale": (
            "Turtle-and-cloud fable + soft-pastel watercolor illustrations + slideshow "
            "narration."
        ),
        "intents": [
            "Write the narration script from the turtle-and-cloud fable.",
            "Generate one soft-pastel watercolor illustration per scene.",
            "Produce a calm TTS narrator track for the fable.",
            "Compose the final slideshow pairing watercolors with narrator audio.",
        ],
    },
    {
        "user_goal": "Make a narrated picture-book science storytime for kids about how an oak tree grows from acorn to giant, with warm cartoon illustrations for each growth stage.",
        "rationale": (
            "Oak-tree growth science storytime + warm cartoon illustrations + slideshow "
            "narration."
        ),
        "intents": [
            "Write the narration script from the oak-tree-growth storytime.",
            "Generate one warm cartoon illustration per growth stage.",
            "Produce a friendly TTS narrator track for the oak-tree storytime.",
            "Compose the final slideshow pairing illustrations with narrator audio.",
        ],
    },
    {
        "user_goal": "Make an illustrated audiobook of this African folktale about Anansi the spider tricking the python, with bright-palette illustrations for each trick.",
        "rationale": (
            "Anansi-the-spider African folktale + bright-palette illustrations + slideshow "
            "narration."
        ),
        "intents": [
            "Write the narration script from the Anansi-spider folktale.",
            "Generate one bright-palette illustration per Anansi trick.",
            "Produce a playful TTS narrator track for the Anansi tale.",
            "Compose the final slideshow pairing illustrations with narrator audio.",
        ],
    },
    {
        "user_goal": "Make an illustrated audiobook of this Sufi parable about the reed-flute yearning for home, with calligraphic illustrations for each verse.",
        "rationale": (
            "Sufi reed-flute parable + calligraphic illustrations + slideshow narration."
        ),
        "intents": [
            "Write the narration script from the Sufi reed-flute parable.",
            "Generate one calligraphic illustration per verse.",
            "Produce a reverent TTS narrator track for the parable.",
            "Compose the final slideshow pairing calligraphy with narrator audio.",
        ],
    },
    {
        "user_goal": "Make a narrated picture-book storytime for kids about how butterflies migrate across continents, with bright-watercolor illustrations for each migration stage.",
        "rationale": (
            "Butterfly migration storytime + bright-watercolor illustrations + slideshow "
            "narration."
        ),
        "intents": [
            "Write the narration script from the butterfly-migration storytime.",
            "Generate one bright-watercolor illustration per migration stage.",
            "Produce a bright TTS narrator track for the butterfly-migration storytime.",
            "Compose the final slideshow pairing watercolors with narrator audio.",
        ],
    },
    {
        "user_goal": "Make an illustrated audiobook of this Hindu fable about how Ganesha lost his tusk, with warm gouache illustrations per scene.",
        "rationale": (
            "Ganesha-lost-his-tusk Hindu fable + warm gouache illustrations + slideshow "
            "narration."
        ),
        "intents": [
            "Write the narration script from the Ganesha-tusk fable.",
            "Generate one warm gouache illustration per scene.",
            "Produce a reverent TTS narrator track for the Ganesha fable.",
            "Compose the final slideshow pairing gouache illustrations with narrator audio.",
        ],
    },
    {
        "user_goal": "Make a narrated picture-book storytime for kids about how a baby sea turtle makes its first trip from beach-nest to ocean, with coastal-watercolor illustrations per trip stage.",
        "rationale": (
            "Baby sea-turtle first-journey storytime + coastal-watercolor illustrations + "
            "slideshow narration."
        ),
        "intents": [
            "Write the narration script from the baby-sea-turtle first-journey storytime.",
            "Generate one coastal-watercolor illustration per journey stage.",
            "Produce a gentle TTS narrator track for the sea-turtle storytime.",
            "Compose the final slideshow pairing watercolors with narrator audio.",
        ],
    },
    {
        "user_goal": "Make an illustrated audiobook of this Greek myth about Persephone's descent into the underworld, with classical-Greek-vase-style illustrations per scene.",
        "rationale": (
            "Persephone Greek myth + Greek-vase-style illustrations + slideshow narration."
        ),
        "intents": [
            "Write the narration script from the Persephone myth.",
            "Generate one Greek-vase-style illustration per scene.",
            "Produce a solemn TTS narrator track for the Persephone myth.",
            "Compose the final slideshow pairing Greek-vase illustrations with narrator audio.",
        ],
    },
    {
        "user_goal": "Make a narrated picture-book storytime about how a tiny seed becomes a sunflower, with bright kid-friendly illustrations per growth stage.",
        "rationale": (
            "Seed-to-sunflower storytime + bright kid-friendly illustrations + slideshow "
            "narration."
        ),
        "intents": [
            "Write the narration script from the seed-to-sunflower storytime.",
            "Generate one bright kid-friendly illustration per growth stage.",
            "Produce a friendly TTS narrator track for the seed-to-sunflower storytime.",
            "Compose the final slideshow pairing illustrations with narrator audio.",
        ],
    },
    {
        "user_goal": "Make an illustrated audiobook of this Native-Hawaiian creation chant about the goddess Pele shaping the islands, with Polynesian-traditional-art illustrations per episode.",
        "rationale": (
            "Pele creation-chant Hawaiian myth + Polynesian-traditional illustrations + "
            "slideshow narration."
        ),
        "intents": [
            "Write the narration script from the Pele creation chant.",
            "Generate one Polynesian-traditional-art illustration per episode.",
            "Produce a reverent TTS narrator track for the chant.",
            "Compose the final slideshow pairing Polynesian illustrations with narrator audio.",
        ],
    },
    {
        "user_goal": "Make a narrated picture-book storytime about how Arctic foxes survive winter, with gentle watercolor illustrations per Arctic-fox behavior.",
        "rationale": (
            "Arctic-fox winter-survival storytime + gentle watercolor illustrations + slideshow "
            "narration."
        ),
        "intents": [
            "Write the narration script from the Arctic-fox winter-survival storytime.",
            "Generate one gentle watercolor illustration per Arctic-fox behavior.",
            "Produce a warm TTS narrator track for the Arctic-fox storytime.",
            "Compose the final slideshow pairing watercolors with narrator audio.",
        ],
    },
    {
        "user_goal": "Make an illustrated audiobook of this Irish folktale about the selkie who left her seal-skin on the shore, with Celtic-knot-border watercolor illustrations per scene.",
        "rationale": (
            "Selkie Irish folktale + Celtic-knot-border watercolor illustrations + slideshow "
            "narration."
        ),
        "intents": [
            "Write the narration script from the selkie folktale.",
            "Generate one Celtic-knot-border watercolor illustration per scene.",
            "Produce a lilting TTS narrator track for the selkie tale.",
            "Compose the final slideshow pairing illustrations with narrator audio.",
        ],
    },
    {
        "user_goal": "Make an illustrated audiobook of this Navajo creation story about Spider Woman teaching weaving, with Navajo-textile-pattern illustrations per episode.",
        "rationale": (
            "Spider-Woman Navajo creation + Navajo-textile illustrations + slideshow narration."
        ),
        "intents": [
            "Write the narration script from the Spider-Woman Navajo creation.",
            "Generate one Navajo-textile-pattern illustration per episode.",
            "Produce a reverent TTS narrator track for the creation story.",
            "Compose the final slideshow pairing illustrations with narrator audio.",
        ],
    },
    {
        "user_goal": "Make a narrated picture-book storytime for kids about how fireflies light up summer meadows, with soft-glow watercolor illustrations per firefly behavior.",
        "rationale": (
            "Firefly summer-meadow storytime + soft-glow watercolor illustrations + slideshow "
            "narration."
        ),
        "intents": [
            "Write the narration script from the firefly-summer-meadow storytime.",
            "Generate one soft-glow watercolor illustration per firefly behavior.",
            "Produce a dreamy TTS narrator track for the firefly storytime.",
            "Compose the final slideshow pairing watercolors with narrator audio.",
        ],
    },
    {
        "user_goal": "Make an illustrated audiobook of this Korean fable about the tiger and the rabbit crossing a river together, with Korean-folk-art illustrations per scene.",
        "rationale": (
            "Korean tiger-and-rabbit fable + Korean-folk-art illustrations + slideshow "
            "narration."
        ),
        "intents": [
            "Write the narration script from the Korean tiger-and-rabbit fable.",
            "Generate one Korean-folk-art illustration per scene.",
            "Produce a playful TTS narrator track for the fable.",
            "Compose the final slideshow pairing illustrations with narrator audio.",
        ],
    },
    {
        "user_goal": "Make a narrated picture-book storytime about the life cycle of a dragonfly, with vibrant watercolor illustrations per life stage.",
        "rationale": (
            "Dragonfly life-cycle storytime + vibrant watercolor illustrations + slideshow "
            "narration."
        ),
        "intents": [
            "Write the narration script from the dragonfly life-cycle storytime.",
            "Generate one vibrant watercolor illustration per life stage.",
            "Produce a curious TTS narrator track for the dragonfly storytime.",
            "Compose the final slideshow pairing watercolors with narrator audio.",
        ],
    },
    {
        "user_goal": "Make an illustrated audiobook of this Brothers-Grimm tale about a poor tailor outwitting a giant, with retro-storybook illustrations per scene.",
        "rationale": (
            "Brothers-Grimm tailor-and-giant tale + retro-storybook illustrations + slideshow "
            "narration."
        ),
        "intents": [
            "Write the narration script from the Brothers-Grimm tailor-and-giant tale.",
            "Generate one retro-storybook illustration per scene.",
            "Produce a whimsical TTS narrator track for the Grimm tale.",
            "Compose the final slideshow pairing retro illustrations with narrator audio.",
        ],
    },
    {
        "user_goal": "Make an illustrated audiobook of this Australian Aboriginal Dreamtime story about how the kangaroo got its pouch, with dot-art illustrations per episode.",
        "rationale": (
            "Aboriginal Dreamtime kangaroo-pouch story + dot-art illustrations + slideshow "
            "narration."
        ),
        "intents": [
            "Write the narration script from the Aboriginal Dreamtime kangaroo story.",
            "Generate one dot-art illustration per episode.",
            "Produce a reverent TTS narrator track for the Dreamtime story.",
            "Compose the final slideshow pairing dot-art illustrations with narrator audio.",
        ],
    },
    {
        "user_goal": "Make a narrated picture-book storytime about how frogs migrate between pond and forest each year, with gentle cartoon illustrations per migration step.",
        "rationale": (
            "Frog pond-and-forest migration storytime + gentle cartoon illustrations + "
            "slideshow narration."
        ),
        "intents": [
            "Write the narration script from the frog-migration storytime.",
            "Generate one gentle cartoon illustration per migration step.",
            "Produce a cheerful TTS narrator track for the frog-migration storytime.",
            "Compose the final slideshow pairing cartoons with narrator audio.",
        ],
    },
]
