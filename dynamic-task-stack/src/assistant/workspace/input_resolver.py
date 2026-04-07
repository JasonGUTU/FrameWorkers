"""Input resolver — purely semantic, label-based artifact dispatch.

Responsibilities:
  * Parse the consumer agent's ``input_needs_description`` for
    ``[label_name] (single|collection)`` headers and their natural-
    language descriptions.
  * Render the artifact registry's caption index (also pure natural
    language) and ask an LLM to match each ``[label]`` block to the
    artifacts whose captions describe the same kind of thing.
  * Pack the LLM's selections into a ``resolved_artifacts`` dict keyed
    by **consumer-declared label name**:
      - ``(single)`` labels → one entry dict
      - ``(collection)`` labels → list of entry dicts
    Each entry: ``what / why / scope / path / mime`` (+ ``payload`` for
    JSON artifacts loaded from disk).

What it does NOT do:
  * Maintain any machine-readable type system — producers and consumers
    communicate purely through natural language captions; the LLM is
    the only translator between them.
  * Decide what to write into the registry — that's ``AssetManager``.
  * Read raw bytes for media files — only loads JSON payloads on demand.

Used by:
  * ``Workspace.resolve_inputs_for_agent`` exposes ``resolve``.
  * ``service.AssistantService._resolve_inputs_for_agent_with_llm``
    invokes it before each agent execution.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .artifact_registry import ArtifactRegistry
    from .file_manager import FileManager

logger = logging.getLogger(__name__)


# Match a label header like "[shot_stills] (collection)" or "[screenplay] (single)"
_LABEL_HEADER_RE = re.compile(
    r"^\s*\[(?P<label>[a-zA-Z_][a-zA-Z0-9_]*)\]\s*\((?P<cardinality>single|collection)\)\s*$",
    re.MULTILINE,
)


def parse_label_specs(input_needs_description: str) -> Dict[str, str]:
    """Extract {label: 'single'|'collection'} from a consumer's input_needs_description.

    Looks for header lines of the form ``[label_name] (single)`` or
    ``[label_name] (collection)``.  Labels with no matching header are
    treated as collections by default in downstream packaging.
    """
    out: Dict[str, str] = {}
    for m in _LABEL_HEADER_RE.finditer(input_needs_description or ""):
        label = m.group("label")
        card = m.group("cardinality").lower()
        out[label] = card
    return out


class InputResolver:
    """Resolve sub-agent inputs by label-based LLM semantic matching.

    Usage
    -----
    resolver = InputResolver(artifact_registry, file_manager, llm_client)
    resolved = resolver.resolve(
        agent_id="VideoAgent",
        task_id="task_1_xxx",
        input_needs_description=\"""
            [screenplay] (single)
            The unified screenplay document...

            [shot_stills] (collection)
            The actual rendered starting frame images...
        \""",
    )
    # resolved["resolved_artifacts"] is a dict keyed by the consumer's labels:
    # {
    #   "screenplay": {"path": ..., "payload": {...}, "what": ..., ...},   # single -> dict
    #   "shot_stills": [{"path": ..., "scope": "shot:sh_001", ...}, ...],  # collection -> list
    # }
    """

    def __init__(
        self,
        artifact_registry: "ArtifactRegistry",
        file_manager: "FileManager",
        llm_client: Any,
    ) -> None:
        self._registry = artifact_registry
        self._file_manager = file_manager
        self._llm = llm_client

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def resolve(
        self,
        *,
        agent_id: str,
        task_id: str,
        input_needs_description: str,
        model: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Return resolved_artifacts ready for InputBundleV2.context.

        Returned dict shape::

            {
              "resolved_artifacts": {
                  "<consumer_label>": <single entry dict> | [<entry dict>, ...],
                  ...
              },
              "selected_artifact_paths": [...],
              "rationale": "...",
            }
        """
        captions_index = self._registry.get_captions_index(task_id=task_id)

        if captions_index == "(no artifacts registered yet)":
            logger.info(
                "[InputResolver] No artifacts registered for task %s — cold start",
                task_id,
            )
            return {
                "resolved_artifacts": {},
                "selected_artifact_paths": [],
                "rationale": "no artifacts registered yet (cold start)",
            }

        cardinality_map = parse_label_specs(input_needs_description)
        if not cardinality_map:
            logger.warning(
                "[InputResolver] No [label] (single|collection) headers found "
                "in input_needs_description for %s — returning empty selection",
                agent_id,
            )
            return {
                "resolved_artifacts": {},
                "selected_artifact_paths": [],
                "rationale": "no [label] headers in input_needs_description",
            }
        labels_list = list(cardinality_map.keys())

        system_prompt = (
            "You match a sub-agent's input requirements to artifacts in an "
            "artifact registry.\n\n"
            "The sub-agent's input requirements are written as one or more "
            "[label] blocks. Each block has a header of the form\n"
            "    [label_name] (single)        -- exactly one matching artifact expected\n"
            "    [label_name] (collection)    -- zero or more matching artifacts expected\n"
            "followed by a natural-language description of what kind of artifact "
            "that label refers to.\n\n"
            "The artifact registry lists every persisted artifact with a natural-"
            "language caption (`what`, `why`, `scope`, `mime`, `path`).\n\n"
            "Your job:\n"
            "  1. Read each [label] block and understand the kind of artifact the "
            "agent is asking for in that slot.\n"
            "  2. For each registry artifact, read its `what` and `why` fields and "
            "understand the artifact's nature, role, and purpose. Do NOT match by "
            "filename, path tokens, or any keyword. Reason about meaning.\n"
            "  3. For each [label], decide which artifacts in the registry are "
            "instances of the kind described in that block.\n"
            "  4. Be inclusive for (collection) labels: include EVERY matching "
            "artifact, never just a sample.\n"
            "  5. Be exclusive for (single) labels: pick the single best matching "
            "artifact (or none if none clearly fits).\n"
            "  6. Distinguish artifacts that look superficially similar but play "
            "different roles in the pipeline (e.g. a reference image of an entity "
            "in isolation vs. a planned frame of a specific shot of the story). "
            "Use the captions, especially `why`, to decide.\n"
            "  7. Do not invent paths. Only return paths that appear verbatim in "
            "the registry.\n\n"
            "Return strict JSON only, with this shape:\n"
            "{\n"
            '  "selections": {\n'
            '    "<label_name>": ["<path_from_registry>", ...],\n'
            "    ...\n"
            "  },\n"
            '  "rationale": "<a short explanation of how you matched each label>"\n'
            "}\n"
            "Use exactly the label names from the agent's [label] headers as keys."
        )
        user_prompt = (
            f"agent_id: {agent_id}\n\n"
            f"=== AGENT INPUT NEEDS ===\n{input_needs_description}\n\n"
            f"Labels expected in your response: {labels_list}\n\n"
            f"=== ARTIFACT REGISTRY ===\n{captions_index}\n"
        )

        parsed: Optional[Dict[str, Any]] = None
        last_exc: Optional[Exception] = None
        import asyncio
        loop = asyncio.new_event_loop()
        try:
            for max_tok in (8192, 16384):
                try:
                    kwargs: Dict[str, Any] = {
                        "system_prompt": system_prompt,
                        "user_prompt": user_prompt,
                        "max_tokens": max_tok,
                        "reasoning_effort": "high",
                    }
                    if model:
                        kwargs["model"] = model
                    parsed = loop.run_until_complete(self._llm.chat_json(**kwargs))
                    break
                except Exception as exc:
                    last_exc = exc
                    continue
        finally:
            loop.close()

        if parsed is None:
            logger.warning("[InputResolver] LLM call failed: %s", last_exc)
            return {
                "resolved_artifacts": {},
                "selected_artifact_paths": [],
                "rationale": f"LLM selection failed: {last_exc}",
            }
        if not isinstance(parsed, dict):
            return {
                "resolved_artifacts": {},
                "selected_artifact_paths": [],
                "rationale": "LLM returned non-object JSON",
            }

        logger.info(
            "[InputResolver] LLM response for %s: %s",
            agent_id, json.dumps(parsed, ensure_ascii=False)[:500],
        )
        # Optional full-response dump for debugging (set FW_INPUT_RESOLVER_DEBUG_FILE)
        try:
            import os as _os
            _dbg = _os.environ.get("FW_INPUT_RESOLVER_DEBUG_FILE", "")
            if _dbg:
                with open(_dbg, "a") as _fh:
                    _fh.write(json.dumps({
                        "agent_id": agent_id,
                        "task_id": task_id,
                        "input_needs": input_needs_description,
                        "captions_index": captions_index,
                        "llm_response": parsed,
                    }, ensure_ascii=False) + "\n")
        except Exception:
            pass

        rationale = str(parsed.get("rationale") or "")
        selections_raw = parsed.get("selections") or {}
        if not isinstance(selections_raw, dict):
            return {
                "resolved_artifacts": {},
                "selected_artifact_paths": [],
                "rationale": rationale or "LLM returned no selections",
            }

        # Collect all paths the LLM picked across labels (for caching / dedup)
        all_paths: List[str] = []
        per_label_paths: Dict[str, List[str]] = {}
        for label, paths in selections_raw.items():
            if not isinstance(label, str) or not isinstance(paths, list):
                continue
            cleaned: List[str] = []
            for p in paths:
                if isinstance(p, str) and p.strip():
                    cleaned.append(p.strip())
                    if p.strip() not in all_paths:
                        all_paths.append(p.strip())
            per_label_paths[label] = cleaned

        if not per_label_paths:
            return {
                "resolved_artifacts": {},
                "selected_artifact_paths": [],
                "rationale": rationale or "LLM returned no selections",
            }

        # Resolve all selected paths to ArtifactRef objects in one registry pass
        refs = self._registry.get_by_paths(all_paths)
        path_to_ref = {r.path: r for r in refs}

        # Build final dict keyed by consumer label
        resolved: Dict[str, Any] = {}
        for label, paths in per_label_paths.items():
            entries: List[Dict[str, Any]] = []
            for p in paths:
                ref = path_to_ref.get(p)
                if ref is None:
                    logger.warning(
                        "[InputResolver] %s: selected path not in registry: %s",
                        label, p,
                    )
                    continue
                entries.append(self._build_entry(ref))
            cardinality = cardinality_map.get(label, "collection")
            if cardinality == "single":
                resolved[label] = entries[0] if entries else {}
            else:
                resolved[label] = entries

        logger.info(
            "[InputResolver] %s: resolved labels=%s",
            agent_id,
            {k: (1 if isinstance(v, dict) else len(v)) for k, v in resolved.items()},
        )

        return {
            "resolved_artifacts": resolved,
            "selected_artifact_paths": all_paths,
            "rationale": rationale,
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _build_entry(self, ref: Any) -> Dict[str, Any]:
        entry: Dict[str, Any] = {
            "what": ref.what,
            "why": ref.why,
            "scope": ref.scope,
            "path": ref.path,
            "mime": ref.mime,
        }
        if ref.mime == "application/json" or ref.path.lower().endswith(".json"):
            entry["payload"] = self._load_json(ref.path)
        return entry

    def _load_json(self, path: str) -> Optional[Dict[str, Any]]:
        try:
            raw = self._file_manager.read_binary_from_uri(path)
            if raw is None:
                return None
            data = json.loads(raw.decode("utf-8"))
            return data if isinstance(data, dict) else None
        except Exception as exc:
            logger.warning("[InputResolver] Failed to load JSON from %s: %s", path, exc)
            return None
