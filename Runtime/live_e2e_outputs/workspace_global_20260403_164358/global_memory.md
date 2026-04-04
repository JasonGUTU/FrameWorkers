# Global memory

Global memory for workspace `workspace_global_20260403_164358`. The **Entries** section is the canonical JSON array. The **File tree** below is a **human-readable snapshot** at write time (may be truncated); for **automation** (persist paths, input packaging, Director), use **live** workspace file-tree APIs and ``artifact_locations`` — the snapshot is not authoritative.

## File tree

<!-- FW_FILE_TREE_BEGIN -->
```
.file_metadata.json
    audio_exec_6.json
    keyframes_exec_4.json
    keyframes_manifest.json
        aud_amb_sc_001.wav
        aud_amb_sc_002.wav
        aud_amb_sc_003.wav
        aud_final.wav
        aud_mix_sc_001.wav
        aud_mix_sc_002.wav
        aud_mix_sc_003.wav
        aud_music_sc_001.wav
        aud_music_sc_002.wav
        aud_music_sc_003.wav
        delivery_final.mp4
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
        clip_sc_002.mp4
        clip_sc_003.mp4
        clip_sh_001.mp4
        clip_sh_003.mp4
        clip_sh_007.mp4
        clip_sh_011.mp4
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
    "task_id": "task_1_ab353b24",
    "created_at": "2026-04-03T16:44:18.918133+00:00",
    "execution_result": {
      "status": "COMPLETED",
      "execution_id": "exec_1_25f6d0bf",
      "persist_plan_meta": {
        "naming_policy_version": "v2.0",
        "persist_plan_digest": "6c2d2fa50e274fab1be638135b232c545f1fd7af0c52e93419bb8ec0f7e16019"
      }
    },
    "artifact_locations": [
      {
        "role": "story_blueprint",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_164358/artifacts/story_blueprint/story_blueprint_exec_1.json"
      }
    ]
  },
  {
    "content": "global_memory test summary",
    "agent_id": "ScreenplayAgent",
    "task_id": "task_1_ab353b24",
    "created_at": "2026-04-03T16:44:52.414832+00:00",
    "execution_result": {
      "status": "COMPLETED",
      "execution_id": "exec_2_5ef07cef",
      "persist_plan_meta": {
        "naming_policy_version": "v2.0",
        "persist_plan_digest": "a5d423292a40d92997772983c9c2b6dd4bc9a9c5f5a3a16c6f03045e50d7fe23"
      }
    },
    "artifact_locations": [
      {
        "role": "screenplay",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_164358/artifacts/screenplay/screenplay_exec_2.json"
      }
    ]
  },
  {
    "content": "global_memory test summary",
    "agent_id": "StoryboardAgent",
    "task_id": "task_1_ab353b24",
    "created_at": "2026-04-03T16:46:46.933022+00:00",
    "execution_result": {
      "status": "COMPLETED",
      "execution_id": "exec_3_f0888c87",
      "persist_plan_meta": {
        "naming_policy_version": "v2.0",
        "persist_plan_digest": "b8496c8aa7ae60e89c51e35bcaa5dd6adde90635a7df6acd8d5179eaf49ba712"
      }
    },
    "artifact_locations": [
      {
        "role": "storyboard",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_164358/artifacts/storyboard/storyboard_exec_3.json"
      }
    ]
  },
  {
    "content": "global_memory test summary",
    "agent_id": "KeyFrameAgent",
    "task_id": "task_1_ab353b24",
    "created_at": "2026-04-03T16:50:41.547537+00:00",
    "execution_result": {
      "status": "COMPLETED",
      "execution_id": "exec_4_a006b719",
      "persist_plan_meta": {
        "naming_policy_version": "v2.0",
        "persist_plan_digest": "49069c856f8defc08e85e0899817584a244017abd4f65cad7445745a5bdd790f"
      }
    },
    "artifact_locations": [
      {
        "role": "keyframes",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_164358/artifacts/keyframes/keyframes_exec_4.json"
      },
      {
        "role": "img_char_001_global",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_164358/artifacts/media/KeyFrameAgent/image/img_char_001_global.png"
      },
      {
        "role": "img_loc_001_global",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_164358/artifacts/media/KeyFrameAgent/image/img_loc_001_global.png"
      },
      {
        "role": "img_char_001_sc_001",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_164358/artifacts/media/KeyFrameAgent/image/img_char_001_sc_001.png"
      },
      {
        "role": "img_loc_001_sc_002",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_164358/artifacts/media/KeyFrameAgent/image/img_loc_001_sc_002.png"
      },
      {
        "role": "img_char_001_sc_003",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_164358/artifacts/media/KeyFrameAgent/image/img_char_001_sc_003.png"
      },
      {
        "role": "img_loc_001_sc_003",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_164358/artifacts/media/KeyFrameAgent/image/img_loc_001_sc_003.png"
      },
      {
        "role": "img_char_001_sc_002",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_164358/artifacts/media/KeyFrameAgent/image/img_char_001_sc_002.png"
      },
      {
        "role": "img_loc_001_sc_001",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_164358/artifacts/media/KeyFrameAgent/image/img_loc_001_sc_001.png"
      },
      {
        "role": "keyframes_manifest",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_164358/artifacts/keyframes/keyframes_manifest.json"
      }
    ]
  },
  {
    "content": "global_memory test summary",
    "agent_id": "VideoAgent",
    "task_id": "task_1_ab353b24",
    "created_at": "2026-04-03T17:05:38.057087+00:00",
    "execution_result": {
      "status": "COMPLETED",
      "execution_id": "exec_5_2b2628c1",
      "persist_plan_meta": {
        "naming_policy_version": "v2.0",
        "persist_plan_digest": "ab4a65a3b8fea76005e0e0e000503007e406a9a9e835a87de345985f2ed15b37"
      }
    },
    "artifact_locations": [
      {
        "role": "video",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_164358/artifacts/video/video_exec_5.json"
      },
      {
        "role": "clip_sh_001",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_164358/artifacts/media/VideoAgent/video/clip_sh_001.mp4"
      },
      {
        "role": "clip_sh_003",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_164358/artifacts/media/VideoAgent/video/clip_sh_003.mp4"
      },
      {
        "role": "clip_sc_001",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_164358/artifacts/media/VideoAgent/video/clip_sc_001.mp4"
      },
      {
        "role": "clip_sh_007",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_164358/artifacts/media/VideoAgent/video/clip_sh_007.mp4"
      },
      {
        "role": "clip_sc_002",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_164358/artifacts/media/VideoAgent/video/clip_sc_002.mp4"
      },
      {
        "role": "clip_sh_011",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_164358/artifacts/media/VideoAgent/video/clip_sh_011.mp4"
      },
      {
        "role": "clip_sc_003",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_164358/artifacts/media/VideoAgent/video/clip_sc_003.mp4"
      },
      {
        "role": "clip_final",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_164358/artifacts/media/VideoAgent/video/clip_final.mp4"
      }
    ]
  },
  {
    "content": "global_memory test summary",
    "agent_id": "AudioAgent",
    "task_id": "task_1_ab353b24",
    "created_at": "2026-04-03T17:06:20.038428+00:00",
    "execution_result": {
      "status": "COMPLETED",
      "execution_id": "exec_6_f6263756",
      "persist_plan_meta": {
        "naming_policy_version": "v2.0",
        "persist_plan_digest": "eadc7e9b2a600b588e856529c563b67347c118b78ed8533ac1dc88bc1479439a"
      }
    },
    "artifact_locations": [
      {
        "role": "audio",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_164358/artifacts/audio/audio_exec_6.json"
      },
      {
        "role": "aud_music_sc_001",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_164358/artifacts/media/AudioAgent/audio/aud_music_sc_001.wav"
      },
      {
        "role": "aud_amb_sc_001",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_164358/artifacts/media/AudioAgent/audio/aud_amb_sc_001.wav"
      },
      {
        "role": "aud_mix_sc_001",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_164358/artifacts/media/AudioAgent/audio/aud_mix_sc_001.wav"
      },
      {
        "role": "aud_music_sc_002",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_164358/artifacts/media/AudioAgent/audio/aud_music_sc_002.wav"
      },
      {
        "role": "aud_amb_sc_002",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_164358/artifacts/media/AudioAgent/audio/aud_amb_sc_002.wav"
      },
      {
        "role": "aud_mix_sc_002",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_164358/artifacts/media/AudioAgent/audio/aud_mix_sc_002.wav"
      },
      {
        "role": "aud_music_sc_003",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_164358/artifacts/media/AudioAgent/audio/aud_music_sc_003.wav"
      },
      {
        "role": "aud_amb_sc_003",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_164358/artifacts/media/AudioAgent/audio/aud_amb_sc_003.wav"
      },
      {
        "role": "aud_mix_sc_003",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_164358/artifacts/media/AudioAgent/audio/aud_mix_sc_003.wav"
      },
      {
        "role": "aud_final",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_164358/artifacts/media/AudioAgent/audio/aud_final.wav"
      },
      {
        "role": "delivery_final",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_164358/artifacts/media/AudioAgent/video/delivery_final.mp4"
      }
    ]
  }
]
```
