"""Generate the CompositorAgent asset bundle end-to-end.

Design:
  - Phase 1 bypasses ``KeyFrameAgent`` (its rework loop is unstable on
    hand-authored seeds; attempt 3 has been observed to wipe attempt 2's
    content) and calls fal image + video APIs directly, one keyframe and
    one 5-second Kling I2V clip per shot, then concatenates with ffmpeg.
  - Phase 2 runs the audio trio + subtitle agent through the normal Flask
    Assistant pipeline (they only need the seeded screenplay).
  - Phase 3 runs CompositorAgent ad-hoc: we instantiate the agent in
    process, let its LLM produce the composition plan against explicit
    screenplay / video / audio / subtitle JSON, then drive
    ``CompositorService.compose`` directly against the real on-disk mp4
    + wav + srt. No Flask resolver hop, so we don't need the VideoAgent
    JSON-vs-mp4 ``path`` ambiguity.
  - Phase 4 harvests every produced asset into
    ``process-flow-visualizer/test-assets/compositor_demo/`` with stable
    numbered folders so the bundle is reproducible and self-contained.

Re-running the script skips phases whose outputs already exist on disk
(cheap to resume if one step fails mid-way).

Budget: ~$1.5-$2.5 of fal credits (Kling dominates). Wall: ~15-30 min.

Usage:
    python scripts/gen_compositor_demo.py
"""

from __future__ import annotations

import asyncio
import json
import os
import shutil
import subprocess
import sys
import time
import types
from datetime import datetime
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
_PKG = _REPO / "plan-stack-backend"
for p in (_REPO, _PKG):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from inference.config.config_loader import ConfigLoader  # noqa: E402

for fname in (".env", ".env.example"):
    p = _REPO / fname
    if p.is_file():
        ConfigLoader.load_env_file(str(p), override=False)

# select_*_service() gates on this: agents hit real fal backends instead
# of the 44-byte MOCK_WAV / MOCK_MP4_HEADER placeholders. Set BEFORE any
# agent module import so lazy factories see it.
os.environ.setdefault("FW_USE_REAL_MEDIA_GEN", "1")

if "flask_cors" not in sys.modules:
    fc = types.ModuleType("flask_cors")
    fc.CORS = lambda *a, **kw: None
    sys.modules["flask_cors"] = fc


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

DEMO_ROOT = _REPO / "process-flow-visualizer" / "test-assets" / "compositor_demo"
SEED_SCREENPLAY = DEMO_ROOT / "01_screenplay_seed.json"
KF_DIR          = DEMO_ROOT / "02_keyframes"
VID_DIR         = DEMO_ROOT / "03_video"
NAR_DIR         = DEMO_ROOT / "04_narration"
MUS_DIR         = DEMO_ROOT / "05_music"
AMB_DIR         = DEMO_ROOT / "06_ambience"
MIX_DIR         = DEMO_ROOT / "07_audio_mix"
SUB_DIR         = DEMO_ROOT / "08_subtitle"
COMP_DIR        = DEMO_ROOT / "09_compositor"

for d in (KF_DIR, VID_DIR, NAR_DIR, MUS_DIR, AMB_DIR, MIX_DIR, SUB_DIR, COMP_DIR):
    d.mkdir(parents=True, exist_ok=True)

RUN_BASE = _REPO / "Runtime" / "compositor_demo_runs"
RUN_BASE.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Shot-level prompts for Phase 1 (hand-authored to honor the seed screenplay)
# ---------------------------------------------------------------------------

