"""Plan A — Screenplay as single source of truth for per-scene duration.

Unit tests verifying:

1. ``ScreenplayScene.estimated_duration_seconds`` exists and defaults to 0.0.
2. ``ScreenplayAgent``'s system prompt and output template ask the LLM
   to compute the field via ``dialogue_words/2.5 + action_shots*3.0``.
3. ``ScreenplayEvaluator`` flags any scene with shots whose
   ``estimated_duration_seconds <= 0``.
4. ``MusicAgent`` and ``AmbienceAgent`` system prompts instruct the LLM
   to READ ``estimated_duration_seconds`` from the screenplay scene
   verbatim and NOT re-derive it from word counts — the old independent
   ``words / 2.5`` formula must be gone from both.
5. ``MusicAgent`` and ``AmbienceAgent`` no longer consume a narration
   label or carry a ``narration_json_text`` input field (that was the
   abandoned Path B path).
"""

from __future__ import annotations

import sys
from pathlib import Path


def _resolve_project_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "agents" / "__init__.py").exists():
            return parent
    raise RuntimeError("Cannot locate project root")


_root = _resolve_project_root()
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))


# ═══════════════════════════════════════════════════════════════════════
# 1. Schema field
# ═══════════════════════════════════════════════════════════════════════

def test_screenplay_scene_has_estimated_duration_seconds_field():
    from agents.screenplay.schema import ScreenplayScene

    scene = ScreenplayScene()
    assert hasattr(scene, "estimated_duration_seconds")
    assert scene.estimated_duration_seconds == 0.0


def test_screenplay_scene_accepts_estimated_duration_seconds_value():
    from agents.screenplay.schema import ScreenplayScene

    scene = ScreenplayScene.model_validate(
        {"scene_id": "sc_001", "estimated_duration_seconds": 12.4}
    )
    assert scene.estimated_duration_seconds == 12.4


# ═══════════════════════════════════════════════════════════════════════
# 2. ScreenplayAgent asks the LLM to compute the field
# ═══════════════════════════════════════════════════════════════════════

def test_screenplay_system_prompt_names_the_formula_and_field():
    from agents.screenplay.agent import ScreenplayAgent

    agent = ScreenplayAgent.__new__(ScreenplayAgent)
    sp = agent.system_prompt()
    assert "estimated_duration_seconds" in sp
    assert "2.5" in sp
    assert "action_shots" in sp
    assert "SINGLE SOURCE OF TRUTH" in sp.upper().replace("  ", " ") or \
        "single source of truth" in sp.lower()


def test_screenplay_output_template_shows_estimated_duration_seconds():
    from agents.screenplay.agent import SCREENPLAY_OUTPUT_TEMPLATE

    assert "estimated_duration_seconds" in SCREENPLAY_OUTPUT_TEMPLATE


# ═══════════════════════════════════════════════════════════════════════
# 3. ScreenplayEvaluator flags bad estimated_duration_seconds
# ═══════════════════════════════════════════════════════════════════════

_MIN_SCREENPLAY = {
    "content": {
        "title": "T",
        "scenes": [{
            "scene_id": "sc_001",
            "order": 1,
            "estimated_duration_seconds": 8.0,
            "shots": [{
                "shot_id": "sh_001",
                "order": 1,
                "block_type": "dialogue",
                "character_id": "char_001",
                "character_name": "A",
                "text": "hi",
                "keyframe_plan": {"keyframe_count": 1, "keyframe_notes": []},
            }],
        }],
    },
    "metrics": {
        "scene_count": 1,
        "shot_count_total": 1,
        "avg_shots_per_scene": 1.0,
        "dialogue_block_count": 1,
        "action_block_count": 0,
    },
}


def test_screenplay_evaluator_passes_when_estimated_duration_seconds_present():
    from agents.screenplay.schema import ScreenplayAgentOutput
    from agents.screenplay.evaluator import ScreenplayEvaluator

    out = ScreenplayAgentOutput.model_validate(_MIN_SCREENPLAY)
    errors = ScreenplayEvaluator().check_structure(out)
    assert errors == [], errors


def test_screenplay_evaluator_flags_missing_estimated_duration_seconds():
    from agents.screenplay.schema import ScreenplayAgentOutput
    from agents.screenplay.evaluator import ScreenplayEvaluator
    import copy

    bad = copy.deepcopy(_MIN_SCREENPLAY)
    bad["content"]["scenes"][0]["estimated_duration_seconds"] = 0.0
    out = ScreenplayAgentOutput.model_validate(bad)
    errors = ScreenplayEvaluator().check_structure(out)
    assert any("estimated_duration_seconds" in e for e in errors), errors


def test_screenplay_evaluator_flags_negative_estimated_duration_seconds():
    from agents.screenplay.schema import ScreenplayAgentOutput
    from agents.screenplay.evaluator import ScreenplayEvaluator
    import copy

    bad = copy.deepcopy(_MIN_SCREENPLAY)
    bad["content"]["scenes"][0]["estimated_duration_seconds"] = -1.0
    out = ScreenplayAgentOutput.model_validate(bad)
    errors = ScreenplayEvaluator().check_structure(out)
    assert any("estimated_duration_seconds" in e for e in errors), errors


