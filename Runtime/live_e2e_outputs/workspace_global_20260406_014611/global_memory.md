# Global memory

Global memory for workspace `workspace_global_20260406_014611`. Records semantic decisions and project context — the 'why' behind agent outputs.
Artifact paths are in ``artifact_registry.jsonl`` (not here).

## Entries

```json
[
  {
    "content": {
      "what": "A poignant drama about an elderly, retired watchmaker attempting to repair his late wife's cherished pocket watch on New Year's Eve. It features a single protagonist across one key location, encompassing two brief, emotionally charged scenes.",
      "why": "The creative choices focus on a melancholic yet hopeful tone, using the ticking of a clock and the delicate repair as metaphors for time, memory, and healing. The narrative is minimalistic and intimate to fit the extremely short duration.",
      "context_note": "scope=global"
    },
    "agent_id": "StoryAgent",
    "task_id": "task_1_9b81f823",
    "execution_id": "exec_1_28b1d66d",
    "created_at": "2026-04-06T01:46:29.096178+00:00",
    "supersedes": null
  },
  {
    "content": {
      "what": "The Watchmaker's Midnight, 2 scenes, 9 total shots, intimate and melancholic realism",
      "why": "The narrative's tone is 'melancholic yet hopeful', requiring a visual approach that emphasizes quiet introspection and the passage of time. Pacing is slow and deliberate in Scene 1, building tension around Arthur's task, then shifts to a serene, reflective resolution in Scene 2. Visuals heavily rely on close-ups of Arthur's hands, the intricate watch mechanism, and his face, creating an intimate connection with his emotional journey. Low-key lighting reinforces the late-night, solitary atmosphere, with a slight warm glow for moments of connection and hope.",
      "context_note": "scope=global"
    },
    "agent_id": "ScreenplayAgent",
    "task_id": "task_1_9b81f823",
    "execution_id": "exec_2_b6b8c7bf",
    "created_at": "2026-04-06T01:47:07.242214+00:00",
    "supersedes": null
  },
  {
    "content": {
      "what": "3 entities (1 character, 1 location, 1 prop), 1 scene, multiple keyframes, intimate and quiet visual style.",
      "why": "Style consistency is maintained through canonical L1 entity descriptions, with L2/L3 focusing on light, environment, and subtle emotional/physical shifts. Key decisions highlight Arthur's detailed work, the intricate prop, and atmospheric workshop lighting.",
      "context_note": "scope=global"
    },
    "agent_id": "KeyFrameAgent",
    "task_id": "task_1_9b81f823",
    "execution_id": "exec_3_ee6c4543",
    "created_at": "2026-04-06T01:49:55.358785+00:00",
    "supersedes": null
  },
  {
    "content": {
      "what": "Video package: 2 scene(s), 8 shot clip(s), 10.0s total. Includes per-shot clips, scene assemblies, and final clip.",
      "why": "Deterministic assembly from screenplay shot structure; no creative LLM decisions.",
      "context_note": "scope=global"
    },
    "agent_id": "VideoAgent",
    "task_id": "task_1_9b81f823",
    "execution_id": "exec_4_d2712bb5",
    "created_at": "2026-04-06T01:50:04.119110+00:00",
    "supersedes": null
  },
  {
    "content": {
      "what": "2 scenes, 0 narration segments, music and ambience provided for each scene, delivered in JSON format.",
      "why": "Music and ambience were designed to follow Arthur's emotional arc, transitioning from melancholic tension and urgent focus in his workshop to serene hope and peaceful closure upon repairing the watch. The audio style emphasizes intimacy, the passage of time, and profound emotional shifts.",
      "context_note": "scope=global"
    },
    "agent_id": "AudioAgent",
    "task_id": "task_1_9b81f823",
    "execution_id": "exec_5_f6796141",
    "created_at": "2026-04-06T01:50:52.053853+00:00",
    "supersedes": null
  }
]
```
