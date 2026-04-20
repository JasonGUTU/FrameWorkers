"""Generate 5 SFT + 5 DPO smoke samples for director routing training.

This is the SMOKE TEST stage — we hand-craft 10 training samples and
verify they flow through the expected training pipeline end-to-end
BEFORE scaling to ~1000 SFT + 500 DPO. The goal is to catch schema /
tokenization / isolation bugs early.

Output:
    training/director/samples_sft.jsonl   (5 SFT samples, messages format)
    training/director/samples_dpo.jsonl   (5 DPO pairs,  trl DPO format)

Both formats match HuggingFace TRL SFTTrainer / DPOTrainer natively.
"""

from __future__ import annotations

import json
from pathlib import Path

from agents import get_agent_registry
from director_agent import prompts as director_prompts


# ---------------------------------------------------------------------------
# Build a COMPACT catalog for training (agent_id + one-line purpose only).
# The full catalog with inputs/outputs is ~35K chars; compact is ~2K chars,
# which lets seq_len=2048 fit a full sample including rationale + plan.
# ---------------------------------------------------------------------------

def build_compact_catalog() -> list[dict]:
    registry = get_agent_registry()
    infos = registry.get_all_agents_info()
    compact = []
    for info in infos:
        agent_id = info.get("id") or info.get("name")
        # Take just the first sentence of description as the one-line purpose.
        desc = (info.get("description") or "").strip()
        one_line = desc.split("\n")[0][:200]
        compact.append({"agent_id": agent_id, "purpose": one_line})
    return compact


def build_system_prompt() -> str:
    """System prompt = PLAN_UPFRONT_SYSTEM + compact agent list (no user goal)."""
    catalog = build_compact_catalog()
    allowed = [c["agent_id"] for c in catalog]
    return (
        director_prompts.PLAN_UPFRONT_SYSTEM
        + "\n\nAllowed agent ids:\n"
        + json.dumps(allowed, ensure_ascii=False)
        + "\n\nAgent catalog (compact, one-line purposes):\n"
        + json.dumps(catalog, ensure_ascii=False)
    )


# ---------------------------------------------------------------------------
# Hand-crafted 5 SFT samples: diverse chain shapes, high-quality rationales.
# ---------------------------------------------------------------------------

def _assistant_response(rationale: str, plan_steps: list[dict]) -> str:
    """Serialize assistant response in the exact schema PLAN_UPFRONT_SYSTEM demands."""
    return json.dumps(
        {"rationale": rationale, "plan": plan_steps},
        ensure_ascii=False,
    )


