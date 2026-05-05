#!/usr/bin/env python3
"""
Eval: InputResolver isolation test.

For each Director-routing GT plan, simulate the caption-index state as if each
step had executed, and measure how accurately InputResolver picks the correct
upstream artifact for each consumer label of the next step.

The harness skips all real sub-agent LLM calls. It builds captions via each
descriptor's own ``build_captions({})`` (empty stub — captions describe role /
vessel, not content, so empty payload is sufficient per the caption-role
principle). Only InputResolver itself actually calls an LLM.

Scoring: a label resolution is **correct** iff InputResolver picks an artifact
whose producer is in ``LABEL_PRODUCERS[consumer_agent][label_name]``. Optional
labels with no upstream yet registered in memory score as correct-by-default
(no producer in memory → resolver rightfully picks none).

Usage (from repo root):
    PYTHONPATH=. python evals/input_resolver/eval_resolver.py
    PYTHONPATH=. python evals/input_resolver/eval_resolver.py --workers 8 --name baseline
    PYTHONPATH=. python evals/input_resolver/eval_resolver.py --limit 10       # smoke

Results → Runtime/input_resolver/<timestamp>[_<name>].json
"""

from __future__ import annotations

import argparse
import json
import os
import time
import asyncio
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Dict, List, Optional, Tuple

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
DEFAULT_CASES_PATH = os.path.join(
    REPO_ROOT, "evals", "director_routing", "eval_cases.json"
)
RUNTIME_DIR = os.path.join(REPO_ROOT, "Runtime", "input_resolver")

# Make plan-stack-backend importable (hyphen in name blocks normal import)
import sys as _sys
_PKG_ROOT = os.path.join(REPO_ROOT, "plan-stack-backend")
for _p in (REPO_ROOT, _PKG_ROOT):
    if _p not in _sys.path:
        _sys.path.insert(0, _p)


# ---------------------------------------------------------------------------
# LABEL_PRODUCERS — auto-derived from AGENT_REGISTRY
# ---------------------------------------------------------------------------
#
# Instead of a hand-maintained per-(consumer, label) table that drifts every
# time an agent is added / removed / renamed, we keep one flat
# producer-type-keyed table (LABEL_TO_PRODUCERS) and build LABEL_PRODUCERS at
# module load time by walking each registered agent's SPEC.inputs.
#
# Result: GT auto-tracks the live registry. A retired agent (e.g.
# IntakeTextAgent — directory removed, gone from AGENT_REGISTRY) drops out of
# every accepted-set automatically. A newly-registered agent's labels are
# picked up the moment it appears in AGENT_REGISTRY.

# Producer-type label name → list of agents that legitimately produce that
# artifact type. The pseudo-producer "user" represents a raw upload (chat
# text → [creative_brief], image / video upload via workspace.persist_raw_upload).
LABEL_TO_PRODUCERS: Dict[str, List[str]] = {
    # Brief / story plane
    "raw_brief": ["user"],
    "creative_brief": ["BriefEnricherAgent", "user"],
    "image_descriptions": ["IntakeImageAgent"],
    "image_files": ["IntakeImageAgent", "user"],
    "story": ["StoryAgent"],
    "screenplay": ["ScreenplayAgent"],
    "reference_analysis": ["VideoAnalysisAgent"],

    # Keyframe plane
    "character_reference": ["IntakeImageAgent", "user"],
    "location_reference": ["IntakeImageAgent", "user"],
    "prop_reference": ["IntakeImageAgent", "user"],
    "style_reference": ["IntakeImageAgent", "user"],
    "keyframes_metadata": ["KeyFrameAgent"],
    "shot_stills": ["KeyFrameAgent"],

    # Video plane
    "source_video": ["IntakeVideoAgent", "user", "VideoAgent", "StyleTransferAgent", "VideoExtendAgent"],
    "source_media": [
        "IntakeVideoAgent", "user", "VideoAgent",
        "StyleTransferAgent", "VideoExtendAgent", "HighlightAgent",
    ],
    "video_analysis": ["VideoAnalysisAgent"],
    "video_package": [
        "VideoAgent", "StyleTransferAgent", "VideoExtendAgent", "HighlightAgent",
        "user", "IntakeVideoAgent",
    ],
    "video_file": [
        "VideoAgent", "StyleTransferAgent", "VideoExtendAgent", "HighlightAgent",
        "user", "IntakeVideoAgent",
    ],
    "continuation_instruction": ["BriefEnricherAgent", "user"],

    # Audio plane
    "music": ["MusicAgent"],
    "music_file": ["MusicAgent"],
    "ambience": ["AmbienceAgent"],
    "ambience_file": ["AmbienceAgent"],
    "narrator_audio": ["NarratorAgent"],
    "audio_package": ["AudioMixAgent"],
    "audio_file": ["AudioMixAgent", "NarratorAgent"],
    "source_text": ["TranscriptionAgent", "NarratorAgent"],

    # Storytelling plane
    "narration_script": ["NarrationAgent"],
    "illustration_sequence": ["IllustrationAgent"],
    "segment_timing": ["NarratorAgent"],
    "subtitle_tracks": ["TranscriptionAgent", "TranslationAgent", "NarratorAgent"],
}


