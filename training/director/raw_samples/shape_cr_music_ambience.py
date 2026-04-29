"""Shape: cr_music_ambience —
    Story → Screenplay → KeyFrame → Video → Music → Ambience → AudioMix → Compositor.

Cinematic mini-drama with BOTH music AND ambient sound.
"""
from __future__ import annotations

SAMPLES: list[dict] = [
    {
        "user_goal": "Make a historical war-epic animated drama about a Three Kingdoms general who leads his troops across a treacherous mountain pass to lift a siege, with orchestral battle music and mountain-wind ambient sounds.",
        "rationale": (
            "Three Kingdoms war epic + orchestral battle music + mountain-wind ambient. "
            "Chain: Story → Screenplay → KeyFrame → Video → Music → Ambience → AudioMix → "
            "Compositor. Reject Transcription (no subtitle), VideoAnalysis (no upload)."
        ),
        "intents": [
            "Write the Three Kingdoms story of the general leading troops across the pass.",
            "Break the story into war-epic scenes with siege-lift climax.",
            "Design key frames for the mountain pass and troop movement.",
            "Render motion-video clips preserving war-epic continuity.",
            "Compose an orchestral battle BGM fitting the Three Kingdoms epic.",
            "Generate mountain-wind ambient (high-altitude wind, distant banners).",
            "Mix the orchestral BGM, mountain ambient, and baked-in audio.",
            "Compose the final war-epic mini-drama with all layers assembled.",
        ],
    },
    {
        "user_goal": "Make a sci-fi space-exploration animated drama where astronauts discover an ancient alien signal coming from a dead star, with cosmic orchestral music and spaceship ambient sounds.",
        "rationale": (
            "Sci-fi space-exploration drama + cosmic orchestral + spaceship ambient."
        ),
        "intents": [
            "Write the sci-fi story of astronauts discovering the alien signal.",
            "Break the story into space-exploration scenes building to the signal reveal.",
            "Design key frames for the spaceship and dead-star signal.",
            "Render motion-video clips preserving sci-fi continuity.",
            "Compose a cosmic orchestral BGM fitting the space-exploration scale.",
            "Generate spaceship ambient (system hums, distant alarms, radio chatter).",
            "Mix the orchestral BGM, spaceship ambient, and baked-in audio.",
            "Compose the final sci-fi mini-drama with all layers assembled.",
        ],
    },
    {
        "user_goal": "Make a pirate-adventure mini-drama where the captain's daughter takes over her dead father's ship to hunt the rival crew, with adventure music and ocean-wind ambient sounds.",
        "rationale": (
            "Pirate-revenge daughter-captain drama + adventure music + ocean-wind ambient."
        ),
        "intents": [
            "Write the pirate story of the daughter taking over her father's ship.",
            "Break the story into pirate-adventure scenes with revenge beats.",
            "Design key frames for the pirate ship and daughter-captain.",
            "Render motion-video clips preserving pirate-adventure continuity.",
            "Compose an adventure BGM fitting the pirate-revenge tone.",
            "Generate ocean-wind ambient (wind, sail creaks, seagulls).",
            "Mix the adventure BGM, ocean ambient, and baked-in audio.",
            "Compose the final pirate mini-drama with all layers assembled.",
        ],
    },
    {
        "user_goal": "Make a fantasy drama about a young dragon-rider chosen by the last dragon egg hatching in a mountain monastery, with epic fantasy music and mountain monastery ambient sounds.",
        "rationale": (
            "Dragon-rider fantasy drama + epic fantasy music + monastery ambient."
        ),
        "intents": [
            "Write the dragon-rider story of the last dragon egg hatching.",
            "Break the story into dragon-bond-and-quest scenes.",
            "Design key frames for the dragon, rider, and mountain monastery.",
            "Render motion-video clips preserving dragon-rider continuity.",
            "Compose an epic fantasy BGM fitting the dragon-rider origin.",
            "Generate mountain-monastery ambient (distant bells, wind chimes, chanting).",
            "Mix the fantasy BGM, monastery ambient, and baked-in audio.",
            "Compose the final dragon-rider mini-drama with all layers assembled.",
        ],
    },
    {
        "user_goal": "Make a zombie-survival mini-drama where a small-town nurse leads her students to safety through overgrown streets, with tense thriller music and creepy city ambient sounds.",
        "rationale": (
            "Zombie-survival drama + tense thriller + creepy city ambient."
        ),
        "intents": [
            "Write the zombie-survival story of the nurse leading students to safety.",
            "Break the story into survival scenes across the overgrown town.",
            "Design key frames for the overgrown streets and survivor group.",
            "Render motion-video clips preserving zombie-survival continuity.",
            "Compose a tense thriller BGM fitting the zombie-survival tone.",
            "Generate creepy city ambient (distant moans, broken glass crunches, sirens).",
            "Mix the thriller BGM, city ambient, and baked-in audio.",
            "Compose the final zombie mini-drama with all layers assembled.",
        ],
    },
    {
        "user_goal": "Make a medieval-fantasy mini-drama about a young knight defending a frontier fort against a siege, with brass-and-choir battle music and siege-camp ambient.",
        "rationale": (
            "Knight-and-frontier-fort siege + brass-and-choir + siege-camp ambient."
        ),
        "intents": [
            "Write the knight's story of defending the frontier fort.",
            "Break the story into siege-defense scenes.",
            "Design key frames for the frontier fort and siege camp.",
            "Render motion-video clips preserving the medieval siege continuity.",
            "Compose a brass-and-choir battle BGM fitting the siege tone.",
            "Generate siege-camp ambient (distant horn calls, catapult creaks, horses).",
            "Mix the battle BGM, siege ambient, and baked-in audio.",
            "Compose the final knight mini-drama with all layers assembled.",
        ],
    },
    {
        "user_goal": "Make a horror mini-drama about a young exorcist facing her first possession case in a storm-locked convent, with a dark choir BGM and stormy-convent ambient.",
        "rationale": (
            "Young-exorcist first-case drama + dark choir BGM + stormy-convent ambient."
        ),
        "intents": [
            "Write the young-exorcist story of her first possession case.",
            "Break the story into horror-convent scenes.",
            "Design key frames for the storm-locked convent and exorcism visuals.",
            "Render motion-video clips preserving horror continuity.",
            "Compose a dark choir BGM fitting the exorcism horror.",
            "Generate stormy-convent ambient (thunder, howling wind, distant chants).",
            "Mix the choir BGM, convent ambient, and baked-in audio.",
            "Compose the final exorcist mini-drama with all layers assembled.",
        ],
    },
    {
        "user_goal": "Make a western mini-drama about a retired gunslinger protecting a stagecoach through bandit country, with a harmonica-western BGM and prairie-wind ambient.",
        "rationale": (
            "Retired-gunslinger stagecoach drama + harmonica-western BGM + prairie-wind ambient."
        ),
        "intents": [
            "Write the retired-gunslinger's story of protecting the stagecoach.",
            "Break the story into western-stagecoach scenes.",
            "Design key frames for the stagecoach and bandit country.",
            "Render motion-video clips preserving western continuity.",
            "Compose a harmonica-western BGM fitting the gunslinger drama.",
            "Generate prairie-wind ambient (wind, distant coyotes, horse hooves).",
            "Mix the harmonica BGM, prairie ambient, and baked-in audio.",
            "Compose the final western mini-drama with all layers assembled.",
        ],
    },
    {
        "user_goal": "Make a cyberpunk mini-drama about a hacker infiltrating a corporate arcology to rescue her kidnapped sister, with synthwave music and arcology-interior ambient.",
        "rationale": (
            "Hacker-rescue cyberpunk drama + synthwave music + arcology ambient."
        ),
        "intents": [
            "Write the cyberpunk story of the hacker rescuing her sister.",
            "Break the story into arcology-infiltration scenes.",
            "Design key frames for the corporate arcology interior.",
            "Render motion-video clips preserving cyberpunk continuity.",
            "Compose a synthwave BGM fitting the cyberpunk rescue tone.",
            "Generate arcology-interior ambient (drone hum, distant elevator, data-hum).",
            "Mix the synthwave BGM, arcology ambient, and baked-in audio.",
            "Compose the final cyberpunk mini-drama with all layers assembled.",
        ],
    },
    {
        "user_goal": "Make a noir mini-drama about a jazz singer who becomes a police informant to catch a mob boss, with a smoky jazz BGM and noir-club ambient.",
        "rationale": (
            "Jazz-singer informant drama + smoky jazz BGM + noir-club ambient."
        ),
        "intents": [
            "Write the jazz-singer informant story.",
            "Break the story into noir-club informant scenes.",
            "Design key frames for the noir club and singer's stage presence.",
            "Render motion-video clips preserving noir continuity.",
            "Compose a smoky jazz BGM fitting the noir tone.",
            "Generate noir-club ambient (glass clinks, hushed chatter, distant laughter).",
            "Mix the jazz BGM, club ambient, and baked-in audio.",
            "Compose the final noir mini-drama with all layers assembled.",
        ],
    },
    {
        "user_goal": "Make a fantasy mini-drama about a desert-nomad princess reclaiming her oasis home from a cult of sand-sorcerers, with Middle-Eastern fusion music and desert-oasis ambient.",
        "rationale": (
            "Desert-nomad princess drama + Middle-Eastern fusion music + desert-oasis ambient."
        ),
        "intents": [
            "Write the desert-nomad princess story of reclaiming her oasis home.",
            "Break the story into desert-princess scenes with sand-sorcerer combat.",
            "Design key frames for the oasis and desert sorcery.",
            "Render motion-video clips preserving the desert-fantasy continuity.",
            "Compose a Middle-Eastern fusion BGM fitting the desert-princess tone.",
            "Generate desert-oasis ambient (water, distant birds, palm rustles, wind).",
            "Mix the fusion BGM, oasis ambient, and baked-in audio.",
            "Compose the final desert mini-drama with all layers assembled.",
        ],
    },
    {
        "user_goal": "Make a gothic-horror mini-drama about a young bride realizing her new husband's castle is haunted by his ten previous wives, with a haunting pipe-organ BGM and castle-crypt ambient.",
        "rationale": (
            "Gothic-horror bride drama + haunting pipe-organ BGM + castle-crypt ambient."
        ),
        "intents": [
            "Write the gothic-horror bride story of the haunted husband's castle.",
            "Break the story into gothic-horror castle scenes.",
            "Design key frames for the castle and ghost-wives.",
            "Render motion-video clips preserving gothic-horror continuity.",
            "Compose a haunting pipe-organ BGM fitting the gothic-horror tone.",
            "Generate castle-crypt ambient (distant whispers, dripping water, metal creaks).",
            "Mix the organ BGM, crypt ambient, and baked-in audio.",
            "Compose the final gothic-horror mini-drama with all layers assembled.",
        ],
    },
    {
        "user_goal": "Make a martial-arts mini-drama about a monk-turned-fugitive defending a village from bandits, with traditional erhu-and-drum BGM and village-attack ambient.",
        "rationale": (
            "Monk-fugitive village-defender drama + erhu-and-drum BGM + village-attack ambient."
        ),
        "intents": [
            "Write the monk-fugitive story of defending the village from bandits.",
            "Break the story into martial-arts defense scenes.",
            "Design key frames for the monk, village, and bandit encounters.",
            "Render motion-video clips preserving martial-arts continuity.",
            "Compose a traditional erhu-and-drum BGM fitting the martial-arts tone.",
            "Generate village-attack ambient (shouts, hoof-beats, clashing steel).",
            "Mix the erhu BGM, village ambient, and baked-in audio.",
            "Compose the final martial-arts mini-drama with all layers assembled.",
        ],
    },
    {
        "user_goal": "Make a period mini-drama about a Scottish Highlands heir reclaiming her family's estate from English occupiers, with a stirring bagpipe BGM and Highlands ambient.",
        "rationale": (
            "Scottish Highlands heir drama + stirring bagpipe BGM + Highlands ambient."
        ),
        "intents": [
            "Write the Scottish-heir story of reclaiming her family estate.",
            "Break the story into Highlands-reclaim scenes.",
            "Design key frames for the Highlands and estate.",
            "Render motion-video clips preserving the Highlands-period continuity.",
            "Compose a stirring bagpipe BGM fitting the Scottish-heir tone.",
            "Generate Highlands ambient (wind over heather, distant stags, sheep bleats).",
            "Mix the bagpipe BGM, Highlands ambient, and baked-in audio.",
            "Compose the final Highlands mini-drama with all layers assembled.",
        ],
    },
    {
        "user_goal": "Make a sci-fi post-apocalyptic mini-drama about a scavenger finding the last functioning library in the ruins, with a melancholic ambient-piano BGM and ruined-city ambient.",
        "rationale": (
            "Scavenger-library post-apocalyptic drama + melancholic ambient-piano + ruined-city "
            "ambient."
        ),
        "intents": [
            "Write the scavenger's story of finding the last functioning library.",
            "Break the story into scavenger-discovery scenes.",
            "Design key frames for the ruined city and intact library.",
            "Render motion-video clips preserving post-apocalyptic continuity.",
            "Compose a melancholic ambient-piano BGM fitting the post-apocalyptic tone.",
            "Generate ruined-city ambient (wind through ruins, distant rubble, occasional fauna).",
            "Mix the piano BGM, city ambient, and baked-in audio.",
            "Compose the final scavenger mini-drama with all layers assembled.",
        ],
    },
    {
        "user_goal": "Make a coming-of-age mini-drama about a country girl moving to 1950s New York to become a jazz pianist, with a swinging 1950s-jazz BGM and 1950s-NY ambient.",
        "rationale": (
            "Country-girl 1950s NY jazz-pianist drama + swinging 1950s-jazz + 1950s-NY ambient."
        ),
        "intents": [
            "Write the country-girl's story of becoming a 1950s NY jazz pianist.",
            "Break the story into 1950s-NY coming-of-age scenes.",
            "Design key frames for 1950s NY streets and jazz clubs.",
            "Render motion-video clips preserving the 1950s continuity.",
            "Compose a swinging 1950s-jazz BGM fitting the pianist's rise.",
            "Generate 1950s-NY ambient (distant horns, trolley bells, crowd chatter).",
            "Mix the jazz BGM, 1950s ambient, and baked-in audio.",
            "Compose the final 1950s mini-drama with all layers assembled.",
        ],
    },
    {
        "user_goal": "Make an adventure mini-drama about an Arctic explorer and her sled dogs racing to reach the pole before her rival, with a stirring expedition-orchestra BGM and Arctic ambient.",
        "rationale": (
            "Arctic-explorer rival-race drama + stirring expedition-orchestra + Arctic ambient."
        ),
        "intents": [
            "Write the Arctic-explorer story of racing her rival to the pole.",
            "Break the story into Arctic expedition scenes.",
            "Design key frames for the Arctic landscape and sled-dog team.",
            "Render motion-video clips preserving the Arctic-adventure continuity.",
            "Compose a stirring expedition-orchestra BGM fitting the Arctic race.",
            "Generate Arctic ambient (howling wind, ice cracks, distant dog pants).",
            "Mix the orchestra BGM, Arctic ambient, and baked-in audio.",
            "Compose the final Arctic mini-drama with all layers assembled.",
        ],
    },
    {
        "user_goal": "Make a heist mini-drama about a getaway driver doing her one last job across the city in a stolen muscle car, with a gritty rock-and-roll BGM and night-city-traffic ambient.",
        "rationale": (
            "Getaway-driver last-job drama + gritty rock-and-roll + night-city-traffic ambient."
        ),
        "intents": [
            "Write the getaway-driver's last-job story.",
            "Break the story into heist-getaway scenes across the city.",
            "Design key frames for the muscle car and night city.",
            "Render motion-video clips preserving the heist tension.",
            "Compose a gritty rock-and-roll BGM fitting the getaway-driver tone.",
            "Generate night-city-traffic ambient (traffic, sirens, engine revs).",
            "Mix the rock BGM, traffic ambient, and baked-in audio.",
            "Compose the final heist mini-drama with all layers assembled.",
        ],
    },
    {
        "user_goal": "Make a period mini-drama about a Roaring-20s speakeasy singer caught between the mob and the Feds, with a raucous ragtime BGM and speakeasy ambient.",
        "rationale": (
            "Roaring-20s speakeasy singer drama + raucous ragtime BGM + speakeasy ambient."
        ),
        "intents": [
            "Write the Roaring-20s speakeasy-singer drama.",
            "Break the story into speakeasy scenes with mob and Fed tension.",
            "Design key frames for the speakeasy stage and back rooms.",
            "Render motion-video clips preserving the Roaring-20s continuity.",
            "Compose a raucous ragtime BGM fitting the speakeasy tone.",
            "Generate speakeasy ambient (glass clinks, hushed laughter, distant piano).",
            "Mix the ragtime BGM, speakeasy ambient, and baked-in audio.",
            "Compose the final speakeasy mini-drama with all layers assembled.",
        ],
    },
    {
        "user_goal": "Make a fantasy mini-drama about a young tribal shaman communing with her ancestors during a blood-moon ritual, with a ceremonial drum-and-chant BGM and sacred-grove ambient.",
        "rationale": (
            "Young-shaman blood-moon ritual + ceremonial drum-and-chant BGM + sacred-grove "
            "ambient."
        ),
        "intents": [
            "Write the young-shaman story of the blood-moon ancestral ritual.",
            "Break the story into shaman-ritual scenes.",
            "Design key frames for the sacred grove and shaman's vision.",
            "Render motion-video clips preserving the tribal-fantasy continuity.",
            "Compose a ceremonial drum-and-chant BGM fitting the blood-moon ritual.",
            "Generate sacred-grove ambient (wind through leaves, distant owls, firelight crackle).",
            "Mix the drum BGM, grove ambient, and baked-in audio.",
            "Compose the final shaman mini-drama with all layers assembled.",
        ],
    },
    {
        "user_goal": "Make a thriller mini-drama about a journalist investigating a remote mining town where the miners keep disappearing, with a tense ambient-industrial BGM and mining-town ambient.",
        "rationale": (
            "Journalist mining-town disappearances drama + tense ambient-industrial (music) + "
            "mining-town ambient."
        ),
        "intents": [
            "Write the journalist's story of the mining-town disappearances.",
            "Break the story into mining-town thriller scenes.",
            "Design key frames for the mining town and eerie mine shafts.",
            "Render motion-video clips preserving the thriller mood.",
            "Compose a tense ambient-industrial BGM fitting the mining-town thriller.",
            "Generate mining-town ambient (distant drills, wind, grinding metal).",
            "Mix the industrial BGM, mining ambient, and baked-in audio.",
            "Compose the final mining-town mini-drama with all layers assembled.",
        ],
    },
    {
        "user_goal": "Make a period Japanese mini-drama about a Meiji-era samurai's daughter training as the first woman warrior in her clan, with a traditional Japanese-orchestra BGM and Meiji-dojo ambient.",
        "rationale": (
            "Meiji-era samurai's-daughter drama + traditional Japanese-orchestra + Meiji-dojo "
            "ambient."
        ),
        "intents": [
            "Write the Meiji samurai's-daughter story.",
            "Break the story into Meiji-dojo training scenes.",
            "Design key frames for the Meiji-era dojo and samurai household.",
            "Render motion-video clips preserving the Meiji-period continuity.",
            "Compose a traditional Japanese-orchestra BGM fitting the Meiji samurai tone.",
            "Generate Meiji-dojo ambient (wooden floor creaks, sword clashes, shouted calls).",
            "Mix the Japanese BGM, dojo ambient, and baked-in audio.",
            "Compose the final Meiji mini-drama with all layers assembled.",
        ],
    },
    {
        "user_goal": "Make a modern mini-drama about a storm-chaser photographing once-in-a-century supercells across the plains, with a sweeping cinematic BGM and tornado ambient.",
        "rationale": (
            "Storm-chaser photographer drama + sweeping cinematic BGM + tornado ambient."
        ),
        "intents": [
            "Write the storm-chaser's story of chasing century supercells.",
            "Break the story into storm-chase scenes across the plains.",
            "Design key frames for the tornadoes and storm-chase vehicle.",
            "Render motion-video clips preserving the storm-chase intensity.",
            "Compose a sweeping cinematic BGM fitting the storm-chaser tone.",
            "Generate tornado ambient (howling wind, distant thunder, debris whistling).",
            "Mix the cinematic BGM, tornado ambient, and baked-in audio.",
            "Compose the final storm-chaser mini-drama with all layers assembled.",
        ],
    },
    {
        "user_goal": "Make a fantasy mini-drama about a sea-witch helping lost sailors find their way home, with a haunting seaborne-celtic BGM and stormy-ocean ambient.",
        "rationale": (
            "Sea-witch lost-sailors drama + haunting seaborne-celtic BGM + stormy-ocean ambient."
        ),
        "intents": [
            "Write the sea-witch's story of helping lost sailors home.",
            "Break the story into sea-witch fantasy scenes.",
            "Design key frames for the sea-witch and her stormy coast.",
            "Render motion-video clips preserving the sea-witch fantasy tone.",
            "Compose a haunting seaborne-celtic BGM fitting the sea-witch lore.",
            "Generate stormy-ocean ambient (waves crashing, wind, distant thunder).",
            "Mix the celtic BGM, ocean ambient, and baked-in audio.",
            "Compose the final sea-witch mini-drama with all layers assembled.",
        ],
    },
    {
        "user_goal": "Make a contemporary mini-drama about a young woman moving to a remote island lighthouse to write her first novel, with a gentle indie-folk BGM and coastal-lighthouse ambient.",
        "rationale": (
            "Young-novelist lighthouse drama + gentle indie-folk BGM + coastal-lighthouse "
            "ambient."
        ),
        "intents": [
            "Write the young-novelist's story of moving to the lighthouse.",
            "Break the story into lighthouse-writing scenes.",
            "Design key frames for the lighthouse and novelist's notebook.",
            "Render motion-video clips preserving the lighthouse-solitude continuity.",
            "Compose a gentle indie-folk BGM fitting the young-novelist tone.",
            "Generate coastal-lighthouse ambient (waves, seagulls, distant fog-horn).",
            "Mix the folk BGM, lighthouse ambient, and baked-in audio.",
            "Compose the final lighthouse mini-drama with all layers assembled.",
        ],
    },
    {
        "user_goal": "Make a mystery mini-drama about a Victorian clairvoyant helping Scotland Yard solve a series of society-lady murders, with a chamber-gothic BGM and foggy-London ambient.",
        "rationale": (
            "Victorian clairvoyant murder-mystery drama + chamber-gothic BGM + foggy-London "
            "ambient."
        ),
        "intents": [
            "Write the Victorian-clairvoyant story of solving the society-lady murders.",
            "Break the story into clairvoyant mystery scenes across London.",
            "Design key frames for Victorian London streets and séance parlors.",
            "Render motion-video clips preserving Victorian mystery continuity.",
            "Compose a chamber-gothic BGM fitting the Victorian-clairvoyant tone.",
            "Generate foggy-London ambient (distant carriages, horse clops, fog-muffled cries).",
            "Mix the chamber BGM, London ambient, and baked-in audio.",
            "Compose the final clairvoyant mini-drama with all layers assembled.",
        ],
    },
    {
        "user_goal": "Make a sci-fi mini-drama about a solo mars-colony biologist when her life-support starts to fail, with a tense ambient-electronica BGM and mars-habitat ambient.",
        "rationale": (
            "Mars-colony biologist life-support-failure drama + tense ambient-electronica + "
            "mars-habitat ambient."
        ),
        "intents": [
            "Write the mars-colony biologist's story of failing life-support.",
            "Break the story into mars-habitat survival scenes.",
            "Design key frames for the mars habitat and dwindling resources.",
            "Render motion-video clips preserving the mars-colony continuity.",
            "Compose a tense ambient-electronica BGM fitting the mars-survival tone.",
            "Generate mars-habitat ambient (life-support hum, dust-storm wind, alarm beeps).",
            "Mix the electronica BGM, habitat ambient, and baked-in audio.",
            "Compose the final mars mini-drama with all layers assembled.",
        ],
    },
    {
        "user_goal": "Make a historical mini-drama about a young female Egyptologist discovering a lost tomb at Valley of the Kings in the 1920s, with a sweeping Middle-Eastern-orchestral BGM and Valley-of-Kings ambient.",
        "rationale": (
            "1920s female-Egyptologist tomb-discovery drama + sweeping Middle-Eastern-orchestral "
            "BGM + Valley-of-Kings ambient."
        ),
        "intents": [
            "Write the female-Egyptologist's story of the 1920s lost-tomb discovery.",
            "Break the story into Egyptology-discovery scenes.",
            "Design key frames for the 1920s Valley of the Kings and tomb interior.",
            "Render motion-video clips preserving period Egyptology continuity.",
            "Compose a sweeping Middle-Eastern-orchestral BGM fitting the Egyptology tone.",
            "Generate Valley-of-Kings ambient (sand wind, distant camels, tomb-echoes).",
            "Mix the orchestral BGM, Valley ambient, and baked-in audio.",
            "Compose the final Egyptology mini-drama with all layers assembled.",
        ],
    },
    {
        "user_goal": "Make a fantasy mini-drama about an elf-scout and a dwarf-warrior forced to cross a haunted forest together to warn their kingdoms of war, with epic fantasy BGM and haunted-forest ambient.",
        "rationale": (
            "Elf-and-dwarf haunted-forest drama + epic fantasy BGM + haunted-forest ambient."
        ),
        "intents": [
            "Write the elf-and-dwarf story of crossing the haunted forest.",
            "Break the story into haunted-forest journey scenes.",
            "Design key frames for the haunted forest and the unlikely duo.",
            "Render motion-video clips preserving fantasy continuity.",
            "Compose an epic fantasy BGM fitting the elf-dwarf journey tone.",
            "Generate haunted-forest ambient (wind through gnarled trees, distant growls, creaking branches).",
            "Mix the fantasy BGM, forest ambient, and baked-in audio.",
            "Compose the final elf-and-dwarf mini-drama with all layers assembled.",
        ],
    },
    {
        "user_goal": "Make a contemporary mini-drama about a rural veterinarian delivering a difficult calf during a winter storm, with a warm Americana-folk BGM and winter-barn ambient.",
        "rationale": (
            "Rural-vet calf-delivery drama + warm Americana-folk BGM + winter-barn ambient."
        ),
        "intents": [
            "Write the rural-vet's story of the difficult calf delivery during a storm.",
            "Break the story into barn-delivery scenes.",
            "Design key frames for the winter farm and barn.",
            "Render motion-video clips preserving the rural-vet continuity.",
            "Compose a warm Americana-folk BGM fitting the rural-vet tone.",
            "Generate winter-barn ambient (howling wind outside, distant livestock, creaking timbers).",
            "Mix the folk BGM, barn ambient, and baked-in audio.",
            "Compose the final rural-vet mini-drama with all layers assembled.",
        ],
    },
    {
        "user_goal": "Make an adventure mini-drama about a helicopter pilot dropping fire-fighters into a raging California wildfire, with an adrenaline-orchestral BGM and wildfire ambient.",
        "rationale": (
            "Helicopter-pilot wildfire drama + adrenaline-orchestral BGM + wildfire ambient."
        ),
        "intents": [
            "Write the helicopter-pilot's story of dropping firefighters into the wildfire.",
            "Break the story into wildfire-chopper scenes.",
            "Design key frames for the burning California forest and the chopper.",
            "Render motion-video clips preserving the wildfire continuity.",
            "Compose an adrenaline-orchestral BGM fitting the wildfire-rescue tone.",
            "Generate wildfire ambient (crackling fire, distant chopper, radio chatter).",
            "Mix the orchestral BGM, wildfire ambient, and baked-in audio.",
            "Compose the final wildfire mini-drama with all layers assembled.",
        ],
    },
    {
        "user_goal": "Make a romance mini-drama about two astronauts on a three-year Mars mission falling in love mid-voyage, with a dreamy ambient-pop BGM and spacecraft-cabin ambient.",
        "rationale": (
            "Mars-mission astronaut romance + dreamy ambient-pop BGM + spacecraft-cabin ambient."
        ),
        "intents": [
            "Write the astronauts' story of falling in love mid-voyage to Mars.",
            "Break the story into spacecraft-romance scenes.",
            "Design key frames for the spacecraft interior and cosmic views.",
            "Render motion-video clips preserving the sci-fi romance tone.",
            "Compose a dreamy ambient-pop BGM fitting the space-romance tone.",
            "Generate spacecraft-cabin ambient (life-support hum, distant beeps, star-silence).",
            "Mix the pop BGM, cabin ambient, and baked-in audio.",
            "Compose the final space-romance mini-drama with all layers assembled.",
        ],
    },
    {
        "user_goal": "Make a mystery mini-drama about a young mortician discovering bodies with identical unexplained tattoos over her first week on the job, with an unsettling ambient-drone BGM and morgue ambient.",
        "rationale": (
            "Young-mortician tattoo-mystery drama + unsettling ambient-drone + morgue ambient."
        ),
        "intents": [
            "Write the young-mortician's story of the matching-tattoo mystery.",
            "Break the story into morgue-mystery scenes.",
            "Design key frames for the morgue and the suspicious tattoos.",
            "Render motion-video clips preserving the mystery tone.",
            "Compose an unsettling ambient-drone BGM fitting the morgue-mystery tone.",
            "Generate morgue ambient (refrigeration hum, distant drip, metal clink).",
            "Mix the drone BGM, morgue ambient, and baked-in audio.",
            "Compose the final morgue mini-drama with all layers assembled.",
        ],
    },
    {
        "user_goal": "Make a contemporary mini-drama about a refugee family's first Ramadan in their new adopted country, with a gentle oud-and-ney BGM and suburban-Ramadan ambient.",
        "rationale": (
            "Refugee-family first-Ramadan drama + gentle oud-and-ney BGM + suburban-Ramadan "
            "ambient."
        ),
        "intents": [
            "Write the refugee-family's first-Ramadan story in their new country.",
            "Break the story into Ramadan-family scenes.",
            "Design key frames for the suburban Ramadan setting and family moments.",
            "Render motion-video clips preserving the refugee-family continuity.",
            "Compose a gentle oud-and-ney BGM fitting the Ramadan tone.",
            "Generate suburban-Ramadan ambient (distant azan, evening chatter, kitchen sounds).",
            "Mix the oud BGM, Ramadan ambient, and baked-in audio.",
            "Compose the final Ramadan mini-drama with all layers assembled.",
        ],
    },
    {
        "user_goal": "Make a fantasy mini-drama about a young druid defending a sacred oak grove from a logger clan, with a cinematic Celtic-orchestra BGM and ancient-forest ambient.",
        "rationale": (
            "Young-druid oak-defender drama + cinematic Celtic-orchestra + ancient-forest "
            "ambient."
        ),
        "intents": [
            "Write the young-druid's story of defending the sacred oak grove.",
            "Break the story into druid-defender scenes.",
            "Design key frames for the oak grove and druid-vs-logger confrontations.",
            "Render motion-video clips preserving the fantasy-druid continuity.",
            "Compose a cinematic Celtic-orchestra BGM fitting the druid tone.",
            "Generate ancient-forest ambient (wind through oaks, distant birds, deep-forest creaks).",
            "Mix the Celtic BGM, forest ambient, and baked-in audio.",
            "Compose the final druid mini-drama with all layers assembled.",
        ],
    },
    {
        "user_goal": "Make a period mini-drama about a 19th-century Chinese railway laborer who falls for a widowed rancher in the American West, with a fusion Chinese-American-folk BGM and frontier-camp ambient.",
        "rationale": (
            "19th-century Chinese railway-laborer and rancher-widow drama + fusion Chinese-"
            "American-folk + frontier-camp ambient."
        ),
        "intents": [
            "Write the 19th-century railway-laborer-and-rancher romance story.",
            "Break the story into frontier-camp romance scenes.",
            "Design key frames for the railway and ranch settings.",
            "Render motion-video clips preserving the 19th-century West continuity.",
            "Compose a fusion Chinese-American-folk BGM fitting the cross-cultural romance.",
            "Generate frontier-camp ambient (distant train, cattle, prairie wind).",
            "Mix the fusion BGM, frontier ambient, and baked-in audio.",
            "Compose the final frontier mini-drama with all layers assembled.",
        ],
    },
    {
        "user_goal": "Make a magical-realism mini-drama about a seamstress whose stitched garments secretly carry the wearers' buried memories, with a whimsical waltz BGM and atelier ambient.",
        "rationale": (
            "Seamstress memory-stitching drama + whimsical waltz BGM + atelier ambient."
        ),
        "intents": [
            "Write the seamstress story of stitched garments carrying memories.",
            "Break the story into magical-realism atelier scenes.",
            "Design key frames for the atelier and the magical garments.",
            "Render motion-video clips preserving magical-realism continuity.",
            "Compose a whimsical waltz BGM fitting the seamstress magic-realism tone.",
            "Generate atelier ambient (sewing-machine hum, fabric rustle, distant street).",
            "Mix the waltz BGM, atelier ambient, and baked-in audio.",
            "Compose the final seamstress mini-drama with all layers assembled.",
        ],
    },
    {
        "user_goal": "Make a contemporary mini-drama about a deaf violinist convinced to join a community orchestra by a retired conductor, with a heartwarming chamber-orchestra BGM and community-hall ambient.",
        "rationale": (
            "Deaf-violinist community-orchestra drama + heartwarming chamber-orchestra BGM + "
            "community-hall ambient."
        ),
        "intents": [
            "Write the deaf-violinist's story of joining the community orchestra.",
            "Break the story into rehearsal-and-concert scenes.",
            "Design key frames for the community hall and rehearsal dynamics.",
            "Render motion-video clips preserving the community-music continuity.",
            "Compose a heartwarming chamber-orchestra BGM fitting the community tone.",
            "Generate community-hall ambient (shuffling audience, tuning strings, distant door).",
            "Mix the chamber BGM, hall ambient, and baked-in audio.",
            "Compose the final community mini-drama with all layers assembled.",
        ],
    },
    {
        "user_goal": "Make a thriller mini-drama about a solo kayaker trapped in a slot canyon during a flash flood, with a tense orchestral BGM and flash-flood canyon ambient.",
        "rationale": (
            "Solo-kayaker slot-canyon flood drama + tense orchestral BGM + flash-flood ambient."
        ),
        "intents": [
            "Write the solo-kayaker's story of the slot-canyon flash flood.",
            "Break the story into canyon-flood thriller scenes.",
            "Design key frames for the slot canyon and rising water.",
            "Render motion-video clips preserving the flood-thriller tone.",
            "Compose a tense orchestral BGM fitting the flash-flood kayaker tone.",
            "Generate flash-flood canyon ambient (roaring water, distant thunder, echo cascades).",
            "Mix the orchestral BGM, canyon ambient, and baked-in audio.",
            "Compose the final kayaker mini-drama with all layers assembled.",
        ],
    },
    {
        "user_goal": "Make a period mini-drama about a Balkan violinist performing in a grand-hotel orchestra in 1930s Budapest as war looms, with a lush gypsy-violin BGM and grand-hotel ambient.",
        "rationale": (
            "1930s Budapest violinist war-looming drama + lush gypsy-violin BGM + grand-hotel "
            "ambient."
        ),
        "intents": [
            "Write the 1930s Budapest violinist's story as war looms.",
            "Break the story into grand-hotel scenes.",
            "Design key frames for the 1930s grand hotel and ballroom.",
            "Render motion-video clips preserving 1930s Budapest continuity.",
            "Compose a lush gypsy-violin BGM fitting the Budapest-violinist tone.",
            "Generate grand-hotel ambient (murmured guests, clinking dinnerware, distant laughter).",
            "Mix the violin BGM, hotel ambient, and baked-in audio.",
            "Compose the final 1930s mini-drama with all layers assembled.",
        ],
    },
    {
        "user_goal": "Make a fantasy mini-drama about a young siren-maiden torn between her ocean kin and a shipwrecked sailor, with a haunting choir-and-harp BGM and ocean-cliff ambient.",
        "rationale": (
            "Young-siren divided-loyalties drama + haunting choir-and-harp BGM + ocean-cliff "
            "ambient."
        ),
        "intents": [
            "Write the young-siren's story of divided loyalty.",
            "Break the story into siren-cliff scenes.",
            "Design key frames for the ocean cliffs and siren's sea-kin.",
            "Render motion-video clips preserving the siren-fantasy tone.",
            "Compose a haunting choir-and-harp BGM fitting the siren-maiden tone.",
            "Generate ocean-cliff ambient (waves, wind, distant seabirds).",
            "Mix the choir BGM, cliff ambient, and baked-in audio.",
            "Compose the final siren mini-drama with all layers assembled.",
        ],
    },
    {
        "user_goal": "Make a contemporary mini-drama about a Parisian pastry chef opening her first bakery in a small American town, with a breezy French-pop BGM and small-town bakery ambient.",
        "rationale": (
            "Parisian-chef American-town bakery drama + breezy French-pop BGM + small-town "
            "bakery ambient."
        ),
        "intents": [
            "Write the Parisian-chef's story of opening her American bakery.",
            "Break the story into bakery-opening scenes.",
            "Design key frames for the small-town bakery.",
            "Render motion-video clips preserving the bakery-drama continuity.",
            "Compose a breezy French-pop BGM fitting the Parisian-chef tone.",
            "Generate small-town bakery ambient (oven whir, doorbell jingle, distant street).",
            "Mix the pop BGM, bakery ambient, and baked-in audio.",
            "Compose the final bakery mini-drama with all layers assembled.",
        ],
    },
    {
        "user_goal": "Make a period mini-drama about a Soviet-era cosmonaut training in secret at Star City, with an ominous orchestral BGM and Star City ambient.",
        "rationale": (
            "Soviet-era cosmonaut Star-City training drama + ominous orchestral BGM + Star "
            "City ambient."
        ),
        "intents": [
            "Write the Soviet cosmonaut's training story at Star City.",
            "Break the story into cosmonaut-training scenes.",
            "Design key frames for Star City's training facilities.",
            "Render motion-video clips preserving Soviet-era continuity.",
            "Compose an ominous orchestral BGM fitting the Soviet cosmonaut tone.",
            "Generate Star City ambient (centrifuge whine, distant Russian orders, metal clangs).",
            "Mix the orchestral BGM, Star City ambient, and baked-in audio.",
            "Compose the final cosmonaut mini-drama with all layers assembled.",
        ],
    },
    {
        "user_goal": "Make a mystery mini-drama about a 1960s Japanese detective investigating a theft at a Kyoto temple, with a 1960s-jazz-Japanese-fusion BGM and temple-courtyard ambient.",
        "rationale": (
            "1960s Japanese detective temple-theft drama + 1960s jazz-Japanese-fusion + "
            "temple-courtyard ambient."
        ),
        "intents": [
            "Write the 1960s-Japanese-detective story of the temple theft.",
            "Break the story into Kyoto temple investigation scenes.",
            "Design key frames for 1960s Kyoto and the temple.",
            "Render motion-video clips preserving 1960s Japanese continuity.",
            "Compose a 1960s-jazz-Japanese-fusion BGM fitting the detective tone.",
            "Generate temple-courtyard ambient (distant bells, gravel footsteps, bamboo rustle).",
            "Mix the fusion BGM, courtyard ambient, and baked-in audio.",
            "Compose the final detective mini-drama with all layers assembled.",
        ],
    },
    {
        "user_goal": "Make a contemporary mini-drama about an ER nurse volunteering at a conflict-zone field hospital for three months, with a tense cinematic BGM and conflict-zone ambient.",
        "rationale": (
            "ER-nurse conflict-zone drama + tense cinematic BGM + conflict-zone ambient."
        ),
        "intents": [
            "Write the ER-nurse's story of volunteering at the conflict-zone field hospital.",
            "Break the story into field-hospital scenes.",
            "Design key frames for the field hospital and conflict-zone surroundings.",
            "Render motion-video clips preserving the conflict-zone continuity.",
            "Compose a tense cinematic BGM fitting the field-hospital tone.",
            "Generate conflict-zone ambient (distant explosions, helicopter rotors, shouts).",
            "Mix the cinematic BGM, conflict ambient, and baked-in audio.",
            "Compose the final conflict mini-drama with all layers assembled.",
        ],
    },
    {
        "user_goal": "Make a fantasy mini-drama about an ice-princess rediscovering her frozen kingdom after a century's curse breaks, with a sweeping orchestral BGM and frozen-palace ambient.",
        "rationale": (
            "Ice-princess century-curse drama + sweeping orchestral BGM + frozen-palace ambient."
        ),
        "intents": [
            "Write the ice-princess's story of rediscovering her frozen kingdom.",
            "Break the story into frozen-palace scenes.",
            "Design key frames for the frozen kingdom and ice palace.",
            "Render motion-video clips preserving the ice-fantasy continuity.",
            "Compose a sweeping orchestral BGM fitting the ice-princess tone.",
            "Generate frozen-palace ambient (ice cracks, wind through pillars, distant chimes).",
            "Mix the orchestral BGM, palace ambient, and baked-in audio.",
            "Compose the final ice-princess mini-drama with all layers assembled.",
        ],
    },
    {
        "user_goal": "Make a thriller mini-drama about a mountain rescue team responding to a lost climber at K2 base camp, with an adrenaline-orchestra BGM and K2-camp ambient.",
        "rationale": (
            "K2 rescue-team drama + adrenaline-orchestra BGM + K2-camp ambient."
        ),
        "intents": [
            "Write the K2 rescue team's story of responding to the lost climber.",
            "Break the story into K2-rescue scenes.",
            "Design key frames for the K2 base camp and climbing stages.",
            "Render motion-video clips preserving the K2 rescue continuity.",
            "Compose an adrenaline-orchestra BGM fitting the K2-rescue tone.",
            "Generate K2-camp ambient (wind, crampon crunches, distant radio chatter).",
            "Mix the orchestra BGM, K2 ambient, and baked-in audio.",
            "Compose the final K2 mini-drama with all layers assembled.",
        ],
    },
    {
        "user_goal": "Make a historical mini-drama about a 1940s female pilot delivering war-planes across the Atlantic, with a sweeping WWII-orchestral BGM and transatlantic-cockpit ambient.",
        "rationale": (
            "1940s female war-plane pilot drama + sweeping WWII-orchestral + transatlantic-"
            "cockpit ambient."
        ),
        "intents": [
            "Write the 1940s female-pilot's story of transatlantic war-plane delivery.",
            "Break the story into transatlantic flight scenes.",
            "Design key frames for the 1940s cockpit and Atlantic ocean.",
            "Render motion-video clips preserving WWII-pilot continuity.",
            "Compose a sweeping WWII-orchestral BGM fitting the transatlantic tone.",
            "Generate transatlantic-cockpit ambient (propeller hum, wind, distant radio).",
            "Mix the orchestral BGM, cockpit ambient, and baked-in audio.",
            "Compose the final WWII pilot mini-drama with all layers assembled.",
        ],
    },
    {
        "user_goal": "Make a cyberpunk mini-drama about a forgotten AI rewakening in a post-corporate wasteland to protect the last humans, with a dark ambient-synth BGM and post-corporate-wasteland ambient.",
        "rationale": (
            "Forgotten-AI post-corporate wasteland drama + dark ambient-synth BGM + post-"
            "corporate-wasteland ambient."
        ),
        "intents": [
            "Write the forgotten-AI's story of protecting the last humans.",
            "Break the story into post-corporate wasteland AI scenes.",
            "Design key frames for the wasteland and AI manifestations.",
            "Render motion-video clips preserving the cyberpunk-AI continuity.",
            "Compose a dark ambient-synth BGM fitting the AI-awakening tone.",
            "Generate post-corporate-wasteland ambient (wind, distant rubble, broken neon hum).",
            "Mix the synth BGM, wasteland ambient, and baked-in audio.",
            "Compose the final cyberpunk mini-drama with all layers assembled.",
        ],
    },
    {
        "user_goal": "Make a period mini-drama about a 17th-century Dutch painter creating a portrait of her own late sister from memory, with a baroque chamber-ensemble BGM and painter's-studio ambient.",
        "rationale": (
            "17th-century Dutch painter drama + baroque chamber-ensemble BGM + painter's-studio "
            "ambient."
        ),
        "intents": [
            "Write the 17th-century Dutch painter's story of painting her sister from memory.",
            "Break the story into painter-studio grief-and-work scenes.",
            "Design key frames for the 17th-century studio and painting.",
            "Render motion-video clips preserving the Dutch-painter continuity.",
            "Compose a baroque chamber-ensemble BGM fitting the Dutch-painter tone.",
            "Generate painter's-studio ambient (brush on canvas, distant Amsterdam street, window rain).",
            "Mix the chamber BGM, studio ambient, and baked-in audio.",
            "Compose the final painter mini-drama with all layers assembled.",
        ],
    },
    {
        "user_goal": "Make a contemporary mini-drama about a young hospice chaplain and a dying veteran sharing one last conversation, with a tender piano-and-cello BGM and hospice-room ambient.",
        "rationale": (
            "Young-hospice-chaplain and dying-veteran drama + tender piano-and-cello BGM + "
            "hospice-room ambient."
        ),
        "intents": [
            "Write the hospice-chaplain-and-veteran story of their last conversation.",
            "Break the story into hospice-conversation scenes.",
            "Design key frames for the hospice room and memories.",
            "Render motion-video clips preserving the hospice-drama continuity.",
            "Compose a tender piano-and-cello BGM fitting the hospice tone.",
            "Generate hospice-room ambient (soft machine beeps, distant hallway, window chirps).",
            "Mix the piano-cello BGM, hospice ambient, and baked-in audio.",
            "Compose the final hospice mini-drama with all layers assembled.",
        ],
    },
    {
        "user_goal": "Make a fantasy mini-drama about a young tavern-keeper who discovers her cellar hides a portal to the fae realm, with a whimsical celtic-folk BGM and tavern-cellar ambient.",
        "rationale": (
            "Tavern-keeper fae-portal drama + whimsical celtic-folk BGM + tavern-cellar ambient."
        ),
        "intents": [
            "Write the tavern-keeper's story of the fae-portal in her cellar.",
            "Break the story into tavern-and-fae scenes.",
            "Design key frames for the tavern cellar and fae realm glimpses.",
            "Render motion-video clips preserving the fantasy continuity.",
            "Compose a whimsical celtic-folk BGM fitting the fae-portal tone.",
            "Generate tavern-cellar ambient (barrel creaks, distant tavern chatter, magical chimes).",
            "Mix the celtic BGM, cellar ambient, and baked-in audio.",
            "Compose the final tavern mini-drama with all layers assembled.",
        ],
    },
]