SFT_SAMPLES = [
    # 1. Pure creative full chain
    {
        "user_goal": "做一部灵异短剧，讲外卖骑手误入凶宅解开尘封多年女尸案的故事",
        "rationale": (
            "用户提供纯文本创作 brief，没有上传任何素材。标准创作链：先 IntakeText 落文，"
            "Story → Screenplay → KeyFrame → Video 生成视频；创作内容默认配 Music + Ambience，"
            "AudioMix 合轨，Compositor 收尾。未要求字幕，不加 Subtitle。"
        ),
        "plan_steps": [
            {"agent_id": "IntakeTextAgent",  "intent": "Ingest the user's textual brief and produce the initial text artifact."},
            {"agent_id": "StoryAgent",       "intent": "Develop the horror short-drama story outline: delivery driver enters haunted house, unveils old corpse case."},
            {"agent_id": "ScreenplayAgent", "intent": "Turn the story outline into a scene/shot breakdown with dialogue."},
            {"agent_id": "KeyFrameAgent",   "intent": "Generate keyframe images for each shot."},
            {"agent_id": "VideoAgent",      "intent": "Animate keyframes into video clips."},
            {"agent_id": "MusicAgent",      "intent": "Compose a tense horror background score."},
            {"agent_id": "AmbienceAgent",   "intent": "Generate haunted-house ambient sounds (wind, creaks, distant whispers)."},
            {"agent_id": "AudioMixAgent",   "intent": "Mix the music and ambience tracks into a single master audio."},
            {"agent_id": "CompositorAgent", "intent": "Burn the master audio onto the video to produce the final deliverable."},
        ],
    },
    # 2. Existing video + BGM only (the hard case router currently fails on)
    {
        "user_goal": "给这段已拍好的短剧加一段紧张悬疑的背景乐",
        "rationale": (
            "用户上传了已有视频 + 只要 BGM。IntakeText 吸收文本指令，IntakeVideo 吸收视频素材。"
            "跳过 VideoAnalysis 因为用户未要求分析或剪辑 — 直接跑 Music 生成 BGM。"
            "不加 Ambience 因为用户没提任何环境音。AudioMix 只处理单一音轨但仍需跑以统一音量。"
            "Compositor 收尾把 BGM 叠到视频上。"
        ),
        "plan_steps": [
            {"agent_id": "IntakeTextAgent",  "intent": "Ingest the user's textual instruction about adding BGM."},
            {"agent_id": "IntakeVideoAgent", "intent": "Ingest the uploaded short-drama video into a caption-rich artifact."},
            {"agent_id": "MusicAgent",       "intent": "Compose a tense suspense background music track matching the video's mood and duration."},
            {"agent_id": "AudioMixAgent",    "intent": "Normalize and master the generated BGM for overlay."},
            {"agent_id": "CompositorAgent",  "intent": "Burn the BGM onto the uploaded video to produce the final deliverable."},
        ],
    },
    # 3. Existing video + style transfer + subtitle
    {
        "user_goal": "把这段现代都市短剧整体转成水彩画风，并加上中文字幕",
        "rationale": (
            "用户上传视频，要求风格迁移 + 加同语字幕。IntakeText + IntakeVideo 先进素材。"
            "StyleTransfer 转水彩画风。字幕 source text 不是用户提供的 — 需要 Transcription"
            "从视频音轨转录出带时间戳的中文台词文本，再由 Subtitle 生成 SRT。"
            "Compositor 把字幕烧到风格迁移后的视频上。"
        ),
        "plan_steps": [
            {"agent_id": "IntakeTextAgent",    "intent": "Ingest the user's instruction."},
            {"agent_id": "IntakeVideoAgent",   "intent": "Ingest the uploaded urban-drama video."},
            {"agent_id": "StyleTransferAgent", "intent": "Convert the video to watercolor painting style, preserving motion and shot composition."},
            {"agent_id": "TranscriptionAgent", "intent": "Transcribe the video's Chinese dialogue to timestamped text."},
            {"agent_id": "SubtitleAgent",      "intent": "Generate a Chinese SRT subtitle track from the transcript, aligned to video timing."},
            {"agent_id": "CompositorAgent",    "intent": "Burn the subtitle track onto the style-transferred video."},
        ],
    },
    # 4. Creative + bilingual subtitle (long chain, standard pattern)
    {
        "user_goal": "做一部带中英双语字幕的赛博朋克短剧，女主是记忆黑客入侵巨头公司董事会的故事",
        "rationale": (
            "纯文本创作 + 双语字幕需求。创作主链 IntakeText → Story → Screenplay → KeyFrame → Video 全走。"
            "配乐用 Music + Ambience + AudioMix 三件套（赛博朋克题材音乐和环境音都需要）。"
            "Subtitle 从 Screenplay 的中文对白生成中文 SRT；Translation 把中文 SRT 翻成英文（保留时间戳）。"
            "Compositor 收尾烧双语字幕。"
        ),
        "plan_steps": [
            {"agent_id": "IntakeTextAgent",   "intent": "Ingest the user's cyberpunk drama brief with bilingual subtitle requirement."},
            {"agent_id": "StoryAgent",        "intent": "Develop the story: female memory hacker infiltrates the mega-corp boardroom."},
            {"agent_id": "ScreenplayAgent",  "intent": "Scene/shot breakdown with Chinese dialogue."},
            {"agent_id": "KeyFrameAgent",    "intent": "Generate cyberpunk-styled keyframes for each shot."},
            {"agent_id": "VideoAgent",       "intent": "Animate keyframes into video clips."},
            {"agent_id": "MusicAgent",       "intent": "Compose a synthwave / cyberpunk-style score."},
            {"agent_id": "AmbienceAgent",    "intent": "Generate urban-tech ambient sounds (neon hum, rain, distant sirens)."},
            {"agent_id": "AudioMixAgent",    "intent": "Mix music and ambience."},
            {"agent_id": "SubtitleAgent",    "intent": "Generate Chinese SRT from the screenplay dialogue."},
            {"agent_id": "TranslationAgent", "intent": "Translate the Chinese SRT to English, preserving cue timing."},
            {"agent_id": "CompositorAgent",  "intent": "Burn both subtitle tracks onto the video with the master audio."},
        ],
    },
    # 5. Highlight as final deliverable (no Compositor, no Music)
    {
        "user_goal": "从这部都市悬疑短剧里剪出最惊悚的反转瞬间做宣发物料",
        "rationale": (
            "用户上传视频，纯剪辑需求 — 要 highlight 片段作为最终交付。IntakeText + IntakeVideo 进料。"
            "VideoAnalysis 先分析视频的情节结构找反转点。Highlight 切出片段。"
            "不加 Music（用户未要求配乐）、不加 Subtitle、不加 Compositor —— Highlight 直接输出的就是成片物料。"
        ),
        "plan_steps": [
            {"agent_id": "IntakeTextAgent",    "intent": "Ingest the user's highlight-reel request."},
            {"agent_id": "IntakeVideoAgent",   "intent": "Ingest the uploaded urban-suspense drama."},
            {"agent_id": "VideoAnalysisAgent", "intent": "Analyze narrative beats and identify twist / reveal moments."},
            {"agent_id": "HighlightAgent",     "intent": "Cut out the top suspenseful twist moments as a promotional highlight reel."},
        ],
    },
]


