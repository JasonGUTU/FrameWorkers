# Global memory

Global memory for workspace `workspace_global_20260403_132858`. The **Entries** section is the canonical JSON array. The **File tree** below is a **human-readable snapshot** at write time (may be truncated); for **automation** (persist paths, input packaging, Director), use **live** workspace file-tree APIs and ``artifact_locations`` — the snapshot is not authoritative.

## File tree

<!-- FW_FILE_TREE_BEGIN -->
```
.file_metadata.json
    audio_exec_6.json
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
        clip_final.mp4
        clip_sc_001.mp4
        clip_sc_003.mp4
        clip_sh_003.mp4
        clip_sh_010.mp4
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
    "task_id": "task_1_d4822c2c",
    "created_at": "2026-04-03T13:29:15.509001+00:00",
    "execution_result": {
      "status": "COMPLETED",
      "execution_id": "exec_1_728601c7",
      "persist_plan_meta": {
        "naming_policy_version": "v2.0",
        "persist_plan_digest": "6c2d2fa50e274fab1be638135b232c545f1fd7af0c52e93419bb8ec0f7e16019"
      }
    },
    "artifact_locations": [
      {
        "role": "story_blueprint",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_132858/artifacts/story_blueprint/story_blueprint_exec_1.json"
      }
    ]
  },
  {
    "content": "global_memory test summary",
    "agent_id": "ScreenplayAgent",
    "task_id": "task_1_d4822c2c",
    "created_at": "2026-04-03T13:29:43.274779+00:00",
    "execution_result": {
      "status": "COMPLETED",
      "execution_id": "exec_2_8426b1c7",
      "persist_plan_meta": {
        "naming_policy_version": "v2.0",
        "persist_plan_digest": "a5d423292a40d92997772983c9c2b6dd4bc9a9c5f5a3a16c6f03045e50d7fe23"
      }
    },
    "artifact_locations": [
      {
        "role": "screenplay",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_132858/artifacts/screenplay/screenplay_exec_2.json"
      }
    ]
  },
  {
    "content": "global_memory test summary",
    "agent_id": "StoryboardAgent",
    "task_id": "task_1_d4822c2c",
    "created_at": "2026-04-03T13:30:41.332747+00:00",
    "execution_result": {
      "status": "COMPLETED",
      "execution_id": "exec_3_a36b054d",
      "persist_plan_meta": {
        "naming_policy_version": "v2.0",
        "persist_plan_digest": "b8496c8aa7ae60e89c51e35bcaa5dd6adde90635a7df6acd8d5179eaf49ba712"
      }
    },
    "artifact_locations": [
      {
        "role": "storyboard",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_132858/artifacts/storyboard/storyboard_exec_3.json"
      }
    ]
  },
  {
    "content": "global_memory test summary",
    "agent_id": "KeyFrameAgent",
    "task_id": "task_1_d4822c2c",
    "created_at": "2026-04-03T13:33:51.283882+00:00",
    "execution_result": {
      "status": "COMPLETED",
      "execution_id": "exec_4_254091cc",
      "persist_plan_meta": {
        "naming_policy_version": "v2.0",
        "persist_plan_digest": "4d96543c2e00da58b238878e9bb3ba18c6a546d9fa4143f2de8e0ca53bba594a"
      }
    },
    "artifact_locations": [
      {
        "role": "keyframes",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_132858/artifacts/keyframes/keyframes_exec_4.json"
      },
      {
        "role": "img_loc_001_global",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_132858/artifacts/media/KeyFrameAgent/image/img_loc_001_global.png"
      },
      {
        "role": "img_char_001_global",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_132858/artifacts/media/KeyFrameAgent/image/img_char_001_global.png"
      },
      {
        "role": "img_char_001_sc_001",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_132858/artifacts/media/KeyFrameAgent/image/img_char_001_sc_001.png"
      },
      {
        "role": "img_loc_001_sc_003",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_132858/artifacts/media/KeyFrameAgent/image/img_loc_001_sc_003.png"
      },
      {
        "role": "img_loc_001_sc_002",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_132858/artifacts/media/KeyFrameAgent/image/img_loc_001_sc_002.png"
      },
      {
        "role": "img_char_001_sc_003",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_132858/artifacts/media/KeyFrameAgent/image/img_char_001_sc_003.png"
      },
      {
        "role": "img_char_001_sc_002",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_132858/artifacts/media/KeyFrameAgent/image/img_char_001_sc_002.png"
      },
      {
        "role": "img_loc_001_sc_001",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_132858/artifacts/media/KeyFrameAgent/image/img_loc_001_sc_001.png"
      },
      {
        "role": "keyframes_manifest",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_132858/artifacts/keyframes/keyframes_manifest.json"
      }
    ]
  },
  {
    "content": "global_memory test summary",
    "agent_id": "VideoAgent",
    "task_id": "task_1_d4822c2c",
    "created_at": "2026-04-03T13:41:17.681824+00:00",
    "execution_result": {
      "status": "COMPLETED",
      "execution_id": "exec_5_4a096cab",
      "persist_plan_meta": {
        "naming_policy_version": "v2.0",
        "persist_plan_digest": "dd56f3e6fbea084504076eb02b2ae9d3cfee77284df3a9523e4879b60dbd3fb3"
      }
    },
    "artifact_locations": [
      {
        "role": "video",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_132858/artifacts/video/video_exec_5.json"
      },
      {
        "role": "clip_sh_003",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_132858/artifacts/media/VideoAgent/video/clip_sh_003.mp4"
      },
      {
        "role": "clip_sc_001",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_132858/artifacts/media/VideoAgent/video/clip_sc_001.mp4"
      },
      {
        "role": "clip_sh_010",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_132858/artifacts/media/VideoAgent/video/clip_sh_010.mp4"
      },
      {
        "role": "clip_sc_003",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_132858/artifacts/media/VideoAgent/video/clip_sc_003.mp4"
      },
      {
        "role": "clip_final",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_132858/artifacts/media/VideoAgent/video/clip_final.mp4"
      }
    ]
  },
  {
    "content": "global_memory test summary",
    "agent_id": "AudioAgent",
    "task_id": "task_1_d4822c2c",
    "created_at": "2026-04-03T13:41:51.282323+00:00",
    "execution_result": {
      "status": "COMPLETED",
      "execution_id": "exec_6_f40009df",
      "persist_plan_meta": {
        "naming_policy_version": "v2.0",
        "persist_plan_digest": "79b88a340511e8d157219786eb83372aed26dea5fb88eeff5c5513c679d3c8c3"
      }
    },
    "artifact_locations": [
      {
        "role": "audio",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_132858/artifacts/audio/audio_exec_6.json"
      }
    ]
  }
]
```
