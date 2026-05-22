"""End-to-end driver: StoryAgent → KeyframeAgent → ShotPromptAgent → (video model).

Standalone — does NOT touch Director / Assistant / Workspace. The specific
video backend is owned by ``_call_video()`` in this file; sub_agents themselves
are backend-agnostic.

Run from project root (after `source ~/.bashrc && conda activate frameworkers`):

    python -m sub_agents.pipeline \\
        --user-goal "A failed kamen-rider candidate makes a final transformation
                     attempt at dawn on a wasteland; the suit rejects him violently." \\
        --reference-image /path/to/protagonist.png \\
        --output-dir _trace/sub_agents_run_001

Outputs land in <output-dir>:
  story.json                    — StoryOutput
  keyframes/anchors/*.png       — per-variant identity anchors
  keyframes/shots/*.png         — per-shot storyboard + blocking
  keyframes.json                — KeyframeOutput
  prompts/<shot_id>.{json,txt}  — assembled video-gen prompt + image_refs per shot
  (videos/*.mp4 — only if --render-video and backend wired)
"""
from __future__ import annotations

import argparse
import asyncio
import os
from pathlib import Path
from typing import Optional

from inference.clients import LLMClient

from . import DEFAULT_LLM_MODEL
from .keyframe import agent as keyframe_agent
from .shot_prompt import agent as shot_prompt_agent
from .shot_prompt.schema import ShotPromptOutput
from .story import agent as story_agent
from .tour import agent as tour_agent


async def run(
    user_goal: str,
    *,
    reference_images: Optional[list[str]] = None,
    output_dir: Path,
    stop_after: Optional[str] = None,  # "story" | "keyframe" | "shot_prompt" | None
    render_video: bool = False,
    mode: str = "story",  # "story" (narrative arc) | "tour" (vignettes, no arc)
) -> Optional[list[ShotPromptOutput]]:
    output_dir.mkdir(parents=True, exist_ok=True)
    llm = LLMClient(model=DEFAULT_LLM_MODEL)

    # 1. Story / Tour — load existing if present (preserves audit-enriched
    # descriptions across reruns), otherwise generate fresh via the agent
    # matching the requested mode.
    story_path = output_dir / "story.json"
    if story_path.exists():
        print(f"[story] reusing existing {story_path} (skip {mode} agent; preserves audit enrichments)")
        from .story.schema import StoryOutput
        story_out = StoryOutput.model_validate_json(story_path.read_text(encoding="utf-8"))
    else:
        if mode == "tour":
            print("[tour] generating observational vignette plan...")
            story_out = await tour_agent.run(
                user_goal, reference_images=reference_images, llm=llm,
            )
        elif mode == "story":
            print("[story] generating narrative plan...")
            story_out = await story_agent.run(
                user_goal, reference_images=reference_images, llm=llm,
            )
        else:
            raise ValueError(f"unknown mode={mode!r} (expected 'story' or 'tour')")
        story_path.write_text(
            story_out.model_dump_json(indent=2), encoding="utf-8",
        )
    print(
        f"[story] OK  · {len(story_out.shots)} shots · "
        f"{len(story_out.characters)} characters · {len(story_out.locations)} locations"
    )
    if stop_after == "story":
        print(f"[pipeline] stopped after story (--stop-after story)")
        return None

    # 2. Keyframes (Phase 1 anchors + Phase 2 per-shot storyboards/blocking, all parallel)
    print("[keyframe] rendering anchors + per-shot storyboards + blocking diagrams...")
    keyframes = await keyframe_agent.run(
        story_out, output_dir=output_dir / "keyframes", llm=llm,
    )
    (output_dir / "keyframes.json").write_text(
        keyframes.model_dump_json(indent=2), encoding="utf-8",
    )
    print(
        f"[keyframe] OK  · {len(keyframes.character_anchors)} char + "
        f"{len(keyframes.location_anchors)} loc anchors · "
        f"{len(keyframes.shot_visuals)} shot visual packs"
    )
    if stop_after == "keyframe":
        print(f"[pipeline] stopped after keyframe (--stop-after keyframe)")
        return None

    # 3. Shot prompts (parallel across shots)
    print(f"[shot_prompt] composing video-gen prompts for {len(story_out.shots)} shots...")
    prompts = await asyncio.gather(*[
        shot_prompt_agent.run(shot, story_out, keyframes, llm=llm)
        for shot in story_out.shots
    ])
    prompts_dir = output_dir / "prompts"
    prompts_dir.mkdir(exist_ok=True)
    for p in prompts:
        (prompts_dir / f"{p.shot_id}.txt").write_text(p.text_prompt, encoding="utf-8")
    print(f"[shot_prompt] OK  · {len(prompts)} prompts written to {prompts_dir}")
    if stop_after == "shot_prompt":
        print(f"[pipeline] stopped after shot_prompt (--stop-after shot_prompt)")
        return prompts

    # 4. Optional video render (backend not wired yet — see _call_video docstring)
    if render_video:
        print(f"[video] generating videos...")
        videos_dir = output_dir / "videos"
        videos_dir.mkdir(exist_ok=True)
        await asyncio.gather(*[_call_video(p, videos_dir) for p in prompts])
        print(f"[video] OK  · videos in {videos_dir}")

    return prompts