def _build_label_producers() -> Dict[str, Dict[str, List[str]]]:
    """Walk every registered agent's SPEC.inputs, look up the producer set
    for each label name in LABEL_TO_PRODUCERS, drop any producer that isn't
    in AGENT_REGISTRY (the "user" pseudo-producer is always kept). Returns
    the per-(consumer, label) GT accepted set.
    """
    import importlib, pkgutil
    import agents as _agents_pkg
    from agents import AGENT_REGISTRY

    registered = set(AGENT_REGISTRY.keys())
    valid = registered | {"user"}

    out: Dict[str, Dict[str, List[str]]] = {}
    for _, modname, ispkg in pkgutil.iter_modules(_agents_pkg.__path__):
        if not ispkg:
            continue
        try:
            mod = importlib.import_module(f"agents.{modname}.descriptor")
            spec = getattr(mod, "SPEC", None)
        except Exception:
            continue
        if spec is None or spec.agent_id not in registered:
            continue
        consumer_dict: Dict[str, List[str]] = {}
        for inp in spec.inputs:
            producers = LABEL_TO_PRODUCERS.get(inp.name, [])
            consumer_dict[inp.name] = [p for p in producers if p in valid]
        out[spec.agent_id] = consumer_dict
    return out


LABEL_PRODUCERS: Dict[str, Dict[str, List[str]]] = _build_label_producers()


# ---------------------------------------------------------------------------
# FakeGlobalMemory — satisfies the two methods InputResolver calls
# ---------------------------------------------------------------------------

@dataclass
class _FakeArtifactRef:
    path: str
    caption: str
    scope: str
    mime: str = ""


@dataclass
class _FakeEntry:
    agent_id: str
    step_id: str
    created_at: datetime
    artifacts: List[_FakeArtifactRef]


