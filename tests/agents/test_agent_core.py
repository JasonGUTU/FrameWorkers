from __future__ import annotations

import os
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


from agents.agent_registry import AgentRegistry


class _DummyDescriptor:
    def __init__(self, name: str, asset_key: str = "asset", catalog_entry: str = "desc"):
        self.agent_name = name
        self.asset_key = asset_key
        self.asset_type = "dummy_asset_type"
        self.catalog_entry = catalog_entry

    def build_equipped_agent(self, llm_client):
        return {"agent_name": self.agent_name, "llm_client": llm_client}

    def build_input(self, project_id, draft_id, assets, config):
        return {"project_id": project_id, "draft_id": draft_id}

    def build_upstream(self, assets):
        return assets


class TestAgentRegistryDescriptorModel:
    def test_register_and_list_pipeline_descriptors(self):
        registry = AgentRegistry()
        descriptors = {
            "StoryAgent": _DummyDescriptor("StoryAgent", asset_key="story_blueprint"),
            "AudioAgent": _DummyDescriptor("AudioAgent", asset_key="audio_package"),
        }
        registry.register_pipeline_agents(descriptors)

        assert registry.list_agents() == ["AudioAgent", "StoryAgent"]
        assert registry.get_descriptor("StoryAgent").asset_key == "story_blueprint"
        assert registry.is_pipeline_agent("AudioAgent") is True
        assert registry.is_pipeline_agent("UnknownAgent") is False

    def test_gather_agents_info_returns_descriptor_metadata(self):
        registry = AgentRegistry()
        registry.register_pipeline_agents(
            {"StoryAgent": _DummyDescriptor("StoryAgent", asset_key="story_blueprint")}
        )

        gathered = registry.gather_agents_info()
        assert gathered["total_agents"] == 1
        assert gathered["agent_ids"] == ["StoryAgent"]
        assert "pipeline_agent" in gathered["all_capabilities"]
        assert "story_blueprint" in gathered["all_capabilities"]
        assert gathered["agents"][0]["input_schema"] == {}
        assert gathered["agents"][0]["output_schema"] == {}

    def test_get_agent_compatibility_requires_llm_client(self):
        registry = AgentRegistry()
        descriptor = _DummyDescriptor("StoryAgent")
        registry.register_pipeline_agents({"StoryAgent": descriptor}, llm_client=None)

        assert registry.get_agent("StoryAgent") is None

        fake_llm = object()
        registry.register_pipeline_agents({}, llm_client=fake_llm)
        equipped = registry.get_agent("StoryAgent")
        assert equipped["agent_name"] == "StoryAgent"
        assert equipped["llm_client"] is fake_llm

    def test_reload_clears_descriptors(self):
        registry = AgentRegistry()
        registry.register_pipeline_agents({"StoryAgent": _DummyDescriptor("StoryAgent")})
        assert registry.list_agents() == ["StoryAgent"]
        registry.reload()
        assert registry.list_agents() == []


class TestLLMClientImport:
    def test_llm_client_importable(self):
        from agents.llm_client import LLMClient

        client = LLMClient(model="test-model", api_key="fake")
        assert client.model == "test-model"
        assert client.max_tokens == 65536

    def test_chat_json_method_exists(self):
        from agents.llm_client import LLMClient
        import inspect

        assert inspect.iscoroutinefunction(LLMClient.chat_json)

    def test_chat_text_method_exists(self):
        from agents.llm_client import LLMClient
        import inspect

        assert inspect.iscoroutinefunction(LLMClient.chat_text)


class TestCommonSchema:
    def test_meta_defaults(self):
        from agents.common_schema import Meta

        m = Meta()
        assert m.schema_version == "0.3"
        assert m.language == "en"
        assert m.created_at

    def test_image_asset_defaults(self):
        from agents.common_schema import ImageAsset

        img = ImageAsset(asset_id="test_001", uri="/path/to/img.png")
        assert img.width == 1024
        assert img.height == 576
        assert img.format == "png"

    def test_duration_estimate(self):
        from agents.common_schema import DurationEstimate

        de = DurationEstimate(seconds=5.0, confidence=0.9)
        assert de.seconds == 5.0

    def test_quality_score_bounds(self):
        from agents.common_schema import QualityScore

        qs = QualityScore(score=0.85, notes=["good"])
        assert 0.0 <= qs.score <= 1.0


class TestSubAgentDescriptor:
    def test_descriptor_basic(self):
        from agents.descriptor import SubAgentDescriptor

        desc = SubAgentDescriptor(
            agent_name="TestAgent",
            asset_key="test",
            asset_type="test_output",
        )
        assert desc.agent_name == "TestAgent"
        assert desc.asset_key == "test"
        assert desc.materializer_factory is None
