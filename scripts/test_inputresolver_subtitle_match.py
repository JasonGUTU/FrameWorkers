#!/usr/bin/env python3
"""Standalone unit test of the caption fix on TranscriptionAgent.

Question: with the new TranscriptionAgent caption (``"SRT-shaped subtitle
artifact — ready for direct burn-in"``), does InputResolver actually
route the transcript artifact into CompositorAgent's [subtitle_tracks]
label?

This bypasses backend / plan stack entirely. We:
  1. Construct a minimal fake GlobalMemory/FileManager whose registry
     mirrors what the e2e_samurai_20260506_222914 run produced, BUT with
     the transcript entry's caption replaced with the new build_captions
     output.
  2. Render CompositorAgent's input_needs_description from descriptor.
  3. Call InputResolver.aresolve directly and inspect resolved_artifacts.

Pass criterion: ``resolved_artifacts["subtitle_tracks"]`` is a non-empty
list whose entries point to the transcript JSON path.
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path
from typing import Any


_REPO = Path("/home/zhendong_li/FrameWorkers")
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))
_BACKEND_SRC = _REPO / "plan-stack-backend"
if str(_BACKEND_SRC) not in sys.path:
    sys.path.insert(0, str(_BACKEND_SRC))

from dotenv import load_dotenv  # noqa: E402

load_dotenv(_REPO / ".env")

from agents.transcription.descriptor import (  # noqa: E402
    build_captions as transcription_build_captions,
)
from agents.compositor.descriptor import DESCRIPTOR as compositor_desc  # noqa: E402
from src.assistant.workspace.input_resolver import InputResolver  # noqa: E402
from src.assistant.workspace.models import ArtifactRef  # noqa: E402
from inference.clients import LLMClient  # noqa: E402


# Existing run we replay against
_RUN_DIR = _REPO / "evals/sub-agents/e2e_samurai_20260506_222914"
_WS_DIR = _RUN_DIR / "workspace_global_20260506_222922"


def _new_transcript_caption() -> str:
    """Render the NEW caption (post-fix) for an existing transcript artifact.

    Mirrors what TranscriptionAgent's new build_captions would emit when
    the agent re-runs over the existing audio.
    """
    transcript_json = next(
        (_WS_DIR / "artifacts/TranscriptionAgent").glob("*.json")
    )
    output_dict = json.loads(transcript_json.read_text())
    caps = transcription_build_captions("TranscriptionAgent", output_dict)
    return caps["TranscriptionAgent"]["caption"]


# ── minimal fake memory + file_manager ────────────────────────────────


class FakeGlobalMemory:
    """Subset of GlobalMemory surface that InputResolver actually calls.

    Returns ``(captions_index_text, id_to_path_list)`` — matches the real
    GlobalMemory.get_captions_index signature.
    """

    def __init__(
        self,
        entries: list[tuple[str, str, str]],  # (caption, path, mime)
    ) -> None:
        self._entries = entries

    def get_captions_index(self) -> tuple[str, list[str]]:
        lines: list[str] = []
        id_to_path: list[str] = []
        for i, (caption, path, _mime) in enumerate(self._entries):
            lines.append(f"#{i}  {caption}")
            id_to_path.append(path)
        return "\n\n".join(lines), id_to_path

    def get_by_paths(self, paths: list[str]) -> list[ArtifactRef]:
        want = set(paths)
        return [
            ArtifactRef(caption=cap, scope="global", path=path, mime=mime)
            for (cap, path, mime) in self._entries
            if path in want
        ]


class FakeFileManager:
    """JSON-path loader (read_binary_from_uri returns raw bytes).

    InputResolver only calls ``read_binary_from_uri`` to load JSON
    payloads — for paths we don't care about (mp4/wav), it never gets
    invoked because those entries don't have JSON payloads.
    """

    def read_binary_from_uri(self, uri: str) -> bytes:
        path = uri[7:] if uri.startswith("file://") else uri
        with open(path, "rb") as fh:
            return fh.read()


# ── build the registry: 4 real entries + transcript with NEW caption ──


def _build_registry() -> list[tuple[str, str, str]]:
    """Construct the artifact registry the resolver should match against.

    We include the real produce-side captions for screenplay / video /
    audio so the resolver has a realistic decision surface (otherwise
    the 'transcript is the only candidate' shortcut would mask whether
    the caption fix actually works).
    """
    sp_path = next(
        (_WS_DIR / "artifacts/ScreenplayAgent").glob("*.json")
    )
    video_path = next(
        (_WS_DIR / "artifacts/media/VideoAgent/video").glob("*_clip_final.mp4")
    )
    video_pkg_path = next(
        (_WS_DIR / "artifacts/VideoAgent").glob("*.json")
    )
    audio_path = next(
        (_WS_DIR / "artifacts/media/AudioMixAgent/audio").glob("*_aud_final.wav")
    )
    audio_pkg_path = next(
        (_WS_DIR / "artifacts/AudioMixAgent").glob("*.json")
    )
    transcript_path = next(
        (_WS_DIR / "artifacts/TranscriptionAgent").glob("*.json")
    )

    return [
        (
            "Screenplay: 3 scene(s), 10 shot(s). Input for keyframe "
            "planning and audio scoring. Produced by ScreenplayAgent.",
            str(sp_path),
            "application/json",
        ),
        (
            "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_final] "
            "Complete assembled video bytes (10 shots). Final visual "
            "deliverable — consumed by a downstream audio-mix step's "
            "materializer via ffmpeg for audio extraction + muxing. "
            "Produced by VideoAgent.",
            str(video_path),
            "video/mp4",
        ),
        (
            "[JSON MANIFEST] Video-assembly planning metadata: 3 "
            "scene(s), 10 shot clip(s) with timing. Produced by VideoAgent.",
            str(video_pkg_path),
            "application/json",
        ),
        (
            "[BINARY WAV FILE · mime=audio/wav · sys_id aud_final] "
            "Final-mix audio bytes — all source audio tracks "
            "(dialogue / foley / music / ambience / narrator) merged. "
            "Ready to be muxed onto the delivered video by a downstream "
            "compositing step. Produced by AudioMixAgent.",
            str(audio_path),
            "audio/wav",
        ),
        (
            "[JSON MANIFEST] Final-audio-mix envelope: amix of 3 source "
            "track(s) (video dialogue+foley + optional global music/"
            "ambience/narrator). Planning manifest only; the wav is a "
            "sibling artifact. Produced by AudioMixAgent.",
            str(audio_pkg_path),
            "application/json",
        ),
        # ★ THE ENTRY UNDER TEST — new transcript caption from the fix
        (_new_transcript_caption() + " Produced by TranscriptionAgent.",
         str(transcript_path),
         "application/json"),
    ]


async def main() -> int:
    registry = _build_registry()

    print("=== artifact registry the resolver will see ===")
    for i, (cap, path, mime) in enumerate(registry):
        is_transcript = "Transcript" in cap and "SRT" in cap
        marker = " ★" if is_transcript else "  "
        print(f"  {marker} #{i}  [{mime:18}] {cap[:90]}...")
    print()

    print("=== CompositorAgent.input_needs_description ===")
    print(compositor_desc.input_needs_description[:400] + "...")
    print()

    gm = FakeGlobalMemory(registry)
    fm = FakeFileManager()
    llm = LLMClient()
    resolver = InputResolver(gm, fm, llm)

    print("=== running InputResolver.aresolve() ===")
    result = await resolver.aresolve(
        agent_id="CompositorAgent",
        step_id="standalone_test",
        input_needs_description=compositor_desc.input_needs_description,
    )

    resolved = result.get("resolved_artifacts", {})
    print()
    print("=== resolved_artifacts (per-label result) ===")
    for label in sorted(resolved.keys()):
        v = resolved[label]
        if isinstance(v, list):
            print(f"  [{label}] (collection): {len(v)} entries")
            for e in v:
                cap = (e.get("caption") or "")[:70] if isinstance(e, dict) else str(e)[:70]
                pth = (e.get("path") or "")[-50:] if isinstance(e, dict) else ""
                print(f"    - {cap}... | path=...{pth}")
        elif isinstance(v, dict):
            cap = (v.get("caption") or "")[:70]
            pth = (v.get("path") or "")[-50:]
            print(f"  [{label}] (single):  {cap}... | path=...{pth}")
        else:
            print(f"  [{label}]: {v}")

    # ── PASS / FAIL verdict ───────────────────────────────────
    print()
    sub = resolved.get("subtitle_tracks") or []
    transcript_paths_in_sub = [
        e.get("path") for e in sub
        if isinstance(e, dict) and "TranscriptionAgent" in (e.get("path") or "")
    ]
    if transcript_paths_in_sub:
        print(f"✅ PASS — InputResolver routed transcript to [subtitle_tracks]: "
              f"{transcript_paths_in_sub[0][-60:]}")
        return 0
    else:
        print(f"❌ FAIL — [subtitle_tracks] does NOT contain the transcript "
              f"(got {len(sub)} entries: {sub})")
        print(f"   (rationale from resolver: "
              f"{(result.get('rationale') or '')[:200]})")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
