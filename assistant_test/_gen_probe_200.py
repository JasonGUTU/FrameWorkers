"""Generate 200-case probe set from 24 anchor shapes.

Distribution: Short (5 shapes × 8) + Medium (10 × 11 + 1 × 10) + Long (8 × 5) = 200
"""
import json
from pathlib import Path

# Each entry: name, category, expected_chain, anchor_goal, variant_goals (N=7 short / 10 medium / 4 long)
SHAPES = [
    # ============ SHORT (5) ============
    {
        "name": "style_018", "category": "style",
        "expected_chain": [["IntakeVideoAgent"],["StyleTransferAgent"],["TranscriptionAgent"],["TranslationAgent"],["CompositorAgent"],["done"]],
        "anchor": "Convert this Mandarin costume-drama clip to a Studio Ghibli watercolor style and add English-Chinese bilingual subtitles.",
        "variants": [
            "Convert this Vietnamese street-market argument clip to a charcoal-sketch animated style and add Vietnamese-English bilingual subtitles.",
            "Convert this Korean K-pop dance performance clip to a vibrant anime style and add Korean-English bilingual subtitles.",
            "Convert this Russian opera-house final aria clip to an oil-painting animated style and add Russian-English bilingual subtitles.",
            "Convert this Japanese tea-ceremony master class clip to a pixel-art 8-bit style and add Japanese-English bilingual subtitles.",
            "Convert this Spanish flamenco-club confrontation clip to a 1940s film-noir black-and-white style and add Spanish-English bilingual subtitles.",
            "Convert this Cantonese family banquet argument clip to a Studio Ghibli watercolor style and add Cantonese-English bilingual subtitles.",
            "Convert this Hindi wedding ceremony clip to a vibrant Bollywood-poster art style and add Hindi-English bilingual subtitles.",
        ],
    },
    {
        "name": "extend_018", "category": "extend",
        "expected_chain": [["IntakeVideoAgent"],["VideoExtendAgent"],["TranscriptionAgent"],["TranslationAgent"],["CompositorAgent"],["done"]],
        "anchor": "Extend this Mandarin courtroom-drama confrontation scene by 12 seconds and add English-Chinese bilingual subtitles.",
        "variants": [
            "Extend this Korean K-drama balcony break-up scene by 10 seconds and add Korean-English bilingual subtitles.",
            "Extend this Italian piazza street-vendor argument scene by 8 seconds and add Italian-English bilingual subtitles.",
            "Extend this Cantonese tea-house gambling-table standoff by 15 seconds and add Cantonese-English bilingual subtitles.",
            "Extend this Russian dacha-kitchen family confrontation scene by 12 seconds and add Russian-English bilingual subtitles.",
            "Extend this Japanese izakaya late-night confession scene by 10 seconds and add Japanese-English bilingual subtitles.",
            "Extend this Arabic souk haggling scene by 8 seconds and add Arabic-English bilingual subtitles.",
            "Extend this French bistro lover's quarrel scene by 12 seconds and add French-English bilingual subtitles.",
        ],
    },
    {
        "name": "highlight_028", "category": "complex",
        "expected_chain": [["IntakeVideoAgent"],["VideoAnalysisAgent"],["HighlightAgent"],["StyleTransferAgent"],["CompositorAgent"],["done"]],
        "anchor": "Cut the most dramatic moments from this Mandarin palace-intrigue mini-drama and convert the resulting teaser to an ink-wash animated style.",
        "variants": [
            "Cut the most thrilling chase moments from this Korean spy-thriller series and convert the resulting teaser to a vibrant anime style.",
            "Cut the most heartbreaking confession scenes from this Japanese romance drama and convert the teaser to a soft watercolor animated style.",
            "Cut the most intense interrogation scenes from this Spanish noir series and convert the teaser to a 1940s black-and-white film-noir style.",
            "Cut the most epic battle moments from this Vietnamese historical war drama and convert the teaser to a gritty ink-wash animated style.",
            "Cut the most emotional reunion scenes from this Indian family drama and convert the teaser to a vibrant Bollywood-poster art style.",
            "Cut the most suspenseful supernatural moments from this Thai horror mini-series and convert the teaser to a charcoal-sketch animated style.",
            "Cut the most dazzling dance moments from this Russian ballet film and convert the teaser to an oil-painting animated style.",
        ],
    },
    {
        "name": "style_201", "category": "style",
        "expected_chain": [["IntakeVideoAgent"],["StyleTransferAgent"],["AmbienceAgent"],["AudioMixAgent"],["CompositorAgent"],["done"]],
        "anchor": "Convert this Mandarin tea-ceremony footage to an ink-wash-painted style and add quiet teahouse-courtyard ambient sounds.",
        "variants": [
            "Convert this Spanish flamenco-class footage to a charcoal-sketch animated style and add wooden-floor-and-clapping ambient sounds.",
            "Convert this Japanese koi-pond garden footage to a Studio Ghibli watercolor style and add gentle water-and-bird ambient sounds.",
            "Convert this Moroccan souk merchant footage to an oil-painting animated style and add bustling-market-haggling ambient sounds.",
            "Convert this Norwegian fjord rowing footage to an art-nouveau-poster style and add cold-wind-and-water-lapping ambient sounds.",
            "Convert this Greek olive-grove harvest footage to a sepia 1920s-postcard style and add cicada-and-rustling-leaves ambient sounds.",
            "Convert this Brazilian samba street-school footage to a vibrant pixel-art style and add drums-and-feet-on-pavement ambient sounds.",
            "Convert this Tibetan monastery prayer-wheel footage to an ink-wash-painted style and add chanting-and-mountain-wind ambient sounds.",
        ],
    },
    {
        "name": "extend_201", "category": "extend",
        "expected_chain": [["IntakeVideoAgent"],["VideoExtendAgent"],["AmbienceAgent"],["AudioMixAgent"],["CompositorAgent"],["done"]],
        "anchor": "Extend this lighthouse-keeper closing scene to 30 seconds and add continuous ocean-wave ambient sounds.",
        "variants": [
            "Extend this monastery-bell-tolling closing scene to 25 seconds and add distant-mountain-wind ambient sounds.",
            "Extend this train-platform farewell scene to 20 seconds and add steam-engine-and-crowd-murmur ambient sounds.",
            "Extend this desert-caravan sunset scene to 30 seconds and add wind-over-sand-dune ambient sounds.",
            "Extend this cathedral organist closing scene to 25 seconds and add reverberant-stone-hall ambient sounds.",
            "Extend this rural-pottery-kiln cooling scene to 20 seconds and add crackling-wood-fire ambient sounds.",
            "Extend this fishing-boat dawn-departure scene to 25 seconds and add seagull-and-water-slap ambient sounds.",
            "Extend this samurai-meditation closing scene to 30 seconds and add bamboo-fountain-and-temple-bell ambient sounds.",
        ],
    },
    # ============ MEDIUM (11) ============
    {
        "name": "highlight_022", "category": "highlight",
        "expected_chain": [["IntakeVideoAgent"],["VideoAnalysisAgent"],["HighlightAgent"],["TranscriptionAgent"],["TranslationAgent"],["CompositorAgent"],["done"]],
        "anchor": "Cut the most thrilling courtroom-confrontation moments from this Mandarin legal-drama series into a 60-second promotional teaser with English-Chinese bilingual subtitles.",
        "variants": [
            "Cut the most explosive battle moments from this Korean military-action series into a 90-second teaser with Korean-English bilingual subtitles.",
            "Cut the most heartbreaking parting scenes from this Japanese family drama into a 60-second teaser with Japanese-English bilingual subtitles.",
            "Cut the most intense sword-fight moments from this Vietnamese wuxia series into a 75-second teaser with Vietnamese-English bilingual subtitles.",
            "Cut the most charged interrogation moments from this Spanish-language noir series into a 60-second teaser with Spanish-English bilingual subtitles.",
            "Cut the most dramatic medical-emergency moments from this Russian hospital drama into a 90-second teaser with Russian-English bilingual subtitles.",
            "Cut the most romantic confession moments from this French period romance into a 60-second teaser with French-English bilingual subtitles.",
            "Cut the most suspenseful supernatural moments from this Thai horror series into a 75-second teaser with Thai-English bilingual subtitles.",
            "Cut the most acrobatic stunt moments from this Hindi action film into a 60-second teaser with Hindi-English bilingual subtitles.",
            "Cut the most emotional graduation moments from this Mandarin coming-of-age series into a 60-second teaser with English-Chinese bilingual subtitles.",
            "Cut the most chilling reveal moments from this Italian giallo mystery series into a 75-second teaser with Italian-English bilingual subtitles.",
        ],
    },
    {
        "name": "extend_022", "category": "extend",
        "expected_chain": [["IntakeVideoAgent"],["VideoExtendAgent"],["AmbienceAgent","MusicAgent"],["AmbienceAgent","MusicAgent"],["AudioMixAgent"],["CompositorAgent"],["done"]],
        "anchor": "Extend this nightclub-confrontation scene by 8 seconds and add a tense electronic score plus crowd-murmur and clinking-glass ambient sounds.",
        "variants": [
            "Extend this casino blackjack-table standoff scene by 10 seconds and add a tense jazz score plus card-shuffle-and-low-conversation ambient sounds.",
            "Extend this airport tearful-farewell scene by 12 seconds and add a melancholy piano score plus crowd-and-distant-PA ambient sounds.",
            "Extend this carnival haunted-house chase scene by 8 seconds and add a creepy organ score plus carnival-crowd-and-distant-screams ambient sounds.",
            "Extend this open-air rooftop stargazing scene by 15 seconds and add a contemplative ambient score plus distant-city-and-light-wind ambient sounds.",
            "Extend this medieval marketplace pickpocket-chase scene by 10 seconds and add an upbeat lute-and-drum score plus market-crowd-and-cart-wheels ambient sounds.",
            "Extend this submarine sonar-tense scene by 12 seconds and add a dread-laden synth score plus low-rumble-and-hissing-pipes ambient sounds.",
            "Extend this gothic cathedral pursuit scene by 10 seconds and add a foreboding choral score plus reverberant-footsteps-and-distant-bells ambient sounds.",
            "Extend this dimly-lit speakeasy whispered-deal scene by 10 seconds and add a smoky saxophone score plus low-murmurs-and-clinking-glass ambient sounds.",
            "Extend this beach bonfire confession scene by 15 seconds and add a soft acoustic-guitar score plus crashing-waves-and-crackling-fire ambient sounds.",
            "Extend this snow-storm cabin standoff scene by 12 seconds and add an unsettling string score plus howling-wind-and-creaking-wood ambient sounds.",
        ],
    },
    {
        "name": "complex_104", "category": "complex",
        "expected_chain": [["IntakeVideoAgent"],["VideoAnalysisAgent"],["HighlightAgent"],["StyleTransferAgent"],["TranscriptionAgent"],["CompositorAgent"],["done"]],
        "anchor": "Analyze this hit Mandarin crime-thriller mini-drama, cut the most suspenseful twist moments into a teaser, then convert the teaser to a gritty Japanese-anime visual style and add English subtitles.",
        "variants": [
            "Analyze this hit Korean medical drama, cut the most emotional surgery moments into a teaser, convert it to a soft watercolor animated style, and add English subtitles.",
            "Analyze this hit Japanese yakuza thriller, cut the most violent confrontation moments into a teaser, convert it to a gritty ink-wash animated style, and add English subtitles.",
            "Analyze this hit Spanish telenovela, cut the most explosive reveal moments into a teaser, convert it to a vibrant pop-art style, and add English subtitles.",
            "Analyze this hit Vietnamese silat-action series, cut the most acrobatic fight moments into a teaser, convert it to a dynamic comic-book style, and add English subtitles.",
            "Analyze this hit Indian mystery series, cut the most chilling reveal moments into a teaser, convert it to a 1940s film-noir black-and-white style, and add English subtitles.",
            "Analyze this hit Russian historical drama, cut the most dramatic court-intrigue moments into a teaser, convert it to an oil-painting animated style, and add English subtitles.",
            "Analyze this hit Italian giallo thriller, cut the most disturbing nightmare moments into a teaser, convert it to a charcoal-sketch animated style, and add English subtitles.",
            "Analyze this hit Cantonese police-procedural series, cut the most tense interrogation moments into a teaser, convert it to a Studio Ghibli watercolor style, and add English subtitles.",
            "Analyze this hit Thai supernatural-horror series, cut the most haunting apparition moments into a teaser, convert it to a sepia 1920s silent-film style, and add English subtitles.",
            "Analyze this hit Brazilian crime drama, cut the most explosive shootout moments into a teaser, convert it to a vibrant graffiti street-art style, and add English subtitles.",
        ],
    },
    {
        "name": "style_202", "category": "style",
        "expected_chain": [["IntakeVideoAgent"],["StyleTransferAgent"],["AmbienceAgent","MusicAgent"],["AmbienceAgent","MusicAgent"],["AudioMixAgent"],["CompositorAgent"],["done"]],
        "anchor": "Convert this rainy Tokyo intersection footage to a Studio Ghibli style and add a melancholy piano score plus rain-and-traffic ambient sounds.",
        "variants": [
            "Convert this snowy Moscow square footage to an oil-painting style and add a soft balalaika score plus distant-bells-and-snow-crunch ambient sounds.",
            "Convert this dawn Cairo bazaar footage to a vibrant ink-wash style and add a haunting oud score plus market-stir-and-call-to-prayer ambient sounds.",
            "Convert this stormy Cornish coastline footage to a sepia 1920s-postcard style and add a sweeping orchestral score plus crashing-waves-and-gull-cries ambient sounds.",
            "Convert this neon Seoul side-street footage to a vibrant pixel-art style and add an upbeat synth-pop score plus footsteps-and-distant-karaoke ambient sounds.",
            "Convert this fogbound Scottish moor footage to a charcoal-sketch animated style and add a mournful bagpipe score plus wind-over-heather ambient sounds.",
            "Convert this bustling Mumbai rickshaw-stand footage to a Bollywood-poster art style and add an upbeat sitar-and-tabla score plus traffic-horn-and-vendor-cry ambient sounds.",
            "Convert this twilight Venice canal footage to a watercolor animated style and add a mournful violin score plus water-lapping-and-distant-laughter ambient sounds.",
            "Convert this misty Vietnamese rice-paddy footage to a Studio Ghibli style and add a gentle dan-bau score plus frog-chorus-and-distant-water-buffalo ambient sounds.",
            "Convert this golden-hour Tuscan vineyard footage to an oil-painting animated style and add a warm mandolin score plus rustling-leaves-and-distant-cicadas ambient sounds.",
            "Convert this midnight Reykjavik harbor footage to an ink-wash-painted style and add an icy ambient-electronic score plus creaking-boats-and-arctic-wind ambient sounds.",
        ],
    },
    {
        "name": "style_203", "category": "style",
        "expected_chain": [["IntakeVideoAgent"],["StyleTransferAgent"],["MusicAgent","TranscriptionAgent"],["MusicAgent","TranscriptionAgent"],["AudioMixAgent"],["CompositorAgent"],["done"]],
        "anchor": "Convert this Mandarin street-performance clip to a traditional ink-wash style, add English subtitles and a soft erhu score.",
        "variants": [
            "Convert this Cantonese late-night talk show clip to a vibrant comic-book style, add English subtitles and a jazzy big-band score.",
            "Convert this Japanese izakaya monologue clip to a Studio Ghibli watercolor style, add English subtitles and a wistful shakuhachi-and-strings score.",
            "Convert this Spanish flamenco club performer monologue clip to a 1940s film-noir black-and-white style, add English subtitles and a brooding flamenco-guitar score.",
            "Convert this Russian poet recitation clip to an oil-painting animated style, add English subtitles and a melancholy balalaika-and-violin score.",
            "Convert this Korean street rapper clip to a vibrant pixel-art style, add English subtitles and a punchy hip-hop-trap score.",
            "Convert this French chanson cabaret clip to an art-nouveau-poster style, add English subtitles and a dreamy accordion-and-strings score.",
            "Convert this Vietnamese village folk-singer clip to a charcoal-sketch animated style, add English subtitles and a gentle dan-bau-and-bamboo-flute score.",
            "Convert this Hindi qawwali singer clip to a vibrant Bollywood-poster art style, add English subtitles and a soaring harmonium-and-tabla score.",
            "Convert this Arabic souk poet clip to a sepia 1920s style, add English subtitles and a haunting oud-and-ney score.",
            "Convert this Greek bouzouki bar singer clip to an aged oil-painting animated style, add English subtitles and a soulful bouzouki-and-clarinet score.",
        ],
    },
    {
        "name": "extend_202", "category": "extend",
        "expected_chain": [["IntakeVideoAgent"],["VideoExtendAgent"],["MusicAgent","TranscriptionAgent"],["MusicAgent","TranscriptionAgent"],["AudioMixAgent"],["CompositorAgent"],["done"]],
        "anchor": "Extend this Spanish flamenco-club confrontation scene to 30 seconds, add English subtitles and a tense flamenco-guitar score.",
        "variants": [
            "Extend this Korean fish-market argument scene to 25 seconds, add English subtitles and a tense electronic score.",
            "Extend this Japanese izakaya whispered-confession scene to 30 seconds, add English subtitles and a wistful piano score.",
            "Extend this Vietnamese rice-paddy elder-villager argument scene to 25 seconds, add English subtitles and a sparse dan-bau score.",
            "Extend this French bistro break-up scene to 30 seconds, add English subtitles and a melancholy accordion score.",
            "Extend this Russian dacha-kitchen heated-argument scene to 25 seconds, add English subtitles and a brooding cello score.",
            "Extend this Cantonese yum-cha-restaurant confrontation scene to 30 seconds, add English subtitles and a moody string score.",
            "Extend this Italian piazza fountain-confession scene to 25 seconds, add English subtitles and a soft mandolin score.",
            "Extend this Arabic souk dispute scene to 30 seconds, add English subtitles and a haunting ney-flute score.",
            "Extend this Hindi temple-courtyard standoff scene to 25 seconds, add English subtitles and a tense sitar-and-tabla score.",
            "Extend this Greek monastery courtyard argument scene to 30 seconds, add English subtitles and a brooding bouzouki score.",
        ],
    },
    {
        "name": "highlight_201", "category": "highlight",
        "expected_chain": [["IntakeVideoAgent"],["VideoAnalysisAgent"],["HighlightAgent"],["AmbienceAgent"],["AudioMixAgent"],["CompositorAgent"],["done"]],
        "anchor": "Cut a 60-second highlight reel from this golf championship footage and add continuous golf-course-and-light-applause ambient sounds.",
        "variants": [
            "Cut a 90-second highlight reel from this archery tournament footage and add continuous quiet-range-and-arrow-thuds ambient sounds.",
            "Cut a 60-second highlight reel from this chess championship footage and add continuous quiet-hall-and-clock-tick ambient sounds.",
            "Cut a 75-second highlight reel from this surfing competition footage and add continuous crashing-waves-and-distant-cheers ambient sounds.",
            "Cut a 60-second highlight reel from this fencing championship footage and add continuous metal-clang-and-soft-applause ambient sounds.",
            "Cut a 90-second highlight reel from this rock-climbing championship footage and add continuous wind-and-rock-scrape ambient sounds.",
            "Cut a 60-second highlight reel from this competitive sailing race footage and add continuous water-rush-and-sail-flap ambient sounds.",
            "Cut a 75-second highlight reel from this dressage competition footage and add continuous arena-soft-and-hoofbeats ambient sounds.",
            "Cut a 60-second highlight reel from this synchronized-swimming meet footage and add continuous water-splash-and-faint-crowd ambient sounds.",
            "Cut a 90-second highlight reel from this tea-ceremony national contest footage and add continuous quiet-room-and-hot-water-pour ambient sounds.",
            "Cut a 60-second highlight reel from this national calligraphy competition footage and add continuous brush-stroke-and-paper-rustle ambient sounds.",
        ],
    },
    {
        "name": "storytelling_035", "category": "storytelling",
        "expected_chain": [["NarrationAgent"],["AmbienceAgent","IllustrationAgent","MusicAgent","NarratorAgent"],["AmbienceAgent","IllustrationAgent","MusicAgent","NarratorAgent"],["AmbienceAgent","IllustrationAgent","MusicAgent","NarratorAgent"],["AmbienceAgent","IllustrationAgent","MusicAgent","NarratorAgent"],["AudioMixAgent"],["CompositorAgent"],["done"]],
        "anchor": "Narrate this seafaring tale of a lighthouse keeper's daughter who befriends a sea-storm spirit as an illustrated audiobook, with a haunting maritime orchestral score, ocean-storm ambient sounds, and English narration.",
        "variants": [
            "Narrate this Tibetan folktale of a young yak-herder who befriends a mountain-spirit as an illustrated audiobook, with a meditative bamboo-flute-and-bowl score, mountain-wind ambient sounds, and English narration.",
            "Narrate this Andean folktale of a llama-herder girl who learns the wind's song from her grandmother as an illustrated audiobook, with a haunting pan-pipe-and-charango score, high-altitude wind ambient sounds, and English narration.",
            "Narrate this Bengali folktale of a boatman who ferries a tiger-spirit across the Sundarbans as an illustrated audiobook, with a soulful sarod-and-tabla score, river-and-jungle ambient sounds, and English narration.",
            "Narrate this Norse folktale of a child-blacksmith who forges a sword for a forest-troll as an illustrated audiobook, with a sweeping nyckelharpa-and-drum score, forest-and-anvil ambient sounds, and English narration.",
            "Narrate this Yoruba folktale of a fisherwoman who tricks a river-deity out of his net as an illustrated audiobook, with a pulsing talking-drum-and-shekere score, river-and-marketplace ambient sounds, and English narration.",
            "Narrate this Inuit folktale of a hunter who dances with the aurora as an illustrated audiobook, with a haunting throat-singing-and-drum score, arctic-wind-and-creaking-ice ambient sounds, and English narration.",
            "Narrate this Ainu folktale of a girl who learns the bear's lullaby as an illustrated audiobook, with a delicate mukkuri-and-tonkori score, deep-forest-and-bear-grunt ambient sounds, and English narration.",
            "Narrate this Maori folktale of a navigator who reads the stars to find a lost island as an illustrated audiobook, with a deep haka-and-koauau score, ocean-and-night-sky ambient sounds, and English narration.",
            "Narrate this Lakota folktale of a buffalo-girl who calls back the herds as an illustrated audiobook, with a powerful drum-and-flute score, prairie-wind ambient sounds, and English narration.",
            "Narrate this Hawaiian folktale of a fire-tender who reasons with Pele as an illustrated audiobook, with a gentle ukulele-and-slack-key score, volcanic-rumble-and-ocean ambient sounds, and English narration.",
        ],
    },
    {
        "name": "complex_201", "category": "complex",
        "expected_chain": [["IntakeVideoAgent"],["VideoExtendAgent"],["StyleTransferAgent"],["AmbienceAgent","MusicAgent"],["AmbienceAgent","MusicAgent"],["AudioMixAgent"],["CompositorAgent"],["done"]],
        "anchor": "Convert this corporate-office walking shot to a cyberpunk-anime style, extend it to 30 seconds, and add a synthwave score plus rain-soaked-neon-city ambient sounds.",
        "variants": [
            "Convert this convenience-store night-clerk shot to a Studio Ghibli style, extend it to 25 seconds, and add a soft lo-fi score plus distant-city-traffic ambient sounds.",
            "Convert this empty subway-platform shot to a 1940s film-noir black-and-white style, extend it to 30 seconds, and add a moody saxophone score plus distant-train-and-rat-scurry ambient sounds.",
            "Convert this rooftop-garden weeding shot to a watercolor animated style, extend it to 25 seconds, and add a gentle harp score plus rooftop-wind-and-leaf-rustle ambient sounds.",
            "Convert this airport waiting-area shot to a vibrant pixel-art style, extend it to 30 seconds, and add an upbeat synth-pop score plus crowd-and-distant-PA ambient sounds.",
            "Convert this gothic-cathedral-tour-guide shot to a charcoal-sketch animated style, extend it to 25 seconds, and add a foreboding choral score plus reverberant-footsteps-and-distant-bells ambient sounds.",
            "Convert this forest-ranger-station log-burning shot to an oil-painting animated style, extend it to 30 seconds, and add a contemplative woodwind score plus crackling-fire-and-distant-owl ambient sounds.",
            "Convert this empty-warehouse pacing shot to a dystopian dark-pixel-art style, extend it to 25 seconds, and add a tense industrial-electronic score plus dripping-water-and-creaking-metal ambient sounds.",
            "Convert this misty-pond morning-tai-chi shot to an ink-wash-painted style, extend it to 30 seconds, and add a meditative guzheng-and-flute score plus lapping-water-and-distant-bird ambient sounds.",
            "Convert this snowed-in mountain-cabin reading shot to a sepia 1920s-postcard style, extend it to 25 seconds, and add a wistful music-box score plus crackling-fireplace-and-howling-wind ambient sounds.",
            "Convert this neon-lit Hong-Kong rooftop shot to an anime style, extend it to 30 seconds, and add a synth-rock score plus distant-traffic-and-helicopter ambient sounds.",
        ],
    },
    {
        "name": "highlight_202", "category": "highlight",
        "expected_chain": [["IntakeVideoAgent"],["VideoAnalysisAgent"],["HighlightAgent"],["AmbienceAgent","MusicAgent","TranscriptionAgent"],["AmbienceAgent","MusicAgent","TranscriptionAgent"],["AmbienceAgent","MusicAgent","TranscriptionAgent"],["AudioMixAgent"],["CompositorAgent"],["done"]],
        "anchor": "Cut a 90-second highlight reel from this Mandarin street-food vlog with English subtitles, lo-fi hip-hop background music, and bustling-night-market ambient sounds.",
        "variants": [
            "Cut a 75-second highlight reel from this Korean cooking-show series with English subtitles, upbeat K-indie music, and kitchen-clatter-and-sizzle ambient sounds.",
            "Cut a 90-second highlight reel from this Japanese izakaya tour vlog with English subtitles, smooth city-pop music, and crowded-bar-laughter ambient sounds.",
            "Cut a 75-second highlight reel from this Vietnamese pho-shop documentary with English subtitles, gentle bossa-nova music, and bowl-clatter-and-broth-pour ambient sounds.",
            "Cut a 60-second highlight reel from this Spanish tapas-bar documentary with English subtitles, lively flamenco-fusion music, and chatter-and-glass-clink ambient sounds.",
            "Cut a 90-second highlight reel from this Indian masala-tea-vendor documentary with English subtitles, upbeat Bollywood-fusion music, and street-bustle-and-tea-pour ambient sounds.",
            "Cut a 75-second highlight reel from this Italian gelato-cart documentary with English subtitles, romantic Italian-pop music, and piazza-stroll-and-children-laughter ambient sounds.",
            "Cut a 60-second highlight reel from this Moroccan tagine-restaurant tour with English subtitles, hypnotic gnawa-trance music, and clay-pot-bubble-and-coal-crackle ambient sounds.",
            "Cut a 90-second highlight reel from this Brazilian acai-bowl street-cart vlog with English subtitles, upbeat samba-pop music, and beach-crowd-and-blender-whir ambient sounds.",
            "Cut a 75-second highlight reel from this Thai green-curry kitchen tour with English subtitles, gentle bossa-bamboo music, and wok-sizzle-and-mortar-pestle ambient sounds.",
            "Cut a 60-second highlight reel from this Russian pelmeni-dumpling-house tour with English subtitles, warm folk-fusion music, and dough-roll-and-soft-chatter ambient sounds.",
        ],
    },
    {
        "name": "storytelling_202", "category": "storytelling",
        "expected_chain": [["NarrationAgent"],["AmbienceAgent","IllustrationAgent","MusicAgent","NarratorAgent"],["AmbienceAgent","IllustrationAgent","MusicAgent","NarratorAgent"],["AmbienceAgent","IllustrationAgent","MusicAgent","NarratorAgent"],["AmbienceAgent","IllustrationAgent","MusicAgent","NarratorAgent"],["AudioMixAgent"],["TranslationAgent"],["CompositorAgent"],["done"]],
        "anchor": "Tell me an old Mexican folktale about a desert-coyote teaching a lost girl to find water as an illustrated audiobook narrated in Spanish, with a guitar-and-marimba score, desert-night-cricket ambient sounds, and English subtitles.",
        "variants": [
            "Tell me a Quechua folktale about a condor-spirit guiding a shepherd boy down from a glacier as an illustrated audiobook narrated in Quechua, with a quena-flute-and-charango score, high-altitude wind ambient sounds, and English subtitles.",
            "Tell me a Yoruba folktale about a tortoise outwitting a sky-king as an illustrated audiobook narrated in Yoruba, with a talking-drum-and-shekere score, palm-grove-and-village ambient sounds, and English subtitles.",
            "Tell me a Persian folktale about a woodcutter who befriends a star-fallen jinn as an illustrated audiobook narrated in Persian, with a santur-and-ney score, mountain-cave-and-fire ambient sounds, and English subtitles.",
            "Tell me a Vietnamese folktale about a fisher-girl who tames a river-dragon as an illustrated audiobook narrated in Vietnamese, with a dan-tranh-and-bamboo-flute score, riverbank ambient sounds, and English subtitles.",
            "Tell me a Hawaiian folktale about a fire-keeper who calms Pele as an illustrated audiobook narrated in Hawaiian, with a slack-key-and-ukulele score, volcano-rumble-and-ocean ambient sounds, and English subtitles.",
            "Tell me a Greek folktale about a shepherd-girl who teaches a Cyclops to play the lyre as an illustrated audiobook narrated in modern Greek, with a bouzouki-and-clarinet score, mountain-meadow-and-distant-bells ambient sounds, and English subtitles.",
            "Tell me a Romanian folktale about a young weaver who outsmarts a forest witch as an illustrated audiobook narrated in Romanian, with a violin-and-cimbalom score, deep-forest-and-loom ambient sounds, and English subtitles.",
            "Tell me a Berber folktale about a date-palm tender who befriends a sand-jinn as an illustrated audiobook narrated in Berber, with an oud-and-bendir score, oasis-and-desert-wind ambient sounds, and English subtitles.",
            "Tell me a Tahitian folktale about a young vahine who learns the lagoon's lullaby as an illustrated audiobook narrated in Tahitian, with a ukulele-and-pahu-drum score, lagoon-and-distant-reef ambient sounds, and English subtitles.",
        ],
    },
    # ============ LONG (8) ============
    {
        "name": "complex_202", "category": "complex",
        "expected_chain": [["StoryAgent"],["ScreenplayAgent"],["KeyFrameAgent"],["VideoAgent"],["VideoExtendAgent"],["AmbienceAgent","MusicAgent"],["AmbienceAgent","MusicAgent"],["AudioMixAgent"],["CompositorAgent"],["done"]],
        "anchor": "Make a 90-second cyberpunk mini-drama about a Tokyo street courier discovering a stolen AI brain in a back alley, extend the discovery moment for dramatic impact, and add a synthwave score plus neon-rain-city ambient sounds.",
        "variants": [
            "Make a 60-second period mini-drama about a Victorian-London midwife uncovering a poisoner's pantry on her last call of the night, prolong the reveal moment for dramatic impact, and add an unsettling string-quartet score plus gas-lamp-fizz-and-distant-carriage ambient sounds.",
            "Make a 90-second post-apocalyptic mini-drama about a salt-flat scavenger finding a still-running music-box in the dust, draw out the find moment for dramatic impact, and add a sparse ambient-electronic score plus dry-wind-and-distant-thunder ambient sounds.",
            "Make a 75-second 1920s mini-drama about a Buenos-Aires tango pianist finding her missing partner's diary in the lining of a dress, prolong the reading moment for dramatic impact, and add a melancholy bandoneon score plus distant-tango-bar-and-rain ambient sounds.",
            "Make a 90-second medieval mini-drama about a Welsh hill-shepherd uncovering a cache of Norman gold in a rabbit warren, draw out the discovery moment for dramatic impact, and add a brooding harp-and-drone score plus high-pasture-and-sheep-bleat ambient sounds.",
        ],
    },
    {
        "name": "highlight_203", "category": "highlight",
        "expected_chain": [["IntakeVideoAgent"],["VideoAnalysisAgent"],["HighlightAgent"],["TranscriptionAgent"],["TranslationAgent"],["AmbienceAgent","MusicAgent"],["AmbienceAgent","MusicAgent"],["AudioMixAgent"],["CompositorAgent"],["done"]],
        "anchor": "Cut a 60-second highlight reel from this Mandarin variety show with English-Mandarin bilingual subtitles, an upbeat orchestral score, and studio-audience ambient sounds.",
        "variants": [
            "Cut a 90-second highlight reel from this Korean cooking competition with Korean-English bilingual subtitles, an upbeat K-pop score, and kitchen-bustle-and-applause ambient sounds.",
            "Cut a 75-second highlight reel from this Spanish dance contest with Spanish-English bilingual subtitles, a flamenco-fusion score, and stage-crowd-and-castanet ambient sounds.",
            "Cut a 60-second highlight reel from this Japanese stand-up comedy show with Japanese-English bilingual subtitles, a jazzy big-band score, and small-club-laughter ambient sounds.",
            "Cut a 90-second highlight reel from this Russian ice-skating gala with Russian-English bilingual subtitles, a sweeping orchestral score, and rink-and-distant-applause ambient sounds.",
        ],
    },
    {
        "name": "complex_203", "category": "complex",
        "expected_chain": [["IntakeVideoAgent"],["VideoExtendAgent"],["StyleTransferAgent"],["TranscriptionAgent"],["TranslationAgent"],["AmbienceAgent","MusicAgent"],["AmbienceAgent","MusicAgent"],["AudioMixAgent"],["CompositorAgent"],["done"]],
        "anchor": "Convert this Mandarin marketplace clip to a Studio Ghibli style, extend it to 30 seconds, add English-Mandarin bilingual subtitles, a traditional pipa-and-strings score, and busy-market ambient sounds.",
        "variants": [
            "Convert this Korean fish-market dawn clip to an oil-painting animated style, extend it to 25 seconds, add Korean-English bilingual subtitles, a haunting daegeum-flute score, and dock-haggle-and-seagull ambient sounds.",
            "Convert this Vietnamese floating-market clip to an ink-wash-painted style, extend it to 30 seconds, add Vietnamese-English bilingual subtitles, a gentle dan-bau score, and water-paddle-and-vendor-call ambient sounds.",
            "Convert this Moroccan souk merchant-haggling clip to a vibrant pop-art style, extend it to 25 seconds, add Arabic-English bilingual subtitles, a hypnotic oud-and-bendir score, and souk-bustle-and-call-to-prayer ambient sounds.",
            "Convert this Indian flower-market dawn clip to a Bollywood-poster art style, extend it to 30 seconds, add Hindi-English bilingual subtitles, an upbeat sitar-and-tabla score, and incense-and-vendor-blessing ambient sounds.",
        ],
    },
    {
        "name": "complex_204", "category": "complex",
        "expected_chain": [["IntakeVideoAgent"],["VideoAnalysisAgent"],["HighlightAgent"],["StyleTransferAgent"],["TranscriptionAgent"],["TranslationAgent"],["AmbienceAgent","MusicAgent"],["AmbienceAgent","MusicAgent"],["AudioMixAgent"],["CompositorAgent"],["done"]],
        "anchor": "Cut a 90-second highlight reel from this Korean K-drama and convert it to an anime style, with English-Korean bilingual subtitles, a sweeping orchestral score, and dramatic indoor-room ambient sounds.",
        "variants": [
            "Cut a 75-second highlight reel from this Mandarin period drama and convert it to an ink-wash-painted style, with English-Mandarin bilingual subtitles, a soaring guzheng-and-strings score, and palace-courtyard ambient sounds.",
            "Cut a 60-second highlight reel from this Japanese yakuza thriller and convert it to a charcoal-sketch animated style, with English-Japanese bilingual subtitles, a tense taiko-and-strings score, and back-alley-rain ambient sounds.",
            "Cut a 90-second highlight reel from this Spanish telenovela and convert it to a Bollywood-poster art style, with English-Spanish bilingual subtitles, a passionate flamenco-fusion score, and bustling-cafeteria ambient sounds.",
            "Cut a 75-second highlight reel from this Vietnamese silat-action series and convert it to a dynamic comic-book style, with English-Vietnamese bilingual subtitles, a driving percussion-and-strings score, and bamboo-grove-and-river ambient sounds.",
        ],
    },
    {
        "name": "storytelling_203", "category": "storytelling",
        "expected_chain": [["IntakeImageAgent"],["BriefEnricherAgent"],["NarrationAgent"],["AmbienceAgent","IllustrationAgent","MusicAgent","NarratorAgent"],["AmbienceAgent","IllustrationAgent","MusicAgent","NarratorAgent"],["AmbienceAgent","IllustrationAgent","MusicAgent","NarratorAgent"],["AmbienceAgent","IllustrationAgent","MusicAgent","NarratorAgent"],["AudioMixAgent"],["TranslationAgent"],["CompositorAgent"],["done"]],
        "anchor": "Using this Sherpa mountaineer portrait as the protagonist, narrate an illustrated audiobook in Spanish about her solo Everest summit attempt, with high-altitude wind ambient sounds, a triumphant orchestral score, and English subtitles.",
        "variants": [
            "Using this Bedouin oud-player portrait as the protagonist, narrate an illustrated audiobook in Arabic about his caravan crossing a contested border, with desert-wind ambient sounds, a haunting oud-and-ney score, and English subtitles.",
            "Using this Yoruba market-mother portrait as the protagonist, narrate an illustrated audiobook in Yoruba about her tortoise-spirit visitor at the spice stall, with marketplace ambient sounds, a vibrant talking-drum score, and English subtitles.",
            "Using this Cossack horsewoman portrait as the protagonist, narrate an illustrated audiobook in Russian about her steppe-crossing in midwinter, with hoofbeat-and-wind ambient sounds, a sweeping balalaika-and-strings score, and English subtitles.",
            "Using this Sami reindeer-herder portrait as the protagonist, narrate an illustrated audiobook in Northern Sami about her aurora-night journey, with snow-crunch-and-arctic-wind ambient sounds, a meditative joik-and-drum score, and English subtitles.",
        ],
    },
    {
        "name": "bilingual_045", "category": "bilingual",
        "expected_chain": [["StoryAgent"],["ScreenplayAgent"],["KeyFrameAgent"],["VideoAgent"],["TranscriptionAgent"],["TranslationAgent"],["AmbienceAgent","MusicAgent"],["AmbienceAgent","MusicAgent"],["AudioMixAgent"],["CompositorAgent"],["done"]],
        "anchor": "Make a slow-paced literary mini-drama about an aging fisherman in a remote coastal village who returns home after a 30-year absence to find his childhood home swallowed by the rising sea, with English-Chinese bilingual subtitles, a melancholic cello score, and realistic ocean-wave and seabird ambient sounds.",
        "variants": [
            "Make a slow-paced period mini-drama about a 1920s Shanghai opera dresser caring for the costumes of a star who never returns from her last performance, with English-Mandarin bilingual subtitles, a wistful erhu-and-piano score, and theater-backstage ambient sounds.",
            "Make a slow-paced supernatural mini-drama about a Korean village shaman who rediscovers a forgotten ritual to call back the river-spirit, with Korean-English bilingual subtitles, a haunting daegeum-flute-and-strings score, and riverbank-and-night-cicadas ambient sounds.",
            "Make a slow-paced literary mini-drama about a Spanish lighthouse keeper who corresponds with a sailor she's never met for forty years, with Spanish-English bilingual subtitles, a wistful piano-and-cello score, and lonely-coast-wind-and-foghorn ambient sounds.",
            "Make a slow-paced rural-noir mini-drama about a Vietnamese rice-paddy elder who unearths the bones of a long-lost brother during a drought, with Vietnamese-English bilingual subtitles, a brooding dan-bau-and-string score, and dry-rice-paddy-and-distant-buffalo ambient sounds.",
        ],
    },
    {
        "name": "intake_img_055", "category": "intake_img",
        "expected_chain": [["IntakeImageAgent"],["BriefEnricherAgent"],["StoryAgent"],["ScreenplayAgent"],["KeyFrameAgent"],["VideoAgent"],["AmbienceAgent","MusicAgent","TranscriptionAgent"],["AmbienceAgent","MusicAgent","TranscriptionAgent"],["AmbienceAgent","MusicAgent","TranscriptionAgent"],["AudioMixAgent"],["CompositorAgent"],["done"]],
        "anchor": "Using this uploaded portrait of a young female Sherpa mountaineer, make a 90-second documentary-style mini-drama about her solo Everest summit attempt, with English subtitles, an inspiring orchestral score, and high-altitude wind and labored-breath ambient sounds.",
        "variants": [
            "Using this uploaded portrait of an elderly Cuban tobacco-roller, make a 90-second character-study mini-drama about his last day in the cigar factory before retirement, with English subtitles, a wistful Cuban-jazz score, and rolling-tobacco-and-radio ambient sounds.",
            "Using this uploaded portrait of a Kazakh eagle-huntress, make a 90-second period mini-drama about her first autumn-eagle hunt across the Altai range, with English subtitles, a sweeping kobyz-and-strings score, and steppe-wind-and-eagle-cry ambient sounds.",
            "Using this uploaded portrait of an Ethiopian coffee-ceremony elder, make a 90-second slow-paced mini-drama about the ritual she conducts on the eve of her granddaughter's wedding, with English subtitles, a meditative krar-and-vocal score, and incense-and-pouring-coffee ambient sounds.",
            "Using this uploaded portrait of a Sicilian deep-sea fisherman, make a 90-second character-study mini-drama about his solo night-fishing run during a sirocco storm, with English subtitles, a brooding mandolin-and-string score, and crashing-waves-and-creaking-boat ambient sounds.",
        ],
    },
    {
        "name": "intake_img_201", "category": "intake_img",
        "expected_chain": [["IntakeImageAgent"],["BriefEnricherAgent"],["StoryAgent"],["ScreenplayAgent"],["KeyFrameAgent"],["VideoAgent"],["TranscriptionAgent"],["TranslationAgent"],["AmbienceAgent"],["AudioMixAgent"],["CompositorAgent"],["done"]],
        "anchor": "Using this Russian lighthouse-keeper portrait, make a 90-second mini-drama about her last storm-watch night before retirement, with English-Russian bilingual subtitles and a raw, atmospheric storm-wind ambient sound throughout.",
        "variants": [
            "Using this Mongolian shepherd portrait, make a 90-second mini-drama about his lone winter trek to find a lost ewe, with English-Mongolian bilingual subtitles and a continuous icy-steppe-wind ambient sound.",
            "Using this Andalusian flamenco-dancer portrait, make a 90-second mini-drama about her late-night street performance after a private heartbreak, with English-Spanish bilingual subtitles and a continuous late-night-plaza-and-distant-fountain ambient sound.",
            "Using this Korean Buddhist nun portrait, make a 90-second mini-drama about her dawn meditation in an empty mountain temple, with English-Korean bilingual subtitles and a continuous mountain-temple-and-light-bird ambient sound.",
            "Using this Brazilian fisherman portrait, make a 90-second mini-drama about his pre-storm reading of the sea on a Bahia beach, with English-Portuguese bilingual subtitles and a continuous wind-and-rough-water ambient sound.",
        ],
    },
]

