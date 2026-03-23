"""Concrete audio generator backed by fal.ai TTS service."""

from __future__ import annotations

from typing import Any, Dict

from ....base_generator import GeneratorMetadata
from ...service import FalAudioService
from ..base_service_generator import BaseServiceAudioGenerator


class FalTTSGenerator(BaseServiceAudioGenerator):
    """Generate speech audio via fal.ai."""

    def __init__(self) -> None:
        super().__init__(service=FalAudioService())

    def get_metadata(self) -> GeneratorMetadata:
        return GeneratorMetadata(
            id="fal_tts_generator",
            name="fal.ai TTS Generator",
            description="Concrete audio generator using fal.ai TTS backend",
            capabilities=["text_to_speech"],
            input_schema={
                "text": {"type": "string", "required": True},
                "voice": {"type": "string", "required": False},
                "response_format": {"type": "string", "required": False, "default": "wav"},
            },
            output_schema={
                "audio": {"type": "string", "description": "Audio data URL"},
                "metadata": {"type": "object"},
            },
        )

    def generate(self, **kwargs) -> Dict[str, Any]:
        text = kwargs.get("text", "")
        voice = kwargs.get("voice")
        response_format = kwargs.get("response_format", "wav")
        audio_bytes = self.run_service_generate_speech(
            text=text,
            voice=voice,
            response_format=response_format,
        )
        data_url = self.to_audio_data_url(audio_bytes, fmt=response_format)
        return {
            "audio": data_url,
            "metadata": {"bytes": len(audio_bytes), "format": response_format, "provider": "fal.ai"},
        }
