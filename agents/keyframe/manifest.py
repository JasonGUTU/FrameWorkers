"""Build ordered keyframes manifest rows from KeyFrameAgent execution results."""

from __future__ import annotations

from typing import Any, Dict, List


def build_keyframes_manifest_items(results: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Build ordered keyframes manifest rows from KeyFrameAgent ``results``."""
    items: List[Dict[str, Any]] = []
    if not isinstance(results, dict):
        return items
    content = results.get("content")
    if not isinstance(content, dict):
        return items

    def _uri(node: Any) -> str:
        if not isinstance(node, dict):
            return ""
        return str(node.get("uri") or "").strip()

    ga = content.get("global_anchors") or {}
    if isinstance(ga, dict):
        for entity_list, layer in (
            ("characters", "global_character"),
            ("locations", "global_location"),
            ("props", "global_prop"),
        ):
            for row in ga.get(entity_list) or []:
                if not isinstance(row, dict):
                    continue
                uri = _uri(row.get("image_asset"))
                if not uri:
                    continue
                eid = str(row.get("entity_id") or "").strip()
                items.append(
                    {
                        "path": uri,
                        "sys_id": eid or "",
                        "entity_id": eid,
                        "entity_type": str(row.get("entity_type") or ""),
                        "layer": layer,
                        "scene_id": "",
                        "shot_id": "",
                        "kf_index": 0,
                        "order": int(row.get("order") or 0),
                    }
                )

    for scene in content.get("scenes") or []:
        if not isinstance(scene, dict):
            continue
        scid = str(scene.get("scene_id") or "").strip()
        stab = scene.get("stability_keyframes") or {}
        if isinstance(stab, dict):
            for entity_list, layer in (
                ("characters", "scene_character"),
                ("locations", "scene_location"),
                ("props", "scene_prop"),
            ):
                for row in stab.get(entity_list) or []:
                    if not isinstance(row, dict):
                        continue
                    uri = _uri(row.get("image_asset"))
                    if not uri:
                        continue
                    eid = str(row.get("entity_id") or "").strip()
                    items.append(
                        {
                            "path": uri,
                            "sys_id": eid or "",
                            "entity_id": eid,
                            "entity_type": str(row.get("entity_type") or ""),
                            "layer": layer,
                            "scene_id": scid,
                            "shot_id": "",
                            "kf_index": 0,
                            "order": int(row.get("order") or 0),
                        }
                    )

        for shot in scene.get("shots") or []:
            if not isinstance(shot, dict):
                continue
            shid = str(shot.get("shot_id") or "").strip()
            for kf in shot.get("keyframes") or []:
                if not isinstance(kf, dict):
                    continue
                uri = _uri(kf.get("image_asset"))
                if not uri:
                    continue
                kid = str(kf.get("keyframe_id") or "").strip()
                items.append(
                    {
                        "path": uri,
                        "sys_id": kid,
                        "entity_id": "",
                        "entity_type": "shot_keyframe",
                        "layer": "shot",
                        "scene_id": scid,
                        "shot_id": shid,
                        "kf_index": int(kf.get("order") or 0),
                        "order": int(kf.get("order") or 0),
                    }
                )

    return items
