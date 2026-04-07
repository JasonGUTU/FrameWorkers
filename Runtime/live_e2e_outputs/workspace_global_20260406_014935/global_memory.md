# Global memory

Global memory for workspace `workspace_global_20260406_014935`. Records semantic decisions and project context — the 'why' behind agent outputs.
Artifact paths are in ``artifact_registry.jsonl`` (not here).

## Entries

```json
[
  {
    "content": {
      "what": "This story blueprint outlines a poignant drama featuring Arthur, a retired watchmaker, as he races against time to repair his late wife's cherished pocket watch across three key scenes.",
      "why": "The tone is hopeful and nostalgic, focusing on Arthur's internal struggle and quiet determination. The structure builds tension with a clear deadline (New Year's Eve midnight) culminating in a moment of peace and connection.",
      "context_note": "scope=global"
    },
    "agent_id": "StoryAgent",
    "task_id": "task_1_4e73ecd7",
    "execution_id": "exec_1_61ba43f5",
    "created_at": "2026-04-06T01:49:53.203488+00:00",
    "supersedes": null
  },
  {
    "content": {
      "what": "The Watchmaker's Midnight, 3 scenes, 9 total shots, Poignant Drama style.",
      "why": "The creative decisions prioritize an intimate and reflective tone, conveyed through deliberate pacing and a visual approach that emphasizes close-ups on Arthur's hands and face, as well as the intricate details of the watch. Warm, soft lighting is used throughout to evoke nostalgia, hope, and the cozy yet solitary nature of the workshop. The pacing is slow and measured in the setup, builds tension in the climax, and resolves with a serene, reflective rhythm, mirroring Arthur's emotional journey.",
      "context_note": "scope=global"
    },
    "agent_id": "ScreenplayAgent",
    "task_id": "task_1_4e73ecd7",
    "execution_id": "exec_2_bee41f2d",
    "created_at": "2026-04-06T01:50:44.702499+00:00",
    "supersedes": null
  },
  {
    "content": {
      "what": "1 character entity, 1 location entity, 3 prop entities; 5 L1 global anchor prompts; Intimate and reflective, warm, golden visual style.",
      "why": "L1 consistency is achieved by extracting the canonical physical appearance of each entity. Visual decisions prioritize a warm, cozy, and detailed aesthetic, focusing on the character's weary determination, the workshop's lived-in clutter, and the props' antique craftsmanship.",
      "context_note": "scope=global"
    },
    "agent_id": "KeyFrameAgent",
    "task_id": "task_1_4e73ecd7",
    "execution_id": "exec_3_20b4e043",
    "created_at": "2026-04-06T01:53:49.366126+00:00",
    "supersedes": null
  },
  {
    "content": {
      "what": "Video package: 3 scene(s), 9 shot clip(s), 10.0s total. Includes per-shot clips, scene assemblies, and final clip.",
      "why": "Deterministic assembly from screenplay shot structure; no creative LLM decisions.",
      "context_note": "scope=global"
    },
    "agent_id": "VideoAgent",
    "task_id": "task_1_4e73ecd7",
    "execution_id": "exec_4_af2a50a2",
    "created_at": "2026-04-06T02:03:11.306476+00:00",
    "supersedes": null
  },
  {
    "content": {
      "what": "3 scenes, 0 narration segments, music and ambience provided for each of the 3 scenes, delivered in JSON format.",
      "why": "Music mood choices track Arthur's emotional arc from focused determination and increasing anxiety, through urgent desperation and precarious hope, to a serene and bittersweet resolution. Ambience is designed to subtly underscore the intimate workshop setting and the passage of time, enhancing Arthur's internal state.",
      "context_note": "scope=global"
    },
    "agent_id": "AudioAgent",
    "task_id": "task_1_4e73ecd7",
    "execution_id": "exec_5_8980e44f",
    "created_at": "2026-04-06T02:03:46.763461+00:00",
    "supersedes": null
  }
]
```
