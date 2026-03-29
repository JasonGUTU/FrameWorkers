from __future__ import annotations

from pathlib import Path


def test_service_has_no_legacy_input_fallbacks() -> None:
    svc = Path("dynamic-task-stack/src/assistant/service.py").read_text(encoding="utf-8")
    # "selected_roles" is part of the new mandatory LLM input planner contract.
    assert "\"pipeline_bundle\"" not in svc
    assert "inputs.get(\"assets\")" not in svc
    assert "collect_indexed_pipeline_assets_for_task" not in svc
    assert "_required_roles_for_agent" not in svc


def test_descriptors_use_v2_input_name() -> None:
    root = Path("agents")
    for path in root.rglob("descriptor.py"):
        text = path.read_text(encoding="utf-8")
        assert "input_bundle_v2" in text
        assert "pipeline_bundle" not in text
