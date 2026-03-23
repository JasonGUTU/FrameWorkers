"""One-shot fal.ai integration smoke script.

This script verifies end-to-end interoperability for:
1) Image generation (FalImageService)
2) One-shot video materialization (VideoMaterializer + FalVideoService)
3) Voice generation (FalAudioService)
4) Optional final mux (audio + shot video)

It exercises the current "keyframe for stability/consistency" mode with a
single scene and a single shot selected from a saved workspace asset bundle.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


def _resolve_project_root() -> Path:
    env_root = os.getenv("FRAMEWORKERS_ROOT")
    if env_root:
        candidate = Path(env_root).expanduser().resolve()
        if (candidate / "agents" / "__init__.py").exists():
            return candidate
    for parent in Path(__file__).resolve().parents:
        if (parent / "agents" / "__init__.py").exists():
            return parent
    raise RuntimeError(
        "Cannot locate project root containing agents/__init__.py. "
        "Set FRAMEWORKERS_ROOT to override."
    )


PROJECT_ROOT = _resolve_project_root()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agents.video.materializer import VideoMaterializer
from inference.generation.audio_generators.service import FalAudioService
from inference.generation.image_generators.service import FalImageService
from inference.generation.video_generators.service import FalVideoService


def _require_fal_key() -> None:
    if not os.getenv("FAL_API_KEY", "").strip():
        raise RuntimeError("FAL_API_KEY is required")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _find_asset_file(workspace_dir: Path, prefix: str) -> Path:
    matches = sorted(workspace_dir.glob(f"{prefix}*.json"))
    if not matches:
        raise FileNotFoundError(f"No file matching {prefix}*.json in {workspace_dir}")
    return matches[0]


def _pick_scene_and_shot(storyboard: dict[str, Any], shot_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
    for scene in storyboard.get("content", {}).get("scenes", []):
        for shot in scene.get("shots", []):
            if shot.get("shot_id", "") == shot_id:
                return scene, shot
    raise ValueError(f"shot_id '{shot_id}' not found in storyboard")


def _build_narration_from_linked_blocks(screenplay: dict[str, Any], linked_blocks: list[str]) -> str:
    blocks_index: dict[str, dict[str, Any]] = {}
    for scene in screenplay.get("content", {}).get("scenes", []):
        for block in scene.get("blocks", []):
            bid = block.get("block_id", "")
            if bid:
                blocks_index[bid] = block

    texts: list[str] = []
    for bid in linked_blocks:
        block = blocks_index.get(bid, {})
        text = str(block.get("text", "")).strip()
        if text:
            texts.append(text)
    if texts:
        return " ".join(texts)
    # fallback
    return "A short cinematic moment unfolds with emotional precision."


def _build_one_shot_payload(
    *,
    work_dir: Path,
    storyboard: dict[str, Any],
    shot_id: str,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Build one-shot video plan + upstream assets from selected storyboard shot."""
    scene, shot = _pick_scene_and_shot(storyboard, shot_id)
    scene_id = scene.get("scene_id", "sc_001")
    duration = float(shot.get("estimated_duration_sec", 2.0) or 2.0)
    keyframe_notes = (
        shot.get("keyframe_plan", {}).get("keyframe_notes", [])
        if isinstance(shot.get("keyframe_plan", {}), dict)
        else []
    )
    # Keep one or two keyframe anchors.
    note_1 = str(keyframe_notes[0]).strip() if len(keyframe_notes) >= 1 else ""
    note_2 = str(keyframe_notes[1]).strip() if len(keyframe_notes) >= 2 else note_1
    if not note_1:
        note_1 = str(shot.get("visual_goal", "")).strip() or "Establish the shot look and subject."
    if not note_2:
        note_2 = str(shot.get("action_focus", "")).strip() or "Keep identity and scene consistency."

    asset_dict = {
        "content": {
            "scenes": [
                {
                    "scene_id": scene_id,
                    "shot_segments": [
                        {
                            "shot_id": shot_id,
                            "estimated_duration_sec": duration,
                            "video_asset": {"format": "mp4"},
                        }
                    ],
                    "transition_plan": [],
                    "scene_clip_asset": {"format": "mp4"},
                }
            ],
            "final_video_asset": {"format": "mp4"},
        }
    }

    assets = {
        "storyboard": {
            "content": {
                "scenes": [
                    {
                        "scene_id": scene_id,
                        "scene_consistency_pack": scene.get("scene_consistency_pack", {}),
                        "shots": [
                            {
                                "shot_id": shot_id,
                                "shot_type": shot.get("shot_type", "medium"),
                                "visual_goal": shot.get("visual_goal", ""),
                                "action_focus": shot.get("action_focus", ""),
                                "characters_in_frame": shot.get("characters_in_frame", []),
                                "props_in_frame": shot.get("props_in_frame", []),
                                "camera": shot.get("camera", {}),
                                "keyframe_plan": {
                                    "keyframe_count": 2 if note_2 else 1,
                                    "keyframe_notes": [
                                        note_1,
                                        note_2,
                                    ],
                                },
                            }
                        ],
                    }
                ]
            }
        },
        "keyframes": {
            "content": {
                "scenes": [
                    {
                        "scene_id": scene_id,
                        "shots": [
                            {
                                "shot_id": shot_id,
                                "keyframes": [
                                    {
                                        "image_asset": {"uri": str(work_dir / "kf_01.png")},
                                        "prompt_summary": note_1,
                                    },
                                    {
                                        "image_asset": {"uri": str(work_dir / "kf_02.png")},
                                        "prompt_summary": note_2,
                                    },
                                ],
                            }
                        ],
                    }
                ]
            }
        },
    }
    selected = {
        "scene_id": scene_id,
        "shot_id": shot_id,
        "linked_blocks": shot.get("linked_blocks", []),
        "duration_sec": duration,
        "note_1": note_1,
        "note_2": note_2,
    }
    return asset_dict, assets, selected


