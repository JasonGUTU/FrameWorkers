"""GRPO shape: cr_compositor_only — Story → Screenplay → KeyFrame → Video → Compositor.

50 short-brief samples (target_n=80; remaining 30 go in shape_cr_compositor_only_long.py).
Cinematic mini-drama with NO audio overlay requested. Topics span genre/era/protagonist
combinations distinct from SFT shape_cr_compositor_only.py. Rationale style mirrors SFT
cr_* pattern: long flow narrative naming all chain agents + standard reject list.
"""
from __future__ import annotations


_REJECT = (
    "Reject MusicAgent / AmbienceAgent / AudioMixAgent (no audio overlay requested), "
    "TranscriptionAgent / TranslationAgent (no subtitles), VideoAnalysisAgent / "
    "IntakeVideoAgent / StyleTransferAgent / VideoExtendAgent / HighlightAgent (no "
    "video uploaded), NarrationAgent / IllustrationAgent / NarratorAgent (not a "
    "slideshow / illustrated-storytelling format)."
)


def _make(theme, blueprint_arc, scene_break, keyframe_settings, render_aesthetic,
          composite_descriptor):
    """Boilerplate for one cr_compositor_only sample."""
    return {
        "rationale": (
            f"{theme} mini-drama from a text brief, no audio overlay. StoryAgent drafts "
            f"the {blueprint_arc} blueprint. ScreenplayAgent breaks it into {scene_break} "
            f"scenes. KeyFrameAgent plans keyframes for the {keyframe_settings} settings "
            f"from text alone. VideoAgent assembles the multi-shot film. CompositorAgent "
            f"muxes the final mp4 with inter-shot transitions. " + _REJECT
        ),
        "intents": [
            f"Draft the {theme} story blueprint — {blueprint_arc} arc.",
            f"Decompose the {blueprint_arc} arc into {scene_break} scenes.",
            f"Plan keyframes for the {keyframe_settings} settings; text-only generation, no reference images supplied.",
            f"Render per-shot clips preserving {render_aesthetic} visual continuity.",
            f"Composite the final {composite_descriptor} mp4 with inter-shot transitions.",
        ],
    }


