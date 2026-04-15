from __future__ import annotations

from pathlib import Path


def test_service_has_no_legacy_input_fallbacks() -> None:
    svc = Path("plan-stack-backend/src/assistant/service.py").read_text(encoding="utf-8")
    # "selected_roles" is part of the new mandatory LLM input planner contract.
    assert "\"pipeline_bundle\"" not in svc
    assert "inputs.get(\"assets\")" not in svc
    assert "collect_indexed_pipeline_assets_for_task" not in svc
    assert "_required_roles_for_agent" not in svc


def test_descriptors_use_resolved_artifacts_param() -> None:
    """After Phase 2 the agent boundary takes a plain
    ``resolved_artifacts: dict`` instead of a typed wrapper. Lock that
    parameter name across every concrete descriptor."""
    root = Path("agents")
    for path in root.rglob("descriptor.py"):
        if path == root / "descriptor.py":
            # Skip the base SubAgentDescriptor module — it defines the
            # field type, not a concrete agent build_input.
            continue
        text = path.read_text(encoding="utf-8")
        assert "resolved_artifacts" in text, (
            f"{path}: build_input must take resolved_artifacts"
        )
        assert "input_bundle_v2" not in text, (
            f"{path}: drop the legacy input_bundle_v2 parameter"
        )
        assert "pipeline_bundle" not in text
