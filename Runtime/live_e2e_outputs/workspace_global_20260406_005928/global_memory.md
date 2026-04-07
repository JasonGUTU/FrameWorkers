# Global memory

Global memory for workspace `workspace_global_20260406_005928`. Records semantic decisions and project context — the 'why' behind agent outputs.
Artifact paths are in ``artifact_registry.jsonl`` (not here).

## Entries

```json
[
  {
    "content": {
      "what": "A storyboard depicting a retired watchmaker's race against midnight to repair his late wife's pocket watch for the New Year.",
      "why": "This storyboard covers the watchmaker's urgent task, his emotional connection to the watch, the challenges of repair, and the final moments of peace and connection as the new year begins, fulfilling the user's storyline.",
      "context_note": "scope=global"
    },
    "agent_id": "UnivaStoryboardAgent",
    "task_id": "task_1_1d69622c",
    "execution_id": "exec_1_bc6ee616",
    "created_at": "2026-04-06T00:59:59.727565+00:00",
    "supersedes": null
  },
  {
    "content": {
      "what": "Keyframe plan: 1 characters, 12 shots",
      "why": "Character reference images and per-shot keyframes for video generation",
      "context_note": "scope=global"
    },
    "agent_id": "UnivaKeyFrameAgent",
    "task_id": "task_1_1d69622c",
    "execution_id": "exec_2_1320564a",
    "created_at": "2026-04-06T01:01:27.442763+00:00",
    "supersedes": null
  },
  {
    "content": {
      "what": "Video plan: 12 shots, 60s total",
      "why": "Per-shot I2V clips merged into final video",
      "context_note": "scope=global"
    },
    "agent_id": "UnivaVideoAgent",
    "task_id": "task_1_1d69622c",
    "execution_id": "exec_3_0b0891bf",
    "created_at": "2026-04-06T01:13:22.549005+00:00",
    "supersedes": null
  }
]
```
