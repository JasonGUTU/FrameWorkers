"""Shared base for service-backed audio generators."""

from __future__ import annotations

import asyncio
import base64

from ...base_generator import BaseAudioGenerator
from ..service import AudioService


class BaseServiceAudioGenerator(BaseAudioGenerator):
    """Base class with common helpers for `AudioService` based generators."""

    def __init__(self, service: AudioService | None = None) -> None:
        self._service = service or AudioService()
        super().__init__()

    @staticmethod
    def to_audio_data_url(audio_bytes: bytes, fmt: str = "wav") -> str:
        return f"data:audio/{fmt};base64,{base64.b64encode(audio_bytes).decode('utf-8')}"

    def run_service_generate_speech(
        self,
        *,
        text: str,
        voice: str | None,
        response_format: str,
    ) -> bytes:
        return asyncio.run(
            self._service.generate_speech(
                text=text,
                voice=voice,
                response_format=response_format,
            )
        )
