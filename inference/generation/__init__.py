"""Generation modules - image/video/audio service classes.

In addition to the raw service classes this module exposes three
``select_*_service`` helpers that are the single decision point for
which media backend a sub-agent should use at runtime.

Default behaviour is **mocks-on**: ``select_*_service`` returns a
``Mock*Service`` so end-to-end pipelines can run without burning fal
credits. Set ``FW_USE_REAL_MEDIA_GEN`` to a truthy value (``1``,
``true``, ``yes``, ``on``) to opt into real providers. For video,
``FW_VIDEO_BACKEND`` then picks between ``fal`` (default), ``wavespeed``
and ``hunyuan`` (self-hosted HunyuanVideo-I2V FastAPI server, requires
``HUNYUAN_VIDEO_ENDPOINT_URL``).

This file is the **only** place that knows about the
``FW_USE_REAL_MEDIA_GEN`` and ``FW_VIDEO_BACKEND`` environment variables.
Sub-agent descriptors call ``select_*_service`` from their
``service_factories`` lambdas; the assistant layer never inspects the
choice and never holds an override map.
"""

import os

from .image_generators.service import (
    FalImageService,
    GeminiImageService,
    ImageService,
    MockImageService,
)
from .video_generators.service import (
    FalVideoService,
    HunyuanVideoService,
    MockVideoService,
    VideoService,
    WavespeedVideoService,
)
from .audio_generators.service import AudioService, FalAudioService, MockAudioService
from .compositor_service import CompositorService, MockCompositorService
from .transcription_service import FalTranscriptionService, MockTranscriptionService
from .video_edit_service import VideoEditService, MockVideoEditService, FalVideoEditService


def _env_truthy(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "on"}


def select_image_service() -> ImageService:
    """Pick the image service backend.

    Default: ``MockImageService`` (placeholder PNG, no API spend).
    Set ``FW_USE_REAL_MEDIA_GEN=1`` to use ``GeminiImageService`` (talks to
    ``gemini-2.5-flash-image`` via the CF AI Gateway native-Gemini Worker).
    """
    if _env_truthy("FW_USE_REAL_MEDIA_GEN"):
        return FalImageService()  # reverted from GeminiImageService — direct Gemini blocks zombie/revenge prompts even in English
    return MockImageService()


def select_video_service() -> VideoService:
    """Pick the video service backend.

    Default: ``MockVideoService`` (placeholder MP4 header, no fal credits).
    Set ``FW_USE_REAL_MEDIA_GEN=1`` to switch to a real provider; in that
    mode ``FW_VIDEO_BACKEND`` chooses between ``FalVideoService`` (default,
    Kling via fal.ai), ``WavespeedVideoService`` (``wavespeed``/``ws``)
    and ``HunyuanVideoService`` (``hunyuan``/``hy`` — self-hosted
    HunyuanVideo-I2V FastAPI server, requires ``HUNYUAN_VIDEO_ENDPOINT_URL``).
    """
    if not _env_truthy("FW_USE_REAL_MEDIA_GEN"):
        return MockVideoService()
    backend = os.getenv("FW_VIDEO_BACKEND", "fal").strip().lower()
    if backend in ("wavespeed", "wave_speed", "ws"):
        return WavespeedVideoService()
    if backend in ("hunyuan", "hy"):
        return HunyuanVideoService()
    return FalVideoService()


def select_audio_service() -> AudioService:
    """Pick the audio service backend.

    Default: ``MockAudioService`` (placeholder WAV header, no fal credits).
    Set ``FW_USE_REAL_MEDIA_GEN=1`` to use ``FalAudioService``.
    """
    if _env_truthy("FW_USE_REAL_MEDIA_GEN"):
        return FalAudioService()
    return MockAudioService()


def select_compositor_service() -> CompositorService:
    if _env_truthy("FW_USE_REAL_MEDIA_GEN"):
        return CompositorService()
    return MockCompositorService()


def select_transcription_service():
    if _env_truthy("FW_USE_REAL_MEDIA_GEN"):
        return FalTranscriptionService()
    return MockTranscriptionService()


def select_video_edit_service() -> VideoEditService:
    if _env_truthy("FW_USE_REAL_MEDIA_GEN"):
        return FalVideoEditService()
    return MockVideoEditService()


__all__ = [
    "FalImageService",
    "GeminiImageService",
    "ImageService",
    "MockImageService",
    "FalVideoService",
    "HunyuanVideoService",
    "WavespeedVideoService",
    "VideoService",
    "MockVideoService",
    "FalAudioService",
    "AudioService",
    "MockAudioService",
    "select_image_service",
    "select_video_service",
    "select_audio_service",
    "CompositorService",
    "MockCompositorService",
    "select_compositor_service",
    "FalTranscriptionService",
    "MockTranscriptionService",
    "select_transcription_service",
    "VideoEditService",
    "MockVideoEditService",
    "FalVideoEditService",
    "select_video_edit_service",
]
