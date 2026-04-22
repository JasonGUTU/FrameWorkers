#!/usr/bin/env python3
"""One-shot: read a story and render it as an illustrated-audiobook video.

Chain (no Plan Stack, no director — just descriptor.build_input + agent.run):

    NarrationAgent ──▶ narration_script.json
                        │
                        ├─▶ IllustrationAgent ──▶ illustration_seg_NNN.png × N
                        │
                        └─▶ NarratorAgent ─────▶ aud_narrator_full.wav
                                                narrator_srt.json
                                                narrator_segment_timing.json
                                                              │
    CompositorAgent ◀─ illustrations + narrator wav + SRT + timing ◀┘
               │
               ▼
       compositor_final.mp4

Env (auto-loaded from .env):
  CF_AIG_TOKEN        — chat LLM (gemini-2.5-flash via CF AI Gateway) for
                        NarrationAgent's creative pass.
  INFERENCE_IMAGE_MODEL — Gemini image-gen model (defaults to
                        ``google/gemini-2.5-flash-image``). Used by
                        IllustrationAgent for text-to-image anchor + the
                        parallel image-to-image edits keyed off it.
  FAL_API_KEY         — real fal backend for TTS (Minimax Speech-02 via
                        ``FAL_TTS_MODEL``). Used by NarratorAgent.
  FW_USE_REAL_MEDIA_GEN=1 is forced on so image / TTS / compositor use
  real backends.

Usage:
  python scripts/run_illustrated_storytelling_demo.py
  python scripts/run_illustrated_storytelling_demo.py --story "Once there was..."
  python scripts/run_illustrated_storytelling_demo.py --story-file tale.txt -v
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

os.environ.setdefault("FW_USE_REAL_MEDIA_GEN", "1")

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from agents import get_agent_registry
from agents.base_agent import MaterializeContext
from inference.clients import LLMClient

logger = logging.getLogger("storytelling_demo")


DEFAULT_STORY = (
    "In a quiet village at the edge of an old forest, a girl named Lin found "
    "an abandoned lantern beside the river. When she lit it that evening, a "
    "tiny silver fox stepped out of the flame and spoke her name. The fox "
    "told Lin that it had been trapped in the lantern for a hundred years, "
    "waiting for someone kind enough to wonder what a lost light might "
    "mean. Together they walked home through the trees, and for the first "
    "time in her life Lin felt that the forest was listening back."
)


def artifact(
    *,
    payload: dict | None = None,
    path: str = "",
    scope: str = "global",
    mime: str = "application/json",
) -> dict:
    return {"payload": payload, "path": path, "scope": scope, "mime": mime}


async def run_agent(
    agent_id: str,
    resolved_artifacts: dict,
    step_id: str,
    out_dir: Path,
) -> tuple[dict | None, dict[str, str]]:
    """Run one sub-agent; persist binary / JSON assets under ``out_dir``.

    Returns ``(output_payload_dict, binary_paths_by_sys_id)``.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    registry = get_agent_registry()
    descriptor = registry.get_descriptor(agent_id)
    if descriptor is None:
        raise RuntimeError(f"Agent not registered: {agent_id}")

    llm = LLMClient()
    agent = descriptor.build_equipped_agent(llm)
    typed_input = descriptor.build_input(step_id, resolved_artifacts)

    binary_paths: dict[str, str] = {}
    materialize_ctx: MaterializeContext | None = None
    if getattr(agent, "materializer", None) is not None:

        def _persist(media_asset):
            p = out_dir / f"{media_asset.sys_id}.{media_asset.extension}"
            p.write_bytes(media_asset.data)
            binary_paths[media_asset.sys_id] = str(p.resolve())
            return str(p.resolve())

        materialize_ctx = MaterializeContext(
            step_id=step_id,
            typed_input=typed_input,
            persist_binary=_persist,
        )

    result = await agent.run(typed_input, materialize_ctx=materialize_ctx)

    # Best-effort cleanup of service handles on the materializer.
    mat = getattr(agent, "materializer", None)
    for attr in ("image_svc", "video_svc", "audio_svc", "svc"):
        svc = getattr(mat, attr, None) if mat is not None else None
        if svc is not None and hasattr(svc, "close"):
            try:
                await svc.close()
            except Exception:  # noqa: BLE001
                pass

    payload: dict | None
    if result.asset_dict is not None:
        payload = dict(result.asset_dict)
    elif result.output is not None:
        out = result.output
        payload = out.model_dump() if hasattr(out, "model_dump") else dict(out)
    else:
        payload = None

    summary = {
        "agent_id": agent_id,
        "passed": result.passed,
        "attempts": result.attempts,
        "eval_result": result.eval_result,
        "binary_paths": binary_paths,
    }
    (out_dir / "_summary.json").write_text(
        json.dumps(summary, indent=2, default=str, ensure_ascii=False),
        encoding="utf-8",
    )
    if payload is not None:
        (out_dir / f"{agent_id}.json").write_text(
            json.dumps(payload, indent=2, default=str, ensure_ascii=False),
            encoding="utf-8",
        )

    if not result.passed:
        raise RuntimeError(
            f"{agent_id} failed after {result.attempts} attempts: "
            f"{result.eval_result.get('summary', '')}"
        )

    logger.info("✅ %s OK (attempts=%s)", agent_id, result.attempts)
    return payload, binary_paths


