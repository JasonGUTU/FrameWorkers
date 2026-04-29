"""x15 cr_music — 14x GRPO user_goal expansion (short briefs only).

Topic pool deliberately disjoint from SFT x15. Style explores sub-genres
where music is essential to the cinematic identity:
  - 80s nostalgia / coming-of-age scored
  - western with score
  - Ghibli-style cinematic w/ score
  - Bollywood-style musical drama
  - Korean melodrama
  - Latin telenovela / nuevo-cine
  - French Nouvelle Vague style
  - Japanese chambara w/ score
  - Steampunk w/ orchestral
  - Silent-cinema style w/ live score
  - Hong Kong wuxia / kung-fu w/ score
  - Soviet-era epic
  - Nordic minimalist
  - Black-and-white classic Hollywood
  - Concert-film moment scored
"""
from __future__ import annotations

USER_GOALS: list[str] = [
    # ── 80s nostalgia / coming-of-age scored (15) ─────────────────────────
    "Make me a 1-minute mini-drama about a teenage girl in 1986 cassette-walking down a suburban Florida street at dusk, scored with a synth-pop instrumental.",
    "I want a 45-second cinematic short of a teenage boy at an arcade in 1985 hitting a high score on a single machine, scored with chiptune-and-synth music.",
    "Create a 30-second piece where a teen girl assembles a mixtape on her bedroom floor in 1987, scored with a soft synth ballad.",
    "Produce a 2-minute mini-drama about a teen couple slow-dancing at a 1989 prom, scored with a power-ballad instrumental.",
    "Build a 45-second short of a teenage skateboarder cruising a sun-bleached 1986 Venice Beach, scored with a synth-rock instrumental.",
    "Render a 30-second cinematic clip of two friends bike-riding through autumn leaves in 1985, scored with a 1980s pastoral synth piece.",
    "Cook up a 1-minute mini-drama about a teen at her older sister's wedding in 1988, scored with a sparkly 1980s synth-pop ballad.",
    "Generate a 45-second short of a teen girl writing in a diary by lamplight in 1987, scored with a soft 1980s film-score synth piece.",
    "I'd like a 30-second cinematic piece of a teen at a 1985 roller rink, scored with a disco-meets-synth-pop instrumental.",
    "Make a 2-minute mini-drama of a teenage girl in 1989 picking out her first synthesizer in a music store, scored with an upbeat synth instrumental.",
    "Produce a 30-second short where a teen boy in 1986 polishes his first car under a garage light, scored with a yacht-rock-style instrumental.",
    "Build a 45-second cinematic piece about a teen girl in 1987 preparing for her first homecoming dance, scored with a synth-and-saxophone ballad.",
    "Create a 1-minute mini-drama of a teen choir-girl in 1988 rehearsing alone after school, scored with a soft synth-and-piano theme.",
    "Render a 30-second clip of a teen girl in 1985 unwrapping her first Walkman as a birthday gift, scored with a 1980s soft-rock instrumental.",
    "I want a 45-second cinematic piece of a teen at a 1989 video-rental store browsing the new releases shelf, scored with a synth-and-drums theme.",
    # ── western with score (15) ───────────────────────────────────────────
    "Make me a 1-minute western mini-drama about a sheriff cleaning his revolver on the porch of an empty saloon at dusk, scored with a low harmonica-and-strings theme.",
    "I want a 45-second cinematic clip of a young homesteader chopping firewood at sunrise with a child watching, scored with a slow acoustic-guitar-and-fiddle piece.",
    "Create a 30-second piece where a stagecoach driver waters his horses at a desert way station at noon, scored with a sweeping orchestral western theme.",
    "Produce a 2-minute mini-drama about a Cherokee scout leading a wagon party across a flooded creek, scored with a Native-American flute-and-drum piece.",
    "Build a 45-second short of a cowgirl repairing her saddle by lantern light in a quiet barn, scored with a delicate guitar-and-strings piece.",
    "Render a 30-second cinematic clip of a piano player picking out a tune in a rough mining-town saloon, scored with a barrelhouse-piano-and-fiddle piece.",
    "Cook up a 1-minute mini-drama where a prospector pans gold at a riverbank as a hawk circles overhead, scored with a contemplative harmonica-and-strings piece.",
    "Generate a 45-second western piece about a young schoolteacher unloading books from a wagon at her first frontier post, scored with a hopeful folk-violin theme.",
    "I'd like a 30-second short of a blacksmith shoeing a horse outside a sun-bleached general store, scored with a sweeping orchestral piece.",
    "Make a 2-minute mini-drama of a former Confederate cavalryman returning home to find his land now belongs to someone else, scored with a melancholic banjo-and-strings piece.",
    "Produce a 45-second cinematic piece where a Mexican vaquero ropes a runaway calf at golden hour, scored with a Mariachi-trumpet-and-strings score.",
    "Build a 30-second western short of a doctor riding through a dust storm to reach a sick child on a remote ranch, scored with a tense fiddle-and-strings piece.",
    "Create a 1-minute mini-drama where a frontier preacher reads a sermon to an empty pew on Sunday morning, scored with a lone harmonium-and-vocal hymn.",
    "Render a 45-second clip of a Pony-Express rider exchanging mailbags at a relay station in the rain, scored with a galloping orchestral percussion piece.",
    "I want a 30-second cinematic short of a sharpshooter cleaning her rifle by candlelight in a wagon at midnight, scored with a tense low-brass piece.",
    # ── Ghibli-style cinematic w/ score (15) ──────────────────────────────
    "Make me a 1-minute Ghibli-style mini-drama of a young witch and her cat tending a windowsill herb garden, scored with a Joe-Hisaishi-style piano-and-strings piece.",
    "I want a 45-second cinematic short of a young train conductor in a Studio-Ghibli-esque village, scored with a hopeful orchestral piano theme.",
    "Create a 30-second piece where a young apprentice cloud-painter touches up the morning sky, scored with a delicate Ghibli-style piano theme.",
    "Produce a 2-minute Ghibli-style mini-drama about a young girl and her grandmother hanging laundry on a windswept Italian terrace, scored with a Hisaishi-esque waltz.",
    "Build a 45-second short of a young apprentice baker delivering bread to a sleeping forest spirit, scored with a Ghibli-style flute-and-strings piece.",
    "Render a 30-second Ghibli-style clip of a young girl flying a hand-built kite over a Japanese countryside, scored with a hopeful piano-and-strings score.",
    "Cook up a 1-minute Ghibli-style mini-drama of a young postman cycling through a misty forest at dawn, scored with a piano-and-flute piece.",
    "Generate a 45-second short of a young firefly catcher releasing fireflies above a moonlit pond, scored with a Hisaishi-style piano-and-strings piece.",
    "I'd like a 30-second cinematic piece of a young apprentice clockmaker oiling tower-clock gears, scored with a delicate music-box theme.",
    "Make a 2-minute Ghibli-style mini-drama of a young girl crossing a stone bridge at dusk holding a paper lantern, scored with a Joe-Hisaishi-esque flute theme.",
    "Produce a 30-second short where a young girl plays a hand-organ for a courtyard of cats, scored with a Ghibli-style waltz.",
    "Build a 45-second Ghibli-style cinematic piece about a young girl walking through a hidden bath-house garden, scored with a Hisaishi-esque piano-and-bell motif.",
    "Create a 1-minute Ghibli-style mini-drama of a young deer-keeper feeding apples to a forest deer, scored with a soft string-and-flute piece.",
    "Render a 30-second Ghibli-style clip of a young girl arranging a tiny shrine of forest moss, scored with a delicate harp-and-strings piece.",
    "I want a 45-second Ghibli-style cinematic piece of a young apprentice mage feeding a single sparrow on a stone wall, scored with a soft piano-and-strings piece.",
    # ── Bollywood-style musical drama (12) ────────────────────────────────
    "Make me a 1-minute Bollywood-style mini-drama of a young woman in a Jaipur courtyard threading flowers into her hair, scored with a tabla-and-sitar piece.",
    "I want a 45-second cinematic short of a young couple stealing a glance across a Mumbai market, scored with a Bollywood-style strings-and-flute theme.",
    "Create a 30-second Bollywood-style piece of a young woman dancing in a monsoon-drenched courtyard, scored with a vocals-and-percussion Bollywood track.",
    "Produce a 2-minute Bollywood-style mini-drama of a young couple separating at a Delhi train station, scored with a tabla-and-strings ballad.",
    "Build a 45-second short of a young woman lighting diyas along a Diwali threshold, scored with a sitar-and-bansuri piece.",
    "Render a 30-second Bollywood-style cinematic clip of a young woman climbing the steps of a Rajasthani palace, scored with a sweeping orchestral-Bollywood theme.",
    "Cook up a 1-minute Bollywood-style mini-drama of a young couple meeting at a Bombay café in the rain, scored with a tabla-and-strings ballad.",
    "Generate a 45-second short of a young woman placing a bindi on her sister's forehead before a wedding, scored with a tabla-and-shehnai piece.",
    "I'd like a 30-second Bollywood-style cinematic piece of a young man writing a letter under a Mumbai overpass, scored with a strings-and-bansuri piece.",
    "Make a 2-minute Bollywood-style mini-drama of a young dancer rehearsing alone in a temple courtyard, scored with a mridangam-and-flute piece.",
    "Produce a 30-second short where a young woman runs through a Kerala tea plantation, scored with a violin-and-Carnatic-vocal piece.",
    "Build a 45-second Bollywood-style cinematic piece of a young man playing tabla on a Varanasi ghat at dawn, scored with a tabla-and-strings piece.",
    # ── Korean melodrama (10) ─────────────────────────────────────────────
    "Make me a 1-minute Korean-melodrama-style mini-drama of a young woman waiting in the rain at a Seoul bus stop, scored with a piano-and-cello K-drama piece.",
    "I want a 45-second cinematic short of a young man reading a letter in his small Seoul apartment, scored with a soft K-drama piano theme.",
    "Create a 30-second K-melodrama piece of a young couple meeting at a Hongdae street stall, scored with an acoustic guitar-and-strings piece.",
    "Produce a 2-minute Korean-melodrama mini-drama of a young woman visiting her grandfather at his Jeju seaside home, scored with a soft piano-and-strings theme.",
    "Build a 45-second short of a young chef preparing a single bowl of jjajangmyeon for her late mother's photograph, scored with a delicate K-drama piano piece.",
    "Render a 30-second K-melodrama-style cinematic clip of a young woman closing her late grandmother's hanok door for the last time, scored with a soft piano-and-cello piece.",
    "Cook up a 1-minute K-melodrama-style mini-drama of a young man writing an apology letter on a Seoul rooftop at sunset, scored with a soft piano-and-violin piece.",
    "Generate a 45-second short of a young couple sharing one umbrella across a Busan street in winter, scored with a strings-and-piano K-drama piece.",
    "I'd like a 30-second K-melodrama-style cinematic piece of a young woman waiting alone at a wedding reception, scored with a soft K-drama strings piece.",
    "Make a 2-minute K-melodrama-style mini-drama of a young couple meeting again on a Jeju beach after years apart, scored with a soaring K-drama orchestral theme.",
    # ── Latin telenovela / nuevo-cine (10) ────────────────────────────────
    "Produce a 1-minute Latin-telenovela-style mini-drama of a young Cuban widow lighting a candle for her husband, scored with a Cuban-bolero piece.",
    "I want a 45-second cinematic short of a young Mexican grandmother teaching her granddaughter to make tortillas, scored with a guitar-and-vocal mariachi piece.",
    "Create a 30-second telenovela-style piece of a young couple dancing salsa in a Havana courtyard, scored with a clave-and-trumpet salsa piece.",
    "Produce a 2-minute Latin-telenovela mini-drama about a young Dominican woman writing a letter to her sister abroad, scored with a Spanish-guitar bolero.",
    "Build a 45-second short of a young Argentine couple meeting in a Buenos Aires café, scored with a bandoneón-and-piano tango.",
    "Render a 30-second Latin-cinema clip of a young Peruvian dancer practicing marinera in a sunlit courtyard, scored with a marinera-band piece.",
    "Cook up a 1-minute Latin-telenovela mini-drama of a young Mexican father braiding his daughter's hair before her quinceañera, scored with a soft mariachi-violin piece.",
    "Generate a 45-second short of a young Colombian baker delivering bread to a small village square, scored with a cumbia-and-accordion piece.",
    "I'd like a 30-second Latin-cinema-style cinematic piece of a young Brazilian woman dancing samba on a Rio rooftop, scored with a samba-cuíca piece.",
    "Make a 2-minute Latin-telenovela-style mini-drama of a young Cuban grandfather teaching his grandson to play dominos, scored with a Cuban-son-cuban piece.",
    # ── French Nouvelle Vague style (10) ──────────────────────────────────
    "Make me a 1-minute French-New-Wave-style mini-drama of a young woman riding a Vespa through Saint-Germain-des-Prés, scored with a jazz-clarinet-and-piano piece.",
    "I want a 45-second cinematic short of a young couple sharing an espresso at a Paris café terrace, scored with an accordion-and-strings musette.",
    "Create a 30-second Nouvelle-Vague-style piece of a young man writing in his notebook on a Pont-des-Arts bench, scored with a soft jazz-piano theme.",
    "Produce a 2-minute French-New-Wave-style mini-drama of a young couple walking along the Seine at midnight, scored with a smoky jazz-trumpet-and-piano piece.",
    "Build a 45-second short of a young woman browsing a Left-Bank bookshop in pouring rain, scored with a jazz-saxophone-and-piano piece.",
    "Render a 30-second cinematic clip of a young man reading Sartre on a Saint-Sulpice bench, scored with a soft jazz-trio piece.",
    "Cook up a 1-minute Nouvelle-Vague-style mini-drama of a young woman crossing a zebra crossing on the Champs-Élysées at dawn, scored with a brushed-snare jazz piece.",
    "Generate a 45-second short of a young couple eating crepes from a Marais stand, scored with an accordion-and-piano musette.",
    "I'd like a 30-second French-New-Wave-style cinematic piece of a young man hailing a taxi outside a Pigalle club at 3 AM, scored with a smoky jazz-saxophone piece.",
    "Make a 2-minute French-New-Wave-style mini-drama of a young woman waiting at a Montparnasse cinema entrance, scored with a soft jazz-piano-and-clarinet piece.",
    # ── Japanese chambara / samurai w/ score (10) ─────────────────────────
    "Make me a 1-minute Japanese chambara-style mini-drama of a young samurai polishing his katana in a sunlit teahouse, scored with a shakuhachi-and-koto piece.",
    "I want a 45-second cinematic short of a young geisha tying her obi by candlelight, scored with a shamisen-and-koto piece.",
    "Create a 30-second chambara-style piece of two samurai bowing before a duel at dawn, scored with a taiko-and-flute piece.",
    "Produce a 2-minute Japanese-chambara mini-drama of a young ronin walking a pine-lined road in autumn, scored with a shakuhachi-and-strings piece.",
    "Build a 45-second short of a young samurai writing a haiku at his writing desk, scored with a soft koto-and-shakuhachi piece.",
    "Render a 30-second chambara-style clip of a young samurai sharpening her blade by lamplight, scored with a shakuhachi piece.",
    "Cook up a 1-minute mini-drama of a young samurai teaching her younger brother kendo basics in a wooden dojo, scored with a taiko-and-shakuhachi piece.",
    "Generate a 45-second short of a young samurai walking a misty mountain path at dawn, scored with a shakuhachi-and-bamboo-flute piece.",
    "I'd like a 30-second chambara-style cinematic piece of a young samurai sitting in seiza before a single tatami flame, scored with a koto-and-shakuhachi piece.",
    "Make a 2-minute Japanese-chambara mini-drama about a young female samurai delivering a sealed scroll across a snowy mountain pass, scored with a koto-and-strings piece.",
    # ── steampunk w/ orchestral (10) ──────────────────────────────────────
    "Make me a 1-minute steampunk mini-drama about a young engineer cranking a brass-and-copper airship engine, scored with an orchestral-and-clockwork-percussion piece.",
    "I want a 45-second cinematic short of a young inventor calibrating a brass-armatured prosthetic, scored with a steampunk-orchestral piece.",
    "Create a 30-second steampunk piece where a young watchmaker assembles a clockwork bird, scored with a music-box-and-orchestra piece.",
    "Produce a 2-minute steampunk mini-drama about a young captain piloting a brass dirigible through alpine clouds, scored with an orchestral-and-pipe-organ piece.",
    "Build a 45-second short of a young inventor lighting a Tesla coil in her London workshop, scored with a steampunk-orchestral piece.",
    "Render a 30-second steampunk-style clip of a young pilot starting a brass-and-leather diving suit's pumps, scored with an orchestral-and-brass piece.",
    "Cook up a 1-minute steampunk mini-drama of a young scientist activating a brass-and-glass time-machine prototype, scored with a clockwork-orchestra piece.",
    "Generate a 45-second short of a young dirigible navigator setting course over a steam-powered London, scored with a brass-and-strings steampunk piece.",
    "I'd like a 30-second steampunk cinematic piece of a young engineer assembling a clockwork chess piece, scored with a music-box-and-strings piece.",
    "Make a 2-minute steampunk mini-drama of a young inventor unveiling a brass automaton at a London exhibition, scored with a brass-and-pipe-organ piece.",
    # ── Hong Kong wuxia / kung-fu w/ score (10) ───────────────────────────
    "Make me a 1-minute wuxia mini-drama of a young swordswoman walking a bamboo-grove path at dusk, scored with an erhu-and-pipa piece.",
    "I want a 45-second cinematic short of a young kung-fu student practicing forms on a temple roof at dawn, scored with an erhu-and-percussion piece.",
    "Create a 30-second wuxia piece of a young master pouring tea for a visiting student, scored with a guzheng-and-erhu piece.",
    "Produce a 2-minute wuxia-style mini-drama of a young swordsman walking across a frosted moonlit lake, scored with a soaring erhu-and-strings piece.",
    "Build a 45-second short of a young kung-fu student lighting incense for her late master, scored with a soft erhu-and-flute piece.",
    "Render a 30-second wuxia-style clip of a young swordswoman climbing a temple's stone steps at dawn, scored with an orchestral-erhu piece.",
    "Cook up a 1-minute wuxia mini-drama of a young master practicing calligraphy under a courtyard lantern, scored with a guzheng-and-flute piece.",
    "Generate a 45-second short of a young kung-fu student sweeping the temple courtyard at dawn, scored with an erhu-and-bamboo-flute piece.",
    "I'd like a 30-second wuxia-style cinematic piece of a young swordswoman feeding a wounded sparrow on a temple wall, scored with a delicate guzheng piece.",
    "Make a 2-minute wuxia-style mini-drama of a young swordswoman walking through a grove of cherry blossoms at dawn, scored with a soaring erhu-and-orchestra piece.",
    # ── Soviet-era epic / Nordic minimalist / silent / black-white (8) ────
    "Produce a 1-minute Soviet-era-style mini-drama of a young farmer plowing a field at dawn, scored with a balalaika-and-strings piece.",
    "I want a 45-second Nordic-minimalist mini-drama of a young woman crossing a frozen Norwegian fjord by ferry, scored with a sparse piano-and-string piece.",
    "Create a 30-second silent-cinema-style piece of a young couple meeting at a Charlie-Chaplin-style park bench, scored with a 1920s honky-tonk piano piece.",
    "Produce a 2-minute black-and-white classic-Hollywood-style mini-drama of a young diva walking onto a packed Hollywood-Bowl stage, scored with a 1940s big-band piece.",
    "Build a 45-second Soviet-style short of a young factory worker watching a shift change at a Leningrad steel mill, scored with a sweeping Soviet-orchestral piece.",
    "Render a 30-second Nordic-minimalist cinematic clip of a young woman lighting a single candle in a Stockholm apartment, scored with a sparse piano piece.",
    "Cook up a 1-minute black-and-white-classic mini-drama of a young chanteuse stepping onto a New York jazz-club stage in 1939, scored with a swinging big-band piece.",
    "Generate a 45-second silent-cinema-style short of a young Buster-Keaton-esque clerk chasing a runaway hat down a city street, scored with a 1920s ragtime piano piece.",
    # ── modern dance / urban performance w/ score (15) ────────────────────
    "Make me a 1-minute mini-drama about a young krump dancer rehearsing in a downtown LA studio at dusk, scored with an urban hip-hop instrumental.",
    "I want a 45-second cinematic short of a young house dancer leading a Paris underground rave, scored with a deep-house BGM.",
    "Create a 30-second piece of a young voguer in a Harlem ballroom strikes her final pose, scored with a ballroom-house anthem.",
    "Produce a 2-minute mini-drama about a young tutting dancer practicing geometry on a Brooklyn rooftop, scored with a synth-electronic piece.",
    "Build a 45-second short of a young popper performing solo at a downtown LA showcase, scored with a funk-electronic piece.",
    "Render a 30-second cinematic clip of a young liquid-dancer at a Berlin techno festival, scored with a Berlin-techno piece.",
    "Cook up a 1-minute mini-drama of a young waacking dancer practicing in a 1970s-themed Tokyo studio, scored with a 1970s disco-funk piece.",
    "Generate a 45-second short of a young tap dancer performing in a Seattle subway station, scored with a swing-jazz piece.",
    "I'd like a 30-second cinematic piece of a young Lindy-hop couple at a New Orleans jazz hall, scored with a Lindy-hop swing piece.",
    "Make a 30-second clip of a young Chicago footwork dancer at a basement battle, scored with a Chicago-footwork piece.",
    "Produce a 2-minute mini-drama about a young Jersey-club dancer leading a high-school crew, scored with a Jersey-club piece.",
    "Build a 45-second short of a young memphis-jookin dancer floating on a downtown Memphis sidewalk, scored with a Memphis-jookin piece.",
    "Create a 30-second piece of a young NewJack-swing dancer leading a 1990s-style block party, scored with a New-Jack-swing piece.",
    "Render a 1-minute mini-drama of a young dancehall dancer leading a Kingston yard party, scored with a dancehall-reggae piece.",
    "I want a 45-second cinematic piece of a young afrobeats dancer leading a Lagos rooftop practice, scored with an afrobeats piece.",
    # ── political-thriller / Cold-War (10) ─────────────────────────────────
    "Make me a 1-minute Cold-War mini-drama of a young CIA analyst decoding a Soviet intercept in a Vienna safe-house, scored with a tense low-strings piece.",
    "I want a 45-second cinematic short of a young KGB courier slipping a microfilm into a Berlin park bench, scored with a tense electronic-pulse piece.",
    "Create a 30-second piece of a young East-Berlin defector crossing Checkpoint Charlie at midnight, scored with a tense rising-strings piece.",
    "Produce a 2-minute mini-drama of a young Stasi linguist translating a Western broadcast at a Leipzig listening post, scored with a tense low-brass piece.",
    "Build a 45-second short of a young Mossad operative tying off a final cable at a Paris drop, scored with a tense electronic-orchestra piece.",
    "Render a 30-second cinematic clip of a young UN diplomat passing a coded note at a Geneva summit, scored with a tense piano-and-strings piece.",
    "Cook up a 1-minute mini-drama of a young CIA analyst destroying classified documents in a Saigon basement, scored with a tense low-strings piece.",
    "Generate a 45-second short of a young double agent meeting her handler in a quiet Lisbon café, scored with a tense piano-and-cello piece.",
    "I'd like a 30-second cinematic piece of a young Mossad cryptographer cracking a final code at midnight, scored with a tense electronic-pulse piece.",
    "Make a 30-second clip of a young SDECE operative taking a final glance at a Paris gendarmerie post, scored with a tense piano-and-cello piece.",
]

assert len(set(USER_GOALS)) == len(USER_GOALS), "duplicate USER_GOALS within file"
