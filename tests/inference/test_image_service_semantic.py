"""Unit tests for ImageService's prompt templating.

Covers ``_compose_generate_prompt`` and ``_compose_edit_prompt`` —
the two static methods that own every fal/Gemini-flavored prompt
string that used to live in ``agents/keyframe/materializer.py``.
"""

from __future__ import annotations

import asyncio

import pytest

from inference.generation.image_generators.service import (
    FalImageService,
    ImageService,
    MockImageService,
)
from inference.generation.image_generators.types import (
    ImageResult,
    ImageSemanticContext,
)


# ---------------------------------------------------------------------------
# _compose_generate_prompt
# ---------------------------------------------------------------------------


def test_compose_generate_prompt_includes_full_style_suffix() -> None:
    ctx = ImageSemanticContext(
        prompt_summary="A warm workshop interior, elderly craftsman at bench.",
        style_notes=["moody cinematic contrast", "warm amber key light"],
        must_avoid=["flat lighting", "washed-out colors"],
    )
    prompt = ImageService._compose_generate_prompt(ctx)

    # Body comes first, unchanged.
    assert prompt.startswith("A warm workshop interior, elderly craftsman at bench.")
    # Visual style block IS included for generate path.
    assert "Visual style: moody cinematic contrast; warm amber key light." in prompt
    # Do NOT use block is included.
    assert "Do NOT use: flat lighting; washed-out colors." in prompt
    # Suffix is separated from body by a newline.
    assert "\nVisual style:" in prompt


def test_compose_generate_prompt_empty_style_lists_leaves_no_suffix() -> None:
    ctx = ImageSemanticContext(prompt_summary="Just the summary.")
    prompt = ImageService._compose_generate_prompt(ctx)
    assert prompt == "Just the summary."


def test_compose_generate_prompt_only_must_avoid_no_visual_style() -> None:
    ctx = ImageSemanticContext(
        prompt_summary="Body.",
        must_avoid=["x"],
    )
    prompt = ImageService._compose_generate_prompt(ctx)
    assert "Visual style:" not in prompt
    assert "Do NOT use: x." in prompt


# ---------------------------------------------------------------------------
# _compose_edit_prompt
# ---------------------------------------------------------------------------


def test_compose_edit_prompt_prepends_edit_instruction_and_omits_visual_style() -> None:
    ctx = ImageSemanticContext(
        prompt_summary="Character tilts head to the right, soft rim light.",
        style_notes=["moody cinematic contrast"],
        must_avoid=["harsh neon", "choppy cuts"],
    )
    prompt = ImageService._compose_edit_prompt(ctx)

    # The edit instruction is prepended verbatim.
    assert prompt.startswith(
        "Edit the attached reference to match the text below; keep subject identity "
        "recognizable; apply lighting, framing, pose, and environment as described."
    )
    # Body follows after the blank line.
    assert "Character tilts head to the right, soft rim light." in prompt
    # Visual style block is OMITTED for edit path (reference carries style).
    assert "Visual style:" not in prompt
    # Do NOT use block is KEPT (refs don't encode avoidance).
    assert "Do NOT use: harsh neon; choppy cuts." in prompt


def test_compose_edit_prompt_no_must_avoid_leaves_no_style_suffix() -> None:
    ctx = ImageSemanticContext(
        prompt_summary="Body.",
        style_notes=["moody"],  # ignored on edit path
    )
    prompt = ImageService._compose_edit_prompt(ctx)
    assert prompt.startswith("Edit the attached reference")
    assert "Body." in prompt
    assert "Visual style:" not in prompt
    assert "Do NOT use:" not in prompt


# ---------------------------------------------------------------------------
# generate_image / edit_image wiring (mock backend)
# ---------------------------------------------------------------------------


def test_mock_generate_image_with_semantic_context_returns_composed_prompt() -> None:
    svc = MockImageService()
    ctx = ImageSemanticContext(
        prompt_summary="Body",
        style_notes=["s1"],
        must_avoid=["x"],
    )
    result = asyncio.run(svc.generate_image(semantic_context=ctx))
    assert isinstance(result, ImageResult)
    assert result.bytes  # non-empty placeholder
    assert result.resolved_prompt.startswith("Body")
    assert "Visual style: s1." in result.resolved_prompt
    assert "Do NOT use: x." in result.resolved_prompt


def test_mock_edit_image_with_semantic_context_prepends_edit_instruction() -> None:
    svc = MockImageService()
    ctx = ImageSemanticContext(prompt_summary="Body", must_avoid=["x"])
    result = asyncio.run(
        svc.edit_image(b"\x89PNG", semantic_context=ctx)
    )
    assert result.bytes
    assert result.resolved_prompt.startswith("Edit the attached reference")
    assert "Body" in result.resolved_prompt
    assert "Do NOT use: x." in result.resolved_prompt


def test_mock_generate_image_legacy_prompt_path_still_works() -> None:
    """Backward compat: callers with pre-composed prompts still get a result."""
    svc = MockImageService()
    result = asyncio.run(svc.generate_image("a hand-written prompt"))
    assert result.bytes
    assert result.resolved_prompt == "a hand-written prompt"


def test_mock_edit_image_legacy_prompt_path_still_works() -> None:
    svc = MockImageService()
    result = asyncio.run(svc.edit_image(b"\x89PNG", "a hand-written edit prompt"))
    assert result.bytes
    assert result.resolved_prompt == "a hand-written edit prompt"
