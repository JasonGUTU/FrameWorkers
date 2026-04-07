# Global memory

Global memory for workspace `workspace_global_20260405_145954`. Records semantic decisions and project context — the 'why' behind agent outputs.
Artifact paths are in ``artifact_registry.jsonl`` (not here).

## Entries

```json
[
  {
    "content": {
      "what": "A poignant drama about a retired watchmaker, Elias Vance, racing against the clock to repair his late wife's cherished pocket watch as the new year begins, all within a single, intimate scene.",
      "why": "The tone is poignant and hopeful, emphasizing a character's internal struggle and connection to memory through a race against time. A single, focused scene is used to heighten urgency and intimacy, creating a powerful emotional impact in a very short duration.",
      "context_note": "scope=global"
    },
    "agent_id": "StoryAgent",
    "task_id": "task_1_dfbbc525",
    "execution_id": "exec_1_4feea6ae",
    "created_at": "2026-04-05T15:00:09.881119+00:00",
    "supersedes": null
  },
  {
    "content": {
      "what": "The Chronos Workshop, 1 scene, 9 shots, intimate and urgent close-ups with a warm, nostalgic palette.",
      "why": "To convey Elias's poignant race against time and deep connection to his late wife. Pacing starts quick and frantic, building tension, then slowing to a serene, hopeful resolution. Visuals emphasize the delicate work and the ticking clock through tight framing, warm lamplight, and a shallow depth of field to draw focus to the intricate details and Elias's emotional journey.",
      "context_note": "scope=global"
    },
    "agent_id": "ScreenplayAgent",
    "task_id": "task_1_dfbbc525",
    "execution_id": "exec_2_7849027e",
    "created_at": "2026-04-05T15:00:48.068479+00:00",
    "supersedes": null
  },
  {
    "content": {
      "what": "1 character, 1 location, 3 props, 1 scene, 5 keyframes, intimate, atmospheric vintage style with warm lighting.",
      "why": "Consistency is achieved through a global application of warm, soft practical lighting and a rich, muted color palette. Key visual decisions include a shallow depth of field to focus on subjects, and highlights of gold and bronze from clockwork and lamplight.",
      "context_note": "scope=global"
    },
    "agent_id": "KeyFrameAgent",
    "task_id": "task_1_dfbbc525",
    "execution_id": "exec_3_e4d1c71d",
    "created_at": "2026-04-05T15:03:53.647496+00:00",
    "supersedes": null
  },
  {
    "content": {
      "what": "Video package: 1 scene(s), 9 shot clip(s), 11.0s total. Includes per-shot clips, scene assemblies, and final clip.",
      "why": "Deterministic assembly from screenplay shot structure; no creative LLM decisions.",
      "context_note": "scope=global"
    },
    "agent_id": "VideoAgent",
    "task_id": "task_1_dfbbc525",
    "execution_id": "exec_4_f2cc891c",
    "created_at": "2026-04-05T15:12:56.652465+00:00",
    "supersedes": null
  },
  {
    "content": {
      "what": "1 scene, 0 narration segments, 1 music track and 1 ambience track per scene, delivered as a final audio mix.",
      "why": "Music is chosen to evoke Elias's urgent, melancholic state, evolving into a warm and hopeful resolution. Ambience emphasizes the intricate clockwork and the quiet intensity of his workshop, contrasting with distant New Year's Eve sounds to underscore his singular focus.",
      "context_note": "scope=global"
    },
    "agent_id": "AudioAgent",
    "task_id": "task_1_dfbbc525",
    "execution_id": "exec_5_5ec470ae",
    "created_at": "2026-04-05T15:13:29.217748+00:00",
    "supersedes": null
  }
]
```
