"""Unit tests for WaveSpeed video backend (mocked HTTP)."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock

import pytest

from inference.generation.video_generators.service import WavespeedVideoService


def test_wavespeed_t2v_generate_clip_happy_path(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WAVESPEED_API_KEY", "test-key")
    monkeypatch.setenv("WAVESPEED_VIDEO_PROVIDER", "bytedance")
    monkeypatch.setenv("WAVESPEED_VIDEO_T2V_MODEL", "seedance-v1-pro-t2v-480p")

    async def fake_submit(client, api_key, **kwargs):
        assert api_key == "test-key"
        return "req-123"

    async def fake_poll(client, api_key, request_id, **kwargs):
        assert request_id == "req-123"
        return "https://cdn.example/video.mp4"

    async def fake_dl(client, url):
        assert url == "https://cdn.example/video.mp4"
        return b"\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00mp42mp41"

    monkeypatch.setattr(
        "inference.generation.video_generators.service.wavespeed_submit_text_to_video",
        fake_submit,
    )
    monkeypatch.setattr(
        "inference.generation.video_generators.service.wavespeed_poll_until_done",
        fake_poll,
    )
    monkeypatch.setattr(
        "inference.generation.video_generators.service.wavespeed_download_video",
        fake_dl,
    )

    async def _run() -> None:
        svc = WavespeedVideoService()
        try:
            out = await svc.generate_clip(
                shot_id="s1",
                keyframe_images=[],
                prompt="hello",
                duration_sec=5.0,
            )
        finally:
            await svc.close()
        assert out.startswith(b"\x00\x00\x00\x18ftyp")

    asyncio.run(_run())


def test_wavespeed_i2v_uses_first_keyframe(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WAVESPEED_API_KEY", "k")
    monkeypatch.setenv("WAVESPEED_VIDEO_I2V_MODEL", "seedance-v1-pro-i2v-480p")

    submit_i2v = AsyncMock(return_value="rid-i2v")

    monkeypatch.setattr(
        "inference.generation.video_generators.service.wavespeed_submit_image_to_video",
        submit_i2v,
    )
    monkeypatch.setattr(
        "inference.generation.video_generators.service.wavespeed_poll_until_done",
        AsyncMock(return_value="https://x/v.mp4"),
    )
    monkeypatch.setattr(
        "inference.generation.video_generators.service.wavespeed_download_video",
        AsyncMock(return_value=b"mp4bytes"),
    )

    png_header = b"\x89PNG\r\n\x1a\n" + b"\x00" * 20

    async def _run() -> None:
        svc = WavespeedVideoService()
        try:
            got = await svc.generate_clip(
                shot_id="s2",
                keyframe_images=[png_header, b"ignored"],
                prompt="move",
                duration_sec=6.0,
            )
        finally:
            await svc.close()
        assert got == b"mp4bytes"
        submit_i2v.assert_awaited_once()
        call_kw = submit_i2v.await_args[1]
        assert call_kw["image_png_or_jpeg"] == png_header
        assert call_kw["duration"] == 10

    asyncio.run(_run())


def test_wavespeed_missing_key_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("WAVESPEED_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="WAVESPEED_API_KEY"):
        WavespeedVideoService()
