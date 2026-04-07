# Global memory

Global memory for workspace `workspace_global_20260406_021153`. Records semantic decisions and project context — the 'why' behind agent outputs.
Artifact paths are in ``artifact_registry.jsonl`` (not here).

## Entries

```json
[
  {
    "content": {
      "what": "A dramatic short film about Elias, a retired watchmaker, racing against time to repair his late wife's cherished pocket watch on New Year's Eve. The story unfolds in a single, intimate scene.",
      "why": "The creative choices emphasize emotional resonance and tension, using a tight timeframe and a focused setting to highlight the protagonist's personal struggle and his yearning for connection and peace.",
      "context_note": "scope=global"
    },
    "agent_id": "StoryAgent",
    "task_id": "task_1_981db100",
    "execution_id": "exec_1_f8736128",
    "created_at": "2026-04-06T02:12:09.165830+00:00",
    "supersedes": null
  },
  {
    "content": {
      "what": "The Midnight Ticker, 1 scene, 6 shots, Poetic Realism with close-ups and intimate framing.",
      "why": "The creative decisions focus on building tension through tight framing on Elias's intricate work and the ticking clock, then transitioning to a poignant, hopeful tone with wider shots and subtle expressions of closure. The pacing moves from urgent to reflective, emphasizing the emotional journey.",
      "context_note": "scope=global"
    },
    "agent_id": "ScreenplayAgent",
    "task_id": "task_1_981db100",
    "execution_id": "exec_2_e45faf08",
    "created_at": "2026-04-06T02:12:42.558382+00:00",
    "supersedes": null
  },
  {
    "content": {
      "what": "1 scenes, 6 shots, 6 shot keyframe stills; 4 entities (1 character, 1 location, 2 props), 1 scene, 4 keyframes, a poignant, reflective visual style with muted colors and warm practical lighting.",
      "why": "Each L1 prompt establishes the canonical physical appearance and inherent qualities of its entity. Key visual decisions focus on intricate details, the interplay of light and shadow, and conveying the core essence of each element to support a consistent poignant and reflective tone.",
      "context_note": "scope=global"
    },
    "agent_id": "KeyFrameAgent",
    "task_id": "task_1_981db100",
    "execution_id": "exec_3_f4866697",
    "created_at": "2026-04-06T02:15:06.452541+00:00",
    "supersedes": null
  },
  {
    "content": {
      "what": "Video package: 1 scene(s), 6 shot clip(s), 10.0s total. Includes per-shot clips, scene assemblies, and final clip.",
      "why": "Deterministic assembly from screenplay shot structure; no creative LLM decisions.",
      "context_note": "scope=global"
    },
    "agent_id": "VideoAgent",
    "task_id": "task_1_981db100",
    "execution_id": "exec_4_8883d9c5",
    "created_at": "2026-04-06T02:21:18.882403+00:00",
    "supersedes": null
  },
  {
    "content": {
      "what": "1 scene, no narration segments, 1 music cue and 1 ambience track per scene, delivered as WAV/MP3 audio assets.",
      "why": "Music mood keywords chosen to reflect Elias's evolving emotional journey from melancholic determination to serene, hopeful resolution, providing a clear narrative arc for the single cue. Ambience prioritizes the intricate, intimate sounds of the workshop and timekeeping, building tension and then offering a moment of symbolic release with the prominent grandfather clock chimes.",
      "context_note": "scope=global"
    },
    "agent_id": "AudioAgent",
    "task_id": "task_1_981db100",
    "execution_id": "exec_5_2e3d2387",
    "created_at": "2026-04-06T02:22:01.400401+00:00",
    "supersedes": null
  }
]
```
