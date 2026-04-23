"""Generate ~1100 SFT training samples via LLM teacher.

Uses project-native `inference.clients.LLMClient` (Cloudflare AI Gateway)
to call a strong teacher (Claude Sonnet / GPT-5 / Gemini Pro) for:
  - Generating diverse user_goal variants for each unique chain in
    VARIANTS_BUDGET
  - Writing high-quality CoT rationale + per-step intents for each
    (goal, chain)

Output:
    training/director/samples_sft_full.jsonl   (~1100 samples)

Next stage (optional): GRPO (see train_grpo.py). DPO stage was retired —
GRPO optimizes the programmatic chain-match reward directly, so we no
longer need programmatic bias-injected preference pairs.

Usage:
    PYTHONPATH=. python training/director/gen_training_full.py --dry-run   # ~50 samples
    PYTHONPATH=. python training/director/gen_training_full.py             # full
"""

from __future__ import annotations

import argparse
import asyncio
import json
import random
import sys
from collections import Counter
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

TEACHER_MODEL = "anthropic/claude-sonnet-4"  # change as needed; also supports gpt-5, gemini-2.5-pro

# Variants-per-chain budget. Sums to ~1100 for SFT.
#
# SubtitleAgent was retired in 2026-04 — subtitle flows now route
# TranscriptionAgent directly into Compositor (which renders segments
# → SRT via a pure-Python helper), and bilingual flows route
# TranscriptionAgent → TranslationAgent → Compositor. Illustrated-
# storytelling chain (NarrationAgent → IllustrationAgent → NarratorAgent
# → Compositor) is the newest deliverable class, with optional hybrids
# that couple in MusicAgent / AmbienceAgent / AudioMixAgent /
# TranslationAgent / IntakeImageAgent + BriefEnricherAgent.
VARIANTS_BUDGET = {
    # ── Cinematic / creative film (chain a) ───────────────────────────
    # Creative full chain (highest freq in real use)
    ("StoryAgent", "ScreenplayAgent", "KeyFrameAgent", "VideoAgent",
     "MusicAgent", "AmbienceAgent", "AudioMixAgent", "CompositorAgent"): 100,
    # Creative + subtitle (TranscriptionAgent on the Kling-baked audio)
    ("StoryAgent", "ScreenplayAgent", "KeyFrameAgent", "VideoAgent",
     "MusicAgent", "AmbienceAgent", "AudioMixAgent", "TranscriptionAgent", "CompositorAgent"): 80,
    # Creative + bilingual
    ("StoryAgent", "ScreenplayAgent", "KeyFrameAgent", "VideoAgent",
     "MusicAgent", "AmbienceAgent", "AudioMixAgent", "TranscriptionAgent", "TranslationAgent",
     "CompositorAgent"): 60,
    # Image-based creative
    ("IntakeImageAgent", "BriefEnricherAgent", "StoryAgent", "ScreenplayAgent",
     "KeyFrameAgent", "VideoAgent", "MusicAgent", "AmbienceAgent", "AudioMixAgent", "CompositorAgent"): 60,

    # ── Existing-video edit (chain b) ─────────────────────────────────
    # BGM on uploaded video
    ("IntakeVideoAgent", "MusicAgent", "AudioMixAgent", "CompositorAgent"): 80,
    # BGM + ambience on uploaded video
    ("IntakeVideoAgent", "MusicAgent", "AmbienceAgent", "AudioMixAgent",
     "CompositorAgent"): 50,
    # Style transfer only
    ("IntakeVideoAgent", "StyleTransferAgent"): 60,
    # Style + subtitle (Transcription direct)
    ("IntakeVideoAgent", "StyleTransferAgent", "TranscriptionAgent",
     "CompositorAgent"): 50,
    # Style + music
    ("IntakeVideoAgent", "StyleTransferAgent", "MusicAgent", "CompositorAgent"): 40,
    # Video extend only
    ("IntakeVideoAgent", "VideoExtendAgent"): 60,
    # Extend + music
    ("IntakeVideoAgent", "VideoExtendAgent", "MusicAgent", "AudioMixAgent",
     "CompositorAgent"): 40,
    # Extend + subtitle
    ("IntakeVideoAgent", "VideoExtendAgent", "TranscriptionAgent",
     "CompositorAgent"): 40,
    # Highlight only
    ("IntakeVideoAgent", "VideoAnalysisAgent", "HighlightAgent"): 60,
    # Highlight + subtitle
    ("IntakeVideoAgent", "VideoAnalysisAgent", "HighlightAgent",
     "TranscriptionAgent", "CompositorAgent"): 40,
    # Highlight + music
    ("IntakeVideoAgent", "VideoAnalysisAgent", "HighlightAgent", "MusicAgent",
     "CompositorAgent"): 30,
    # Transcribe + translate (bilingual subtitle on uploaded video)
    ("IntakeVideoAgent", "TranscriptionAgent", "TranslationAgent",
     "CompositorAgent"): 40,
    # Subtitle for uploaded video (monolingual)
    ("IntakeVideoAgent", "TranscriptionAgent", "CompositorAgent"): 50,
    # Extend + style
    ("IntakeVideoAgent", "VideoExtendAgent", "StyleTransferAgent"): 30,
    # Style + extend + music
    ("IntakeVideoAgent", "StyleTransferAgent", "VideoExtendAgent",
     "MusicAgent", "CompositorAgent"): 30,
    # Analyze + creative + subtitle (long)
    ("IntakeVideoAgent", "VideoAnalysisAgent", "StoryAgent", "ScreenplayAgent",
     "KeyFrameAgent", "VideoAgent", "MusicAgent", "AmbienceAgent", "AudioMixAgent",
     "TranscriptionAgent", "CompositorAgent"): 30,

    # ── Illustrated storytelling (chain c) — newest deliverable class ─
    # Single-modifier variants + pair combos of the 4 modifier dims
    # (Music / Ambience / Translation / IntakeImage+BriefEnricher) —
    # 6 pair combos total, 5 added below plus the existing triple-
    # modifier "full" variant. Pure + single-modifier dominate the
    # budget because they are the most frequent request shape in the
    # wild; the pair/triple variants seed cross-modifier routing.
    #
    # Pure
    ("NarrationAgent", "IllustrationAgent", "NarratorAgent", "CompositorAgent"): 60,
    # + Translation (bilingual SRT)
    ("NarrationAgent", "IllustrationAgent", "NarratorAgent",
     "TranslationAgent", "CompositorAgent"): 25,
    # + Music (BGM under narrator)
    ("NarrationAgent", "IllustrationAgent", "NarratorAgent", "MusicAgent",
     "AudioMixAgent", "CompositorAgent"): 25,
    # + Ambience (ambient bed)
    ("NarrationAgent", "IllustrationAgent", "NarratorAgent", "AmbienceAgent",
     "AudioMixAgent", "CompositorAgent"): 20,
    # + IntakeImage + BriefEnricher (character / setting reference)
    ("IntakeImageAgent", "BriefEnricherAgent", "NarrationAgent",
     "IllustrationAgent", "NarratorAgent", "CompositorAgent"): 20,
    # + Music + Ambience (dual audio underlay)
    ("NarrationAgent", "IllustrationAgent", "NarratorAgent",
     "MusicAgent", "AmbienceAgent", "AudioMixAgent", "CompositorAgent"): 20,
    # + Music + Translation (BGM + bilingual — common international audiobook)
    ("NarrationAgent", "IllustrationAgent", "NarratorAgent",
     "MusicAgent", "AudioMixAgent", "TranslationAgent", "CompositorAgent"): 15,
    # + Ambience + Translation (ambient bed + bilingual)
    ("NarrationAgent", "IllustrationAgent", "NarratorAgent",
     "AmbienceAgent", "AudioMixAgent", "TranslationAgent", "CompositorAgent"): 10,
    # + imgref + Music (character ref + BGM, no bilingual)
    ("IntakeImageAgent", "BriefEnricherAgent", "NarrationAgent",
     "IllustrationAgent", "NarratorAgent", "MusicAgent", "AudioMixAgent",
     "CompositorAgent"): 15,
    # + imgref + Translation (character ref + bilingual, no audio overlay)
    ("IntakeImageAgent", "BriefEnricherAgent", "NarrationAgent",
     "IllustrationAgent", "NarratorAgent", "TranslationAgent", "CompositorAgent"): 15,
    # + imgref + Music + Translation (triple-modifier; was original "full_01")
    ("IntakeImageAgent", "BriefEnricherAgent", "NarrationAgent",
     "IllustrationAgent", "NarratorAgent", "MusicAgent", "AudioMixAgent",
     "TranslationAgent", "CompositorAgent"): 15,
    # + imgref + Music + Ambience + Translation (all 4 modifiers — truly full)
    ("IntakeImageAgent", "BriefEnricherAgent", "NarrationAgent",
     "IllustrationAgent", "NarratorAgent", "MusicAgent", "AmbienceAgent",
     "AudioMixAgent", "TranslationAgent", "CompositorAgent"): 10,
}  # Total: 1280 — storytelling expanded 6→12 shapes / 165→250 samples


