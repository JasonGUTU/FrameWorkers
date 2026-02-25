"""Concrete audio generator backed by OpenAI TTS service."""

from __future__ import annotations

from typing import Any, Dict

from ....base_generator import GeneratorMetadata
from ..base_service_generator import BaseServiceAudioGenerator


class OpenAITTSGenerator(BaseServiceAudioGenerator):
    """Generate speech audio via `AudioService.generate_speech()`."""

    def get_metadata(self) -> GeneratorMetadata:
        return GeneratorMetadata(
            id="openai_tts_generator",
            name="OpenAI TTS Generator",
            description="Concrete audio generator using OpenAI TTS backend",
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
        fmt = "wav" if response_format not in {"mp3", "opus", "aac", "flac", "pcm"} else response_format
        data_url = self.to_audio_data_url(audio_bytes, fmt=fmt)
        return {"audio": data_url, "metadata": {"bytes": len(audio_bytes), "format": fmt}}
