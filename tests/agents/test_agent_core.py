# Unit tests for the agents package (migrated from agent_core)

import os
import sys
from pathlib import Path
from threading import Lock

import pytest

def _resolve_agents_project_root() -> Path:
    """Resolve the project root that contains the ``agents`` package.

    Priority:
      1. ``FRAMEWORKERS_ROOT`` env var (if valid)
      2. Walk upward from this test file until ``agents/__init__.py`` exists
    """
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


# Add project root to sys.path so ``agents`` is importable as a package.
_project_root = _resolve_agents_project_root()
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from agents.sync_adapter import (
    BaseAgent,
    AgentMetadata,
    PipelineAgentAdapter,
    _AttrDict,
)
from agents.agent_registry import AgentRegistry


# -----------------------------------------------------------------------
# Fixtures / helpers
# -----------------------------------------------------------------------

def _make_empty_registry() -> AgentRegistry:
    """Create a minimally initialized registry for isolated unit tests."""
    registry = AgentRegistry.__new__(AgentRegistry)
    registry._agents = {}
    registry._agent_classes = {}
    registry._sync_factories = {}
    registry._descriptors = {}
    registry._pipeline_llm_client = None
    registry._pipeline_init_lock = Lock()
    registry._sync_init_lock = Lock()
    return registry

class _SimpleAgent(BaseAgent):
    """Minimal agent with no evaluator."""

    def get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            id="simple_agent",
            name="Simple Agent",
            description="A simple test agent",
        )

    def execute(self, inputs):
        return {"echo": inputs.get("msg", "")}


class _ErrorAgent(BaseAgent):
    """Agent whose execute() always raises."""

    def get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            id="error_agent",
            name="Error Agent",
            description="Always raises",
        )

    def execute(self, inputs):
        raise RuntimeError("boom")


# -----------------------------------------------------------------------
# Tests: BaseAgent interface (no evaluator)
# -----------------------------------------------------------------------

class TestBaseAgent:
    def test_execute_returns_dict(self):
        agent = _SimpleAgent()
        result = agent.execute({"msg": "hello"})
        assert result == {"echo": "hello"}

    def test_metadata_populated(self):
        agent = _SimpleAgent()
        assert agent.metadata.id == "simple_agent"
        assert agent.metadata.name == "Simple Agent"

    def test_execute_exception_propagates(self):
        agent = _ErrorAgent()
        with pytest.raises(RuntimeError, match="boom"):
            agent.execute({})


# -----------------------------------------------------------------------
# Tests: AgentRegistry
# -----------------------------------------------------------------------

class TestAgentRegistry:
    def test_register_and_get(self):
        registry = _make_empty_registry()

        agent = _SimpleAgent()
        registry.register_agent(agent)

        assert registry.get_agent("simple_agent") is agent
        assert registry.get_agent("nonexistent") is None

    def test_list_agents(self):
        registry = _make_empty_registry()

        registry.register_agent(_SimpleAgent())
        assert "simple_agent" in registry.list_agents()

    def test_get_all_agents_info(self):
        registry = _make_empty_registry()

        registry.register_agent(_SimpleAgent())
        infos = registry.get_all_agents_info()
        assert len(infos) == 1
        assert infos[0]["id"] == "simple_agent"

    def test_gather_agents_info(self):
        registry = _make_empty_registry()

        registry.register_agent(_SimpleAgent())
        gathered = registry.gather_agents_info()
        assert gathered["total_agents"] == 1
        assert "simple_agent" in gathered["agent_ids"]


# -----------------------------------------------------------------------
# Tests: AgentMetadata convenience methods
# -----------------------------------------------------------------------

class TestAgentMetadataConvenience:
    def test_get_info(self):
        agent = _SimpleAgent()
        info = agent.get_info()
        assert info["id"] == "simple_agent"
        assert "created_at" in info

    def test_get_input_schema(self):
        agent = _SimpleAgent()
        assert isinstance(agent.get_input_schema(), dict)

    def test_get_output_schema(self):
        agent = _SimpleAgent()
        assert isinstance(agent.get_output_schema(), dict)

    def test_get_capabilities(self):
        agent = _SimpleAgent()
        assert isinstance(agent.get_capabilities(), list)