SHOTS: list[dict] = [
    {
        "shot_id": "sh_001",
        "kf_prompt": (
            "Cinematic 35mm wide interior of a neighborhood coffee shop at "
            "sunrise. Warm golden morning light rakes in through the front "
            "window. Reclaimed-wood counter in the foreground, copper espresso "
            "machine on the back bar behind it. A young woman (Anna, early 30s, "
            "chestnut shoulder-length hair, oatmeal-tone wool sweater) sits at "
            "the counter cupping her hands around her phone. A female barista "
            "(Mira, mid-20s, dark hair in a low pony, dark denim apron over "
            "white tee) stands behind the counter reaching out with a steaming "
            "cream-colored ceramic coffee cup. Shallow depth of field, soft "
            "film grain, handful of patrons soft-focus in the background."
        ),
        "motion": (
            "Slow push-in. Mira slides the cup across the counter toward Anna; "
            "steam curls softly upward. Anna's eyes lift from her phone. "
            "Subtle natural motion only; no camera shake."
        ),
    },
    {
        "shot_id": "sh_002",
        "kf_prompt": (
            "Cinematic medium close-up, over Anna's right shoulder. Anna "
            "(chestnut shoulder-length hair, oatmeal wool sweater) holds the "
            "cream-colored ceramic coffee cup near her lips, lips parted "
            "mid-word. Mira (dark hair in low pony, dark denim apron over "
            "white tee) is slightly out of focus across the counter, her face "
            "softly smiling. Steam from the cup softens the foreground. Warm "
            "golden morning light, shallow depth of field, 35mm film look."
        ),
        "motion": (
            "Anna speaks over the rim of the cup; Mira nods gently in "
            "response. Steam continues to curl. Subtle natural motion only."
        ),
    },
    {
        "shot_id": "sh_003",
        "kf_prompt": (
            "Cinematic top-down overhead close-up on a reclaimed-wood coffee "
            "shop counter. A cream-colored ceramic coffee cup on the right "
            "side with rising steam. A man's hand in a charcoal wool coat "
            "sleeve is sliding a small folded cream-colored paper note across "
            "the wood, stopping the note just beside the cup. The hand-torn "
            "edge of the note catches warm morning light. Shallow depth of "
            "field, warm palette, soft film grain."
        ),
        "motion": (
            "The hand continues to slide the note gently next to the cup, "
            "then the fingers begin to lift away. Steam from the cup curls "
            "upward. Subtle natural motion only."
        ),
    },
    {
        "shot_id": "sh_004",
        "kf_prompt": (
            "Cinematic medium two-shot profile view. On the right, Anna "
            "(chestnut shoulder-length hair, oatmeal wool sweater, silver "
            "stud earrings) holds the folded cream-colored paper note, partly "
            "unfolded in her hands, lifting her face to look left. On the "
            "left in half profile, the stranger (late 30s, short dark hair, "
            "charcoal wool coat, collared shirt) mid-word, already beginning "
            "to turn away. Warm golden morning light, shallow depth of field, "
            "reclaimed-wood counter in the foreground, 35mm film look."
        ),
        "motion": (
            "The stranger finishes speaking and steps back half a pace, "
            "turning away. Anna continues unfolding the note; the corners of "
            "her mouth lift into a small smile. Subtle natural motion only."
        ),
    },
]


# ---------------------------------------------------------------------------
# Phase 1 — direct fal calls for keyframes + clips, then ffmpeg concat
# ---------------------------------------------------------------------------

async def _phase1_video() -> Path:
    from inference.generation.image_generators.service import FalImageService
    from inference.generation.video_generators.service import FalVideoService

    # 1a. Keyframes (one PNG per shot). FalImageService uses
    # FAL_IMAGE_MODEL (fal-ai/nano-banana-2) — the OpenRouter path was
    # removed.
    img_svc = FalImageService()
    for shot in SHOTS:
        out = KF_DIR / f"kf_{shot['shot_id']}.png"
        if out.is_file() and out.stat().st_size > 1000:
            print(f"  [P1a] {out.name} already exists, skip", flush=True)
            continue
        t0 = time.time()
        print(f"  [P1a] generating {out.name} ...", flush=True)
        res = await img_svc.generate_image(prompt=shot["kf_prompt"])
        out.write_bytes(res.bytes)
        print(f"  [P1a] {out.name} ({len(res.bytes)} bytes, wall {time.time()-t0:.1f}s)", flush=True)

    # 1b. Video clips (one mp4 per shot via Kling I2V).
    vid_svc = FalVideoService()
    try:
        for shot in SHOTS:
            out = VID_DIR / f"clip_{shot['shot_id']}.mp4"
            if out.is_file() and out.stat().st_size > 10_000:
                print(f"  [P1b] {out.name} already exists, skip", flush=True)
                continue
            kf_path = KF_DIR / f"kf_{shot['shot_id']}.png"
            kf_bytes = kf_path.read_bytes()
            t0 = time.time()
            print(f"  [P1b] generating {out.name} ...", flush=True)
            res = await vid_svc.generate_clip(
                shot_id=shot["shot_id"],
                keyframe_images=[kf_bytes],
                prompt=shot["motion"],
                duration_sec=5.0,
            )
            out.write_bytes(res.bytes)
            print(f"  [P1b] {out.name} ({len(res.bytes)} bytes, wall {time.time()-t0:.1f}s)", flush=True)
    finally:
        await vid_svc.close()

    # 1c. Concat via ffmpeg.
    final = VID_DIR / "clip_final.mp4"
    if final.is_file() and final.stat().st_size > 10_000:
        print(f"  [P1c] {final.name} already exists, skip", flush=True)
        return final

    clips = [VID_DIR / f"clip_{s['shot_id']}.mp4" for s in SHOTS]
    list_file = VID_DIR / "_concat.txt"
    list_file.write_text("".join(f"file '{c.as_posix()}'\n" for c in clips), encoding="utf-8")
    print(f"  [P1c] ffmpeg concat -> {final.name}", flush=True)
    # Use demux concat; clips all came from the same Kling model so they
    # should share codec/resolution and concat cleanly without re-encoding.
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0",
            "-i", str(list_file),
            "-c", "copy",
            str(final),
        ],
        check=True, capture_output=True, text=True, timeout=120,
    )
    list_file.unlink(missing_ok=True)
    print(f"  [P1c] {final.name} ({final.stat().st_size} bytes)", flush=True)
    return final


