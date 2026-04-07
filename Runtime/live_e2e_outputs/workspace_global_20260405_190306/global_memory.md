# Global memory

Global memory for workspace `workspace_global_20260405_190306`. Records semantic decisions and project context — the 'why' behind agent outputs.
Artifact paths are in ``artifact_registry.jsonl`` (not here).

## Entries

```json
[
  {
    "content": {
      "what": "This is a short drama about a retired watchmaker, Arthur, who races against time to repair his late wife's cherished pocket watch on New Year's Eve, seeking solace and connection. It features a single protagonist across one poignant scene.",
      "why": "The creative choices focus on evoking a sense of quiet desperation, the delicate tension of intricate repair, and the bittersweet hope of new beginnings. The style is intimate and reflective, using a condensed story arc for emotional impact within a brief duration.",
      "context_note": "scope=global"
    },
    "agent_id": "StoryAgent",
    "task_id": "task_1_4c2030c0",
    "execution_id": "exec_1_33699ab1",
    "created_at": "2026-04-05T19:03:22.691096+00:00",
    "supersedes": null
  },
  {
    "content": {
      "what": "Untitled Screenplay, 1 scene, 2 shots, minimalist style",
      "why": "No user text provided, so a default, minimalist structure is presented to demonstrate schema with placeholder content and no empty dialogue text.",
      "context_note": "scope=global"
    },
    "agent_id": "ScreenplayAgent",
    "task_id": "task_1_4c2030c0",
    "execution_id": "exec_2_00022cd8",
    "created_at": "2026-04-05T19:03:44.529118+00:00",
    "supersedes": null
  },
  {
    "content": {
      "what": "1 character, 1 location, 0 props, 2 keyframes, neutral and functional visual style.",
      "why": "Layer 1 defines canonical looks for each entity, establishing a consistent foundational appearance. These anchors will be built upon by subsequent layers for specific scene contexts. Key visual decisions prioritize concrete light and material depiction, avoiding overly dramatic or highly stylized visuals.",
      "context_note": "scope=global"
    },
    "agent_id": "KeyFrameAgent",
    "task_id": "task_1_4c2030c0",
    "execution_id": "exec_3_b64546a3",
    "created_at": "2026-04-05T19:05:40.394026+00:00",
    "supersedes": null
  },
  {
    "content": {
      "what": "Video package: 1 scene(s), 2 shot clip(s), 6.0s total. Includes per-shot clips, scene assemblies, and final clip.",
      "why": "Deterministic assembly from screenplay shot structure; no creative LLM decisions.",
      "context_note": "scope=global"
    },
    "agent_id": "VideoAgent",
    "task_id": "task_1_4c2030c0",
    "execution_id": "exec_4_bb96bf87",
    "created_at": "2026-04-05T19:09:05.943579+00:00",
    "supersedes": null
  },
  {
    "content": {
      "what": "1 scene, 0 narration segments, 1 music track and 1 ambience track per scene, delivered in JSON format.",
      "why": "Mood choices are based on the 'unknown location' context, aiming for a sense of mystery and subtle anticipation. The audio style is minimalist and atmospheric, providing a neutral yet engaging sonic backdrop for a placeholder scene.",
      "context_note": "scope=global"
    },
    "agent_id": "AudioAgent",
    "task_id": "task_1_4c2030c0",
    "execution_id": "exec_5_e97d98f3",
    "created_at": "2026-04-05T19:09:29.430737+00:00",
    "supersedes": null
  }
]
```
