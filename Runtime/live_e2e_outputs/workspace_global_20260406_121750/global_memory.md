# Global memory

Global memory for workspace `workspace_global_20260406_121750`. Records semantic decisions and project context — the 'why' behind agent outputs.
Artifact paths are in ``artifact_registry.jsonl`` (not here).

## Entries

```json
[
  {
    "content": {
      "what": "This is a poignant drama about a retired watchmaker, Arthur, racing against the New Year's chime to repair his late wife's cherished pocket watch. It features one character and two brief, connected scenes.",
      "why": "The creative choices focus on evoking a sense of quiet determination and emotional connection through visual storytelling. The tone is melancholic yet hopeful, emphasizing Arthur's precision and the symbolic race against time to honor a memory.",
      "context_note": "scope=global"
    },
    "agent_id": "StoryAgent",
    "task_id": "task_1_2d60f672",
    "execution_id": "exec_1_b910f2bc",
    "created_at": "2026-04-06T12:18:02.601837+00:00",
    "supersedes": null
  },
  {
    "content": {
      "what": "The Watchmaker's Midnight, 2 scenes, 11 shots, detailed close-ups and warm, intimate lighting.",
      "why": "The narrative emphasizes Arthur's meticulous precision and internal struggle. Pacing starts deliberate and tense, building to a moment of release. Visually, a focus on extreme close-ups of the watch mechanisms and Arthur's hands highlights the intricate work and his dedication. Warm, soft lighting creates an intimate, slightly melancholic but ultimately hopeful atmosphere, contrasting the old workshop with the spark of new life.",
      "context_note": "scope=global"
    },
    "agent_id": "ScreenplayAgent",
    "task_id": "task_1_2d60f672",
    "execution_id": "exec_2_b7a1e6b5",
    "created_at": "2026-04-06T12:18:52.114101+00:00",
    "supersedes": null
  },
  {
    "content": {
      "what": "A keyframe planning document covering 2 scenes and 11 shots. For each shot in the screenplay it provides a textual description of the planned starting frame and a separate motion hint describing how that frame should move when animated. It also catalogs the visual identity references (characters, locations, props) used to keep imagery consistent. Used by the video step to fetch the prompt and motion intent for each shot. 4 entities (1 character, 1 location, 2 props), canonical look defined, melancholic yet hopeful visual style.",
      "why": "Maintaining a consistent visual identity across all elements; focusing on Arthur's internal state, a detailed and aged workshop, and symbolic props, all unified by warm, intimate, and melancholic lighting with deep shadows.",
      "context_note": "scope=global"
    },
    "agent_id": "KeyFrameAgent",
    "task_id": "task_1_2d60f672",
    "execution_id": "exec_3_85c9a495",
    "created_at": "2026-04-06T12:25:55.151649+00:00",
    "supersedes": null
  }
]
```