SAMPLES: list[dict] = [
    {**_make(
        theme="Wuxia revenge", blueprint_arc="disciple-avenges-master / sect-betrayal",
        scene_break="wuxia revenge", keyframe_settings="ancient-temple / bamboo-forest / sect-confrontation",
        render_aesthetic="wuxia revenge", composite_descriptor="wuxia revenge mini-drama",
    ), "user_goal": "Make a wuxia mini-drama about a junior disciple who tracks down the rival sect that murdered his master and takes the master's stolen sword back."},
    {**_make(
        theme="Royal-bloodline awakening fantasy", blueprint_arc="forgotten-prince hidden-bloodline / kingdom-restoration",
        scene_break="royal-bloodline awakening", keyframe_settings="hidden-village / royal-archive / coronation-throne",
        render_aesthetic="fantasy royal-bloodline", composite_descriptor="royal-bloodline fantasy mini-drama",
    ), "user_goal": "Produce a fantasy mini-drama about a forgotten prince raised in a hidden village who discovers his royal bloodline and reclaims the kingdom from a tyrant uncle."},
    {**_make(
        theme="Underdog MMA-comeback", blueprint_arc="street-fighter / scout-discovery / amateur-title-bid",
        scene_break="MMA underdog", keyframe_settings="back-alley fight ring / pro-gym / championship cage",
        render_aesthetic="MMA underdog", composite_descriptor="MMA underdog mini-drama",
    ), "user_goal": "Make an MMA underdog mini-drama about a self-taught street fighter discovered by a washed-up scout who guides her to an amateur title shot."},
    {**_make(
        theme="1920s NYC noir-detective", blueprint_arc="weary-detective / serial-killer-pattern / showdown",
        scene_break="1920s noir", keyframe_settings="speakeasy / precinct / abandoned warehouse climax",
        render_aesthetic="1920s noir-detective", composite_descriptor="1920s noir-detective mini-drama",
    ), "user_goal": "Produce a 1920s NYC noir mini-drama where a weary detective uncovers the pattern behind a string of murders targeting jazz singers and walks into a final-act showdown."},
    {**_make(
        theme="Open-sea survival", blueprint_arc="shipwrecked-couple / makeshift-raft / dwindling-rations",
        scene_break="open-sea survival", keyframe_settings="capsized yacht deck / makeshift raft / open ocean horizon",
        render_aesthetic="open-sea survival", composite_descriptor="open-sea survival mini-drama",
    ), "user_goal": "Make a survival-at-sea mini-drama about a vacationing couple whose yacht capsizes in a storm and who must build a raft from debris and ration the last of their water."},
    {**_make(
        theme="Olympic-comeback sports", blueprint_arc="injured-athlete-rehab / coach-doubts / final-trial",
        scene_break="Olympic comeback", keyframe_settings="rehab clinic / training track / Olympic-trial stadium",
        render_aesthetic="Olympic-comeback sports", composite_descriptor="Olympic-comeback mini-drama",
    ), "user_goal": "Produce an Olympic-comeback mini-drama about a sprinter who shattered her ankle two years ago, returns to her old coach who doubts her, and races for a place at the Trials."},
    {**_make(
        theme="Embassy-conspiracy spy thriller", blueprint_arc="junior-cultural-attache / foreign-asset / leak-trail",
        scene_break="embassy spy", keyframe_settings="embassy ballroom / dead-drop alley / interrogation room",
        render_aesthetic="embassy spy thriller", composite_descriptor="embassy spy mini-drama",
    ), "user_goal": "Make a spy thriller mini-drama about a junior cultural attaché in a foreign embassy who realizes a suspected asset is leaking classified material to the host country."},
    {**_make(
        theme="Amazon-jungle expedition", blueprint_arc="lost-tribe seeker / hostile terrain / discovery",
        scene_break="Amazon expedition", keyframe_settings="riverboat / dense jungle / hidden village clearing",
        render_aesthetic="Amazon-jungle expedition", composite_descriptor="Amazon-expedition mini-drama",
    ), "user_goal": "Produce an exploration mini-drama where a young anthropologist leads a four-person expedition deep into the Amazon to find a tribe believed to have vanished a century ago."},
    {**_make(
        theme="Cyberpunk neo-Tokyo samurai", blueprint_arc="corporate-bodyguard cybernetic-samurai / hacker-fugitive / showdown",
        scene_break="cyberpunk samurai", keyframe_settings="neon street / corporate-tower top floor / underground sewer-arena",
        render_aesthetic="cyberpunk samurai", composite_descriptor="cyberpunk-samurai mini-drama",
    ), "user_goal": "Make a cyberpunk mini-drama set in 2080s neo-Tokyo about a cybernetic samurai contracted as a bodyguard who breaks her contract to protect a hacker fugitive she was meant to capture."},
    {**_make(
        theme="Witch-apprentice fantasy", blueprint_arc="young-witch / cursed-village / ancient-curse-source",
        scene_break="witch-apprentice fantasy", keyframe_settings="cottage workshop / cursed forest / ancient stone circle",
        render_aesthetic="witch-apprentice fantasy", composite_descriptor="witch-apprentice mini-drama",
    ), "user_goal": "Produce a fantasy mini-drama about a witch's young apprentice who agrees to lift a curse from a neighboring village only to discover the curse's source is bound to her own bloodline."},
    {**_make(
        theme="Civil-War battlefield-medic", blueprint_arc="medic-tending-both-sides / spy-accusation / battlefield-final",
        scene_break="Civil-War medic", keyframe_settings="field hospital tent / battlefield trench / commander's tent",
        render_aesthetic="Civil-War medic", composite_descriptor="Civil-War medic mini-drama",
    ), "user_goal": "Make a Civil-War mini-drama about a battlefield medic who treats wounded soldiers on both Union and Confederate sides and is accused of spying when his neutrality is exposed."},
    {**_make(
        theme="Music-prodigy stage-fright", blueprint_arc="violinist / panic-attacks / mentor-confrontation",
        scene_break="music-prodigy", keyframe_settings="conservatory practice room / packed concert hall / mentor's studio",
        render_aesthetic="music-prodigy", composite_descriptor="music-prodigy mini-drama",
    ), "user_goal": "Produce a music-prodigy mini-drama about a teen violinist who freezes mid-performance at her debut concerto and must confront the mentor whose pressure caused the panic attacks."},
    {**_make(
        theme="Mountain-rescue avalanche", blueprint_arc="rescue-team / avalanche-zone / trapped-climbers",
        scene_break="mountain-rescue", keyframe_settings="ranger station / avalanche slope / trapped climber's snow cave",
        render_aesthetic="mountain-rescue", composite_descriptor="mountain-rescue mini-drama",
    ), "user_goal": "Make a mountain-rescue mini-drama about a four-person avalanche-response team racing to reach a pair of trapped climbers before a second slide buries the slope."},
    {**_make(
        theme="Whistleblower-hacker corporate-thriller", blueprint_arc="junior-hacker / corporate-fraud / exposure-deadline",
        scene_break="whistleblower-hacker", keyframe_settings="open-plan tech office / late-night data-center / press-room reveal",
        render_aesthetic="whistleblower-hacker", composite_descriptor="whistleblower-hacker mini-drama",
    ), "user_goal": "Produce a corporate thriller mini-drama about a junior security engineer who uncovers her company's accounting fraud and races to leak the proof to a journalist before legal hits her with an injunction."},
    {**_make(
        theme="Time-loop survivor", blueprint_arc="time-loop / same-day / break-pattern-discovery",
        scene_break="time-loop", keyframe_settings="apartment alarm clock / coffee shop / fatal-collision intersection",
        render_aesthetic="time-loop survivor", composite_descriptor="time-loop mini-drama",
    ), "user_goal": "Make a time-loop mini-drama about an architecture student who keeps reliving the same Wednesday — the day she dies in a traffic collision — and must figure out why the loop won't break."},
    {**_make(
        theme="Boxer's-daughter legacy", blueprint_arc="amateur-boxer-daughter / father-arena-record / weighing-her-name",
        scene_break="boxing-legacy", keyframe_settings="father's old gym / amateur tournament / commentary-booth interview",
        render_aesthetic="boxing-legacy", composite_descriptor="boxing-legacy mini-drama",
    ), "user_goal": "Produce a boxing-legacy mini-drama about a young amateur boxer who fights under her late father's last name and must decide whether to keep that name when her own career starts diverging from his."},
    {**_make(
        theme="Lunar-mining-colony survival", blueprint_arc="stranded-engineer / dwindling-oxygen / rescue-radio",
        scene_break="lunar-survival", keyframe_settings="lunar habitat module / cratered surface / collapsed mining-tunnel",
        render_aesthetic="lunar-mining survival", composite_descriptor="lunar-mining survival mini-drama",
    ), "user_goal": "Make a sci-fi survival mini-drama about a junior engineer stranded on a small lunar mining colony after a collapse — she has 72 hours of oxygen left and the rescue ship is six days out."},
    {**_make(
        theme="Magic-school awakening fantasy", blueprint_arc="bullied-student / latent-magic-awakening / standoff-with-bully",
        scene_break="magic-school", keyframe_settings="dorm room / cobbled magic-school courtyard / spell-duel chamber",
        render_aesthetic="magic-school awakening", composite_descriptor="magic-school mini-drama",
    ), "user_goal": "Produce a fantasy mini-drama set at a remote magic school about a bullied second-year student whose latent talent suddenly awakens — and who must decide whether to use it on the bullies or hide it again."},
    {**_make(
        theme="Behind-enemy-lines special-forces", blueprint_arc="four-person-team / extraction-blown / fight-out",
        scene_break="special-forces", keyframe_settings="enemy compound / forest exfil route / extraction LZ",
        render_aesthetic="special-forces tactical", composite_descriptor="special-forces mini-drama",
    ), "user_goal": "Make a tactical mini-drama about a four-person special forces team whose extraction goes wrong behind enemy lines and who must fight their way to a backup landing zone before dawn."},
    {**_make(
        theme="Galactic rebel-pilot", blueprint_arc="conscripted-pilot / rebel-defection / dogfight-finale",
        scene_break="galactic rebel-pilot", keyframe_settings="imperial fighter hangar / rebel asteroid base / asteroid-belt dogfight",
        render_aesthetic="galactic rebel-pilot", composite_descriptor="galactic-rebel mini-drama",
    ), "user_goal": "Produce a galactic-war mini-drama about a conscripted imperial fighter pilot who defects mid-mission and must survive a dogfight against her own former wingmen to reach a rebel base."},
    {**_make(
        theme="Family-restaurant gentrification fight", blueprint_arc="chef-daughter / failing-family-restaurant / developer-buyout-pressure",
        scene_break="family-restaurant", keyframe_settings="cramped restaurant kitchen / city-hall hearing / packed reopening night",
        render_aesthetic="family-restaurant", composite_descriptor="family-restaurant mini-drama",
    ), "user_goal": "Make a family-drama mini-drama about a chef who returns home to save her parents' Korean restaurant from a developer-driven gentrification buyout that's pushing the whole block out."},
    {**_make(
        theme="Apprentice-bladesmith legendary-weapon", blueprint_arc="apprentice / forging-legendary-blade / master-test",
        scene_break="apprentice-bladesmith", keyframe_settings="smithy forge / mountain-ore mine / master's test arena",
        render_aesthetic="apprentice-bladesmith fantasy", composite_descriptor="apprentice-bladesmith mini-drama",
    ), "user_goal": "Produce a fantasy mini-drama about a young bladesmith's apprentice who insists on forging a legendary weapon her master deems too dangerous, and must pass his trial to prove she can wield it."},
    {**_make(
        theme="Storm-chaser tornado-record", blueprint_arc="storm-chaser team / record-breaking F5 / split-second escape",
        scene_break="storm-chaser", keyframe_settings="storm-chaser truck / open prairie / wreckage aftermath",
        render_aesthetic="storm-chaser", composite_descriptor="storm-chaser mini-drama",
    ), "user_goal": "Make a storm-chaser mini-drama about a three-person team pursuing what radar predicts will be the largest tornado on record, with only one of them old enough to know how F5s really behave."},
    {**_make(
        theme="Victorian-London vampire-detective", blueprint_arc="vampire-detective / serial-throat-killings / suspect-coven",
        scene_break="Victorian-London vampire-detective", keyframe_settings="gas-lit cobbled street / morgue / vampire-coven crypt",
        render_aesthetic="Victorian-London vampire-detective", composite_descriptor="vampire-detective mini-drama",
    ), "user_goal": "Produce a Victorian-London mini-drama about a vampire detective working with Scotland Yard who realizes the throat-killings she's been called to solve trace back to her own coven."},
    {**_make(
        theme="Pirate-captain royal-navy chase", blueprint_arc="pirate-captain / pursued-by-royal-navy / final-naval-duel",
        scene_break="pirate-pursuit", keyframe_settings="pirate ship deck / Caribbean port / open-ocean naval duel",
        render_aesthetic="pirate naval-pursuit", composite_descriptor="pirate naval-pursuit mini-drama",
    ), "user_goal": "Make a pirate mini-drama about a captain who learned her trade from a royal-navy father and is now hunted by his old fleet — leading to a final ship-to-ship duel against her former mentor."},
    {**_make(
        theme="1850s Kyoto geisha", blueprint_arc="apprentice-geisha / okiya-rivalry / debut-night",
        scene_break="1850s-Kyoto geisha", keyframe_settings="okiya tea-house / rehearsal hall / debut-night banquet",
        render_aesthetic="1850s-Kyoto geisha", composite_descriptor="apprentice-geisha mini-drama",
    ), "user_goal": "Produce an 1850s Kyoto mini-drama about an apprentice geisha navigating the rivalries inside her okiya as her debut night approaches and a rival senior tries to sabotage her."},
    {**_make(
        theme="Eastern-war dragon-rider fantasy", blueprint_arc="rider-trainee / bonded-dragon / first-skirmish",
        scene_break="dragon-rider", keyframe_settings="mountain dragon-aerie / training arena / eastern-front skirmish ridge",
        render_aesthetic="dragon-rider fantasy", composite_descriptor="dragon-rider mini-drama",
    ), "user_goal": "Make a fantasy mini-drama about a rider trainee whose bonded dragon is younger and smaller than the others — and who must lead her wing into its first skirmish on the eastern front."},
    {**_make(
        theme="Exiled-prince rebellion", blueprint_arc="exiled-prince / loyalist-recruitment / first-territory-strike",
        scene_break="exiled-prince rebellion", keyframe_settings="rebel hideout / loyalist-recruitment town / first-territory siege",
        render_aesthetic="exiled-prince rebellion", composite_descriptor="exiled-prince rebellion mini-drama",
    ), "user_goal": "Produce a fantasy mini-drama about an exiled prince who returns to his homeland to recruit loyalists, hoping a successful strike on the usurper's first border keep will gain him momentum."},
    {**_make(
        theme="Haunted-hotel ghost-hunt", blueprint_arc="paranormal-investigator team / haunted-hotel-history / final-séance",
        scene_break="haunted-hotel", keyframe_settings="grand-hotel lobby / sealed sub-basement / final-séance suite",
        render_aesthetic="haunted-hotel", composite_descriptor="haunted-hotel mini-drama",
    ), "user_goal": "Make a haunted-hotel mini-drama about a three-person paranormal team investigating a long-shuttered grand hotel where every previous owner has died, and the séance reveals more than they bargained for."},
    {**_make(
        theme="Holy-grail knight-quest", blueprint_arc="disgraced-knight / grail-quest / hermitage-revelation",
        scene_break="holy-grail quest", keyframe_settings="ruined chapel / haunted forest / hermitage cave",
        render_aesthetic="holy-grail quest", composite_descriptor="holy-grail quest mini-drama",
    ), "user_goal": "Produce a medieval mini-drama about a disgraced knight sent on the holy-grail quest as penance, who finds the hermit at journey's end is the man whose name he was disgraced for tarnishing."},
    {**_make(
        theme="Mecha-pilot kaiju-defense", blueprint_arc="rookie-pilot / kaiju-incursion / city-defense",
        scene_break="mecha kaiju", keyframe_settings="mecha-hangar / harbor-front kaiju emergence / final cityscape battle",
        render_aesthetic="mecha kaiju-defense", composite_descriptor="mecha kaiju-defense mini-drama",
    ), "user_goal": "Make a mecha mini-drama about a rookie pilot scrambling on her first deployment when a kaiju emerges in the harbor — every senior pilot is offline, so it's her or no one."},
    {**_make(
        theme="Galactic bounty-hunter chase", blueprint_arc="bounty-hunter / fugitive-with-secret / final-confrontation",
        scene_break="galactic bounty-hunter", keyframe_settings="frontier cantina / asteroid-belt chase / fugitive's last refuge",
        render_aesthetic="galactic bounty-hunter", composite_descriptor="galactic bounty-hunter mini-drama",
    ), "user_goal": "Produce a galactic mini-drama about a bounty hunter chasing a fugitive across three planets only to learn the fugitive is carrying intel that justifies why the empire wants her silenced."},
    {**_make(
        theme="Caver unmapped-cave survival", blueprint_arc="solo-caver / collapse / unknown-passage exit",
        scene_break="cave-survival", keyframe_settings="cave-mouth entrance / collapsed-passage chamber / lit exit aperture",
        render_aesthetic="cave-survival", composite_descriptor="cave-survival mini-drama",
    ), "user_goal": "Make a survival mini-drama about a solo caver trapped in an unmapped passage after a roof collapse — radio dead, water dwindling, must find an alternate exit through tunnels no one has charted."},
    {**_make(
        theme="Forensic-scientist cold-case", blueprint_arc="forensic-scientist / decades-old cold-case / decisive-evidence",
        scene_break="forensic cold-case", keyframe_settings="forensic lab / archive evidence-vault / suspect-confrontation interview room",
        render_aesthetic="forensic cold-case", composite_descriptor="forensic cold-case mini-drama",
    ), "user_goal": "Produce a forensic mini-drama about a scientist reopening her grandmother's unsolved 1972 case using techniques that didn't exist then — and walking into the suspect's still-living door."},
    {**_make(
        theme="Amish-to-worldly transition", blueprint_arc="Amish-youth / Rumspringa / outside-world choice",
        scene_break="Amish-Rumspringa", keyframe_settings="Amish farm / city street / family-front-porch return-or-leave decision",
        render_aesthetic="Amish-Rumspringa coming-of-age", composite_descriptor="Amish-Rumspringa mini-drama",
    ), "user_goal": "Make a coming-of-age mini-drama about an Amish boy on Rumspringa navigating a city he doesn't understand, deciding by season's end whether to return home or live outside."},
    {**_make(
        theme="War-zone redemption surgeon", blueprint_arc="disgraced-surgeon / volunteer-clinic in-war-zone / final-surgery-redemption",
        scene_break="war-zone surgeon", keyframe_settings="bombed clinic / front-line tent / city under shellfire",
        render_aesthetic="war-zone surgeon", composite_descriptor="war-zone surgeon mini-drama",
    ), "user_goal": "Produce a redemption mini-drama about a surgeon who lost her license after a malpractice scandal, volunteers in a war-zone clinic, and saves a life that costs her former accuser everything."},
    {**_make(
        theme="Vatican-vault heist", blueprint_arc="five-person heist-crew / Vatican-vault / patron-betrayal",
        scene_break="Vatican-vault heist", keyframe_settings="St-Peter's basilica / sub-Vatican-vault corridor / extraction rooftop",
        render_aesthetic="Vatican-vault heist", composite_descriptor="Vatican-vault heist mini-drama",
    ), "user_goal": "Make a heist mini-drama about a five-person crew breaking into the Vatican's restricted vault to recover a relic — and finding their patron has set them up to take the fall."},
    {**_make(
        theme="Endangered-species ranger", blueprint_arc="park-ranger / poacher-syndicate / standoff",
        scene_break="endangered-species ranger", keyframe_settings="ranger outpost / dense rainforest patrol / poacher-camp standoff",
        render_aesthetic="endangered-species ranger", composite_descriptor="endangered-species ranger mini-drama",
    ), "user_goal": "Produce a wildlife mini-drama about a park ranger who realizes the poacher syndicate hunting her tigers is bankrolled by the same lodge owner whose donation pays the ranger station's bills."},
    {**_make(
        theme="Oregon-Trail pioneer wagon-train", blueprint_arc="wagon-train / mountain-pass / decisive-river-ford",
        scene_break="Oregon-Trail pioneer", keyframe_settings="prairie-camp circle / mountain-pass snowline / river-ford crossing",
        render_aesthetic="Oregon-Trail pioneer", composite_descriptor="Oregon-Trail pioneer mini-drama",
    ), "user_goal": "Make a pioneer mini-drama about a 19-year-old daughter forced to lead her family's wagon along the Oregon Trail after her father dies of cholera, with the river-ford crossing the make-or-break test."},
    {**_make(
        theme="Underground street-racing championship", blueprint_arc="rookie-racer / underground-circuit / championship-final",
        scene_break="underground street-race", keyframe_settings="underground garage / industrial-district race-strip / championship-finale circuit",
        render_aesthetic="underground street-race", composite_descriptor="underground street-race mini-drama",
    ), "user_goal": "Produce a street-racing mini-drama about a rookie driver moving up an underground championship ladder she promised her dying brother she'd win — and meeting his old rival in the final."},
    {**_make(
        theme="Banned-books smuggling", blueprint_arc="border-courier / banned-books / regime-checkpoint",
        scene_break="banned-books smuggling", keyframe_settings="hidden printing-press cellar / mountain border crossing / urban underground meeting",
        render_aesthetic="banned-books smuggling", composite_descriptor="banned-books smuggling mini-drama",
    ), "user_goal": "Make a dystopian mini-drama about a courier smuggling banned literature across an authoritarian-state border — discovering at the final checkpoint that her contact is regime-compromised."},
    {**_make(
        theme="Lighthouse-keeper haunting", blueprint_arc="lone-keeper / shipwreck-ghosts / lantern-final-night",
        scene_break="lighthouse-haunting", keyframe_settings="lighthouse-keeper cottage / cliff-side rocks / lantern room at night",
        render_aesthetic="lighthouse-haunting", composite_descriptor="lighthouse-haunting mini-drama",
    ), "user_goal": "Produce a horror mini-drama about a lone lighthouse keeper assigned to a remote post that's been crewed twelve different times — every previous keeper went mad — as the ghosts of the wrecked ship return."},
    {**_make(
        theme="Salem witch-tribunal", blueprint_arc="accused-village-girl / tribunal / community-collapse",
        scene_break="Salem witch-tribunal", keyframe_settings="meeting-house tribunal / village street / courtroom of pressed accusers",
        render_aesthetic="Salem witch-tribunal", composite_descriptor="Salem witch-tribunal mini-drama",
    ), "user_goal": "Make a Salem witch-trial mini-drama about a 17-year-old village girl accused by her own cousin's daughter, watching the tribunal devour the community as she awaits the testimony that will hang or save her."},
    {**_make(
        theme="WW2 Atlantic submarine", blueprint_arc="submarine-commander / convoy-engagement / depth-charge survival",
        scene_break="WW2 submarine", keyframe_settings="submarine control-room / convoy-attack periscope / sinking-bottom survival",
        render_aesthetic="WW2 submarine", composite_descriptor="WW2 submarine mini-drama",
    ), "user_goal": "Produce a WW2 mini-drama about a U-boat commander whose attack on a Canadian convoy goes wrong when destroyers force her boat to the sea floor — silent running until the depth charges fade or run out."},
    {**_make(
        theme="Reluctant-hero village-bandit defense", blueprint_arc="reluctant-fighter / village-defense / bandit-leader-final-duel",
        scene_break="reluctant-hero village-defense", keyframe_settings="village square / bandit camp / final wheat-field duel",
        render_aesthetic="reluctant-hero village-defense", composite_descriptor="reluctant-hero village-defense mini-drama",
    ), "user_goal": "Make a frontier mini-drama about a former soldier hiding in a small village she once fought to liberate — when bandits return demanding tribute, she must decide whether to draw her gun again."},
    {**_make(
        theme="Reincarnated-soul childhood-home", blueprint_arc="adult-with-past-life-memories / childhood-home / reckoning",
        scene_break="reincarnation-childhood-home", keyframe_settings="adult apartment / childhood home exterior / attic of recovered memories",
        render_aesthetic="reincarnation-childhood-home", composite_descriptor="reincarnation-childhood-home mini-drama",
    ), "user_goal": "Produce a quiet supernatural mini-drama about an adult woman who keeps dreaming of a childhood that wasn't hers — and travels to a small town she's never visited to find the house she remembers exactly."},
    {**_make(
        theme="1960s-Paris aspiring writer", blueprint_arc="young-American writer / left-bank cafe-circle / breakout-novel",
        scene_break="1960s-Paris writer", keyframe_settings="Left Bank cafe / cramped flat / publisher's office",
        render_aesthetic="1960s-Paris writer", composite_descriptor="1960s-Paris writer mini-drama",
    ), "user_goal": "Make a 1960s Paris mini-drama about a young American writer who joins a Left Bank café circle of better-known novelists and must risk her friendships to publish the manuscript that exposes them."},
    {**_make(
        theme="Pacific-theater code-talker", blueprint_arc="Native code-talker / coded-radio mission / island-final-stand",
        scene_break="Pacific-code-talker", keyframe_settings="boot-camp radio classroom / Pacific-island jungle / final-stand bunker",
        render_aesthetic="Pacific-code-talker", composite_descriptor="Pacific-code-talker mini-drama",
    ), "user_goal": "Produce a WW2 Pacific-theater mini-drama about a young Navajo code-talker whose unit is overrun on a contested island, who must keep transmitting the language her grandfather taught her until reinforcements arrive."},
    {**_make(
        theme="Sushi-master apprentice", blueprint_arc="Tokyo-master sushi-chef / Western apprentice / final-omakase test",
        scene_break="sushi-master apprentice", keyframe_settings="back-alley Tokyo restaurant / pre-dawn Tsukiji fish market / final-omakase counter",
        render_aesthetic="sushi-master apprentice", composite_descriptor="sushi-master apprentice mini-drama",
    ), "user_goal": "Make a culinary mini-drama about a Western culinary-school graduate apprenticing under a Tokyo sushi master who refuses to teach her — until she earns the right to serve at his counter on omakase night."},
    {**_make(
        theme="Wildfire smoke-jumper", blueprint_arc="rookie-smoke-jumper / massive-blaze / family-cabin defense",
        scene_break="wildfire smoke-jumper", keyframe_settings="smoke-jumper plane / fire-line ridge / threatened family-cabin valley",
        render_aesthetic="wildfire smoke-jumper", composite_descriptor="wildfire smoke-jumper mini-drama",
    ), "user_goal": "Produce a wildfire mini-drama about a rookie smoke-jumper whose first major drop is into a fire heading directly toward the valley her family's cabin is in — and she's the only one near enough to hold the line."},
]
