"""Shape: extend_only — IntakeVideo → VideoExtend (raw extend output).

User uploaded a video and wants ONLY a longer version — no audio overlay,
no subtitle, no style change, no compositor pass.  Raw VideoExtendAgent
output is the deliverable.

Reject biases:
  - CompositorAgent (nothing to compose; raw extended clip IS the deliverable)
  - MusicAgent / AmbienceAgent / AudioMixAgent (no audio overlay)
  - TranscriptionAgent / TranslationAgent (no subtitle)
  - StyleTransferAgent (no style change)
  - VideoAnalysisAgent / HighlightAgent (no trimming)
"""
from __future__ import annotations

SAMPLES: list[dict] = [
    {
        "user_goal": "This is a 10-second clip of waves crashing — please extend it to about 30 seconds so I can use it as a background loop.",
        "rationale": (
            "User uploaded a 10-second wave clip and asks to extend it to ~30 seconds. "
            "IntakeVideoAgent ingests the short clip. VideoExtendAgent generates additional "
            "coherent frames continuing the wave motion. The raw extended clip is the deliverable "
            "— no Compositor pass needed since there is nothing to overlay. Reject MusicAgent / "
            "AmbienceAgent / AudioMixAgent (no audio overlay asked), TranscriptionAgent (no "
            "subtitles), StyleTransferAgent (no visual restyle), VideoAnalysisAgent / "
            "HighlightAgent (no trimming)."
        ),
        "intents": [
            "Ingest the 10-second wave-crashing clip into the workspace as the source video.",
            "Extend the wave clip from roughly 10 seconds out to ~30 seconds of continuous footage.",
        ],
    },
    {
        "user_goal": "Here's a short drone shot of a mountain ridge — please extend it by another 20 seconds in the same direction of motion.",
        "rationale": (
            "Short drone footage + request to extend ~20 seconds continuing the existing motion. "
            "IntakeVideoAgent loads the drone clip; VideoExtendAgent produces the continuation "
            "matching the flight path. Raw extended footage is the output — no compositor, no "
            "audio, no subtitles, no style transfer requested."
        ),
        "intents": [
            "Ingest the drone mountain-ridge clip into the workspace.",
            "Extend the drone footage another ~20 seconds preserving the original flight trajectory.",
        ],
    },
    {
        "user_goal": "I have a 5-second shot of a cat yawning. Please stretch it into about a 15-second piece where the cat's actions continue naturally.",
        "rationale": (
            "5-second cat clip + extend-to-15s request with natural continuation. "
            "IntakeVideoAgent ingests the clip. VideoExtendAgent generates continuation frames "
            "keeping the cat's motion consistent. The raw extended clip is the final asset. No "
            "audio, subtitle, style, or compositor needed."
        ),
        "intents": [
            "Ingest the 5-second cat-yawning clip into the workspace.",
            "Extend the cat clip to ~15 seconds so the animal's behavior continues naturally.",
        ],
    },
    {
        "user_goal": "Can you extend this short fireworks clip? It's about 8 seconds — stretch it to maybe 20 seconds with more bursts.",
        "rationale": (
            "8-second fireworks + extend-to-20s with additional bursts. IntakeVideoAgent ingests "
            "the fireworks clip. VideoExtendAgent generates further burst sequences continuing "
            "the pyrotechnics. The extended file is the deliverable — no overlay, subtitle, or "
            "restyle requested."
        ),
        "intents": [
            "Ingest the 8-second fireworks clip into the workspace.",
            "Extend the fireworks clip to ~20 seconds with additional coherent burst sequences.",
        ],
    },
    {
        "user_goal": "Please extend this skateboard trick clip — it's about 4 seconds and I need a 12-second version for a longer social post.",
        "rationale": (
            "4-second skate trick + extend-to-12s for social post. IntakeVideoAgent loads the "
            "trick clip. VideoExtendAgent continues the trick motion / landing / follow-through "
            "for the extra seconds. Raw extended clip is the deliverable. No audio, subtitle, "
            "style, or compositor requested."
        ),
        "intents": [
            "Ingest the 4-second skateboard trick clip into the workspace.",
            "Extend the trick clip to roughly 12 seconds so the motion and follow-through continue.",
        ],
    },
    {
        "user_goal": "I shot a short sunset timelapse — about 6 seconds. Please extend it to ~25 seconds with smooth continuation of the color shift.",
        "rationale": (
            "6-second sunset timelapse + extend-to-25s with smooth color shift continuation. "
            "IntakeVideoAgent loads the timelapse; VideoExtendAgent extrapolates additional "
            "frames preserving the color grade progression. Raw output is the final deliverable."
        ),
        "intents": [
            "Ingest the 6-second sunset timelapse into the workspace.",
            "Extend the timelapse to ~25 seconds with a smooth continuation of the color shift.",
        ],
    },
    {
        "user_goal": "This is a 7-second clip of a horse galloping across a field. Please extend to 20 seconds — same field, same horse, keep going.",
        "rationale": (
            "7-second horse gallop + extend-to-20s maintaining the field and subject. "
            "IntakeVideoAgent ingests the clip; VideoExtendAgent generates additional footage of "
            "the same horse continuing across the same field. No other modifications requested."
        ),
        "intents": [
            "Ingest the 7-second horse-galloping clip into the workspace.",
            "Extend the gallop to roughly 20 seconds with the same horse and field continuing.",
        ],
    },
    {
        "user_goal": "I have a short 3-second clip of a blooming flower. Please extend it to around 12 seconds so the flower fully opens on camera.",
        "rationale": (
            "3-second partial bloom clip + extend-to-12s showing the full opening. "
            "IntakeVideoAgent loads the clip. VideoExtendAgent continues the bloom motion "
            "through the full opening. Raw extended clip is the output — no audio, no SRT, no "
            "restyle."
        ),
        "intents": [
            "Ingest the 3-second blooming-flower clip into the workspace.",
            "Extend the bloom to ~12 seconds so the flower visibly opens fully on camera.",
        ],
    },
    {
        "user_goal": "Please extend this short shot of a candle flickering. It's maybe 5 seconds long — I need around 30 seconds of continuous flicker.",
        "rationale": (
            "5-second candle flicker + extend-to-30s continuous flicker. IntakeVideoAgent "
            "ingests the clip. VideoExtendAgent generates continuation frames preserving the "
            "flicker cadence. Raw extended clip is delivered as-is."
        ),
        "intents": [
            "Ingest the 5-second candle-flicker clip into the workspace.",
            "Extend the candle flicker to ~30 seconds of continuous, naturally varying flame motion.",
        ],
    },
    {
        "user_goal": "Here's a 4-second clip of a snowfall in the forest. Please extend to 18 seconds — same forest, snow keeps falling.",
        "rationale": (
            "4-second snowfall clip + extend-to-18s with snow continuing. IntakeVideoAgent "
            "loads the clip; VideoExtendAgent generates additional coherent snowfall frames in "
            "the same forest. Output is the raw extended clip."
        ),
        "intents": [
            "Ingest the 4-second forest-snowfall clip into the workspace.",
            "Extend the snowfall clip to ~18 seconds preserving the forest setting and snow motion.",
        ],
    },
    {
        "user_goal": "I have a brief 6-second shot of a city street at night with traffic. Please extend to 25 seconds with more passing cars.",
        "rationale": (
            "6-second night city-street traffic clip + extend-to-25s with more traffic. "
            "IntakeVideoAgent ingests the clip; VideoExtendAgent extrapolates additional passing "
            "vehicles consistent with the scene lighting. Raw extended clip is the deliverable."
        ),
        "intents": [
            "Ingest the 6-second night city-street traffic clip into the workspace.",
            "Extend the night-traffic footage to ~25 seconds with additional coherent passing vehicles.",
        ],
    },
    {
        "user_goal": "This short clip of a waterfall is just 5 seconds long. Please extend it to 30 seconds — same waterfall, same angle, keep the water flowing.",
        "rationale": (
            "5-second waterfall clip + extend-to-30s with same framing. IntakeVideoAgent loads "
            "the clip; VideoExtendAgent continues the water motion while holding the original "
            "camera angle and lighting. Output is the extended footage as-is."
        ),
        "intents": [
            "Ingest the 5-second waterfall clip into the workspace.",
            "Extend the waterfall footage to ~30 seconds with the same angle and continuous flow.",
        ],
    },
    {
        "user_goal": "Please stretch this clip of a dancer spinning — it's about 3 seconds. I want roughly 10 seconds with the motion continuing smoothly.",
        "rationale": (
            "3-second dancer-spin clip + extend-to-10s with smooth motion continuation. "
            "IntakeVideoAgent ingests the clip; VideoExtendAgent produces continuation frames "
            "preserving the rotation. Deliverable is the raw extended clip."
        ),
        "intents": [
            "Ingest the 3-second dancer-spinning clip into the workspace.",
            "Extend the dancer's spin to roughly 10 seconds with continuous, coherent motion.",
        ],
    },
    {
        "user_goal": "Extend this aerial beach shot for me — it's 8 seconds, needs to be around 25 seconds for my reel.",
        "rationale": (
            "8-second aerial beach footage + extend-to-25s. IntakeVideoAgent loads the clip; "
            "VideoExtendAgent generates additional aerial frames continuing the flight path and "
            "wave motion. Output is the raw extended clip."
        ),
        "intents": [
            "Ingest the 8-second aerial beach-shot clip into the workspace.",
            "Extend the aerial footage to ~25 seconds continuing the flight path and wave motion.",
        ],
    },
    {
        "user_goal": "I have a tiny 2-second clip of a bird taking off. Please extend it to 8 seconds — the bird should continue its flight arc.",
        "rationale": (
            "2-second bird takeoff + extend-to-8s with flight arc continuing. IntakeVideoAgent "
            "ingests the clip; VideoExtendAgent extrapolates the flight trajectory for the "
            "additional seconds. Raw extended clip is the deliverable."
        ),
        "intents": [
            "Ingest the 2-second bird-takeoff clip into the workspace.",
            "Extend the bird-takeoff footage to ~8 seconds continuing the flight arc smoothly.",
        ],
    },
    {
        "user_goal": "Please extend this 5-second shot of rainfall on a window — I need about 20 seconds of rainfall for a meditation video.",
        "rationale": (
            "5-second rain-on-window clip + extend-to-20s for meditation-video use. "
            "IntakeVideoAgent loads the clip; VideoExtendAgent produces ~15 more seconds of "
            "coherent rainfall. Raw extended output is the final asset — no audio overlay was "
            "requested; if a meditation soundtrack is wanted that would be a separate ask."
        ),
        "intents": [
            "Ingest the 5-second rain-on-window clip into the workspace.",
            "Extend the rain-on-window footage to ~20 seconds for meditation-video use.",
        ],
    },
    {
        "user_goal": "Please extend this short clip of a campfire burning — 6 seconds currently, stretch to 40 seconds with the flames continuing naturally.",
        "rationale": (
            "6-second campfire clip + extend-to-40s with natural flame continuation. "
            "IntakeVideoAgent ingests the clip. VideoExtendAgent generates additional flame-motion "
            "frames preserving fire dynamics. Output is the raw extended file."
        ),
        "intents": [
            "Ingest the 6-second campfire clip into the workspace.",
            "Extend the campfire clip to ~40 seconds with naturally continuing flame motion.",
        ],
    },
    {
        "user_goal": "I have a 5-second shot of clouds passing over a mountaintop. Please extend to ~30 seconds — same view, more clouds drifting by.",
        "rationale": (
            "5-second cloud-over-mountain timelapse + extend-to-30s continuing the drift. "
            "IntakeVideoAgent ingests the clip; VideoExtendAgent produces additional coherent "
            "cloud-drift frames preserving the viewpoint. Output is the extended clip."
        ),
        "intents": [
            "Ingest the 5-second cloud-over-mountain clip into the workspace.",
            "Extend the cloud-drift footage to ~30 seconds preserving the mountaintop viewpoint.",
        ],
    },
    {
        "user_goal": "Extend this city-skyline establishing shot — it's 7 seconds, I need a 20-second version for my opening sequence.",
        "rationale": (
            "7-second city-skyline establishing shot + extend-to-20s for opening-sequence use. "
            "IntakeVideoAgent ingests the clip. VideoExtendAgent produces continuation frames "
            "preserving the skyline framing and time-of-day. Raw extended clip is the deliverable."
        ),
        "intents": [
            "Ingest the 7-second city-skyline establishing shot into the workspace.",
            "Extend the skyline shot to roughly 20 seconds preserving framing and time-of-day lighting.",
        ],
    },
    {
        "user_goal": "This is a 10-second clip of a chef stirring a pot. Please extend it to about 30 seconds — same chef, same pot, stirring continues.",
        "rationale": (
            "10-second chef-stirring clip + extend-to-30s with continuity. IntakeVideoAgent "
            "loads the clip; VideoExtendAgent continues the stirring motion for the additional "
            "seconds. Output is the raw extended clip, nothing else overlaid."
        ),
        "intents": [
            "Ingest the 10-second chef-stirring-pot clip into the workspace.",
            "Extend the stirring footage to ~30 seconds preserving the chef, pot, and stirring motion.",
        ],
    },
    {
        "user_goal": "I have a 4-second clip of a steam-train puffing smoke. Please extend to 15 seconds with continuous smoke billows.",
        "rationale": (
            "4-second steam-train clip + extend-to-15s with continuing smoke. IntakeVideoAgent "
            "ingests the clip; VideoExtendAgent extrapolates additional coherent smoke / steam "
            "motion. Raw extended clip is the output."
        ),
        "intents": [
            "Ingest the 4-second steam-train clip into the workspace.",
            "Extend the steam-train footage to ~15 seconds with continuous smoke billows.",
        ],
    },
    {
        "user_goal": "Please extend this 8-second clip of koi fish swimming — I'd like about 25 seconds of koi swimming in the same pond.",
        "rationale": (
            "8-second koi-pond clip + extend-to-25s with koi continuing to swim. "
            "IntakeVideoAgent loads the clip; VideoExtendAgent produces coherent additional "
            "fish motion within the same pond. Output is the extended clip only."
        ),
        "intents": [
            "Ingest the 8-second koi-fish pond clip into the workspace.",
            "Extend the koi-pond footage to ~25 seconds with fish continuing to swim naturally.",
        ],
    },
    {
        "user_goal": "Please extend this 6-second clip of northern lights in the sky. Needs to be ~30 seconds with the aurora ribbon continuing to shift.",
        "rationale": (
            "6-second northern-lights clip + extend-to-30s with ribbon-shift continuation. "
            "IntakeVideoAgent ingests the clip; VideoExtendAgent generates additional aurora-motion "
            "frames preserving the spectral shift cadence. Raw extended output is delivered."
        ),
        "intents": [
            "Ingest the 6-second northern-lights clip into the workspace.",
            "Extend the aurora footage to ~30 seconds with the ribbon continuing to shift naturally.",
        ],
    },
    {
        "user_goal": "I have a 5-second shot of a dancer leaping mid-air, frozen for a moment. Please extend to ~12 seconds of her completing the leap and landing.",
        "rationale": (
            "5-second mid-leap dancer clip + extend-to-12s with leap completion and landing. "
            "IntakeVideoAgent ingests the clip. VideoExtendAgent continues the trajectory "
            "through to a natural landing pose. Output is the raw extended clip."
        ),
        "intents": [
            "Ingest the 5-second mid-leap dancer clip into the workspace.",
            "Extend the leap to ~12 seconds so the dancer completes the jump and lands naturally.",
        ],
    },
    {
        "user_goal": "This short clip is 3 seconds of a glass filling with water. Please extend it to about 10 seconds so the glass fully fills on camera.",
        "rationale": (
            "3-second partial glass-filling clip + extend-to-10s to fill completely. "
            "IntakeVideoAgent loads the clip; VideoExtendAgent continues the pour until the "
            "glass is full. Raw extended clip is the deliverable."
        ),
        "intents": [
            "Ingest the 3-second glass-filling clip into the workspace.",
            "Extend the glass-filling footage to ~10 seconds so the glass fully fills on camera.",
        ],
    },
    {
        "user_goal": "Extend this 6-second clip of a pendulum swinging — needs to be ~25 seconds of continuous swings for my physics lecture.",
        "rationale": (
            "6-second pendulum clip + extend-to-25s with continuous swing motion for a physics "
            "lecture. IntakeVideoAgent ingests the clip. VideoExtendAgent continues the "
            "pendulum's oscillation at the same rhythm. Output is the raw extended clip."
        ),
        "intents": [
            "Ingest the 6-second pendulum-swinging clip into the workspace.",
            "Extend the pendulum footage to ~25 seconds of continuous oscillation at the same rhythm.",
        ],
    },
    {
        "user_goal": "Please extend this 7-second clip of a cyclist riding down a forest path. I want 20 seconds with the rider continuing down the trail.",
        "rationale": (
            "7-second cyclist-on-trail clip + extend-to-20s with continuing ride. "
            "IntakeVideoAgent ingests the clip; VideoExtendAgent extrapolates the trail ride "
            "for the additional seconds preserving the forest setting. Raw extended clip is the "
            "deliverable."
        ),
        "intents": [
            "Ingest the 7-second cyclist-on-forest-trail clip into the workspace.",
            "Extend the cyclist-on-trail footage to ~20 seconds with the rider continuing down the path.",
        ],
    },
    {
        "user_goal": "I have a 4-second clip of paint being poured onto a canvas. Please extend to 12 seconds so the paint keeps spreading.",
        "rationale": (
            "4-second paint-pour clip + extend-to-12s with continued spreading. "
            "IntakeVideoAgent loads the clip; VideoExtendAgent continues the pour and resulting "
            "spread across the canvas for the extra seconds. Raw extended clip is the output."
        ),
        "intents": [
            "Ingest the 4-second paint-pour clip into the workspace.",
            "Extend the paint-pour footage to ~12 seconds with continuing spread across the canvas.",
        ],
    },
    {
        "user_goal": "Please extend this 5-second clip of lava flowing out of a volcano crater. I need ~20 seconds for a science documentary.",
        "rationale": (
            "5-second volcano lava clip + extend-to-20s for science-documentary use. "
            "IntakeVideoAgent ingests the clip. VideoExtendAgent produces continuation frames "
            "preserving the lava-flow dynamics and glow. Raw extended clip is the deliverable."
        ),
        "intents": [
            "Ingest the 5-second volcano lava-flow clip into the workspace.",
            "Extend the lava-flow footage to ~20 seconds with naturally continuing flow and glow.",
        ],
    },
    {
        "user_goal": "This 3-second clip shows a balloon being inflated. Please extend to about 10 seconds so the balloon fully inflates.",
        "rationale": (
            "3-second balloon-inflation clip + extend-to-10s to reach full inflation. "
            "IntakeVideoAgent ingests the clip; VideoExtendAgent continues the inflation motion "
            "through to the balloon's final expanded size. Output is the extended clip only."
        ),
        "intents": [
            "Ingest the 3-second balloon-inflation clip into the workspace.",
            "Extend the balloon-inflation footage to ~10 seconds so the balloon reaches full size.",
        ],
    },
    {
        "user_goal": "Please extend this 6-second clip of rain dripping off a rooftop. I want 25 seconds of steady drips for a lo-fi visual loop.",
        "rationale": (
            "6-second rain-dripping-rooftop clip + extend-to-25s for lo-fi loop use. "
            "IntakeVideoAgent loads the clip. VideoExtendAgent generates additional coherent "
            "drip sequences. Raw extended clip is the output — user didn't ask for audio, so "
            "no BGM / AudioMix / Compositor needed."
        ),
        "intents": [
            "Ingest the 6-second rain-dripping-rooftop clip into the workspace.",
            "Extend the rain-dripping footage to ~25 seconds with steady continuing drip motion.",
        ],
    },
    {
        "user_goal": "I have a 4-second clip of a ball bouncing on pavement. Please extend to 12 seconds so the ball continues bouncing naturally with decreasing height.",
        "rationale": (
            "4-second bouncing-ball clip + extend-to-12s with decreasing-height continuation. "
            "IntakeVideoAgent ingests the clip. VideoExtendAgent produces additional bounces "
            "with physically plausible amplitude decay. Raw extended output is the deliverable."
        ),
        "intents": [
            "Ingest the 4-second bouncing-ball-on-pavement clip into the workspace.",
            "Extend the ball's bouncing to ~12 seconds with naturally decreasing bounce height.",
        ],
    },
    {
        "user_goal": "This 5-second clip shows autumn leaves drifting from a tree. Please extend to 20 seconds with more leaves falling.",
        "rationale": (
            "5-second autumn-leaves clip + extend-to-20s with continuing leaf fall. "
            "IntakeVideoAgent ingests the clip; VideoExtendAgent generates additional leaves "
            "falling consistently with the scene's wind and lighting. Output is the raw extended "
            "clip."
        ),
        "intents": [
            "Ingest the 5-second autumn-leaves-falling clip into the workspace.",
            "Extend the leaves-falling footage to ~20 seconds with more leaves continuing to drift down.",
        ],
    },
    {
        "user_goal": "I have a 6-second clip of a hot-air balloon rising. Please extend to 25 seconds as it continues to climb.",
        "rationale": (
            "6-second hot-air balloon clip + extend-to-25s with climbing continuation. "
            "IntakeVideoAgent loads the clip; VideoExtendAgent continues the balloon's upward "
            "motion while preserving sky conditions. Raw extended clip is the deliverable."
        ),
        "intents": [
            "Ingest the 6-second hot-air-balloon clip into the workspace.",
            "Extend the balloon-rise footage to ~25 seconds with the balloon continuing to climb.",
        ],
    },
    {
        "user_goal": "Please extend this 7-second clip of a river flowing through a rocky bed. I need ~20 seconds for a nature reel.",
        "rationale": (
            "7-second river clip + extend-to-20s for nature-reel use. IntakeVideoAgent ingests "
            "the clip. VideoExtendAgent produces additional coherent river-flow footage "
            "preserving rock and water-light details. Output is the raw extended clip only."
        ),
        "intents": [
            "Ingest the 7-second river-flowing-over-rocks clip into the workspace.",
            "Extend the river footage to ~20 seconds with the water continuing to flow over the rocks.",
        ],
    },
    {
        "user_goal": "This 4-second clip shows a windmill turning slowly. Please extend to 18 seconds with the same rotation speed.",
        "rationale": (
            "4-second windmill clip + extend-to-18s at the same rotation rate. "
            "IntakeVideoAgent ingests the clip; VideoExtendAgent continues the windmill's "
            "rotation at the observed rate. Raw extended clip is the deliverable."
        ),
        "intents": [
            "Ingest the 4-second slow-windmill clip into the workspace.",
            "Extend the windmill footage to ~18 seconds preserving the observed slow rotation rate.",
        ],
    },
    {
        "user_goal": "Extend this 8-second clip of a train passing through a station. Please stretch to about 25 seconds as the train continues to roll through.",
        "rationale": (
            "8-second train-at-station clip + extend-to-25s with train continuing through. "
            "IntakeVideoAgent loads the clip. VideoExtendAgent extrapolates additional coach "
            "passes preserving the motion and perspective. Output is the raw extended clip."
        ),
        "intents": [
            "Ingest the 8-second train-passing-station clip into the workspace.",
            "Extend the train-passing footage to ~25 seconds with the train continuing to roll through.",
        ],
    },
    {
        "user_goal": "I have a 5-second shot of smoke rising from a chimney. Please extend to 20 seconds with the smoke continuing to rise steadily.",
        "rationale": (
            "5-second chimney-smoke clip + extend-to-20s with steady continuation. "
            "IntakeVideoAgent ingests the clip; VideoExtendAgent generates additional smoke-rise "
            "frames preserving plume shape and wind direction. Output is the raw extended clip."
        ),
        "intents": [
            "Ingest the 5-second chimney-smoke clip into the workspace.",
            "Extend the smoke-rising footage to ~20 seconds preserving plume shape and direction.",
        ],
    },
    {
        "user_goal": "Please extend this 6-second clip of a ferris wheel rotating. I need 30 seconds of slow continuous rotation.",
        "rationale": (
            "6-second ferris-wheel clip + extend-to-30s with slow continuous rotation. "
            "IntakeVideoAgent ingests the clip; VideoExtendAgent produces additional rotation "
            "frames at the observed rate. Raw extended clip is the deliverable."
        ),
        "intents": [
            "Ingest the 6-second ferris-wheel clip into the workspace.",
            "Extend the ferris-wheel footage to ~30 seconds of continuous slow rotation.",
        ],
    },
    {
        "user_goal": "This is a 4-second clip of a chef flipping a pancake mid-air. Please stretch to 12 seconds — flip completes and lands in the pan.",
        "rationale": (
            "4-second pancake-flip clip + extend-to-12s with full flip + landing. "
            "IntakeVideoAgent loads the clip; VideoExtendAgent continues the flip trajectory "
            "through to the pancake's landing. Output is the raw extended clip."
        ),
        "intents": [
            "Ingest the 4-second pancake-flip clip into the workspace.",
            "Extend the pancake-flip footage to ~12 seconds so the flip completes and lands in the pan.",
        ],
    },
    {
        "user_goal": "Please extend this 7-second clip of a Ferris wheel at dusk with city lights in the background. Stretch to 25 seconds.",
        "rationale": (
            "7-second dusk-Ferris-wheel clip + extend-to-25s preserving dusk lighting and city "
            "backdrop. IntakeVideoAgent ingests the clip; VideoExtendAgent generates additional "
            "rotation frames at the observed rate preserving the city lights and sky gradient. "
            "Raw extended clip is the output."
        ),
        "intents": [
            "Ingest the 7-second dusk-Ferris-wheel clip into the workspace.",
            "Extend the dusk-Ferris-wheel footage to ~25 seconds preserving dusk lighting and city backdrop.",
        ],
    },
    {
        "user_goal": "I have a 6-second clip of a puppy rolling in grass. Please extend to 20 seconds of the puppy continuing to roll and play.",
        "rationale": (
            "6-second puppy-in-grass clip + extend-to-20s with continued play. "
            "IntakeVideoAgent ingests the clip. VideoExtendAgent produces additional coherent "
            "roll / play motion preserving the grass and lighting. Raw extended clip is the "
            "output."
        ),
        "intents": [
            "Ingest the 6-second puppy-rolling-in-grass clip into the workspace.",
            "Extend the puppy-in-grass footage to ~20 seconds with continuing roll and play motion.",
        ],
    },
    {
        "user_goal": "This 5-second shot shows a robot walking. Please extend to 25 seconds of the robot continuing forward.",
        "rationale": (
            "5-second walking-robot clip + extend-to-25s with continued forward locomotion. "
            "IntakeVideoAgent loads the clip; VideoExtendAgent continues the robot's gait "
            "cycle forward for the additional seconds. Output is the extended clip."
        ),
        "intents": [
            "Ingest the 5-second walking-robot clip into the workspace.",
            "Extend the robot-walking footage to ~25 seconds with the robot continuing to walk forward.",
        ],
    },
    {
        "user_goal": "Extend this 4-second clip of a hummingbird hovering near a flower to about 15 seconds of continuous hovering.",
        "rationale": (
            "4-second hummingbird-hover clip + extend-to-15s with continuous hover. "
            "IntakeVideoAgent ingests the clip. VideoExtendAgent produces additional coherent "
            "wing-beat frames while keeping the bird near the flower. Output is the raw extended "
            "clip."
        ),
        "intents": [
            "Ingest the 4-second hummingbird-near-flower clip into the workspace.",
            "Extend the hummingbird-hovering footage to ~15 seconds of continuous hover.",
        ],
    },
    {
        "user_goal": "Please extend this 6-second underwater clip of fish swimming through a reef. I want 30 seconds of coral reef with fish continuing to swim.",
        "rationale": (
            "6-second reef clip + extend-to-30s with fish continuing to swim. IntakeVideoAgent "
            "ingests the clip. VideoExtendAgent produces additional swim-through-reef footage "
            "preserving water-light and coral detail. Output is the raw extended clip."
        ),
        "intents": [
            "Ingest the 6-second underwater coral-reef clip into the workspace.",
            "Extend the reef footage to ~30 seconds with fish continuing to swim through the coral.",
        ],
    },
    {
        "user_goal": "I have a 5-second clip of a falcon diving. Please extend to ~15 seconds so the dive completes with a pullout at the bottom.",
        "rationale": (
            "5-second falcon-dive clip + extend-to-15s with dive completion and pullout. "
            "IntakeVideoAgent loads the clip; VideoExtendAgent extrapolates the dive trajectory "
            "through to a pullout / recovery phase. Output is the raw extended clip."
        ),
        "intents": [
            "Ingest the 5-second falcon-diving clip into the workspace.",
            "Extend the falcon-dive footage to ~15 seconds with the dive completing and pulling out.",
        ],
    },
    {
        "user_goal": "This 8-second shot shows waves crashing on a cliff. Please extend to 25 seconds of continuous wave action.",
        "rationale": (
            "8-second wave-against-cliff clip + extend-to-25s with continuous wave action. "
            "IntakeVideoAgent ingests the clip. VideoExtendAgent generates additional wave "
            "impact frames preserving cliff geometry and spray dynamics. Raw extended clip is "
            "the deliverable."
        ),
        "intents": [
            "Ingest the 8-second waves-against-cliff clip into the workspace.",
            "Extend the wave-action footage to ~25 seconds with continuous crashing waves.",
        ],
    },
    {
        "user_goal": "Please extend this 4-second clip of a ballerina en pointe — I need about 12 seconds of her holding and releasing the pose.",
        "rationale": (
            "4-second ballerina-en-pointe clip + extend-to-12s with hold-and-release. "
            "IntakeVideoAgent ingests the clip. VideoExtendAgent continues the pose for a hold "
            "and then produces a graceful release motion. Output is the raw extended clip."
        ),
        "intents": [
            "Ingest the 4-second ballerina-en-pointe clip into the workspace.",
            "Extend the en-pointe footage to ~12 seconds with the ballerina holding then releasing the pose.",
        ],
    },
    {
        "user_goal": "I have a 6-second aerial clip of a cornfield in wind. Please extend to 25 seconds of the same cornfield rippling under the wind.",
        "rationale": (
            "6-second aerial cornfield-in-wind clip + extend-to-25s with continuing ripple. "
            "IntakeVideoAgent loads the clip; VideoExtendAgent continues the wind-driven ripple "
            "across the field preserving the aerial viewpoint. Raw extended clip is the "
            "deliverable."
        ),
        "intents": [
            "Ingest the 6-second aerial cornfield-in-wind clip into the workspace.",
            "Extend the cornfield footage to ~25 seconds with the wind-driven ripple continuing.",
        ],
    },
    {
        "user_goal": "Please extend this 5-second clip of a tea being poured from a kettle. Stretch to 15 seconds — the pour continues steadily into a cup.",
        "rationale": (
            "5-second tea-pour clip + extend-to-15s with steady continuation into the cup. "
            "IntakeVideoAgent ingests the clip. VideoExtendAgent continues the pour motion "
            "until the cup reaches a natural filling point. Output is the raw extended clip."
        ),
        "intents": [
            "Ingest the 5-second tea-pouring-from-kettle clip into the workspace.",
            "Extend the tea-pour footage to ~15 seconds with the pour continuing steadily into the cup.",
        ],
    },
]
