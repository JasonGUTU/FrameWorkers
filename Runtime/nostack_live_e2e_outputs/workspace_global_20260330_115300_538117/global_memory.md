# Global memory

Global memory for workspace `workspace_global_20260330_115300_538117`. The **Entries** section is the canonical JSON array. The **File tree** below is a **human-readable snapshot** at write time (may be truncated); for **automation** (persist paths, input packaging, Director), use **live** workspace file-tree APIs and ``artifact_locations`` — the snapshot is not authoritative.

## File tree

<!-- FW_FILE_TREE_BEGIN -->
```
.file_metadata.json
    nostack_live_e2e_tid_story_blueprint_exec_1.json
global_memory.md
logs.jsonl
```
<!-- FW_FILE_TREE_END -->

## Entries

```json
[
  {
    "content": "A Story Blueprint was generated, outlining a quiet, emotionally resonant narrative about an elderly librarian whose routine is disrupted by a sentimental note, expertly detailing characters, locations, and a three-act story arc.",
    "agent_id": "StoryAgent",
    "task_id": "nostack_live_e2e_tid",
    "created_at": "2026-03-30T11:53:34.096251+00:00",
    "execution_result": {
      "status": "COMPLETED",
      "execution_id": "exec_1_47feb67b",
      "persist_plan_meta": {
        "naming_policy_version": "v2.0",
        "persist_plan_digest": "723eac71bb0210975c032c63b1a4543c5b9107fd28054524c33f6e319da8806e"
      },
      "artifact_briefs": [
        {
          "path": "nostack_live_e2e_tid_story_blueprint_exec_1.json",
          "brief": "Story Blueprint"
        }
      ]
    },
    "artifact_locations": [
      {
        "role": "story_blueprint",
        "path": "/home/zhendong_li/frameworkers/FrameWorkers/Runtime/nostack_live_e2e_outputs/workspace_global_20260330_115300_538117/artifacts/story_blueprint/nostack_live_e2e_tid_story_blueprint_exec_1.json"
      }
    ]
  }
]
```