# ---------------------------------------------------------------------------
# 5 DPO pairs: each injects exactly ONE known bias into the rejected side.
# ---------------------------------------------------------------------------

DPO_PAIRS = [
    # 1. VideoAnalysis overshoot on pure BGM task
    {
        "user_goal": "给这段都市 vlog 配一段轻快的电子氛围背景乐",
        "chosen_rationale": (
            "用户上传视频 + 只要 BGM。跳过 VideoAnalysis — 用户没要求分析或剪辑，"
            "直接生成 BGM 叠上去即可。只 Music（不带 Ambience，因为未提及环境音）。"
        ),
        "chosen_plan": [
            {"agent_id": "IntakeTextAgent",  "intent": "Ingest the BGM request."},
            {"agent_id": "IntakeVideoAgent", "intent": "Ingest the urban vlog."},
            {"agent_id": "MusicAgent",       "intent": "Compose an upbeat electronic background track."},
            {"agent_id": "AudioMixAgent",    "intent": "Normalize the BGM."},
            {"agent_id": "CompositorAgent",  "intent": "Burn the BGM onto the vlog."},
        ],
        "rejected_rationale": (
            "用户上传了视频，先跑 VideoAnalysis 分析视频内容和情绪基调才能选出最匹配的 BGM，"
            "然后再生成音乐叠上去。"
        ),
        "rejected_plan": [
            {"agent_id": "IntakeTextAgent",    "intent": "Ingest the BGM request."},
            {"agent_id": "IntakeVideoAgent",   "intent": "Ingest the urban vlog."},
            {"agent_id": "VideoAnalysisAgent", "intent": "Analyze the vlog's content and emotional tone to inform music selection."},
            {"agent_id": "MusicAgent",         "intent": "Compose BGM guided by the analysis."},
            {"agent_id": "AudioMixAgent",      "intent": "Normalize the BGM."},
            {"agent_id": "CompositorAgent",    "intent": "Burn the BGM onto the vlog."},
        ],
    },
    # 2. Ambience overshoot (Music-Ambience coupling) on BGM-only request
    {
        "user_goal": "给这段古装短剧配一段悲壮的鼓点背景乐",
        "chosen_rationale": (
            "用户只要 BGM（鼓点配乐），没提任何环境音（风声/雨声/刀剑声）。"
            "只调 Music，不加 Ambience —— 创作链里 Music+Ambience 捆绑是默认模式，"
            "但对'给已有视频加 BGM'场景 Ambience 是多余的。"
        ),
        "chosen_plan": [
            {"agent_id": "IntakeTextAgent",  "intent": "Ingest the BGM request."},
            {"agent_id": "IntakeVideoAgent", "intent": "Ingest the costume drama clip."},
            {"agent_id": "MusicAgent",       "intent": "Compose a solemn, epic drum-driven score."},
            {"agent_id": "AudioMixAgent",    "intent": "Master the drum track."},
            {"agent_id": "CompositorAgent",  "intent": "Burn the music onto the video."},
        ],
        "rejected_rationale": (
            "既然是古装场景，鼓点背景乐加上金戈铁马风声等环境音会更有氛围感。"
            "跑 Music 和 Ambience 双轨，AudioMix 合成。"
        ),
        "rejected_plan": [
            {"agent_id": "IntakeTextAgent",  "intent": "Ingest the BGM request."},
            {"agent_id": "IntakeVideoAgent", "intent": "Ingest the costume drama clip."},
            {"agent_id": "MusicAgent",       "intent": "Compose a solemn drum score."},
            {"agent_id": "AmbienceAgent",    "intent": "Generate battlefield ambient sounds (wind, distant horns)."},
            {"agent_id": "AudioMixAgent",    "intent": "Mix drum track with ambient."},
            {"agent_id": "CompositorAgent",  "intent": "Burn combined audio onto video."},
        ],
    },
    # 3. Compositor overshoot on pure VideoExtend
    {
        "user_goal": "把这场女主表白落泪的戏延长到 12 秒，加上她颤抖的手部特写",
        "chosen_rationale": (
            "用户只要把一段视频延长 —— 输出本身就是延长后的视频片段，不涉及叠字幕 / 加音轨。"
            "VideoExtend 之后直接 done，不跑 Compositor —— Compositor 只在要烧字幕 / 烧音轨时才需要。"
        ),
        "chosen_plan": [
            {"agent_id": "IntakeTextAgent",  "intent": "Ingest the extension request."},
            {"agent_id": "IntakeVideoAgent", "intent": "Ingest the source clip."},
            {"agent_id": "VideoExtendAgent", "intent": "Extend the confession scene to 12s, adding a trembling-hand close-up."},
        ],
        "rejected_rationale": (
            "延长视频后由 Compositor 合成为最终成品交付 —— 视频类交付都应走 Compositor 作为统一收尾步骤。"
            "即便没有字幕叠加，Compositor 也能规整输出格式和容器，保证产物编码一致。"
        ),
        "rejected_plan": [
            {"agent_id": "IntakeTextAgent",  "intent": "Ingest the extension request."},
            {"agent_id": "IntakeVideoAgent", "intent": "Ingest the source clip."},
            {"agent_id": "VideoExtendAgent", "intent": "Extend the confession scene."},
            {"agent_id": "CompositorAgent",  "intent": "Compose the extended clip as the final deliverable."},
        ],
    },
    # 4. Missing IntakeText
    {
        "user_goal": "把这段短剧整体转成日漫画风",
        "chosen_rationale": (
            "用户上传视频 + 纯风格迁移需求。任何用户 text 指令都要先 IntakeText 落文 —— "
            "这是框架硬约束。IntakeVideo 进素材，StyleTransfer 转画风，done。"
        ),
        "chosen_plan": [
            {"agent_id": "IntakeTextAgent",    "intent": "Ingest the style-transfer request."},
            {"agent_id": "IntakeVideoAgent",   "intent": "Ingest the uploaded drama."},
            {"agent_id": "StyleTransferAgent", "intent": "Convert to Japanese anime painting style."},
        ],
        "rejected_rationale": (
            "用户这次上传主要是视频素材，文字指令只是简短的风格切换要求，"
            "IntakeText 对这种纯视频编辑场景可以省略，直接 IntakeVideo 进料然后风格迁移，流水线更精简。"
            "省去 IntakeText 还能少占一段 workspace artifact，下游召回的噪声更少，整体延迟也更低。"
        ),
        "rejected_plan": [
            {"agent_id": "IntakeVideoAgent",   "intent": "Ingest the uploaded drama."},
            {"agent_id": "StyleTransferAgent", "intent": "Convert to Japanese anime painting style."},
        ],
    },
    # 5. Compositor overshoot on Highlight reel
    {
        "user_goal": "从这部爆款短剧里剪出男女主的高甜互动瞬间做推广短视频",
        "chosen_rationale": (
            "用户要的是剪出高光片段做推广物料 —— Highlight 的输出本身就是成片物料，"
            "不需要再 Compositor 叠任何东西。链止于 Highlight。"
        ),
        "chosen_plan": [
            {"agent_id": "IntakeTextAgent",    "intent": "Ingest the highlight-reel request."},
            {"agent_id": "IntakeVideoAgent",   "intent": "Ingest the hit mini-drama."},
            {"agent_id": "VideoAnalysisAgent", "intent": "Identify the high-chemistry interaction moments."},
            {"agent_id": "HighlightAgent",     "intent": "Cut a promotional reel of sweet romantic interactions."},
        ],
        "rejected_rationale": (
            "剪出高光片段后用 Compositor 合成为最终可交付的宣传片。"
        ),
        "rejected_plan": [
            {"agent_id": "IntakeTextAgent",    "intent": "Ingest the highlight-reel request."},
            {"agent_id": "IntakeVideoAgent",   "intent": "Ingest the hit mini-drama."},
            {"agent_id": "VideoAnalysisAgent", "intent": "Identify high-chemistry interaction moments."},
            {"agent_id": "HighlightAgent",     "intent": "Cut a romantic-interaction reel."},
            {"agent_id": "CompositorAgent",   "intent": "Finalize the promotional deliverable."},
        ],
    },
]