# -----------------------------------------------------------------------
# Tests: LLMClient import
# -----------------------------------------------------------------------

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


# -----------------------------------------------------------------------
# Tests: common_schema models
# -----------------------------------------------------------------------

class TestCommonSchema:
    def test_meta_defaults(self):
        from agents.common_schema import Meta
        m = Meta()
        assert m.schema_version == "0.3"
        assert m.language == "en"
        assert m.created_at  # should have a default timestamp

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


# -----------------------------------------------------------------------
# Tests: SubAgentDescriptor construction
# -----------------------------------------------------------------------

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

    def test_descriptor_auto_build_upstream(self):
        from agents.descriptor import SubAgentDescriptor
        desc = SubAgentDescriptor(
            agent_name="TestAgent",
            asset_key="test",
            asset_type="test_output",
            upstream_keys=["story", "screenplay"],
        )
        assets = {"story": {"title": "A"}, "screenplay": {"scenes": []}}
        upstream = desc.build_upstream(assets)
        assert upstream == {"story": {"title": "A"}, "screenplay": {"scenes": []}}

    def test_media_asset_dataclass(self):
        from agents.descriptor import MediaAsset
        holder = {"uri": ""}
        ma = MediaAsset(sys_id="img_001", data=b"\x89PNG", extension="png", uri_holder=holder)
        assert ma.sys_id == "img_001"
        assert ma.extension == "png"


# -----------------------------------------------------------------------
# Tests: Pipeline agent imports and descriptors
# -----------------------------------------------------------------------

class TestPipelineAgentImports:
    def test_story_descriptor(self):
        from agents.story.descriptor import DESCRIPTOR
        assert DESCRIPTOR.agent_name == "StoryAgent"
        assert DESCRIPTOR.asset_key == "story_blueprint"

    def test_screenplay_descriptor(self):
        from agents.screenplay.descriptor import DESCRIPTOR
        assert DESCRIPTOR.agent_name == "ScreenplayAgent"

    def test_storyboard_descriptor(self):
        from agents.storyboard.descriptor import DESCRIPTOR
        assert DESCRIPTOR.agent_name == "StoryboardAgent"

    def test_keyframe_descriptor(self):
        from agents.keyframe.descriptor import DESCRIPTOR
        assert DESCRIPTOR.agent_name == "KeyFrameAgent"
        assert DESCRIPTOR.materializer_factory is not None

    def test_video_descriptor(self):
        from agents.video.descriptor import DESCRIPTOR
        assert DESCRIPTOR.agent_name == "VideoAgent"
        assert DESCRIPTOR.materializer_factory is not None

    def test_audio_descriptor(self):
        from agents.audio.descriptor import DESCRIPTOR
        assert DESCRIPTOR.agent_name == "AudioAgent"
        assert DESCRIPTOR.materializer_factory is not None

    def test_agent_registry_dict(self):
        from agents import AGENT_REGISTRY
        assert len(AGENT_REGISTRY) == 7
        assert "StoryAgent" in AGENT_REGISTRY
        assert "KeyFrameAgent" in AGENT_REGISTRY
        assert "ExamplePipelineAgent" in AGENT_REGISTRY

    def test_agent_name_to_asset_key(self):
        from agents import AGENT_NAME_TO_ASSET_KEY
        assert AGENT_NAME_TO_ASSET_KEY["StoryAgent"] == "story_blueprint"


# -----------------------------------------------------------------------
# Tests: LLM evaluator helpers
# -----------------------------------------------------------------------

class TestLLMEvaluatorHelpers:
    def test_check_uri(self):
        from agents.base_evaluator import check_uri
        assert check_uri("") == "missing"
        assert check_uri("placeholder") == "missing"
        assert check_uri("error: timeout") == "error"
        assert check_uri("/path/to/file.png") == "success"


# -----------------------------------------------------------------------
# Tests: PipelineAgentAdapter
# -----------------------------------------------------------------------