_VEO_MODEL = "veo-3.1-generate-preview"  # standard ($0.40/s); fast: -fast- ($0.15/s); lite has no refs/extend.
_VIDEO_BACKEND = os.environ.get("FW_SUB_AGENTS_VIDEO_BACKEND", "seedance")
# Backends: "seedance" (default — best storyboard-following per sh_003 A/B; $0.30/s 720p),
#           "happyhorse" ($0.14/s 720p; weaker beat-following, skips transitional beats),
#           "veo" (8s + 7s extend; Gemini-channel).


async def _call_video(prompt: ShotPromptOutput, out_dir: Path) -> str:
    """Dispatch to the configured video backend. ONLY this function (+ its
    backend-specific helpers) knows the backend. Switch via env var
    ``FW_SUB_AGENTS_VIDEO_BACKEND=seedance|happyhorse|veo`` (default ``seedance``).
    """
    if _VIDEO_BACKEND == "veo":
        return await _call_video_veo(prompt, out_dir)
    elif _VIDEO_BACKEND == "happyhorse":
        return await _call_video_happyhorse(prompt, out_dir)
    elif _VIDEO_BACKEND == "seedance":
        return await _call_video_seedance(prompt, out_dir)
    raise RuntimeError(f"Unknown FW_SUB_AGENTS_VIDEO_BACKEND={_VIDEO_BACKEND!r}")


