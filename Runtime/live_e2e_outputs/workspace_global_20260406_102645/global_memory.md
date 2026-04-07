# Global memory

Global memory for workspace `workspace_global_20260406_102645`. Records semantic decisions and project context — the 'why' behind agent outputs.
Artifact paths are in ``artifact_registry.jsonl`` (not here).

## Entries

```json
[
  {
    "content": {
      "what": "A UniVA-style storyboard document for the whole video. It defines a cast of 2 character(s) with their visual descriptions, and breaks the story into 12 ordered shots — each shot specifying its setting, plot beat, static visual description, planned camera, and duration. It is the upstream creative source used by the keyframe and video steps to render and animate each shot of the story. A storyboard depicting a retired watchmaker's race against midnight to repair his late wife's cherished pocket watch.",
      "why": "This storyboard captures the emotional journey of the watchmaker, from focused determination and frustration to a breakthrough, culminating in a poignant moment of peace and connection at the start of a new year, fulfilling the user's storyline.",
      "context_note": "scope=global"
    },
    "agent_id": "UnivaStoryboardAgent",
    "task_id": "task_1_49bf0fe5",
    "execution_id": "exec_1_35785ca4",
    "created_at": "2026-04-06T10:27:19.840148+00:00",
    "supersedes": null
  },
  {
    "content": {
      "what": "A UniVA keyframe planning document covering 2 character(s) and 12 shots. For each character it holds a refined image-generation prompt fixing the canonical appearance; for each shot it holds the planned starting frame prompt. Used by the UniVA video step to fetch the prompt for each shot when animating clips. Keyframe plan: 2 characters, 12 shots",
      "why": "Character reference images and per-shot keyframes for video generation",
      "context_note": "scope=global"
    },
    "agent_id": "UnivaKeyFrameAgent",
    "task_id": "task_1_49bf0fe5",
    "execution_id": "exec_2_613228e9",
    "created_at": "2026-04-06T10:34:20.862793+00:00",
    "supersedes": null
  },
  {
    "content": {
      "what": "A manifest of the assembled UniVA video for the whole story: 12 shot clip(s), 60.0 seconds total runtime. It catalogs the per-shot animated clips and the single complete final video file. It is the document describing the finished UniVA video — there is exactly one such document per pipeline run. Video plan: 12 shots, 60s total",
      "why": "Per-shot I2V clips merged into final video",
      "context_note": "scope=global"
    },
    "agent_id": "UnivaVideoAgent",
    "task_id": "task_1_49bf0fe5",
    "execution_id": "exec_3_904fafd4",
    "created_at": "2026-04-06T10:53:13.730669+00:00",
    "supersedes": null
  }
]
```