# ---------------------------------------------------------------------------
# Emit JSONL files in TRL-native formats.
# ---------------------------------------------------------------------------

def emit():
    out_dir = Path(__file__).parent
    system_prompt = build_system_prompt()

    # SFT: messages format, TRL SFTTrainer native
    sft_path = out_dir / "samples_sft.jsonl"
    with sft_path.open("w", encoding="utf-8") as f:
        for s in SFT_SAMPLES:
            record = {
                "messages": [
                    {"role": "system",    "content": system_prompt},
                    {"role": "user",      "content": s["user_goal"]},
                    {"role": "assistant", "content": _assistant_response(s["rationale"], s["plan_steps"])},
                ]
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    # DPO: prompt / chosen / rejected triples as message lists, TRL DPOTrainer native
    dpo_path = out_dir / "samples_dpo.jsonl"
    with dpo_path.open("w", encoding="utf-8") as f:
        for p in DPO_PAIRS:
            record = {
                "prompt": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user",   "content": p["user_goal"]},
                ],
                "chosen": [
                    {"role": "assistant", "content": _assistant_response(p["chosen_rationale"], p["chosen_plan"])},
                ],
                "rejected": [
                    {"role": "assistant", "content": _assistant_response(p["rejected_rationale"], p["rejected_plan"])},
                ],
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"Wrote {sft_path.relative_to(Path.cwd())} ({len(SFT_SAMPLES)} samples)")
    print(f"Wrote {dpo_path.relative_to(Path.cwd())} ({len(DPO_PAIRS)} pairs)")


if __name__ == "__main__":
    emit()
