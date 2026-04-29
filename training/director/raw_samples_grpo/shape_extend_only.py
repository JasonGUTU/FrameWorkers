"""GRPO shape: extend_only — IntakeVideo → VideoExtend.

50 samples (target_n=50, no long_story_n). Topics deliberately disjoint
from SFT shape_extend_only.py. Rationale style mirrors SFT: 3-sentence
flow narrative naming both chain agents + implicit-rejection closure.
"""
from __future__ import annotations

SAMPLES: list[dict] = [
    {
        "user_goal": "Got a 15-second clip of jellyfish floating in an aquarium tank. Could you stretch it to about 60 seconds? Want it as a calming desk-monitor loop.",
        "rationale": (
            "15-second aquarium jellyfish clip + extend-to-60s for desk-monitor loop. "
            "IntakeVideoAgent ingests the clip; VideoExtendAgent generates additional "
            "coherent jellyfish-drift frames. Raw extended clip is the deliverable — no "
            "audio, no SRT, no restyle."
        ),
        "intents": [
            "Ingest the 15-second jellyfish aquarium clip into the workspace as the source video.",
            "Extend the jellyfish clip from 15 seconds out to ~60 seconds of seamless aquarium drift footage.",
        ],
    },
    {
        "user_goal": "I shot 8 seconds of a lava lamp on my desk. Please extend it out to a one-minute version so I can use it as a chill stream background.",
        "rationale": (
            "8-second lava-lamp clip + extend-to-60s for chill stream background. "
            "IntakeVideoAgent loads the clip; VideoExtendAgent produces additional frames "
            "preserving the slow undulating wax motion. Raw extended footage is the output "
            "— no overlay, audio, or restyle requested."
        ),
        "intents": [
            "Ingest the 8-second lava-lamp clip into the workspace.",
            "Extend the lava-lamp clip from 8 seconds to ~60 seconds preserving the slow undulating wax motion.",
        ],
    },
    {
        "user_goal": "Here's a 12-second time-lapse of city traffic at dusk — please grow it to roughly 45 seconds, keeping the same flow direction.",
        "rationale": (
            "12-second dusk city-traffic time-lapse + extend-to-45s preserving flow "
            "direction. IntakeVideoAgent ingests the clip; VideoExtendAgent generates "
            "additional frames continuing the same vehicular flow. Raw extended clip is "
            "the deliverable."
        ),
        "intents": [
            "Ingest the 12-second dusk city-traffic time-lapse into the workspace as the source video.",
            "Extend the dusk-traffic time-lapse from 12 seconds to ~45 seconds keeping the original flow direction.",
        ],
    },
    {
        "user_goal": "10-second clip of a campfire crackling, can you make it about 2 minutes long? It's for a relaxation video I'm putting together.",
        "rationale": (
            "10-second campfire-crackling clip + extend-to-2-minutes for a separate "
            "relaxation video the user is assembling elsewhere. IntakeVideoAgent ingests "
            "the source; VideoExtendAgent grows the clip to ~120 seconds preserving the "
            "flame motion. Raw extended footage is the final asset — no compositor, "
            "audio, or subtitle work requested here."
        ),
        "intents": [
            "Ingest the 10-second campfire-crackling clip into the workspace.",
            "Extend the campfire clip from 10 seconds out to ~2 minutes of continuous crackling-flames footage.",
        ],
    },
    {
        "user_goal": "Short 7-second clip of snow falling on pine branches — please extend to 30 seconds for a winter intro.",
        "rationale": (
            "7-second snow-on-pines clip + extend-to-30s for a winter intro. "
            "IntakeVideoAgent loads the clip; VideoExtendAgent produces ~23 more seconds "
            "of coherent snowfall frames. Output is the raw extended clip — no overlay, "
            "audio, or subtitle work requested."
        ),
        "intents": [
            "Ingest the 7-second snow-falling-on-pine-branches clip into the workspace.",
            "Extend the snow-on-pines clip from 7 seconds to ~30 seconds of continuous snowfall.",
        ],
    },
    {
        "user_goal": "I have an 11-second hot-air-balloon launch clip. Could you extend it out to ~40 seconds so the balloon visibly rises higher into the sky?",
        "rationale": (
            "11-second hot-air-balloon-launch clip + extend-to-40s of continued ascent. "
            "IntakeVideoAgent loads the launch clip; VideoExtendAgent generates additional "
            "ascent frames so the balloon visibly rises higher. Raw extended clip is the "
            "deliverable — no overlay, audio, subtitle, or restyle requested."
        ),
        "intents": [
            "Ingest the 11-second hot-air-balloon launch clip into the workspace.",
            "Extend the balloon-launch clip from 11 seconds out to ~40 seconds of continued ascent into the sky.",
        ],
    },
    {
        "user_goal": "Got a 6-second clip of a crab walking sideways across a tide pool — extend to ~25 seconds with the crab continuing its scuttle.",
        "rationale": (
            "6-second tide-pool crab clip + extend-to-25s with continuing scuttle. "
            "IntakeVideoAgent loads the clip; VideoExtendAgent generates additional frames "
            "of the crab's sideways motion across the rocks. Raw extended footage is the "
            "deliverable."
        ),
        "intents": [
            "Ingest the 6-second tide-pool crab clip into the workspace.",
            "Extend the crab-walking footage from 6 seconds to ~25 seconds preserving the sideways scuttle motion.",
        ],
    },
    {
        "user_goal": "Here's a 9-second clip of ice cracking on a frozen lake — please extend to 35 seconds with more crack patterns spreading.",
        "rationale": (
            "9-second frozen-lake ice-crack clip + extend-to-35s with continuing crack "
            "patterns. IntakeVideoAgent ingests the clip; VideoExtendAgent extrapolates "
            "additional crack-pattern frames spreading across the ice surface. Raw "
            "extended clip is the output."
        ),
        "intents": [
            "Ingest the 9-second frozen-lake ice-crack clip into the workspace.",
            "Extend the ice-crack clip from 9 seconds to ~35 seconds with continuing crack-pattern spread.",
        ],
    },
    {
        "user_goal": "I have a 5-second shot of wind blowing through a wheat field. Stretch it to about 20 seconds with the wheat continuing to ripple.",
        "rationale": (
            "5-second wind-through-wheat clip + extend-to-20s with continuing ripple. "
            "IntakeVideoAgent loads the clip; VideoExtendAgent produces additional "
            "wheat-rippling frames preserving the wind direction. Output is the raw "
            "extended clip."
        ),
        "intents": [
            "Ingest the 5-second wheat-field wind clip into the workspace.",
            "Extend the wheat-rippling footage from 5 seconds to ~20 seconds with the wind direction held steady.",
        ],
    },
    {
        "user_goal": "Got a quick 4-second clip of cherry blossom petals falling — please grow it to roughly 30 seconds for a spring-themed video opening.",
        "rationale": (
            "4-second cherry-blossom petal-fall clip + extend-to-30s for a spring-themed "
            "opening. IntakeVideoAgent loads the clip; VideoExtendAgent generates "
            "additional petal-drift frames. Raw extended clip is the deliverable — no "
            "overlay, audio, or subtitle work requested."
        ),
        "intents": [
            "Ingest the 4-second cherry-blossom petal-fall clip into the workspace.",
            "Extend the cherry-blossom clip from 4 seconds to ~30 seconds of continued petal drift.",
        ],
    },
    {
        "user_goal": "8-second clip of autumn leaves spinning down to the ground. Could you extend to ~25 seconds with more leaves falling in the same scene?",
        "rationale": (
            "8-second autumn leaf-fall clip + extend-to-25s with continuing leaf drift. "
            "IntakeVideoAgent ingests the clip; VideoExtendAgent generates additional "
            "leaf-fall frames. Output is the extended clip only."
        ),
        "intents": [
            "Ingest the 8-second autumn leaf-fall clip into the workspace.",
            "Extend the leaf-fall clip from 8 seconds to ~25 seconds with continuing autumn-leaf descent.",
        ],
    },
    {
        "user_goal": "Please extend this 6-second clip of raindrops creating ripples in a puddle — I want about 30 seconds for a meditation backdrop.",
        "rationale": (
            "6-second raindrop-ripple clip + extend-to-30s for meditation backdrop. "
            "IntakeVideoAgent loads the clip; VideoExtendAgent generates additional "
            "ripple-pattern frames preserving the rainfall cadence. Raw extended footage "
            "is the final asset."
        ),
        "intents": [
            "Ingest the 6-second raindrop-on-puddle clip into the workspace.",
            "Extend the raindrop-ripple clip from 6 seconds to ~30 seconds with continuing rainfall cadence.",
        ],
    },
    {
        "user_goal": "I have a 5-second clip of mist drifting over a pond at dawn — please extend to roughly 25 seconds keeping the same misty mood.",
        "rationale": (
            "5-second dawn-mist-over-pond clip + extend-to-25s preserving the misty "
            "mood. IntakeVideoAgent ingests the clip; VideoExtendAgent generates "
            "additional mist-drift frames at the same dawn lighting. Raw extended clip "
            "is the deliverable."
        ),
        "intents": [
            "Ingest the 5-second dawn-mist-over-pond clip into the workspace.",
            "Extend the mist-drift footage from 5 seconds to ~25 seconds preserving the dawn lighting and mood.",
        ],
    },
    {
        "user_goal": "Got a 3-second clip of a hummingbird hovering at a feeder. Could you extend to ~12 seconds with the bird continuing to drink?",
        "rationale": (
            "3-second hummingbird-at-feeder clip + extend-to-12s with continuing feeding. "
            "IntakeVideoAgent loads the clip; VideoExtendAgent extrapolates additional "
            "frames of the hummingbird's hover and drink motion. Output is the raw "
            "extended footage."
        ),
        "intents": [
            "Ingest the 3-second hummingbird-feeder clip into the workspace.",
            "Extend the hummingbird hover from 3 seconds to ~12 seconds preserving the wing-beat cadence and feeding motion.",
        ],
    },
    {
        "user_goal": "Please extend this 4-second clip of a butterfly slowly opening its wings on a flower — to roughly 15 seconds.",
        "rationale": (
            "4-second butterfly wing-opening clip + extend-to-15s with continued slow "
            "wing motion. IntakeVideoAgent ingests the clip; VideoExtendAgent generates "
            "additional frames continuing the slow wing-open motion. Raw extended clip "
            "is the deliverable."
        ),
        "intents": [
            "Ingest the 4-second butterfly-on-flower clip into the workspace.",
            "Extend the butterfly wing-opening footage from 4 seconds to ~15 seconds with continued slow wing motion.",
        ],
    },
    {
        "user_goal": "I have a 7-second clip of small fish swimming through coral reef. Stretch to ~28 seconds with the school continuing to drift past.",
        "rationale": (
            "7-second coral-reef fish-school clip + extend-to-28s with continuing drift. "
            "IntakeVideoAgent loads the clip; VideoExtendAgent generates additional "
            "fish-school frames preserving the underwater coral setting. Output is the "
            "raw extended clip."
        ),
        "intents": [
            "Ingest the 7-second coral-reef fish-school clip into the workspace.",
            "Extend the fish-school footage from 7 seconds to ~28 seconds with the coral setting and drift held steady.",
        ],
    },
    {
        "user_goal": "Got a 5-second shot of tall grass swaying in summer wind. Please grow it to about 25 seconds for a peaceful intro.",
        "rationale": (
            "5-second tall-grass wind-sway clip + extend-to-25s for peaceful intro. "
            "IntakeVideoAgent ingests the clip; VideoExtendAgent generates additional "
            "frames of continuing grass sway in the same summer-wind direction. Raw "
            "extended footage is the deliverable."
        ),
        "intents": [
            "Ingest the 5-second tall-grass wind-sway clip into the workspace.",
            "Extend the grass-sway footage from 5 seconds to ~25 seconds preserving the summer-wind direction.",
        ],
    },
    {
        "user_goal": "Extend this 6-second clip of dappled sunlight through forest canopy to about 30 seconds — same forest, light keeps shifting.",
        "rationale": (
            "6-second dappled-sunlight-through-canopy clip + extend-to-30s preserving "
            "the same forest. IntakeVideoAgent loads the clip; VideoExtendAgent generates "
            "additional frames with the dappled-light shift continuing. Raw extended "
            "clip is the output."
        ),
        "intents": [
            "Ingest the 6-second dappled-canopy-light clip into the workspace.",
            "Extend the dappled-sunlight footage from 6 seconds to ~30 seconds preserving the forest setting and light-shift cadence.",
        ],
    },
    {
        "user_goal": "I have a 4-second clip of distant lightning flashes in storm clouds — please extend to roughly 20 seconds with more flashes.",
        "rationale": (
            "4-second distant-lightning-flash clip + extend-to-20s with continuing "
            "flashes. IntakeVideoAgent ingests the clip; VideoExtendAgent extrapolates "
            "additional lightning-flash events within the same storm-cloud framing. "
            "Output is the raw extended footage."
        ),
        "intents": [
            "Ingest the 4-second distant-lightning storm-cloud clip into the workspace.",
            "Extend the lightning-flash footage from 4 seconds to ~20 seconds with additional flashes in the same storm framing.",
        ],
    },
    {
        "user_goal": "Got a 6-second time-lapse of desert sand dunes shifting in wind. Stretch to about 30 seconds.",
        "rationale": (
            "6-second desert-sand-dune time-lapse + extend-to-30s with continuing wind "
            "shift. IntakeVideoAgent loads the clip; VideoExtendAgent generates additional "
            "frames of sand-shift motion. Raw extended clip is the deliverable."
        ),
        "intents": [
            "Ingest the 6-second desert-sand-dune time-lapse into the workspace.",
            "Extend the sand-shift footage from 6 seconds to ~30 seconds preserving the wind direction.",
        ],
    },
    {
        "user_goal": "5-second clip of waves washing over a rocky shore — extend to about 25 seconds with the wave cadence holding.",
        "rationale": (
            "5-second waves-on-rocky-shore clip + extend-to-25s with wave cadence held. "
            "IntakeVideoAgent ingests the clip; VideoExtendAgent generates additional "
            "wave-wash frames preserving the rocky-shore framing. Output is the raw "
            "extended clip."
        ),
        "intents": [
            "Ingest the 5-second waves-on-rocky-shore clip into the workspace.",
            "Extend the wave-wash footage from 5 seconds to ~25 seconds preserving the rocky-shore framing and wave cadence.",
        ],
    },
    {
        "user_goal": "Please extend this 8-second clip of a neon sign reflecting in wet pavement — to roughly 30 seconds for a noir-vibe intro.",
        "rationale": (
            "8-second neon-on-wet-pavement reflection clip + extend-to-30s for noir-vibe "
            "intro. IntakeVideoAgent loads the clip; VideoExtendAgent generates additional "
            "frames preserving the neon-flicker pattern and reflection. Raw extended clip "
            "is the deliverable."
        ),
        "intents": [
            "Ingest the 8-second neon-on-wet-pavement reflection clip into the workspace.",
            "Extend the neon-reflection footage from 8 seconds to ~30 seconds preserving the flicker pattern and pavement reflection.",
        ],
    },
    {
        "user_goal": "Got a 6-second clip of a busy night-market vendor stand — please extend to ~25 seconds with customers continuing to pass by.",
        "rationale": (
            "6-second night-market vendor-stand clip + extend-to-25s with continuing "
            "foot-traffic. IntakeVideoAgent ingests the clip; VideoExtendAgent generates "
            "additional frames of customers passing the stand. Output is the raw "
            "extended footage."
        ),
        "intents": [
            "Ingest the 6-second night-market vendor-stand clip into the workspace.",
            "Extend the vendor-stand footage from 6 seconds to ~25 seconds with continuing customer foot-traffic.",
        ],
    },
    {
        "user_goal": "Please extend this 5-second clip of a food truck with a customer queue — to roughly 20 seconds with the queue still moving.",
        "rationale": (
            "5-second food-truck queue clip + extend-to-20s with continuing queue motion. "
            "IntakeVideoAgent loads the clip; VideoExtendAgent generates additional "
            "queue-movement frames. Raw extended clip is the deliverable."
        ),
        "intents": [
            "Ingest the 5-second food-truck queue clip into the workspace.",
            "Extend the food-truck-queue footage from 5 seconds to ~20 seconds with the queue still progressing forward.",
        ],
    },
    {
        "user_goal": "Got a 7-second clip of harbor lights twinkling at dusk. Stretch to ~30 seconds for a slow opening shot.",
        "rationale": (
            "7-second harbor-lights-at-dusk clip + extend-to-30s for slow opening. "
            "IntakeVideoAgent ingests the clip; VideoExtendAgent generates additional "
            "frames of continuing twinkle and dusk-light shift. Raw extended footage "
            "is the deliverable."
        ),
        "intents": [
            "Ingest the 7-second harbor-lights-at-dusk clip into the workspace.",
            "Extend the harbor-lights footage from 7 seconds to ~30 seconds preserving the dusk-light shift and twinkle cadence.",
        ],
    },
    {
        "user_goal": "I have a 6-second clip of a street performer juggling. Please extend to about 22 seconds with the juggling continuing.",
        "rationale": (
            "6-second street-performer juggling clip + extend-to-22s with continuing "
            "juggling. IntakeVideoAgent loads the clip; VideoExtendAgent generates "
            "additional juggling-motion frames preserving the cadence. Output is the raw "
            "extended clip."
        ),
        "intents": [
            "Ingest the 6-second street-performer juggling clip into the workspace.",
            "Extend the juggling footage from 6 seconds to ~22 seconds with the juggling cadence held steady.",
        ],
    },
    {
        "user_goal": "Please extend this 5-second clip of a city park fountain gurgling — to about 25 seconds for a peaceful background.",
        "rationale": (
            "5-second city-park fountain clip + extend-to-25s for peaceful background. "
            "IntakeVideoAgent ingests the clip; VideoExtendAgent generates additional "
            "fountain-gurgle frames preserving the water-flow pattern. Raw extended clip "
            "is the deliverable."
        ),
        "intents": [
            "Ingest the 5-second city-park fountain clip into the workspace.",
            "Extend the fountain-gurgle footage from 5 seconds to ~25 seconds preserving the water-flow pattern.",
        ],
    },
    {
        "user_goal": "Got a 4-second clip of my cat curled up napping by a sunny window. Stretch to ~20 seconds with the cat continuing to nap peacefully.",
        "rationale": (
            "4-second sleeping-cat-by-window clip + extend-to-20s with continuing nap. "
            "IntakeVideoAgent loads the clip; VideoExtendAgent generates additional "
            "frames of the cat's peaceful breathing motion. Output is the raw extended "
            "footage."
        ),
        "intents": [
            "Ingest the 4-second sleeping-cat-by-window clip into the workspace.",
            "Extend the napping-cat footage from 4 seconds to ~20 seconds with continuing peaceful breathing motion.",
        ],
    },
    {
        "user_goal": "5-second clip of my dog wagging his tail by the door — please extend to about 18 seconds with continuing happy wag.",
        "rationale": (
            "5-second dog-tail-wag clip + extend-to-18s with continuing wag. "
            "IntakeVideoAgent ingests the clip; VideoExtendAgent generates additional "
            "tail-wag frames preserving the cadence. Raw extended clip is the "
            "deliverable."
        ),
        "intents": [
            "Ingest the 5-second dog-tail-wagging clip into the workspace.",
            "Extend the tail-wag footage from 5 seconds to ~18 seconds preserving the happy-wag cadence.",
        ],
    },
    {
        "user_goal": "Got an 8-second clip of soup simmering in a pot — please extend to ~30 seconds for a cooking-show transition.",
        "rationale": (
            "8-second soup-simmering clip + extend-to-30s for cooking-show transition. "
            "IntakeVideoAgent loads the clip; VideoExtendAgent generates additional "
            "simmer-bubble frames preserving the cooking cadence. Output is the raw "
            "extended clip."
        ),
        "intents": [
            "Ingest the 8-second soup-simmering clip into the workspace.",
            "Extend the soup-simmer footage from 8 seconds to ~30 seconds preserving the bubble cadence.",
        ],
    },
    {
        "user_goal": "Please extend this 6-second clip of a windmill spinning slowly in a green field — to about 25 seconds with the same rotation.",
        "rationale": (
            "6-second windmill-in-field clip + extend-to-25s with continuing rotation. "
            "IntakeVideoAgent ingests the clip; VideoExtendAgent generates additional "
            "windmill-blade-rotation frames preserving the field setting. Raw extended "
            "clip is the deliverable."
        ),
        "intents": [
            "Ingest the 6-second windmill-in-field clip into the workspace.",
            "Extend the windmill-rotation footage from 6 seconds to ~25 seconds preserving the field setting and rotation cadence.",
        ],
    },
    {
        "user_goal": "Got a 4-second clip of a wind chime spinning in a breeze. Stretch to ~15 seconds for a meditation cue.",
        "rationale": (
            "4-second wind-chime spin clip + extend-to-15s for meditation cue. "
            "IntakeVideoAgent loads the clip; VideoExtendAgent generates additional "
            "wind-chime-spin frames preserving the breeze cadence. Output is the raw "
            "extended clip."
        ),
        "intents": [
            "Ingest the 4-second wind-chime-spinning clip into the workspace.",
            "Extend the wind-chime footage from 4 seconds to ~15 seconds preserving the breeze cadence.",
        ],
    },
    {
        "user_goal": "Please extend this 6-second clip of a hammock swaying in the backyard — to about 25 seconds with continuing gentle sway.",
        "rationale": (
            "6-second hammock-sway clip + extend-to-25s with continuing gentle sway. "
            "IntakeVideoAgent ingests the clip; VideoExtendAgent generates additional "
            "frames of the hammock's pendulum motion. Raw extended clip is the "
            "deliverable."
        ),
        "intents": [
            "Ingest the 6-second hammock-sway clip into the workspace.",
            "Extend the hammock-sway footage from 6 seconds to ~25 seconds preserving the gentle pendulum motion.",
        ],
    },
    {
        "user_goal": "Got an 8-second clip of an assembly-line conveyor belt moving products. Extend to ~30 seconds for a manufacturing-process B-roll.",
        "rationale": (
            "8-second assembly-line conveyor clip + extend-to-30s for manufacturing "
            "B-roll. IntakeVideoAgent loads the clip; VideoExtendAgent generates "
            "additional conveyor-motion frames preserving the line speed. Output is "
            "the raw extended clip."
        ),
        "intents": [
            "Ingest the 8-second assembly-line conveyor clip into the workspace.",
            "Extend the conveyor-belt footage from 8 seconds to ~30 seconds preserving the line speed and product flow.",
        ],
    },
    {
        "user_goal": "Please extend this 5-second clip of a robotic arm tightening bolts on a production line — to about 20 seconds with continuing repetition.",
        "rationale": (
            "5-second robotic-arm bolt-tightening clip + extend-to-20s with continuing "
            "repetition. IntakeVideoAgent ingests the clip; VideoExtendAgent extrapolates "
            "additional bolt-tightening cycles preserving the production-line setting. "
            "Raw extended clip is the deliverable."
        ),
        "intents": [
            "Ingest the 5-second robotic-arm bolt-tightening clip into the workspace.",
            "Extend the robotic-arm footage from 5 seconds to ~20 seconds with continuing bolt-tightening cycles.",
        ],
    },
    {
        "user_goal": "Got a 6-second clip of a factory smokestack puffing white smoke. Extend to ~25 seconds with continuing smoke release.",
        "rationale": (
            "6-second factory-smokestack clip + extend-to-25s with continuing smoke "
            "release. IntakeVideoAgent loads the clip; VideoExtendAgent generates "
            "additional smoke-puff frames preserving the cadence. Output is the raw "
            "extended footage."
        ),
        "intents": [
            "Ingest the 6-second factory-smokestack clip into the workspace.",
            "Extend the smokestack footage from 6 seconds to ~25 seconds with continuing smoke-release cadence.",
        ],
    },
    {
        "user_goal": "Please extend this 8-second clip of a rock climber moving up a cliff face — to about 30 seconds with the climb continuing.",
        "rationale": (
            "8-second rock-climber clip + extend-to-30s with continuing ascent. "
            "IntakeVideoAgent ingests the clip; VideoExtendAgent generates additional "
            "frames of the climber's hand-and-foot progression up the cliff. Raw "
            "extended clip is the deliverable."
        ),
        "intents": [
            "Ingest the 8-second rock-climber-on-cliff clip into the workspace.",
            "Extend the rock-climber footage from 8 seconds to ~30 seconds with the climb progressing upward.",
        ],
    },
    {
        "user_goal": "Got a 5-second offshore clip of a surfer riding a wave. Stretch to ~22 seconds with the ride continuing.",
        "rationale": (
            "5-second offshore surfer-on-wave clip + extend-to-22s with continuing ride. "
            "IntakeVideoAgent loads the clip; VideoExtendAgent generates additional "
            "frames of the surfer's wave progression. Output is the raw extended clip."
        ),
        "intents": [
            "Ingest the 5-second offshore surfer-on-wave clip into the workspace.",
            "Extend the surfer footage from 5 seconds to ~22 seconds with the wave-ride continuing toward shore.",
        ],
    },
    {
        "user_goal": "Please extend this 6-second clip of a mountain biker descending a forest trail — to about 25 seconds with continuing descent.",
        "rationale": (
            "6-second mountain-biker forest-descent clip + extend-to-25s with continuing "
            "descent. IntakeVideoAgent ingests the clip; VideoExtendAgent generates "
            "additional frames preserving the trail framing and biker speed. Raw "
            "extended footage is the deliverable."
        ),
        "intents": [
            "Ingest the 6-second mountain-biker forest-trail clip into the workspace.",
            "Extend the mountain-biker footage from 6 seconds to ~25 seconds with the descent continuing through the forest.",
        ],
    },
    {
        "user_goal": "Got a 5-second clip of an ice skater spinning in the rink center. Extend to ~18 seconds with the spin continuing.",
        "rationale": (
            "5-second ice-skater rink-center spin clip + extend-to-18s with continuing "
            "spin. IntakeVideoAgent loads the clip; VideoExtendAgent generates additional "
            "spin frames preserving the rotation cadence. Output is the raw extended "
            "clip."
        ),
        "intents": [
            "Ingest the 5-second ice-skater rink-center spin clip into the workspace.",
            "Extend the spin footage from 5 seconds to ~18 seconds preserving the rink-center rotation cadence.",
        ],
    },
    {
        "user_goal": "Please extend this 4-second clip of a kid on a swing in a playground — to about 16 seconds with the swing continuing.",
        "rationale": (
            "4-second kid-on-swing clip + extend-to-16s with continuing swing motion. "
            "IntakeVideoAgent ingests the clip; VideoExtendAgent generates additional "
            "swing-pendulum frames preserving the playground setting. Raw extended clip "
            "is the deliverable."
        ),
        "intents": [
            "Ingest the 4-second kid-on-playground-swing clip into the workspace.",
            "Extend the swing footage from 4 seconds to ~16 seconds preserving the swing pendulum and playground setting.",
        ],
    },
    {
        "user_goal": "Got a 7-second clip of a plane taking off down a runway. Extend to ~25 seconds with the climb continuing into the sky.",
        "rationale": (
            "7-second plane-takeoff clip + extend-to-25s with continuing climb. "
            "IntakeVideoAgent loads the clip; VideoExtendAgent generates additional "
            "frames of the plane's ascent. Output is the raw extended footage."
        ),
        "intents": [
            "Ingest the 7-second plane-takeoff clip into the workspace.",
            "Extend the plane-takeoff footage from 7 seconds to ~25 seconds with the climb continuing into the sky.",
        ],
    },
    {
        "user_goal": "Please extend this 6-second clip of a cargo ship cutting across calm sea — to about 30 seconds with continuing forward motion.",
        "rationale": (
            "6-second cargo-ship-on-calm-sea clip + extend-to-30s with continuing "
            "forward motion. IntakeVideoAgent ingests the clip; VideoExtendAgent "
            "generates additional frames of the ship's progression across the sea. "
            "Raw extended clip is the deliverable."
        ),
        "intents": [
            "Ingest the 6-second cargo-ship-on-calm-sea clip into the workspace.",
            "Extend the cargo-ship footage from 6 seconds to ~30 seconds with continuing forward motion across the sea.",
        ],
    },
    {
        "user_goal": "Got a 5-second clip of a helicopter hovering over water. Stretch to ~20 seconds with the helicopter holding position.",
        "rationale": (
            "5-second helicopter-hovering-over-water clip + extend-to-20s with hover "
            "held. IntakeVideoAgent loads the clip; VideoExtendAgent generates additional "
            "rotor-spin frames preserving the hover position. Output is the raw extended "
            "clip."
        ),
        "intents": [
            "Ingest the 5-second helicopter-hovering-over-water clip into the workspace.",
            "Extend the helicopter footage from 5 seconds to ~20 seconds preserving the hover position over the water.",
        ],
    },
    {
        "user_goal": "Please extend this 4-second clip of chimney smoke curling up from a rooftop — to about 18 seconds with continuing wisps.",
        "rationale": (
            "4-second chimney-smoke-curl clip + extend-to-18s with continuing wisps. "
            "IntakeVideoAgent ingests the clip; VideoExtendAgent generates additional "
            "smoke-curl frames preserving the rooftop setting. Raw extended footage "
            "is the deliverable."
        ),
        "intents": [
            "Ingest the 4-second chimney-smoke-curl clip into the workspace.",
            "Extend the chimney-smoke footage from 4 seconds to ~18 seconds with continuing curling wisps.",
        ],
    },
    {
        "user_goal": "Got a 6-second clip of clouds passing over the moon at night. Extend to ~30 seconds with the cloud drift continuing.",
        "rationale": (
            "6-second clouds-over-moon clip + extend-to-30s with continuing drift. "
            "IntakeVideoAgent loads the clip; VideoExtendAgent generates additional "
            "cloud-drift frames preserving the moon framing. Output is the raw extended "
            "clip."
        ),
        "intents": [
            "Ingest the 6-second clouds-over-moon clip into the workspace.",
            "Extend the cloud-drift footage from 6 seconds to ~30 seconds preserving the moon framing and drift speed.",
        ],
    },
    {
        "user_goal": "Please extend this 7-second clip of a fairground Ferris wheel spinning at night — to about 30 seconds with continuing rotation.",
        "rationale": (
            "7-second night-Ferris-wheel clip + extend-to-30s with continuing rotation. "
            "IntakeVideoAgent ingests the clip; VideoExtendAgent generates additional "
            "Ferris-wheel-spin frames preserving the night-light pattern. Raw extended "
            "clip is the deliverable."
        ),
        "intents": [
            "Ingest the 7-second night-Ferris-wheel clip into the workspace.",
            "Extend the Ferris-wheel footage from 7 seconds to ~30 seconds preserving the rotation cadence and night-light pattern.",
        ],
    },
    {
        "user_goal": "Got a 5-second clip of a desert tumbleweed rolling across a dirt road. Extend to ~20 seconds with the roll continuing.",
        "rationale": (
            "5-second desert-tumbleweed-rolling clip + extend-to-20s with continuing "
            "roll. IntakeVideoAgent loads the clip; VideoExtendAgent generates additional "
            "tumbleweed-motion frames preserving the dirt-road setting. Output is the "
            "raw extended footage."
        ),
        "intents": [
            "Ingest the 5-second desert-tumbleweed-rolling clip into the workspace.",
            "Extend the tumbleweed footage from 5 seconds to ~20 seconds with continuing roll across the dirt road.",
        ],
    },
    {
        "user_goal": "Please extend this 6-second clip of a lighthouse beam sweeping at night — to about 25 seconds with continuing rotation.",
        "rationale": (
            "6-second lighthouse-beam-sweep clip + extend-to-25s with continuing "
            "rotation. IntakeVideoAgent ingests the clip; VideoExtendAgent generates "
            "additional beam-sweep frames preserving the night-coast setting. Raw "
            "extended clip is the deliverable."
        ),
        "intents": [
            "Ingest the 6-second lighthouse-beam-sweep clip into the workspace.",
            "Extend the lighthouse-beam footage from 6 seconds to ~25 seconds with continuing rotation against the night sky.",
        ],
    },
    {
        "user_goal": "Got a 7-second clip of wind turbines spinning over green hills. Extend to ~30 seconds with continuing rotation.",
        "rationale": (
            "7-second wind-turbines-over-hills clip + extend-to-30s with continuing "
            "rotation. IntakeVideoAgent loads the clip; VideoExtendAgent generates "
            "additional turbine-blade-rotation frames preserving the hill setting. "
            "Output is the raw extended clip."
        ),
        "intents": [
            "Ingest the 7-second wind-turbines-over-hills clip into the workspace.",
            "Extend the wind-turbine footage from 7 seconds to ~30 seconds preserving the rotation cadence and green-hill setting.",
        ],
    },
    {
        "user_goal": "Please extend this 5-second clip of a ferry boat pulling into a dock — to about 22 seconds with the docking continuing.",
        "rationale": (
            "5-second ferry-boat-docking clip + extend-to-22s with continuing approach. "
            "IntakeVideoAgent ingests the clip; VideoExtendAgent generates additional "
            "frames of the ferry's slow approach to the dock. Raw extended footage is "
            "the deliverable."
        ),
        "intents": [
            "Ingest the 5-second ferry-boat-docking clip into the workspace.",
            "Extend the ferry-docking footage from 5 seconds to ~22 seconds with the slow approach continuing toward the dock.",
        ],
    },
]
