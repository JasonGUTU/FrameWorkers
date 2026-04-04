# Global memory

Global memory for workspace `workspace_global_20260403_130818`. The **Entries** section is the canonical JSON array. The **File tree** below is a **human-readable snapshot** at write time (may be truncated); for **automation** (persist paths, input packaging, Director), use **live** workspace file-tree APIs and ``artifact_locations`` — the snapshot is not authoritative.

## File tree

<!-- FW_FILE_TREE_BEGIN -->
```
.file_metadata.json
    audio_exec_6.json
    keyframes_exec_4.json
    keyframes_manifest.json
        aud_amb_sc_001.wav
        aud_final.wav
        aud_mix_sc_001.wav
        aud_music_sc_001.wav
        img_char_001_global.png
        img_char_001_sc_001.png
        img_loc_001_global.png
        img_loc_001_sc_001.png
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
    "task_id": "task_1_b6955cf7",
    "created_at": "2026-04-03T13:08:37.129901+00:00",
    "execution_result": {
      "status": "COMPLETED",
      "execution_id": "exec_1_b31191dd",
      "persist_plan_meta": {
        "naming_policy_version": "v2.0",
        "persist_plan_digest": "6c2d2fa50e274fab1be638135b232c545f1fd7af0c52e93419bb8ec0f7e16019"
      }
    },
    "artifact_locations": [
      {
        "role": "story_blueprint",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_130818/artifacts/story_blueprint/story_blueprint_exec_1.json"
      }
    ]
  },
  {
    "content": "global_memory test summary",
    "agent_id": "ScreenplayAgent",
    "task_id": "task_1_b6955cf7",
    "created_at": "2026-04-03T13:09:03.006153+00:00",
    "execution_result": {
      "status": "COMPLETED",
      "execution_id": "exec_2_66dd1874",
      "persist_plan_meta": {
        "naming_policy_version": "v2.0",
        "persist_plan_digest": "a5d423292a40d92997772983c9c2b6dd4bc9a9c5f5a3a16c6f03045e50d7fe23"
      }
    },
    "artifact_locations": [
      {
        "role": "screenplay",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_130818/artifacts/screenplay/screenplay_exec_2.json"
      }
    ]
  },
  {
    "content": "global_memory test summary",
    "agent_id": "StoryboardAgent",
    "task_id": "task_1_b6955cf7",
    "created_at": "2026-04-03T13:09:41.538498+00:00",
    "execution_result": {
      "status": "COMPLETED",
      "execution_id": "exec_3_34f16233",
      "persist_plan_meta": {
        "naming_policy_version": "v2.0",
        "persist_plan_digest": "b8496c8aa7ae60e89c51e35bcaa5dd6adde90635a7df6acd8d5179eaf49ba712"
      }
    },
    "artifact_locations": [
      {
        "role": "storyboard",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_130818/artifacts/storyboard/storyboard_exec_3.json"
      }
    ]
  },
  {
    "content": "global_memory test summary",
    "agent_id": "KeyFrameAgent",
    "task_id": "task_1_b6955cf7",
    "created_at": "2026-04-03T13:12:10.279501+00:00",
    "execution_result": {
      "status": "COMPLETED",
      "execution_id": "exec_4_c652801f",
      "persist_plan_meta": {
        "naming_policy_version": "v2.0",
        "persist_plan_digest": "9a77710bbb36a17bdba6b40d16cc4889168c23b62e8641627ae7693e49d1c11b"
      }
    },
    "artifact_locations": [
      {
        "role": "keyframes",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_130818/artifacts/keyframes/keyframes_exec_4.json"
      },
      {
        "role": "img_char_001_global",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_130818/artifacts/media/KeyFrameAgent/image/img_char_001_global.png"
      },
      {
        "role": "img_loc_001_global",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_130818/artifacts/media/KeyFrameAgent/image/img_loc_001_global.png"
      },
      {
        "role": "img_char_001_sc_001",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_130818/artifacts/media/KeyFrameAgent/image/img_char_001_sc_001.png"
      },
      {
        "role": "img_loc_001_sc_001",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_130818/artifacts/media/KeyFrameAgent/image/img_loc_001_sc_001.png"
      },
      {
        "role": "keyframes_manifest",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_130818/artifacts/keyframes/keyframes_manifest.json"
      }
    ]
  },
  {
    "content": "global_memory test summary",
    "agent_id": "VideoAgent",
    "task_id": "task_1_b6955cf7",
    "created_at": "2026-04-03T13:12:19.541070+00:00",
    "execution_result": {
      "status": "COMPLETED",
      "execution_id": "exec_5_46d901b5",
      "persist_plan_meta": {
        "naming_policy_version": "v2.0",
        "persist_plan_digest": "5065bf7e02b1efb4447e79abdfa00a431f1ff4793a2c7a9f83303e02d13110d1"
      }
    },
    "artifact_locations": [
      {
        "role": "video",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_130818/artifacts/video/video_exec_5.json"
      }
    ]
  },
  {
    "content": "global_memory test summary",
    "agent_id": "AudioAgent",
    "task_id": "task_1_b6955cf7",
    "created_at": "2026-04-03T13:12:46.925654+00:00",
    "execution_result": {
      "status": "COMPLETED",
      "execution_id": "exec_6_7d996a59",
      "persist_plan_meta": {
        "naming_policy_version": "v2.0",
        "persist_plan_digest": "bf9b8f8a59e33eb3bef31d42a44b9a4c33d4c70275f3e68650e8953037a9788c"
      }
    },
    "artifact_locations": [
      {
        "role": "audio",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_130818/artifacts/audio/audio_exec_6.json"
      },
      {
        "role": "aud_music_sc_001",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_130818/artifacts/media/AudioAgent/audio/aud_music_sc_001.wav"
      },
      {
        "role": "aud_amb_sc_001",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_130818/artifacts/media/AudioAgent/audio/aud_amb_sc_001.wav"
      },
      {
        "role": "aud_mix_sc_001",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_130818/artifacts/media/AudioAgent/audio/aud_mix_sc_001.wav"
      },
      {
        "role": "aud_final",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_130818/artifacts/media/AudioAgent/audio/aud_final.wav"
      }
    ]
  }
]
```
