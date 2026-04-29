"""Shape: style_music — IntakeVideo → StyleTransfer → Music → AudioMix → Compositor.

User uploaded video, wants it restyled AND BGM added.

Reject: AmbienceAgent (music only), Transcription / Translation
(no subtitle), VideoExtendAgent (no extend), VideoAnalysisAgent /
HighlightAgent (no trim).
"""
from __future__ import annotations

SAMPLES: list[dict] = [
    {
        "user_goal": "Please restyle this skate clip as a Japanese ukiyo-e woodblock and add a traditional koto-and-shakuhachi BGM.",
        "rationale": (
            "User uploaded a skate clip, asks for ukiyo-e visual restyle AND traditional "
            "koto-shakuhachi BGM. IntakeVideoAgent ingests. StyleTransferAgent applies the "
            "ukiyo-e rendition. MusicAgent composes the koto-and-shakuhachi cue. AudioMixAgent "
            "mixes BGM with the styled clip's audio. CompositorAgent muxes the mixed audio "
            "onto the styled video. Reject AmbienceAgent (music only), Transcription / "
            "Translation (no subtitle), VideoExtendAgent (no length change), "
            "VideoAnalysisAgent / HighlightAgent (no trim)."
        ),
        "intents": [
            "Ingest the skate clip into the workspace as the source video.",
            "Restyle the skate footage into a Japanese ukiyo-e woodblock aesthetic.",
            "Compose a traditional koto-and-shakuhachi BGM cue fitting the ukiyo-e atmosphere.",
            "Mix the koto-shakuhachi BGM with the styled skate clip's baked audio.",
            "Compose the styled skate clip with the mixed BGM overlaid on the ukiyo-e frames.",
        ],
    },
    {
        "user_goal": "Restyle this forest-walk vlog as a Ghibli watercolor and add a gentle folk-acoustic BGM.",
        "rationale": (
            "Forest-walk vlog + Ghibli watercolor style + gentle folk-acoustic BGM. "
            "IntakeVideoAgent → StyleTransferAgent (Ghibli) → MusicAgent (folk acoustic) → "
            "AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the forest-walk vlog into the workspace.",
            "Restyle the forest-walk footage into a Studio Ghibli watercolor aesthetic.",
            "Compose a gentle folk-acoustic BGM fitting the Ghibli atmosphere.",
            "Mix the folk BGM with the styled vlog's baked audio.",
            "Compose the styled vlog with the mixed folk BGM overlaid on the watercolor frames.",
        ],
    },
    {
        "user_goal": "Please apply a neon cyberpunk Blade Runner style to this city-night drive and add a synthwave BGM.",
        "rationale": (
            "City-night drive + Blade Runner neon cyberpunk style + synthwave BGM. "
            "IntakeVideoAgent → StyleTransferAgent (Blade Runner cyberpunk) → MusicAgent "
            "(synthwave) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the city-night drive clip into the workspace.",
            "Restyle the drive footage into a Blade Runner neon-cyberpunk aesthetic.",
            "Compose a synthwave BGM fitting the cyberpunk atmosphere.",
            "Mix the synthwave BGM with the styled drive clip's baked audio.",
            "Compose the styled clip with the mixed synthwave BGM overlaid on the cyberpunk frames.",
        ],
    },
    {
        "user_goal": "Restyle this beachfront-sunset as a Monet impressionist painting and add a mellow bossa-nova BGM.",
        "rationale": (
            "Beachfront sunset + Monet impressionist style + mellow bossa-nova BGM. "
            "IntakeVideoAgent → StyleTransferAgent (Monet) → MusicAgent (bossa-nova) → "
            "AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the beachfront-sunset clip into the workspace.",
            "Restyle the sunset footage into a Monet impressionist painting aesthetic.",
            "Compose a mellow bossa-nova BGM fitting the sunset mood.",
            "Mix the bossa BGM with the styled clip's baked audio.",
            "Compose the styled clip with the mixed bossa BGM overlaid on the Monet frames.",
        ],
    },
    {
        "user_goal": "Please apply a Van Gogh impasto style to this lavender-field clip and add a dreamy ambient-piano BGM.",
        "rationale": (
            "Lavender-field clip + Van Gogh impasto style + dreamy ambient-piano BGM (music "
            "genre). IntakeVideoAgent → StyleTransferAgent (Van Gogh impasto) → MusicAgent "
            "(ambient piano) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the lavender-field clip into the workspace.",
            "Restyle the lavender footage into a Van Gogh impasto oil-painting aesthetic.",
            "Compose a dreamy ambient-piano BGM fitting the Van Gogh dreamscape.",
            "Mix the ambient BGM with the styled clip's ambient audio.",
            "Compose the styled clip with the mixed piano BGM overlaid on the impasto frames.",
        ],
    },
    {
        "user_goal": "Restyle this mountain-hike vlog as a Thomas Cole Hudson-school oil painting and add a sweeping orchestral BGM.",
        "rationale": (
            "Mountain-hike vlog + Hudson-school oil style + sweeping orchestral BGM. "
            "IntakeVideoAgent → StyleTransferAgent (Hudson school) → MusicAgent (sweeping "
            "orchestral) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the mountain-hike vlog into the workspace.",
            "Restyle the hike footage into a Thomas Cole Hudson-school oil-painting aesthetic.",
            "Compose a sweeping orchestral BGM fitting the Hudson-school grandeur.",
            "Mix the orchestral BGM with the styled hike's baked audio.",
            "Compose the styled vlog with the mixed orchestral BGM overlaid on the oil-painting frames.",
        ],
    },
    {
        "user_goal": "Please apply a 1970s-disco-funk look to this rollerskating clip and add funky disco BGM.",
        "rationale": (
            "Rollerskating clip + 1970s-disco-funk visual style + funky disco BGM. "
            "IntakeVideoAgent → StyleTransferAgent (1970s disco-funk) → MusicAgent (funky "
            "disco) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the rollerskating clip into the workspace.",
            "Restyle the rollerskating footage into a 1970s-disco-funk visual aesthetic.",
            "Compose a funky 1970s-disco BGM fitting the disco-funk atmosphere.",
            "Mix the disco BGM with the styled rollerskating clip's baked audio.",
            "Compose the styled clip with the mixed disco BGM overlaid on the disco-funk frames.",
        ],
    },
    {
        "user_goal": "Restyle this cherry-blossom clip as a sumi-e ink-painting and add a gentle shakuhachi BGM.",
        "rationale": (
            "Cherry-blossom clip + sumi-e ink-painting style + gentle shakuhachi BGM. "
            "IntakeVideoAgent → StyleTransferAgent (sumi-e) → MusicAgent (gentle shakuhachi) "
            "→ AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the cherry-blossom clip into the workspace.",
            "Restyle the cherry-blossom footage into a Japanese sumi-e ink-painting aesthetic.",
            "Compose a gentle shakuhachi BGM fitting the sumi-e atmosphere.",
            "Mix the shakuhachi BGM with the styled clip's ambient audio.",
            "Compose the styled clip with the mixed shakuhachi BGM overlaid on the sumi-e frames.",
        ],
    },
    {
        "user_goal": "Please apply a Pixar 3D-cartoon style to this kids-playground clip and add cheerful Disney-style orchestral BGM.",
        "rationale": (
            "Kids-playground clip + Pixar 3D-cartoon style + cheerful Disney-style orchestral "
            "BGM. IntakeVideoAgent → StyleTransferAgent (Pixar 3D) → MusicAgent (Disney "
            "orchestral) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the kids-playground clip into the workspace.",
            "Restyle the playground footage into a Pixar 3D-cartoon aesthetic.",
            "Compose a cheerful Disney-style orchestral BGM fitting the Pixar mood.",
            "Mix the Disney BGM with the styled clip's baked audio.",
            "Compose the styled clip with the mixed Disney BGM overlaid on the Pixar frames.",
        ],
    },
    {
        "user_goal": "Restyle this drone-canyon flyover as a Dali surrealist dreamscape and add an ethereal ambient-electronica BGM.",
        "rationale": (
            "Drone-canyon flyover + Dali surrealist style + ethereal ambient-electronica BGM "
            "(music genre). IntakeVideoAgent → StyleTransferAgent (Dali surrealist) → "
            "MusicAgent (ambient electronica) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the drone-canyon flyover clip into the workspace.",
            "Restyle the flyover footage into a Dali-style surrealist dreamscape aesthetic.",
            "Compose an ethereal ambient-electronica BGM fitting the surrealist atmosphere.",
            "Mix the ambient BGM with the styled flyover's baked audio.",
            "Compose the styled clip with the mixed ambient BGM overlaid on the surrealist frames.",
        ],
    },
    {
        "user_goal": "Please apply a Warhol pop-art screen-print style to this runway walk and add an upbeat 1980s-synth-pop BGM.",
        "rationale": (
            "Runway walk + Warhol pop-art style + upbeat 1980s-synth-pop BGM. "
            "IntakeVideoAgent → StyleTransferAgent (Warhol pop-art) → MusicAgent (1980s "
            "synth-pop) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the runway walk clip into the workspace.",
            "Restyle the runway footage into a Warhol pop-art screen-print aesthetic.",
            "Compose an upbeat 1980s-synth-pop BGM fitting the pop-art mood.",
            "Mix the synth-pop BGM with the styled runway clip's baked audio.",
            "Compose the styled clip with the mixed synth-pop BGM overlaid on the Warhol frames.",
        ],
    },
    {
        "user_goal": "Restyle this yoga session as an anime slice-of-life pastel and add a meditative spa-piano BGM.",
        "rationale": (
            "Yoga session + anime slice-of-life pastel style + meditative spa-piano BGM. "
            "IntakeVideoAgent → StyleTransferAgent (anime pastel slice-of-life) → MusicAgent "
            "(meditative spa piano) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the yoga-session clip into the workspace.",
            "Restyle the yoga footage into a pastel anime slice-of-life aesthetic.",
            "Compose a meditative spa-piano BGM fitting the yoga's calm pacing.",
            "Mix the spa BGM with the styled yoga clip's ambient audio.",
            "Compose the styled clip with the mixed piano BGM overlaid on the pastel-anime frames.",
        ],
    },
    {
        "user_goal": "Please apply a stained-glass cathedral-window look to this ice-skating clip and add a grand pipe-organ BGM.",
        "rationale": (
            "Ice-skating clip + stained-glass style + grand pipe-organ BGM. IntakeVideoAgent "
            "→ StyleTransferAgent (stained-glass) → MusicAgent (grand pipe organ) → "
            "AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the ice-skating clip into the workspace.",
            "Restyle the skating footage into a stained-glass cathedral-window aesthetic.",
            "Compose a grand pipe-organ BGM fitting the stained-glass majesty.",
            "Mix the organ BGM with the styled skating clip's baked audio.",
            "Compose the styled clip with the mixed organ BGM overlaid on the stained-glass frames.",
        ],
    },
    {
        "user_goal": "Restyle this pottery-wheel clip as a Chinese ink-wash painting and add a gentle guzheng BGM.",
        "rationale": (
            "Pottery-wheel + Chinese ink-wash style + gentle guzheng BGM. IntakeVideoAgent → "
            "StyleTransferAgent (Chinese ink-wash) → MusicAgent (gentle guzheng) → "
            "AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the pottery-wheel clip into the workspace.",
            "Restyle the pottery-wheel footage into a Chinese ink-wash painting aesthetic.",
            "Compose a gentle guzheng BGM fitting the ink-wash atmosphere.",
            "Mix the guzheng BGM with the styled pottery clip's baked audio.",
            "Compose the styled clip with the mixed guzheng BGM overlaid on the ink-wash frames.",
        ],
    },
    {
        "user_goal": "Please apply a charcoal-sketch grayscale style to this figure-skating performance and add a haunting cello-solo BGM.",
        "rationale": (
            "Figure-skating performance + charcoal-sketch grayscale style + haunting cello-solo "
            "BGM. IntakeVideoAgent → StyleTransferAgent (charcoal sketch) → MusicAgent "
            "(haunting cello) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the figure-skating performance clip into the workspace.",
            "Restyle the performance footage into a charcoal-sketch grayscale aesthetic.",
            "Compose a haunting cello-solo BGM fitting the charcoal atmosphere.",
            "Mix the cello BGM with the styled skating clip's baked audio.",
            "Compose the styled clip with the mixed cello BGM overlaid on the charcoal frames.",
        ],
    },
    {
        "user_goal": "Restyle this underwater reef clip as a neon bioluminescence abstract and add an ethereal synth BGM.",
        "rationale": (
            "Underwater reef + neon bioluminescence abstract style + ethereal synth BGM. "
            "IntakeVideoAgent → StyleTransferAgent (neon bioluminescence) → MusicAgent "
            "(ethereal synth) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the underwater reef clip into the workspace.",
            "Restyle the reef footage into a neon-bioluminescence abstract aesthetic.",
            "Compose an ethereal synth BGM fitting the neon underwater mood.",
            "Mix the synth BGM with the styled reef clip's baked audio.",
            "Compose the styled clip with the mixed synth BGM overlaid on the neon-reef frames.",
        ],
    },
    {
        "user_goal": "Please apply a Matisse cutout-collage style to this fashion-show runway and add a mellow jazz-piano BGM.",
        "rationale": (
            "Fashion-show runway + Matisse cutout-collage style + mellow jazz-piano BGM. "
            "IntakeVideoAgent → StyleTransferAgent (Matisse cutout) → MusicAgent (mellow "
            "jazz piano) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the fashion-show runway clip into the workspace.",
            "Restyle the runway footage into a Matisse cutout-collage aesthetic.",
            "Compose a mellow jazz-piano BGM fitting the fashion runway vibe.",
            "Mix the jazz BGM with the styled runway clip's baked audio.",
            "Compose the styled clip with the mixed jazz BGM overlaid on the Matisse frames.",
        ],
    },
    {
        "user_goal": "Restyle this kung-fu sparring clip as a wuxia ink-scroll and add an epic taiko-drum BGM.",
        "rationale": (
            "Kung-fu sparring + wuxia ink-scroll style + epic taiko-drum BGM. "
            "IntakeVideoAgent → StyleTransferAgent (wuxia ink-scroll) → MusicAgent (epic "
            "taiko) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the kung-fu sparring clip into the workspace.",
            "Restyle the sparring footage into a wuxia ink-scroll aesthetic.",
            "Compose an epic taiko-drum BGM fitting the wuxia intensity.",
            "Mix the taiko BGM with the styled sparring clip's baked audio.",
            "Compose the styled clip with the mixed taiko BGM overlaid on the wuxia frames.",
        ],
    },
    {
        "user_goal": "Please apply a 1930s B&W silent-film grainy look to this jazz-club performance and add a mellow solo-saxophone BGM.",
        "rationale": (
            "Jazz-club performance + 1930s B&W silent-film grainy style + mellow solo-sax BGM. "
            "IntakeVideoAgent → StyleTransferAgent (1930s silent-film B&W) → MusicAgent "
            "(mellow saxophone) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the jazz-club performance clip into the workspace.",
            "Restyle the performance footage into a 1930s B&W silent-film grainy aesthetic.",
            "Compose a mellow solo-saxophone BGM fitting the jazz-club period mood.",
            "Mix the sax BGM with the styled jazz clip's baked audio.",
            "Compose the styled clip with the mixed sax BGM overlaid on the 1930s frames.",
        ],
    },
    {
        "user_goal": "Restyle this marathon-running clip as a Japanese woodblock print and add an epic Hans-Zimmer-style cinematic BGM.",
        "rationale": (
            "Marathon-running + Japanese woodblock style + Hans-Zimmer epic BGM. "
            "IntakeVideoAgent → StyleTransferAgent (Japanese woodblock) → MusicAgent (Hans "
            "Zimmer cinematic) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the marathon-running clip into the workspace.",
            "Restyle the marathon footage into a Japanese woodblock-print aesthetic.",
            "Compose a Hans-Zimmer-style epic cinematic BGM fitting the marathon's scale.",
            "Mix the cinematic BGM with the styled marathon clip's baked audio.",
            "Compose the styled clip with the mixed cinematic BGM overlaid on the woodblock frames.",
        ],
    },
    {
        "user_goal": "Please apply a Corot-style vintage oil-painting to this autumn-park walk and add a Celtic-harp folk BGM.",
        "rationale": (
            "Autumn-park walk + Corot vintage oil-painting style + Celtic-harp folk BGM. "
            "IntakeVideoAgent → StyleTransferAgent (Corot oil) → MusicAgent (Celtic harp) → "
            "AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the autumn-park walk clip into the workspace.",
            "Restyle the walk footage into a Corot-style vintage oil-painting aesthetic.",
            "Compose a Celtic-harp folk BGM fitting the pastoral oil-painting mood.",
            "Mix the harp BGM with the styled walk clip's ambient audio.",
            "Compose the styled clip with the mixed harp BGM overlaid on the Corot frames.",
        ],
    },
    {
        "user_goal": "Restyle this surfing clip as a classic Hawaiian-shirt tropical-print and add a cheerful ukulele BGM.",
        "rationale": (
            "Surfing clip + Hawaiian-shirt tropical-print style + cheerful ukulele BGM. "
            "IntakeVideoAgent → StyleTransferAgent (Hawaiian tropical-print) → MusicAgent "
            "(cheerful ukulele) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the surfing clip into the workspace.",
            "Restyle the surf footage into a classic Hawaiian-shirt tropical-print aesthetic.",
            "Compose a cheerful ukulele BGM fitting the tropical-surf vibe.",
            "Mix the ukulele BGM with the styled surf clip's baked audio.",
            "Compose the styled clip with the mixed ukulele BGM overlaid on the tropical frames.",
        ],
    },
    {
        "user_goal": "Please apply a Hokusai woodblock look to this rooftop dawn-yoga clip and add a gentle koto BGM.",
        "rationale": (
            "Rooftop dawn-yoga + Hokusai woodblock style + gentle koto BGM. IntakeVideoAgent "
            "→ StyleTransferAgent (Hokusai woodblock) → MusicAgent (gentle koto) → "
            "AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the rooftop dawn-yoga clip into the workspace.",
            "Restyle the dawn-yoga footage into a Hokusai-style woodblock aesthetic.",
            "Compose a gentle koto BGM fitting the Hokusai dawn mood.",
            "Mix the koto BGM with the styled yoga clip's ambient audio.",
            "Compose the styled clip with the mixed koto BGM overlaid on the Hokusai frames.",
        ],
    },
    {
        "user_goal": "Restyle this city-night drive as Sin City B&W-with-selective-red and add a dark film-noir BGM.",
        "rationale": (
            "City-night drive + Sin City B&W selective-red style + dark film-noir BGM. "
            "IntakeVideoAgent → StyleTransferAgent (Sin City) → MusicAgent (dark film-noir) "
            "→ AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the city-night drive clip into the workspace.",
            "Restyle the drive footage into a Sin City B&W with selective-red aesthetic.",
            "Compose a dark film-noir BGM fitting the Sin City atmosphere.",
            "Mix the noir BGM with the styled drive clip's baked audio.",
            "Compose the styled clip with the mixed noir BGM overlaid on the Sin City frames.",
        ],
    },
    {
        "user_goal": "Please apply a retro pixel-art arcade style to this basketball-dunk clip and add a chiptune 8-bit BGM.",
        "rationale": (
            "Basketball-dunk + retro pixel-art arcade style + chiptune 8-bit BGM. "
            "IntakeVideoAgent → StyleTransferAgent (retro pixel-art) → MusicAgent (chiptune "
            "8-bit) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the basketball-dunk clip into the workspace.",
            "Restyle the dunk footage into a retro pixel-art arcade aesthetic.",
            "Compose a chiptune 8-bit BGM fitting the arcade mood.",
            "Mix the chiptune BGM with the styled dunk clip's baked audio.",
            "Compose the styled clip with the mixed chiptune BGM overlaid on the pixel-art frames.",
        ],
    },
    {
        "user_goal": "Restyle this kitchen-prep clip as a 1920s silent-film B&W with grain and add a ragtime-piano BGM.",
        "rationale": (
            "Kitchen-prep clip + 1920s silent-film B&W style + ragtime-piano BGM. "
            "IntakeVideoAgent → StyleTransferAgent (1920s silent-film B&W) → MusicAgent "
            "(ragtime piano) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the kitchen-prep clip into the workspace.",
            "Restyle the kitchen-prep footage into a 1920s silent-film B&W grainy aesthetic.",
            "Compose a ragtime-piano BGM fitting the silent-film period mood.",
            "Mix the ragtime BGM with the styled kitchen clip's baked audio.",
            "Compose the styled clip with the mixed ragtime BGM overlaid on the silent-film frames.",
        ],
    },
    {
        "user_goal": "Please apply a Moebius comic-book ink-outline style to this parkour clip and add an energetic electronic drum-and-bass BGM.",
        "rationale": (
            "Parkour clip + Moebius comic-book style + energetic drum-and-bass BGM. "
            "IntakeVideoAgent → StyleTransferAgent (Moebius comic) → MusicAgent (drum and "
            "bass) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the parkour clip into the workspace.",
            "Restyle the parkour footage into a Moebius comic-book ink-outline aesthetic.",
            "Compose an energetic drum-and-bass BGM fitting the parkour intensity.",
            "Mix the drum-and-bass BGM with the styled parkour clip's baked audio.",
            "Compose the styled clip with the mixed drum-and-bass BGM overlaid on the comic frames.",
        ],
    },
    {
        "user_goal": "Restyle this desert-dunes drone flyover as a Georgia O'Keeffe minimalist-abstract and add a Middle-Eastern oud-and-ney BGM.",
        "rationale": (
            "Desert-dunes flyover + O'Keeffe minimalist-abstract style + Middle-Eastern "
            "oud-and-ney BGM. IntakeVideoAgent → StyleTransferAgent (O'Keeffe minimalist) → "
            "MusicAgent (Middle-Eastern oud-and-ney) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the desert-dunes drone flyover into the workspace.",
            "Restyle the flyover footage into a Georgia O'Keeffe minimalist-abstract aesthetic.",
            "Compose a Middle-Eastern oud-and-ney BGM fitting the desert vibe.",
            "Mix the Middle-Eastern BGM with the styled flyover's baked audio.",
            "Compose the styled clip with the mixed BGM overlaid on the minimalist frames.",
        ],
    },
    {
        "user_goal": "Please apply a 1990s-VHS skate-video grain to this street-skate clip and add a punk-rock BGM.",
        "rationale": (
            "Street-skate clip + 1990s-VHS grain style + punk-rock BGM. IntakeVideoAgent → "
            "StyleTransferAgent (1990s VHS skate) → MusicAgent (punk rock) → AudioMixAgent → "
            "CompositorAgent."
        ),
        "intents": [
            "Ingest the street-skate clip into the workspace.",
            "Restyle the skate footage into a 1990s-VHS skate-video grainy aesthetic.",
            "Compose a punk-rock BGM fitting the VHS-era skate mood.",
            "Mix the punk BGM with the styled skate clip's baked audio.",
            "Compose the styled clip with the mixed punk BGM overlaid on the VHS frames.",
        ],
    },
    {
        "user_goal": "Restyle this tea-ceremony performance as a traditional Chinese ink-wash and add a melodic erhu BGM.",
        "rationale": (
            "Tea-ceremony + Chinese ink-wash style + melodic erhu BGM. IntakeVideoAgent → "
            "StyleTransferAgent (Chinese ink-wash) → MusicAgent (melodic erhu) → "
            "AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the tea-ceremony performance clip into the workspace.",
            "Restyle the ceremony footage into a traditional Chinese ink-wash aesthetic.",
            "Compose a melodic erhu BGM fitting the ink-wash ceremonial mood.",
            "Mix the erhu BGM with the styled ceremony clip's baked audio.",
            "Compose the styled clip with the mixed erhu BGM overlaid on the ink-wash frames.",
        ],
    },
]
