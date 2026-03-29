"""Input bundle v2 contracts for fully decoupled artifact selection."""

from __future__ import annotations

from collections.abc import Iterator, MutableMapping
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ArtifactRefV2:
    """One artifact candidate in assistant-provided catalog."""

    artifact_id: str
    semantic_type: str
    schema_ref: str = ""
    mime: str = "application/json"
    payload: Any = None
    uri: str = ""
    provenance: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)


@dataclass
class InputBundleV2(MutableMapping[str, Any]):
    """Generic artifact bundle passed to sub-agent descriptor/builders."""

    task_id: str
    artifacts: list[ArtifactRefV2] = field(default_factory=list)
    context: dict[str, Any] = field(default_factory=dict)
    hints: dict[str, Any] = field(default_factory=dict)

    def _as_mapping(self) -> dict[str, Any]:
        out: dict[str, Any] = {}
        for art in self.artifacts:
            out[art.semantic_type] = art.payload
        out.update(self.context)
        out.update(self.hints)
        return out

    def __getitem__(self, key: str) -> Any:
        return self._as_mapping()[key]

    def __setitem__(self, key: str, value: Any) -> None:
        # Keep user/runtime overlays in hints for mutability compatibility.
        self.hints[key] = value

    def __delitem__(self, key: str) -> None:
        if key in self.hints:
            del self.hints[key]
            return
        raise KeyError(key)

    def __iter__(self) -> Iterator[str]:
        return iter(self._as_mapping())

    def __len__(self) -> int:
        return len(self._as_mapping())

@dataclass
class FrozenInputBundleV2(InputBundleV2):
    """Read-only view for descriptor/evaluator safety."""

    def __setitem__(self, key: str, value: Any) -> None:  # pragma: no cover
        raise TypeError("FrozenInputBundleV2 is read-only")

    def __delitem__(self, key: str) -> None:  # pragma: no cover
        raise TypeError("FrozenInputBundleV2 is read-only")
