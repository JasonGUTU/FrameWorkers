"""Integration test for TranscriptionAgent's full ``run()`` loop.

Closes the coverage gap that previously let a day-1 ordering bug sit
unnoticed: the LLM half (``agent.generate``) and the materializer half
(``materializer.materialize``) each had green unit tests, but nobody
ever exercised the two through ``BaseAgent.run()`` together. This test
stubs the STT service, drives ``agent.run()`` end-to-end, and asserts
the materialized output carries real segments — which only happens if
``pre_generate`` ran before the LLM loop and seeded
``raw_segments_json_text`` on ``input_data``.

Uses a FakeLLMClient that returns a deterministic cleaned transcript so
the test stays offline — no chat model, no fal.ai.
"""

from __future__ import annotations

import asyncio
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


def _resolve_project_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "agents" / "__init__.py").exists():
            return parent
    raise RuntimeError("Cannot locate project root")


_root = _resolve_project_root()
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))


class _FakeSTTService:
    def __init__(self):
        self.calls: list[str] = []

    async def transcribe(self, media_path: str):
        from inference.generation.transcription_service import (
            TranscriptionResult, TranscriptSegment,
        )
        self.calls.append(media_path)
        return TranscriptionResult(
            language="zh",
            segments=[
                TranscriptSegment(start=0.5, end=2.1, text="嗯 你好 世界"),
                TranscriptSegment(start=2.4, end=4.0, text="测试 转录"),
            ],
            full_text="嗯 你好 世界 测试 转录",
        )


class _FakeLLMClient:
    """Returns a hard-coded cleaned transcript.

    ``BaseAgent._llm_fill_full`` calls ``self.llm.chat_json(system, user,
    max_tokens=...)`` which must return a parsed dict. Shape must match
    ``TranscriptionAgentOutput`` so ``parse_output`` succeeds."""

    def __init__(self):
        self.calls: list[tuple[str, str]] = []

    async def chat_json(self, system: str, user: str, **kwargs) -> dict:
        self.calls.append((system, user))
        return {
            "content": {
                "language": "zh",
                "segments": [
                    {"segment_id": "seg_001", "start_time": 0.5, "end_time": 2.1, "text": "你好世界"},
                    {"segment_id": "seg_002", "start_time": 2.4, "end_time": 4.0, "text": "测试转录"},
                ],
                "full_text": "你好世界 测试转录",
            },
        }


def test_transcription_agent_run_end_to_end_with_pre_generate():
    from agents.base_agent import MaterializeContext
    from agents.transcription.agent import TranscriptionAgent
    from agents.transcription.materializer import TranscriptionMaterializer
    from agents.transcription.evaluator import TranscriptionEvaluator
    from agents.transcription.schema import TranscriptionAgentInput

    stt = _FakeSTTService()
    llm = _FakeLLMClient()
    agent = TranscriptionAgent(llm_client=llm)
    agent.evaluator = TranscriptionEvaluator()
    agent.materializer = TranscriptionMaterializer(transcription_service=stt)

    inp = TranscriptionAgentInput(source_media_path="/tmp/fake_audio.wav")
    ctx = MaterializeContext(
        step_id="test_step",
        typed_input=inp,
        persist_binary=lambda asset: f"/mock/{asset.sys_id}.{asset.extension}",
    )

    result = asyncio.run(agent.run(inp, materialize_ctx=ctx))

    # pre_generate fired exactly once (not per retry), seeding real
    # segments into input_data so the LLM produced a valid cleaned
    # output on the first attempt.
    assert stt.calls == ["/tmp/fake_audio.wav"]
    assert inp.raw_segments_json_text, "pre_generate must seed raw_segments_json_text"
    seeded = json.loads(inp.raw_segments_json_text)
    assert seeded["language"] == "zh"
    assert len(seeded["segments"]) == 2
    assert "你好" in seeded["segments"][0]["text"]

    # Full run() passed — this is the regression that the ordering bug
    # prevented.
    assert result.passed, f"run() failed: {result.eval_result.get('summary')}"
    assert result.attempts == 1
    assert len(result.output.content.segments) == 2
    assert result.output.content.segments[0].segment_id == "seg_001"
    assert result.output.content.full_text == "你好世界 测试转录"