async def _run(
    *,
    output_dir: Path,
    workspace_dir: Path,
    shot_id: str,
    narration_text: str | None = None,
) -> dict[str, Any]:
    _require_fal_key()
    output_dir.mkdir(parents=True, exist_ok=True)

    image_svc = FalImageService()
    video_svc = FalVideoService()
    audio_svc = FalAudioService()
    try:
        storyboard = _load_json(_find_asset_file(workspace_dir, "storyboardagent_storyboard_"))
        screenplay = _load_json(_find_asset_file(workspace_dir, "screenplayagent_screenplay_"))
        asset_dict, assets, selected = _build_one_shot_payload(
            work_dir=output_dir,
            storyboard=storyboard,
            shot_id=shot_id,
        )

        if narration_text is None:
            narration_text = _build_narration_from_linked_blocks(
                screenplay,
                selected.get("linked_blocks", []),
            )

        # 1) image step: generate + edit to form two keyframe anchors
        img_1 = await image_svc.generate_image(selected["note_1"])
        img_2 = await image_svc.edit_image(
            img_1,
            selected["note_2"],
        )
        (output_dir / "kf_01.png").write_bytes(img_1)
        (output_dir / "kf_02.png").write_bytes(img_2)

        # 2) video step: one-shot materialization
        materializer = VideoMaterializer(video_service=video_svc)
        media_assets = await materializer.materialize(
            project_id="proj_fal_one_shot",
            asset_dict=asset_dict,
            assets=assets,
        )
        clip_asset = next((m for m in media_assets if m.sys_id == f"clip_{shot_id}"), None)
        if clip_asset is None:
            raise RuntimeError(f"clip_{shot_id} was not produced by VideoMaterializer")
        (output_dir / f"clip_{shot_id}.mp4").write_bytes(clip_asset.data)

        # 3) voice step
        wav = await audio_svc.generate_speech(narration_text or "", response_format="wav")
        (output_dir / "voice.wav").write_bytes(wav)

        # 4) optional mux step (falls back to original video when ffmpeg unavailable)
        muxed = await audio_svc.mux_audio_with_video(video_bytes=clip_asset.data, audio_bytes=wav)
        (output_dir / f"delivery_{shot_id}.mp4").write_bytes(muxed)

        summary = {
            "status": "ok",
            "output_dir": str(output_dir),
            "workspace_dir": str(workspace_dir),
            "selected_shot": selected,
            "narration_text": narration_text,
            "files": {
                "keyframe_1": "kf_01.png",
                "keyframe_2": "kf_02.png",
                "shot_clip": f"clip_{shot_id}.mp4",
                "voice": "voice.wav",
                "delivery": f"delivery_{shot_id}.mp4",
            },
            "bytes": {
                "keyframe_1": len(img_1),
                "keyframe_2": len(img_2),
                "shot_clip": len(clip_asset.data),
                "voice": len(wav),
                "delivery": len(muxed),
            },
            "fal_models": {
                "image": image_svc.model,
                "video": video_svc.model,
                "tts": audio_svc.tts_model,
            },
            "notes": [
                "Video was generated from one shot using two keyframe anchors.",
                "Keyframes are used as stability/consistency anchors.",
                "If ffmpeg is unavailable, delivery may match raw clip bytes.",
            ],
        }
        (output_dir / "summary.json").write_text(
            json.dumps(summary, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return summary
    finally:
        await image_svc.close()
        await video_svc.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="fal.ai one-shot smoke integration script")
    parser.add_argument(
        "--output-dir",
        default=str(PROJECT_ROOT / "Runtime" / "fal_one_shot"),
        help="Output directory for generated artifacts.",
    )
    parser.add_argument(
        "--workspace-dir",
        default=str(
            PROJECT_ROOT
            / "Runtime"
            / "saved_workspaces"
            / "workspace_simplified_20260320_105714"
        ),
        help="Workspace directory containing storyboard/screenplay/story asset JSONs.",
    )
    parser.add_argument(
        "--shot-id",
        default="sh_001",
        help="Shot id to execute (must exist in storyboard asset).",
    )
    parser.add_argument(
        "--narration",
        default="",
        help="Optional narration text override for FalAudioService TTS.",
    )
    args = parser.parse_args()

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(args.output_dir).expanduser().resolve() / ts
    workspace_dir = Path(args.workspace_dir).expanduser().resolve()
    narration = args.narration.strip() or None
    summary = asyncio.run(
        _run(
            output_dir=output_dir,
            workspace_dir=workspace_dir,
            shot_id=args.shot_id,
            narration_text=narration,
        )
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