# ---------------------------------------------------------------------------
# Phase 2 — audio + subtitle via in-process agent calls
#
# Earlier attempt drove this through the Flask /api/assistant/execute
# route, but the InputResolver path wasn't picking up the seed
# screenplay's payload (no failure signal, just empty output — Narration
# produced 0 segments, Subtitle said "No dialogue found"). Since the
# only upstream each audio / subtitle agent needs is the screenplay, it
# is simpler and more deterministic to build their typed inputs directly
# from the seed JSON we already have on disk, then call agent.run() with
# a hand-built MaterializeContext that persists binaries straight into
# the demo bundle.
# ---------------------------------------------------------------------------

async def _run_agent_inprocess(
    *,
    agent,
    evaluator,
    materializer,
    typed_input,
    dest_dir: Path,
    agent_id: str,
    label: str,
):
    """Run one agent with its own workspace-free materialize context.

    Binaries are written straight into ``dest_dir`` with their original
    filenames (derived from ``MediaAsset.sys_id`` + extension); the
    asset dict returned in ``ExecutionResult`` carries the updated URIs.
    """
    from agents.base_agent import MaterializeContext
    from agents.descriptor import MediaAsset

    dest_dir.mkdir(parents=True, exist_ok=True)

    def _persist(media: "MediaAsset") -> str:
        out = dest_dir / f"{media.sys_id}.{media.extension}"
        out.write_bytes(media.data)
        return str(out)

    def _report(*, kind: str, sys_id: str, error: str) -> None:
        print(f"  [P2-fail] {agent_id} kind={kind} sys_id={sys_id} error={error[:200]}", flush=True)

    ctx = MaterializeContext(
        step_id="compositor_demo",
        typed_input=typed_input,
        persist_binary=_persist,
        report_failure=_report,
    )

    agent.evaluator = evaluator
    agent.materializer = materializer

    t0 = time.time()
    print(f"  [P2] {label} ... ", end="", flush=True)
    result = await agent.run(typed_input, materialize_ctx=ctx, max_retries=3)
    wall = time.time() - t0
    print(f"passed={result.passed} attempts={result.attempts} media={len(result.media_assets)} wall={wall:.1f}s", flush=True)

    if not result.passed:
        raise RuntimeError(
            f"{agent_id} failed after {result.attempts} attempts: "
            f"{str(result.eval_result.get('summary',''))[:300]}"
        )

    # Persist the agent's output JSON next to the binaries.
    pkg_path = dest_dir / "package.json"
    pkg_path.write_text(
        json.dumps(result.asset_dict or result.output.model_dump(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return result


async def phase2_audio_and_subtitle() -> dict:
    """Run Narration / Music / Ambience / AudioMix / Subtitle in-process."""
    from inference.clients import LLMClient
    from inference.generation import select_audio_service

    from agents.narration.agent import NarrationAgent
    from agents.narration.evaluator import NarrationEvaluator
    from agents.narration.materializer import NarrationMaterializer
    from agents.narration.schema import NarrationAgentInput

    from agents.music.agent import MusicAgent
    from agents.music.evaluator import MusicEvaluator
    from agents.music.materializer import MusicMaterializer
    from agents.music.schema import MusicAgentInput

    from agents.ambience.agent import AmbienceAgent
    from agents.ambience.evaluator import AmbienceEvaluator
    from agents.ambience.materializer import AmbienceMaterializer
    from agents.ambience.schema import AmbienceAgentInput

    from agents.audio_mix.agent import AudioMixAgent
    from agents.audio_mix.evaluator import AudioMixEvaluator
    from agents.audio_mix.materializer import AudioMixMaterializer
    from agents.audio_mix.schema import AudioMixAgentInput

    from agents.subtitle.agent import SubtitleAgent
    from agents.subtitle.evaluator import SubtitleEvaluator
    from agents.subtitle.schema import SubtitleAgentInput

    llm = LLMClient()
    screenplay_payload = json.loads(SEED_SCREENPLAY.read_text(encoding="utf-8"))
    screenplay_json_text = json.dumps(screenplay_payload, ensure_ascii=False, indent=2)

    # Narration
    narr_audio_dir = NAR_DIR
    narr_result = await _run_agent_inprocess(
        agent=NarrationAgent(llm_client=llm),
        evaluator=NarrationEvaluator(),
        materializer=NarrationMaterializer(audio_service=select_audio_service()),
        typed_input=NarrationAgentInput(screenplay_json_text=screenplay_json_text),
        dest_dir=narr_audio_dir,
        agent_id="NarrationAgent",
        label="NarrationAgent (extract dialogue + TTS)",
    )

    # Music
    mus_result = await _run_agent_inprocess(
        agent=MusicAgent(llm_client=llm),
        evaluator=MusicEvaluator(),
        materializer=MusicMaterializer(audio_service=select_audio_service()),
        typed_input=MusicAgentInput(screenplay_json_text=screenplay_json_text),
        dest_dir=MUS_DIR,
        agent_id="MusicAgent",
        label="MusicAgent (scene mood -> music)",
    )

    # Ambience
    amb_result = await _run_agent_inprocess(
        agent=AmbienceAgent(llm_client=llm),
        evaluator=AmbienceEvaluator(),
        materializer=AmbienceMaterializer(audio_service=select_audio_service()),
        typed_input=AmbienceAgentInput(screenplay_json_text=screenplay_json_text),
        dest_dir=AMB_DIR,
        agent_id="AmbienceAgent",
        label="AmbienceAgent (scene location -> ambience)",
    )

    # Subtitle (no materializer — purely LLM output → SRT text inside JSON)
    sub_result = await _run_agent_inprocess(
        agent=SubtitleAgent(llm_client=llm),
        evaluator=SubtitleEvaluator(),
        materializer=None,
        typed_input=SubtitleAgentInput(
            screenplay_json_text=screenplay_json_text,
            video_json_text="",
        ),
        dest_dir=SUB_DIR,
        agent_id="SubtitleAgent",
        label="SubtitleAgent (screenplay -> SRT)",
    )

    # Extract SRT as a real .srt file.
    sub_dict = sub_result.asset_dict or sub_result.output.model_dump()
    tracks = sub_dict.get("content", {}).get("tracks", []) or []
    srt_text = (tracks[0].get("srt_text") or "").strip() if tracks else ""
    if srt_text:
        (SUB_DIR / "subtitle.srt").write_text(srt_text + "\n", encoding="utf-8")
        print(f"  [P2] SRT extracted ({len(srt_text)} chars)", flush=True)
    else:
        print(f"  [P2] WARNING: SubtitleAgent produced no srt_text", flush=True)

    # AudioMix — feed the three upstream package JSONs as input.
    narr_pkg_json = json.dumps(narr_result.asset_dict or narr_result.output.model_dump(), ensure_ascii=False, indent=2)
    mus_pkg_json = json.dumps(mus_result.asset_dict or mus_result.output.model_dump(), ensure_ascii=False, indent=2)
    amb_pkg_json = json.dumps(amb_result.asset_dict or amb_result.output.model_dump(), ensure_ascii=False, indent=2)

    mix_result = await _run_agent_inprocess(
        agent=AudioMixAgent(llm_client=llm),
        evaluator=AudioMixEvaluator(),
        materializer=AudioMixMaterializer(audio_service=select_audio_service()),
        typed_input=AudioMixAgentInput(
            narration_json_text=narr_pkg_json,
            music_json_text=mus_pkg_json,
            ambience_json_text=amb_pkg_json,
        ),
        dest_dir=MIX_DIR,
        agent_id="AudioMixAgent",
        label="AudioMixAgent (amix narration+music+ambience)",
    )

    return {
        "narration": narr_result,
        "music": mus_result,
        "ambience": amb_result,
        "subtitle": sub_result,
        "audio_mix": mix_result,
        "srt_text": srt_text,
    }


# ---------------------------------------------------------------------------
# Phase 3 — CompositorAgent in-process (LLM plan + FFmpeg compose)
# ---------------------------------------------------------------------------

async def _phase3_compose(video_path: Path, audio_path: Path, srt_text: str, screenplay_payload: dict, video_json_text: str, audio_json_text: str, subtitle_json_text: str) -> tuple[dict, bytes]:
    from agents.compositor.agent import CompositorAgent
    from agents.compositor.schema import CompositorAgentInput
    from inference.clients import LLMClient
    from inference.generation.compositor_service import CompositorService

    llm = LLMClient()
    agent = CompositorAgent(llm_client=llm)
    typed_input = CompositorAgentInput(
        screenplay_json_text=json.dumps(screenplay_payload, ensure_ascii=False, indent=2),
        video_json_text=video_json_text,
        audio_json_text=audio_json_text,
        subtitle_json_text=subtitle_json_text,
        video_file_path=str(video_path),
        audio_file_path=str(audio_path),
    )
    t0 = time.time()
    print(f"  [P3] LLM planning composition ...", flush=True)
    output = await agent.generate(typed_input)
    agent.recompute_metrics(output)
    plan_dict = output.model_dump().get("content", {}).get("plan", {})
    print(f"  [P3] plan: {len(plan_dict.get('transitions', []))} transitions, "
          f"tone={plan_dict.get('color_grade', {}).get('tone', '?')!r}, "
          f"wall={time.time()-t0:.1f}s", flush=True)

    t0 = time.time()
    print(f"  [P3] ffmpeg mux + burn + grade ...", flush=True)
    svc = CompositorService()
    final_bytes = await svc.compose(
        video_path=str(video_path),
        audio_path=str(audio_path),
        subtitle_srt=srt_text,
        plan=plan_dict,
    )
    print(f"  [P3] compose produced {len(final_bytes)} bytes in {time.time()-t0:.1f}s", flush=True)
    return output.model_dump(), final_bytes


# ---------------------------------------------------------------------------
# Phase 4 — Compositor package + README (Phase 2 already wrote its own binaries)
# ---------------------------------------------------------------------------

def phase4_write_compositor_and_readme(compositor_package: dict, compositor_final_bytes: bytes):
    (COMP_DIR / "package.json").write_text(
        json.dumps(compositor_package, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (COMP_DIR / "final.mp4").write_bytes(compositor_final_bytes)
    print(
        f"  [P4] CompositorAgent -> 09_compositor/  "
        f"(package.json + final.mp4 {len(compositor_final_bytes)} bytes)",
        flush=True,
    )


def _write_readme():
    lines = [
        "# CompositorAgent Demo — \"The Note\" (Coffee Shop)\n\n",
        "Self-contained asset bundle for the CompositorAgent demo on the ",
        "/agents-test-results page. Generated by `scripts/gen_compositor_demo.py` ",
        "against live fal.ai APIs (fal-ai/nano-banana-2 image, fal-ai/kling-video/v2.6/pro I2V, ",
        "fal-ai/minimax/speech-02-turbo TTS, fal-ai/stable-audio music + ambience) + ",
        "LLM via CF AI Gateway (google-ai-studio/gemini-2.5-flash).\n\n",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n",
        "## Chain\n\n",
        "1. Screenplay seeded in-process (see 01_screenplay_seed.json).\n",
        "2. 4 keyframes (fal-ai/nano-banana-2) -> 02_keyframes/.\n",
        "3. 4 Kling I2V 5-second clips (fal-ai/kling-video/v2.6/pro) + ffmpeg concat -> 03_video/.\n",
        "4. NarrationAgent / MusicAgent / AmbienceAgent / SubtitleAgent / AudioMixAgent ",
        "called in-process (each agent.run() with a MaterializeContext that writes binaries ",
        "straight into the respective 04_..08_ folders).\n",
        "5. CompositorAgent run in-process: LLM plan + CompositorService.compose ",
        "(FFmpeg mux + subtitles burn + eq color grade) -> 09_compositor/.\n\n",
        "## Why the script bypasses KeyFrameAgent and Flask\n\n",
        "Phase 1 avoids KeyFrameAgent because its rework loop is unstable on hand-authored ",
        "seeds (attempt 2 can produce content only for attempt 3 to wipe it back to empty ",
        "when fed L2 rework notes). Phase 2 does not route through /api/assistant/execute ",
        "because InputResolver was returning an empty payload for the seed screenplay in an ",
        "earlier run (silent failure — NarrationAgent output had 0 segments). Calling the ",
        "agents in-process with hand-built typed inputs sidesteps both issues without ",
        "touching agent internals.\n\n",
        "## Replay (offline, no API cost)\n\n",
        "See `tests/agents/test_compositor_demo_replay.py`. It loads the checked-in ",
        "screenplay/video/audio/subtitle/plan and re-runs `CompositorService.compose` ",
        "to validate FFmpeg mux + burn + grade is reproducible from the bundle.\n",
    ]
    (DEMO_ROOT / "README.md").write_text("".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    print("=== Compositor demo generator (V2) ===", flush=True)
    print(f"Demo root: {DEMO_ROOT.relative_to(_REPO)}", flush=True)
    if not SEED_SCREENPLAY.is_file():
        print(f"ERROR: seed screenplay missing at {SEED_SCREENPLAY}", file=sys.stderr)
        return 1

    # Phase 1 — video (async, direct fal).
    print("\n-- Phase 1: keyframes + Kling I2V + concat --", flush=True)
    video_final = asyncio.run(_phase1_video())

    # Phase 2 — audio + subtitle via in-process agent calls.
    print("\n-- Phase 2: narration / music / ambience / subtitle / audio_mix --", flush=True)
    p2 = asyncio.run(phase2_audio_and_subtitle())

    # Locate AudioMix final audio on disk. AudioMixMaterializer writes
    # both per-scene mixes (sys_id=aud_mix_<scene_id>) and one final
    # aggregated mix (sys_id=aud_final).
    audio_final = MIX_DIR / "aud_final.wav"
    if not audio_final.is_file():
        # Fallback: biggest wav in 07_audio_mix/ (some earlier runs
        # wrote a single mix file under a per-scene sys_id only).
        wavs = sorted(MIX_DIR.glob("*.wav"), key=lambda p: p.stat().st_size, reverse=True)
        audio_final = wavs[0] if wavs else None
    if audio_final is None or not audio_final.is_file():
        print("ERROR: could not locate AudioMix final audio in 07_audio_mix/", file=sys.stderr)
        return 2
    print(f"  [P2] audio_final: {audio_final.relative_to(_REPO)}", flush=True)

    srt_text = p2.get("srt_text", "")
    if not srt_text:
        print("ERROR: SubtitleAgent produced no SRT text", file=sys.stderr)
        return 2

    # Load upstream JSON texts for CompositorAgent's LLM. video_package
    # doesn't come from an agent on this path — we fabricate a minimal
    # one that reflects the 4-shot / 5s reality of Phase 1.
    screenplay_payload = json.loads(SEED_SCREENPLAY.read_text(encoding="utf-8"))
    video_json_payload = {
        "content": {
            "scenes": [{
                "scene_id": "sc_001",
                "shot_segments": [
                    {"shot_id": s["shot_id"], "duration_sec": 5.0,
                     "video_asset": {"uri": str(VID_DIR / f"clip_{s['shot_id']}.mp4"), "format": "mp4"}}
                    for s in SHOTS
                ],
            }],
            "final_video_asset": {"uri": str(video_final), "format": "mp4"},
        },
    }
    audio_json_text = (MIX_DIR / "package.json").read_text(encoding="utf-8")
    subtitle_json_text = (SUB_DIR / "package.json").read_text(encoding="utf-8")
    video_json_text = json.dumps(video_json_payload, ensure_ascii=False, indent=2)

    # Phase 3 — CompositorAgent.
    print("\n-- Phase 3: CompositorAgent (LLM plan + FFmpeg) --", flush=True)
    compositor_pkg, compositor_bytes = asyncio.run(_phase3_compose(
        video_path=video_final,
        audio_path=audio_final,
        srt_text=srt_text,
        screenplay_payload=screenplay_payload,
        video_json_text=video_json_text,
        audio_json_text=audio_json_text,
        subtitle_json_text=subtitle_json_text,
    ))

    # Phase 4 — write Compositor artifacts + README.
    print("\n-- Phase 4: Compositor artifacts + README --", flush=True)
    phase4_write_compositor_and_readme(compositor_pkg, compositor_bytes)

    _write_readme()

    print("\n=== done ===", flush=True)
    print(f"final mp4: {(COMP_DIR / 'final.mp4').relative_to(_REPO)} "
          f"({(COMP_DIR / 'final.mp4').stat().st_size} bytes)", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