class TestPipelineAgentAdapter:
    def test_adapter_metadata_from_descriptor(self):
        from agents.sync_adapter import PipelineAgentAdapter
        from agents.descriptor import SubAgentDescriptor

        desc = SubAgentDescriptor(
            agent_name="TestPipelineAgent",
            asset_key="test_output",
            asset_type="test_type",
            catalog_entry="A test pipeline agent for unit testing.",
        )
        adapter = PipelineAgentAdapter(desc)
        assert adapter.metadata.id == "TestPipelineAgent"
        assert adapter.metadata.name == "TestPipelineAgent"
        assert "pipeline_agent" in adapter.metadata.capabilities
        assert "test_output" in adapter.metadata.capabilities

    def test_adapter_get_info(self):
        from agents.sync_adapter import PipelineAgentAdapter
        from agents.descriptor import SubAgentDescriptor

        desc = SubAgentDescriptor(
            agent_name="InfoAgent",
            asset_key="info",
            asset_type="info_type",
        )
        adapter = PipelineAgentAdapter(desc)
        info = adapter.get_info()
        assert info["id"] == "InfoAgent"
        assert "created_at" in info

    def test_adapter_execute_raises_without_llm_client(self):
        from agents.sync_adapter import PipelineAgentAdapter
        from agents.descriptor import SubAgentDescriptor

        desc = SubAgentDescriptor(
            agent_name="NoClientAgent",
            asset_key="nc",
            asset_type="nc_type",
        )
        adapter = PipelineAgentAdapter(desc, llm_client=None)
        with pytest.raises(RuntimeError, match="no LLMClient"):
            adapter.execute({})



# -----------------------------------------------------------------------
# Tests: Unified AgentRegistry with pipeline agents
# -----------------------------------------------------------------------

class TestUnifiedRegistry:
    def test_register_pipeline_agents(self):
        from agents.agent_registry import AgentRegistry
        from agents.descriptor import SubAgentDescriptor

        registry = _make_empty_registry()

        desc = SubAgentDescriptor(
            agent_name="PipelineTest",
            asset_key="pt",
            asset_type="pt_type",
        )
        registry.register_pipeline_agents({"PipelineTest": desc})

        assert "PipelineTest" in registry.list_agents()
        assert registry.is_pipeline_agent("PipelineTest")
        assert registry.get_descriptor("PipelineTest") is desc
        assert registry.get_agent("PipelineTest") is not None

    def test_mixed_registry(self):
        """Both sync and pipeline agents coexist in the same registry."""
        from agents.agent_registry import AgentRegistry
        from agents.descriptor import SubAgentDescriptor

        registry = _make_empty_registry()

        registry.register_agent(_SimpleAgent())

        desc = SubAgentDescriptor(
            agent_name="PipelineMixed",
            asset_key="pm",
            asset_type="pm_type",
        )
        registry.register_pipeline_agents({"PipelineMixed": desc})

        assert len(registry.list_agents()) == 2
        assert "simple_agent" in registry.list_agents()
        assert "PipelineMixed" in registry.list_agents()
        assert not registry.is_pipeline_agent("simple_agent")
        assert registry.is_pipeline_agent("PipelineMixed")

    def test_gather_includes_pipeline_agents(self):
        from agents.agent_registry import AgentRegistry
        from agents.descriptor import SubAgentDescriptor

        registry = _make_empty_registry()

        registry.register_agent(_SimpleAgent())
        desc = SubAgentDescriptor(
            agent_name="GatherTest",
            asset_key="gt",
            asset_type="gt_type",
        )
        registry.register_pipeline_agents({"GatherTest": desc})

        gathered = registry.gather_agents_info()
        assert gathered["total_agents"] == 2
        ids = gathered["agent_ids"]
        assert "simple_agent" in ids
        assert "GatherTest" in ids

    def test_pipeline_agents_from_real_registry(self):
        """AGENT_REGISTRY descriptors register successfully."""
        from agents import AGENT_REGISTRY
        from agents.agent_registry import AgentRegistry

        registry = _make_empty_registry()

        registry.register_pipeline_agents(AGENT_REGISTRY)

        assert len(registry.list_agents()) == 7
        for name in ["StoryAgent", "ScreenplayAgent", "StoryboardAgent",
                      "KeyFrameAgent", "VideoAgent", "AudioAgent",
                      "ExamplePipelineAgent"]:
            assert name in registry.list_agents()
            assert registry.is_pipeline_agent(name)
            info = registry.get_agent(name).get_info()
            assert info["id"] == name


