"""Keyframe package: excluded metadata must not appear in model_dump (workspace JSON)."""

from __future__ import annotations

import sys
from pathlib import Path

for parent in Path(__file__).resolve().parents:
    if (parent / "agents" / "__init__.py").exists():
        if str(parent) not in sys.path:
            sys.path.insert(0, str(parent))
        break

from agents.common_schema import ImageAsset
from agents.keyframe.schema import (
    Keyframe,
    KeyframeConstraintsApplied,
    KeyframesPackage,
    StabilityAnchorKeyframe,
)


def test_stability_anchor_excludes_purpose_and_display_name_from_dump():
    a = StabilityAnchorKeyframe(
        entity_type="prop",
        entity_id="prop_001",
        display_name="Sword",
        purpose="prop_anchor",
        keyframe_id="kf_x",
        image_asset=ImageAsset(),
        prompt_summary="A blade",
    )
    d = a.model_dump()
    assert "purpose" not in d
    assert "display_name" not in d
    assert d.get("entity_id") == "prop_001"
    assert d.get("prompt_summary") == "A blade"


def test_l3_keyframe_excludes_constraints_applied_from_dump():
    k = Keyframe(
        keyframe_id="kf_001",
        prompt_summary="still",
        video_motion_hint="slow pan",
        constraints_applied=KeyframeConstraintsApplied(
            characters_in_frame=["char_001"],
        ),
    )
    d = k.model_dump()
    assert "constraints_applied" not in d


def test_roundtrip_old_json_with_excluded_keys_still_loads():
    raw = {
        "meta": {"asset_id": "k1"},
        "content": {
            "global_anchors": {
                "characters": [],
                "locations": [
                    {
                        "entity_type": "location",
                        "entity_id": "loc_001",
                        "purpose": "style_anchor",
                        "display_name": "",
                        "keyframe_id": "kf_g",
                        "image_asset": {},
                        "prompt_summary": "room",
                    }
                ],
                "props": [],
            },
            "scenes": [],
        },
        "metrics": {},
    }
    pkg = KeyframesPackage.model_validate(raw)
    loc = pkg.content.global_anchors.locations[0]
    assert loc.purpose == "style_anchor"
    dumped = pkg.model_dump(exclude={"meta"})
    loc_out = dumped["content"]["global_anchors"]["locations"][0]
    assert "purpose" not in loc_out
