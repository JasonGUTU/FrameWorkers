"""Scale to 1000 SFT + 500 DPO training samples via LLM teacher.

Uses project-native `inference.clients.LLMClient` (Cloudflare AI Gateway)
to call a strong teacher (Claude Sonnet / GPT-5 / Gemini Pro) for:
  - Generating diverse user_goal variants for each unique chain
  - Writing high-quality CoT rationale for each (goal, chain)
  - Writing "justification" rationale for bias-injected rejected chains

Bias injection for DPO is PROGRAMMATIC (Python, not LLM) — deterministic
and covers all 4 known failure modes: VA overshoot / Ambience coupling /
Compositor suffix / missing IntakeText.

Output:
    training/director/samples_sft_full.jsonl   (~1000 samples)
    training/director/samples_dpo_full.jsonl   (~500 pairs)

Usage:
    PYTHONPATH=. python training/director/gen_training_full.py --dry-run   # 50 samples only
    PYTHONPATH=. python training/director/gen_training_full.py             # full 1000+500
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

# Variants-per-chain budget. Sums to ~1000 for SFT.
VARIANTS_BUDGET = {
    # Creative full chain (highest freq in real use)
    ("IntakeTextAgent", "StoryAgent", "ScreenplayAgent", "KeyFrameAgent", "VideoAgent",
     "MusicAgent", "AmbienceAgent", "AudioMixAgent", "CompositorAgent"): 100,
    # Creative + subtitle
    ("IntakeTextAgent", "StoryAgent", "ScreenplayAgent", "KeyFrameAgent", "VideoAgent",
     "MusicAgent", "AmbienceAgent", "AudioMixAgent", "SubtitleAgent", "CompositorAgent"): 80,
    # Creative + bilingual
    ("IntakeTextAgent", "StoryAgent", "ScreenplayAgent", "KeyFrameAgent", "VideoAgent",
     "MusicAgent", "AmbienceAgent", "AudioMixAgent", "SubtitleAgent", "TranslationAgent", "CompositorAgent"): 60,
    # Image-based creative
    ("IntakeTextAgent", "IntakeImageAgent", "BriefEnricherAgent", "StoryAgent", "ScreenplayAgent",
     "KeyFrameAgent", "VideoAgent", "MusicAgent", "AmbienceAgent", "AudioMixAgent", "CompositorAgent"): 60,
    # BGM on uploaded video
    ("IntakeTextAgent", "IntakeVideoAgent", "MusicAgent", "AudioMixAgent", "CompositorAgent"): 80,
    # BGM + ambience on uploaded video
    ("IntakeTextAgent", "IntakeVideoAgent", "MusicAgent", "AmbienceAgent", "AudioMixAgent", "CompositorAgent"): 50,
    # Style transfer only
    ("IntakeTextAgent", "IntakeVideoAgent", "StyleTransferAgent"): 60,
    # Style + subtitle
    ("IntakeTextAgent", "IntakeVideoAgent", "StyleTransferAgent", "TranscriptionAgent",
     "SubtitleAgent", "CompositorAgent"): 50,
    # Style + music
    ("IntakeTextAgent", "IntakeVideoAgent", "StyleTransferAgent", "MusicAgent", "CompositorAgent"): 40,
    # Video extend only
    ("IntakeTextAgent", "IntakeVideoAgent", "VideoExtendAgent"): 60,
    # Extend + music
    ("IntakeTextAgent", "IntakeVideoAgent", "VideoExtendAgent", "MusicAgent", "AudioMixAgent",
     "CompositorAgent"): 40,
    # Extend + subtitle
    ("IntakeTextAgent", "IntakeVideoAgent", "VideoExtendAgent", "TranscriptionAgent", "SubtitleAgent",
     "CompositorAgent"): 40,
    # Highlight only
    ("IntakeTextAgent", "IntakeVideoAgent", "VideoAnalysisAgent", "HighlightAgent"): 60,
    # Highlight + subtitle
    ("IntakeTextAgent", "IntakeVideoAgent", "VideoAnalysisAgent", "HighlightAgent",
     "TranscriptionAgent", "SubtitleAgent", "CompositorAgent"): 40,
    # Highlight + music
    ("IntakeTextAgent", "IntakeVideoAgent", "VideoAnalysisAgent", "HighlightAgent", "MusicAgent",
     "CompositorAgent"): 30,
    # Transcribe + translate + subtitle
    ("IntakeTextAgent", "IntakeVideoAgent", "TranscriptionAgent", "TranslationAgent",
     "SubtitleAgent", "CompositorAgent"): 40,
    # Subtitle for uploaded video (monolingual)
    ("IntakeTextAgent", "IntakeVideoAgent", "TranscriptionAgent", "SubtitleAgent", "CompositorAgent"): 50,
    # Extend + style
    ("IntakeTextAgent", "IntakeVideoAgent", "VideoExtendAgent", "StyleTransferAgent"): 30,
    # Style + extend + music
    ("IntakeTextAgent", "IntakeVideoAgent", "StyleTransferAgent", "VideoExtendAgent",
     "MusicAgent", "CompositorAgent"): 30,
    # Analyze + creative + subtitle (long)
    ("IntakeTextAgent", "IntakeVideoAgent", "VideoAnalysisAgent", "StoryAgent", "ScreenplayAgent",
     "KeyFrameAgent", "VideoAgent", "MusicAgent", "AmbienceAgent", "AudioMixAgent",
     "SubtitleAgent", "CompositorAgent"): 30,
}  # Total: 1030


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


REJECTED_RATIONALE_SYSTEM = """\
你是为 DPO 训练合成 "rejected" rationale 的助手。
给定：(user_goal, chosen chain, rejected chain, 注入的 bias 类型)