# Build final 200-case list
cases = []
for s in SHAPES:
    cases.append({
        "name": s["name"],
        "category": s["category"],
        "user_goal": s["anchor"],
        "expected_chain": s["expected_chain"],
    })
    for i, v in enumerate(s["variants"], 1):
        cases.append({
            "name": f"{s['name']}_v{i:02d}",
            "category": s["category"],
            "user_goal": v,
            "expected_chain": s["expected_chain"],
        })

# verify count
print(f"Total cases: {len(cases)}")
from collections import Counter
shape_counts = Counter(c["name"].rsplit("_v", 1)[0] if "_v" in c["name"] else c["name"] for c in cases)
print(f"Shapes: {len(shape_counts)}")

# length distribution
lens = [sum(1 for l in c['expected_chain'] if l != ['done']) for c in cases]
buckets = Counter()
for l in lens:
    if l <= 5: buckets['short(5)'] += 1
    elif l <= 8: buckets['medium(6-8)'] += 1
    else: buckets['long(9-11)'] += 1
print(f"Length distribution: {dict(buckets)}")

# write
out = Path('/home/zhendong_li/FrameWorkers/assistant_test/probe_cases_200.json')
out.write_text(json.dumps(cases, indent=2, ensure_ascii=False) + '\n')
print(f"Wrote {len(cases)} cases to {out}")
