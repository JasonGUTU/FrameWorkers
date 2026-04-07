# Global memory

Global memory for workspace `workspace_global_20260405_184827`. Records semantic decisions and project context — the 'why' behind agent outputs.
Artifact paths are in ``artifact_registry.jsonl`` (not here).

## Entries

```json
[
  {
    "content": {
      "what": "A poignant drama about a retired watchmaker racing against time on New Year's Eve to fix his late wife's cherished pocket watch. It features one main character and unfolds within a single, intimate scene.",
      "why": "The narrative aims for a reflective and hopeful tone, focusing on the character's internal struggle and connection to memory. The short duration dictates a highly concentrated, single-scene structure to maximize emotional impact.",
      "context_note": "scope=global"
    },
    "agent_id": "StoryAgent",
    "task_id": "task_1_32b8ce87",
    "execution_id": "exec_1_393677e0",
    "created_at": "2026-04-05T18:48:46.348518+00:00",
    "supersedes": null
  },
  {
    "content": {
      "what": "The Whispering Relic, 1 scene, 7 shots, mystical archaeological thriller style.",
      "why": "To establish a sense of mystery and discovery. Pacing starts slow and tense, builds to a reveal, then shifts to cautious excitement. Visuals focus on close-ups of ancient details and the relic's glowing effect to enhance mysticism.",
      "context_note": "scope=global"
    },
    "agent_id": "ScreenplayAgent",
    "task_id": "task_1_32b8ce87",
    "execution_id": "exec_2_4ece93ac",
    "created_at": "2026-04-05T18:49:28.711479+00:00",
    "supersedes": null
  },
  {
    "content": {
      "what": "3 entities (2 characters, 1 location), 3 canonical views, 3 keyframes, Mysterious, suspenseful visual style with heavy contrast.",
      "why": "Consistency is achieved by applying a core lighting and mood directive across all entity prompts. Key decisions include emphasizing high contrast, deep shadows, and specific atmospheric light sources like flickering torchlight to convey mystery and wonder. Character attire is detailed and practical, location textures are ancient and crumbling.",
      "context_note": "scope=global"
    },
    "agent_id": "KeyFrameAgent",
    "task_id": "task_1_32b8ce87",
    "execution_id": "exec_3_ab0e2813",
    "created_at": "2026-04-05T18:51:46.937273+00:00",
    "supersedes": null
  },
  {
    "content": {
      "what": "Video package: 1 scene(s), 7 shot clip(s), 27.0s total. Includes per-shot clips, scene assemblies, and final clip.",
      "why": "Deterministic assembly from screenplay shot structure; no creative LLM decisions.",
      "context_note": "scope=global"
    },
    "agent_id": "VideoAgent",
    "task_id": "task_1_32b8ce87",
    "execution_id": "exec_4_712efb78",
    "created_at": "2026-04-05T18:59:33.515174+00:00",
    "supersedes": null
  },
  {
    "content": {
      "what": "1 scene, 1 narration segment (as pre-built by system), 1 music track/1 ambience layer per scene, delivered as JSON descriptions.",
      "why": "Moods and ambience are chosen to create an evocative, reflective, and slightly melancholic atmosphere. The audio style prioritizes subtle emotional resonance and immersive environmental detailing, designed to complement and enhance potential narrative beats and character introspection, while ensuring clear space for any pre-built narration.",
      "context_note": "scope=global"
    },
    "agent_id": "AudioAgent",
    "task_id": "task_1_32b8ce87",
    "execution_id": "exec_5_5d364d2f",
    "created_at": "2026-04-05T19:00:02.828182+00:00",
    "supersedes": null
  }
]
```
