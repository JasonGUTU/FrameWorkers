"""Unit tests for IntakeImageAgent.

IntakeTextAgent was retired 2026-04-23 — chat / text-plain uploads
are now persisted directly as ``[creative_brief]`` artifacts by
``workspace.persist_raw_upload`` (see its text/plain branch), so no
agent needs to intake them. IntakeImageAgent stays as a real LLM-
backed agent because it captions the uploaded image via a vision
model, which no infrastructure shortcut can replicate.

These tests cover the four intake-flow corner cases that the intake
sub-system promises to handle without crashing or losing data:

  * happy path (LLM call succeeds and returns the expected JSON)
  * fallback when the LLM call fails (network / parse / quota)
  * empty / missing input (no path, empty file, missing file on disk)
  * descriptor wiring (build_input pulls path from resolved entry)

The tests use stub LLM clients so they run offline.
"""

from __future__ import annotations

import asyncio
import json
import sys
import tempfile
from io import BytesIO
from pathlib import Path

import pytest
from PIL import Image

_repo_root = Path(__file__).resolve().parents[2]
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from agents.intake.intake_image.agent import IntakeImageAgent
from agents.intake.intake_image.evaluator import IntakeImageEvaluator
from agents.intake.intake_image.schema import IntakeImageInput, IntakeImageOutput


# ---------------------------------------------------------------------------
# Stub LLM clients
# ---------------------------------------------------------------------------


class _StubVisionLLM:
    """Stand-in for ``LLMClient.acall`` — records the multimodal payload
    and returns a canned chat-completions-style response."""

    def __init__(self, response_text: str | None = None) -> None:
        self.response_text = (
            response_text
            if response_text is not None
            else json.dumps({"visual_description": "stub vision description"})
        )
        self.last_messages: list | None = None
        self.last_kwargs: dict | None = None

    async def acall(self, messages, **kwargs):
        self.last_messages = messages
        self.last_kwargs = kwargs
        return {
            "choices": [
                {"message": {"content": self.response_text}},
            ]
        }


class _RaisingVisionLLM:
    async def acall(self, messages, **kwargs):
        raise RuntimeError("simulated vision endpoint failure")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write_png(color: tuple[int, int, int] = (255, 0, 0)) -> str:
    img = Image.new("RGB", (8, 8), color=color)
    fh = tempfile.NamedTemporaryFile("wb", suffix=".png", delete=False)
    img.save(fh, format="PNG")
    fh.close()
    return fh.name


# ---------------------------------------------------------------------------
# IntakeImageAgent
# ---------------------------------------------------------------------------


class TestIntakeImageAgent:
    def test_happy_path_carries_image_bytes_in_multimodal_message(self):
        stub = _StubVisionLLM()
        agent = IntakeImageAgent(llm_client=stub)
        path = _write_png()

        out = asyncio.run(agent.generate(
            IntakeImageInput(raw_image_path=path),
        ))

        assert isinstance(out, IntakeImageOutput)
        assert out.content.image_asset.uri == path
        assert out.content.visual_description == "stub vision description"

        # Confirm the multimodal message actually carried the image bytes.
        assert stub.last_messages is not None
        assert len(stub.last_messages) == 2
        assert stub.last_messages[0]["role"] == "system"
        user_msg = stub.last_messages[1]
        assert user_msg["role"] == "user"
        assert isinstance(user_msg["content"], list)
        text_items = [c for c in user_msg["content"] if c.get("type") == "text"]
        image_items = [c for c in user_msg["content"] if c.get("type") == "image_url"]
        assert len(text_items) == 1
        assert len(image_items) == 1
        url = image_items[0]["image_url"]["url"]
        assert url.startswith("data:image/")
        assert "base64," in url

        # JSON mode flag must be forwarded so providers that honor it use it.
        assert stub.last_kwargs.get("response_format") == {"type": "json_object"}

    def test_plain_text_response_falls_back_to_raw_text(self):
        stub = _StubVisionLLM(response_text="a wide misty forest at dawn")
        agent = IntakeImageAgent(llm_client=stub)
        path = _write_png()
        out = asyncio.run(agent.generate(
            IntakeImageInput(raw_image_path=path),
        ))
        assert out.content.visual_description == "a wide misty forest at dawn"

    def test_llm_failure_emits_fallback_caption(self):
        agent = IntakeImageAgent(llm_client=_RaisingVisionLLM())
        path = _write_png()
        out = asyncio.run(agent.generate(
            IntakeImageInput(raw_image_path=path),
        ))
        assert out.content.visual_description == ""

    def test_empty_path_returns_valid_artifact(self):
        agent = IntakeImageAgent(llm_client=_StubVisionLLM())
        out = asyncio.run(agent.generate(
            IntakeImageInput(raw_image_path=""),
        ))
        assert out.content.visual_description == ""

    def test_missing_file_emits_fallback_caption(self):
        agent = IntakeImageAgent(llm_client=_StubVisionLLM())
        out = asyncio.run(agent.generate(
            IntakeImageInput(raw_image_path="/tmp/no_such_image_xyz.png"),
        ))
        assert out.content.visual_description == ""

    def test_invalid_json_in_strict_response_falls_back(self):
        # Provider returns broken JSON — agent should treat the raw text
        # as the description rather than crashing.
        stub = _StubVisionLLM(response_text="{not really json")
        agent = IntakeImageAgent(llm_client=stub)
        path = _write_png()
        out = asyncio.run(agent.generate(
            IntakeImageInput(raw_image_path=path),
        ))
        assert out.content.visual_description == "{not really json"

    def test_full_run_passes_evaluator(self):
        agent = IntakeImageAgent(llm_client=_StubVisionLLM())
        agent.evaluator = IntakeImageEvaluator()
        path = _write_png()
        result = asyncio.run(agent.run(
            IntakeImageInput(raw_image_path=path),
        ))
        assert result.passed is True
        assert result.attempts == 1


# ---------------------------------------------------------------------------
# Descriptor wiring
# ---------------------------------------------------------------------------


def test_intake_image_descriptor_extracts_path_from_resolved_entry():
    from agents.intake.intake_image.descriptor import build_input as build_image_input
    from agents.intake.intake_image.labels import INPUT_LABEL_RAW_IMAGE_UPLOAD

    resolved = {
        INPUT_LABEL_RAW_IMAGE_UPLOAD: {
            "caption": "Raw user upload (mime=image/png). Pending intake processing — only visible to Intake* agents.",
            "scope": "raw_pending",
            "path": "/tmp/some/character.png",
            "mime": "image/png",
        }
    }
    inp = build_image_input("task_yyy", resolved)
    assert isinstance(inp, IntakeImageInput)
    assert inp.raw_image_path == "/tmp/some/character.png"
