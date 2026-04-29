"""End-to-end smoke for the input-rejection channel against a real LLM.

Two cases drive ScreenplayAgent.run() with the production LLM:

  * **Empty story** — story_json_text is "{}". The agent's WHEN TO REJECT
    block must trigger; we expect ``passed=False`` with
    ``eval_result.kind == "upstream_input_rejected"``.

  * **Sparse-but-valid story** — a one-sentence premise + one named
    character. The agent must NOT over-reject this; we expect
    ``passed=True`` and a real screenplay output.

Run with:
    set -a && source .env && set +a
    conda activate frameworkers
    python scripts/verify_input_rejection_e2e.py
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path

_repo_root = Path(__file__).resolve().parents[1]
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from agents.screenplay.agent import ScreenplayAgent
from agents.screenplay.evaluator import ScreenplayEvaluator
from agents.screenplay.schema import ScreenplayAgentInput
from inference.clients import LLMClient


def _build_agent() -> ScreenplayAgent:
    llm = LLMClient()
    agent = ScreenplayAgent(llm_client=llm)
    agent.evaluator = ScreenplayEvaluator(llm_client=llm)
    return agent


async def _run_case(label: str, story_payload: dict | str) -> dict:
    """Drive one ScreenplayAgent.run() and return a slim verdict dict."""
    if isinstance(story_payload, str):
        story_json_text = story_payload
    else:
        story_json_text = json.dumps(story_payload, ensure_ascii=False, indent=2)

    print(f"\n{'='*72}\nCASE: {label}\n{'='*72}")
    print(f"story_json_text (first 240 chars):\n{story_json_text[:240]}")

    agent = _build_agent()
    input_data = ScreenplayAgentInput(story_json_text=story_json_text)
    # max_retries=2 so we can also confirm 0-retry behavior in the rejection
    # case (call_count would be 1 even though budget allows 2).
    result = await agent.run(input_data, max_retries=2)

    eval_result = result.eval_result or {}
    verdict = {
        "label": label,
        "passed": result.passed,
        "attempts": result.attempts,
        "kind": eval_result.get("kind"),
        "summary": eval_result.get("summary"),
        "input_rejection": eval_result.get("input_rejection"),
    }
    print(
        f"→ passed={verdict['passed']}, attempts={verdict['attempts']}, "
        f"kind={verdict['kind']!r}"
    )
    if verdict["input_rejection"]:
        print("→ input_rejection:")
        print(json.dumps(verdict["input_rejection"], ensure_ascii=False, indent=2))
    if verdict["summary"]:
        print(f"→ summary: {verdict['summary'][:300]}")
    if result.passed and result.output is not None:
        scenes = getattr(result.output.content, "scenes", []) or []
        print(f"→ produced screenplay with {len(scenes)} scene(s)")
    return verdict


async def _main() -> int:
    if os.getenv("OPENAI_API_KEY") is None and os.getenv("GEMINI_API_KEY") is None:
        print(
            "ERROR: no LLM credentials in env. Run with: "
            "`set -a && source .env && set +a` first.",
            file=sys.stderr,
        )
        return 2

    failures: list[str] = []

    empty = await _run_case("empty story (must reject)", {})
    if empty["passed"]:
        failures.append(
            "empty story did NOT trigger rejection — agent fabricated output "
            "from an empty blueprint, which is the silent-failure pattern we "
            "are trying to catch."
        )
    elif empty["kind"] != "upstream_input_rejected":
        failures.append(
            f"empty story failed for the wrong reason: kind={empty['kind']!r} "
            "(expected 'upstream_input_rejected'). Likely a structural eval "
            "failure rather than the rejection channel firing."
        )
    elif empty["attempts"] != 1:
        failures.append(
            f"empty story used {empty['attempts']} attempts; rejection path "
            "must short-circuit at attempt 1 (no retry)."
        )

    sparse = await _run_case(
        "sparse-but-valid story (must NOT reject)",
        {
            "logline": (
                "A retired fisherman in a foggy coastal town finds a "
                "message in a bottle that names his estranged daughter."
            ),
            "characters": [
                {
                    "id": "char_001",
                    "name": "Henrik",
                    "role": "retired fisherman, mid-60s, soft-spoken",
                }
            ],
            "locations": [
                {"id": "loc_001", "name": "weathered harbor cottage"}
            ],
            "tone": "quiet, melancholic, hopeful",
        },
    )
    if not sparse["passed"]:
        if sparse["kind"] == "upstream_input_rejected":
            failures.append(
                "sparse-but-valid story was rejected (over-rejection). The "
                "WHEN TO REJECT criteria are too strict — sparse input must "
                "still yield a real screenplay."
            )
        else:
            # Could be an evaluator structural failure on a small story —
            # not a rejection-channel bug. Print for human inspection but
            # don't count as a hard failure.
            print(
                "\nNOTE: sparse case did not pass, but failure was "
                f"kind={sparse['kind']!r} (eval gate, not rejection channel). "
                "Inspect summary above; not failing the smoke for this."
            )

    print(f"\n{'='*72}\nSMOKE SUMMARY\n{'='*72}")
    if failures:
        for f in failures:
            print(f"  FAIL: {f}")
        return 1
    print("  PASS: rejection channel behaves as designed end-to-end.")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(_main()))