# -----------------------------------------------------------------------
# Tests: ExamplePipelineAgent package
# -----------------------------------------------------------------------

class TestExamplePipelineAgent:
    def test_descriptor(self):
        from agents.example_agent.descriptor import DESCRIPTOR
        assert DESCRIPTOR.agent_name == "ExamplePipelineAgent"
        assert DESCRIPTOR.asset_key == "example_summary"
        assert DESCRIPTOR.materializer_factory is None

    def test_schema_input(self):
        from agents.example_agent.schema import ExamplePipelineInput
        inp = ExamplePipelineInput(
            project_id="proj_1", draft_id="d_1", source_text="hello world"
        )
        assert inp.source_text == "hello world"

    def test_schema_output_defaults(self):
        from agents.example_agent.schema import ExamplePipelineOutput
        out = ExamplePipelineOutput()
        assert out.content.title == ""
        assert out.content.word_count == 0
        assert out.meta.schema_version == "0.3"

    def test_evaluator_passes_valid_output(self):
        from agents.example_agent.evaluator import ExamplePipelineEvaluator
        from agents.example_agent.schema import ExamplePipelineOutput, SummaryContent
        evaluator = ExamplePipelineEvaluator()
        output = ExamplePipelineOutput(
            content=SummaryContent(
                title="Test",
                summary="A test summary.",
                key_points=["point one"],
                word_count=3,
            )
        )
        errors = evaluator.check_structure(output)
        assert errors == []

    def test_evaluator_catches_empty_title(self):
        from agents.example_agent.evaluator import ExamplePipelineEvaluator
        from agents.example_agent.schema import ExamplePipelineOutput, SummaryContent
        evaluator = ExamplePipelineEvaluator()
        output = ExamplePipelineOutput(
            content=SummaryContent(
                title="",
                summary="Some text",
                key_points=["p1"],
                word_count=2,
            )
        )
        errors = evaluator.check_structure(output)
        assert "title is empty" in errors

    def test_evaluator_catches_empty_key_points(self):
        from agents.example_agent.evaluator import ExamplePipelineEvaluator
        from agents.example_agent.schema import ExamplePipelineOutput, SummaryContent
        evaluator = ExamplePipelineEvaluator()
        output = ExamplePipelineOutput(
            content=SummaryContent(
                title="Title",
                summary="Some text",
                key_points=[],
                word_count=2,
            )
        )
        errors = evaluator.check_structure(output)
        assert "key_points must have at least 1 item" in errors

    def test_build_input(self):
        from agents.example_agent.descriptor import build_input
        inp = build_input("proj_1", "d_1", {"source_text": "hello"}, {})
        assert inp.source_text == "hello"
        assert inp.project_id == "proj_1"

    def test_in_agent_registry(self):
        from agents import AGENT_REGISTRY, AGENT_NAME_TO_ASSET_KEY
        assert "ExamplePipelineAgent" in AGENT_REGISTRY
        assert AGENT_NAME_TO_ASSET_KEY["ExamplePipelineAgent"] == "example_summary"


# -----------------------------------------------------------------------
# Tests: _AttrDict config wrapper
# -----------------------------------------------------------------------

class TestAttrDict:
    def test_defaults_present(self):
        cfg = _AttrDict(None)
        assert cfg.target_total_duration_sec == 60
        assert cfg.language == "en"

    def test_user_overrides(self):
        cfg = _AttrDict({"language": "zh", "custom_key": 42})
        assert cfg.language == "zh"
        assert cfg.custom_key == 42
        assert cfg.target_total_duration_sec == 60

    def test_missing_key_raises(self):
        cfg = _AttrDict(None)
        with pytest.raises(AttributeError):
            _ = cfg.nonexistent_key

    def test_underscore_attr_raises(self):
        cfg = _AttrDict({"_secret": "x"})
        with pytest.raises(AttributeError):
            _ = cfg._secret


# -----------------------------------------------------------------------
# Tests: PipelineAgentAdapter._map_inputs
# -----------------------------------------------------------------------

