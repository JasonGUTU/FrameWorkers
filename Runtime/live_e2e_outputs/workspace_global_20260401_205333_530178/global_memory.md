# Global memory

Global memory for workspace `workspace_global_20260401_205333_530178`. The **Entries** section is the canonical JSON array. The **File tree** below is a **human-readable snapshot** at write time (may be truncated); for **automation** (persist paths, input packaging, Director), use **live** workspace file-tree APIs and ``artifact_locations`` — the snapshot is not authoritative.

## File tree

<!-- FW_FILE_TREE_BEGIN -->
```
.file_metadata.json
    keyframes_exec_4.json
    keyframes_manifest.json
        img_char_001_global.png
        img_char_001_sc_001.png
        img_loc_001_global.png
        img_loc_001_sc_001.png
        img_sh_001_kf_01.png
        img_sh_002_kf_01.png
        img_sh_003_kf_01.png
        img_sh_004_kf_01.png
        img_sh_005_kf_01.png
        img_sh_005_kf_02.png
        img_sh_006_kf_01.png
        img_sh_006_kf_02.png
    screenplay_exec_2.json
    story_blueprint_exec_1.json
    storyboard_exec_3.json
global_memory.md
logs.jsonl
```
<!-- FW_FILE_TREE_END -->

## Entries

```json
[
  {
    "content": "global_memory test summary",
    "agent_id": "StoryAgent",
    "task_id": "task_1_cfaab40a",
    "created_at": "2026-04-01T20:53:53.798027+00:00",
    "execution_result": {
      "status": "COMPLETED",
      "execution_id": "exec_1_b09ad41c",
      "persist_plan_meta": {
        "naming_policy_version": "v2.0",
        "persist_plan_digest": "6c2d2fa50e274fab1be638135b232c545f1fd7af0c52e93419bb8ec0f7e16019"
      }
    },
    "artifact_locations": [
      {
        "role": "story_blueprint",
        "path": "/home/zhendong_li/test_frameworkers/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260401_205333_530178/artifacts/story_blueprint/story_blueprint_exec_1.json"
      }
    ]
  },
  {
    "content": "global_memory test summary",
    "agent_id": "ScreenplayAgent",
    "task_id": "task_1_cfaab40a",
    "created_at": "2026-04-01T20:54:15.670519+00:00",
    "execution_result": {
      "status": "COMPLETED",
      "execution_id": "exec_2_5319d80c",
      "persist_plan_meta": {
        "naming_policy_version": "v2.0",
        "persist_plan_digest": "a5d423292a40d92997772983c9c2b6dd4bc9a9c5f5a3a16c6f03045e50d7fe23"
      }
    },
    "artifact_locations": [
      {
        "role": "screenplay",
        "path": "/home/zhendong_li/test_frameworkers/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260401_205333_530178/artifacts/screenplay/screenplay_exec_2.json"
      }
    ]
  },
  {
    "content": "global_memory test summary",
    "agent_id": "StoryboardAgent",
    "task_id": "task_1_cfaab40a",
    "created_at": "2026-04-01T20:55:17.440622+00:00",
    "execution_result": {
      "status": "COMPLETED",
      "execution_id": "exec_3_bdae85f7",
      "persist_plan_meta": {
        "naming_policy_version": "v2.0",
        "persist_plan_digest": "b8496c8aa7ae60e89c51e35bcaa5dd6adde90635a7df6acd8d5179eaf49ba712"
      }
    },
    "artifact_locations": [
      {
        "role": "storyboard",
        "path": "/home/zhendong_li/test_frameworkers/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260401_205333_530178/artifacts/storyboard/storyboard_exec_3.json"
      }
    ]
  },
  {
    "content": "global_memory test summary",
    "agent_id": "KeyFrameAgent",
    "task_id": "task_1_cfaab40a",
    "created_at": "2026-04-01T20:55:56.800994+00:00",
    "execution_result": {
      "status": "COMPLETED",
      "execution_id": "exec_4_04641f94",
      "persist_plan_meta": {
        "naming_policy_version": "v2.0",
        "persist_plan_digest": "0e1e078dee260082dcabe054e01a6ab843d4c1e5de7de660cd8601e810c8f3d9"
      }
    },
    "artifact_locations": [
      {
        "role": "keyframes",
        "path": "/home/zhendong_li/test_frameworkers/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260401_205333_530178/artifacts/keyframes/keyframes_exec_4.json"
      },
      {
        "role": "img_loc_001_global",
        "path": "/home/zhendong_li/test_frameworkers/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260401_205333_530178/artifacts/media/KeyFrameAgent/image/img_loc_001_global.png"
      },
      {
        "role": "img_char_001_global",
        "path": "/home/zhendong_li/test_frameworkers/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260401_205333_530178/artifacts/media/KeyFrameAgent/image/img_char_001_global.png"
      },
      {
        "role": "img_char_001_sc_001",
        "path": "/home/zhendong_li/test_frameworkers/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260401_205333_530178/artifacts/media/KeyFrameAgent/image/img_char_001_sc_001.png"
      },
      {
        "role": "img_loc_001_sc_001",
        "path": "/home/zhendong_li/test_frameworkers/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260401_205333_530178/artifacts/media/KeyFrameAgent/image/img_loc_001_sc_001.png"
      },
      {
        "role": "img_sh_001_kf_01",
        "path": "/home/zhendong_li/test_frameworkers/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260401_205333_530178/artifacts/media/KeyFrameAgent/image/img_sh_001_kf_01.png"
      },
      {
        "role": "img_sh_002_kf_01",
        "path": "/home/zhendong_li/test_frameworkers/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260401_205333_530178/artifacts/media/KeyFrameAgent/image/img_sh_002_kf_01.png"
      },
      {
        "role": "img_sh_006_kf_02",
        "path": "/home/zhendong_li/test_frameworkers/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260401_205333_530178/artifacts/media/KeyFrameAgent/image/img_sh_006_kf_02.png"
      },
      {
        "role": "img_sh_005_kf_02",
        "path": "/home/zhendong_li/test_frameworkers/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260401_205333_530178/artifacts/media/KeyFrameAgent/image/img_sh_005_kf_02.png"
      },
      {
        "role": "img_sh_006_kf_01",
        "path": "/home/zhendong_li/test_frameworkers/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260401_205333_530178/artifacts/media/KeyFrameAgent/image/img_sh_006_kf_01.png"
      },
      {
        "role": "img_sh_004_kf_01",
        "path": "/home/zhendong_li/test_frameworkers/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260401_205333_530178/artifacts/media/KeyFrameAgent/image/img_sh_004_kf_01.png"
      },
      {
        "role": "img_sh_005_kf_01",
        "path": "/home/zhendong_li/test_frameworkers/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260401_205333_530178/artifacts/media/KeyFrameAgent/image/img_sh_005_kf_01.png"
      },
      {
        "role": "img_sh_003_kf_01",
        "path": "/home/zhendong_li/test_frameworkers/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260401_205333_530178/artifacts/media/KeyFrameAgent/image/img_sh_003_kf_01.png"
      },
      {
        "role": "keyframes_manifest",
        "path": "/home/zhendong_li/test_frameworkers/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260401_205333_530178/artifacts/keyframes/keyframes_manifest.json"
      }
    ]
  }
]
```