class FakeGlobalMemory:
    """Drop-in replacement for GlobalMemory satisfying InputResolver's needs."""

    def __init__(self) -> None:
        self._entries: List[_FakeEntry] = []

    def register(self, agent_id: str, step_id: str, captions: Dict[str, Dict[str, str]]) -> None:
        self.register_with_producer(producer=agent_id, step_id=step_id, captions=captions)

    def register_with_producer(
        self, *, producer: str, step_id: str, captions: Dict[str, Dict[str, str]]
    ) -> None:
        arts = [
            _FakeArtifactRef(
                path=v.get("path") or f"/fake/{producer}/{k}.json",
                caption=v.get("caption", ""),
                scope=v.get("scope", "global"),
            )
            for k, v in captions.items()
        ]
        self._entries.append(
            _FakeEntry(
                agent_id=producer,
                step_id=step_id,
                created_at=datetime.now(UTC),
                artifacts=arts,
            )
        )

    def update_caption_by_path(self, path: str, *, caption: str, scope: str = None) -> bool:
        """Mirrors GlobalMemory.update_caption_by_path — walks backwards, patches most recent match."""
        for entry in reversed(self._entries):
            for ref in entry.artifacts:
                if ref.path == path:
                    ref.caption = caption
                    if scope is not None:
                        ref.scope = scope
                    return True
        return False

    def get_captions_index(self) -> Tuple[str, List[str]]:
        if not self._entries:
            return "(no artifacts registered yet)", []
        lines: List[str] = []
        paths: List[str] = []
        idx = 0
        for e in self._entries:
            date_str = e.created_at.strftime("%Y-%m-%d %H:%M")
            for ref in e.artifacts:
                caption = ref.caption or "(no caption)"
                lines.append(
                    f"#{idx}  {caption} "
                    f"Produced by {e.agent_id} on {date_str}."
                )
                paths.append(ref.path)
                idx += 1
        return "\n\n".join(lines), paths

    def get_by_paths(self, paths: List[str]) -> List[Any]:
        wanted = set(paths)
        out = []
        for e in self._entries:
            for ref in e.artifacts:
                if ref.path in wanted:
                    out.append(ref)
        return out

    def path_to_producer(self, path: str) -> Optional[str]:
        for e in self._entries:
            for ref in e.artifacts:
                if ref.path == path:
                    return e.agent_id
        return None


class _NoopFileManager:
    def read_binary_from_uri(self, path: str) -> Optional[bytes]:
        # Captions carry all the info the resolver needs; payload loading
        # is only used by descriptor.build_input (not exercised here).
        return None


# ---------------------------------------------------------------------------
# Harness core
# ---------------------------------------------------------------------------

def _pick_agent_at_slot(slot: List[str]) -> str:
    """Collapse a set-valued GT slot into one concrete agent for simulation."""
    for aid in slot:
        if aid != "done":
            return aid
    return ""


# Minimal stubs for agents whose build_captions emits sub-artifacts only
# when payload has content (cues / beds / shots etc.). Agents not listed
# here use ``{}`` which already yields the canonical-single-artifact caption.
AGENT_STUBS: Dict[str, Dict[str, Any]] = {
    "MusicAgent": {"content": {"cues": [{"cue_id": "cue_001"}]}},
    "AmbienceAgent": {"content": {"beds": [{"bed_id": "bed_001"}]}},
    "KeyFrameAgent": {
        "content": {
            "scenes": [{
                "scene_id": "sc_001",
                "shots": [{"shot_id": "sh_001", "keyframes": [{}]}],
            }],
        }
    },
    "VideoAgent": {
        "content": {
            "scenes": [{
                "scene_id": "sc_001",
                "shot_segments": [{"shot_id": "sh_001"}],
            }],
        }
    },
}


# Raw uploads that workspace.persist_raw_upload registers BEFORE any Intake
# agent runs (producer=user, caption = "Raw user upload (mime=X)."). Needed
# because downstream labels like VideoAnalysis.source_video want the raw
# file, not the Intake agent's metadata JSON.
#
# IntakeImageAgent: register ONE upload (simple baseline). BriefEnricher
# subsequently classifies it as 'character' via _update: patch (production
# behavior). Plans without BriefEnricher see the raw "Raw user upload"
# caption; resolver can't confidently place it in any role-specific slot
# which is the correct behavior.
ASSUMED_IMAGE_ROLE = "character"
RAW_UPLOAD_STUBS: Dict[str, List[Tuple[str, str, str]]] = {
    # agent_id triggering upload: [(path_key, mime, caption)]
    "IntakeVideoAgent": [("raw_video", "video/mp4", "Raw user upload (mime=video/mp4).")],
    "IntakeImageAgent": [("raw_image", "image/jpeg", "Raw user upload (mime=image/jpeg).")],
}