class TestMapInputs:
    """Verify key mapping from service.py format to pipeline format."""

    def _make_adapter(self):
        from agents.descriptor import SubAgentDescriptor
        desc = SubAgentDescriptor(
            agent_name="MapTest",
            asset_key="mt",
            asset_type="mt_type",
        )
        return PipelineAgentAdapter(desc)

    def test_service_format(self):
        adapter = self._make_adapter()
        inputs = {
            "task_id": "task_123",
            "task_description": "Make a short film",
            "workspace_context": {"story_blueprint": {"title": "Test"}},
        }
        pid, did, assets, config = adapter._map_inputs(inputs)
        assert pid == "task_123"
        assert did == "task_123"
        assert assets["draft_idea"] == "Make a short film"
        assert assets["source_text"] == "Make a short film"
        assert assets["story_blueprint"] == {"title": "Test"}
        assert config.language == "en"

    def test_pipeline_format(self):
        adapter = self._make_adapter()
        inputs = {
            "project_id": "proj_001",
            "draft_id": "draft_001",
            "assets": {"draft_idea": "A dragon story"},
            "config": {"language": "zh"},
        }
        pid, did, assets, config = adapter._map_inputs(inputs)
        assert pid == "proj_001"
        assert did == "draft_001"
        assert assets["draft_idea"] == "A dragon story"
        assert config.language == "zh"

    def test_pipeline_keys_take_priority(self):
        adapter = self._make_adapter()
        inputs = {
            "project_id": "proj_001",
            "draft_id": "draft_001",
            "task_id": "task_999",
            "assets": {"x": 1},
        }
        pid, did, assets, _ = adapter._map_inputs(inputs)
        assert pid == "proj_001"
        assert did == "draft_001"
        assert assets == {"x": 1}

    def test_empty_inputs(self):
        adapter = self._make_adapter()
        pid, did, assets, config = adapter._map_inputs({})
        assert pid == ""
        assert did == ""
        assert assets == {}
        assert config.language == "en"


# -----------------------------------------------------------------------
# Tests: PipelineAgentAdapter.execute() — full flow with mocks
# -----------------------------------------------------------------------

