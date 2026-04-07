# Global memory

Global memory for workspace `workspace_global_20260405_191058`. Records semantic decisions and project context — the 'why' behind agent outputs.
Artifact paths are in ``artifact_registry.jsonl`` (not here).

## Entries

```json
[
  {
    "content": {
      "what": "This is a poignant micro-drama about Arthur, a retired watchmaker, who races against the clock on New Year's Eve to repair his late wife's cherished pocket watch. The story unfolds across three brief scenes, focusing on his delicate work and emotional connection.",
      "why": "The creative choices emphasize a tone of quiet urgency and profound nostalgia, using a minimalist structure to convey deep emotion within a very short duration. The focus is on the character's internal journey and the symbolic act of repair.",
      "context_note": "scope=global"
    },
    "agent_id": "StoryAgent",
    "task_id": "task_1_8cace241",
    "execution_id": "exec_1_f002a132",
    "created_at": "2026-04-05T19:11:17.212743+00:00",
    "supersedes": null
  },
  {
    "content": {
      "what": "The Watchmaker's Midnight, 3 scenes, 8 shots, intimate and poignant with warm, low-key lighting.",
      "why": "To convey Arthur's internal struggle and emotional journey, the pacing shifts from tense and urgent to serene. Visuals emphasize delicate work and the passage of time through static, focused close-ups on the watch and Arthur's expressions, contrasted with wider shots to establish the workshop and the imposing grandfather clock. The lighting transitions from dramatic low light to a softer, hopeful glow.",
      "context_note": "scope=global"
    },
    "agent_id": "ScreenplayAgent",
    "task_id": "task_1_8cace241",
    "execution_id": "exec_2_26768bf5",
    "created_at": "2026-04-05T19:12:11.071873+00:00",
    "supersedes": null
  },
  {
    "content": {
      "what": "1 character, 1 location, 2 props, 3 implied scenes, 4 Layer 1 keyframes. Visual style ranges from poignant to tense to serene.",
      "why": "Consistency is maintained through detailed entity descriptions across layers, with lighting and environment adapted to specific scene moods. Key visual decisions focus on Arthur's emotional journey and the symbolic passage of time via the watch and clock.",
      "context_note": "scope=global"
    },
    "agent_id": "KeyFrameAgent",
    "task_id": "task_1_8cace241",
    "execution_id": "exec_3_3f48025f",
    "created_at": "2026-04-05T19:14:29.189843+00:00",
    "supersedes": null
  },
  {
    "content": {
      "what": "Video package: 3 scene(s), 8 shot clip(s), 10.0s total. Includes per-shot clips, scene assemblies, and final clip.",
      "why": "Deterministic assembly from screenplay shot structure; no creative LLM decisions.",
      "context_note": "scope=global"
    },
    "agent_id": "VideoAgent",
    "task_id": "task_1_8cace241",
    "execution_id": "exec_4_20a992e9",
    "created_at": "2026-04-05T19:23:31.812113+00:00",
    "supersedes": null
  },
  {
    "content": {
      "what": "3 scenes, no narration segments, distinct music and ambience cues for each scene, delivered as a cohesive audio package.",
      "why": "Music and ambience are designed to follow Arthur's emotional arc: from focused determination and subtle tension, through escalating urgency and desperate hope, to agonizing suspense, culminating in profound serenity and hopeful closure, using the grandfather clock's presence as a recurring motif for time and pressure.",
      "context_note": "scope=global"
    },
    "agent_id": "AudioAgent",
    "task_id": "task_1_8cace241",
    "execution_id": "exec_5_bcb0c39c",
    "created_at": "2026-04-05T19:24:07.634918+00:00",
    "supersedes": null
  }
]
```