# ═══════════════════════════════════════════════════════════════════════
# 4. Music / Ambience system prompts now READ the field — old formula is gone
# ═══════════════════════════════════════════════════════════════════════

def test_music_system_prompt_reads_estimated_duration_seconds_and_drops_old_formula():
    from agents.music.agent import MusicAgent

    agent = MusicAgent.__new__(MusicAgent)
    sp = agent.system_prompt()
    assert "estimated_duration_seconds" in sp
    assert "single source of truth" in sp.lower()
    # Old formula text must not survive in MusicAgent's prompt — it lives
    # only in ScreenplayAgent's prompt now.
    assert "words / 2.5" not in sp and "words/2.5" not in sp, sp
    # Must explicitly warn against re-derivation.
    assert "do not re-derive" in sp.lower() or "do not re-estimate" in sp.lower() or "do not re-derive" in sp.lower().replace("-", "") or "not re-derive" in sp.lower()


def test_ambience_system_prompt_reads_estimated_duration_seconds_and_drops_old_formula():
    from agents.ambience.agent import AmbienceAgent

    agent = AmbienceAgent.__new__(AmbienceAgent)
    sp = agent.system_prompt()
    assert "estimated_duration_seconds" in sp
    assert "single source of truth" in sp.lower()
    assert "words / 2.5" not in sp and "words/2.5" not in sp, sp


def test_music_user_prompt_reminds_llm_to_read_verbatim():
    from agents.music.agent import MusicAgent
    from agents.music.schema import MusicAgentInput

    agent = MusicAgent.__new__(MusicAgent)
    inp = MusicAgentInput(screenplay_json_text='{"content": {"scenes": []}}')
    up = agent.build_user_prompt(inp)
    assert "estimated_duration_seconds" in up
    assert "do not re-estimate" in up.lower() or "do not re-derive" in up.lower()


def test_ambience_user_prompt_reminds_llm_to_read_verbatim():
    from agents.ambience.agent import AmbienceAgent
    from agents.ambience.schema import AmbienceAgentInput

    agent = AmbienceAgent.__new__(AmbienceAgent)
    inp = AmbienceAgentInput(screenplay_json_text='{"content": {"scenes": []}}')
    up = agent.build_user_prompt(inp)
    assert "estimated_duration_seconds" in up
    assert "do not re-estimate" in up.lower() or "do not re-derive" in up.lower()


# ═══════════════════════════════════════════════════════════════════════
# 5. Path B wiring is gone — Music / Ambience no longer depend on narration
# ═══════════════════════════════════════════════════════════════════════

def test_music_input_has_no_narration_field():
    from agents.music.schema import MusicAgentInput

    inp = MusicAgentInput()
    assert not hasattr(inp, "narration_json_text"), \
        "Plan A reverted Path B — MusicAgentInput must not carry narration_json_text"


def test_ambience_input_has_no_narration_field():
    from agents.ambience.schema import AmbienceAgentInput

    inp = AmbienceAgentInput()
    assert not hasattr(inp, "narration_json_text"), \
        "Plan A reverted Path B — AmbienceAgentInput must not carry narration_json_text"


def test_music_labels_only_declare_screenplay():
    from agents.music import labels

    label_constants = {
        name: getattr(labels, name)
        for name in dir(labels) if name.startswith("INPUT_LABEL_")
    }
    assert label_constants == {"INPUT_LABEL_SCREENPLAY": "screenplay"}, label_constants


def test_ambience_labels_only_declare_screenplay():
    from agents.ambience import labels

    label_constants = {
        name: getattr(labels, name)
        for name in dir(labels) if name.startswith("INPUT_LABEL_")
    }
    assert label_constants == {"INPUT_LABEL_SCREENPLAY": "screenplay"}, label_constants


def test_music_descriptor_input_needs_description_mentions_estimated_duration_seconds():
    from agents.music.descriptor import DESCRIPTOR

    desc = DESCRIPTOR.input_needs_description or ""
    assert "estimated_duration_seconds" in desc
    # Must not advertise a narration label.
    assert "[narration]" not in desc


def test_ambience_descriptor_input_needs_description_mentions_estimated_duration_seconds():
    from agents.ambience.descriptor import DESCRIPTOR

    desc = DESCRIPTOR.input_needs_description or ""
    assert "estimated_duration_seconds" in desc
    assert "[narration]" not in desc


# ═══════════════════════════════════════════════════════════════════════
# 6. Narration is unchanged by Plan A
# ═══════════════════════════════════════════════════════════════════════

def test_narration_segment_has_no_plan_b_fields():
    from agents.narration.schema import NarrationSegment

    seg = NarrationSegment()
    # Plan B experimental fields must be gone.
    assert not hasattr(seg, "linked_scene_id")
    assert not hasattr(seg, "actual_duration_seconds")


def test_narration_content_has_no_scene_durations():
    from agents.narration.schema import NarrationContent

    c = NarrationContent()
    assert not hasattr(c, "scene_durations")