# ---------------------------------------------------------------------------
# Teacher prompts
# ---------------------------------------------------------------------------

GOAL_GEN_SYSTEM = """\
你是为 AI 助手的路由规划器合成训练数据的助手。根据给定的 agent chain，
写出 N 条不同的用户目标语句（user_goal），这些 goal 应该都**自然地路由到这条 chain**。

要求：
- 题材多样：修仙 / 都市 / 古装 / 科幻 / 武侠 / 霸总 / 悬疑 / 校园 / 职场 等尽量覆盖
- 语种混合：中文为主，每 5 条里 1 条英文
- 长度差异：30-80 字的短表达 + 偶尔 120+ 字的详细描述
- 表达风格差异：正式 / 口语 / 带具体数字 / 带情绪词
- 禁止：完全相同的句式，抄 eval 数据里的 goal
- 一条一行，JSON 数组格式输出
"""


RATIONALE_GEN_SYSTEM = """\
你是为 AI 路由器合成训练样本的助手。给定 user_goal 和 expected chain（agent_id 列表，
顺序固定），同时产出：
  (a) 一段 chain-of-thought rationale，解释为什么包含/不包含每个 agent
  (b) 与 chain 一一对应的 intents 列表（长度必须等于 chain 长度，顺序必须与 chain 完全一致）

rationale 约束：
- 必须显式**解释**为什么链里的每个 agent 都在：e.g. "IntakeVideo 因为用户上传了视频"
- 必须显式**说明**为什么某些 agent 不在：e.g. "不加 VideoAnalysis 因为用户没要求分析"
- 特别 flag 4 种常见 bias 并显式拒绝它们（在适用情况下）：
  1. "不先跑 VideoAnalysis 因为用户没要求分析/剪辑"
  2. "只 Music 不加 Ambience 因为用户没提环境音"
  3. "不加 Compositor 因为输出是 VideoExtend/Highlight 的原始片段，不需合成"
  4. "开头必加 IntakeText 因为框架要求文本指令先落文"
- rationale 长度目标 80-150 字（token 200 左右）

intents 约束：
- 每个 agent 一句话，描述**它在这个 user_goal 下要做什么**（不是模板，要带上 user_goal 的具体内容）
- 例：goal "给古装短剧加凄美二胡 BGM"，对应的 MusicAgent intent 应是
  "Compose a melancholic erhu BGM for the costume drama clip"，而不是 "step for MusicAgent"
- 长度 8-25 个英文词或等价中文长度
- 中英文按 user_goal 的语种决定（user_goal 中文 → intent 也用中文；英文 → 英文）
- 列表长度严格等于 chain 长度，顺序严格匹配 chain

输出 JSON 格式（不要包 markdown 代码块）：
{
  "rationale": "...",
  "intents": ["...", "...", ...]
}
"""


