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
from .contracts import InputBundleV2
from .common_schema import Meta, ImageAsset, QualityScore

# -- Agent classes (convenience re-exports) --------------------------------
from .story.agent import StoryAgent
from .screenplay.agent import ScreenplayAgent
from .keyframe.agent import KeyFrameAgent
from .video.agent import VideoAgent
from .audio.agent import AudioAgent
from .univa_storyboard.agent import UnivaStoryboardAgent
from .univa_keyframe.agent import UnivaKeyFrameAgent
from .univa_video.agent import UnivaVideoAgent
from .intake.intake_text.agent import IntakeTextAgent
from .intake.intake_image.agent import IntakeImageAgent
from .intake.intake_video.agent import IntakeVideoAgent
from .intake.intake_audio.agent import IntakeAudioAgent

# -- Evaluator classes -----------------------------------------------------
from .story.evaluator import StoryEvaluator
from .screenplay.evaluator import ScreenplayEvaluator
from .keyframe.evaluator import KeyframeEvaluator
from .video.evaluator import VideoEvaluator
from .audio.evaluator import AudioEvaluator
from .univa_storyboard.evaluator import UnivaStoryboardEvaluator
from .univa_keyframe.evaluator import UnivaKeyFrameEvaluator
from .univa_video.evaluator import UnivaVideoEvaluator

# -- Descriptors -----------------------------------------------------------
from .story.descriptor import DESCRIPTOR as _story_desc
from .screenplay.descriptor import DESCRIPTOR as _screenplay_desc
from .keyframe.descriptor import DESCRIPTOR as _keyframe_desc
from .video.descriptor import DESCRIPTOR as _video_desc
from .audio.descriptor import DESCRIPTOR as _audio_desc
from .univa_storyboard.descriptor import DESCRIPTOR as _univa_storyboard_desc
from .univa_keyframe.descriptor import DESCRIPTOR as _univa_keyframe_desc
from .univa_video.descriptor import DESCRIPTOR as _univa_video_desc
from .intake.intake_text.descriptor import DESCRIPTOR as _intake_text_desc
from .intake.intake_image.descriptor import DESCRIPTOR as _intake_image_desc
from .intake.intake_video.descriptor import DESCRIPTOR as _intake_video_desc
from .intake.intake_audio.descriptor import DESCRIPTOR as _intake_audio_desc

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
        _univa_storyboard_desc,
        _univa_keyframe_desc,
        _univa_video_desc,
        _intake_text_desc,
        _intake_image_desc,
        _intake_video_desc,
        _intake_audio_desc,
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
    # Common schema
    "Meta",
    "ImageAsset",
    "QualityScore",
    # Registry
    "AGENT_REGISTRY",
    # Agent classes
    "StoryAgent",
    "ScreenplayAgent",
    "KeyFrameAgent",
    "VideoAgent",
    "AudioAgent",
    # Evaluator classes
    "StoryEvaluator",
    "ScreenplayEvaluator",
    "KeyframeEvaluator",
    "VideoEvaluator",
    "AudioEvaluator",
    # Univa agents
    "UnivaStoryboardAgent",
    "UnivaKeyFrameAgent",
    "UnivaVideoAgent",
    "UnivaStoryboardEvaluator",
    "UnivaKeyFrameEvaluator",
    "UnivaVideoEvaluator",
    # Intake agents
    "IntakeTextAgent",
    "IntakeImageAgent",
    "IntakeVideoAgent",
    "IntakeAudioAgent",
]
