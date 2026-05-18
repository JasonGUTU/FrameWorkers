#!/usr/bin/env python3
"""Gemini image-generation smoke test (validates GeminiImageService end-to-end).

Hits the same path KeyFrameAgent's L1/L2/L3 image renders take when
``FW_USE_REAL_MEDIA_GEN=1``: ``select_image_service()`` →
``GeminiImageService.generate_image(prompt=...)`` → native-Gemini CF AI
Gateway → ``inline_data`` PNG bytes → file on disk.

Useful to probe:

  * model availability (``INFERENCE_IMAGE_MODEL`` reachable on the gateway)
  * end-to-end content-moderation behaviour for a specific prompt
    (Gemini occasionally blocks 'execution / chained / corpse' wording
    even in non-graphic contexts — see git log for the history of
    revert-from-Gemini events)
  * average latency for a single-image generate call

Costs depend on the Gateway pricing for ``INFERENCE_IMAGE_MODEL``.

Examples::

    # default fox-demon prompt aligned to current user_goal demo
    python scripts/gemini_image_smoke.py

    # custom prompt, custom output path
    python scripts/gemini_image_smoke.py \\
      --prompt "An ink-wash painting of a fox spirit on a mountain at dawn" \\
      -o Runtime/gemini_smoke_fox.png
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from inference.generation.fal_helpers import ensure_fal_runtime_env_loaded
from inference.generation.image_generators.service import GeminiImageService


_DEFAULT_PROMPT = (
    "A small nine-tailed fox demoness chained on a stone Investiture "
    "Platform under stormy nine-heaven skies; her sorrowful gaze drifts "
    "to a half-remembered figure in the clouds. Classical Chinese "
    "ink-wash painting style, muted traditional palette, cinematic "
    "composition, fine brushwork, mythic atmosphere."
)


async def _run(args: argparse.Namespace) -> int:
    ensure_fal_runtime_env_loaded()
    if not (os.getenv("GEMINI_API_KEY") or "").strip():
        print("ERROR: GEMINI_API_KEY not set in env or .env.", file=sys.stderr)
        return 2
    model = (args.model or os.getenv("INFERENCE_IMAGE_MODEL") or "").strip()
    if not model:
        print("ERROR: INFERENCE_IMAGE_MODEL not set in env or .env.", file=sys.stderr)
        return 2

    out_path = args.output
    if out_path is None:
        runtime = _REPO_ROOT / "Runtime"
        runtime.mkdir(parents=True, exist_ok=True)
        out_path = runtime / (
            f"gemini_image_smoke_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        )

    print("INFERENCE_IMAGE_MODEL:", model)
    print("GEMINI_BASE_URL:", os.getenv("GEMINI_BASE_URL", "(unset)"))
    print(
        "prompt:",
        args.prompt if len(args.prompt) <= 200 else args.prompt[:197] + "...",
    )

    svc = GeminiImageService(model=model)
    try:
        result = await svc.generate_image(prompt=args.prompt)
        png = result.bytes
    except Exception as exc:
        print("ERROR:", type(exc).__name__, exc, file=sys.stderr)
        return 3

    if not png or len(png) < 64:
        print("ERROR: payload too small.", file=sys.stderr)
        return 4

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(png)
    head = png[:8]
    print("OK: wrote", out_path, "size_bytes=", len(png))
    print("png head:", head)
    if head[:8] == b"\x89PNG\r\n\x1a\n":
        print("png container: valid (magic bytes match)")
    else:
        print("WARN: head does not match PNG magic — content may not be PNG.")
    return 0


def main() -> None:
    p = argparse.ArgumentParser(
        description=(
            "Gemini image-generation smoke (requires INFERENCE_IMAGE_MODEL + "
            "GEMINI_API_KEY in .env)."
        )
    )
    p.add_argument(
        "--prompt", default=_DEFAULT_PROMPT,
        help="Image prompt (defaults to a fox-demon mythology scene).",
    )
    p.add_argument(
        "--model", default=None,
        help="Override INFERENCE_IMAGE_MODEL just for this run.",
    )
    p.add_argument(
        "-o", "--output", type=Path, default=None,
        help="Output PNG path (default: Runtime/gemini_image_smoke_<ts>.png — gitignored).",
    )
    args = p.parse_args()
    raise SystemExit(asyncio.run(_run(args)))


if __name__ == "__main__":
    main()
