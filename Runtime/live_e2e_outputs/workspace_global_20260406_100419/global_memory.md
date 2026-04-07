# Global memory

Global memory for workspace `workspace_global_20260406_100419`. Records semantic decisions and project context — the 'why' behind agent outputs.
Artifact paths are in ``artifact_registry.jsonl`` (not here).

## Entries

```json
[
  {
    "content": {
      "what": "This is a poignant drama short featuring a retired watchmaker racing against time in his workshop to repair his late wife's cherished pocket watch before the new year, in a single, focused scene.",
      "why": "The creative choices emphasize a reflective and hopeful tone, using a simple, linear narrative structure to highlight the protagonist's emotional journey towards peace and connection through a symbolic act of repair.",
      "context_note": "scope=global"
    },
    "agent_id": "StoryAgent",
    "task_id": "task_1_a04ec51c",
    "execution_id": "exec_1_ab97450d",
    "created_at": "2026-04-06T10:04:36.329179+00:00",
    "supersedes": null
  },
  {
    "content": {
      "what": "The Final Tick, 3 scenes, 8 shots, Poignant Intimate Realism",
      "why": "The creative decisions prioritize an intimate, poignant tone to match the story's emotional core. Pacing is deliberate, building tension through Arthur's meticulous work, then resolving into peaceful reflection. Visually, the approach focuses on close-ups of hands, tools, and the watch to emphasize the intricate craft and Arthur's emotional connection, using warm, soft lighting to create an intimate atmosphere befitting the 'slice of life' drama.",
      "context_note": "scope=global"
    },
    "agent_id": "ScreenplayAgent",
    "task_id": "task_1_a04ec51c",
    "execution_id": "exec_2_f529abb0",
    "created_at": "2026-04-06T10:05:20.106179+00:00",
    "supersedes": null
  },
  {
    "content": {
      "what": "A keyframe planning document covering 3 scenes and 6 shots. For each shot in the screenplay it provides a textual description of the planned starting frame and a separate motion hint describing how that frame should move when animated. It also catalogs the visual identity references (characters, locations, props) used to keep imagery consistent. Used by the video step to fetch the prompt and motion intent for each shot. 1 character, 1 location, 3 props; 1 scene; 5 shot keyframes; poignant, intimate, soft warm lighting visual style.",
      "why": "Style consistency is maintained across all entities by adhering to the overarching poignant, intimate tone and soft, warm lighting. Key visual decisions emphasize Arthur's weathered precision, the workshop's cozy clutter, and the intricate detail of the cherished watch and tools, all contributing to a sense of melancholy and hope.",
      "context_note": "scope=global"
    },
    "agent_id": "KeyFrameAgent",
    "task_id": "task_1_a04ec51c",
    "execution_id": "exec_3_a9532635",
    "created_at": "2026-04-06T10:08:50.603770+00:00",
    "supersedes": null
  },
  {
    "content": {
      "what": "A manifest of the assembled video for the whole story: 3 scene(s), 6 shot clip(s), 10.0 seconds total runtime. It catalogs the per-shot clips, the per-scene cuts, and the single complete final video file. It is the document describing the finished video; downstream audio mixing reads it to mux audio against the final video file.",
      "why": "Deterministic assembly from screenplay shot structure; no creative LLM decisions.",
      "context_note": "scope=global"
    },
    "agent_id": "VideoAgent",
    "task_id": "task_1_a04ec51c",
    "execution_id": "exec_4_34e83324",
    "created_at": "2026-04-06T10:19:58.932275+00:00",
    "supersedes": null
  },
  {
    "content": {
      "what": "3 scenes, music and ambience provided for each scene, standard audio file delivery.",
      "why": "To underscore Arthur's emotional journey from delicate tension and a race against time, through intense urgency, to a final moment of peaceful resolution and profound connection. Audio style prioritizes intimate sound design around the watch's mechanics and a dynamic musical score, employing the watch's ticking as a persistent, evolving motif.",
      "context_note": "scope=global"
    },
    "agent_id": "AudioAgent",
    "task_id": "task_1_a04ec51c",
    "execution_id": "exec_5_5b269900",
    "created_at": "2026-04-06T10:20:44.602801+00:00",
    "supersedes": null
  }
]
```
