#!/usr/bin/env python3
"""One-shot: add bilingual subtitles + background music + ambience to an existing mp4.

Chain (no Plan Stack, no director — just descriptor.build_input + agent.run):
    VideoAnalysisAgent  ──┐
                          ├─▶ MusicAgent ──▶ aud_music_film.wav ─┐
                          └─▶ AmbienceAgent ─▶ aud_amb_film.wav ─┤
    TranscriptionAgent ─────▶ timestamped segments  ─▶ TranslationAgent ─▶ translated segments
                                                                          │
                          source mp4 ─────────────────────────────────────┤
                                                                          ▼
                                                AudioMixAgent ─▶ aud_final.wav
                                                                          │
    CompositorAgent ◀─ video + final audio + [cn segments, en segments] ◀┘
                  (materializer renders segments → SRT via pure-python helper
                   and ffmpeg burns both language tracks in one pass)
                          │
                          ▼
               compositor_final.mp4

Env (auto-loaded from .env):
  FAL_API_KEY         — real fal backends for audio + transcription
  GEMINI_API_KEY      — chat LLM (gemini-2.5-flash via CF AI Gateway native-Gemini Worker)
  FW_USE_REAL_MEDIA_GEN=1 is forced on so music/ambience/compositor use real backends.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

load_dotenv()

os.environ.setdefault("FW_USE_REAL_MEDIA_GEN", "1")

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from agents import get_agent_registry
from agents.base_agent import MaterializeContext
from inference.clients import LLMClient

logger = logging.getLogger("enrich_demo")


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
    """Run one sub-agent; persist binary assets under ``out_dir``.

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


async def _pipeline(source_video: Path, out_root: Path) -> Path:
    out_root.mkdir(parents=True, exist_ok=True)

    logger.info("▶ VideoAnalysisAgent")
    va_payload, _ = await run_agent(
        "VideoAnalysisAgent",
        resolved_artifacts={
            "source_video": artifact(path=str(source_video), mime="video/mp4"),
        },
        step_id="step_video_analysis",
        out_dir=out_root / "01_video_analysis",
    )

    logger.info("▶ TranscriptionAgent")
    tr_payload, _ = await run_agent(
        "TranscriptionAgent",
        resolved_artifacts={
            "source_media": artifact(path=str(source_video), mime="video/mp4"),
        },
        step_id="step_transcription",
        out_dir=out_root / "02_transcription",
    )
    segments = ((tr_payload or {}).get("content") or {}).get("segments") or []
    if not segments:
        raise RuntimeError("TranscriptionAgent returned no usable segments — aborting")

    logger.info("▶ TranslationAgent (CN transcript → EN transcript)")
    # TranslationAgent reads ``target_language`` from the upstream payload
    # (see agents/translation/descriptor.py). Injecting it on the
    # transcription payload is the project's canonical way of steering a
    # translation — and the translated payload preserves the transcript
    # shape (same content.segments with timestamps, just translated text).
    cn_tr_with_tgt = dict(tr_payload or {})
    cn_tr_with_tgt["target_language"] = "en"
    tn_payload, _ = await run_agent(
        "TranslationAgent",
        resolved_artifacts={
            "source_text": artifact(payload=cn_tr_with_tgt, mime="application/json"),
        },
        step_id="step_translation",
        out_dir=out_root / "03_translation",
    )
    # CompositorMaterializer's _extract_srt_texts handles both shapes:
    #   (a) the raw CN transcription payload (content.segments → rendered to SRT)
    #   (b) the EN translation wrapper (content.translated_payload.content.segments
    #       → wrapper peeled, inner segments rendered to SRT)
    # so one list of {CN transcript, EN translation} burns bilingually.
    cn_sub_payload = tr_payload
    en_sub_payload = tn_payload or {}

    logger.info("▶ MusicAgent")
    music_payload, music_files = await run_agent(
        "MusicAgent",
        resolved_artifacts={
            "video_analysis": artifact(payload=va_payload, mime="application/json"),
        },
        step_id="step_music",
        out_dir=out_root / "04_music",
    )
    music_wav = music_files.get("aud_music_film", "")

    logger.info("▶ AmbienceAgent")
    amb_payload, amb_files = await run_agent(
        "AmbienceAgent",
        resolved_artifacts={
            "video_analysis": artifact(payload=va_payload, mime="application/json"),
        },
        step_id="step_ambience",
        out_dir=out_root / "05_ambience",
    )
    amb_wav = amb_files.get("aud_amb_film", "")

    logger.info("▶ AudioMixAgent")
    # No assembled-video JSON manifest exists for an imported mp4; we pass
    # the VideoAnalysisAgent output as the video_package payload. The
    # AudioMix / Compositor LLMs read this as raw JSON text for planning —
    # they don't key-access upstream-schema fields.
    mix_payload, mix_files = await run_agent(
        "AudioMixAgent",
        resolved_artifacts={
            "video_package": artifact(payload=va_payload, mime="application/json"),
            "video_file": artifact(path=str(source_video), mime="video/mp4"),
            "music": artifact(payload=music_payload, mime="application/json"),
            "music_file": artifact(path=music_wav, mime="audio/wav"),
            "ambience": artifact(payload=amb_payload, mime="application/json"),
            "ambience_file": artifact(path=amb_wav, mime="audio/wav"),
        },
        step_id="step_audio_mix",
        out_dir=out_root / "06_audio_mix",
    )
    final_audio = mix_files.get("aud_final", "")

    logger.info("▶ CompositorAgent")
    _comp_payload, comp_files = await run_agent(
        "CompositorAgent",
        resolved_artifacts={
            "video_package": artifact(payload=va_payload, mime="application/json"),
            "video_file": artifact(path=str(source_video), mime="video/mp4"),
            "audio_package": artifact(payload=mix_payload, mime="application/json"),
            "audio_file": artifact(path=final_audio, mime="audio/wav"),
            "subtitle_tracks": [
                artifact(payload=cn_sub_payload, mime="application/json"),
                artifact(payload=en_sub_payload, mime="application/json"),
            ],
        },
        step_id="step_compositor",
        out_dir=out_root / "07_compositor",
    )
    final_mp4 = comp_files.get("compositor_final", "")
    if not final_mp4 or not Path(final_mp4).is_file():
        raise RuntimeError(f"compositor_final.mp4 not produced (got {final_mp4!r})")
    return Path(final_mp4)


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--source-video",
        default=str(
            Path("/home/zhendong_li/FrameWorkers/_workspaces/kling_capability_probe/")
            / "1B_voice_consistency_line_B.mp4"
        ),
    )
    p.add_argument(
        "--output-dir",
        default="/home/zhendong_li/FrameWorkers/_workspaces/enrich_1B_demo",
    )
    args = p.parse_args()

    src = Path(args.source_video).resolve()
    if not src.is_file():
        raise SystemExit(f"source video not found: {src}")

    out_root = Path(args.output_dir).resolve()
    final = asyncio.run(_pipeline(src, out_root))
    logger.info("🎬 Final composited mp4: %s", final)


if __name__ == "__main__":
    main()
