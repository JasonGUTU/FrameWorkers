"""Shared guidance-doc loader for sub_agents.

KeyframeAgent (storyboard planner) and ShotPromptAgent both load per-category
guidance .md to align visual styling and prompt vocabulary on the same axes.
"""
from __future__ import annotations

from pathlib import Path

from ._categories import ShotCategory


_GUIDANCE_DIR = Path(__file__).parent / "shot_prompt" / "guidance"


def load_guidance(categories: list[ShotCategory]) -> str:
    """Concat the .md guidance docs for the given categories (separated by ---)."""
    chunks: list[str] = []
    for c in categories:
        path = _GUIDANCE_DIR / f"{c.value}.md"
        chunks.append(path.read_text(encoding="utf-8"))
    return "\n\n---\n\n".join(chunks)


def active_categories_for_shot(shot) -> list[ShotCategory]:
    """Unique sorted categories across all of a shot's panels."""
    return sorted(
        {c for panel in shot.panels for c in panel.categories},
        key=lambda c: c.value,
    )
