# Global memory

Global memory for workspace `workspace_global_20260406_014046`. Records semantic decisions and project context — the 'why' behind agent outputs.
Artifact paths are in ``artifact_registry.jsonl`` (not here).

## Entries

```json
[
  {
    "content": {
      "what": "This short drama features a retired watchmaker, Arthur, racing against time on New Year's Eve to repair his late wife's cherished pocket watch. The story unfolds across three brief scenes in his study.",
      "why": "The creative choices focus on a melancholic yet hopeful tone, using the race against time as a symbolic representation of grief and the yearning for connection. The structure is a simple progression from frantic work to a moment of serene resolution, emphasizing emotional impact over complex narrative.",
      "context_note": "scope=global"
    },
    "agent_id": "StoryAgent",
    "task_id": "task_1_2167090f",
    "execution_id": "exec_1_986fcd40",
    "created_at": "2026-04-06T01:41:04.341788+00:00",
    "supersedes": null
  },
  {
    "content": {
      "what": "The Midnight Mender, 3 scenes, 9 total shots, intimate, melancholic, determined, close-up focused visual style.",
      "why": "The creative decisions prioritize conveying Arthur's internal struggle and profound connection through meticulous detail. The tone shifts from tense and determined to peaceful and hopeful. Pacing is slow and deliberate in the beginning, building tension through close-ups and sound, then releasing into a moment of serene contemplation. The visual approach uses warm, focused lighting to highlight Arthur's work and expressions, contrasting with the soft shadows of his study, emphasizing his dedication and the intimate nature of his task.",
      "context_note": "scope=global"
    },
    "agent_id": "ScreenplayAgent",
    "task_id": "task_1_2167090f",
    "execution_id": "exec_2_9644c6d2",
    "created_at": "2026-04-06T01:41:47.335787+00:00",
    "supersedes": null
  },
  {
    "content": {
      "what": "1 character, 1 location, 3 props, 1 foundational scene, detailed and melancholic craftsmanship visual style.",
      "why": "Establishes the canonical appearance and physical characteristics of Arthur, his workshop, and the key props (watch, clock, tools) for visual consistency throughout all future keyframes. Key decisions emphasize Arthur's aged wisdom, the intricate nature of his craft, the lived-in detail of his workspace, and the symbolic presence of the heirloom watch and imposing clock.",
      "context_note": "scope=global"
    },
    "agent_id": "KeyFrameAgent",
    "task_id": "task_1_2167090f",
    "execution_id": "exec_3_13b25b64",
    "created_at": "2026-04-06T01:44:31.026759+00:00",
    "supersedes": null
  },
  {
    "content": {
      "what": "Video package: 3 scene(s), 9 shot clip(s), 10.0s total. Includes per-shot clips, scene assemblies, and final clip.",
      "why": "Deterministic assembly from screenplay shot structure; no creative LLM decisions.",
      "context_note": "scope=global"
    },
    "agent_id": "VideoAgent",
    "task_id": "task_1_2167090f",
    "execution_id": "exec_4_03ac1652",
    "created_at": "2026-04-06T01:44:41.390670+00:00",
    "supersedes": null
  },
  {
    "content": {
      "what": "3 scenes, 0 narration segments, dedicated music and ambience per scene, delivered as stereo audio mixes.",
      "why": "Music moods were chosen to dynamically underscore Arthur's emotional arc—from pensive determination and mounting tension to eventual peace and hopeful closure. Ambience was designed to emphasize the relentless passage of time through the ticking clock, creating an immersive and anxiety-inducing, then resolving, acoustic environment.",
      "context_note": "scope=global"
    },
    "agent_id": "AudioAgent",
    "task_id": "task_1_2167090f",
    "execution_id": "exec_5_f3500020",
    "created_at": "2026-04-06T01:45:14.915335+00:00",
    "supersedes": null
  }
]
```