# ---------------------------------------------------------------------------
# Teacher-model helper
# ---------------------------------------------------------------------------

async def llm_json(system: str, user: str, model: str = TEACHER_MODEL) -> Any:
    """Call the teacher via LLMClient.chat_json."""
    from inference.clients import LLMClient
    client = LLMClient()
    return await client.chat_json(
        system_prompt=system,
        user_prompt=user,
        model=model,
    )


# ---------------------------------------------------------------------------
# SFT generation
# ---------------------------------------------------------------------------

async def gen_goals_for_chain(chain_ids: tuple, n: int) -> list[str]:
    user = json.dumps({"chain": list(chain_ids), "n": n}, ensure_ascii=False)
    data = await llm_json(GOAL_GEN_SYSTEM + "\n\n返回 JSON: {\"goals\": [\"...\", \"...\"]}", user)
    goals = data.get("goals") or []
    return [g.strip() for g in goals if isinstance(g, str) and g.strip()]


async def gen_assistant_response(user_goal: str, chain_ids: list[str]) -> dict:
    """Single teacher call returns {rationale, plan} where plan is
    [{agent_id, intent}, ...] with agent_id order locked to chain_ids and
    intent populated from teacher (NOT a placeholder)."""
    user = json.dumps({"user_goal": user_goal, "chain": chain_ids}, ensure_ascii=False)
    data = await llm_json(RATIONALE_GEN_SYSTEM, user)
    rationale = (data.get("rationale") or "").strip()
    intents = data.get("intents") or []
    if not isinstance(intents, list) or len(intents) != len(chain_ids):
        raise ValueError(
            f"intent count mismatch: got {len(intents) if isinstance(intents, list) else 'non-list'}, "
            f"expected {len(chain_ids)} for chain {chain_ids}"
        )
    plan = [{"agent_id": a, "intent": str(i).strip()} for a, i in zip(chain_ids, intents)]
    return {"rationale": rationale, "plan": plan}




