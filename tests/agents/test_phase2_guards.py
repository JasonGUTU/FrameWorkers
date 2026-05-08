"""Architectural guards established by the Round-2 cleanup (Phases A through H).

These tests are pure source-code grep checks. They run fast (no LLM, no
network, no fixtures) and exist solely to keep the architectural
invariants from regressing. The principles being guarded are:

  1.  Sub-agent input boundary: every ``descriptor.build_input`` takes
      ``(step_id, resolved_artifacts: dict)`` — where values are
      ``ResolvedArtifactEntry`` (or lists thereof). Adding a new FIELD
      to an entry only edits ``ResolvedArtifactEntry`` in
      ``agents/common_schema.py`` — one place. Adding a new CHANNEL
      (a whole new build_input parameter) still requires editing every
      descriptor signature, keeping that cross-cutting change visible
      in PR review.

  2.  Evaluators do not perform cross-validation — ``check_structure`` /
      ``evaluate_creative`` / ``evaluate`` / ``evaluate_asset`` take only
      the agent's own ``output`` (or ``asset_data`` for L3). They never
      receive the resolved-artifacts dict.

  3.  Materializers receive a ``MaterializeContext`` carrying
      ``typed_input``, never a second resolved-artifacts channel.

  4.  Assistant layer is agent-agnostic — no ``if execution.agent_id ==
      "<AgentName>"`` hard-codes in ``service.py`` / ``artifact_writer.py``.
      Agent-specific behavior must live in the agent's own descriptor /
      manifest.

  5.  Dead Round-1 contracts (``OutputEnvelopeV2``, ``StructuredOutputV2``,
      ``BinaryOutputV2``, ``NamingSpecV2``, ``NamingRuleV2``) and the
      Round-1 dead inference plugin registry never come back.

  6.  Intake sub-system is wired up: all four Intake agents are
      registered in ``AGENT_REGISTRY`` and the workspace upload route
      exists.

  7.  Label vocabulary discipline:
        * ``ScreenplayAgent`` only declares ``[story]`` (no
          ``[creative_brief]`` or ``[user_instruction]`` directive label).
        * Entry-point agents (``StoryAgent``, ``UnivaStoryboardAgent``)
          are the only ones that declare ``[creative_brief]``.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _all_python_files(*roots: Path) -> list[Path]:
    out: list[Path] = []
    for root in roots:
        for p in root.rglob("*.py"):
            # Ignore test files for grep checks that scan production code,
            # and ignore caches.
            parts = set(p.parts)
            if "__pycache__" in parts:
                continue
            out.append(p)
    return out


# ---------------------------------------------------------------------------
# 1. Dead Round-1 contracts must not return
# ---------------------------------------------------------------------------


_FORBIDDEN_DEAD_SYMBOLS = (
    "OutputEnvelopeV2",
    "StructuredOutputV2",
    "BinaryOutputV2",
    "NamingSpecV2",
    "NamingRuleV2",
    "BaseGeneratorRegistry",
    "get_image_generator_registry",
    "get_video_generator_registry",
    "get_audio_generator_registry",
)


def test_dead_round1_symbols_never_resurface():
    targets = _all_python_files(
        _REPO / "agents",
        _REPO / "plan-stack-backend" / "src",
        _REPO / "inference",
        _REPO / "director_agent",
        _REPO / "scripts",
    )
    for symbol in _FORBIDDEN_DEAD_SYMBOLS:
        offenders: list[Path] = []
        for path in targets:
            text = _read(path)
            if symbol in text:
                offenders.append(path)
        assert not offenders, (
            f"Dead Round-1 symbol {symbol!r} reappeared in:\n  "
            + "\n  ".join(str(p.relative_to(_REPO)) for p in offenders)
        )


# ---------------------------------------------------------------------------
# 2. Sub-agent input boundary: descriptors take only `resolved_artifacts`
# ---------------------------------------------------------------------------


def test_descriptors_take_only_resolved_artifacts():
    """``descriptor.build_input`` is the agent boundary. Its signature
    must be ``(step_id, resolved_artifacts: dict)`` — no extra channels.
    Adding a new parameter requires intentionally editing every
    descriptor, which is exactly the kind of change we want to be
    visible in PR review (not a one-line dataclass field bump on a
    wrapper)."""
    import re

    descriptor_files = list((_REPO / "agents").rglob("descriptor.py"))
    sig_re = re.compile(
        r"^\s*def\s+build_input\s*\(([^)]*)\)",
        re.MULTILINE,
    )
    offenders: list[tuple[Path, str]] = []
    for path in descriptor_files:
        # Skip the base SubAgentDescriptor module — it defines the
        # field type, not a concrete agent build_input.
        if path.name == "descriptor.py" and path.parent == _REPO / "agents":
            continue
        text = _read(path)
        for match in sig_re.finditer(text):
            params = match.group(1)
            if "input_bundle_v2" in params or "InputBundleV2" in params:
                offenders.append((path, match.group(0).strip()))
                continue
            if "resolved_artifacts" not in params:
                offenders.append((path, match.group(0).strip()))
    assert not offenders, (
        "descriptor.build_input signature drifted from "
        "(step_id, resolved_artifacts):\n  "
        + "\n  ".join(f"{p.relative_to(_REPO)}: {sig}" for p, sig in offenders)
    )


# ---------------------------------------------------------------------------
# 3. Evaluators do not perform cross-validation
# ---------------------------------------------------------------------------


def test_evaluator_methods_take_only_output():
    """check_structure / evaluate_creative / evaluate / evaluate_asset
    must not accept ``input_bundle_v2`` as a parameter."""
    eval_files = list((_REPO / "agents").rglob("evaluator.py"))
    eval_files.append(_REPO / "agents" / "base_evaluator.py")
    method_re = re.compile(
        r"^\s*(?:async\s+)?def\s+"
        r"(check_structure|evaluate_creative|evaluate|evaluate_asset)"
        r"\s*\(([^)]*)\)",
        re.MULTILINE,
    )
    offenders: list[tuple[Path, str]] = []
    for path in eval_files:
        text = _read(path)
        for match in method_re.finditer(text):
            params = match.group(2)
            if "input_bundle" in params or "InputBundle" in params:
                offenders.append((path, match.group(0).strip()))
    assert not offenders, (
        "Evaluator method still takes input_bundle_v2:\n  "
        + "\n  ".join(f"{p.relative_to(_REPO)}: {sig}" for p, sig in offenders)
    )


# ---------------------------------------------------------------------------
# 4. Materializers receive only MaterializeContext + asset_dict
# ---------------------------------------------------------------------------


def test_materializer_signatures_take_only_ctx_and_asset_dict():
    mat_files = list((_REPO / "agents").rglob("materializer.py"))
    mat_files.append(_REPO / "agents" / "descriptor.py")
    sig_re = re.compile(
        r"^\s*async\s+def\s+materialize\s*\(\s*self\s*,([^)]*)\)",
        re.MULTILINE,
    )
    offenders: list[tuple[Path, str]] = []
    for path in mat_files:
        text = _read(path)
        for match in sig_re.finditer(text):
            params_block = match.group(1)
            # Allowed: ctx + asset_dict (with type annotations / defaults).
            # Forbidden: any param mentioning input_bundle*.
            if "input_bundle" in params_block or "InputBundle" in params_block:
                offenders.append((path, match.group(0).strip()))
    assert not offenders, (
        "Materializer.materialize signature still mentions input_bundle:\n  "
        + "\n  ".join(f"{p.relative_to(_REPO)}: {sig}" for p, sig in offenders)
    )


# ---------------------------------------------------------------------------
# 5. Assistant layer carries no agent-specific hard-codes
# ---------------------------------------------------------------------------


_ASSISTANT_HARD_CODE_AGENTS = (
    "StoryAgent",
    "ScreenplayAgent",
    "KeyFrameAgent",
    "VideoAgent",
    "MusicAgent",
    "AmbienceAgent",
    "AudioMixAgent",
    "UnivaStoryboardAgent",
    "UnivaKeyFrameAgent",
    "UnivaVideoAgent",
)


def test_assistant_layer_has_no_agent_id_hardcodes():
    assistant_files = (
        _REPO / "plan-stack-backend" / "src" / "assistant" / "service.py",
        _REPO / "plan-stack-backend" / "src" / "assistant" / "routes.py",
        _REPO / "plan-stack-backend" / "src" / "assistant" / "workspace" / "artifact_writer.py",
        _REPO / "plan-stack-backend" / "src" / "assistant" / "workspace" / "workspace.py",
    )
    pattern = re.compile(
        r'agent_id\s*==\s*["\'](?P<name>\w+Agent)["\']'
    )
    offenders: list[tuple[Path, str]] = []
    for path in assistant_files:
        if not path.exists():
            continue
        for i, line in enumerate(_read(path).splitlines(), 1):
            for match in pattern.finditer(line):
                if match.group("name") in _ASSISTANT_HARD_CODE_AGENTS:
                    offenders.append((path, f"L{i}: {line.strip()}"))
    assert not offenders, (
        "Assistant layer still hardcodes a content-pipeline agent_id:\n  "
        + "\n  ".join(f"{p.relative_to(_REPO)}: {l}" for p, l in offenders)
    )


def test_assistant_does_not_import_agent_specific_modules():
    """``assistant/`` must not directly import any agent-specific module
    (e.g. ``agents.keyframe.manifest``). Agent-specific knowledge ships
    via descriptors / output_manifests, not via direct imports."""
    assistant_files = list(
        (_REPO / "plan-stack-backend" / "src" / "assistant").rglob("*.py")
    )
    forbidden_re = re.compile(
        r"^\s*from\s+agents\.(?P<mod>\w+)(?:\.\w+)*\s+import",
        re.MULTILINE,
    )
    allowed_top_levels = {
        "",  # `from agents import ...`
        "contracts",
        "descriptor",
        "agent_registry",
        "common_schema",
        "base_agent",
        "base_evaluator",
    }
    offenders: list[tuple[Path, str]] = []
    for path in assistant_files:
        text = _read(path)
        for match in forbidden_re.finditer(text):
            mod = match.group("mod")
            if mod not in allowed_top_levels:
                offenders.append((path, match.group(0).strip()))
    assert not offenders, (
        "Assistant layer is importing agent-specific modules:\n  "
        + "\n  ".join(f"{p.relative_to(_REPO)}: {l}" for p, l in offenders)
    )


# ---------------------------------------------------------------------------
# 6. Intake sub-system is wired up
# ---------------------------------------------------------------------------


def test_all_intake_agents_registered():
    """IntakeTextAgent was retired 2026-04-23 — chat/text uploads are
    now persisted directly as [creative_brief] artifacts by the
    workspace layer (see ``workspace.persist_raw_upload`` branching on
    ``mime=text/plain``). Binary intake agents stay registered since
    they still carry real LLM work (image captioning / video analysis)."""
    from agents import AGENT_REGISTRY  # late import — tests import order

    expected = {"IntakeImageAgent", "IntakeVideoAgent"}
    missing = expected - set(AGENT_REGISTRY.keys())
    assert not missing, f"Missing intake agents from AGENT_REGISTRY: {missing}"
    assert "IntakeTextAgent" not in AGENT_REGISTRY, (
        "IntakeTextAgent was retired — its responsibilities moved into "
        "workspace.persist_raw_upload. Removing it from the registry was "
        "the point of the refactor; re-adding it re-introduces a no-value "
        "agent step at the head of every plan."
    )


def test_workspace_upload_route_is_registered():
    routes_src = _read(
        _REPO / "plan-stack-backend" / "src" / "assistant" / "routes.py"
    )
    assert "/api/workspace/upload" in routes_src
    assert "def upload_user_file" in routes_src


def test_workspace_persist_raw_upload_exists():
    src = _read(
        _REPO / "plan-stack-backend" / "src" / "assistant" / "workspace" / "workspace.py"
    )
    assert "def persist_raw_upload(" in src
    # The placeholder caption convention must be present:
    #   - scope marker "raw_pending"
    #   - self-identifying "Raw user upload" prefix + "Pending intake"
    assert "raw_pending" in src
    assert "Raw user upload" in src
    assert "Pending intake" in src


# ---------------------------------------------------------------------------
# 7. Label vocabulary discipline
# ---------------------------------------------------------------------------


def test_screenplay_agent_only_declares_story_label():
    """ScreenplayAgent's ``input_needs_description`` is built with
    f-strings, so a static regex over the source mostly sees Python
    identifiers (e.g. ``[INPUT_LABEL_STORY]``). Use the live descriptor
    instead so we see the rendered label names."""
    from agents.screenplay.descriptor import DESCRIPTOR

    rendered = DESCRIPTOR.input_needs_description or ""
    headers = re.findall(
        r"\[(?P<label>[a-zA-Z_][a-zA-Z0-9_]*)\]\s*\((?:single|collection)\)",
        rendered,
    )
    assert headers, "ScreenplayAgent descriptor declares no [label] headers"
    assert set(headers) == {"story"}, (
        f"ScreenplayAgent must declare exactly [story], got {headers}"
    )


def test_screenplay_labels_module_only_exports_story_label():
    """No INPUT_LABEL_* constant other than ``story`` should live in
    ``screenplay/labels.py``. The directive label was removed in
    Phase A.5; the docstring still mentions the historical word
    "directives" so don't grep — introspect the module."""
    from agents.screenplay import labels as screenplay_labels

    label_constants = {
        name: getattr(screenplay_labels, name)
        for name in dir(screenplay_labels)
        if name.startswith("INPUT_LABEL_")
    }
    assert label_constants == {"INPUT_LABEL_STORY": "story"}, (
        f"agents/screenplay/labels.py drift: {label_constants}"
    )


