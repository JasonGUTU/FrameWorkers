from __future__ import annotations

import inspect
import os
import re
import sys
from pathlib import Path


def _resolve_agents_project_root() -> Path:
    env_root = os.getenv("FRAMEWORKERS_ROOT")
    if env_root:
        candidate = Path(env_root).expanduser().resolve()
        if (candidate / "agents" / "__init__.py").exists():
            return candidate

    for parent in Path(__file__).resolve().parents:
        if (parent / "agents" / "__init__.py").exists():
            return parent

    raise RuntimeError(
        "Cannot locate project root containing agents/__init__.py. "
        "Set FRAMEWORKERS_ROOT to override."
    )


_project_root = _resolve_agents_project_root()
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))


from agents import AGENT_REGISTRY


_ASSET_GET_PATTERN = re.compile(r'assets\.get\(\s*["\']([^"\']+)["\']')


def _extract_asset_get_keys(build_input_callable) -> set[str]:
    source = inspect.getsource(build_input_callable)
    return set(_ASSET_GET_PATTERN.findall(source))


def test_descriptor_build_input_uses_literal_asset_keys():
    violations: list[str] = []
    for agent_id, descriptor in AGENT_REGISTRY.items():
        build_input = getattr(descriptor, "build_input", None)
        if build_input is None:
            continue
        used_keys = _extract_asset_get_keys(build_input)
        for key in used_keys:
            if not key.strip():
                violations.append(f"{agent_id}: build_input reads empty assets key")
    assert not violations, "\n".join(violations)


def test_descriptor_identity_fields_are_present():
    for agent_id, descriptor in AGENT_REGISTRY.items():
        assert getattr(descriptor, "agent_id", "") == agent_id
        assert isinstance(getattr(descriptor, "asset_key", ""), str)
        assert getattr(descriptor, "asset_key", "")