# ---------------------------------------------------------------------------
# Main driver
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Concurrency-bounded helpers — wrap teacher calls so we can fire many in
# parallel without blowing past the rate limit.
# ---------------------------------------------------------------------------

async def _gather_with_limit(coros: list, limit: int = 20) -> list:
    """asyncio.gather but capped at `limit` concurrent in-flight tasks.
    Failures are returned as the exception itself (caller filters)."""
    sem = asyncio.Semaphore(limit)
    async def _wrapped(c):
        async with sem:
            try:
                return await c
            except Exception as e:
                return e
    return await asyncio.gather(*[_wrapped(c) for c in coros])


# ---------------------------------------------------------------------------
# Spot-check dump (human-readable markdown sample for QA before training)
# ---------------------------------------------------------------------------

def write_spot_check_md(sft_records: list[dict], out_path: Path,
                         n_sft: int, seed: int = 42) -> None:
    """Sample N SFT records and dump in human-readable markdown for manual QA."""
    rng = random.Random(seed)
    sft_sample = rng.sample(sft_records, min(n_sft, len(sft_records)))

    lines = [
        f"# Spot check — {len(sft_sample)} SFT samples",
        "",
        "**For each SFT sample, check:**",
        "1. rationale 引用的规则在 descriptor 里存在吗？（不要胡编「根据 XXX 原则」）",
        "2. rationale 的结论和 plan 一致吗？（rationale 说不加 X，plan 里就不该有 X）",
        "3. intent 是否带上了 user_goal 的具体内容（不是模板化的「process the X」）",
        "",
        "---",
        "",
        "# SFT samples",
        "",
    ]
    for i, r in enumerate(sft_sample, 1):
        msgs = r["messages"]
        user = next(m["content"] for m in msgs if m["role"] == "user")
        asst = json.loads(next(m["content"] for m in msgs if m["role"] == "assistant"))
        lines.append(f"## SFT #{i}")
        lines.append(f"**user_goal:** {user}")
        lines.append("")
        lines.append(f"**rationale:** {asst['rationale']}")
        lines.append("")
        lines.append("**plan:**")
        for s in asst["plan"]:
            lines.append(f"- `{s['agent_id']}` — {s['intent']}")
        lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# Main driver
# ---------------------------------------------------------------------------

