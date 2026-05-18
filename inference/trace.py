"""Director→Assistant→Workspace pipeline tracer.

Dumps the 5 categories of intermediate state to disk during a run so
the data can be picked up for downstream analysis (diagrams, audits,
replay reconstruction). Always-on; controlled by ``FW_TRACE_DIR``.

Layout under ``<trace_dir>/``::

    director_plan.json                       # one-shot per user turn
    step_001_<agent_id>_<step_id_prefix>/    # one folder per agent execution
        global_memory_before.json
        input_resolver_io.json
        sub_agent_result.json
        assistant_to_director.json
        global_memory_after.json
    step_002_<agent_id>_<step_id_prefix>/
        ...

Each per-step folder reuses the same name on repeat dumps for the same
(agent_id, step_id) pair, so multiple writes for one step land together.

The step index is the count of existing ``step_*`` folders at write time.
For diagram purposes that recovers the execution order. Multi-turn runs
overwrite within the same trace dir — wipe ``_trace/`` between turns or
override ``FW_TRACE_DIR`` to isolate.

All writers swallow exceptions: tracing must never crash the pipeline.
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_REPO_ROOT = Path(__file__).resolve().parent.parent
_DEFAULT_TRACE = _REPO_ROOT / "_trace"


def _serialize_default(obj: Any) -> Any:
    """JSON fallback serializer for Pydantic / dataclass / datetime / bytes."""
    if hasattr(obj, "model_dump"):
        try:
            return obj.model_dump(mode="json")
        except Exception:
            return obj.model_dump()
    if hasattr(obj, "to_dict"):
        return obj.to_dict()
    if hasattr(obj, "__dict__"):
        return {k: v for k, v in obj.__dict__.items() if not k.startswith("_")}
    if isinstance(obj, bytes):
        return f"<bytes len={len(obj)}>"
    return str(obj)


def trace_root() -> Path:
    """Return the trace root dir, creating it if missing."""
    p = Path(os.environ.get("FW_TRACE_DIR") or _DEFAULT_TRACE)
    p.mkdir(parents=True, exist_ok=True)
    return p


def _step_dir(agent_id: str, step_id: str) -> Path:
    base = trace_root()
    short = (step_id or "")[:8] or "nostep"
    suffix = f"{agent_id}_{short}"
    for existing in base.glob(f"step_*_{suffix}"):
        if existing.is_dir():
            return existing
    idx = sum(1 for p in base.glob("step_*") if p.is_dir()) + 1
    new = base / f"step_{idx:03d}_{suffix}"
    new.mkdir(parents=True, exist_ok=True)
    return new


def _write(path: Path, data: Any) -> None:
    try:
        path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2, default=_serialize_default),
            encoding="utf-8",
        )
    except Exception as exc:
        logger.debug("trace write %s failed: %s", path, exc)


def dump_director_plan(data: Any) -> None:
    """One-shot per user turn: raw planner LLM output + parsed plan."""
    try:
        _write(trace_root() / "director_plan.json", data)
    except Exception as exc:
        logger.debug("trace dump_director_plan failed: %s", exc)


def dump_step(category: str, agent_id: str, step_id: str, data: Any) -> None:
    """Per-step dump. ``category`` becomes the filename (e.g.
    ``global_memory_before``, ``input_resolver_io``, ``sub_agent_result``,
    ``assistant_to_director``, ``global_memory_after``)."""
    try:
        _write(_step_dir(agent_id, step_id) / f"{category}.json", data)
    except Exception as exc:
        logger.debug("trace dump_step(%s) failed: %s", category, exc)
