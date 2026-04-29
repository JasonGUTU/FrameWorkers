"""Shape: cr_compositor_only —
    Story → Screenplay → KeyFrame → Video → Compositor.

Cinematic mini-drama with NO audio overlay requested. Reject Music /
Ambience / Transcription / AudioMix / VideoAnalysis biases.

Target 80; this file has the 50 short-brief samples. Long-story samples
(30) go in shape_cr_compositor_only_long.py (separate file to keep
context costs isolated — long-story authoring is ~3000 chars each).
"""
from __future__ import annotations

SAMPLES: list[dict] = [
    {
        "user_goal": "Make a rebirth-revenge mini-drama where the female lead, framed by her best friend and pushed to her death, is reborn three years earlier and strikes back.",
        "rationale": (
            "Rebirth-revenge mini-drama with no audio overlay. Chain: Story → Screenplay → "
            "KeyFrame → Video → Compositor. Reject Music / Ambience (no audio request), "
            "Transcription (no subtitle), AudioMix (nothing to mix), VideoAnalysis (no upload)."
        ),
        "intents": [
            "Write the rebirth-revenge story where the framed female lead is reborn to strike back.",
            "Break the rebirth-revenge story into cinematic scenes with rebirth, setup, and revenge beats.",
            "Design key frames for each scene capturing the revenge arc visually.",
            "Render motion-video clips from the key frames preserving character continuity.",
            "Compose the final rebirth-revenge mini-drama with all clips assembled.",
        ],
    },
    {
        "user_goal": "Make a post-apocalyptic animated drama where the last survivors discover a hidden sanctuary guarded by an awakened AI.",
        "rationale": (
            "Post-apocalyptic AI-sanctuary drama, no audio requested. Story → Screenplay → "
            "KeyFrame → Video → Compositor."
        ),
        "intents": [
            "Write the post-apocalyptic story about survivors discovering an AI-guarded sanctuary.",
            "Break the story into post-apocalyptic scenes building to the AI reveal.",
            "Design key frames for the wasteland-to-sanctuary journey.",
            "Render motion-video clips preserving the post-apocalyptic aesthetic.",
            "Compose the final post-apocalyptic mini-drama assembly.",
        ],
    },
    {
        "user_goal": "Make a palace-intrigue costume-drama mini-drama where a real and fake princess swap places, exploit each other, and team up to expose the empress's ambitions.",
        "rationale": (
            "Palace-intrigue costume drama, no audio requested."
        ),
        "intents": [
            "Write the palace-intrigue story where the real and fake princess swap and then ally.",
            "Break the story into palace-intrigue scenes with swap, exploitation, and alliance beats.",
            "Design key frames showcasing palace opulence and the princess characters.",
            "Render motion-video clips preserving palace-intrigue continuity.",
            "Compose the final palace-intrigue mini-drama assembly.",
        ],
    },
    {
        "user_goal": "Make a martial-arts animated drama about a young swordsman who ventures alone into the demonic cult's seven-layered killing formation to avenge his sect.",
        "rationale": (
            "Martial-arts vengeance drama, no audio requested."
        ),
        "intents": [
            "Write the martial-arts story about the young swordsman entering the demonic formation.",
            "Break the story into seven-formation scenes with escalating combat.",
            "Design key frames for the killing-formation visuals.",
            "Render motion-video clips preserving martial-arts action continuity.",
            "Compose the final martial-arts mini-drama assembly.",
        ],
    },
    {
        "user_goal": "Make an epic-battle scene for a fantasy animated drama: seven ancient divine beasts gather to face a demon god returning to the mortal realm.",
        "rationale": (
            "Epic-battle fantasy scene, no audio requested."
        ),
        "intents": [
            "Write the epic-battle story of seven divine beasts confronting the returning demon god.",
            "Break the battle into escalating scenes showcasing each divine beast.",
            "Design key frames for the divine beasts and demon god confrontation.",
            "Render motion-video clips preserving epic fantasy continuity.",
            "Compose the final fantasy-battle mini-drama assembly.",
        ],
    },
    {
        "user_goal": "Make a sci-fi exploration drama about a lone astronaut discovering an ancient alien relic on a dead planet.",
        "rationale": (
            "Sci-fi exploration drama, no audio requested."
        ),
        "intents": [
            "Write the sci-fi story of the lone astronaut discovering the alien relic.",
            "Break the story into exploration scenes leading to the relic reveal.",
            "Design key frames for the dead-planet landscape and the relic.",
            "Render motion-video clips preserving the sci-fi exploration tone.",
            "Compose the final sci-fi mini-drama assembly.",
        ],
    },
    {
        "user_goal": "Make a cyberpunk hacker mini-drama where a young hacker discovers a corporate conspiracy that threatens everyone.",
        "rationale": (
            "Cyberpunk hacker drama, no audio requested."
        ),
        "intents": [
            "Write the cyberpunk hacker story about the corporate conspiracy.",
            "Break the story into hacker-thriller scenes with escalating stakes.",
            "Design key frames for the neon-cyberpunk world.",
            "Render motion-video clips preserving the cyberpunk aesthetic.",
            "Compose the final cyberpunk mini-drama assembly.",
        ],
    },
    {
        "user_goal": "Make a western-revenge mini-drama where a gunslinger returns to her hometown to avenge her murdered family.",
        "rationale": (
            "Western-revenge drama, no audio requested."
        ),
        "intents": [
            "Write the western-revenge story about the gunslinger's return.",
            "Break the story into western scenes with showdown buildup.",
            "Design key frames for the dusty-town western aesthetic.",
            "Render motion-video clips preserving the western continuity.",
            "Compose the final western mini-drama assembly.",
        ],
    },
    {
        "user_goal": "Make a transmigration period mini-drama where a modern doctor finds herself in the court of a feudal emperor and must outwit the queen.",
        "rationale": (
            "Transmigration period drama, no audio requested."
        ),
        "intents": [
            "Write the transmigration story of the modern doctor in the feudal court.",
            "Break the story into court-intrigue scenes with doctor-vs-queen beats.",
            "Design key frames for feudal-court opulence and character costuming.",
            "Render motion-video clips preserving transmigration period continuity.",
            "Compose the final transmigration mini-drama assembly.",
        ],
    },
    {
        "user_goal": "Make a superhero origin mini-drama about a shy librarian who discovers she can speak to ghosts.",
        "rationale": (
            "Superhero ghost-speaker origin drama, no audio requested."
        ),
        "intents": [
            "Write the superhero origin story of the librarian who speaks to ghosts.",
            "Break the story into origin scenes with awakening and first heroic act.",
            "Design key frames for the library and ghost manifestations.",
            "Render motion-video clips preserving the ghost-speaker origin tone.",
            "Compose the final origin mini-drama assembly.",
        ],
    },
    {
        "user_goal": "Make a swordswoman mini-drama about a disciple of the jade sword who must prove her worth in a duel tournament.",
        "rationale": (
            "Swordswoman tournament drama, no audio requested."
        ),
        "intents": [
            "Write the swordswoman story about the jade-sword disciple's tournament.",
            "Break the story into duel-tournament scenes with escalating opponents.",
            "Design key frames for the tournament arena and swordswoman's style.",
            "Render motion-video clips preserving swordswoman action continuity.",
            "Compose the final swordswoman mini-drama assembly.",
        ],
    },
    {
        "user_goal": "Make an underdog-comeback mini-drama about a dropout who rebuilds his company from scratch after being betrayed by his partner.",
        "rationale": (
            "Underdog-comeback business drama, no audio requested."
        ),
        "intents": [
            "Write the underdog-comeback story of the betrayed dropout rebuilding.",
            "Break the story into business-comeback scenes with betrayal and triumph beats.",
            "Design key frames for the business-drama office and rebuilding arc.",
            "Render motion-video clips preserving the underdog-comeback continuity.",
            "Compose the final underdog-comeback mini-drama assembly.",
        ],
    },
    {
        "user_goal": "Make a heist mini-drama about a team of thieves breaking into the most secure vault in Monaco.",
        "rationale": (
            "Heist thriller drama, no audio requested."
        ),
        "intents": [
            "Write the heist story of the Monaco vault break-in.",
            "Break the story into heist scenes with setup, execution, and twist.",
            "Design key frames for the vault and heist team dynamics.",
            "Render motion-video clips preserving heist-thriller continuity.",
            "Compose the final heist mini-drama assembly.",
        ],
    },
    {
        "user_goal": "Make an amnesia mystery mini-drama where a woman wakes up in a strange apartment with no memory of who she is or why she's there.",
        "rationale": (
            "Amnesia mystery drama, no audio requested."
        ),
        "intents": [
            "Write the amnesia-mystery story of the woman waking up in a strange apartment.",
            "Break the story into amnesia-discovery scenes with mounting clues.",
            "Design key frames for the mysterious apartment and unfolding memories.",
            "Render motion-video clips preserving the amnesia-mystery tone.",
            "Compose the final amnesia mini-drama assembly.",
        ],
    },
    {
        "user_goal": "Make a generation-gap family drama about a strict grandmother and a rebellious teen who must share one small apartment for the summer.",
        "rationale": (
            "Generation-gap family drama, no audio requested."
        ),
        "intents": [
            "Write the generation-gap story of grandmother and teen in one apartment.",
            "Break the story into family-clash scenes with eventual reconciliation beats.",
            "Design key frames for the cramped apartment and family dynamics.",
            "Render motion-video clips preserving the family-drama continuity.",
            "Compose the final family mini-drama assembly.",
        ],
    },
    {
        "user_goal": "Make a boxing mini-drama about an aging fighter who takes one last fight to pay for his daughter's surgery.",
        "rationale": (
            "Boxing sports-drama, no audio requested."
        ),
        "intents": [
            "Write the boxing story of the aging fighter's last fight for his daughter.",
            "Break the story into boxing-drama scenes with training and fight-night beats.",
            "Design key frames for the gym, home, and fight arena.",
            "Render motion-video clips preserving boxing-drama continuity.",
            "Compose the final boxing mini-drama assembly.",
        ],
    },
    {
        "user_goal": "Make a time-loop mini-drama where a detective relives the same day until he solves a murder.",
        "rationale": (
            "Time-loop murder-mystery drama, no audio requested."
        ),
        "intents": [
            "Write the time-loop detective story about reliving the day to solve the murder.",
            "Break the story into time-loop scenes with progressive clue gathering.",
            "Design key frames for the repeating crime scene and subtle variations.",
            "Render motion-video clips preserving the time-loop continuity.",
            "Compose the final time-loop mini-drama assembly.",
        ],
    },
    {
        "user_goal": "Make a political-intrigue mini-drama where a young senator uncovers corruption in her own party.",
        "rationale": (
            "Political-intrigue drama, no audio requested."
        ),
        "intents": [
            "Write the political-intrigue story of the young senator uncovering corruption.",
            "Break the story into political-thriller scenes with escalating revelations.",
            "Design key frames for political chambers and behind-the-scenes intrigue.",
            "Render motion-video clips preserving political-drama continuity.",
            "Compose the final political mini-drama assembly.",
        ],
    },
    {
        "user_goal": "Make a pirate mini-drama where the daughter of a legendary captain takes command of his ship after his death.",
        "rationale": (
            "Pirate succession drama, no audio requested."
        ),
        "intents": [
            "Write the pirate story of the daughter inheriting her captain-father's ship.",
            "Break the story into pirate-succession scenes with crew-earning beats.",
            "Design key frames for the pirate ship and the new captain.",
            "Render motion-video clips preserving pirate-adventure continuity.",
            "Compose the final pirate mini-drama assembly.",
        ],
    },
    {
        "user_goal": "Make a ghost-love mini-drama where a violinist falls for the ghost of the previous tenant in her new apartment.",
        "rationale": (
            "Ghost-love drama, no audio requested."
        ),
        "intents": [
            "Write the ghost-love story of the violinist and the ghost tenant.",
            "Break the story into ghost-love scenes with supernatural romance beats.",
            "Design key frames for the apartment and ghost's manifestations.",
            "Render motion-video clips preserving ghost-romance continuity.",
            "Compose the final ghost-love mini-drama assembly.",
        ],
    },
    {
        "user_goal": "Make a supernatural-detective mini-drama where a medium and a skeptical cop investigate disappearances in a small coastal town.",
        "rationale": (
            "Supernatural-detective drama, no audio requested."
        ),
        "intents": [
            "Write the supernatural-detective story of the medium and cop investigating disappearances.",
            "Break the story into investigation scenes blending skeptical and supernatural perspectives.",
            "Design key frames for the coastal town and supernatural encounters.",
            "Render motion-video clips preserving the investigation tone.",
            "Compose the final supernatural mini-drama assembly.",
        ],
    },
    {
        "user_goal": "Make a restaurant-redemption mini-drama where a down-on-her-luck chef reopens her dead husband's bistro.",
        "rationale": (
            "Restaurant-redemption drama, no audio requested."
        ),
        "intents": [
            "Write the restaurant-redemption story of the chef reopening the bistro.",
            "Break the story into restaurant-redemption scenes with reopening beats.",
            "Design key frames for the bistro interior and kitchen activity.",
            "Render motion-video clips preserving the restaurant-drama continuity.",
            "Compose the final restaurant mini-drama assembly.",
        ],
    },
    {
        "user_goal": "Make a dance-rivalry mini-drama about two ballerinas competing for the lead role in Swan Lake.",
        "rationale": (
            "Dance-rivalry drama, no audio requested."
        ),
        "intents": [
            "Write the dance-rivalry story of the two Swan Lake aspirants.",
            "Break the story into rehearsal-and-audition scenes with rivalry beats.",
            "Design key frames for the ballet studio and stage.",
            "Render motion-video clips preserving dance-rivalry continuity.",
            "Compose the final dance-rivalry mini-drama assembly.",
        ],
    },
    {
        "user_goal": "Make a survival mini-drama about a climber stranded alone on a mountain peak after her partner falls.",
        "rationale": (
            "Survival mountain drama, no audio requested."
        ),
        "intents": [
            "Write the survival story of the stranded climber after her partner's fall.",
            "Break the story into survival scenes across the mountain descent.",
            "Design key frames for the harsh mountain environment.",
            "Render motion-video clips preserving the survival tension.",
            "Compose the final survival mini-drama assembly.",
        ],
    },
    {
        "user_goal": "Make a small-town-mystery mini-drama where a journalist returns to her hometown to investigate her best friend's disappearance.",
        "rationale": (
            "Small-town-mystery drama, no audio requested."
        ),
        "intents": [
            "Write the small-town-mystery story of the journalist's investigation.",
            "Break the story into mystery scenes across the town's hidden corners.",
            "Design key frames for the town's main street, diner, and secrets.",
            "Render motion-video clips preserving the mystery atmosphere.",
            "Compose the final small-town mystery mini-drama assembly.",
        ],
    },
    {
        "user_goal": "Make a steampunk inventor mini-drama about a young tinkerer who builds an illegal flying machine to escape a dystopian city.",
        "rationale": (
            "Steampunk escape drama, no audio requested."
        ),
        "intents": [
            "Write the steampunk story of the tinkerer escaping the dystopia.",
            "Break the story into invention-and-escape scenes.",
            "Design key frames for the brass-clockwork inventions and dystopian city.",
            "Render motion-video clips preserving steampunk continuity.",
            "Compose the final steampunk mini-drama assembly.",
        ],
    },
    {
        "user_goal": "Make a zombie-survival mini-drama about a small-town nurse leading her students through overgrown streets to a rumored safe zone.",
        "rationale": (
            "Zombie-survival drama, no audio requested."
        ),
        "intents": [
            "Write the zombie-survival story of the nurse leading students to safety.",
            "Break the story into zombie-survival scenes across the overgrown town.",
            "Design key frames for the overgrown streets and survivor group.",
            "Render motion-video clips preserving zombie-survival continuity.",
            "Compose the final zombie mini-drama assembly.",
        ],
    },
    {
        "user_goal": "Make a monster-hunter mini-drama about a scarred huntress who tracks a cursed wolf through a misty forest.",
        "rationale": (
            "Monster-hunter fantasy drama, no audio requested."
        ),
        "intents": [
            "Write the monster-hunter story of the huntress tracking the cursed wolf.",
            "Break the story into hunter-track-and-confront scenes.",
            "Design key frames for the misty forest and cursed wolf.",
            "Render motion-video clips preserving monster-hunter continuity.",
            "Compose the final monster-hunter mini-drama assembly.",
        ],
    },
    {
        "user_goal": "Make a historical spy mini-drama about a double agent in 1940s Berlin balancing loyalty and love.",
        "rationale": (
            "Historical spy drama, no audio requested."
        ),
        "intents": [
            "Write the historical spy story of the 1940s Berlin double agent.",
            "Break the story into spy-thriller scenes balancing loyalty and romance.",
            "Design key frames for 1940s Berlin streets and spy encounters.",
            "Render motion-video clips preserving the period-spy continuity.",
            "Compose the final historical spy mini-drama assembly.",
        ],
    },
    {
        "user_goal": "Make an animal-companion mini-drama about a lonely shepherd and her orphaned wolf cub surviving winter alone.",
        "rationale": (
            "Animal-companion survival drama, no audio requested."
        ),
        "intents": [
            "Write the animal-companion story of the shepherd and wolf cub surviving winter.",
            "Break the story into winter-survival companionship scenes.",
            "Design key frames for the snowy terrain and companion bonding.",
            "Render motion-video clips preserving the winter-survival continuity.",
            "Compose the final animal-companion mini-drama assembly.",
        ],
    },
    {
        "user_goal": "Make a dragon-rider fantasy mini-drama about a young stablehand chosen by the last dragon egg to hatch in a mountain monastery.",
        "rationale": (
            "Dragon-rider fantasy drama, no audio requested."
        ),
        "intents": [
            "Write the dragon-rider story of the stablehand chosen by the last dragon egg.",
            "Break the story into dragon-bond-and-quest scenes.",
            "Design key frames for the dragon, stablehand, and mountain monastery.",
            "Render motion-video clips preserving dragon-rider fantasy continuity.",
            "Compose the final dragon-rider mini-drama assembly.",
        ],
    },
    {
        "user_goal": "Make a romance mini-drama about a young actress who falls for her stunt double's shy twin brother on set.",
        "rationale": (
            "Behind-the-scenes romance drama, no audio requested."
        ),
        "intents": [
            "Write the romance story of the actress falling for the stunt double's twin brother.",
            "Break the story into behind-the-scenes romance scenes.",
            "Design key frames for the film set and growing attraction.",
            "Render motion-video clips preserving the set-romance continuity.",
            "Compose the final set-romance mini-drama assembly.",
        ],
    },
    {
        "user_goal": "Make a revolutionary mini-drama about a young princess who sides with the rebel leader against her own royal family.",
        "rationale": (
            "Revolutionary princess drama, no audio requested."
        ),
        "intents": [
            "Write the revolutionary story of the princess allying with the rebel leader.",
            "Break the story into revolution scenes with loyalty conflicts.",
            "Design key frames for the palace and rebel camps.",
            "Render motion-video clips preserving the revolutionary tone.",
            "Compose the final revolutionary mini-drama assembly.",
        ],
    },
    {
        "user_goal": "Make a spy-thief mini-drama about a gentleman thief who pulls one last con to steal back his wrongfully imprisoned sister's freedom.",
        "rationale": (
            "Spy-thief redemption drama, no audio requested."
        ),
        "intents": [
            "Write the spy-thief story of the gentleman thief's last con for his sister.",
            "Break the story into con-artist scenes leading to the freedom reveal.",
            "Design key frames for the con sites and gentleman-thief flair.",
            "Render motion-video clips preserving the con-artist continuity.",
            "Compose the final spy-thief mini-drama assembly.",
        ],
    },
    {
        "user_goal": "Make a haunted-lighthouse mini-drama about a lighthouse keeper's granddaughter who returns after his death and discovers his ghost won't leave.",
        "rationale": (
            "Haunted-lighthouse drama, no audio requested."
        ),
        "intents": [
            "Write the haunted-lighthouse story of the granddaughter and grandfather's ghost.",
            "Break the story into haunted-lighthouse scenes with emotional climax.",
            "Design key frames for the stormy lighthouse and ghost's presence.",
            "Render motion-video clips preserving haunted-lighthouse continuity.",
            "Compose the final haunted-lighthouse mini-drama assembly.",
        ],
    },
    {
        "user_goal": "Make a musical biopic mini-drama about a jazz singer rising from the smoky clubs of 1950s Harlem to international fame.",
        "rationale": (
            "Jazz-singer biopic drama, no audio requested."
        ),
        "intents": [
            "Write the jazz-singer biopic story of her rise from Harlem to international fame.",
            "Break the story into biopic scenes across clubs, rehearsals, and performances.",
            "Design key frames for 1950s Harlem clubs and the singer's style.",
            "Render motion-video clips preserving the biopic continuity.",
            "Compose the final jazz-singer mini-drama assembly.",
        ],
    },
    {
        "user_goal": "Make a mentor-student mini-drama about a reclusive pianist coaxed out of retirement to train one last prodigy.",
        "rationale": (
            "Mentor-student music drama, no audio requested."
        ),
        "intents": [
            "Write the mentor-student story of the reclusive pianist training the prodigy.",
            "Break the story into mentor-training scenes with emotional growth.",
            "Design key frames for the pianist's home and training sessions.",
            "Render motion-video clips preserving the mentor-student tone.",
            "Compose the final mentor mini-drama assembly.",
        ],
    },
    {
        "user_goal": "Make a colonial-era mini-drama about a young widow who inherits a tea plantation and must outmaneuver the governor who wants to seize it.",
        "rationale": (
            "Colonial widow drama, no audio requested."
        ),
        "intents": [
            "Write the colonial-widow story of the widow outmaneuvering the governor.",
            "Break the story into colonial-drama scenes across the plantation and colonial offices.",
            "Design key frames for the plantation and colonial era detail.",
            "Render motion-video clips preserving the colonial-drama continuity.",
            "Compose the final colonial mini-drama assembly.",
        ],
    },
    {
        "user_goal": "Make a fantasy-sword mini-drama about a blind swordsman facing ten duelists to reclaim his stolen sword.",
        "rationale": (
            "Blind-swordsman fantasy drama, no audio requested."
        ),
        "intents": [
            "Write the blind-swordsman story of reclaiming his stolen sword through ten duels.",
            "Break the story into ten escalating duel scenes.",
            "Design key frames for each duelist and the blind-swordsman's style.",
            "Render motion-video clips preserving martial continuity.",
            "Compose the final blind-swordsman mini-drama assembly.",
        ],
    },
    {
        "user_goal": "Make a street-art mini-drama about a young graffiti artist discovered by a famous gallery owner who wants to exploit her.",
        "rationale": (
            "Street-art mini-drama, no audio requested."
        ),
        "intents": [
            "Write the street-art story of the graffiti artist being exploited by the gallery owner.",
            "Break the story into art-world scenes with discovery and betrayal beats.",
            "Design key frames for street-art walls and gallery interiors.",
            "Render motion-video clips preserving the street-art aesthetic.",
            "Compose the final street-art mini-drama assembly.",
        ],
    },
    {
        "user_goal": "Make a disaster-rescue mini-drama about a helicopter pilot airlifting survivors from a collapsed mine shaft.",
        "rationale": (
            "Disaster-rescue drama, no audio requested."
        ),
        "intents": [
            "Write the disaster-rescue story of the helicopter pilot airlifting mine survivors.",
            "Break the story into rescue scenes with escalating urgency.",
            "Design key frames for the collapsed mine and rescue helicopter.",
            "Render motion-video clips preserving the rescue tension.",
            "Compose the final disaster-rescue mini-drama assembly.",
        ],
    },
    {
        "user_goal": "Make a werewolf-love mini-drama about a human woman falling in love with the alpha of a northern pack.",
        "rationale": (
            "Werewolf-love supernatural drama, no audio requested."
        ),
        "intents": [
            "Write the werewolf-love story of the woman and northern-pack alpha.",
            "Break the story into werewolf-romance scenes with transformation and acceptance beats.",
            "Design key frames for the northern pack and werewolf transformations.",
            "Render motion-video clips preserving supernatural-romance continuity.",
            "Compose the final werewolf mini-drama assembly.",
        ],
    },
    {
        "user_goal": "Make a magic-school mini-drama about a first-year student who accidentally summons an ancient spirit that only she can see.",
        "rationale": (
            "Magic-school fantasy drama, no audio requested."
        ),
        "intents": [
            "Write the magic-school story of the first-year summoning the ancient spirit.",
            "Break the story into magic-school scenes across lessons, dorms, and secret encounters.",
            "Design key frames for the magic academy and spirit manifestations.",
            "Render motion-video clips preserving magic-school continuity.",
            "Compose the final magic-school mini-drama assembly.",
        ],
    },
    {
        "user_goal": "Make a mountaineer mini-drama about two estranged siblings forced to climb K2 together to fulfill their father's last wish.",
        "rationale": (
            "Mountaineer family drama, no audio requested."
        ),
        "intents": [
            "Write the mountaineer story of estranged siblings climbing K2 together.",
            "Break the story into sibling-reconciliation climbing scenes.",
            "Design key frames for the K2 ascent stages.",
            "Render motion-video clips preserving mountaineer intensity.",
            "Compose the final mountaineer mini-drama assembly.",
        ],
    },
    {
        "user_goal": "Make a deep-sea mini-drama about a marine biologist encountering a previously unknown species in a trench expedition.",
        "rationale": (
            "Deep-sea expedition drama, no audio requested."
        ),
        "intents": [
            "Write the deep-sea story of the marine biologist discovering the unknown species.",
            "Break the story into expedition scenes across the research vessel and trench descent.",
            "Design key frames for the submarine interior and trench environment.",
            "Render motion-video clips preserving the deep-sea tension.",
            "Compose the final deep-sea mini-drama assembly.",
        ],
    },
    {
        "user_goal": "Make a stage-actor mini-drama about a Broadway veteran who takes a final role in a small-town community theater.",
        "rationale": (
            "Stage-actor drama, no audio requested."
        ),
        "intents": [
            "Write the stage-actor story of the Broadway veteran's last small-town role.",
            "Break the story into theater-drama scenes with rehearsal and opening-night beats.",
            "Design key frames for the small-town theater and veteran actor.",
            "Render motion-video clips preserving the theater-drama continuity.",
            "Compose the final stage-actor mini-drama assembly.",
        ],
    },
    {
        "user_goal": "Make a young-composer mini-drama about a music student who inherits a mysterious score from her dying grandfather.",
        "rationale": (
            "Young-composer heritage drama, no audio requested."
        ),
        "intents": [
            "Write the young-composer story of inheriting the mysterious score from her grandfather.",
            "Break the story into music-heritage scenes across rehearsal and discovery.",
            "Design key frames for the music-studio and heritage manuscript.",
            "Render motion-video clips preserving the young-composer tone.",
            "Compose the final young-composer mini-drama assembly.",
        ],
    },
    {
        "user_goal": "Make a circus-troupe mini-drama about a trapeze artist who must convince her estranged twin to return to the family circus.",
        "rationale": (
            "Circus-troupe family drama, no audio requested."
        ),
        "intents": [
            "Write the circus-troupe story of the trapeze artist and her estranged twin.",
            "Break the story into circus-reconciliation scenes across big tops and travel.",
            "Design key frames for the circus big top and twin dynamics.",
            "Render motion-video clips preserving circus-family continuity.",
            "Compose the final circus mini-drama assembly.",
        ],
    },
    {
        "user_goal": "Make a cooking-journey mini-drama about a young chef traveling through Europe to win back her famous mother's approval.",
        "rationale": (
            "Cooking-journey drama, no audio requested."
        ),
        "intents": [
            "Write the cooking-journey story of the young chef's European pilgrimage.",
            "Break the story into culinary-journey scenes across European kitchens.",
            "Design key frames for each European destination and signature dish.",
            "Render motion-video clips preserving the cooking-journey continuity.",
            "Compose the final cooking mini-drama assembly.",
        ],
    },
    {
        "user_goal": "Make a high-school-rivalry mini-drama about two debate-team captains who slowly fall for each other despite being fierce rivals.",
        "rationale": (
            "High-school debate rivalry-to-romance drama, no audio requested."
        ),
        "intents": [
            "Write the high-school-rivalry story of the debate captains falling in love.",
            "Break the story into debate-rivalry-to-romance scenes.",
            "Design key frames for the debate-team classroom and tournament arena.",
            "Render motion-video clips preserving the high-school-drama continuity.",
            "Compose the final high-school mini-drama assembly.",
        ],
    },
]
