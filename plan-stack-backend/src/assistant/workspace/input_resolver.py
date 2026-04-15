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
      - ``(single)`` labels → one ``ResolvedArtifactEntry``
      - ``(collection)`` labels → list of ``ResolvedArtifactEntry``
    Each entry carries ``caption / scope / path / mime`` (and
    ``payload`` for JSON artifacts loaded from disk). The shared
    ``ResolvedArtifactEntry`` class lives in ``agents.common_schema``
    and is the single point of truth for the cross-agent entry shape.

What it does NOT do:
  * Maintain any machine-readable type system — producers and consumers
    communicate purely through natural language captions; the LLM is
    the only translator between them.
  * Decide what to write into the registry — that's ``ArtifactWriter``.
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

from agents.common_schema import ResolvedArtifactEntry

if TYPE_CHECKING:
    from .global_memory import GlobalMemory
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
    resolver = InputResolver(global_memory, file_manager, llm_client)
    resolved = resolver.resolve(
        agent_id="VideoAgent",
        step_id="task_1_xxx",
        input_needs_description=\"""
            [screenplay] (single)
            The unified screenplay document...

            [shot_stills] (collection)
            The actual rendered starting frame images...
        \""",
    )
    # resolved["resolved_artifacts"] is a dict keyed by the consumer's labels:
    # {
    #   "screenplay":  ResolvedArtifactEntry(path=..., payload={...}, caption=..., ...),  # single
    #   "shot_stills": [ResolvedArtifactEntry(path=..., scope="shot:sh_001", ...), ...],  # collection
    # }
    # ``(single)`` labels with no matching artifact get an empty
    # ``ResolvedArtifactEntry()`` (all fields blank) so consumers can
    # read attributes without defensive None checks.
    """

    def __init__(
        self,
        global_memory: "GlobalMemory",
        file_manager: "FileManager",
        llm_client: Any,
    ) -> None:
        self._memory = global_memory
        self._file_manager = file_manager
        self._llm = llm_client

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def resolve(
        self,
        *,
        agent_id: str,
        step_id: str,
        input_needs_description: str,
        model: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Return the resolved_artifacts dict ready for descriptor.build_input.

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
        captions_index, id_to_path = self._memory.get_captions_index()

        if not id_to_path:
            logger.info(
                "[InputResolver] No artifacts registered (step %s) — cold start",
                step_id,
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
            "The artifact registry lists every persisted artifact with a #N id "
            "and a natural-language caption describing its type, pipeline role, "
            "and which agent produced it.\n\n"
            "Your job:\n"
            "  1. Read each [label] block and understand the kind of artifact the "
            "agent is asking for in that slot.\n"
            "  2. For each registry artifact, read its caption and understand the "
            "artifact's type, role, and purpose. Reason about meaning.\n"
            "  3. For each [label], decide which artifacts in the registry are "
            "instances of the kind described in that block.\n"
            "  4. Be inclusive for (collection) labels: include EVERY matching "
            "artifact, never just a sample.\n"
            "  5. Be exclusive for (single) labels: pick the single best matching "
            "artifact (or none if none clearly fits).\n"
            "  6. Distinguish artifacts that look superficially similar but play "
            "different roles in the pipeline (e.g. a reference image of an entity "
            "in isolation vs. a planned frame of a specific shot of the story). "
            "Use the caption to decide.\n"
            "  7. Only return #N ids that appear in the registry.\n\n"
            "Return strict JSON only, with this shape:\n"
            "{\n"
            '  "selections": {\n'
            '    "<label_name>": [0, 3, 5],\n'
            "    ...\n"
            "  },\n"
            '  "rationale": "<a short explanation of how you matched each label>"\n'
            "}\n"
            "Use exactly the label names from the agent's [label] headers as keys. "
            "Values are arrays of integer ids (the #N numbers from the registry)."
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
            agent_id, json.dumps(parsed, ensure_ascii=False),
        )
        logger.debug(
            "[InputResolver] full prompt for %s:\n%s", agent_id, user_prompt,
        )

        rationale = str(parsed.get("rationale") or "")
        selections_raw = parsed.get("selections") or {}
        if not isinstance(selections_raw, dict):
            return {
                "resolved_artifacts": {},
                "selected_artifact_paths": [],
                "rationale": rationale or "LLM returned no selections",
            }

        # Map #N ids back to paths, then resolve to ArtifactRef objects
        all_paths: List[str] = []
        per_label_paths: Dict[str, List[str]] = {}
        for label, ids in selections_raw.items():
            if not isinstance(label, str) or not isinstance(ids, list):
                continue
            paths: List[str] = []
            for raw_id in ids:
                idx = int(raw_id) if isinstance(raw_id, (int, float)) else None
                if idx is None:
                    # Backward compat: LLM might still return a path string
                    if isinstance(raw_id, str) and raw_id.strip():
                        paths.append(raw_id.strip())
                    continue
                if 0 <= idx < len(id_to_path):
                    paths.append(id_to_path[idx])
                else:
                    logger.warning(
                        "[InputResolver] %s: id #%d out of range (max %d)",
                        label, idx, len(id_to_path) - 1,
                    )
            for p in paths:
                if p not in all_paths:
                    all_paths.append(p)
            per_label_paths[label] = paths

        if not per_label_paths:
            return {
                "resolved_artifacts": {},
                "selected_artifact_paths": [],
                "rationale": rationale or "LLM returned no selections",
            }

        refs = self._memory.get_by_paths(all_paths)
        path_to_ref = {r.path: r for r in refs}

        resolved: Dict[str, Any] = {}
        for label, paths in per_label_paths.items():
            entries: List[ResolvedArtifactEntry] = []
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
                # Empty entry for missing singles so descriptors don't
                # have to branch on None vs dict vs ResolvedArtifactEntry.
                resolved[label] = entries[0] if entries else ResolvedArtifactEntry()
            else:
                resolved[label] = entries

        logger.info(
            "[InputResolver] %s: resolved labels=%s",
            agent_id,
            # (single) labels map to a ResolvedArtifactEntry (count=1);
            # (collection) labels map to list[ResolvedArtifactEntry] (count=len).
            # Previously this branched on ``isinstance(v, dict)`` which was
            # correct when resolved entries were raw dicts, but broke once the
            # resolver started producing typed ResolvedArtifactEntry objects
            # — those are neither dict nor list, so the old fallback ``len(v)``
            # blew up with "object of type 'ResolvedArtifactEntry' has no len()".
            {k: (len(v) if isinstance(v, list) else 1) for k, v in resolved.items()},
        )

        return {
            "resolved_artifacts": resolved,
            "selected_artifact_paths": all_paths,
            "rationale": rationale,
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _build_entry(self, ref: Any) -> ResolvedArtifactEntry:
        payload: Optional[Dict[str, Any]] = None
        if ref.mime == "application/json" or ref.path.lower().endswith(".json"):
            payload = self._load_json(ref.path)
        return ResolvedArtifactEntry(
            caption=ref.caption,
            scope=ref.scope,
            path=ref.path,
            mime=ref.mime,
            payload=payload,
        )

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

