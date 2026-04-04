"""Agents — descriptor-driven pipeline agent framework for FrameWorkers.

The ``AGENT_REGISTRY`` dict holds ``SubAgentDescriptor`` instances for all
pipeline agents. ``get_agent_registry()`` exposes descriptor metadata and
lookup for runtime orchestration.
"""

from .agent_registry import AgentRegistry, get_agent_registry

# -- Async / LLM layer (pipeline agents) ---------------------------------
from .base_agent import BaseAgent as LLMBaseAgent
from .base_agent import MaterializeContext
from .base_agent import ExecutionResult as LLMExecutionResult
from .base_evaluator import BaseEvaluator as LLMBaseEvaluator
from .base_evaluator import check_uri
from inference.clients import LLMClient
from .descriptor import SubAgentDescriptor, BaseMaterializer, MediaAsset
from .contracts import InputBundleV2, OutputEnvelopeV2, NamingSpecV2
from .common_schema import Meta, ImageAsset, QualityScore, AssetRef, DurationEstimate

# -- Agent classes (convenience re-exports) --------------------------------
from .story.agent import StoryAgent
from .screenplay.agent import ScreenplayAgent
from .keyframe.agent import KeyFrameAgent
from .video.agent import VideoAgent
from .audio.agent import AudioAgent
from .example_agent.agent import ExamplePipelineAgent

# -- Evaluator classes -----------------------------------------------------
from .story.evaluator import StoryEvaluator
from .screenplay.evaluator import ScreenplayEvaluator
from .keyframe.evaluator import KeyframeEvaluator
from .video.evaluator import VideoEvaluator
from .audio.evaluator import AudioEvaluator
from .example_agent.evaluator import ExamplePipelineEvaluator

# -- Descriptors -----------------------------------------------------------
from .story.descriptor import DESCRIPTOR as _story_desc
from .screenplay.descriptor import DESCRIPTOR as _screenplay_desc
from .keyframe.descriptor import DESCRIPTOR as _keyframe_desc
from .video.descriptor import DESCRIPTOR as _video_desc
from .audio.descriptor import DESCRIPTOR as _audio_desc
from .example_agent.descriptor import DESCRIPTOR as _example_desc

# ---------------------------------------------------------------------------
# AGENT_REGISTRY — SubAgentDescriptor-based registry for pipeline agents
# ---------------------------------------------------------------------------

AGENT_REGISTRY: dict[str, SubAgentDescriptor] = {
    d.agent_id: d
    for d in [
        _story_desc,
        _screenplay_desc,
        _keyframe_desc,
        _video_desc,
        _audio_desc,
        _example_desc,
    ]
}

__all__ = [
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
    "InputBundleV2",
    "OutputEnvelopeV2",
    "NamingSpecV2",
    # Common schema
    "Meta",
    "ImageAsset",
    "QualityScore",
    "AssetRef",
    "DurationEstimate",
    # Registry
    "AGENT_REGISTRY",
    # Agent classes
    "StoryAgent",
    "ScreenplayAgent",
    "KeyFrameAgent",
    "VideoAgent",
    "AudioAgent",
    "ExamplePipelineAgent",
    # Evaluator classes
    "StoryEvaluator",
    "ScreenplayEvaluator",
    "KeyframeEvaluator",
    "VideoEvaluator",
    "AudioEvaluator",
    "ExamplePipelineEvaluator",
]
