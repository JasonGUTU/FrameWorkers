# Global memory

Global memory for workspace `workspace_e2e_midstream_image_20260407_010248`. Records semantic decisions and project context — the 'why' behind agent outputs.
Artifact paths are in ``artifact_registry.jsonl`` (not here).

## Entries

```json
[
  {
    "content": {
      "what": "natural-language brief from the user: \"30-second cinematic short about Mei, a young female street muralist in her late twenties, painting a giant mural of a ph\" (stated intent: initial creative brief — young female street muralist)",
      "why": "initial creative brief — young female street muralist",
      "context_note": "scope=global"
    },
    "agent_id": "IntakeTextAgent",
    "task_id": "task_1_9d793710",
    "execution_id": "exec_1_8bb5b992",
    "created_at": "2026-04-07T01:02:56.727016+00:00",
    "supersedes": null
  },
  {
    "content": {
      "what": "A cyberpunk urban drama featuring Mei, a determined street artist, as she battles the elements to paint a vibrant phoenix mural on a rain-soaked alley wall at midnight. The story unfolds within a single compelling scene.",
      "why": "The narrative embraces a neo-noir, atmospheric tone, emphasizing visual aesthetics and Mei's solitary struggle and artistic passion. A single scene structure maintains a tight focus on the core act of creation amidst an evocative, challenging environment.",
      "context_note": "scope=global"
    },
    "agent_id": "StoryAgent",
    "task_id": "task_1_9d793710",
    "execution_id": "exec_2_172ac80f",
    "created_at": "2026-04-07T01:03:28.021576+00:00",
    "supersedes": null
  },
  {
    "content": {
      "what": "Neon Phoenix; 1 scene, 5 shots, Cyberpunk Gritty & Vibrant visual style.",
      "why": "This screenplay focuses on the intense contrast between the gritty, rain-soaked cyberpunk environment and the vibrant, life-affirming art Mei creates. Pacing is slow and atmospheric, emphasizing Mei's determination and the visual spectacle of the mural coming to life under neon lights. Visuals will be high-contrast, moody, and rich with color reflections.",
      "context_note": "scope=global"
    },
    "agent_id": "ScreenplayAgent",
    "task_id": "task_1_9d793710",
    "execution_id": "exec_3_f9bab53d",
    "created_at": "2026-04-07T01:04:13.720253+00:00",
    "supersedes": null
  },
  {
    "content": {
      "what": "image (vision LLM returned no description)",
      "why": "finally adding the protagonist reference",
      "context_note": "scope=global"
    },
    "agent_id": "IntakeImageAgent",
    "task_id": "task_1_9d793710",
    "execution_id": "exec_4_15ad17e4",
    "created_at": "2026-04-07T01:04:28.061382+00:00",
    "supersedes": null
  },
  {
    "content": {
      "what": "Phoenix Neon Rise; 1 scene, 5 shots; Cyberpunk, Gritty, Vibrant Visual Style",
      "why": "This screenplay aims for a gritty, atmospheric, yet ultimately triumphant tone. Pacing is deliberate, allowing the viewer to feel Mei's struggle against the elements and her determined focus on the art. The visual approach contrasts the harsh, rain-soaked cyberpunk alley with the vibrant, almost mystical glow of the emerging phoenix mural, emphasizing themes of resilience and creativity in a challenging world.",
      "context_note": "scope=global"
    },
    "agent_id": "ScreenplayAgent",
    "task_id": "task_1_9d793710",
    "execution_id": "exec_5_5202fd3d",
    "created_at": "2026-04-07T01:05:06.522416+00:00",
    "supersedes": null
  }
]
```