# BriefEnricher stub: classify the single uploaded image as the assumed role
# via _update:ref_{role}_{idx}. Harness service layer patches the existing
# caption in place, matching production.
BRIEF_ENRICHER_STUB: Dict[str, Any] = {
    "content": {
        "image_paths": ["/fake/user/raw_image.json"],
        "image_classifications": [
            {"image_index": 0, "role": ASSUMED_IMAGE_ROLE},
        ],
    }
}

# Labels that slice a single producer by fine-grained role (character vs
# location vs prop vs style). When the only available user-uploaded image
# is tagged for a different role (or no BriefEnricher classified it),
# resolver correctly returns empty for non-matching role labels. The
# upstream-exists check in scoring is too coarse for these — accept
# picked=[] as correct regardless of whether a "user" artifact exists.
ROLE_SPECIFIC_LABELS = {
    "character_reference", "location_reference",
    "prop_reference", "style_reference",
}


def _build_optional_labels() -> set:
    """Auto-derive (consumer_agent, label_name) pairs marked optional=True
    by reading each agent's ``descriptor.SPEC.inputs`` directly. Avoids the
    need to manually maintain an OPTIONAL_LABELS table in sync with
    InputLabelSpec changes."""
    import importlib, pkgutil
    import agents as _agents_pkg
    out = set()
    for _, modname, ispkg in pkgutil.iter_modules(_agents_pkg.__path__):
        if not ispkg:
            continue
        try:
            mod = importlib.import_module(f"agents.{modname}.descriptor")
            spec = getattr(mod, "SPEC", None)
            if spec is None:
                continue
            for inp in spec.inputs:
                if getattr(inp, "optional", False):
                    out.add((spec.agent_id, inp.name))
        except Exception:
            # Not all agent submodules carry a SPEC (e.g. base helpers).
            continue
    return out


OPTIONAL_LABELS = _build_optional_labels()


def _register_step(
    mem: FakeGlobalMemory,
    registry: Dict[str, Any],
    agent_id: str,
    step_idx: int,
) -> None:
    if agent_id not in registry:
        return
    # Raw upload (producer="user") — mirrors workspace.persist_raw_upload
    raws = RAW_UPLOAD_STUBS.get(agent_id, [])
    if raws:
        caps = {
            path_key: {
                "caption": caption,
                "scope": "global",
                "path": f"/fake/user/{path_key}.json",
            }
            for (path_key, _mime, caption) in raws
        }
        mem.register_with_producer(
            producer="user",
            step_id=f"upload_{step_idx}",
            captions=caps,
        )
    desc = registry[agent_id]
    stub = AGENT_STUBS.get(agent_id, {})
    if agent_id == "BriefEnricherAgent":
        stub = BRIEF_ENRICHER_STUB
    try:
        caps = desc.build_captions(agent_id, stub)
    except Exception:
        caps = {agent_id: {"caption": f"(fallback) Produced by {agent_id}", "scope": "global"}}

    # Handle _update: keys — mirror plan-stack-backend service.py's behavior:
    # patch existing artifact's caption instead of registering a new entry.
    update_keys = [k for k in caps if k.startswith("_update:")]
    for uk in update_keys:
        entry = caps.pop(uk)
        path = entry.get("path", "")
        if path:
            mem.update_caption_by_path(
                path, caption=entry.get("caption", ""), scope=entry.get("scope"),
            )
    if caps:
        mem.register(agent_id, f"step_{step_idx}", caps)


