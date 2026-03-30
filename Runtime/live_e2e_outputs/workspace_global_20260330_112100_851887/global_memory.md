# Global memory

Global memory for workspace `workspace_global_20260330_112100_851887`. The **Entries** section is the canonical JSON array. The **File tree** below is a **human-readable snapshot** at write time (may be truncated); for **automation** (persist paths, input packaging, Director), use **live** workspace file-tree APIs and ``artifact_locations`` — the snapshot is not authoritative.

## File tree

<!-- FW_FILE_TREE_BEGIN -->
```
.file_metadata.json
    keyframes_exec_4.json
    keyframes_manifest.json
        img_char_001_global.png
        img_char_001_sc_001.png
        img_char_001_sc_002.png
        img_char_001_sc_003.png
        img_loc_001_global.png
        img_loc_001_sc_001.png
        img_loc_001_sc_002.png
        img_loc_001_sc_003.png
        img_sh_001_kf_01.png
        img_sh_002_kf_01.png
        img_sh_003_kf_01.png
        img_sh_003_kf_02.png
        img_sh_004_kf_01.png
        img_sh_005_kf_01.png
        img_sh_005_kf_02.png
        img_sh_006_kf_01.png
        img_sh_006_kf_02.png
        img_sh_007_kf_01.png
        img_sh_007_kf_02.png
        img_sh_008_kf_01.png
        img_sh_009_kf_01.png
        clip_final.mp4
        clip_sc_001.mp4
        clip_sc_002.mp4
        clip_sc_003.mp4
        clip_sh_001.mp4
        clip_sh_002.mp4
        clip_sh_003.mp4
        clip_sh_004.mp4
        clip_sh_005.mp4
        clip_sh_006.mp4
        clip_sh_007.mp4
        clip_sh_008.mp4
        clip_sh_009.mp4
    screenplay_exec_2.json
    story_blueprint_exec_1.json
    storyboard_exec_3.json
    video_exec_5.json
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
    "task_id": "task_1_f46573a1",
    "created_at": "2026-03-30T11:21:23.550924+00:00",
    "execution_result": {
      "status": "COMPLETED",
      "execution_id": "exec_1_5cc5ea60",
      "persist_plan_meta": {
        "naming_policy_version": "v2.0",
        "persist_plan_digest": "6c2d2fa50e274fab1be638135b232c545f1fd7af0c52e93419bb8ec0f7e16019"
      }
    },
    "artifact_locations": [
      {
        "role": "story_blueprint",
        "path": "/home/zhendong_li/frameworkers/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260330_112100_851887/artifacts/story_blueprint/story_blueprint_exec_1.json"
      }
    ]
  },
  {
    "content": "global_memory test summary",
    "agent_id": "ScreenplayAgent",
    "task_id": "task_1_f46573a1",
    "created_at": "2026-03-30T11:21:50.279945+00:00",
    "execution_result": {
      "status": "COMPLETED",
      "execution_id": "exec_2_fa76b18e",
      "persist_plan_meta": {
        "naming_policy_version": "v2.0",
        "persist_plan_digest": "a5d423292a40d92997772983c9c2b6dd4bc9a9c5f5a3a16c6f03045e50d7fe23"
      }
    },
    "artifact_locations": [
      {
        "role": "screenplay",
        "path": "/home/zhendong_li/frameworkers/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260330_112100_851887/artifacts/screenplay/screenplay_exec_2.json"
      }
    ]
  },
  {
    "content": "global_memory test summary",
    "agent_id": "StoryboardAgent",
    "task_id": "task_1_f46573a1",
    "created_at": "2026-03-30T11:22:24.624345+00:00",
    "execution_result": {
      "status": "COMPLETED",
      "execution_id": "exec_3_01527d32",
      "persist_plan_meta": {
        "naming_policy_version": "v2.0",
        "persist_plan_digest": "b8496c8aa7ae60e89c51e35bcaa5dd6adde90635a7df6acd8d5179eaf49ba712"
      }
    },
    "artifact_locations": [
      {
        "role": "storyboard",
        "path": "/home/zhendong_li/frameworkers/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260330_112100_851887/artifacts/storyboard/storyboard_exec_3.json"
      }
    ]
  },
  {
    "content": "global_memory test summary",
    "agent_id": "KeyFrameAgent",
    "task_id": "task_1_f46573a1",
    "created_at": "2026-03-30T11:23:02.304586+00:00",
    "execution_result": {
      "status": "COMPLETED",
      "execution_id": "exec_4_d82d864d",
      "persist_plan_meta": {
        "naming_policy_version": "v2.0",
        "persist_plan_digest": "fd75b4d7ace1647c3cf8e089805a9fd8bdd3832658277a4a0c91c9f4fcfbb868"
      }
    },
    "artifact_locations": [
      {
        "role": "keyframes",
        "path": "/home/zhendong_li/frameworkers/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260330_112100_851887/artifacts/keyframes/keyframes_exec_4.json"
      },
      {
        "role": "img_char_001_global",
        "path": "/home/zhendong_li/frameworkers/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260330_112100_851887/artifacts/media/KeyFrameAgent/image/img_char_001_global.png"
      },
      {
        "role": "img_loc_001_global",
        "path": "/home/zhendong_li/frameworkers/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260330_112100_851887/artifacts/media/KeyFrameAgent/image/img_loc_001_global.png"
      },
      {
        "role": "img_char_001_sc_001",
        "path": "/home/zhendong_li/frameworkers/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260330_112100_851887/artifacts/media/KeyFrameAgent/image/img_char_001_sc_001.png"
      },
      {
        "role": "img_loc_001_sc_001",
        "path": "/home/zhendong_li/frameworkers/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260330_112100_851887/artifacts/media/KeyFrameAgent/image/img_loc_001_sc_001.png"
      },
      {
        "role": "img_loc_001_sc_002",
        "path": "/home/zhendong_li/frameworkers/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260330_112100_851887/artifacts/media/KeyFrameAgent/image/img_loc_001_sc_002.png"
      },
      {
        "role": "img_char_001_sc_003",
        "path": "/home/zhendong_li/frameworkers/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260330_112100_851887/artifacts/media/KeyFrameAgent/image/img_char_001_sc_003.png"
      },
      {
        "role": "img_loc_001_sc_003",
        "path": "/home/zhendong_li/frameworkers/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260330_112100_851887/artifacts/media/KeyFrameAgent/image/img_loc_001_sc_003.png"
      },
      {
        "role": "img_char_001_sc_002",
        "path": "/home/zhendong_li/frameworkers/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260330_112100_851887/artifacts/media/KeyFrameAgent/image/img_char_001_sc_002.png"
      },
      {
        "role": "img_sh_004_kf_01",
        "path": "/home/zhendong_li/frameworkers/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260330_112100_851887/artifacts/media/KeyFrameAgent/image/img_sh_004_kf_01.png"
      },
      {
        "role": "img_sh_005_kf_01",
        "path": "/home/zhendong_li/frameworkers/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260330_112100_851887/artifacts/media/KeyFrameAgent/image/img_sh_005_kf_01.png"
      },
      {
        "role": "img_sh_002_kf_01",
        "path": "/home/zhendong_li/frameworkers/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260330_112100_851887/artifacts/media/KeyFrameAgent/image/img_sh_002_kf_01.png"
      },
      {
        "role": "img_sh_003_kf_01",
        "path": "/home/zhendong_li/frameworkers/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260330_112100_851887/artifacts/media/KeyFrameAgent/image/img_sh_003_kf_01.png"
      },
      {
        "role": "img_sh_001_kf_01",
        "path": "/home/zhendong_li/frameworkers/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260330_112100_851887/artifacts/media/KeyFrameAgent/image/img_sh_001_kf_01.png"
      },
      {
        "role": "img_sh_006_kf_02",
        "path": "/home/zhendong_li/frameworkers/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260330_112100_851887/artifacts/media/KeyFrameAgent/image/img_sh_006_kf_02.png"
      },
      {
        "role": "img_sh_008_kf_01",
        "path": "/home/zhendong_li/frameworkers/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260330_112100_851887/artifacts/media/KeyFrameAgent/image/img_sh_008_kf_01.png"
      },
      {
        "role": "img_sh_007_kf_01",
        "path": "/home/zhendong_li/frameworkers/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260330_112100_851887/artifacts/media/KeyFrameAgent/image/img_sh_007_kf_01.png"
      },
      {
        "role": "img_sh_006_kf_01",
        "path": "/home/zhendong_li/frameworkers/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260330_112100_851887/artifacts/media/KeyFrameAgent/image/img_sh_006_kf_01.png"
      },
      {
        "role": "img_sh_005_kf_02",
        "path": "/home/zhendong_li/frameworkers/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260330_112100_851887/artifacts/media/KeyFrameAgent/image/img_sh_005_kf_02.png"
      },
      {
        "role": "img_sh_009_kf_01",
        "path": "/home/zhendong_li/frameworkers/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260330_112100_851887/artifacts/media/KeyFrameAgent/image/img_sh_009_kf_01.png"
      },
      {
        "role": "img_sh_007_kf_02",
        "path": "/home/zhendong_li/frameworkers/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260330_112100_851887/artifacts/media/KeyFrameAgent/image/img_sh_007_kf_02.png"
      },
      {
        "role": "img_sh_003_kf_02",
        "path": "/home/zhendong_li/frameworkers/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260330_112100_851887/artifacts/media/KeyFrameAgent/image/img_sh_003_kf_02.png"
      },
      {
        "role": "keyframes_manifest",
        "path": "/home/zhendong_li/frameworkers/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260330_112100_851887/artifacts/keyframes/keyframes_manifest.json"
      }
    ]
  },
  {
    "content": "global_memory test summary",
    "agent_id": "VideoAgent",
    "task_id": "task_1_f46573a1",
    "created_at": "2026-03-30T11:44:47.497730+00:00",
    "execution_result": {
      "status": "COMPLETED",
      "execution_id": "exec_5_95e69d0a",
      "persist_plan_meta": {
        "naming_policy_version": "v2.0",
        "persist_plan_digest": "f7e95fd224b44a8afaeec3360d20b4342256379800bd020bb5f32733d04d26bf"
      }
    },
    "artifact_locations": [
      {
        "role": "video",
        "path": "/home/zhendong_li/frameworkers/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260330_112100_851887/artifacts/video/video_exec_5.json"
      },
      {
        "role": "clip_sh_001",
        "path": "/home/zhendong_li/frameworkers/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260330_112100_851887/artifacts/media/VideoAgent/video/clip_sh_001.mp4"
      },
      {
        "role": "clip_sh_002",
        "path": "/home/zhendong_li/frameworkers/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260330_112100_851887/artifacts/media/VideoAgent/video/clip_sh_002.mp4"
      },
      {
        "role": "clip_sh_003",
        "path": "/home/zhendong_li/frameworkers/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260330_112100_851887/artifacts/media/VideoAgent/video/clip_sh_003.mp4"
      },
      {
        "role": "clip_sc_001",
        "path": "/home/zhendong_li/frameworkers/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260330_112100_851887/artifacts/media/VideoAgent/video/clip_sc_001.mp4"
      },
      {
        "role": "clip_sh_004",
        "path": "/home/zhendong_li/frameworkers/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260330_112100_851887/artifacts/media/VideoAgent/video/clip_sh_004.mp4"
      },
      {
        "role": "clip_sh_005",
        "path": "/home/zhendong_li/frameworkers/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260330_112100_851887/artifacts/media/VideoAgent/video/clip_sh_005.mp4"
      },
      {
        "role": "clip_sh_006",
        "path": "/home/zhendong_li/frameworkers/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260330_112100_851887/artifacts/media/VideoAgent/video/clip_sh_006.mp4"
      },
      {
        "role": "clip_sc_002",
        "path": "/home/zhendong_li/frameworkers/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260330_112100_851887/artifacts/media/VideoAgent/video/clip_sc_002.mp4"
      },
      {
        "role": "clip_sh_007",
        "path": "/home/zhendong_li/frameworkers/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260330_112100_851887/artifacts/media/VideoAgent/video/clip_sh_007.mp4"
      },
      {
        "role": "clip_sh_008",
        "path": "/home/zhendong_li/frameworkers/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260330_112100_851887/artifacts/media/VideoAgent/video/clip_sh_008.mp4"
      },
      {
        "role": "clip_sh_009",
        "path": "/home/zhendong_li/frameworkers/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260330_112100_851887/artifacts/media/VideoAgent/video/clip_sh_009.mp4"
      },
      {
        "role": "clip_sc_003",
        "path": "/home/zhendong_li/frameworkers/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260330_112100_851887/artifacts/media/VideoAgent/video/clip_sc_003.mp4"
      },
      {
        "role": "clip_final",
        "path": "/home/zhendong_li/frameworkers/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260330_112100_851887/artifacts/media/VideoAgent/video/clip_final.mp4"
      }
    ]
  },
  {
    "content": "global_memory test summary",
    "agent_id": "AudioAgent",
    "task_id": "task_1_f46573a1",
    "created_at": "2026-03-30T11:45:06.911637+00:00",
    "execution_result": {
      "status": "FAILED",
      "execution_id": "exec_6_e738c4ed",
      "error": "chat_json: model output is not valid JSON: Expecting ',' delimiter: line 7 column 5 (char 244)"
    }
  }
]
```
