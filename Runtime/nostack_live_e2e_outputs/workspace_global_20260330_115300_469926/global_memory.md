# Global memory

Global memory for workspace `workspace_global_20260330_115300_469926`. The **Entries** section is the canonical JSON array. The **File tree** below is a **human-readable snapshot** at write time (may be truncated); for **automation** (persist paths, input packaging, Director), use **live** workspace file-tree APIs and ``artifact_locations`` — the snapshot is not authoritative.

## File tree

<!-- FW_FILE_TREE_BEGIN -->
```
.file_metadata.json
    nostack_e2e_asset_exec_1.json
global_memory.md
logs.jsonl
```
<!-- FW_FILE_TREE_END -->

## Entries

```json
[
  {
    "content": "nostack e2e global_memory summary",
    "agent_id": "NostackE2eAgent",
    "task_id": "nostack_embed_e2e_tid",
    "created_at": "2026-03-30T11:53:00.495566+00:00",
    "execution_result": {
      "status": "COMPLETED",
      "execution_id": "exec_1_95ba3c99",
      "persist_plan_meta": {
        "naming_policy_version": "v2.0",
        "persist_plan_digest": "7edfd71bf80724474a0497737baf9f7ca8037f1581dfb22230bd26ad7dc04446"
      }
    },
    "artifact_locations": [
      {
        "role": "nostack_e2e_asset",
        "path": "/home/zhendong_li/frameworkers/FrameWorkers/Runtime/nostack_live_e2e_outputs/workspace_global_20260330_115300_469926/artifacts/nostack_e2e_asset/nostack_e2e_asset_exec_1.json"
      }
    ]
  }
]
```