def _score_one_resolution(
    mem: FakeGlobalMemory,
    consumer_agent: str,
    resolved: Dict[str, Any],
) -> Dict[str, Any]:
    """Return label-level results + step-level aggregate."""
    label_gt = LABEL_PRODUCERS.get(consumer_agent, {})
    label_results: List[Dict[str, Any]] = []

    for label, entry in resolved.items():
        accepted = label_gt.get(label, [])
        # Extract paths from entry (single ResolvedArtifactEntry or list)
        if isinstance(entry, list):
            picked_paths = [e.path for e in entry if getattr(e, "path", "")]
        else:
            picked_paths = [entry.path] if getattr(entry, "path", "") else []

        picked_producers = [mem.path_to_producer(p) for p in picked_paths]

        if not picked_paths:
            # For role-specific labels, picked=[] is correct by default:
            # resolver can't confidently fill a role slot when the only
            # uploaded image is tagged for a different role (or unclassified).
            if label in ROLE_SPECIFIC_LABELS:
                correct = True
                verdict = "none-picked-ok"
            elif (consumer_agent, label) in OPTIONAL_LABELS:
                # Optional input labels: sub-agent has fallback when the slot
                # is empty (e.g. CompositorAgent picks illustration_sequence
                # OR video_package, never both required). Production chains
                # pass with these slots unfilled, so eval should not penalise.
                correct = True
                verdict = "none-picked-optional-ok"
            else:
                upstream_exists = any(
                    p in label_gt.get(label, [])
                    for e in mem._entries
                    for p in [e.agent_id]
                )
                correct = not upstream_exists or not accepted
                verdict = "none-picked-ok" if correct else "missing-upstream"
        else:
            # Correct iff every picked producer is in accepted set
            correct = bool(accepted) and all(p in accepted for p in picked_producers)
            verdict = "ok" if correct else "wrong-producer"

        label_results.append({
            "label": label,
            "accepted": accepted,
            "picked_producers": picked_producers,
            "correct": correct,
            "verdict": verdict,
        })

    step_correct = all(r["correct"] for r in label_results) if label_results else True
    return {
        "consumer_agent": consumer_agent,
        "step_correct": step_correct,
        "labels": label_results,
    }


