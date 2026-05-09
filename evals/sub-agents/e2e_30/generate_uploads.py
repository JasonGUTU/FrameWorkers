#!/usr/bin/env python3
"""Generate 14 mock upload portraits via GeminiImageService (gemini-3.1-flash-image-preview).

Output: <case_name>.png in evals/sub-agents/e2e_30/uploads/.

Cases needing portraits = those whose GT chain includes IntakeImageAgent:
  - intake_img: all 10 (rewritten as 中文短剧人设 — portraits are East Asian
    drama characters matched to each new short-drama role)
  - storytelling: 4 (storytelling_004 / 065 / 079 / 104 — portraits use the
    original v4500 description since storytelling user_goal kept the same topic)

Parallelism: 14-way asyncio.gather; gemini-3.1-flash-image-preview ~25s/frame
single-frame, parallel calls amortize that down to ~30-40s wall time.
"""
from __future__ import annotations
import asyncio
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

# Load .env (GEMINI_API_KEY / GEMINI_BASE_URL / INFERENCE_IMAGE_MODEL)
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv(REPO_ROOT / ".env")
except ImportError:
    # Fallback: manual parse of KEY=VAL lines
    import os
    env_path = REPO_ROOT / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())

from inference.generation.image_generators.service import GeminiImageService  # noqa: E402

# 14 prompts keyed by case_name
PROMPTS: dict[str, str] = {
    # === intake_img (10) — East Asian short-drama character portraits ===
    "intake_img_019": (
        "Portrait of a young East Asian woman in her early 20s wearing intricate "
        "Tang/Ming-style imperial palace robes, ornate gold-plated headpiece with "
        "pearls, calm and steely gaze with hints of vengeance, soft natural "
        "lighting, photorealistic, head-and-shoulders shot, neutral palace-corridor "
        "background."
    ),
    "intake_img_018": (
        "Portrait of a handsome East Asian man in his early 30s, sharp jawline, "
        "cold expressive eyes, wearing a tailored black wool suit with silver tie, "
        "slight 5 o'clock shadow, dim modern penthouse lighting in background, "
        "photorealistic, head-and-shoulders shot."
    ),
    "intake_img_005": (
        "Portrait of a young East Asian man in his late teens, slender frame, "
        "simple wuxia-style white-and-blue training robes with frayed edges, calm "
        "but unreadable amber eyes, jet-black long hair in a half-up topknot, "
        "cherry-blossom branch out of focus in background, photorealistic xianxia "
        "drama still."
    ),
    "intake_img_008": (
        "Portrait of a determined East Asian woman in her mid 20s, short tactical "
        "hair, light scratches on her cheek, worn dark-grey leather jacket over a "
        "tank top, faint metallic glow on her right hand, post-apocalyptic ruined "
        "city blurred behind her, photorealistic cinematic still."
    ),
    "intake_img_046": (
        "Portrait of a regal East Asian woman in her late 20s, elaborate "
        "Qing-dynasty palace headdress with kingfisher feathers and pearls, "
        "embroidered silk imperial robe in deep red and gold, composed expression "
        "with sharp intelligent eyes, soft palace-window lighting, photorealistic."
    ),
    "intake_img_039": (
        "Portrait of a 17-year-old East Asian high-school girl in a "
        "navy-and-white private-school uniform, neat ponytail, calm intelligent "
        "eyes with a hint of mischief, soft natural daylight in a school corridor, "
        "photorealistic still from a contemporary Chinese campus drama."
    ),
    "intake_img_036": (
        "Portrait of a successful East Asian man in his mid 30s, immaculately "
        "groomed, wearing a charcoal-grey three-piece bespoke suit with a "
        "steel-blue silk tie, intense brooding gaze, modern glass-walled CEO "
        "office at dusk in soft focus behind him, photorealistic cinematic."
    ),
    "intake_img_037": (
        "Portrait of a striking East Asian woman in her late 20s, ink-black hair "
        "flowing past her shoulders, dramatic blood-red robes with silver "
        "embroidery and a high collar, glowing red sigil faintly visible on her "
        "forehead, cold dignified expression, dark moody lighting, xianxia/wuxia "
        "photoreal style."
    ),
    "intake_img_030": (
        "Portrait of a serious East Asian man in his early 30s, short messy hair, "
        "slight stubble, wearing a dark-grey waterproof jacket over a black "
        "turtleneck, sharp tired eyes, faint scar on his eyebrow, rainy-night "
        "Shanghai precinct background out of focus, photorealistic cinematic noir "
        "lighting."
    ),
    "intake_img_049": (
        "Portrait of a delicate East Asian woman in her mid 20s, soft long hair "
        "half-tied with a pearl pin, fragile beautiful features with a sad "
        "faraway gaze, wearing an off-white cashmere coat with a single pearl "
        "earring, blurred winter window light behind her, photorealistic cinematic."
    ),
    # === storytelling (4) — children's-book style, matches v4500 original ===
    "storytelling_004": (
        "A children's-book pencil sketch of a barn cat with white-and-tabby fur, "
        "slightly chubby, alert green eyes, sitting on hay, sketchy crosshatch "
        "shading, white paper background, scanned-paper texture."
    ),
    "storytelling_104": (
        "Soft watercolor illustration of an elderly Inuit grandmother in a "
        "fur-trimmed parka braiding her young grandchild's hair, sitting inside a "
        "snow-house lit by a small oil lamp, warm pastel palette, gentle "
        "children's-storybook style, cream background."
    ),
    "storytelling_065": (
        "Pencil-and-watercolor sketch of a young Greek shepherd boy in a worn "
        "linen tunic standing among three goats on a dry sunlit hillside, distant "
        "Mount Parnassus and olive trees, soft Mediterranean palette, simple "
        "children's-book illustration style."
    ),
    "storytelling_079": (
        "Watercolor portrait of a middle-aged Bengali boatman in a white kurta, "
        "weathered face, calmly steering a wooden country boat through narrow "
        "Sundarbans mangrove channels at golden hour, mangrove roots and water "
        "reflections visible, painterly storybook style."
    ),
}


async def gen_one(svc: GeminiImageService, name: str, prompt: str, out_dir: Path):
    out_path = out_dir / f"{name}.png"
    t0 = time.time()
    try:
        result = await svc.generate_image(prompt)
        out_path.write_bytes(result.bytes)
        return name, "ok", len(result.bytes), time.time() - t0
    except Exception as e:
        return name, f"err: {type(e).__name__}: {e}", 0, time.time() - t0


async def main() -> None:
    here = Path(__file__).parent.resolve()
    out_dir = here / "uploads"
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"out_dir: {out_dir}")
    print(f"prompts: {len(PROMPTS)} cases")

    svc = GeminiImageService()
    print(f"model: {svc.model}")
    t0 = time.time()
    results = await asyncio.gather(*(
        gen_one(svc, name, prompt, out_dir) for name, prompt in PROMPTS.items()
    ))
    elapsed = time.time() - t0

    ok = sum(1 for _, status, _, _ in results if status == "ok")
    fail = len(results) - ok
    print(f"\n=== done in {elapsed:.1f}s — ok={ok} fail={fail} ===")
    for name, status, size, dt in sorted(results, key=lambda r: r[0]):
        print(f"  {name:20} {status:50} {size:>8} bytes  {dt:.1f}s")


if __name__ == "__main__":
    asyncio.run(main())