你的任务是写一段**看似合理但实际错误**的 rationale，为这条 rejected chain 找"借口"。
这段 rationale 在训练时会被模型学到"这类推理是错的"。

约束：
- rationale 要**自洽**，不能明显胡扯
- 要包含 bias 对应的**错误推理模式**，如：
  - "需要先分析视频才能决定..." (VA overshoot 的借口)
  - "音乐搭配环境音更有氛围..." (Ambience coupling 的借口)
  - "视频交付都应由 Compositor 收尾..." (Compositor suffix 的借口)
  - "纯视频操作可以省略 IntakeText..." (missing IntakeText 的借口)
- rationale 长度目标必须对齐参考的 chosen rationale token 数 ± 5%
- 中英文按 user_goal 的语种决定
- 输出纯文本 rationale
"""


# ---------------------------------------------------------------------------
# Bias injection (programmatic, deterministic)
# ---------------------------------------------------------------------------

def inject_va_overshoot(chain: list[dict]) -> list[dict] | None:
    """Insert VideoAnalysisAgent after IntakeVideoAgent. Only applies to
    uploaded-video chains where VA is NOT already there."""
    agent_ids = [s["agent_id"] for s in chain]
    if "IntakeVideoAgent" not in agent_ids or "VideoAnalysisAgent" in agent_ids:
        return None
    out = []
    for step in chain:
        out.append(step)
        if step["agent_id"] == "IntakeVideoAgent":
            out.append({"agent_id": "VideoAnalysisAgent",
                        "intent": "Analyze the video's content and mood before proceeding."})
    return out


def inject_ambience_coupling(chain: list[dict]) -> list[dict] | None:
    """Insert AmbienceAgent after MusicAgent. Only applies when Music is
    present but Ambience is NOT."""
    agent_ids = [s["agent_id"] for s in chain]
    if "MusicAgent" not in agent_ids or "AmbienceAgent" in agent_ids:
        return None
    out = []
    for step in chain:
        out.append(step)
        if step["agent_id"] == "MusicAgent":
            out.append({"agent_id": "AmbienceAgent",
                        "intent": "Layer in environmental sounds to enrich the mood."})
    return out


def inject_compositor_suffix(chain: list[dict]) -> list[dict] | None:
    """Append CompositorAgent. Only applies when chain ends with
    VideoExtend/Highlight/StyleTransfer (raw deliverables)."""
    if not chain:
        return None
    last = chain[-1]["agent_id"]
    if last not in ("VideoExtendAgent", "HighlightAgent", "StyleTransferAgent"):
        return None
    return chain + [{"agent_id": "CompositorAgent",
                     "intent": "Finalize the clip as the deliverable."}]


def drop_intake_text(chain: list[dict]) -> list[dict] | None:
    """Remove IntakeTextAgent from the front. Only applies if present."""
    if not chain or chain[0]["agent_id"] != "IntakeTextAgent":
        return None
    return chain[1:]


BIAS_INJECTORS = [
    ("va_overshoot",        inject_va_overshoot),
    ("ambience_coupling",   inject_ambience_coupling),
    ("compositor_suffix",   inject_compositor_suffix),
    ("missing_intake_text", drop_intake_text),
]


# ---------------------------------------------------------------------------
# Teacher-model helpers (stubs — wire when ready)
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


async def llm_text(system: str, user: str, model: str = TEACHER_MODEL) -> str:
    """Call the teacher; return raw text (for rationale)."""
    from inference.clients import LLMClient
    client = LLMClient()
    return await client.chat_text(
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


async def gen_rejected_rationale(user_goal: str, chosen_rationale: str,
                                  chosen_chain: list[str], rejected_chain: list[str],
                                  bias_type: str) -> str:
    user = json.dumps({
        "user_goal": user_goal,
        "chosen_chain": chosen_chain,
        "rejected_chain": rejected_chain,
        "bias_type": bias_type,
        "chosen_rationale_length_hint": len(chosen_rationale),
    }, ensure_ascii=False)
    return (await llm_text(REJECTED_RATIONALE_SYSTEM, user)).strip()


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

def write_spot_check_md(sft_records: list[dict], dpo_records: list[dict],
                         out_path: Path, n_sft: int, n_dpo: int, seed: int = 42) -> None:
    """Sample N SFT + N/2 DPO records and dump in human-readable markdown.
    The reviewer answers 3 questions per sample (see docstring at top of file)."""
    rng = random.Random(seed)
    sft_sample = rng.sample(sft_records, min(n_sft, len(sft_records)))
    dpo_sample = rng.sample(dpo_records, min(n_dpo, len(dpo_records)))

    lines = [
        f"# Spot check — {len(sft_sample)} SFT + {len(dpo_sample)} DPO samples",
        "",
        "**For each SFT sample, check:**",
        "1. rationale 引用的规则在 descriptor 里存在吗？（不要胡编「根据 XXX 原则」）",
        "2. rationale 的结论和 plan 一致吗？（rationale 说不加 X，plan 里就不该有 X）",
        "3. intent 是否带上了 user_goal 的具体内容（不是模板化的「process the X」）",
        "",
        "**For each DPO pair, check:**",
        "1. chosen rationale 是否清晰拒绝了 rejected 引入的 bias",
        "2. rejected rationale 是否「看似合理但显然错」（自洽但确实是错的推理）",
        "3. 长度是否大致平衡（chosen vs rejected total assistant content 差距 < 15%）",
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

    lines.append("# DPO pairs")
    lines.append("")
    for i, r in enumerate(dpo_sample, 1):
        prompt = r["prompt"]
        user = next(m["content"] for m in prompt if m["role"] == "user")
        chosen = json.loads(r["chosen"][0]["content"])
        rejected = json.loads(r["rejected"][0]["content"])
        lines.append(f"## DPO #{i}")
        lines.append(f"**user_goal:** {user}")
        lines.append("")
        lines.append(f"**chosen rationale:** {chosen['rationale']}")
        lines.append("**chosen plan:** " + " → ".join(s["agent_id"] for s in chosen["plan"]))
        lines.append("")
        lines.append(f"**rejected rationale:** {rejected['rationale']}")
        lines.append("**rejected plan:** " + " → ".join(s["agent_id"] for s in rejected["plan"]))
        lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# Main driver
# ---------------------------------------------------------------------------

async def run(dry_run: bool = False, seed: int = 42, concurrency: int = 20,
              spot_check_n: int = 50) -> None:
    random.seed(seed)
    from training.director.gen_samples import build_system_prompt, _assistant_response
    system_prompt = build_system_prompt()

    # Load eval user_goals for isolation filter
    eval_path = REPO_ROOT / "evals/director_routing/eval_cases.json"
    eval_cases = json.loads(eval_path.read_text(encoding="utf-8"))
    eval_goals_norm = {_normalize(c["user_goal"]) for c in eval_cases}

    # Scale down budget for dry-run (50 SFT + ~25 DPO total)
    budget = VARIANTS_BUDGET.copy()
    if dry_run:
        budget = {k: max(2, v // 20) for k, v in budget.items()}
    total_sft = sum(budget.values())
    print(f"Target: {total_sft} SFT samples across {len(budget)} chains "
          f"(concurrency={concurrency}, dry_run={dry_run})")

    # -------- Phase 1: generate goals for all chains in parallel --------
    print("\n[1/3] Generating user_goals…")
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
    print(f"\n[2/3] Generating rationale + intents for {n_goals} goals…")
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
            "_meta": {"chain_ids": list(chain), "plan": resp["plan"]},
        })
    print(f"  {len(sft_records)} SFT records (failed: {failed})")

    # -------- Phase 3: build DPO pairs --------
    print("\n[3/3] Generating DPO rejected rationales…")
    dpo_target = 25 if dry_run else 500
    dpo_sources = random.sample(sft_records, k=min(len(sft_records), dpo_target * 2))

    # First pass: pick a bias-injector per source synchronously (deterministic)
    dpo_jobs = []  # list of (src, chosen_obj, rejected_plan, bias_name)
    for src in dpo_sources:
        chosen_plan = src["_meta"]["plan"]
        chosen_obj = json.loads(src["messages"][-1]["content"])
        applicable = []
        for name, fn in BIAS_INJECTORS:
            rp = fn(chosen_plan)
            if rp is not None:
                applicable.append((name, rp))
        if not applicable:
            continue
        bias_name, rejected_plan = random.choice(applicable)
        dpo_jobs.append((src, chosen_obj, rejected_plan, bias_name))
        if len(dpo_jobs) >= dpo_target:
            break

    # Second pass: parallel call teacher for rejected rationales
    rej_coros = [
        gen_rejected_rationale(
            user_goal=src["messages"][1]["content"],
            chosen_rationale=chosen_obj["rationale"],
            chosen_chain=src["_meta"]["chain_ids"],
            rejected_chain=[s["agent_id"] for s in rejected_plan],
            bias_type=bias_name,
        )
        for (src, chosen_obj, rejected_plan, bias_name) in dpo_jobs
    ]
    rej_results = await _gather_with_limit(rej_coros, limit=concurrency)

    dpo_records: list[dict] = []
    failed_dpo = 0
    for (src, chosen_obj, rejected_plan, bias_name), rej in zip(dpo_jobs, rej_results):
        if isinstance(rej, Exception):
            failed_dpo += 1
            continue
        rejected_content = _assistant_response(rej, rejected_plan)
        dpo_records.append({
            "prompt": src["messages"][:2],
            "chosen": [{"role": "assistant", "content": src["messages"][-1]["content"]}],
            "rejected": [{"role": "assistant", "content": rejected_content}],
        })
    print(f"  {len(dpo_records)} DPO pairs (failed: {failed_dpo})")

    # Strip _meta before save
    for r in sft_records:
        r.pop("_meta", None)

    # ----- Save -----
    out_dir = Path(__file__).parent
    suffix = "_dryrun" if dry_run else "_full"
    sft_path = out_dir / f"samples_sft{suffix}.jsonl"
    dpo_path = out_dir / f"samples_dpo{suffix}.jsonl"
    spot_path = out_dir / f"samples{suffix}.spot_check.md"

    with sft_path.open("w", encoding="utf-8") as f:
        for r in sft_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with dpo_path.open("w", encoding="utf-8") as f:
        for r in dpo_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    write_spot_check_md(sft_records, dpo_records, spot_path,
                        n_sft=spot_check_n, n_dpo=spot_check_n // 2, seed=seed)

    print(f"\nWrote {sft_path.relative_to(Path.cwd())}  ({len(sft_records)} samples)")
    print(f"Wrote {dpo_path.relative_to(Path.cwd())}  ({len(dpo_records)} pairs)")
    print(f"Wrote {spot_path.relative_to(Path.cwd())}  (review {spot_check_n} SFT + {spot_check_n//2} DPO before training)")
    print("\nNext: PYTHONPATH=. python training/director/validate.py --seq-len 4096 \\")
    print(f"        --sft {sft_path.name} --dpo {dpo_path.name}")


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def _normalize(g: str) -> str:
    import re
    return re.sub(r"[\s,。,！!？?、；;：:]+", "", (g or "").lower().strip())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="Generate ~50 SFT + ~25 DPO for smoke test")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--concurrency", type=int, default=20,
                    help="Max concurrent teacher API calls (default 20)")
    ap.add_argument("--spot-check", type=int, default=50,
                    help="Number of SFT samples (and N/2 DPO pairs) to dump for human review")
    args = ap.parse_args()
    asyncio.run(run(dry_run=args.dry_run, seed=args.seed,
                    concurrency=args.concurrency, spot_check_n=args.spot_check))


if __name__ == "__main__":
    main()
