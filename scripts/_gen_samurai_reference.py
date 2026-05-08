"""One-shot helper: generate a lone-samurai character anchor for the
feudal-Japan revenge demo. Saves to /tmp/samurai_reference.png.

Run from repo root with the frameworkers env active. .env is loaded
manually so the FAL_* / INFERENCE_IMAGE_MODEL keys are visible.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path


_REPO = Path("/home/zhendong_li/FrameWorkers")
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from dotenv import load_dotenv  # noqa: E402

load_dotenv(_REPO / ".env")

from inference.generation import select_image_service  # noqa: E402
from inference.generation.image_generators.types import (  # noqa: E402
    ImageSemanticContext,
)


_PROMPT = (
    "A lone samurai standing under cherry blossoms in spring. "
    "Mid-30s, stoic weathered face, dark eyes, traditional dark "
    "indigo-and-black hakama with a charcoal haori, katana sheathed at "
    "the left hip, hair tied in a topknot, subtle scar across the left "
    "cheek. Calm steady gaze. Photoreal cinematic still."
)


async def main() -> int:
    out_path = Path("/tmp/samurai_reference.png")
    svc = select_image_service()
    ctx = ImageSemanticContext(
        prompt_summary=_PROMPT,
        is_identity_reference=True,
        ref_kind="character",
    )
    print(f"[gen] using image service: {type(svc).__name__}")
    result = await svc.generate_image(semantic_context=ctx)
    if not result.bytes:
        print("[gen] FATAL: empty bytes from image service")
        return 1
    out_path.write_bytes(result.bytes)
    print(f"[gen] saved {len(result.bytes)} bytes -> {out_path}")
    print(f"[gen] resolved_prompt:\n{result.resolved_prompt[:500]}...")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
