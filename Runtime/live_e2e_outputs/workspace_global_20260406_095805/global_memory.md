# Global memory

Global memory for workspace `workspace_global_20260406_095805`. Records semantic decisions and project context — the 'why' behind agent outputs.
Artifact paths are in ``artifact_registry.jsonl`` (not here).

## Entries

```json
[
  {
    "content": {
      "what": "A poignant drama about a retired watchmaker, John, attempting to repair his late wife's cherished pocket watch before the new year. It unfolds across three intimate scenes, focusing on his race against time and search for connection.",
      "why": "The tone is reflective and hopeful, emphasizing the emotional connection to objects and the passage of time. The structure is linear, building subtle tension towards a quiet, personal resolution. The style aims for a close, intimate portrayal of John's internal world.",
      "context_note": "scope=global"
    },
    "agent_id": "StoryAgent",
    "task_id": "task_1_1cc3f71c",
    "execution_id": "exec_1_ad123c37",
    "created_at": "2026-04-06T09:58:24.478773+00:00",
    "supersedes": null
  },
  {
    "content": {
      "what": "The Midnight Watchmaker, 3 scenes, 9 shots, intimate close-ups and soft, warm lighting.",
      "why": "The creative decisions prioritize an intimate and reflective tone, utilizing close-up shots to convey John's focused intensity and the delicate nature of his task. Pacing is deliberate, slowly building subtle tension towards the crisis point, then resolving with a peaceful, poignant emotional release. The visual approach emphasizes warm, low-key lighting to enhance the reflective atmosphere and highlight the antique details of the workshop and the cherished pocket watch.",
      "context_note": "scope=global"
    },
    "agent_id": "ScreenplayAgent",
    "task_id": "task_1_1cc3f71c",
    "execution_id": "exec_2_371f5151",
    "created_at": "2026-04-06T09:59:10.031010+00:00",
    "supersedes": null
  },
  {
    "content": {
      "what": "3 scenes, 9 shots, 9 shot keyframe stills; 1 character, 1 location, 6 props, detailed canonical look visual style.",
      "why": "Ensures foundational visual consistency by providing precise physical descriptions for each entity, emphasizing key details like age, material, and inherent state (e.g., broken, repaired).",
      "context_note": "scope=global"
    },
    "agent_id": "KeyFrameAgent",
    "task_id": "task_1_1cc3f71c",
    "execution_id": "exec_3_d18250d9",
    "created_at": "2026-04-06T10:01:33.398516+00:00",
    "supersedes": null
  },
  {
    "content": {
      "what": "Video package: 3 scene(s), 9 shot clip(s), 10.0s total. Includes per-shot clips, scene assemblies, and final clip.",
      "why": "Deterministic assembly from screenplay shot structure; no creative LLM decisions.",
      "context_note": "scope=global"
    },
    "agent_id": "VideoAgent",
    "task_id": "task_1_1cc3f71c",
    "execution_id": "exec_4_178edbf3",
    "created_at": "2026-04-06T10:01:53.952927+00:00",
    "supersedes": null
  },
  {
    "content": {
      "what": "3 scenes, 0 narration segments, dedicated music and layered ambience per scene, delivered as mixed stereo audio files.",
      "why": "Music is composed to follow the protagonist's emotional journey: starting with quiet determination and subtle melancholy, building tension and frustration, and resolving into a poignant sense of peace and bittersweet hope. Ambience reinforces the setting's solitude and the relentless passage of time, with the wall clock's ticking acting as a central motif driving the narrative urgency and eventual resolution.",
      "context_note": "scope=global"
    },
    "agent_id": "AudioAgent",
    "task_id": "task_1_1cc3f71c",
    "execution_id": "exec_5_8dff4e76",
    "created_at": "2026-04-06T10:02:44.781751+00:00",
    "supersedes": null
  }
]
```