async def _call_video_veo(prompt: ShotPromptOutput, out_dir: Path) -> str:
    """Google Veo 3.1 via google.genai SDK (same Gemini channel as LLM).
    8s initial w/ ref images + 7s extend = 15s. Cost: ~$6/shot standard w/ audio.
    Limitation: Veo's reference_images is for subject identity preservation,
    NOT temporal panel-sequence binding. Storyboard sheet gets treated as
    overall identity ref, not as a per-panel time map.
    """
    import time as _time
    from google import genai
    from google.genai import types

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Veo via Gemini needs GEMINI_API_KEY in .env")
    base_url = os.environ.get("GEMINI_BASE_URL")

    out_path = out_dir / f"{prompt.shot_id}.mp4"

    def _load_ref(path: str) -> "types.Image":
        # google.genai expects types.Image(image_bytes=..., mime_type=...) — passing
        # a raw PIL.Image throws 400 INVALID_ARGUMENT on missing bytesBase64Encoded.
        suffix = Path(path).suffix.lower()
        mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg"}.get(
            suffix.lstrip("."), "image/png"
        )
        return types.Image(image_bytes=Path(path).read_bytes(), mime_type=mime)

    def _sync_generate_extend_download() -> None:
        client_kwargs = {"api_key": api_key}
        if base_url:
            client_kwargs["http_options"] = types.HttpOptions(base_url=base_url)
        client = genai.Client(**client_kwargs)

        # Veo 3.1 r2v cap = 3 refs; our video_image_refs = [style, storyboard, blocking]
        refs = [
            types.VideoGenerationReferenceImage(
                image=_load_ref(p),
                reference_type="asset",
            )
            for p in prompt.video_image_refs[:3]
        ]

        # --- Step 1: initial 8s with reference_images ---
        op = client.models.generate_videos(
            model=_VEO_MODEL,
            prompt=prompt.text_prompt,
            config=types.GenerateVideosConfig(
                reference_images=refs,
                duration_seconds="8",  # required when reference_images is set
                resolution="720p",
            ),
        )
        while not op.done:
            _time.sleep(10)
            op = client.operations.get(op)
        if getattr(op, "error", None):
            raise RuntimeError(f"[{prompt.shot_id}] Veo initial op error: {op.error}")
        if not op.response or not getattr(op.response, "generated_videos", None):
            raise RuntimeError(
                f"[{prompt.shot_id}] Veo initial returned empty response "
                f"(likely safety block or gateway issue). raw op: {op!r}"
            )
        initial_video = op.response.generated_videos[0].video

        # --- Step 2: extend +7s using the initial video as seed ---
        op2 = client.models.generate_videos(
            model=_VEO_MODEL,
            video=initial_video,                 # seeds from last 24 frames
            prompt=prompt.text_prompt,            # same prompt (Veo decides continuation)
            config=types.GenerateVideosConfig(
                number_of_videos=1,
                resolution="720p",
            ),
        )
        while not op2.done:
            _time.sleep(10)
            op2 = client.operations.get(op2)
        if getattr(op2, "error", None):
            raise RuntimeError(f"[{prompt.shot_id}] Veo extend op error: {op2.error}")
        if not op2.response or not getattr(op2.response, "generated_videos", None):
            raise RuntimeError(
                f"[{prompt.shot_id}] Veo extend returned empty response. raw op: {op2!r}"
            )
        final_video = op2.response.generated_videos[0].video

        # Final mp4 is merged 15s (Veo merges internally)
        client.files.download(file=final_video)
        final_video.save(str(out_path))

    print(f"[video] {prompt.shot_id} → Veo 3.1 8s+extend=15s (~3-5 min/shot)")
    await asyncio.to_thread(_sync_generate_extend_download)
    return str(out_path)


async def _call_video_seedance(prompt: ShotPromptOutput, out_dir: Path) -> str:
    """Seedance 2.0 reference-to-video via fal.ai. Single call, up to 9 ref
    images, 4-15s duration. 720p 16:9. Cost: $0.3024/s standard tier (image
    refs) → $4.54 per 15s shot.

    Empirically (sh_003 A/B vs HappyHorse on identical input): Seedance follows
    the storyboard sheet's per-panel temporal beats more faithfully than
    HappyHorse — HappyHorse tends to skip transitional / non-iconic beats
    (e.g. beat 4 "cleaved beast" was dropped entirely by HappyHorse but
    rendered by Seedance). Pay 2.16× the per-second cost in exchange.

    Backend-specific prompt translation: ShotPromptAgent emits ``[Image N]``
    (our backend-neutral convention). Seedance natively uses ``@ImageN``
    syntax (per fal docs — each ref in image_urls is addressed as @Image1..N
    in the prompt). Regex-translated here.

    ``generate_audio=False`` — Seedance defaults to on and will hallucinate
    Chinese subtitle text on-screen if left enabled. We do TTS / audio mix
    separately in downstream pipelines, so disable here.
    """
    import re
    import httpx
    from inference.generation.fal_helpers import fal_subscribe

    api_key = os.environ.get("FAL_API_KEY")
    if not api_key:
        raise RuntimeError("Seedance needs FAL_API_KEY in .env")
    os.environ.setdefault("FAL_KEY", api_key)

    out_path = out_dir / f"{prompt.shot_id}.mp4"

    try:
        import fal_client
    except ImportError as exc:
        raise RuntimeError("Install `fal-client` (pip install fal-client)") from exc

    image_urls: list[str] = []
    for p in prompt.video_image_refs[:9]:  # Seedance cap = 9 images
        url = await asyncio.to_thread(fal_client.upload_file, str(p))
        image_urls.append(url)

    fal_prompt = re.sub(r"\[Image\s+(\d+)\]", r"@Image\1", prompt.text_prompt)

    print(f"[video] {prompt.shot_id} → Seedance 2.0 r2v 15s 720p ({len(image_urls)} refs, [Image N]→@Image{{N}}, audio OFF)")
    result = await fal_subscribe(
        api_key,
        "bytedance/seedance-2.0/reference-to-video",
        {
            "prompt": fal_prompt,
            "image_urls": image_urls,
            "resolution": "720p",
            "duration": 15,
            "aspect_ratio": "16:9",
            "generate_audio": False,
        },
    )

    video_field = result.get("video")
    video_url = (
        video_field.get("url") if isinstance(video_field, dict) else video_field
    )
    if not video_url:
        raise RuntimeError(
            f"[{prompt.shot_id}] Seedance returned unexpected payload: {result!r}"
        )

    async with httpx.AsyncClient(timeout=180.0) as http:
        resp = await http.get(video_url)
        resp.raise_for_status()
        out_path.write_bytes(resp.content)

    return str(out_path)