async def run_one_case(
    *,
    case: Dict[str, Any],
    registry: Dict[str, Any],
    resolver_factory,
    model: Optional[str] = None,
) -> Dict[str, Any]:
    plan = [slot for slot in case["expected_chain"] if slot and slot[0] != "done"]
    concrete = [_pick_agent_at_slot(s) for s in plan]

    mem = FakeGlobalMemory()
    resolver = resolver_factory(mem)

    step_results: List[Dict[str, Any]] = []

    for k, agent_id in enumerate(concrete):
        if k > 0:
            # Resolve inputs for this consumer from the memory snapshot
            desc = registry.get(agent_id)
            if desc is None:
                step_results.append({"consumer_agent": agent_id, "step_correct": False,
                                     "labels": [], "error": "agent not registered"})
            else:
                try:
                    r = await resolver.aresolve(
                        agent_id=agent_id,
                        step_id=f"step_{k}",
                        input_needs_description=desc.input_needs_description,
                        model=model,
                    )
                    resolved = r.get("resolved_artifacts", {})
                    step_results.append(_score_one_resolution(mem, agent_id, resolved))
                except Exception as exc:
                    step_results.append({"consumer_agent": agent_id, "step_correct": False,
                                         "labels": [], "error": str(exc)})

        _register_step(mem, registry, agent_id, k + 1)

    scored_steps = [s for s in step_results if "error" not in s]
    label_total = sum(len(s["labels"]) for s in scored_steps)
    label_correct = sum(
        sum(1 for l in s["labels"] if l["correct"]) for s in scored_steps
    )
    step_total = len(scored_steps)
    step_correct = sum(1 for s in scored_steps if s["step_correct"])
    plan_correct = step_total > 0 and step_correct == step_total

    return {
        "name": case["name"],
        "user_goal": case["user_goal"][:200],
        "chain": concrete,
        "step_results": step_results,
        "label_total": label_total,
        "label_correct": label_correct,
        "step_total": step_total,
        "step_correct": step_correct,
        "plan_correct": plan_correct,
    }


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", default=DEFAULT_CASES_PATH)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--limit", type=int, default=0, help="First N cases only (0 = all)")
    parser.add_argument("--name", default="", help="Tag appended to output filename")
    parser.add_argument("--model", default=None)
    args = parser.parse_args()

    from agents import AGENT_REGISTRY
    from inference.clients import LLMClient
    from src.assistant.workspace.input_resolver import InputResolver

    registry = AGENT_REGISTRY

    with open(args.cases, "r", encoding="utf-8") as f:
        cases = json.load(f)
    if args.limit > 0:
        cases = cases[: args.limit]

    # One shared LLM client, per-call thread-safe (new event loop inside resolver)
    llm = LLMClient()

    def resolver_factory(mem: FakeGlobalMemory):
        return InputResolver(
            global_memory=mem,
            file_manager=_NoopFileManager(),
            llm_client=llm,
        )

    os.makedirs(RUNTIME_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_name = f"{ts}{'_' + args.name if args.name else ''}.json"
    out_path = os.path.join(RUNTIME_DIR, out_name)

    print(f"Cases: {len(cases)} · workers: {args.workers} · model: {args.model or 'default'}")

    # ── Parallel execution (asyncio.gather + Semaphore — single event loop
    #    avoids the cross-loop Future bug that ThreadPoolExecutor +
    #    new_event_loop hits with google.genai's cached async client) ─────────
    t0 = time.time()
    results: List[Dict[str, Any]] = []

    async def _run_one(c: Dict[str, Any], sem: asyncio.Semaphore) -> Dict[str, Any]:
        async with sem:
            try:
                return await run_one_case(
                    case=c,
                    registry=registry,
                    resolver_factory=resolver_factory,
                    model=args.model,
                )
            except Exception as exc:
                return {"name": c.get("name", "<err>"), "error": str(exc)}

    async def _run_all() -> None:
        sem = asyncio.Semaphore(args.workers)
        tasks = [asyncio.create_task(_run_one(c, sem)) for c in cases]
        done = 0
        for coro in asyncio.as_completed(tasks):
            r = await coro
            done += 1
            results.append(r)
            if "error" in r:
                print(f"[{done:>3}/{len(cases)}] ERROR {r.get('name','?')}: {r['error']}")
            else:
                mark = "✓" if r["plan_correct"] else "✗"
                print(f"[{done:>3}/{len(cases)}] {mark} "
                      f"step={r['step_correct']}/{r['step_total']} "
                      f"label={r['label_correct']}/{r['label_total']}  {r['name']}")

    asyncio.run(_run_all())

    elapsed = time.time() - t0
    results.sort(key=lambda r: r.get("name", ""))

    # Aggregate
    total_label = sum(r.get("label_total", 0) for r in results)
    correct_label = sum(r.get("label_correct", 0) for r in results)
    total_step = sum(r.get("step_total", 0) for r in results)
    correct_step = sum(r.get("step_correct", 0) for r in results)
    plan_correct = sum(1 for r in results if r.get("plan_correct"))

    summary = {
        "cases": len(results),
        "elapsed_seconds": round(elapsed, 1),
        "plan_perfect": plan_correct,
        "plan_perfect_rate": round(plan_correct / max(1, len(results)), 4),
        "step_correct": correct_step,
        "step_total": total_step,
        "step_accuracy": round(correct_step / max(1, total_step), 4),
        "label_correct": correct_label,
        "label_total": total_label,
        "label_accuracy": round(correct_label / max(1, total_label), 4),
        "model": args.model or "default",
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"summary": summary, "results": results}, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 72)
    print(f"Elapsed:           {summary['elapsed_seconds']}s")
    print(f"Plan-perfect:      {summary['plan_perfect']}/{summary['cases']} "
          f"({100 * summary['plan_perfect_rate']:.1f}%)")
    print(f"Step accuracy:     {summary['step_correct']}/{summary['step_total']} "
          f"({100 * summary['step_accuracy']:.1f}%)")
    print(f"Label accuracy:    {summary['label_correct']}/{summary['label_total']} "
          f"({100 * summary['label_accuracy']:.1f}%)")
    print(f"Output:            {out_path}")


if __name__ == "__main__":
    main()
