# Global memory

Global memory for workspace `workspace_global_20260406_004907`. Records semantic decisions and project context — the 'why' behind agent outputs.
Artifact paths are in ``artifact_registry.jsonl`` (not here).

## Entries

```json
[
  {
    "content": {
      "what": "A storyboard detailing a retired watchmaker's race against time to repair his late wife's pocket watch for the new year.",
      "why": "It captures the watchmaker's dedication, the urgency of the task, and the emotional connection sought through the repair, culminating in a moment of peace and remembrance at midnight.",
      "context_note": "scope=global"
    },
    "agent_id": "UnivaStoryboardAgent",
    "task_id": "task_1_d83260f9",
    "execution_id": "exec_1_7ab5175a",
    "created_at": "2026-04-06T00:49:41.073565+00:00",
    "supersedes": null
  },
  {
    "content": {
      "what": "Keyframe plan: 2 characters, 12 shots",
      "why": "Character reference images and per-shot keyframes for video generation",
      "context_note": "scope=global"
    },
    "agent_id": "UnivaKeyFrameAgent",
    "task_id": "task_1_d83260f9",
    "execution_id": "exec_2_241ce20a",
    "created_at": "2026-04-06T00:53:11.803228+00:00",
    "supersedes": null
  },
  {
    "content": {
      "what": "Video plan: 12 shots, 60s total",
      "why": "Per-shot I2V clips merged into final video",
      "context_note": "scope=global"
    },
    "agent_id": "UnivaVideoAgent",
    "task_id": "task_1_d83260f9",
    "execution_id": "exec_3_89e4f337",
    "created_at": "2026-04-06T00:53:28.345260+00:00",
    "supersedes": null
  }
]
```
