"""Shape: style_extend_music — IntakeVideo → StyleTransfer → VideoExtend → Music → AudioMix → Compositor.

Uploaded video: restyled → extended → BGM.  Order matters: Style first
(so the extended clip inherits the styled look), then Extend (produces
longer styled clip), then Music+AudioMix+Compositor for the BGM layer.
"""
from __future__ import annotations

SAMPLES: list[dict] = [
    {
        "user_goal": "Please turn this 6-second drone clip into Ghibli-watercolor, extend it to 20 seconds, and add a gentle folk BGM.",
        "rationale": (
            "User uploaded a 6-second drone clip, asks for Ghibli watercolor style + extend "
            "to 20s + gentle folk BGM. IntakeVideoAgent ingests. StyleTransferAgent applies "
            "the Ghibli-watercolor first (so the extension inherits the styled baseline). "
            "VideoExtendAgent extends the styled clip to 20 seconds. MusicAgent composes the "
            "folk BGM. AudioMixAgent mixes BGM with baked audio. CompositorAgent muxes the "
            "audio onto the styled-extended clip."
        ),
        "intents": [
            "Ingest the 6-second drone clip into the workspace.",
            "Restyle the drone footage into a Studio Ghibli watercolor aesthetic.",
            "Extend the styled drone clip to ~20 seconds preserving the watercolor look.",
            "Compose a gentle folk BGM covering the extended ~20-second length.",
            "Mix the folk BGM with the styled-extended clip's baked audio.",
            "Compose the final clip with the mixed folk BGM overlaid on the styled-extended drone footage.",
        ],
    },
    {
        "user_goal": "Restyle this 5-second skate clip as ukiyo-e, extend it to 15 seconds, and add some traditional Japanese koto BGM.",
        "rationale": (
            "Skate clip + ukiyo-e style + extend-to-15s + koto BGM. IntakeVideoAgent → "
            "StyleTransferAgent (ukiyo-e) → VideoExtendAgent (~15s) → MusicAgent (koto) → "
            "AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the 5-second skate clip into the workspace.",
            "Restyle the skate footage into a Japanese ukiyo-e woodblock aesthetic.",
            "Extend the styled skate clip to ~15 seconds preserving the ukiyo-e look.",
            "Compose a traditional Japanese koto BGM covering the extended length.",
            "Mix the koto BGM with the styled-extended skate clip's baked audio.",
            "Compose the final clip with the mixed koto BGM overlaid on the styled-extended skate footage.",
        ],
    },
    {
        "user_goal": "Please restyle this 7-second cityscape clip as Blade Runner cyberpunk, extend to 25 seconds, and add a synthwave BGM.",
        "rationale": (
            "Cityscape + Blade Runner cyberpunk style + extend-to-25s + synthwave BGM. "
            "IntakeVideoAgent → StyleTransferAgent (Blade Runner cyberpunk) → "
            "VideoExtendAgent (~25s) → MusicAgent (synthwave) → AudioMixAgent → "
            "CompositorAgent."
        ),
        "intents": [
            "Ingest the 7-second cityscape clip into the workspace.",
            "Restyle the cityscape footage into a Blade Runner neon-cyberpunk aesthetic.",
            "Extend the styled cityscape clip to ~25 seconds preserving the cyberpunk look.",
            "Compose a synthwave BGM covering the extended length.",
            "Mix the synthwave BGM with the styled-extended cityscape's baked audio.",
            "Compose the final clip with the mixed synthwave BGM overlaid on the styled-extended footage.",
        ],
    },
    {
        "user_goal": "Apply a Van Gogh impasto style to this 6-second lavender-field clip, extend to 20 seconds, and add a dreamy piano BGM.",
        "rationale": (
            "Lavender-field clip + Van Gogh impasto + extend-to-20s + dreamy piano BGM. "
            "IntakeVideoAgent → StyleTransferAgent (Van Gogh impasto) → VideoExtendAgent "
            "(~20s) → MusicAgent (dreamy piano) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the 6-second lavender-field clip into the workspace.",
            "Restyle the lavender-field footage into a Van Gogh impasto oil-painting aesthetic.",
            "Extend the styled lavender clip to ~20 seconds preserving the impasto look.",
            "Compose a dreamy piano BGM covering the extended length.",
            "Mix the piano BGM with the styled-extended lavender clip's baked audio.",
            "Compose the final clip with the mixed piano BGM overlaid on the styled-extended footage.",
        ],
    },
    {
        "user_goal": "Restyle this 5-second mountain-hike clip as a Hudson-school oil painting, extend to 18 seconds, and add a sweeping orchestral BGM.",
        "rationale": (
            "Mountain-hike + Hudson-school style + extend-to-18s + sweeping orchestral BGM. "
            "IntakeVideoAgent → StyleTransferAgent (Hudson school) → VideoExtendAgent (~18s) "
            "→ MusicAgent (sweeping orchestral) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the 5-second mountain-hike clip into the workspace.",
            "Restyle the mountain-hike footage into a Hudson-school oil-painting aesthetic.",
            "Extend the styled hike clip to ~18 seconds preserving the oil-painting look.",
            "Compose a sweeping orchestral BGM covering the extended length.",
            "Mix the orchestral BGM with the styled-extended hike clip's baked audio.",
            "Compose the final clip with the mixed orchestral BGM overlaid on the styled-extended mountain footage.",
        ],
    },
    {
        "user_goal": "Please restyle this 7-second underwater-reef as neon bioluminescence, extend to 22 seconds, and add an ethereal synth BGM.",
        "rationale": (
            "Underwater reef + neon bioluminescence + extend-to-22s + ethereal synth BGM. "
            "IntakeVideoAgent → StyleTransferAgent (neon bioluminescence) → VideoExtendAgent "
            "(~22s) → MusicAgent (ethereal synth) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the 7-second underwater-reef clip into the workspace.",
            "Restyle the reef footage into a neon-bioluminescence abstract aesthetic.",
            "Extend the styled reef clip to ~22 seconds preserving the bioluminescent look.",
            "Compose an ethereal synth BGM covering the extended length.",
            "Mix the synth BGM with the styled-extended reef clip's baked audio.",
            "Compose the final clip with the mixed synth BGM overlaid on the styled-extended reef footage.",
        ],
    },
    {
        "user_goal": "Apply a charcoal-sketch grayscale style to this 4-second figure-skating clip, extend to 15 seconds, and add a haunting cello BGM.",
        "rationale": (
            "Figure-skating clip + charcoal-sketch style + extend-to-15s + haunting cello BGM. "
            "IntakeVideoAgent → StyleTransferAgent (charcoal sketch) → VideoExtendAgent "
            "(~15s) → MusicAgent (haunting cello) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the 4-second figure-skating clip into the workspace.",
            "Restyle the skating footage into a charcoal-sketch grayscale aesthetic.",
            "Extend the styled skating clip to ~15 seconds preserving the charcoal look.",
            "Compose a haunting cello BGM covering the extended length.",
            "Mix the cello BGM with the styled-extended skating clip's baked audio.",
            "Compose the final clip with the mixed cello BGM overlaid on the styled-extended skating footage.",
        ],
    },
    {
        "user_goal": "Restyle this 5-second pottery-wheel clip as Chinese ink-wash, extend to 18 seconds, and add a gentle guzheng BGM.",
        "rationale": (
            "Pottery-wheel + Chinese ink-wash style + extend-to-18s + gentle guzheng BGM. "
            "IntakeVideoAgent → StyleTransferAgent (Chinese ink-wash) → VideoExtendAgent "
            "(~18s) → MusicAgent (gentle guzheng) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the 5-second pottery-wheel clip into the workspace.",
            "Restyle the pottery-wheel footage into a Chinese ink-wash aesthetic.",
            "Extend the styled pottery clip to ~18 seconds preserving the ink-wash look.",
            "Compose a gentle guzheng BGM covering the extended length.",
            "Mix the guzheng BGM with the styled-extended pottery clip's baked audio.",
            "Compose the final clip with the mixed guzheng BGM overlaid on the styled-extended pottery footage.",
        ],
    },
    {
        "user_goal": "Restyle this 6-second beach-sunset walk as a Monet impressionist painting, extend to 20 seconds, and add a mellow bossa-nova BGM.",
        "rationale": (
            "Beach-sunset walk + Monet impressionist + extend-to-20s + mellow bossa-nova BGM. "
            "IntakeVideoAgent → StyleTransferAgent (Monet) → VideoExtendAgent (~20s) → "
            "MusicAgent (bossa-nova) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the 6-second beach-sunset walk clip into the workspace.",
            "Restyle the sunset footage into a Monet impressionist aesthetic.",
            "Extend the styled sunset clip to ~20 seconds preserving the impressionist look.",
            "Compose a mellow bossa-nova BGM covering the extended length.",
            "Mix the bossa BGM with the styled-extended sunset clip's baked audio.",
            "Compose the final clip with the mixed bossa BGM overlaid on the styled-extended sunset footage.",
        ],
    },
    {
        "user_goal": "Please apply a 1970s disco-funk look to this 5-second rollerskating clip, extend to 15 seconds, and add a funky disco BGM.",
        "rationale": (
            "Rollerskating + 1970s disco-funk style + extend-to-15s + funky disco BGM. "
            "IntakeVideoAgent → StyleTransferAgent (1970s disco-funk) → VideoExtendAgent "
            "(~15s) → MusicAgent (funky disco) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the 5-second rollerskating clip into the workspace.",
            "Restyle the rollerskating footage into a 1970s disco-funk aesthetic.",
            "Extend the styled rollerskating clip to ~15 seconds preserving the disco-funk look.",
            "Compose a funky disco BGM covering the extended length.",
            "Mix the disco BGM with the styled-extended rollerskating clip's baked audio.",
            "Compose the final clip with the mixed disco BGM overlaid on the styled-extended rollerskating footage.",
        ],
    },
    {
        "user_goal": "Restyle this 4-second kung-fu spar clip as wuxia ink-scroll, extend to 12 seconds, and add an epic taiko BGM.",
        "rationale": (
            "Kung-fu spar + wuxia ink-scroll style + extend-to-12s + epic taiko BGM. "
            "IntakeVideoAgent → StyleTransferAgent (wuxia ink-scroll) → VideoExtendAgent "
            "(~12s) → MusicAgent (epic taiko) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the 4-second kung-fu spar clip into the workspace.",
            "Restyle the spar footage into a wuxia ink-scroll aesthetic.",
            "Extend the styled spar clip to ~12 seconds preserving the wuxia look.",
            "Compose an epic taiko BGM covering the extended length.",
            "Mix the taiko BGM with the styled-extended spar clip's baked audio.",
            "Compose the final clip with the mixed taiko BGM overlaid on the styled-extended spar footage.",
        ],
    },
    {
        "user_goal": "Apply a stained-glass cathedral-window look to this 5-second ice-skating clip, extend to 15 seconds, and add a grand organ BGM.",
        "rationale": (
            "Ice-skating + stained-glass style + extend-to-15s + grand organ BGM. "
            "IntakeVideoAgent → StyleTransferAgent (stained-glass) → VideoExtendAgent (~15s) "
            "→ MusicAgent (grand organ) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the 5-second ice-skating clip into the workspace.",
            "Restyle the ice-skating footage into a stained-glass cathedral aesthetic.",
            "Extend the styled skating clip to ~15 seconds preserving the stained-glass look.",
            "Compose a grand organ BGM covering the extended length.",
            "Mix the organ BGM with the styled-extended skating clip's baked audio.",
            "Compose the final clip with the mixed organ BGM overlaid on the styled-extended skating footage.",
        ],
    },
    {
        "user_goal": "Restyle this 6-second city-night drive as Sin City B&W selective-red, extend to 20 seconds, and add a dark film-noir BGM.",
        "rationale": (
            "City-night drive + Sin City style + extend-to-20s + dark film-noir BGM. "
            "IntakeVideoAgent → StyleTransferAgent (Sin City) → VideoExtendAgent (~20s) → "
            "MusicAgent (dark film-noir) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the 6-second city-night drive clip into the workspace.",
            "Restyle the drive footage into a Sin City B&W with selective-red aesthetic.",
            "Extend the styled drive clip to ~20 seconds preserving the Sin City look.",
            "Compose a dark film-noir BGM covering the extended length.",
            "Mix the noir BGM with the styled-extended drive clip's baked audio.",
            "Compose the final clip with the mixed noir BGM overlaid on the styled-extended drive footage.",
        ],
    },
    {
        "user_goal": "Please apply a retro pixel-art arcade style to this 4-second basketball-dunk, extend to 12 seconds, and add a chiptune BGM.",
        "rationale": (
            "Basketball dunk + retro pixel-art arcade style + extend-to-12s + chiptune BGM. "
            "IntakeVideoAgent → StyleTransferAgent (retro pixel-art) → VideoExtendAgent "
            "(~12s) → MusicAgent (chiptune 8-bit) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the 4-second basketball-dunk clip into the workspace.",
            "Restyle the dunk footage into a retro pixel-art arcade aesthetic.",
            "Extend the styled dunk clip to ~12 seconds preserving the arcade look.",
            "Compose a chiptune 8-bit BGM covering the extended length.",
            "Mix the chiptune BGM with the styled-extended dunk clip's baked audio.",
            "Compose the final clip with the mixed chiptune BGM overlaid on the styled-extended dunk footage.",
        ],
    },
    {
        "user_goal": "Restyle this 5-second desert-dune drone shot as a Georgia O'Keeffe minimalist-abstract, extend to 18 seconds, and add a Middle-Eastern oud BGM.",
        "rationale": (
            "Desert-dune drone + O'Keeffe minimalist + extend-to-18s + Middle-Eastern oud BGM. "
            "IntakeVideoAgent → StyleTransferAgent (O'Keeffe minimalist) → VideoExtendAgent "
            "(~18s) → MusicAgent (Middle-Eastern oud) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the 5-second desert-dune drone clip into the workspace.",
            "Restyle the dune footage into a Georgia O'Keeffe minimalist-abstract aesthetic.",
            "Extend the styled dune clip to ~18 seconds preserving the minimalist look.",
            "Compose a Middle-Eastern oud BGM covering the extended length.",
            "Mix the oud BGM with the styled-extended dune clip's baked audio.",
            "Compose the final clip with the mixed oud BGM overlaid on the styled-extended dune footage.",
        ],
    },
    {
        "user_goal": "Apply a 1930s silent-film B&W grain to this 5-second jazz-club performance, extend to 15 seconds, and add a mellow saxophone BGM.",
        "rationale": (
            "Jazz-club performance + 1930s silent-film grain + extend-to-15s + mellow saxophone "
            "BGM. IntakeVideoAgent → StyleTransferAgent (1930s silent-film B&W) → "
            "VideoExtendAgent (~15s) → MusicAgent (mellow saxophone) → AudioMixAgent → "
            "CompositorAgent."
        ),
        "intents": [
            "Ingest the 5-second jazz-club performance clip into the workspace.",
            "Restyle the performance footage into a 1930s B&W silent-film grainy aesthetic.",
            "Extend the styled performance clip to ~15 seconds preserving the silent-film look.",
            "Compose a mellow saxophone BGM covering the extended length.",
            "Mix the sax BGM with the styled-extended performance clip's baked audio.",
            "Compose the final clip with the mixed sax BGM overlaid on the styled-extended jazz footage.",
        ],
    },
    {
        "user_goal": "Restyle this 4-second marathon runner clip as a Japanese woodblock, extend to 12 seconds, and add a Hans-Zimmer cinematic BGM.",
        "rationale": (
            "Marathon runner + Japanese woodblock + extend-to-12s + Hans-Zimmer cinematic BGM. "
            "IntakeVideoAgent → StyleTransferAgent (Japanese woodblock) → VideoExtendAgent "
            "(~12s) → MusicAgent (Hans-Zimmer cinematic) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the 4-second marathon-runner clip into the workspace.",
            "Restyle the runner footage into a Japanese woodblock aesthetic.",
            "Extend the styled runner clip to ~12 seconds preserving the woodblock look.",
            "Compose a Hans-Zimmer cinematic BGM covering the extended length.",
            "Mix the cinematic BGM with the styled-extended runner clip's baked audio.",
            "Compose the final clip with the mixed cinematic BGM overlaid on the styled-extended marathon footage.",
        ],
    },
    {
        "user_goal": "Apply a Corot vintage oil-painting style to this 6-second autumn-park walk, extend to 18 seconds, and add a Celtic-harp folk BGM.",
        "rationale": (
            "Autumn-park walk + Corot oil-painting + extend-to-18s + Celtic-harp folk BGM. "
            "IntakeVideoAgent → StyleTransferAgent (Corot oil) → VideoExtendAgent (~18s) → "
            "MusicAgent (Celtic harp folk) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the 6-second autumn-park walk clip into the workspace.",
            "Restyle the walk footage into a Corot vintage oil-painting aesthetic.",
            "Extend the styled walk clip to ~18 seconds preserving the Corot look.",
            "Compose a Celtic-harp folk BGM covering the extended length.",
            "Mix the harp BGM with the styled-extended walk clip's ambient audio.",
            "Compose the final clip with the mixed harp BGM overlaid on the styled-extended autumn-park footage.",
        ],
    },
    {
        "user_goal": "Restyle this 5-second cherry-blossom clip as sumi-e ink-painting, extend to 15 seconds, and add a gentle shakuhachi BGM.",
        "rationale": (
            "Cherry-blossom + sumi-e style + extend-to-15s + gentle shakuhachi BGM. "
            "IntakeVideoAgent → StyleTransferAgent (sumi-e) → VideoExtendAgent (~15s) → "
            "MusicAgent (gentle shakuhachi) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the 5-second cherry-blossom clip into the workspace.",
            "Restyle the cherry-blossom footage into a sumi-e ink-painting aesthetic.",
            "Extend the styled cherry clip to ~15 seconds preserving the sumi-e look.",
            "Compose a gentle shakuhachi BGM covering the extended length.",
            "Mix the shakuhachi BGM with the styled-extended cherry clip's ambient audio.",
            "Compose the final clip with the mixed shakuhachi BGM overlaid on the styled-extended cherry-blossom footage.",
        ],
    },
    {
        "user_goal": "Apply a Moebius comic-book style to this 4-second parkour clip, extend to 12 seconds, and add a drum-and-bass BGM.",
        "rationale": (
            "Parkour + Moebius comic-book style + extend-to-12s + drum-and-bass BGM. "
            "IntakeVideoAgent → StyleTransferAgent (Moebius comic) → VideoExtendAgent (~12s) "
            "→ MusicAgent (drum and bass) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the 4-second parkour clip into the workspace.",
            "Restyle the parkour footage into a Moebius comic-book aesthetic.",
            "Extend the styled parkour clip to ~12 seconds preserving the comic-book look.",
            "Compose a drum-and-bass BGM covering the extended length.",
            "Mix the drum-and-bass BGM with the styled-extended parkour clip's baked audio.",
            "Compose the final clip with the mixed drum-and-bass BGM overlaid on the styled-extended parkour footage.",
        ],
    },
]
