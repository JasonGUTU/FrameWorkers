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
from .common_schema import Meta, ImageAsset, QualityScore

# -- Agent classes (convenience re-exports) --------------------------------
from .story.agent import StoryAgent
from .screenplay.agent import ScreenplayAgent
from .keyframe.agent import KeyFrameAgent
from .video.agent import VideoAgent
from .brief_enricher.agent import BriefEnricherAgent
from .intake.intake_text.agent import IntakeTextAgent
from .intake.intake_image.agent import IntakeImageAgent
from .intake.intake_video.agent import IntakeVideoAgent
from .transcription.agent import TranscriptionAgent
from .translation.agent import TranslationAgent
from .subtitle.agent import SubtitleAgent
from .compositor.agent import CompositorAgent
from .style_transfer.agent import StyleTransferAgent
from .video_extend.agent import VideoExtendAgent
from .video_analysis.agent import VideoAnalysisAgent
from .highlight.agent import HighlightAgent
from .music.agent import MusicAgent
from .ambience.agent import AmbienceAgent
from .audio_mix.agent import AudioMixAgent

# -- Evaluator classes -----------------------------------------------------
from .story.evaluator import StoryEvaluator
from .screenplay.evaluator import ScreenplayEvaluator
from .keyframe.evaluator import KeyframeEvaluator
from .video.evaluator import VideoEvaluator
from .brief_enricher.evaluator import BriefEnricherEvaluator
from .transcription.evaluator import TranscriptionEvaluator
from .translation.evaluator import TranslationEvaluator
from .subtitle.evaluator import SubtitleEvaluator
from .compositor.evaluator import CompositorEvaluator
from .style_transfer.evaluator import StyleTransferEvaluator
from .video_extend.evaluator import VideoExtendEvaluator
from .video_analysis.evaluator import VideoAnalysisEvaluator
from .highlight.evaluator import HighlightEvaluator
from .music.evaluator import MusicEvaluator
from .ambience.evaluator import AmbienceEvaluator
from .audio_mix.evaluator import AudioMixEvaluator

# -- Descriptors -----------------------------------------------------------
from .story.descriptor import DESCRIPTOR as _story_desc
from .screenplay.descriptor import DESCRIPTOR as _screenplay_desc
from .keyframe.descriptor import DESCRIPTOR as _keyframe_desc
from .video.descriptor import DESCRIPTOR as _video_desc
from .brief_enricher.descriptor import DESCRIPTOR as _brief_enricher_desc
from .intake.intake_text.descriptor import DESCRIPTOR as _intake_text_desc
from .intake.intake_image.descriptor import DESCRIPTOR as _intake_image_desc
from .intake.intake_video.descriptor import DESCRIPTOR as _intake_video_desc
from .transcription.descriptor import DESCRIPTOR as _transcription_desc
from .translation.descriptor import DESCRIPTOR as _translation_desc
from .subtitle.descriptor import DESCRIPTOR as _subtitle_desc
from .compositor.descriptor import DESCRIPTOR as _compositor_desc
from .style_transfer.descriptor import DESCRIPTOR as _style_transfer_desc
from .video_extend.descriptor import DESCRIPTOR as _video_extend_desc
from .video_analysis.descriptor import DESCRIPTOR as _video_analysis_desc
from .highlight.descriptor import DESCRIPTOR as _highlight_desc
from .music.descriptor import DESCRIPTOR as _music_desc
from .ambience.descriptor import DESCRIPTOR as _ambience_desc
from .audio_mix.descriptor import DESCRIPTOR as _audio_mix_desc

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
        _brief_enricher_desc,
        _intake_text_desc,
        _intake_image_desc,
        _intake_video_desc,
        _transcription_desc,
        _translation_desc,
        _subtitle_desc,
        _compositor_desc,
        _style_transfer_desc,
        _video_extend_desc,
        _video_analysis_desc,
        _highlight_desc,
        _music_desc,
        _ambience_desc,
        _audio_mix_desc,
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
    # Evaluator classes
    "StoryEvaluator",
    "ScreenplayEvaluator",
    "KeyframeEvaluator",
    "VideoEvaluator",
    "BriefEnricherAgent",
    "BriefEnricherEvaluator",
    # Intake agents
    "IntakeTextAgent",
    "IntakeImageAgent",
    "IntakeVideoAgent",
    # New capability agents
    "TranscriptionAgent",
    "TranscriptionEvaluator",
    "TranslationAgent",
    "TranslationEvaluator",
    "SubtitleAgent",
    "SubtitleEvaluator",
    "CompositorAgent",
    "CompositorEvaluator",
    "StyleTransferAgent",
    "StyleTransferEvaluator",
    "VideoExtendAgent",
    "VideoExtendEvaluator",
    "VideoAnalysisAgent",
    "VideoAnalysisEvaluator",
    "HighlightAgent",
    "HighlightEvaluator",
    "MusicAgent",
    "MusicEvaluator",
    "AmbienceAgent",
    "AmbienceEvaluator",
    "AudioMixAgent",
    "AudioMixEvaluator",
]
