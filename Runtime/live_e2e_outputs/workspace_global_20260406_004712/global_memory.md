# Global memory

Global memory for workspace `workspace_global_20260406_004712`. Records semantic decisions and project context — the 'why' behind agent outputs.
Artifact paths are in ``artifact_registry.jsonl`` (not here).

## Entries

```json
[
  {
    "content": {
      "what": "A poignant drama about a retired watchmaker, Arthur, racing against midnight to repair his late wife's cherished pocket watch, conveyed in a single evocative scene.",
      "why": "The creative choices focus on a melancholic yet hopeful tone, using a tight, intimate style to highlight the watchmaker's grief, determination, and the symbolic act of renewal within a very short duration.",
      "context_note": "scope=global"
    },
    "agent_id": "StoryAgent",
    "task_id": "task_1_bf27d44c",
    "execution_id": "exec_1_b3d84219",
    "created_at": "2026-04-06T00:47:25.493555+00:00",
    "supersedes": null
  },
  {
    "content": {
      "what": "The Watchmaker's Midnight, 1 scene, 3 shots, intimate and poignant visual style.",
      "why": "The creative decisions prioritize an intimate and melancholic yet hopeful tone, focusing on Arthur's delicate work and emotional journey. Pacing is deliberate, building tension towards midnight and resolving with quiet peace. Visuals emphasize close-ups of hands and the watch, warm lighting, and a shallow depth of field to draw the viewer into Arthur's world.",
      "context_note": "scope=global"
    },
    "agent_id": "ScreenplayAgent",
    "task_id": "task_1_bf27d44c",
    "execution_id": "exec_2_90648d87",
    "created_at": "2026-04-06T00:47:55.256446+00:00",
    "supersedes": null
  },
  {
    "content": {
      "what": "1 character, 1 location, 3 props; detailed, canonical visual style.",
      "why": "Defines the canonical, consistent visual appearance for each entity, focusing on their physical attributes and inherent design to ensure recognition across all future shots.",
      "context_note": "scope=global"
    },
    "agent_id": "KeyFrameAgent",
    "task_id": "task_1_bf27d44c",
    "execution_id": "exec_3_dc10e31b",
    "created_at": "2026-04-06T00:51:27.365961+00:00",
    "supersedes": null
  },
  {
    "content": {
      "what": "Video package: 1 scene(s), 3 shot clip(s), 10.0s total. Includes per-shot clips, scene assemblies, and final clip.",
      "why": "Deterministic assembly from screenplay shot structure; no creative LLM decisions.",
      "context_note": "scope=global"
    },
    "agent_id": "VideoAgent",
    "task_id": "task_1_bf27d44c",
    "execution_id": "exec_4_b30fb55d",
    "created_at": "2026-04-06T00:55:21.094596+00:00",
    "supersedes": null
  },
  {
    "content": {
      "what": "1 scene, 0 narration segments, 1 distinct music track and 1 layered ambience track per scene, delivered as an integrated audio mixdown.",
      "why": "Music mood shifts from tense and melancholic determination to delicate and hopeful resolution, mirroring Arthur's internal journey. Ambience prioritizes intimate workshop sounds and subtle distant New Year's chimes to build tension and then signify release and connection.",
      "context_note": "scope=global"
    },
    "agent_id": "AudioAgent",
    "task_id": "task_1_bf27d44c",
    "execution_id": "exec_5_5df69992",
    "created_at": "2026-04-06T00:55:59.003190+00:00",
    "supersedes": null
  }
]
```
