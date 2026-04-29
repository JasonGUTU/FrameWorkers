"""Shape: style_only — IntakeVideo → StyleTransfer (raw style output).

User uploaded a video and asks ONLY for a style-transferred version — no
audio overlay, no subtitle, no compositor pass.  Raw StyleTransferAgent
output is the deliverable.

Reject biases:
  - CompositorAgent (nothing to compose on top of raw style output)
  - MusicAgent / AmbienceAgent / AudioMixAgent (no audio overlay)
  - TranscriptionAgent / TranslationAgent (no subtitle ask)
  - VideoExtendAgent (no length change)
  - VideoAnalysisAgent / HighlightAgent (no analysis / trim ask)
"""
from __future__ import annotations

SAMPLES: list[dict] = [
    {
        "user_goal": "Please turn this phone video of my morning walk into a Studio Ghibli watercolor look.",
        "rationale": (
            "User uploaded a walk clip and asks only for a Ghibli-watercolor stylistic transfer — "
            "no audio, subtitle, length, or composition change. IntakeVideoAgent ingests the clip. "
            "StyleTransferAgent produces the Ghibli-watercolor rendition. Raw styled clip is the "
            "deliverable. Reject CompositorAgent (nothing to overlay on the styled output), "
            "MusicAgent / AmbienceAgent / AudioMixAgent (no audio overlay), TranscriptionAgent / "
            "TranslationAgent (no subtitles), VideoExtendAgent (no length change), "
            "VideoAnalysisAgent / HighlightAgent (no trimming)."
        ),
        "intents": [
            "Ingest the morning-walk phone video into the workspace as the source clip.",
            "Transform the morning-walk footage into a Studio Ghibli watercolor-style rendition.",
        ],
    },
    {
        "user_goal": "Transform this vacation clip into a Wes Anderson-style pastel symmetrical look.",
        "rationale": (
            "Vacation clip + Wes-Anderson pastel symmetrical style transfer, nothing else. "
            "IntakeVideoAgent ingests the clip; StyleTransferAgent applies the signature pastel "
            "palette and centered framing treatment. Raw styled clip is delivered. No audio, "
            "subtitle, compositor, length, or trimming changes requested."
        ),
        "intents": [
            "Ingest the vacation clip into the workspace as the source video.",
            "Restyle the vacation footage into a Wes Anderson pastel symmetrical aesthetic.",
        ],
    },
    {
        "user_goal": "Please turn this home-cooking video into a pencil-sketch black-and-white sketch animation look.",
        "rationale": (
            "Home-cooking video + pencil-sketch monochrome style transfer. IntakeVideoAgent "
            "ingests the clip. StyleTransferAgent produces a hand-drawn pencil-sketch rendition "
            "in black and white. Output is the raw styled clip only — no compositor, audio, or "
            "subtitle operations."
        ),
        "intents": [
            "Ingest the home-cooking video into the workspace.",
            "Transform the cooking footage into a pencil-sketch black-and-white animation style.",
        ],
    },
    {
        "user_goal": "Apply an oil-painting style to this portrait video of my grandmother — make it look like a Van Gogh portrait in motion.",
        "rationale": (
            "Portrait video + Van Gogh oil-painting style transfer. IntakeVideoAgent loads the "
            "portrait clip. StyleTransferAgent applies Van Gogh brushstroke dynamics across all "
            "frames while preserving facial identity. Raw styled clip is the deliverable. No "
            "overlay, subtitle, or length changes."
        ),
        "intents": [
            "Ingest the portrait video of the grandmother into the workspace.",
            "Apply a Van Gogh oil-painting brushstroke style to the portrait footage.",
        ],
    },
    {
        "user_goal": "Convert this dance performance into a neon cyberpunk visual with glowing edges and synthwave color grading.",
        "rationale": (
            "Dance performance clip + neon cyberpunk style transfer. IntakeVideoAgent ingests "
            "the dance clip. StyleTransferAgent re-renders it with neon edge highlights, "
            "synthwave color grade, and cyberpunk urban glow. Raw styled output is the final "
            "deliverable — no overlays, audio swap, or trimming requested."
        ),
        "intents": [
            "Ingest the dance-performance clip into the workspace.",
            "Transform the dance footage into a neon cyberpunk visual with glowing edges and synthwave grading.",
        ],
    },
    {
        "user_goal": "Please style this skate video as if it were Japanese ukiyo-e woodblock prints.",
        "rationale": (
            "Skate video + ukiyo-e woodblock style transfer. IntakeVideoAgent ingests the clip; "
            "StyleTransferAgent applies the ukiyo-e flat-color woodblock aesthetic frame-by-frame. "
            "Raw styled clip is delivered as-is — no compositor, audio, subtitle, length, or "
            "trimming operations."
        ),
        "intents": [
            "Ingest the skate video into the workspace.",
            "Restyle the skate footage into a Japanese ukiyo-e woodblock-print aesthetic.",
        ],
    },
    {
        "user_goal": "Turn this kitchen-prep clip into a 1920s silent-film black-and-white look with film-grain texture.",
        "rationale": (
            "Kitchen-prep clip + 1920s silent-film monochrome restyle with grain. "
            "IntakeVideoAgent loads the clip. StyleTransferAgent applies the monochrome "
            "grain-heavy silent-film rendition. Raw styled clip is the output — no subtitle "
            "cards or music added (user didn't ask for those)."
        ),
        "intents": [
            "Ingest the kitchen-prep clip into the workspace.",
            "Apply a 1920s silent-film black-and-white grainy style to the kitchen-prep footage.",
        ],
    },
    {
        "user_goal": "Please convert this nature documentary B-roll into a children's-book watercolor illustration style.",
        "rationale": (
            "Nature B-roll + children's-book watercolor style transfer. IntakeVideoAgent "
            "ingests the B-roll. StyleTransferAgent produces the watercolor-illustration "
            "rendition. Raw styled clip is the final asset. No narration, music, or compositor "
            "overlay was requested, so those agents stay out."
        ),
        "intents": [
            "Ingest the nature-documentary B-roll into the workspace.",
            "Restyle the nature B-roll as a children's-book watercolor illustration.",
        ],
    },
    {
        "user_goal": "Make this city-street footage look like a Moebius comic-book illustration — bold ink outlines, flat colors.",
        "rationale": (
            "City-street footage + Moebius comic-book restyle. IntakeVideoAgent ingests the "
            "clip. StyleTransferAgent applies bold ink outlines and flat colors per frame. Raw "
            "styled clip is delivered. No audio, subtitle, or other modifications."
        ),
        "intents": [
            "Ingest the city-street footage into the workspace.",
            "Transform the city-street footage into a Moebius comic-book ink-outline flat-color style.",
        ],
    },
    {
        "user_goal": "Apply an impressionist Monet-style look to this garden-tour video.",
        "rationale": (
            "Garden-tour video + Monet impressionist style transfer. IntakeVideoAgent ingests "
            "the clip; StyleTransferAgent re-renders the footage in a Monet-style soft-brush "
            "impressionist palette. Raw styled clip is delivered. No overlays or audio changes."
        ),
        "intents": [
            "Ingest the garden-tour video into the workspace.",
            "Apply a Monet impressionist-style visual transformation to the garden-tour footage.",
        ],
    },
    {
        "user_goal": "Please turn this wedding-dance clip into a vintage Super-8 home-movie look with faded color and light leaks.",
        "rationale": (
            "Wedding-dance + vintage Super-8 home-movie restyle with faded color and light "
            "leaks. IntakeVideoAgent ingests the clip. StyleTransferAgent applies the Super-8 "
            "grain, faded grade, and light-leak artifacts. Raw styled clip is the deliverable."
        ),
        "intents": [
            "Ingest the wedding-dance clip into the workspace.",
            "Restyle the wedding-dance footage into a vintage Super-8 home-movie aesthetic with light leaks.",
        ],
    },
    {
        "user_goal": "Convert this pet-playing clip to a Pixar-style 3D cartoon look.",
        "rationale": (
            "Pet-playing clip + Pixar-style 3D-cartoon restyle. IntakeVideoAgent ingests the "
            "clip; StyleTransferAgent produces the Pixar-look rendition preserving the pet's "
            "behaviour. Raw styled clip is the output. No compositor, audio, or subtitle pass."
        ),
        "intents": [
            "Ingest the pet-playing clip into the workspace.",
            "Transform the pet-playing footage into a Pixar-style 3D cartoon rendition.",
        ],
    },
    {
        "user_goal": "Make this city-night video look like a classic film-noir shot — high-contrast black-and-white, deep shadows, chiaroscuro.",
        "rationale": (
            "City-night footage + film-noir high-contrast monochrome restyle. IntakeVideoAgent "
            "ingests the clip. StyleTransferAgent applies high-contrast B&W grading with deep "
            "chiaroscuro shadows. Raw styled clip is delivered."
        ),
        "intents": [
            "Ingest the city-night video into the workspace.",
            "Restyle the city-night footage into a film-noir high-contrast chiaroscuro aesthetic.",
        ],
    },
    {
        "user_goal": "Apply a Matisse cutout-collage look to this fashion-show runway clip — flat bold colors.",
        "rationale": (
            "Fashion-show runway + Matisse cutout-collage restyle. IntakeVideoAgent ingests the "
            "clip. StyleTransferAgent produces the cutout-collage rendition with flat bold "
            "color panels preserving silhouette motion. Raw styled output delivered."
        ),
        "intents": [
            "Ingest the fashion-show runway clip into the workspace.",
            "Apply a Matisse cutout-collage style with flat bold colors to the runway footage.",
        ],
    },
    {
        "user_goal": "Turn this drone flight through a canyon into a Dali surrealist dreamscape.",
        "rationale": (
            "Drone canyon flight + Dali surrealist restyle. IntakeVideoAgent ingests the drone "
            "clip. StyleTransferAgent re-renders the canyon with Dali-style surrealist distortions, "
            "melting geometries, and the painter's signature palette. Raw styled clip delivered."
        ),
        "intents": [
            "Ingest the drone canyon-flight clip into the workspace.",
            "Restyle the drone canyon footage into a Dali-style surrealist dreamscape rendition.",
        ],
    },
    {
        "user_goal": "Please give this soccer match highlight reel an anime-action shonen look.",
        "rationale": (
            "Soccer highlight reel + anime-shonen action restyle. IntakeVideoAgent ingests the "
            "reel. StyleTransferAgent re-renders the match in anime-action aesthetic with "
            "shonen visual cues. Raw styled clip is the deliverable — no new music or subtitles, "
            "the existing highlight cuts stay as-is."
        ),
        "intents": [
            "Ingest the soccer-match highlight reel into the workspace.",
            "Transform the highlight reel into an anime-action shonen visual style.",
        ],
    },
    {
        "user_goal": "Make this autumn-park walk into a vintage oil-painting look — Corot-style landscape.",
        "rationale": (
            "Autumn-park walk + Corot-style vintage oil-painting restyle. IntakeVideoAgent "
            "ingests the clip. StyleTransferAgent produces the Corot-landscape rendition with "
            "soft brush texture and period tonal palette. Raw styled clip is the output."
        ),
        "intents": [
            "Ingest the autumn-park walk clip into the workspace.",
            "Apply a Corot-style vintage oil-painting landscape look to the park-walk footage.",
        ],
    },
    {
        "user_goal": "Turn this winter village drone shot into a storybook-illustration look — warm lighting and cozy palette.",
        "rationale": (
            "Winter village drone footage + storybook-illustration restyle with warm cozy "
            "palette. IntakeVideoAgent ingests the clip; StyleTransferAgent applies the "
            "storybook watercolor treatment and warm-toned palette. Raw styled output is "
            "delivered."
        ),
        "intents": [
            "Ingest the winter-village drone-shot clip into the workspace.",
            "Restyle the winter-village footage into a storybook illustration with warm cozy palette.",
        ],
    },
    {
        "user_goal": "Apply an art-nouveau Mucha-style ornamental look to this runway-model video.",
        "rationale": (
            "Runway-model video + art-nouveau Mucha restyle. IntakeVideoAgent ingests the clip; "
            "StyleTransferAgent applies Mucha ornamental motifs, pastel palette, and characteristic "
            "decorative framing. Raw styled output is the deliverable."
        ),
        "intents": [
            "Ingest the runway-model video into the workspace.",
            "Apply an art-nouveau Mucha-style ornamental aesthetic to the runway footage.",
        ],
    },
    {
        "user_goal": "Please turn this underwater swim clip into a pointillist Seurat-style rendition.",
        "rationale": (
            "Underwater swim clip + Seurat pointillist restyle. IntakeVideoAgent ingests the "
            "clip; StyleTransferAgent re-renders the footage in a pointillist dotted style "
            "preserving motion. Raw styled clip delivered."
        ),
        "intents": [
            "Ingest the underwater swim clip into the workspace.",
            "Transform the underwater swim footage into a Seurat pointillist dotted rendition.",
        ],
    },
    {
        "user_goal": "Convert this yoga-session clip to a Japanese sumi-e ink-painting aesthetic.",
        "rationale": (
            "Yoga-session clip + sumi-e ink-painting restyle. IntakeVideoAgent ingests the clip; "
            "StyleTransferAgent applies the minimalist black-ink brush aesthetic preserving "
            "poses and motion. Raw styled clip is the output."
        ),
        "intents": [
            "Ingest the yoga-session clip into the workspace.",
            "Restyle the yoga-session footage into a Japanese sumi-e ink-painting aesthetic.",
        ],
    },
    {
        "user_goal": "Turn this basketball-dunk clip into a 1990s arcade-game pixel-art look.",
        "rationale": (
            "Basketball dunk clip + 1990s arcade pixel-art restyle. IntakeVideoAgent ingests "
            "the clip; StyleTransferAgent renders the motion in chunky pixel-art palette with "
            "CRT-era color limitations. Raw styled clip delivered."
        ),
        "intents": [
            "Ingest the basketball-dunk clip into the workspace.",
            "Transform the basketball-dunk footage into a 1990s arcade-game pixel-art rendition.",
        ],
    },
    {
        "user_goal": "Apply a dreamy double-exposure film-look to this lavender-field clip.",
        "rationale": (
            "Lavender-field clip + dreamy double-exposure film restyle. IntakeVideoAgent "
            "ingests the clip; StyleTransferAgent applies the soft double-exposure film-grain "
            "rendition. Raw styled clip is delivered as the final asset."
        ),
        "intents": [
            "Ingest the lavender-field clip into the workspace.",
            "Apply a dreamy double-exposure film-look to the lavender-field footage.",
        ],
    },
    {
        "user_goal": "Make this parkour clip look like Frank Miller's Sin City — black and white with selective red highlights.",
        "rationale": (
            "Parkour clip + Sin City B&W + selective-red restyle. IntakeVideoAgent ingests the "
            "clip. StyleTransferAgent applies the high-contrast B&W grade with selective red "
            "preservation. Raw styled clip is the final deliverable."
        ),
        "intents": [
            "Ingest the parkour clip into the workspace.",
            "Restyle the parkour footage into a Sin City black-and-white with selective red highlights.",
        ],
    },
    {
        "user_goal": "Convert this mountain-hike video to a dreamy Thomas Cole Hudson-River-School oil look.",
        "rationale": (
            "Mountain-hike video + Hudson-River-School Thomas Cole oil restyle. IntakeVideoAgent "
            "ingests the clip; StyleTransferAgent renders the hike in soft-brush Hudson-school "
            "palette with romantic lighting. Raw styled clip delivered."
        ),
        "intents": [
            "Ingest the mountain-hike video into the workspace.",
            "Transform the mountain-hike footage into a Thomas Cole Hudson-River-School oil-painting look.",
        ],
    },
    {
        "user_goal": "Please turn this kids-playing-in-rain clip into a Cocomelon-style vibrant kid-show 3D animation look.",
        "rationale": (
            "Kids-in-rain clip + Cocomelon-style 3D-kid-show restyle. IntakeVideoAgent ingests "
            "the clip. StyleTransferAgent applies the Cocomelon vibrant color palette and "
            "rounded 3D-cartoon character feel. Raw styled clip delivered."
        ),
        "intents": [
            "Ingest the kids-playing-in-rain clip into the workspace.",
            "Restyle the kids-in-rain footage into a Cocomelon vibrant 3D kid-show aesthetic.",
        ],
    },
    {
        "user_goal": "Give this cityscape timelapse a dark cyberpunk Blade Runner 2049 color grade and atmosphere.",
        "rationale": (
            "Cityscape timelapse + Blade Runner 2049 cyberpunk grade restyle. IntakeVideoAgent "
            "ingests the clip; StyleTransferAgent applies the amber / teal palette, heavy haze, "
            "and neon glow characteristic of Blade Runner 2049. Raw styled clip delivered."
        ),
        "intents": [
            "Ingest the cityscape timelapse into the workspace.",
            "Restyle the cityscape timelapse with a Blade Runner 2049 cyberpunk amber-teal atmosphere.",
        ],
    },
    {
        "user_goal": "Apply a 1980s VHS-tape aesthetic to this concert footage — scanlines, chromatic aberration, slight tracking noise.",
        "rationale": (
            "Concert footage + 1980s VHS aesthetic restyle with scanlines and chromatic "
            "aberration. IntakeVideoAgent ingests the clip; StyleTransferAgent applies the "
            "VHS-era artifacts across frames. Raw styled clip is the output."
        ),
        "intents": [
            "Ingest the concert footage into the workspace.",
            "Restyle the concert footage into a 1980s VHS-tape aesthetic with scanlines and tracking noise.",
        ],
    },
    {
        "user_goal": "Make this ballroom-dance clip look like a Victorian-era oil portrait — low-light candlelit palette, painterly brushstrokes.",
        "rationale": (
            "Ballroom-dance clip + Victorian candlelit oil-portrait restyle. IntakeVideoAgent "
            "ingests the clip; StyleTransferAgent applies the candlelit palette and oil-paint "
            "brushstroke texture preserving the dancers' motion. Raw styled clip delivered."
        ),
        "intents": [
            "Ingest the ballroom-dance clip into the workspace.",
            "Apply a Victorian candlelit oil-portrait painterly look to the ballroom-dance footage.",
        ],
    },
    {
        "user_goal": "Turn this morning-coffee-shop clip into a cozy soft-pastel anime slice-of-life style.",
        "rationale": (
            "Morning coffee-shop clip + soft-pastel anime slice-of-life restyle. IntakeVideoAgent "
            "ingests the clip; StyleTransferAgent applies the anime slice-of-life pastel palette "
            "with warm ambient lighting. Raw styled clip delivered."
        ),
        "intents": [
            "Ingest the morning coffee-shop clip into the workspace.",
            "Restyle the coffee-shop footage into a soft-pastel anime slice-of-life aesthetic.",
        ],
    },
    {
        "user_goal": "Please convert this pottery-making demonstration into a medieval-illuminated-manuscript visual style with gold-leaf details.",
        "rationale": (
            "Pottery-making demonstration + medieval illuminated-manuscript restyle with gold "
            "leaf. IntakeVideoAgent ingests the clip; StyleTransferAgent re-renders the demo in "
            "the illuminated-manuscript aesthetic with decorative gold accents. Raw styled clip "
            "delivered."
        ),
        "intents": [
            "Ingest the pottery-making demonstration video into the workspace.",
            "Transform the pottery-making demonstration into a medieval illuminated-manuscript style with gold leaf.",
        ],
    },
    {
        "user_goal": "Restyle this street-skateboarding video as a 1990s VHS skate video with grain and warped colors.",
        "rationale": (
            "Street-skate video + 1990s VHS skate-video restyle with grain / warped color. "
            "IntakeVideoAgent ingests the clip; StyleTransferAgent applies the period-accurate "
            "VHS degradation and color shifts. Raw styled clip delivered."
        ),
        "intents": [
            "Ingest the street-skateboarding video into the workspace.",
            "Restyle the street-skate footage into a 1990s VHS skate-video aesthetic with grain and warped colors.",
        ],
    },
    {
        "user_goal": "Apply a charcoal-sketch style to this figure-skating clip — soft grayscale, emphasis on motion lines.",
        "rationale": (
            "Figure-skating clip + charcoal-sketch grayscale restyle. IntakeVideoAgent ingests "
            "the clip; StyleTransferAgent applies the charcoal grayscale rendition emphasizing "
            "motion streaks. Raw styled clip is the deliverable."
        ),
        "intents": [
            "Ingest the figure-skating clip into the workspace.",
            "Apply a charcoal-sketch grayscale style with motion-line emphasis to the figure-skating footage.",
        ],
    },
    {
        "user_goal": "Turn this jazz-club performance into a 1930s black-and-white nostalgic film grain look.",
        "rationale": (
            "Jazz-club performance + 1930s B&W nostalgic-film-grain restyle. IntakeVideoAgent "
            "ingests the clip; StyleTransferAgent applies period-accurate grayscale with heavy "
            "grain. Raw styled clip delivered."
        ),
        "intents": [
            "Ingest the jazz-club performance clip into the workspace.",
            "Restyle the jazz-club footage into a 1930s black-and-white nostalgic film-grain look.",
        ],
    },
    {
        "user_goal": "Please convert this marathon-running clip into a Japanese woodblock print with bold outlines and flat tonal zones.",
        "rationale": (
            "Marathon-running clip + Japanese woodblock restyle. IntakeVideoAgent ingests the "
            "clip; StyleTransferAgent applies bold line-art outlines and flat tonal zones. Raw "
            "styled output delivered."
        ),
        "intents": [
            "Ingest the marathon-running clip into the workspace.",
            "Transform the marathon-running footage into a Japanese woodblock-print bold-outline flat-tone aesthetic.",
        ],
    },
    {
        "user_goal": "Apply a Studio Ghibli animation look to this countryside-train-ride clip I filmed from the window.",
        "rationale": (
            "Countryside train-window clip + Ghibli animation restyle. IntakeVideoAgent ingests "
            "the clip; StyleTransferAgent renders the footage in the Ghibli watercolor / "
            "hand-drawn animation aesthetic preserving motion parallax. Raw styled clip "
            "delivered."
        ),
        "intents": [
            "Ingest the countryside-train-ride clip into the workspace.",
            "Restyle the train-window footage into a Studio Ghibli hand-drawn animation aesthetic.",
        ],
    },
    {
        "user_goal": "Make this kung-fu sparring clip look like a black-ink wuxia scroll painting.",
        "rationale": (
            "Kung-fu sparring clip + wuxia ink-scroll restyle. IntakeVideoAgent ingests the "
            "clip; StyleTransferAgent applies flowing black-ink brush aesthetic preserving "
            "martial motion. Raw styled clip is the output."
        ),
        "intents": [
            "Ingest the kung-fu sparring clip into the workspace.",
            "Restyle the sparring footage into a wuxia black-ink scroll-painting aesthetic.",
        ],
    },
    {
        "user_goal": "Turn this beachfront-sunset walk into a Rothko colorfield gradient abstraction.",
        "rationale": (
            "Beachfront-sunset walk + Rothko colorfield restyle. IntakeVideoAgent ingests the "
            "clip; StyleTransferAgent abstracts the footage into large gradient color bands "
            "reminiscent of Rothko's colorfield paintings while preserving some silhouette "
            "motion. Raw styled clip delivered."
        ),
        "intents": [
            "Ingest the beachfront-sunset walk clip into the workspace.",
            "Transform the sunset-walk footage into a Rothko-style colorfield gradient abstraction.",
        ],
    },
    {
        "user_goal": "Please give this volleyball match an 1980s anime action-scene look with speed lines and saturated colors.",
        "rationale": (
            "Volleyball-match footage + 1980s-anime action restyle with speed lines. "
            "IntakeVideoAgent ingests the clip; StyleTransferAgent renders the match with "
            "saturated anime palette and action speed-line overlays preserving play motion. Raw "
            "styled clip delivered."
        ),
        "intents": [
            "Ingest the volleyball-match footage into the workspace.",
            "Restyle the volleyball match into a 1980s anime action-scene look with speed lines and saturated colors.",
        ],
    },
    {
        "user_goal": "Convert this farmers-market walkthrough to an oil-impasto Van Gogh style with thick brush texture.",
        "rationale": (
            "Farmers-market walkthrough + Van Gogh impasto restyle with thick brush texture. "
            "IntakeVideoAgent ingests the clip; StyleTransferAgent applies the impasto brushstroke "
            "aesthetic per frame. Raw styled clip is the deliverable."
        ),
        "intents": [
            "Ingest the farmers-market walkthrough clip into the workspace.",
            "Transform the farmers-market footage into a Van Gogh impasto thick-brush oil-painting style.",
        ],
    },
    {
        "user_goal": "Restyle this rooftop yoga at dawn as a Japanese Hokusai-style woodblock scene.",
        "rationale": (
            "Rooftop dawn yoga + Hokusai woodblock restyle. IntakeVideoAgent ingests the clip; "
            "StyleTransferAgent applies the Hokusai line-art and flat-tone palette characteristic "
            "of his ukiyo-e woodblock series. Raw styled clip delivered."
        ),
        "intents": [
            "Ingest the rooftop dawn-yoga clip into the workspace.",
            "Restyle the dawn-yoga footage into a Hokusai-style woodblock scene.",
        ],
    },
    {
        "user_goal": "Apply a Warhol pop-art screen-print aesthetic to this runway walk — bright flat colors, high contrast.",
        "rationale": (
            "Runway walk + Warhol pop-art screen-print restyle. IntakeVideoAgent ingests the "
            "clip; StyleTransferAgent applies Warhol flat bright-color screen-print treatment "
            "preserving silhouette motion. Raw styled clip delivered."
        ),
        "intents": [
            "Ingest the runway walk clip into the workspace.",
            "Restyle the runway walk into a Warhol pop-art screen-print flat-color aesthetic.",
        ],
    },
    {
        "user_goal": "Make this surfing clip look like a classic Hawaiian shirt print — tropical flat motifs, bold color palette.",
        "rationale": (
            "Surfing clip + Hawaiian-shirt tropical-print restyle. IntakeVideoAgent ingests the "
            "clip; StyleTransferAgent applies tropical flat motifs and bold tropical palette "
            "while preserving wave and surfer motion. Raw styled clip delivered."
        ),
        "intents": [
            "Ingest the surfing clip into the workspace.",
            "Transform the surfing footage into a classic Hawaiian-shirt tropical-print aesthetic.",
        ],
    },
    {
        "user_goal": "Please convert this tea-ceremony performance into a traditional Chinese ink-wash painting style.",
        "rationale": (
            "Tea-ceremony performance + Chinese ink-wash restyle. IntakeVideoAgent ingests the "
            "clip; StyleTransferAgent applies minimalist ink-wash brushwork with muted tonal "
            "palette preserving ceremonial motion. Raw styled clip delivered."
        ),
        "intents": [
            "Ingest the tea-ceremony performance clip into the workspace.",
            "Restyle the tea-ceremony footage into a traditional Chinese ink-wash painting aesthetic.",
        ],
    },
    {
        "user_goal": "Turn this hip-hop dance rehearsal into a graffiti-spraypaint street-art look.",
        "rationale": (
            "Hip-hop rehearsal + graffiti-spraypaint street-art restyle. IntakeVideoAgent "
            "ingests the clip; StyleTransferAgent applies spraypaint textures, graffiti-style "
            "outlines, and urban palette while preserving choreography. Raw styled clip delivered."
        ),
        "intents": [
            "Ingest the hip-hop dance rehearsal clip into the workspace.",
            "Transform the hip-hop rehearsal into a graffiti-spraypaint street-art aesthetic.",
        ],
    },
    {
        "user_goal": "Apply a pastel chalk-drawing style to this child's-birthday-party clip.",
        "rationale": (
            "Birthday-party clip + pastel chalk-drawing restyle. IntakeVideoAgent ingests the "
            "clip; StyleTransferAgent applies chalk-texture strokes with pastel palette "
            "preserving party motion. Raw styled clip delivered."
        ),
        "intents": [
            "Ingest the child's-birthday-party clip into the workspace.",
            "Restyle the birthday-party footage into a pastel chalk-drawing rendition.",
        ],
    },
    {
        "user_goal": "Restyle this drone flyover of desert dunes as a minimalist Georgia O'Keeffe abstract painting.",
        "rationale": (
            "Desert-dunes drone flyover + O'Keeffe minimalist-abstract restyle. IntakeVideoAgent "
            "ingests the clip; StyleTransferAgent applies the O'Keeffe smooth gradients and "
            "simplified organic forms. Raw styled clip delivered."
        ),
        "intents": [
            "Ingest the desert-dunes drone-flyover clip into the workspace.",
            "Restyle the drone flyover into a Georgia O'Keeffe minimalist-abstract rendition.",
        ],
    },
    {
        "user_goal": "Convert this ice-skating performance to a stained-glass cathedral-window look with bold lead lines.",
        "rationale": (
            "Ice-skating performance + stained-glass cathedral-window restyle. IntakeVideoAgent "
            "ingests the clip; StyleTransferAgent applies bold lead-line segmentation and "
            "cathedral-window color palette preserving skating motion. Raw styled clip delivered."
        ),
        "intents": [
            "Ingest the ice-skating performance clip into the workspace.",
            "Restyle the ice-skating footage into a stained-glass cathedral-window rendition with bold lead lines.",
        ],
    },
    {
        "user_goal": "Please apply a Mondrian-style primary-color geometric abstraction to this urban architecture walkthrough.",
        "rationale": (
            "Urban-architecture walkthrough + Mondrian primary-color geometric restyle. "
            "IntakeVideoAgent ingests the clip; StyleTransferAgent abstracts the architecture "
            "into a Mondrian grid with primary-color fills. Raw styled clip delivered."
        ),
        "intents": [
            "Ingest the urban architecture walkthrough into the workspace.",
            "Transform the architecture walkthrough into a Mondrian primary-color geometric abstraction.",
        ],
    },
    {
        "user_goal": "Make this autumn-forest walk into a retro 2D Cartoon Network animation style — flat colors, thick outlines.",
        "rationale": (
            "Autumn-forest walk + Cartoon Network 2D restyle with thick outlines. "
            "IntakeVideoAgent ingests the clip; StyleTransferAgent applies flat-color 2D "
            "cartoon styling with bold outlines. Raw styled clip delivered."
        ),
        "intents": [
            "Ingest the autumn-forest walk clip into the workspace.",
            "Restyle the autumn-forest footage into a retro 2D Cartoon Network flat-color outlined aesthetic.",
        ],
    },
    {
        "user_goal": "Turn this aerial shot of a lighthouse at dawn into a soft pastel J.M.W. Turner seascape.",
        "rationale": (
            "Lighthouse-at-dawn aerial + J.M.W. Turner pastel seascape restyle. "
            "IntakeVideoAgent ingests the clip; StyleTransferAgent applies Turner's atmospheric "
            "soft-pastel seascape aesthetic with diffused dawn light. Raw styled clip delivered."
        ),
        "intents": [
            "Ingest the lighthouse-at-dawn aerial clip into the workspace.",
            "Restyle the aerial lighthouse footage into a J.M.W. Turner pastel seascape rendition.",
        ],
    },
]