class TestAdapterExecuteFlow:
    """End-to-end adapter tests using mock async agents."""

    def _make_text_descriptor(self):
        """Descriptor for a text-only agent (no materializer)."""
        import asyncio
        from dataclasses import dataclass, field
        from pydantic import BaseModel
        from agents.descriptor import SubAgentDescriptor

        class _MockOutput(BaseModel):
            title: str = ""
            summary: str = ""

        class _MockInput(BaseModel):
            project_id: str = ""
            draft_id: str = ""
            draft_idea: str = ""

        class _MockAgent:
            materializer = None
            evaluator = None

            async def run(self, input_data, **kwargs):
                from agents.base_agent import ExecutionResult as LLMResult
                output = _MockOutput(
                    title="Generated",
                    summary=f"Based on: {input_data.draft_idea}",
                )
                return LLMResult(
                    output=output,
                    eval_result={"overall_pass": True},
                    passed=True,
                    attempts=1,
                )

        return SubAgentDescriptor(
            agent_name="MockTextAgent",
            asset_key="mock_text",
            asset_type="mock_text_type",
            agent_factory=lambda llm: _MockAgent(),
            evaluator_factory=lambda: None,
            build_input=lambda pid, did, assets, cfg: _MockInput(
                project_id=pid, draft_id=did,
                draft_idea=assets.get("draft_idea", ""),
            ),
        ), _MockOutput

    def _make_media_descriptor(self):
        """Descriptor for a media agent (with materializer)."""
        from pydantic import BaseModel
        from agents.descriptor import SubAgentDescriptor, BaseMaterializer, MediaAsset

        class _MockMediaOutput(BaseModel):
            image: dict = {"asset_id": "", "uri": ""}

        class _MockMediaInput(BaseModel):
            project_id: str = ""
            draft_id: str = ""

        class _MockMaterializer(BaseMaterializer):
            async def materialize(self, project_id, asset_dict, assets):
                holder = asset_dict.get("image", {})
                holder["asset_id"] = "img_test_001"
                return [
                    MediaAsset(
                        sys_id="img_test_001",
                        data=b"\x89PNG_FAKE_DATA",
                        extension="png",
                        uri_holder=holder,
                    )
                ]

        class _MockMediaAgent:
            materializer = _MockMaterializer()
            evaluator = None

            async def run(self, input_data, *, upstream=None,
                          rework_notes="", max_retries=3,
                          materialize_ctx=None):
                from agents.base_agent import ExecutionResult as LLMResult
                output = _MockMediaOutput(image={"asset_id": "", "uri": ""})

                asset_dict = output.model_dump()
                media_assets = []
                if self.materializer and materialize_ctx:
                    raw = await self.materializer.materialize(
                        materialize_ctx.project_id,
                        asset_dict,
                        materialize_ctx.assets,
                    )
                    for m in raw:
                        uri = materialize_ctx.persist_binary(m)
                        m.uri_holder["uri"] = uri
                    media_assets = list(raw)

                return LLMResult(
                    output=output,
                    eval_result={"overall_pass": True},
                    passed=True,
                    attempts=1,
                    media_assets=media_assets,
                    asset_dict=asset_dict,
                )

        return SubAgentDescriptor(
            agent_name="MockMediaAgent",
            asset_key="mock_media",
            asset_type="mock_media_type",
            agent_factory=lambda llm: _MockMediaAgent(),
            evaluator_factory=lambda: None,
            build_input=lambda pid, did, assets, cfg: _MockMediaInput(
                project_id=pid, draft_id=did,
            ),
            materializer_factory=lambda svcs: _MockMaterializer(),
        )

    # -- Text agent tests --

    def test_text_agent_service_format(self):
        from agents.llm_client import LLMClient
        desc, _ = self._make_text_descriptor()
        adapter = PipelineAgentAdapter(desc, llm_client=LLMClient(api_key="fake"))

        result = adapter.execute({
            "task_id": "task_42",
            "task_description": "A dragon story",
        })

        assert result["title"] == "Generated"
        assert "A dragon story" in result["summary"]
        assert "_media_files" not in result

    def test_text_agent_pipeline_format(self):
        from agents.llm_client import LLMClient
        desc, _ = self._make_text_descriptor()
        adapter = PipelineAgentAdapter(desc, llm_client=LLMClient(api_key="fake"))

        result = adapter.execute({
            "project_id": "proj_1",
            "draft_id": "d_1",
            "assets": {"draft_idea": "Space opera"},
            "config": {"language": "en"},
        })

        assert result["title"] == "Generated"
        assert "Space opera" in result["summary"]

    # -- Media agent tests --

    def test_media_agent_produces_files(self):
        import os
        from agents.llm_client import LLMClient
        desc = self._make_media_descriptor()
        adapter = PipelineAgentAdapter(desc, llm_client=LLMClient(api_key="fake"))

        result = adapter.execute({
            "task_id": "task_media",
            "task_description": "Generate keyframes",
        })

        assert "image" in result
        assert result["image"]["asset_id"] == "img_test_001"
        assert result["image"]["uri"].endswith(".png")

        assert "_media_files" in result
        files = result["_media_files"]
        assert "img_test_001" in files
        entry = files["img_test_001"]
        assert entry["file_content"] == b"\x89PNG_FAKE_DATA"
        assert entry["filename"] == "img_test_001.png"

    def test_media_agent_cleans_temp(self):
        import os
        from agents.llm_client import LLMClient
        desc = self._make_media_descriptor()
        adapter = PipelineAgentAdapter(desc, llm_client=LLMClient(api_key="fake"))

        result = adapter.execute({"task_id": "t1", "task_description": "test"})

        uri = result["image"]["uri"]
        temp_dir = os.path.dirname(uri)
        assert not os.path.exists(temp_dir), "temp dir should be cleaned up"

    def test_media_files_format_for_process_results(self):
        """Verify _media_files matches what service.py process_results() expects."""
        from agents.llm_client import LLMClient
        desc = self._make_media_descriptor()
        adapter = PipelineAgentAdapter(desc, llm_client=LLMClient(api_key="fake"))

        result = adapter.execute({"task_id": "t2", "task_description": "test"})

        for sys_id, entry in result["_media_files"].items():
            assert "file_content" in entry, "process_results() needs file_content"
            assert "filename" in entry
            assert isinstance(entry["file_content"], bytes)