async def _call_video_happyhorse(prompt: ShotPromptOutput, out_dir: Path) -> str:
    """HappyHorse 1.0 r2v via fal.ai. Single call, up to 9 ref images, 3-15s.
    Cost: ~$2.10/shot 720p (15s × $0.14/s).

    Backend-specific prompt translation: ShotPromptAgent emits `[Image N]` (our
    backend-neutral convention). Fal's HappyHorse natively uses `character{N}`
    (per fal docs — each ref in image_urls is addressed as character1..9 in
    prompt). We regex-translate here so HappyHorse parses refs accurately.
    """
    import re
    import httpx
    from inference.generation.fal_helpers import fal_subscribe

    api_key = os.environ.get("FAL_API_KEY")
    if not api_key:
        raise RuntimeError("HappyHorse needs FAL_API_KEY in .env")
    os.environ.setdefault("FAL_KEY", api_key)

    out_path = out_dir / f"{prompt.shot_id}.mp4"

    # Upload local PNGs to fal storage → URLs the API can pull
    try:
        import fal_client
    except ImportError as exc:
        raise RuntimeError("Install `fal-client` (pip install fal-client)") from exc

    image_urls: list[str] = []
    for p in prompt.video_image_refs[:9]:  # HappyHorse cap = 9
        url = await asyncio.to_thread(fal_client.upload_file, str(p))
        image_urls.append(url)

    # Translate [Image N] → character{N} to match fal HappyHorse's prompt convention
    fal_prompt = re.sub(r"\[Image\s+(\d+)\]", r"character\1", prompt.text_prompt)

    print(f"[video] {prompt.shot_id} → HappyHorse r2v 15s 720p ({len(image_urls)} refs, [Image N]→character{{N}})")
    result = await fal_subscribe(
        api_key,
        "alibaba/happy-horse/reference-to-video",
        {
            "prompt": fal_prompt,
            "image_urls": image_urls,
            "resolution": "720p",
            "duration": 15,
            "aspect_ratio": "16:9",
        },
    )

    # Locate video URL in response (different fal endpoints package it differently)
    video_field = result.get("video")
    video_url = (
        video_field.get("url") if isinstance(video_field, dict) else video_field
    )
    if not video_url:
        raise RuntimeError(
            f"[{prompt.shot_id}] HappyHorse returned unexpected payload: {result!r}"
        )

    async with httpx.AsyncClient(timeout=180.0) as http:
        resp = await http.get(video_url)
        resp.raise_for_status()
        out_path.write_bytes(resp.content)

    return str(out_path)


def _main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--user-goal", required=True)
    parser.add_argument("--reference-image", action="append", default=[],
                        help="Repeatable: --reference-image a.png --reference-image b.png")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--render-video", action="store_true",
                        help="Call the video backend after prompt assembly (requires backend wired in _call_video).")
    parser.add_argument("--stop-after", choices=["story", "keyframe", "shot_prompt"], default=None,
                        help="Stop after the named stage (artifacts up to that stage are written).")
    parser.add_argument("--mode", choices=["story", "tour"], default="story",
                        help="story = narrative arc with character drama (default). "
                             "tour = observational vignettes (no narrative arc; environment / process / atmosphere).")
    args = parser.parse_args()
    asyncio.run(run(
        args.user_goal,
        reference_images=args.reference_image or None,
        output_dir=args.output_dir,
        stop_after=args.stop_after,
        render_video=args.render_video,
        mode=args.mode,
    ))


if __name__ == "__main__":
    _main()
