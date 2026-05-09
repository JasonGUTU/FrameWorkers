#!/usr/bin/env python3
"""Scan 30_results/storytelling/ → results.json for the viewer.

Per case, collect:
  - final mp4 (CompositorAgent)
  - aud_final wav (AudioMixAgent)
  - narrator / music / ambience wavs
  - illustration segments (illustration_seg_*.png)
  - character anchors (illustration_anchor_*.png) — present iff a run
    after the 2026-05-09 anchor-dump patch
  - execution_log.json + plan_stack.json paths
  - per-step status summary (PASS / FAIL counts)

All paths are relative to e2e_30/ via the `30_results` symlink, so the
viewer's `fetch('./30_results/...')` resolves through http.server.

Re-run this script every time a new case lands; the viewer's reload picks
up the new manifest.
"""
from __future__ import annotations
import json
from pathlib import Path

HERE = Path(__file__).parent.resolve()
RESULTS_ROOT = HERE.parent / "30_results"
# eval_cases category → on-disk dir name. cr lives under "creative/",
# intake_img under "intakeimage/" (matches the cinematic-line driver's
# layout; the storytelling driver writes to "storytelling/").
CAT_DIRS = {
    "cr": "creative",
    "intake_img": "intakeimage",
    "storytelling": "storytelling",
}


def first_or_none(items: list) -> str | None:
    return items[0] if items else None


def list_files(d: Path, suffix: str | None = None) -> list[str]:
    if not d.exists():
        return []
    out: list[str] = []
    for p in sorted(d.iterdir()):
        if not p.is_file():
            continue
        if suffix and not p.name.endswith(suffix):
            continue
        # Path expressed relative to sub-agents/, which through the
        # e2e_30/30_results symlink lets fetch('./30_results/...')
        # resolve to the actual file.
        out.append(str(p.relative_to(HERE.parent)))
    return out


def build_case_entry(case_dir: Path) -> dict | None:
    if not case_dir.is_dir() or case_dir.name.endswith(".before_pb_fix"):
        return None
    workspace_globals = sorted(case_dir.glob("_workspace/workspace_global_*"))
    media = (workspace_globals[-1] / "artifacts" / "media") if workspace_globals else None
    has_media = media is not None and media.exists()

    illust_imgs = list_files(media / "IllustrationAgent" / "image", suffix=".png") if has_media else []
    seg_imgs = [p for p in illust_imgs if "_anchor_" not in Path(p).name
                and "illustration_seg_" in Path(p).name or "_illustration_seg_" in Path(p).name]
    # The actual seg files have names like step_2_<hash>_illustration_seg_NNN.png
    seg_imgs = [p for p in illust_imgs
                if "illustration_seg_" in Path(p).name and "_anchor_" not in Path(p).name]
    anchor_imgs = [p for p in illust_imgs if "anchor" in Path(p).name]

    if has_media:
        final_mp4 = first_or_none(list_files(media / "CompositorAgent" / "video", suffix=".mp4"))
        audio_final = first_or_none(list_files(media / "AudioMixAgent" / "audio", suffix=".wav"))
        narrator_wav = first_or_none(list_files(media / "NarratorAgent" / "audio", suffix=".wav"))
        music_wav = first_or_none(list_files(media / "MusicAgent" / "audio", suffix=".wav"))
        ambience_wav = first_or_none(list_files(media / "AmbienceAgent" / "audio", suffix=".wav"))
        # Cinematic line: KeyFrame images live under media/KeyFrameAgent/image
        keyframe_imgs = list_files(media / "KeyFrameAgent" / "image", suffix=".png")
        # Cinematic line: Video shot mp4s under media/VideoAgent/video (per-shot)
        video_shot_mp4s = list_files(media / "VideoAgent" / "video", suffix=".mp4")
    else:
        final_mp4 = audio_final = narrator_wav = music_wav = ambience_wav = None
        keyframe_imgs = []
        video_shot_mp4s = []

    exec_log_path = case_dir / "execution_log.json"
    plan_stack_path = case_dir / "plan_stack.json"
    exec_log_data: list[dict] = []
    if exec_log_path.exists():
        try:
            exec_log_data = json.loads(exec_log_path.read_text())
        except Exception:
            pass

    n_completed = sum(1 for e in exec_log_data if e.get("status") == "COMPLETED")
    n_total = len(exec_log_data)

    return {
        "case_name": case_dir.name,
        "final_mp4": final_mp4,
        "audio_final": audio_final,
        "narrator_wav": narrator_wav,
        "music_wav": music_wav,
        "ambience_wav": ambience_wav,
        "illustration_segments": sorted(seg_imgs),
        "character_anchors": sorted(anchor_imgs),
        "keyframe_images": sorted(keyframe_imgs),
        "video_shots": sorted(video_shot_mp4s),
        "execution_log_path": (
            str(exec_log_path.relative_to(HERE.parent)) if exec_log_path.exists() else None),
        "plan_stack_path": (
            str(plan_stack_path.relative_to(HERE.parent)) if plan_stack_path.exists() else None),
        "execution_summary": {
            "completed": n_completed,
            "total": n_total,
            "all_pass": n_completed == n_total and n_total > 0,
            "step_statuses": [
                {"agent_id": e.get("agent_id"), "status": e.get("status"),
                 "elapsed_sec": e.get("elapsed_sec")}
                for e in exec_log_data
            ],
        },
    }


def main() -> None:
    manifest: dict[str, dict] = {}
    for cat, dir_name in CAT_DIRS.items():
        cat_dir = RESULTS_ROOT / dir_name
        if not cat_dir.exists():
            continue
        for case_dir in sorted(cat_dir.iterdir()):
            entry = build_case_entry(case_dir)
            if entry:
                entry["category"] = cat
                manifest[entry["case_name"]] = entry

    out = HERE / "results.json"
    out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    print(f"Wrote {out} — {len(manifest)} cases:")
    for name, entry in manifest.items():
        s = entry["execution_summary"]
        print(f"  {name}: {s['completed']}/{s['total']} steps, "
              f"{len(entry['illustration_segments'])} illustrations, "
              f"{len(entry['character_anchors'])} anchors, "
              f"final_mp4={'✓' if entry['final_mp4'] else '✗'}")


if __name__ == "__main__":
    main()
