"""Generate image / video fixtures for the assistant_test eval.

Output layout::

    assistant_test/fixtures/
    ├── images/<case_name>.png        # 8 files (one per image-intake case)
    ├── videos/<fixture_id>.mp4       # 10 files (covering 23 video-intake cases)
    └── _metadata.json                # prompts + mappings, audit log

Modes:
  * Default — dry-run. Prints every image prompt, every video starting-image
    + motion-hint pair, the 23-case → 10-fixture mapping, and an estimated
    cost. NO API calls.
  * ``--execute`` — real generation. ImageService (OpenRouter Gemini-image,
    per CLAUDE.md flux is forbidden). Video uses ImageService for the
    starting frame, then Kling i2v via VideoService (FAL_VIDEO_MODEL).

Cost / time estimates (executing both stages):
  * Image: 8 + 10 starting frames = 18 × ~$0.005 ≈ $0.09, < 1 min
  * Video: 10 × Kling i2v 5s ≈ $5, ~5–15 min total

Re-running ``--execute`` regenerates everything (overwrites existing).
Use ``--only-images`` / ``--only-videos`` to scope the regeneration.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import time
from pathlib import Path
from typing import Optional


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
PKG_ROOT = REPO_ROOT / "plan-stack-backend"
for _p in (str(REPO_ROOT), str(PKG_ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)


CASES_PATH = SCRIPT_DIR / "assistant_test_cases.json"
FIXTURES_DIR = SCRIPT_DIR / "fixtures"
IMAGES_DIR = FIXTURES_DIR / "images"
VIDEOS_DIR = FIXTURES_DIR / "videos"
METADATA_PATH = FIXTURES_DIR / "_metadata.json"


# ---------------------------------------------------------------------------
# Image fixtures: 8 — one per image-intake case
# ---------------------------------------------------------------------------
# Each prompt distills user_goal's character / role / aesthetic so the
# generated image is what BriefEnricher would describe consistently with
# the brief, avoiding the upstream_input_rejected path we hit before.

IMAGE_FIXTURES: dict[str, str] = {
    # cultivation-fantasy male hero
    "intake_img_01": (
        "Anime-style portrait of a young male cultivation-fantasy hero, "
        "determined expression, ancient Chinese-inspired flowing robes, "
        "subtle mystical aura, upper-body shot, cinematic lighting, "
        "high-detail animated drama style, 3:4 portrait composition"
    ),
    # animated-drama young CEO male character
    "complex_19": (
        "Animated mini-drama character portrait of a handsome young CEO, "
        "sharp dark suit, confident gaze, modern office background blurred, "
        "cinematic warm-cool lighting, polished animated-drama art style, "
        "3:4 portrait"
    ),
    # cyberpunk female lead
    "complex_23": (
        "Cyberpunk female lead portrait, neon city lights reflected on her "
        "face, sleek futuristic outfit with subtle glowing accents, intense "
        "determined gaze, dystopian sci-fi mood, dark teal and magenta "
        "palette, 3:4 portrait"
    ),
    # fox protagonist (folk tale audiobook)
    "storytelling_full_01": (
        "Children's storybook illustration of a clever red fox protagonist "
        "standing upright on a forest path, expressive intelligent eyes, "
        "slight smile, soft watercolor style with warm autumn palette, "
        "audiobook cover composition"
    ),
    # heroine character (folktale audiobook, female protagonist)
    "storytelling_imgref_01": (
        "Children's storybook illustration of a young heroine, traditional "
        "folktale attire, kind expression, gentle posture, simple village "
        "background, watercolor storybook style, audiobook cover composition"
    ),
    # grandmother storyteller (English-Spanish bilingual folk tale)
    "storytelling_imgref_bilingual_01": (
        "Children's storybook illustration of an elderly storyteller "
        "grandmother, warm smile, woven shawl, hands gesturing as if "
        "narrating, soft hearth lighting, watercolor folk-art style, "
        "audiobook cover composition"
    ),
    # protagonist (myth audiobook with guzheng score)
    "storytelling_imgref_music_01": (
        "Children's storybook illustration of a mythological protagonist in "
        "ancient Chinese-inspired robe, flowing sleeves, calm expression, "
        "subtle musical motif (guzheng silhouette in background), watercolor "
        "ink-wash style, audiobook cover composition"
    ),
    # fox-and-crow fable protagonist (bilingual)
    "storytelling_ultra_01": (
        "Children's storybook illustration of the classic fox-and-crow "
        "fable: a clever fox standing at the base of a tree looking up at "
        "a crow on a branch holding a piece of cheese, autumn forest "
        "setting, warm watercolor fable-art style, audiobook cover "
        "composition"
    ),
}


# ---------------------------------------------------------------------------
# Video fixtures: 10 — covering 23 video-intake cases
# ---------------------------------------------------------------------------
# Each video is generated as Kling i2v: a starting image (from t2i) +
# a motion hint that drives 5 seconds of action. Both are tuned to
# match the user_goal of every case mapped to this fixture.

VIDEO_FIXTURES: dict[str, dict[str, str]] = {
    "mini_drama_generic": {
        "starting_image_prompt": (
            "Cinematic still of two modern characters facing each other in "
            "a contemporary apartment living room, soft dramatic lighting, "
            "expressive faces, Chinese mini-drama film look, 16:9 aspect"
        ),
        "motion_hint": (
            "Two characters argue heatedly with expressive hand gestures, "
            "the camera holds on a tight medium shot, slight push-in, "
            "natural conversational rhythm"
        ),
    },
    "ceo_romance_confrontation": {
        "starting_image_prompt": (
            "Cinematic still of a young male CEO in dark suit and a young "
            "female lead in business attire, facing each other tensely "
            "across a modern office desk, city skyline through window, "
            "Chinese mini-drama film look, 16:9"
        ),
        "motion_hint": (
            "Female lead steps forward angrily and points her finger, the "
            "CEO catches her wrist firmly, intense locked eye contact, "
            "subtle camera dolly-in on their faces"
        ),
    },
    "rainy_night": {
        "starting_image_prompt": (
            "Cinematic still of a lone figure standing on a wet city street "
            "at night, neon signs reflected in puddles, heavy rain, "
            "melancholic mood, Chinese mini-drama film look, 16:9"
        ),
        "motion_hint": (
            "Heavy rain falls steadily, the character walks slowly forward "
            "through the downpour, raindrops visible streaking past, "
            "camera slowly tracks alongside"
        ),
    },
    "costume_drama": {
        "starting_image_prompt": (
            "Cinematic still of two characters in elaborate classical "
            "Chinese costume-drama robes (Tang or Song dynasty styling) "
            "standing in an ancient courtyard, lanterns hanging, soft "
            "warm lighting, period film look, 16:9"
        ),
        "motion_hint": (
            "Characters bow gracefully toward each other, robes and "
            "sleeves flow with the movement, camera slowly dollies "
            "forward through the courtyard"
        ),
    },
    "confrontation": {
        "starting_image_prompt": (
            "Cinematic still of two modern figures facing off in a dim "
            "back alley at night, tension visible in their stances, "
            "harsh single-source lighting, gritty Chinese mini-drama "
            "film look, 16:9"
        ),
        "motion_hint": (
            "One figure steps forward menacingly, the other recoils a "
            "step back, both keep their guard up, harsh shadows shift "
            "across their faces"
        ),
    },
    "fight_scene": {
        "starting_image_prompt": (
            "Cinematic still of two martial-arts fighters mid-stance in an "
            "outdoor arena at dusk, ready posture, dramatic backlighting, "
            "Chinese action mini-drama film look, 16:9"
        ),
        "motion_hint": (
            "The two fighters exchange rapid martial-arts strikes — punch, "
            "block, kick, dodge — dynamic handheld-feel camera follows "
            "the action"
        ),
    },
    "female_lead_crying": {
        "starting_image_prompt": (
            "Cinematic close-up still of a young female lead with tears "
            "welling in her eyes, soft warm window light, emotional "
            "vulnerability, Chinese mini-drama film look, 16:9"
        ),
        "motion_hint": (
            "Tears stream down her face, her lips tremble, her head slowly "
            "lowers as she struggles to hold back sobs, her hands shake "
            "gently in the foreground"
        ),
    },
    "english_drama": {
        "starting_image_prompt": (
            "Cinematic still of two English-speaking characters seated "
            "across a small modern table in a Western-style living room, "
            "mid-conversation, naturalistic lighting, contemporary mini-"
            "drama film look, 16:9"
        ),
        "motion_hint": (
            "The two characters speak in English with expressive gestures, "
            "the camera cuts between their talking heads, natural "
            "conversational beats"
        ),
    },
    "meeting_scene": {
        "starting_image_prompt": (
            "Cinematic still of a group of corporate professionals seated "
            "around a long conference table in a modern glass meeting "
            "room, papers and laptops in front of them, mid-discussion, "
            "16:9"
        ),
        "motion_hint": (
            "The participants discuss seriously around the table, hands "
            "gesture, papers are slid across, one person makes a firm "
            "point, camera slowly pans the room"
        ),
    },
    "interview_style": {
        "starting_image_prompt": (
            "Cinematic still of a single character seated facing the "
            "camera in an interview-style framing, simple uncluttered "
            "background, soft three-point lighting, mini-drama "
            "documentary look, 16:9"
        ),
        "motion_hint": (
            "The character speaks directly to camera with natural facial "
            "expressions and modest hand gestures, slight head movement, "
            "camera holds steady on the medium close-up"
        ),
    },
}


# 23 video-intake case names → fixture id
# 9 unique strict-match fixtures + 1 generic shared by 13 cases.
VIDEO_CASE_MAPPING: dict[str, str] = {
    # Strict: content must match the user_goal's specific scene
    "extend_01": "ceo_romance_confrontation",
    "complex_25": "rainy_night",
    "complex_27": "costume_drama",
    "complex_28": "confrontation",
    "complex_29": "fight_scene",
    "extend_05": "female_lead_crying",
    "sub_vid_03": "english_drama",
    "complex_18": "english_drama",
    "complex_20": "meeting_scene",
    "sub_vid_01": "interview_style",
    # Generic: any mini-drama clip will do
    "style_01": "mini_drama_generic",
    "highlight_01": "mini_drama_generic",
    "complex_10": "mini_drama_generic",
    "complex_13": "mini_drama_generic",
    "complex_24": "mini_drama_generic",
    "complex_26": "mini_drama_generic",
    "complex_30": "mini_drama_generic",
    "complex_01": "mini_drama_generic",
    "complex_02": "mini_drama_generic",
    "complex_03": "mini_drama_generic",
    "complex_04": "mini_drama_generic",
    "complex_06": "mini_drama_generic",
    "complex_21": "mini_drama_generic",
}


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def _load_cases() -> list[dict]:
    with open(CASES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _linearize(chain: list) -> list[str]:
    out: list[str] = []
    for slot in chain:
        if isinstance(slot, list):
            if slot and slot != ["done"]:
                out.append(slot[0])
        elif slot != "done":
            out.append(slot)
    return out


def validate_coverage(cases: list[dict]) -> tuple[set[str], set[str]]:
    """Return (image_intake_names, video_intake_names) and assert mappings cover them."""
    image_names: set[str] = set()
    video_names: set[str] = set()
    for c in cases:
        chain = _linearize(c["expected_chain"])
        if not chain:
            continue
        first = chain[0]
        if first == "IntakeImageAgent":
            image_names.add(c["name"])
        elif first == "IntakeVideoAgent":
            video_names.add(c["name"])

    img_keys = set(IMAGE_FIXTURES.keys())
    vid_keys = set(VIDEO_CASE_MAPPING.keys())
    if image_names != img_keys:
        missing = image_names - img_keys
        extra = img_keys - image_names
        raise SystemExit(
            f"IMAGE_FIXTURES mismatch — missing: {sorted(missing)}, extra: {sorted(extra)}"
        )
    if video_names != vid_keys:
        missing = video_names - vid_keys
        extra = vid_keys - video_names
        raise SystemExit(
            f"VIDEO_CASE_MAPPING mismatch — missing: {sorted(missing)}, extra: {sorted(extra)}"
        )
    # Every fixture id used in mapping must exist in VIDEO_FIXTURES
    used_fixtures = set(VIDEO_CASE_MAPPING.values())
    fixture_ids = set(VIDEO_FIXTURES.keys())
    if not used_fixtures.issubset(fixture_ids):
        raise SystemExit(
            f"VIDEO_FIXTURES missing entries used by mapping: "
            f"{sorted(used_fixtures - fixture_ids)}"
        )
    if fixture_ids - used_fixtures:
        raise SystemExit(
            f"VIDEO_FIXTURES has unused entries: {sorted(fixture_ids - used_fixtures)}"
        )

    return image_names, video_names


# ---------------------------------------------------------------------------
# Dry-run rendering
# ---------------------------------------------------------------------------


def render_dry_run(image_names: set[str], video_names: set[str]) -> None:
    print("=" * 80)
    print(f"DRY RUN — no API calls. Pass --execute to actually generate.")
    print("=" * 80)
    print()

    print(f"## Image fixtures ({len(IMAGE_FIXTURES)} files)")
    print(f"## Output: {IMAGES_DIR.relative_to(REPO_ROOT)}/<case_name>.png")
    print()
    for name in sorted(IMAGE_FIXTURES):
        print(f"  [{name}]")
        print(f"    prompt: {IMAGE_FIXTURES[name]}")
        print()

    print(f"## Video fixtures ({len(VIDEO_FIXTURES)} files, "
          f"covering {len(VIDEO_CASE_MAPPING)} video-intake cases)")
    print(f"## Output: {VIDEOS_DIR.relative_to(REPO_ROOT)}/<fixture_id>.mp4")
    print()
    # Print fixtures and which cases bind to each
    cases_per_fixture: dict[str, list[str]] = {}
    for case_name, fixture_id in VIDEO_CASE_MAPPING.items():
        cases_per_fixture.setdefault(fixture_id, []).append(case_name)
    for fixture_id in VIDEO_FIXTURES:
        spec = VIDEO_FIXTURES[fixture_id]
        bound = sorted(cases_per_fixture.get(fixture_id, []))
        print(f"  [{fixture_id}.mp4] — used by {len(bound)} case(s): {bound}")
        print(f"    starting_image_prompt: {spec['starting_image_prompt']}")
        print(f"    motion_hint:           {spec['motion_hint']}")
        print()

    print("## Cost / time estimates (--execute mode)")
    n_imgs = len(IMAGE_FIXTURES) + len(VIDEO_FIXTURES)  # image fixtures + starting frames
    n_vids = len(VIDEO_FIXTURES)
    print(f"  Images (8 fixtures + 10 starting frames): {n_imgs} × ~$0.005 ≈ ${n_imgs * 0.005:.2f}")
    print(f"  Videos (Kling i2v 5s):                    {n_vids} × ~$0.5  ≈ ${n_vids * 0.5:.2f}")
    print(f"  Time:                                     ~5–15 minutes")
    print()
    print(f"  Total cases covered: {len(image_names)} image + {len(video_names)} video"
          f" = {len(image_names)+len(video_names)}/43")
    print()
    print("Run with --execute to actually generate.")


# ---------------------------------------------------------------------------
# Real generation
# ---------------------------------------------------------------------------


async def _generate_one_image(image_service, prompt: str) -> bytes:
    res = await image_service.generate_image(prompt=prompt)
    return res.bytes


async def _generate_one_video(
    video_service, *, fixture_id: str, starting_image_bytes: bytes, motion_hint: str
) -> bytes:
    res = await video_service.generate_clip(
        shot_id=fixture_id,
        keyframe_images=[starting_image_bytes],
        prompt=motion_hint,
        duration_sec=5.0,
    )
    return res.bytes


async def _generate_image_fixture(
    image_service, case_name: str, prompt: str
) -> tuple[str, dict, Optional[Exception]]:
    """One image fixture task — generate, write to disk, return audit dict."""
    t0 = time.time()
    print(f"  [image:{case_name}] starting", flush=True)
    try:
        img_bytes = await _generate_one_image(image_service, prompt)
    except Exception as exc:
        print(f"  [image:{case_name}] FAILED: {type(exc).__name__}: {exc}", flush=True)
        return case_name, {}, exc
    out_path = IMAGES_DIR / f"{case_name}.png"
    out_path.write_bytes(img_bytes)
    elapsed = round(time.time() - t0, 2)
    audit = {
        "prompt": prompt,
        "path": str(out_path.relative_to(REPO_ROOT)),
        "bytes": len(img_bytes),
        "elapsed_s": elapsed,
    }
    print(
        f"  [image:{case_name}] OK ({len(img_bytes)} bytes, {elapsed}s) "
        f"→ {out_path.relative_to(SCRIPT_DIR)}",
        flush=True,
    )
    return case_name, audit, None


async def _generate_video_fixture(
    image_service, video_service, fixture_id: str, spec: dict
) -> tuple[str, dict, Optional[Exception]]:
    """One video fixture task — starting frame + i2v in sequence (within
    a fixture), but multiple fixtures run concurrently."""
    t0 = time.time()
    print(f"  [video:{fixture_id}] step 1/2: starting frame", flush=True)
    try:
        start_bytes = await _generate_one_image(
            image_service, spec["starting_image_prompt"]
        )
    except Exception as exc:
        print(
            f"  [video:{fixture_id}] starting-frame FAILED: "
            f"{type(exc).__name__}: {exc}",
            flush=True,
        )
        return fixture_id, {}, exc
    print(f"  [video:{fixture_id}] step 2/2: i2v 5s", flush=True)
    try:
        vid_bytes = await _generate_one_video(
            video_service,
            fixture_id=fixture_id,
            starting_image_bytes=start_bytes,
            motion_hint=spec["motion_hint"],
        )
    except Exception as exc:
        print(
            f"  [video:{fixture_id}] i2v FAILED: "
            f"{type(exc).__name__}: {exc}",
            flush=True,
        )
        return fixture_id, {}, exc
    out_path = VIDEOS_DIR / f"{fixture_id}.mp4"
    out_path.write_bytes(vid_bytes)
    elapsed = round(time.time() - t0, 2)
    audit = {
        "starting_image_prompt": spec["starting_image_prompt"],
        "motion_hint": spec["motion_hint"],
        "path": str(out_path.relative_to(REPO_ROOT)),
        "bytes": len(vid_bytes),
        "elapsed_s": elapsed,
    }
    print(
        f"  [video:{fixture_id}] OK ({len(vid_bytes)} bytes, {elapsed}s) "
        f"→ {out_path.relative_to(SCRIPT_DIR)}",
        flush=True,
    )
    return fixture_id, audit, None


async def execute(only_images: bool, only_videos: bool) -> int:
    # Lazy imports — only after env is loaded (load .env below) and after
    # we know we're really going to call APIs.
    from inference.config.config_loader import ConfigLoader
    for fname in (".env", ".env.example"):
        p = REPO_ROOT / fname
        if p.is_file():
            ConfigLoader.load_env_file(str(p), override=False)
    # Force real backends regardless of caller env.
    os.environ["FW_USE_REAL_MEDIA_GEN"] = "1"

    from inference.generation import select_image_service, select_video_service

    image_service = select_image_service()
    video_service = select_video_service() if not only_images else None

    print(f"Image backend: {type(image_service).__name__} (model={getattr(image_service, 'model', '?')})")
    if video_service is not None:
        print(f"Video backend: {type(video_service).__name__} (model={getattr(video_service, 'model', '?')})")
    print()

    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    VIDEOS_DIR.mkdir(parents=True, exist_ok=True)

    audit: dict = {
        "image_fixtures": {},
        "video_fixtures": {},
        "video_case_mapping": VIDEO_CASE_MAPPING,
    }

    # All tasks go into a single asyncio.gather so image fixtures + video
    # fixtures run concurrently. Each video task internally chains
    # starting-frame → i2v sequentially (Kling i2v needs the frame), but
    # different video fixtures don't wait on each other.
    tasks: list[asyncio.Task] = []
    image_task_meta: list[str] = []  # case_name per image task, by index
    video_task_meta: list[str] = []  # fixture_id per video task, by index

    if not only_videos:
        print(f"## Launching {len(IMAGE_FIXTURES)} image fixture tasks (parallel)")
        for case_name, prompt in IMAGE_FIXTURES.items():
            tasks.append(
                asyncio.create_task(
                    _generate_image_fixture(image_service, case_name, prompt)
                )
            )
            image_task_meta.append(case_name)

    if not only_images:
        assert video_service is not None
        print(f"## Launching {len(VIDEO_FIXTURES)} video fixture tasks (parallel, each internally chains image→i2v)")
        for fixture_id, spec in VIDEO_FIXTURES.items():
            tasks.append(
                asyncio.create_task(
                    _generate_video_fixture(
                        image_service, video_service, fixture_id, spec
                    )
                )
            )
            video_task_meta.append(fixture_id)
    print()

    overall_t0 = time.time()
    results = await asyncio.gather(*tasks, return_exceptions=True)
    overall_elapsed = round(time.time() - overall_t0, 2)

    n_img = len(image_task_meta)
    image_results = results[:n_img]
    video_results = results[n_img:]

    image_failed: list[str] = []
    video_failed: list[str] = []

    for r in image_results:
        if isinstance(r, BaseException):
            image_failed.append(f"<task crashed: {type(r).__name__}: {r}>")
            continue
        case_name, ad, err = r
        if err is not None:
            image_failed.append(case_name)
        else:
            audit["image_fixtures"][case_name] = ad

    for r in video_results:
        if isinstance(r, BaseException):
            video_failed.append(f"<task crashed: {type(r).__name__}: {r}>")
            continue
        fixture_id, ad, err = r
        if err is not None:
            video_failed.append(fixture_id)
        else:
            audit["video_fixtures"][fixture_id] = ad

    print()
    print(f"## Done in {overall_elapsed}s")
    print(f"  Image fixtures: {len(audit['image_fixtures'])}/{n_img} ok"
          f"{', failed: ' + str(image_failed) if image_failed else ''}")
    print(f"  Video fixtures: {len(audit['video_fixtures'])}/{len(video_task_meta)} ok"
          f"{', failed: ' + str(video_failed) if video_failed else ''}")

    METADATA_PATH.write_text(
        json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Audit log → {METADATA_PATH.relative_to(REPO_ROOT)}")
    return 0 if not (image_failed or video_failed) else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually call APIs and write fixtures (default is dry-run).",
    )
    parser.add_argument(
        "--only-images",
        action="store_true",
        help="In execute mode, only regenerate image fixtures.",
    )
    parser.add_argument(
        "--only-videos",
        action="store_true",
        help="In execute mode, only regenerate video fixtures (still generates each video's starting frame).",
    )
    args = parser.parse_args()

    cases = _load_cases()
    image_names, video_names = validate_coverage(cases)

    if not args.execute:
        render_dry_run(image_names, video_names)
        return 0

    return asyncio.run(execute(only_images=args.only_images, only_videos=args.only_videos))


if __name__ == "__main__":
    raise SystemExit(main())