async def run(dry_run: bool = False, seed: int = 42, concurrency: int = 20,
              spot_check_n: int = 50,
              chains_filter: tuple[str, ...] = (),
              append_to: Path | None = None) -> None:
    random.seed(seed)
    from training.director.gen_samples import build_system_prompt, _assistant_response
    system_prompt = build_system_prompt()

    # Load eval user_goals for isolation filter
    eval_path = REPO_ROOT / "evals/director_routing/eval_cases.json"
    eval_cases = json.loads(eval_path.read_text(encoding="utf-8"))
    eval_goals_norm = {_normalize(c["user_goal"]) for c in eval_cases}

    # Scale down budget for dry-run (~50 SFT samples total)
    budget = VARIANTS_BUDGET.copy()

    # Apply --chains-filter: keep only shapes whose tuple contains EVERY
    # requested agent id (AND-semantics). Used to regenerate a slice of
    # the blueprint without re-burning the whole 1280-sample budget —
    # e.g. ``--chains-filter NarrationAgent`` picks the 12 storytelling
    # shapes.
    if chains_filter:
        required = set(chains_filter)
        budget = {
            chain: n for chain, n in budget.items() if required.issubset(set(chain))
        }
        if not budget:
            raise SystemExit(
                f"No chain shapes contain all of {sorted(required)!r} — nothing to generate"
            )

    if dry_run:
        budget = {k: max(2, v // 20) for k, v in budget.items()}
    total_sft = sum(budget.values())
    print(f"Target: {total_sft} SFT samples across {len(budget)} chains "
          f"(concurrency={concurrency}, dry_run={dry_run}"
          + (f", chains_filter={sorted(chains_filter)}" if chains_filter else "")
          + ")")

    # -------- Phase 1: generate goals for all chains in parallel --------
    print("\n[1/2] Generating user_goals…")
    goal_coros = [gen_goals_for_chain(chain, n) for chain, n in budget.items()]
    goal_results = await _gather_with_limit(goal_coros, limit=concurrency)
    chain_to_goals: dict[tuple, list[str]] = {}
    for chain, res in zip(budget.keys(), goal_results):
        if isinstance(res, Exception):
            print(f"  WARN: goal-gen failed for chain {chain[:3]}…: {res}")
            chain_to_goals[chain] = []
            continue
        # filter out anything overlapping eval set
        filtered = [g for g in res if _normalize(g) not in eval_goals_norm]
        chain_to_goals[chain] = filtered[:budget[chain]]
    n_goals = sum(len(v) for v in chain_to_goals.values())
    print(f"  {n_goals} goals after eval-isolation filter")

    # -------- Phase 2: generate (rationale, plan) per goal in parallel --------
    print(f"\n[2/2] Generating rationale + intents for {n_goals} goals…")
    flat: list[tuple[tuple, str]] = []  # (chain_ids, goal)
    for chain, goals in chain_to_goals.items():
        for g in goals:
            flat.append((chain, g))
    rationale_coros = [gen_assistant_response(g, list(c)) for c, g in flat]
    rationale_results = await _gather_with_limit(rationale_coros, limit=concurrency)

    sft_records: list[dict] = []
    failed = 0
    for (chain, goal), resp in zip(flat, rationale_results):
        if isinstance(resp, Exception):
            failed += 1
            continue
        sft_records.append({
            "messages": [
                {"role": "system",    "content": system_prompt},
                {"role": "user",      "content": goal},
                {"role": "assistant", "content": _assistant_response(resp["rationale"], resp["plan"])},
            ],
        })
    print(f"  {len(sft_records)} SFT records (failed: {failed})")

    # ----- Save -----
    out_dir = Path(__file__).parent
    suffix = "_dryrun" if dry_run else "_full"
    spot_path = out_dir / f"samples{suffix}.spot_check.md"

    if append_to is not None:
        # Merge into an existing jsonl (e.g. the post-processed 1110-sample
        # baseline) so the delta slice this run produced adds to — rather
        # than replaces — the prior corpus. Useful with --chains-filter
        # to grow coverage of a new chain class without re-burning the
        # whole budget.
        sft_path = append_to if append_to.is_absolute() else (out_dir / append_to)
        existing = []
        if sft_path.is_file():
            with sft_path.open("r", encoding="utf-8") as f:
                existing = [line for line in f if line.strip()]
        with sft_path.open("w", encoding="utf-8") as f:
            for line in existing:
                f.write(line if line.endswith("\n") else line + "\n")
            for r in sft_records:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        print(
            f"\nAppended {len(sft_records)} new samples → "
            f"{sft_path.relative_to(Path.cwd())} "
            f"(prior {len(existing)} preserved; total {len(existing) + len(sft_records)})"
        )
    else:
        sft_path = out_dir / f"samples_sft{suffix}.jsonl"
        with sft_path.open("w", encoding="utf-8") as f:
            for r in sft_records:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        print(f"\nWrote {sft_path.relative_to(Path.cwd())}  ({len(sft_records)} samples)")

    write_spot_check_md(sft_records, spot_path, n_sft=spot_check_n, seed=seed)
    print(f"Wrote {spot_path.relative_to(Path.cwd())}  (review {spot_check_n} SFT before training)")
    print("\nNext: PYTHONPATH=. python training/director/validate.py --seq-len 8192 \\")
    print(f"        --sft {sft_path.name}")


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def _normalize(g: str) -> str:
    import re
    return re.sub(r"[\s,。,！!？?、；;：:]+", "", (g or "").lower().strip())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="Generate ~50 SFT samples for smoke test")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--concurrency", type=int, default=20,
                    help="Max concurrent teacher API calls (default 20)")
    ap.add_argument("--spot-check", type=int, default=50,
                    help="Number of SFT samples to dump for human review")
    ap.add_argument(
        "--chains-filter", nargs="*", default=[],
        help=(
            "Regenerate only chain shapes that contain ALL of the given "
            "agent ids. AND-semantics — e.g. `--chains-filter NarrationAgent` "
            "targets the 12 storytelling shapes; `--chains-filter "
            "NarrationAgent TranslationAgent` narrows to bilingual "
            "storytelling chains."
        ),
    )
    ap.add_argument(
        "--append-to", type=Path, default=None,
        help=(
            "Instead of overwriting samples_sft_full.jsonl, merge the "
            "newly generated samples into this existing jsonl (prior rows "
            "preserved). Pair with --chains-filter to grow coverage of a "
            "new chain class without re-burning the full 1280-sample budget."
        ),
    )
    args = ap.parse_args()
    asyncio.run(run(
        dry_run=args.dry_run,
        seed=args.seed,
        concurrency=args.concurrency,
        spot_check_n=args.spot_check,
        chains_filter=tuple(args.chains_filter),
        append_to=args.append_to,
    ))


if __name__ == "__main__":
    main()
