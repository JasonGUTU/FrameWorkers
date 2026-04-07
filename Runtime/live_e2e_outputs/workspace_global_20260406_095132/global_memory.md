# Global memory

Global memory for workspace `workspace_global_20260406_095132`. Records semantic decisions and project context — the 'why' behind agent outputs.
Artifact paths are in ``artifact_registry.jsonl`` (not here).

## Entries

```json
[
  {
    "content": {
      "what": "A poignant drama focusing on a retired watchmaker, Arthur, as he races against time in a single scene to repair his late wife's cherished pocket watch before midnight on New Year's Eve.",
      "why": "The creative choices emphasize a melancholic yet hopeful tone, utilizing a tight, linear structure to convey the emotional weight of time and memory within a very short duration. The single scene intensifies the internal and external conflicts.",
      "context_note": "scope=global"
    },
    "agent_id": "StoryAgent",
    "task_id": "task_1_73d425f1",
    "execution_id": "exec_1_6fcb1356",
    "created_at": "2026-04-06T09:51:50.033637+00:00",
    "supersedes": null
  },
  {
    "content": {
      "what": "The Midnight Tick, 1 scene, 5 shots, intimate and melancholic visual style.",
      "why": "The creative decisions prioritize a tone that is initially urgent and melancholic, transitioning to bittersweet hope. Pacing is deliberate, building tension around the watch's repair before settling into a moment of quiet resolution. Visually, the approach emphasizes close-ups on Arthur's hands and the intricate watch, using warm, low lighting to create an intimate, reflective atmosphere, avoiding fast cuts to maintain focus on the internal journey.",
      "context_note": "scope=global"
    },
    "agent_id": "ScreenplayAgent",
    "task_id": "task_1_73d425f1",
    "execution_id": "exec_2_6b785058",
    "created_at": "2026-04-06T09:52:24.410447+00:00",
    "supersedes": null
  },
  {
    "content": {
      "what": "1 scenes, 5 shots, 5 shot keyframe stills; 1 character, 1 location, 3 props; 0 shot keyframes at L1; Visual style: Moody, warm, intimate, detailed, and reflective.",
      "why": "Style consistency is achieved by anchoring descriptions in 'Moody, warm, and intimate lighting' and 'focus on texture and worn quality.' Key visual decisions emphasize aged details, the precision of craftsmanship, and the emotional resonance of light and shadows.",
      "context_note": "scope=global"
    },
    "agent_id": "KeyFrameAgent",
    "task_id": "task_1_73d425f1",
    "execution_id": "exec_3_a97ef8a6",
    "created_at": "2026-04-06T09:55:13.173649+00:00",
    "supersedes": null
  },
  {
    "content": {
      "what": "Video package: 1 scene(s), 5 shot clip(s), 10.0s total. Includes per-shot clips, scene assemblies, and final clip.",
      "why": "Deterministic assembly from screenplay shot structure; no creative LLM decisions.",
      "context_note": "scope=global"
    },
    "agent_id": "VideoAgent",
    "task_id": "task_1_73d425f1",
    "execution_id": "exec_4_18b2c11d",
    "created_at": "2026-04-06T09:55:29.933334+00:00",
    "supersedes": null
  },
  {
    "content": {
      "what": "1 scene, 0 narration segments, 1 music track and 1 ambience track per scene, delivered as mixed stereo audio files.",
      "why": "Music choices emphasize Arthur's journey from melancholic urgency to bittersweet peace and hope. Ambience sets the intimate workshop scene, marking time with subtle distant New Year's sounds and the symbolic sounds of watch repair and renewal, culminating in the singular, hopeful watch tick.",
      "context_note": "scope=global"
    },
    "agent_id": "AudioAgent",
    "task_id": "task_1_73d425f1",
    "execution_id": "exec_5_259d4d1b",
    "created_at": "2026-04-06T09:56:08.879881+00:00",
    "supersedes": null
  }
]
```
