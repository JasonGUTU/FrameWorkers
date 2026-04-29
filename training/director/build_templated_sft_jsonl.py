"""Build a TEMPLATED sft jsonl from existing raw_samples (read-only).

For each (user_goal, _, _) sample in every raw_samples shape module:
  - keep user_goal verbatim (input distribution stays diverse)
  - REPLACE rationale with one of 3 programmatically-generated skeletons
    (chain walk + reject list, no topic words from user_goal)
  - REPLACE intents with per-slot variant pulled from a 3-per-agent pool
    (chain-independent enough; specifics come from agent role only)

Variation:
  - 3 rationale skeleton variants per sample, picked by md5 hash of (slug, idx)
  - 3 intent variants per agent, picked by md5 hash of (slug, idx, slot)
  - reject-list ordering shuffled per sample (additional surface variation)

The raw_samples directory is NOT modified — the script reads each shape
module via training.director.build_sft_jsonl.load_shape_module and emits
to a new jsonl file separate from samples_sft_full.jsonl.

Output: training/director/samples_sft_full.templated.jsonl
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import random
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from training.director.gen_samples import build_system_prompt, _assistant_response  # noqa: E402
from training.director.build_sft_jsonl import load_shape_module, _normalize  # noqa: E402
from training.director.raw_samples._blueprint import SHAPES, TOTAL_TARGET  # noqa: E402


# ── x15 user_goal pool loader (raw_samples_x15/) ─────────────────────────────
# x15 modules export USER_GOALS: list[str] (lightweight schema).
# rationale / intents come 100% from the templating engine — chain is fixed by
# blueprint, so we don't need to hand-author the three-tuple per sample.

X15_DIR = REPO_ROOT / "training/director/raw_samples_x15"
X15_IDX_OFFSET = 10000  # md5 seed offset; ensures x15 entries never share a
                        # (slug, idx) hash with original raw_samples entries.


def load_x15_user_goals(slug: str) -> list[str]:
    """Import ``raw_samples_x15.shape_<slug>`` (+ ``_long``) and return merged USER_GOALS.

    Returns empty list if no x15 module exists for this shape (legitimate: x15
    rollout may be partial during incremental data authoring).
    """
    merged: list[str] = []
    for suffix in ("", "_long"):
        path = X15_DIR / f"shape_{slug}{suffix}.py"
        if not path.is_file():
            continue
        mod_name = f"training.director.raw_samples_x15.shape_{slug}{suffix}"
        if mod_name in sys.modules:
            del sys.modules[mod_name]
        mod = importlib.import_module(mod_name)
        goals = getattr(mod, "USER_GOALS", None)
        if not isinstance(goals, list):
            raise TypeError(f"{mod_name}.USER_GOALS must be list[str], got {type(goals).__name__}")
        merged.extend(g for g in goals if isinstance(g, str) and g.strip())
    return merged


# ── 20 agents × 3 chain-independent intent variants ──────────────────────────
INTENT_VARIANTS: dict[str, list[str]] = {
    "StoryAgent": [
        "Draft the story blueprint from the brief — character arc and act structure.",
        "Author the story blueprint following the brief, with a clear arc and beat structure.",
        "Outline the story blueprint per the brief — protagonist arc and pivot beats.",
    ],
    "ScreenplayAgent": [
        "Decompose the story into scenes with mood progression aligned to the brief.",
        "Break the drafted story into scene-by-scene units, preserving the brief's tonal register.",
        "Convert the story into a scene-by-scene screenplay matching the brief's register.",
    ],
    "KeyFrameAgent": [
        "Plan keyframes for the screenplay's settings, one per scene.",
        "Design keyframes from the screenplay scene by scene.",
        "Lay out keyframes for the screenplay's settings, scene-by-scene.",
    ],
    "VideoAgent": [
        "Render per-shot motion clips from the keyframes, preserving visual continuity.",
        "Produce per-shot video clips from each keyframe, holding aesthetic continuity across cuts.",
        "Animate each keyframe into a per-shot motion clip.",
    ],
    "MusicAgent": [
        "Compose the BGM the user requested, matching the brief's emotional register.",
        "Write the requested BGM, aligned to the brief's tonal cue.",
        "Generate the requested BGM, scored to the brief's mood.",
    ],
    "AmbienceAgent": [
        "Generate the ambient sound bed the brief asks for.",
        "Author the environmental ambient layer per the brief.",
        "Produce the requested ambient atmosphere as an audio bed.",
    ],
    "TranscriptionAgent": [
        "Transcribe the spoken dialogue into a timestamped subtitle track.",
        "Generate the subtitle track from the dialogue audio with per-line timestamps.",
        "Author the timestamped transcription of the spoken dialogue.",
    ],
    "TranslationAgent": [
        "Translate the source-language subtitles into the requested target language.",
        "Produce the second-language subtitle track from the source transcription.",
        "Render the bilingual translation of the subtitle track.",
    ],
    "AudioMixAgent": [
        "Mix the available audio tracks into one final mixed wav.",
        "Combine the produced audio layers into a single mixed wav.",
        "Layer the available audio tracks into the final mixed wav.",
    ],
    "CompositorAgent": [
        "Composite the final mp4 — assemble video, audio, and any subtitle / transitions into the deliverable.",
        "Mux the final mp4, combining the rendered visual track with audio and any subtitle overlay.",
        "Output the final mp4 by composing the video, audio, and subtitle / transition elements.",
    ],
    "NarrationAgent": [
        "Author the narration script from the brief — paragraph-by-paragraph story text.",
        "Draft the narration script per the brief, paragraph-by-paragraph.",
        "Write the narration script broken into reading paragraphs.",
    ],
    "IllustrationAgent": [
        "Render one still illustration per narration paragraph.",
        "Produce per-paragraph illustrations matching the narration.",
        "Generate one illustration image per paragraph of the narration.",
    ],
    "NarratorAgent": [
        "Generate the TTS narrator audio track from the narration script.",
        "Produce the spoken narrator track via TTS over the narration text.",
        "Synthesize the narrator audio track from the narration script.",
    ],
    "IntakeImageAgent": [
        "Register the uploaded image as a captioned workspace artifact.",
        "Ingest the uploaded image into the workspace with caption metadata.",
        "Persist the uploaded image into the workspace as a captioned artifact.",
    ],
    "IntakeVideoAgent": [
        "Register the uploaded video as a captioned workspace artifact.",
        "Ingest the uploaded video into the workspace with caption metadata.",
        "Persist the uploaded video into the workspace as a captioned artifact.",
    ],
    "BriefEnricherAgent": [
        "Enrich the brief by integrating descriptions of the uploaded reference images.",
        "Fold image-reference descriptions into the brief to produce an enriched creative brief.",
        "Augment the brief with the uploaded image's descriptive content.",
    ],
    "StyleTransferAgent": [
        "Apply the requested style transfer to the source video.",
        "Re-render the source video under the requested visual style.",
        "Run style transfer on the source video to match the requested aesthetic.",
    ],
    "VideoExtendAgent": [
        "Extend the source video beyond its original duration.",
        "Generate continuation footage extending the source video.",
        "Produce extended footage that continues the source video.",
    ],
    "VideoAnalysisAgent": [
        "Analyze the source video into a scene-by-scene report (genre, mood, beats, entities).",
        "Produce a scene-level analysis report of the source video for downstream reasoning.",
        "Generate a structured scene-level report of the source video.",
    ],
    "HighlightAgent": [
        "Extract the highlight moments from the analyzed video.",
        "Pick the top highlight clips from the source video using the analysis report.",
        "Select the highlight segments from the analyzed source video.",
    ],
}


# ── Per-agent reject reason (for non-chain agents in rationale) ──────────────
REJECT_REASON: dict[str, str] = {
    "StoryAgent": "no NEW film authoring requested",
    "ScreenplayAgent": "no NEW film scene-decomposition needed",
    "KeyFrameAgent": "no keyframe planning required",
    "VideoAgent": "no NEW motion-clip generation requested",
    "BriefEnricherAgent": "no image upload to enrich the brief with",
    "IntakeImageAgent": "no image upload",
    "IntakeVideoAgent": "no source clip uploaded",
    "TranscriptionAgent": "no subtitle requested",
    "TranslationAgent": "no translation / second language requested",
    "CompositorAgent": "no final mux required",
    "StyleTransferAgent": "no style transfer requested",
    "VideoExtendAgent": "no video extension requested",
    "VideoAnalysisAgent": "no source-video analysis required",
    "HighlightAgent": "not a highlight workflow",
    "MusicAgent": "no BGM requested",
    "AmbienceAgent": "no environmental layer requested",
    "AudioMixAgent": "no audio tracks to mix",
    "NarrationAgent": "not a slideshow / illustrated-storytelling format",
    "IllustrationAgent": "not a slideshow / illustrated-storytelling format",
    "NarratorAgent": "not a slideshow / illustrated-storytelling format",
}


ALL_AGENTS = list(INTENT_VARIANTS.keys())  # all 20 agents


def _format_label(chain: list[str]) -> str:
    """Format only (no input modality, no overlays). Topic-independent."""
    cs = set(chain)
    has_story = {"StoryAgent", "ScreenplayAgent", "KeyFrameAgent", "VideoAgent"}.issubset(cs)
    has_slideshow = {"NarrationAgent", "IllustrationAgent", "NarratorAgent"}.issubset(cs)
    has_style = "StyleTransferAgent" in cs
    has_extend = "VideoExtendAgent" in cs
    has_analysis = "VideoAnalysisAgent" in cs
    has_highlight = "HighlightAgent" in cs
    has_video = "IntakeVideoAgent" in cs

    if has_slideshow:
        return "illustrated storytelling slideshow"
    if has_story:
        if has_analysis:
            return "reference-video-informed cinematic mini-drama"
        if has_extend:
            return "extended-runtime cinematic mini-drama"
        return "cinematic mini-drama"
    if has_highlight:
        return "highlight reel"
    if has_style and has_extend:
        return "style-transferred + extended video cut"
    if has_style:
        return "style-transferred video cut"
    if has_extend:
        return "extended video cut"
    if has_video:
        return "modified video cut"
    return "pipeline"


def _input_label(chain: list[str]) -> str:
    """Input modality phrase ('from a text brief' / 'from an uploaded video' / etc)."""
    cs = set(chain)
    has_image = "IntakeImageAgent" in cs
    has_video = "IntakeVideoAgent" in cs
    if has_image and has_video:
        return "from an uploaded reference image + uploaded source video"
    if has_image:
        return "from a text brief + uploaded reference image"
    if has_video:
        return "from an uploaded source video"
    return "from a text brief"


def _audio_subs_feats(chain: list[str]) -> list[str]:
    """Topic-independent overlay feature list (audio / subtitle layers IN this chain)."""
    cs = set(chain)
    feats: list[str] = []
    if "MusicAgent" in cs and "AmbienceAgent" in cs:
        feats.append("BGM + ambient layer")
    elif "MusicAgent" in cs:
        feats.append("BGM")
    elif "AmbienceAgent" in cs:
        feats.append("ambient layer")
    if "TranscriptionAgent" in cs and "TranslationAgent" in cs:
        feats.append("bilingual subtitles")
    elif "TranscriptionAgent" in cs:
        feats.append("subtitles")
    elif "TranslationAgent" in cs:
        feats.append("bilingual narration track")
    return feats


def _kind_phrasings(chain: list[str]) -> list[str]:
    """Three chain-free single-sentence summaries: input + format + overlays."""
    fmt = _format_label(chain)
    feats = _audio_subs_feats(chain)
    inp = _input_label(chain)
    if feats:
        feat_str = " + ".join(feats)
        return [
            f"{fmt.capitalize()} {inp} with {feat_str} as the only added overlays.",
            f"{fmt.capitalize()} {inp}; overlays applied: {feat_str}.",
            f"{fmt.capitalize()} produced {inp}, layered with {feat_str}.",
        ]
    return [
        f"{fmt.capitalize()} {inp} with no audio / subtitle overlays.",
        f"{fmt.capitalize()} {inp}; no overlays added.",
        f"{fmt.capitalize()} produced {inp}, nothing layered on top.",
    ]


def _pick(slug: str, idx: int, key: str, n: int) -> int:
    """Deterministic per-(sample, key) variant index via md5."""
    digest = hashlib.md5(f"{slug}|{idx}|{key}".encode()).digest()
    return digest[0] % n


def _shuffled_rejects(chain: list[str], slug: str, idx: int) -> list[str]:
    """Return reject lines 'AgentName (reason)' in a deterministic shuffled order."""
    cs = set(chain)
    rejected = [a for a in ALL_AGENTS if a not in cs]
    rng = random.Random(f"{slug}|{idx}|reject_order")
    rng.shuffle(rejected)
    return [f"{a} ({REJECT_REASON[a]})" for a in rejected]


def render_rationale(slug: str, idx: int, chain: list[str]) -> str:
    """Chain-free rationale: <kind one-liner> + <reject list>.

    NEVER mentions agent names that are IN the chain (those live in plan[].agent_id);
    only the rejected agents (NOT in plan) are named, with their reject reason.
    """
    phrasings = _kind_phrasings(chain)
    rejects = _shuffled_rejects(chain, slug, idx)
    rejects_str = "; ".join(rejects)
    variant = _pick(slug, idx, "rationale", 3)
    body = phrasings[variant]
    reject_prefix = ["Reject:", "Excluded —", "Skipped:"][variant]
    return f"{body} {reject_prefix} {rejects_str}."


def render_intents(slug: str, idx: int, chain: list[str]) -> list[str]:
    """Per-slot intent: pick from each agent's variant pool by hash of (slug, idx, slot)."""
    out: list[str] = []
    for slot, agent in enumerate(chain):
        pool = INTENT_VARIANTS[agent]
        out.append(pool[_pick(slug, idx, f"intent_{slot}", len(pool))])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=None,
                    help="Output jsonl path (default depends on --include-x15)")
    ap.add_argument("--shape", default=None, help="Pilot mode: only one shape slug")
    ap.add_argument("--spot-check", type=int, default=50)
    ap.add_argument("--include-x15", action="store_true",
                    help="Also merge raw_samples_x15/ (USER_GOALS schema) into the user_goal "
                         "pool. Output defaults to samples_sft_full.templated.x15.jsonl.")
    args = ap.parse_args()

    out_root = Path(__file__).parent
    default_name = "samples_sft_full.templated.x15.jsonl" if args.include_x15 \
                   else "samples_sft_full.templated.jsonl"
    out_path = args.out if args.out else out_root / default_name

    print("Building canonical system prompt…")
    sys_prompt = build_system_prompt()
    print(f"  system prompt: {len(sys_prompt):,} chars")

    eval_path = REPO_ROOT / "evals/director_routing/eval_cases.json"
    eval_norm = {_normalize(c["user_goal"]) for c in json.loads(eval_path.read_text(encoding="utf-8"))}
    print(f"  eval-goal isolation set: {len(eval_norm)} normalized goals")

    selected = [s for s in SHAPES if args.shape in (None, s.slug)]
    if not selected:
        raise SystemExit(f"No shape matching --shape={args.shape!r}")

    records: list[dict] = []
    seen: set[str] = set()
    eval_collisions = 0
    train_collisions = 0
    per_shape: list[tuple[str, int, int]] = []

    for shape in selected:
        raw = load_shape_module(shape.slug)
        if raw is None:
            print(f"  ⚠ {shape.slug}: shape module missing, skipping")
            per_shape.append((shape.slug, shape.target_n, 0))
            continue
        kept = 0
        for idx, sample in enumerate(raw):
            goal = (sample.get("user_goal") or "").strip()
            n = _normalize(goal)
            if n in eval_norm:
                eval_collisions += 1
                continue
            if n in seen:
                train_collisions += 1
                continue
            seen.add(n)

            chain = list(shape.canonical_chain)
            rationale = render_rationale(shape.slug, idx, chain)
            intents = render_intents(shape.slug, idx, chain)
            plan = [{"agent_id": a, "intent": it} for a, it in zip(chain, intents)]
            asst = _assistant_response(rationale, plan)
            records.append({
                "messages": [
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": goal},
                    {"role": "assistant", "content": asst},
                ]
            })
            kept += 1
        per_shape.append((shape.slug, shape.target_n, kept))
        print(f"  {shape.slug:34s}  target={shape.target_n:3d}  kept={kept:3d}")

    # ── x15 user_goal pass (raw_samples_x15/) ────────────────────────────────
    x15_added_total = 0
    if args.include_x15:
        print("\n--- Merging raw_samples_x15/ user_goals ---")
        for shape in selected:
            x15_goals = load_x15_user_goals(shape.slug)
            if not x15_goals:
                print(f"  {shape.slug:34s}  (no x15 module yet — skipping)")
                continue
            chain = list(shape.canonical_chain)
            added = 0
            for offset, goal in enumerate(x15_goals):
                goal = goal.strip()
                if not goal:
                    continue
                n = _normalize(goal)
                if n in eval_norm:
                    eval_collisions += 1
                    continue
                if n in seen:
                    train_collisions += 1
                    continue
                seen.add(n)
                idx = X15_IDX_OFFSET + offset
                rationale = render_rationale(shape.slug, idx, chain)
                intents = render_intents(shape.slug, idx, chain)
                plan = [{"agent_id": a, "intent": it} for a, it in zip(chain, intents)]
                asst = _assistant_response(rationale, plan)
                records.append({
                    "messages": [
                        {"role": "system", "content": sys_prompt},
                        {"role": "user", "content": goal},
                        {"role": "assistant", "content": asst},
                    ]
                })
                added += 1
            x15_added_total += added
            print(f"  {shape.slug:34s}  x15-pool={len(x15_goals):4d}  added={added:4d}")

    print()
    print("=" * 60)
    print(f"Total records: {len(records)} (blueprint target: {TOTAL_TARGET})")
    if args.include_x15:
        print(f"  ↳ x15 contribution: +{x15_added_total}")
    if eval_collisions:
        print(f"Dropped (eval-goal collision):    {eval_collisions}")
    if train_collisions:
        print(f"Dropped (within-train duplicate): {train_collisions}")

    if not records:
        raise SystemExit("No records to write — aborting.")

    random.Random(42).shuffle(records)
    with out_path.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"\nWrote {out_path}  ({len(records)} samples)")

    # Spot-check md (50 random samples) for manual review
    spot_path = out_path.with_name(out_path.stem + ".spot_check.md")
    rng = random.Random(7)
    sample = rng.sample(records, min(args.spot_check, len(records)))
    lines = [
        f"# Templated SFT spot check — {len(sample)} of {len(records)} samples",
        "",
        "Variation comes from: 3 rationale skeletons × per-sample shuffled reject list × 3 intent variants per agent (md5-hash picked).",
        "",
        "---",
        "",
    ]
    for i, r in enumerate(sample, 1):
        u = next(m for m in r["messages"] if m["role"] == "user")["content"]
        a = next(m for m in r["messages"] if m["role"] == "assistant")["content"]
        p = json.loads(a)
        u_show = u if len(u) < 400 else u[:400] + f"... [+{len(u)-400} chars]"
        lines.append(f"## #{i}")
        lines.append(f"**user_goal** ({len(u)} chars):")
        lines.append("")
        lines.append(f"> {u_show}")
        lines.append("")
        lines.append(f"**rationale:** {p['rationale']}")
        lines.append("")
        lines.append("**plan:**")
        for step in p["plan"]:
            lines.append(f"  - `{step['agent_id']}` — {step['intent']}")
        lines.append("")
    spot_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {spot_path}  ({len(sample)} random samples)")


if __name__ == "__main__":
    main()