async def _pipeline(story_text: str, out_root: Path) -> Path:
    out_root.mkdir(parents=True, exist_ok=True)

    # Write the story to disk for reproducibility and to make the run
    # directory self-contained.
    (out_root / "00_input_story.txt").write_text(story_text, encoding="utf-8")

    logger.info("▶ NarrationAgent (story → narrator script + segments + image prompts)")
    narr_payload, _ = await run_agent(
        "NarrationAgent",
        resolved_artifacts={
            "creative_brief": artifact(
                payload={"content": {"text": story_text}},
                mime="application/json",
            ),
        },
        step_id="step_narration",
        out_dir=out_root / "01_narration",
    )

    # Peek at what NarrationAgent decided for the console — gives instant
    # feedback on whether segment slicing looks right before we burn a
    # dozen Gemini image calls.
    seg_count = len((narr_payload or {}).get("content", {}).get("segments", []))
    line_count = sum(
        len(s.get("lines", []))
        for s in (narr_payload or {}).get("content", {}).get("segments", [])
    )
    style = (narr_payload or {}).get("content", {}).get("overall_style", "?")
    lang = (narr_payload or {}).get("content", {}).get("language", "?")
    logger.info(
        "  → %d segment(s), %d narrator line(s), lang=%s, style=%r",
        seg_count, line_count, lang, style,
    )

    logger.info("▶ IllustrationAgent (one image per segment, anchored to seg_001)")
    _illus_payload, illus_files = await run_agent(
        "IllustrationAgent",
        resolved_artifacts={
            "narration_script": artifact(payload=narr_payload, mime="application/json"),
        },
        step_id="step_illustration",
        out_dir=out_root / "02_illustration",
    )
    illus_count = sum(
        1 for k in illus_files if k.startswith("illustration_seg_")
    )
    logger.info("  → %d illustration(s) generated", illus_count)
    if illus_count == 0:
        raise RuntimeError("IllustrationAgent produced zero images — aborting")

    logger.info("▶ NarratorAgent (per-line TTS + concat + per-segment timing + SRT)")
    _narrator_payload, narrator_files = await run_agent(
        "NarratorAgent",
        resolved_artifacts={
            "narration_script": artifact(payload=narr_payload, mime="application/json"),
        },
        step_id="step_narrator",
        out_dir=out_root / "03_narrator",
    )
    audio_path = narrator_files.get("aud_narrator_full", "")
    srt_json_path = narrator_files.get("narrator_srt", "")
    timing_json_path = narrator_files.get("narrator_segment_timing", "")
    for label, p in [
        ("aud_narrator_full", audio_path),
        ("narrator_srt", srt_json_path),
        ("narrator_segment_timing", timing_json_path),
    ]:
        if not p or not Path(p).is_file():
            raise RuntimeError(
                f"NarratorAgent missing expected artifact {label!r} (got {p!r})"
            )

    # Load back the two side-car JSON envelopes so we can hand their
    # payloads to CompositorAgent's build_input via artifact(payload=...).
    srt_envelope = json.loads(Path(srt_json_path).read_text(encoding="utf-8"))
    timing_envelope = json.loads(Path(timing_json_path).read_text(encoding="utf-8"))

    logger.info("▶ CompositorAgent (slideshow: ffmpeg concat images → mux audio → burn SRT)")
    # Assemble the illustration collection in segment order. The
    # IllustrationMaterializer writes files as ``illustration_seg_NNN.png``
    # via sys_id, so a plain sort by key recovers render order;
    # CompositorAgent's descriptor will re-sort defensively anyway.
    illus_artifacts = [
        artifact(path=path, mime="image/png")
        for sys_id, path in sorted(illus_files.items())
        if sys_id.startswith("illustration_seg_")
    ]

    _comp_payload, comp_files = await run_agent(
        "CompositorAgent",
        resolved_artifacts={
            "illustration_sequence": illus_artifacts,
            "audio_file": artifact(path=audio_path, mime="audio/wav"),
            "subtitle_tracks": [
                artifact(payload=srt_envelope, mime="application/json"),
            ],
            "segment_timing": artifact(payload=timing_envelope, mime="application/json"),
        },
        step_id="step_compositor",
        out_dir=out_root / "04_compositor",
    )
    final_mp4 = comp_files.get("compositor_final", "")
    if not final_mp4 or not Path(final_mp4).is_file():
        raise RuntimeError(f"compositor_final.mp4 not produced (got {final_mp4!r})")
    return Path(final_mp4)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render an illustrated-audiobook video from a story text.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--story", type=str, default=None,
        help="Inline story text (quote it).",
    )
    parser.add_argument(
        "--story-file", type=Path, default=None,
        help="Path to a plain-text story file (utf-8).",
    )
    parser.add_argument(
        "--out", type=Path,
        default=_ROOT / "_workspaces" / "storytelling_demo",
        help="Output directory for per-step artifacts + final mp4.",
    )
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    if args.story_file:
        story_text = args.story_file.read_text(encoding="utf-8").strip()
    elif args.story:
        story_text = args.story.strip()
    else:
        story_text = DEFAULT_STORY

    if not story_text:
        raise SystemExit("Empty story text — nothing to narrate.")

    logger.info(
        "Story length: %d chars | output dir: %s",
        len(story_text), args.out.resolve(),
    )

    final_mp4 = asyncio.run(_pipeline(story_text, args.out))
    print()
    print(f"🎬 Final illustrated-audiobook video: {final_mp4}")
    print(f"   (intermediate artifacts in {args.out.resolve()})")


if __name__ == "__main__":
    main()
