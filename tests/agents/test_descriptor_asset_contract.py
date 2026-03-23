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


def _allowed_keys_for_descriptor(descriptor) -> set[str]:
    allowed = set(getattr(descriptor, "upstream_keys", []) or [])
    user_text_key = getattr(descriptor, "user_text_key", "") or ""
    if user_text_key:
        allowed.add(user_text_key)
    asset_key = getattr(descriptor, "asset_key", "") or ""
    if asset_key:
        allowed.add(asset_key)
    return allowed


def test_descriptor_build_input_asset_keys_are_declared():
    violations: list[str] = []

    for agent_name, descriptor in AGENT_REGISTRY.items():
        build_input = getattr(descriptor, "build_input", None)
        if build_input is None:
            continue

        used_keys = _extract_asset_get_keys(build_input)
        allowed_keys = _allowed_keys_for_descriptor(descriptor)
        undeclared = sorted(used_keys - allowed_keys)
        if undeclared:
            violations.append(
                f"{agent_name}: build_input reads undeclared assets keys {undeclared}; "
                f"allowed keys are {sorted(allowed_keys)} "
                "(must come from upstream_keys/user_text_key/asset_key)."
            )

    assert not violations, "\n".join(violations)

