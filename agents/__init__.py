"""Agents — pluggable agent framework for FrameWorkers.

Two class hierarchies coexist:

  **Sync adapter** (``sync_adapter.py``):
    ``BaseAgent`` with ``execute(Dict) -> Dict``.  Used by ``service.py``,
    ``AgentRegistry``, and ``PipelineAgentAdapter``.

  **Async pipeline agents** (``base_agent.py`` / ``base_evaluator.py``):
    ``BaseAgent`` (aliased as ``LLMBaseAgent``) with
    ``async run(InputT) -> ExecutionResult``.  Used by the 7 pipeline
    agents via ``SubAgentDescriptor``.

The ``AGENT_REGISTRY`` dict holds ``SubAgentDescriptor`` instances for
all pipeline agents.  ``get_agent_registry()`` returns the filesystem-
based ``AgentRegistry`` for simple sync agents.
"""

# -- Sync adapter layer (service.py interface) ----------------------------
from .sync_adapter import (
    BaseAgent,
    AgentMetadata,
    PipelineAgentAdapter,
)
from .agent_registry import AgentRegistry, get_agent_registry

# -- Async / LLM layer (pipeline agents) ---------------------------------
from .base_agent import BaseAgent as LLMBaseAgent
from .base_agent import MaterializeContext
from .base_agent import ExecutionResult as LLMExecutionResult
from .base_evaluator import BaseEvaluator as LLMBaseEvaluator
from .base_evaluator import check_uri
from .llm_client import LLMClient
from .descriptor import SubAgentDescriptor, BaseMaterializer, MediaAsset
from .common_schema import Meta, ImageAsset, QualityScore, AssetRef, DurationEstimate

# -- Agent classes (convenience re-exports) --------------------------------
from .story.agent import StoryAgent
from .screenplay.agent import ScreenplayAgent
from .storyboard.agent import StoryboardAgent
from .keyframe.agent import KeyFrameAgent
from .video.agent import VideoAgent
from .audio.agent import AudioAgent
from .example_agent.agent import ExamplePipelineAgent

# -- Evaluator classes -----------------------------------------------------
from .story.evaluator import StoryEvaluator
from .screenplay.evaluator import ScreenplayEvaluator
from .storyboard.evaluator import StoryboardEvaluator
from .keyframe.evaluator import KeyframeEvaluator
from .video.evaluator import VideoEvaluator
from .audio.evaluator import AudioEvaluator
from .example_agent.evaluator import ExamplePipelineEvaluator

# -- Descriptors -----------------------------------------------------------
from .story.descriptor import DESCRIPTOR as _story_desc
from .screenplay.descriptor import DESCRIPTOR as _screenplay_desc
from .storyboard.descriptor import DESCRIPTOR as _storyboard_desc
from .keyframe.descriptor import DESCRIPTOR as _keyframe_desc
from .video.descriptor import DESCRIPTOR as _video_desc
from .audio.descriptor import DESCRIPTOR as _audio_desc
from .example_agent.descriptor import DESCRIPTOR as _example_desc

# ---------------------------------------------------------------------------
# AGENT_REGISTRY — SubAgentDescriptor-based registry for pipeline agents
# ---------------------------------------------------------------------------

AGENT_REGISTRY: dict[str, SubAgentDescriptor] = {
    d.agent_name: d
    for d in [
        _story_desc,
        _screenplay_desc,
        _storyboard_desc,
        _keyframe_desc,
        _video_desc,
        _audio_desc,
        _example_desc,
    ]
}

AGENT_NAME_TO_EVALUATOR: dict[str, LLMBaseEvaluator] = {
    name: desc.evaluator_factory()
    for name, desc in AGENT_REGISTRY.items()
}

AGENT_NAME_TO_ASSET_KEY: dict[str, str] = {
    name: desc.asset_key
    for name, desc in AGENT_REGISTRY.items()
}

__all__ = [
    # Sync adapter layer
    "BaseAgent",
    "AgentMetadata",
    "PipelineAgentAdapter",
    "AgentRegistry",
    "get_agent_registry",
    # Async / LLM layer
    "LLMBaseAgent",
    "LLMExecutionResult",
    "MaterializeContext",
    "LLMBaseEvaluator",
    "check_uri",
    "LLMClient",
    "SubAgentDescriptor",
    "BaseMaterializer",
    "MediaAsset",
    # Common schema
    "Meta",
    "ImageAsset",
    "QualityScore",
    "AssetRef",
    "DurationEstimate",
    # Registry
    "AGENT_REGISTRY",
    "AGENT_NAME_TO_EVALUATOR",
    "AGENT_NAME_TO_ASSET_KEY",
    # Agent classes
    "StoryAgent",
    "ScreenplayAgent",
    "StoryboardAgent",
    "KeyFrameAgent",
    "VideoAgent",
    "AudioAgent",
    "ExamplePipelineAgent",
    # Evaluator classes
    "StoryEvaluator",
    "ScreenplayEvaluator",
    "StoryboardEvaluator",
    "KeyframeEvaluator",
    "VideoEvaluator",
    "AudioEvaluator",
    "ExamplePipelineEvaluator",
]