def test_only_entry_point_agents_declare_creative_brief():
    """Only creative-head + leaf-tool entry agents may declare the
    [creative_brief] label as an InputLabelSpec.name.

    Two categories are allowed:

    Creative heads — turn a brief into a structured multi-step plan:
      - StoryAgent (cinematic flows)
      - UnivaStoryboardAgent (univa flows)
      - NarrationAgent (illustrated-storytelling flows)

    Leaf-tool entries — single-purpose end-to-end tools the user invokes
    directly with an inline brief, no head-agent plan in between:
      - VideoExtendAgent ('extend by 5s')
      - StyleTransferAgent ('convert to Studio Ghibli style')
      - MusicAgent ('add piano BGM')
      - AmbienceAgent ('layer in jungle ambience')

    (IntakeTextAgent was retired — chat/text uploads are persisted as
    [creative_brief] artifacts by the workspace layer.)

    Mid-pipeline agents (Screenplay, KeyFrame, Video, etc.) must not
    declare this label, otherwise users could bypass the creative head
    and inject directives mid-pipeline.

    The check inspects InputLabelSpec ``name=...`` declarations only —
    descriptors whose docstring or label *description* merely mention
    the literal string ``[creative_brief]`` (e.g. brief_enricher's
    raw_brief description hints that its matched caption tends to come
    from a [creative_brief] artifact) are not violations.
    """
    descriptor_files = list((_REPO / "agents").rglob("descriptor.py"))
    head_dirs = {"story", "univa_storyboard", "narration"}
    leaf_tool_dirs = {"video_extend", "style_transfer", "music", "ambience"}
    allowed_dirs = head_dirs | leaf_tool_dirs
    # Match real label declarations inside InputLabelSpec, e.g.
    #   name=INPUT_LABEL_CREATIVE_BRIEF,
    #   name="creative_brief",
    name_pattern = re.compile(
        r"name\s*=\s*(INPUT_LABEL_CREATIVE_BRIEF\b|[\"']creative_brief[\"'])"
    )
    offenders: list[Path] = []
    for path in descriptor_files:
        text = _read(path)
        if not name_pattern.search(text):
            continue
        rel_parts = path.relative_to(_REPO / "agents").parts
        top = rel_parts[0] if rel_parts else ""
        if top in allowed_dirs:
            continue
        offenders.append(path)
    assert not offenders, (
        "[creative_brief] label declared on mid-pipeline descriptors:\n  "
        + "\n  ".join(str(p.relative_to(_REPO)) for p in offenders)
    )


# ---------------------------------------------------------------------------
# 8. example_agent is no longer in AGENT_REGISTRY
# ---------------------------------------------------------------------------


def test_example_agent_not_in_registry():
    from agents import AGENT_REGISTRY
    assert "ExamplePipelineAgent" not in AGENT_REGISTRY
    # The directory may still exist as a developer template, but the
    # registry must not surface it as a runnable agent.
