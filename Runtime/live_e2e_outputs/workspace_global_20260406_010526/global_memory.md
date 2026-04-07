# Global memory

Global memory for workspace `workspace_global_20260406_010526`. Records semantic decisions and project context — the 'why' behind agent outputs.
Artifact paths are in ``artifact_registry.jsonl`` (not here).

## Entries

```json
[
  {
    "content": {
      "what": "A poignant drama about a retired watchmaker racing against time to repair his late wife's cherished pocket watch in a single, intense scene.",
      "why": "This blueprint captures a reflective, hopeful tone amidst the tension of a looming deadline, focusing on emotional connection and the quiet triumph of new beginnings.",
      "context_note": "scope=global"
    },
    "agent_id": "StoryAgent",
    "task_id": "task_1_5ae39789",
    "execution_id": "exec_1_d77b7d72",
    "created_at": "2026-04-06T01:05:44.383376+00:00",
    "supersedes": null
  },
  {
    "content": {
      "what": "The Midnight Watchmaker, 1 scene, 5 shots, poignant close-up visual style.",
      "why": "To convey the protagonist's internal struggle and meticulous focus through intimate close-ups and the amplifying sound of time. Pacing is deliberate, building tension as midnight approaches, underscored by warm, nostalgic lighting and a poignant, hopeful tone.",
      "context_note": "scope=global"
    },
    "agent_id": "ScreenplayAgent",
    "task_id": "task_1_5ae39789",
    "execution_id": "exec_2_3bc36fa1",
    "created_at": "2026-04-06T01:06:23.010761+00:00",
    "supersedes": null
  },
  {
    "content": {
      "what": "1 character, 1 location, 4 props, intimate and warm visual style, emphasizing texture and detail.",
      "why": "Each L1 prompt establishes the canonical physical look for its entity, focusing on material and lighting details to ensure a consistent, warm, and highly textured aesthetic throughout the project.",
      "context_note": "scope=global"
    },
    "agent_id": "KeyFrameAgent",
    "task_id": "task_1_5ae39789",
    "execution_id": "exec_3_35fcae43",
    "created_at": "2026-04-06T01:09:10.360224+00:00",
    "supersedes": null
  },
  {
    "content": {
      "what": "Video package: 1 scene(s), 5 shot clip(s), 10.0s total. Includes per-shot clips, scene assemblies, and final clip.",
      "why": "Deterministic assembly from screenplay shot structure; no creative LLM decisions.",
      "context_note": "scope=global"
    },
    "agent_id": "VideoAgent",
    "task_id": "task_1_5ae39789",
    "execution_id": "exec_4_192c2f1b",
    "created_at": "2026-04-06T01:09:21.711330+00:00",
    "supersedes": null
  },
  {
    "content": {
      "what": "1 scene, 0 narration segments, 1 music track and 1 ambience track per scene, delivered as an integrated stereo mix.",
      "why": "Music choices evoke initial tension, determination, and poignant nostalgia, evolving into peace and accomplishment. Ambience emphasizes the intricate mechanical world and the relentless passage of time, enhancing the protagonist's focused internal struggle and eventual resolution.",
      "context_note": "scope=global"
    },
    "agent_id": "AudioAgent",
    "task_id": "task_1_5ae39789",
    "execution_id": "exec_5_02a06c25",
    "created_at": "2026-04-06T01:10:01.653132+00:00",
    "supersedes": null
  }
]
```
