# Global memory

Global memory for workspace `workspace_global_20260406_004044`. Records semantic decisions and project context — the 'why' behind agent outputs.
Artifact paths are in ``artifact_registry.jsonl`` (not here).

## Entries

```json
[
  {
    "content": {
      "what": "A poignant drama about a retired watchmaker on New Year's Eve. The story features one character in a single location across two brief scenes, focusing on a deeply personal quest.",
      "why": "The creative choices emphasize a melancholic yet hopeful tone, using a highly condensed narrative structure to convey urgency and emotional resolution within a very short timeframe.",
      "context_note": "scope=global"
    },
    "agent_id": "StoryAgent",
    "task_id": "task_1_212d3481",
    "execution_id": "exec_1_2ba261fa",
    "created_at": "2026-04-06T00:41:04.000020+00:00",
    "supersedes": null
  },
  {
    "content": {
      "what": "Untitled Screenplay, 1 scene, 2 shots, Minimalist",
      "why": "Placeholder content due to empty input, focusing on basic screenplay structure and shot planning. Tone and pacing are neutral, visual approach is generic to allow for future content.",
      "context_note": "scope=global"
    },
    "agent_id": "ScreenplayAgent",
    "task_id": "task_1_212d3481",
    "execution_id": "exec_2_485a22cd",
    "created_at": "2026-04-06T00:41:20.864114+00:00",
    "supersedes": null
  },
  {
    "content": {
      "what": "1 location, 1 scene, 1 keyframe, realistic and atmospheric.",
      "why": "Layer 1 prompt establishes a canonical visual identity for the location (ancient forest), ensuring visual consistency across all subsequent layers. Key decision is to focus on natural elements and a sense of age.",
      "context_note": "scope=global"
    },
    "agent_id": "KeyFrameAgent",
    "task_id": "task_1_212d3481",
    "execution_id": "exec_3_c662f4b1",
    "created_at": "2026-04-06T00:43:28.542944+00:00",
    "supersedes": null
  },
  {
    "content": {
      "what": "Video package: 1 scene(s), 2 shot clip(s), 10.0s total. Includes per-shot clips, scene assemblies, and final clip.",
      "why": "Deterministic assembly from screenplay shot structure; no creative LLM decisions.",
      "context_note": "scope=global"
    },
    "agent_id": "VideoAgent",
    "task_id": "task_1_212d3481",
    "execution_id": "exec_4_90d4d494",
    "created_at": "2026-04-06T00:45:56.954133+00:00",
    "supersedes": null
  },
  {
    "content": {
      "what": "1 scene, no narration, each scene features bespoke music and ambience, delivered as a JSON object.",
      "why": "Moods are chosen to establish an understated, contemplative atmosphere for the initial placeholder scene. Audio style emphasizes subtle layering of atmospheric pads and gentle ambient sounds to create a foundational, non-intrusive sonic bed.",
      "context_note": "scope=global"
    },
    "agent_id": "AudioAgent",
    "task_id": "task_1_212d3481",
    "execution_id": "exec_5_bca4d9c4",
    "created_at": "2026-04-06T00:46:22.794687+00:00",
    "supersedes": null
  }
]
```
