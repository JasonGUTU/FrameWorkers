# Global memory

Global memory for workspace `workspace_global_20260404_190954`. The **Entries** section is the canonical JSON array. The **File tree** below is a **human-readable snapshot** at write time (may be truncated); for **automation** (persist paths, input packaging, Director), use **live** workspace file-tree APIs and ``artifact_locations`` — the snapshot is not authoritative.

## File tree

<!-- FW_FILE_TREE_BEGIN -->
```
.file_metadata.json
    audio_exec_5.json
    keyframes_exec_3.json
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
        img_prop_001_global.png
        img_prop_001_sc_001.png
        img_prop_001_sc_002.png
        img_prop_001_sc_003.png
        img_sh_001_kf_001.png
        img_sh_002_kf_002.png
        img_sh_003_kf_003.png
        img_sh_004_kf_004.png
        img_sh_005_kf_005.png
        img_sh_006_kf_006.png
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
    screenplay_exec_2.json
    story_blueprint_exec_1.json
    video_exec_4.json
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
    "task_id": "task_1_0f696dda",
    "created_at": "2026-04-04T19:10:12.843195+00:00",
    "execution_result": {
      "status": "COMPLETED",
      "execution_id": "exec_1_3acf0ffa",
      "persist_plan_meta": {
        "naming_policy_version": "v2.0",
        "persist_plan_digest": "6c2d2fa50e274fab1be638135b232c545f1fd7af0c52e93419bb8ec0f7e16019"
      }
    },
    "artifact_locations": [
      {
        "role": "story_blueprint",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260404_190954/artifacts/story_blueprint/story_blueprint_exec_1.json"
      }
    ]
  },
  {
    "content": "global_memory test summary",
    "agent_id": "ScreenplayAgent",
    "task_id": "task_1_0f696dda",
    "created_at": "2026-04-04T19:10:55.185592+00:00",
    "execution_result": {
      "status": "COMPLETED",
      "execution_id": "exec_2_7b00aeee",
      "persist_plan_meta": {
        "naming_policy_version": "v2.0",
        "persist_plan_digest": "a5d423292a40d92997772983c9c2b6dd4bc9a9c5f5a3a16c6f03045e50d7fe23"
      }
    },
    "artifact_locations": [
      {
        "role": "screenplay",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260404_190954/artifacts/screenplay/screenplay_exec_2.json"
      }
    ]
  },
  {
    "content": "global_memory test summary",
    "agent_id": "KeyFrameAgent",
    "task_id": "task_1_0f696dda",
    "created_at": "2026-04-04T19:13:48.475390+00:00",
    "execution_result": {
      "status": "COMPLETED",
      "execution_id": "exec_3_073e6575",
      "persist_plan_meta": {
        "naming_policy_version": "v2.0",
        "persist_plan_digest": "b296c67faed4f845a0ca443d38f971dffb4cf9552899618718dd2461338505fa"
      }
    },
    "artifact_locations": [
      {
        "role": "keyframes",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260404_190954/artifacts/keyframes/keyframes_exec_3.json"
      },
      {
        "role": "img_loc_001_global",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260404_190954/artifacts/media/KeyFrameAgent/image/img_loc_001_global.png"
      },
      {
        "role": "img_prop_001_global",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260404_190954/artifacts/media/KeyFrameAgent/image/img_prop_001_global.png"
      },
      {
        "role": "img_char_001_global",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260404_190954/artifacts/media/KeyFrameAgent/image/img_char_001_global.png"
      },
      {
        "role": "img_char_001_sc_002",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260404_190954/artifacts/media/KeyFrameAgent/image/img_char_001_sc_002.png"
      },
      {
        "role": "img_prop_001_sc_001",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260404_190954/artifacts/media/KeyFrameAgent/image/img_prop_001_sc_001.png"
      },
      {
        "role": "img_char_001_sc_001",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260404_190954/artifacts/media/KeyFrameAgent/image/img_char_001_sc_001.png"
      },
      {
        "role": "img_loc_001_sc_002",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260404_190954/artifacts/media/KeyFrameAgent/image/img_loc_001_sc_002.png"
      },
      {
        "role": "img_loc_001_sc_003",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260404_190954/artifacts/media/KeyFrameAgent/image/img_loc_001_sc_003.png"
      },
      {
        "role": "img_prop_001_sc_002",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260404_190954/artifacts/media/KeyFrameAgent/image/img_prop_001_sc_002.png"
      },
      {
        "role": "img_char_001_sc_003",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260404_190954/artifacts/media/KeyFrameAgent/image/img_char_001_sc_003.png"
      },
      {
        "role": "img_prop_001_sc_003",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260404_190954/artifacts/media/KeyFrameAgent/image/img_prop_001_sc_003.png"
      },
      {
        "role": "img_loc_001_sc_001",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260404_190954/artifacts/media/KeyFrameAgent/image/img_loc_001_sc_001.png"
      },
      {
        "role": "img_sh_003_kf_003",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260404_190954/artifacts/media/KeyFrameAgent/image/img_sh_003_kf_003.png"
      },
      {
        "role": "img_sh_001_kf_001",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260404_190954/artifacts/media/KeyFrameAgent/image/img_sh_001_kf_001.png"
      },
      {
        "role": "img_sh_005_kf_005",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260404_190954/artifacts/media/KeyFrameAgent/image/img_sh_005_kf_005.png"
      },
      {
        "role": "img_sh_006_kf_006",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260404_190954/artifacts/media/KeyFrameAgent/image/img_sh_006_kf_006.png"
      },
      {
        "role": "img_sh_004_kf_004",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260404_190954/artifacts/media/KeyFrameAgent/image/img_sh_004_kf_004.png"
      },
      {
        "role": "img_sh_002_kf_002",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260404_190954/artifacts/media/KeyFrameAgent/image/img_sh_002_kf_002.png"
      },
      {
        "role": "keyframes_manifest",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260404_190954/artifacts/keyframes/keyframes_manifest.json"
      }
    ]
  },
  {
    "content": "global_memory test summary",
    "agent_id": "VideoAgent",
    "task_id": "task_1_0f696dda",
    "created_at": "2026-04-04T19:21:48.527064+00:00",
    "execution_result": {
      "status": "COMPLETED",
      "execution_id": "exec_4_9a7bcb69",
      "persist_plan_meta": {
        "naming_policy_version": "v2.0",
        "persist_plan_digest": "3ce5d37442009cf2c72d20d4242925d438bf769ea3ab710e9b9861372f689626"
      }
    },
    "artifact_locations": [
      {
        "role": "video",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260404_190954/artifacts/video/video_exec_4.json"
      },
      {
        "role": "clip_sh_001",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260404_190954/artifacts/media/VideoAgent/video/clip_sh_001.mp4"
      },
      {
        "role": "clip_sh_002",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260404_190954/artifacts/media/VideoAgent/video/clip_sh_002.mp4"
      },
      {
        "role": "clip_sc_001",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260404_190954/artifacts/media/VideoAgent/video/clip_sc_001.mp4"
      },
      {
        "role": "clip_sh_003",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260404_190954/artifacts/media/VideoAgent/video/clip_sh_003.mp4"
      },
      {
        "role": "clip_sh_004",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260404_190954/artifacts/media/VideoAgent/video/clip_sh_004.mp4"
      },
      {
        "role": "clip_sc_002",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260404_190954/artifacts/media/VideoAgent/video/clip_sc_002.mp4"
      },
      {
        "role": "clip_sh_005",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260404_190954/artifacts/media/VideoAgent/video/clip_sh_005.mp4"
      },
      {
        "role": "clip_sh_006",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260404_190954/artifacts/media/VideoAgent/video/clip_sh_006.mp4"
      },
      {
        "role": "clip_sc_003",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260404_190954/artifacts/media/VideoAgent/video/clip_sc_003.mp4"
      },
      {
        "role": "clip_final",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260404_190954/artifacts/media/VideoAgent/video/clip_final.mp4"
      }
    ]
  },
  {
    "content": "global_memory test summary",
    "agent_id": "AudioAgent",
    "task_id": "task_1_0f696dda",
    "created_at": "2026-04-04T19:22:26.906782+00:00",
    "execution_result": {
      "status": "COMPLETED",
      "execution_id": "exec_5_a7cebb7b",
      "persist_plan_meta": {
        "naming_policy_version": "v2.0",
        "persist_plan_digest": "463170730d94d5b326bb7e62ba20d18aa63a2861d2ce218010e657f655b1024a"
      }
    },
    "artifact_locations": [
      {
        "role": "audio",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260404_190954/artifacts/audio/audio_exec_5.json"
      },
      {
        "role": "aud_music_sc_001",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260404_190954/artifacts/media/AudioAgent/audio/aud_music_sc_001.wav"
      },
      {
        "role": "aud_amb_sc_001",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260404_190954/artifacts/media/AudioAgent/audio/aud_amb_sc_001.wav"
      },
      {
        "role": "aud_mix_sc_001",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260404_190954/artifacts/media/AudioAgent/audio/aud_mix_sc_001.wav"
      },
      {
        "role": "aud_music_sc_002",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260404_190954/artifacts/media/AudioAgent/audio/aud_music_sc_002.wav"
      },
      {
        "role": "aud_amb_sc_002",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260404_190954/artifacts/media/AudioAgent/audio/aud_amb_sc_002.wav"
      },
      {
        "role": "aud_mix_sc_002",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260404_190954/artifacts/media/AudioAgent/audio/aud_mix_sc_002.wav"
      },
      {
        "role": "aud_music_sc_003",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260404_190954/artifacts/media/AudioAgent/audio/aud_music_sc_003.wav"
      },
      {
        "role": "aud_amb_sc_003",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260404_190954/artifacts/media/AudioAgent/audio/aud_amb_sc_003.wav"
      },
      {
        "role": "aud_mix_sc_003",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260404_190954/artifacts/media/AudioAgent/audio/aud_mix_sc_003.wav"
      },
      {
        "role": "aud_final",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260404_190954/artifacts/media/AudioAgent/audio/aud_final.wav"
      },
      {
        "role": "delivery_final",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260404_190954/artifacts/media/AudioAgent/video/delivery_final.mp4"
      }
    ]
  }
]
```
