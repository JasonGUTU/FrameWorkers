# Global memory

Global memory for workspace `workspace_e2e_text_with_image_20260407_010751`. Records semantic decisions and project context — the 'why' behind agent outputs.
Artifact paths are in ``artifact_registry.jsonl`` (not here).

## Entries

```json
[
  {
    "content": {
      "what": "natural-language brief from the user: \"30-second cinematic short about Elias, an elderly watchmaker, racing on New Year's Eve to repair his late wife's pocket\" (stated intent: creative brief for the project)",
      "why": "creative brief for the project",
      "context_note": "scope=global"
    },
    "agent_id": "IntakeTextAgent",
    "task_id": "task_1_90453eae",
    "execution_id": "exec_1_06ec00c9",
    "created_at": "2026-04-07T01:08:02.125515+00:00",
    "supersedes": null
  },
  {
    "content": {
      "what": "image showing An elderly, bearded man in a plaid shirt and apron meticulously works on a wooden mechanism with gears at a cluttered workbench. Warm light from a window on the left illuminates his focused face and hands, creating an industrious and calm mood.",
      "why": "this is the protagonist Elias — use as character reference",
      "context_note": "scope=global"
    },
    "agent_id": "IntakeImageAgent",
    "task_id": "task_1_90453eae",
    "execution_id": "exec_2_5ab9f754",
    "created_at": "2026-04-07T01:08:22.690175+00:00",
    "supersedes": null
  }
]
```
