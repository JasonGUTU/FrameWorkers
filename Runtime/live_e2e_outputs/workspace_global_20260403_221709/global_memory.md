# Global memory

Global memory for workspace `workspace_global_20260403_221709`. The **Entries** section is the canonical JSON array. The **File tree** below is a **human-readable snapshot** at write time (may be truncated); for **automation** (persist paths, input packaging, Director), use **live** workspace file-tree APIs and ``artifact_locations`` — the snapshot is not authoritative.

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
        img_char_001_global.png
        img_char_001_sc_001.png
        img_char_001_sc_002.png
        img_char_001_sc_003.png
        img_loc_001_global.png
        img_loc_001_sc_001.png
        img_loc_001_sc_002.png
        img_loc_001_sc_003.png
        img_sh_001_kf_001.png
        img_sh_002_kf_002.png
        img_sh_003_kf_003.png
        img_sh_004_kf_004.png
        img_sh_005_kf_005.png
        img_sh_006_kf_006.png
        img_sh_007_kf_007.png
        img_sh_008_kf_008.png
        img_sh_009_kf_009.png
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
    "task_id": "task_1_921a02d6",
    "created_at": "2026-04-03T22:17:23.727144+00:00",
    "execution_result": {
      "status": "COMPLETED",
      "execution_id": "exec_1_98c1b7b4",
      "persist_plan_meta": {
        "naming_policy_version": "v2.0",
        "persist_plan_digest": "6c2d2fa50e274fab1be638135b232c545f1fd7af0c52e93419bb8ec0f7e16019"
      }
    },
    "artifact_locations": [
      {
        "role": "story_blueprint",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_221709/artifacts/story_blueprint/story_blueprint_exec_1.json"
      }
    ]
  },
  {
    "content": "global_memory test summary",
    "agent_id": "ScreenplayAgent",
    "task_id": "task_1_921a02d6",
    "created_at": "2026-04-03T22:18:09.010048+00:00",
    "execution_result": {
      "status": "COMPLETED",
      "execution_id": "exec_2_dfe38969",
      "persist_plan_meta": {
        "naming_policy_version": "v2.0",
        "persist_plan_digest": "a5d423292a40d92997772983c9c2b6dd4bc9a9c5f5a3a16c6f03045e50d7fe23"
      }
    },
    "artifact_locations": [
      {
        "role": "screenplay",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_221709/artifacts/screenplay/screenplay_exec_2.json"
      }
    ]
  },
  {
    "content": "global_memory test summary",
    "agent_id": "KeyFrameAgent",
    "task_id": "task_1_921a02d6",
    "created_at": "2026-04-03T22:20:52.949359+00:00",
    "execution_result": {
      "status": "COMPLETED",
      "execution_id": "exec_3_0ab39c52",
      "persist_plan_meta": {
        "naming_policy_version": "v2.0",
        "persist_plan_digest": "f67056e8d83b3a54322c4e1bc33913fbbc73149a28b12cae2b03d3cd1f3cb88f"
      }
    },
    "artifact_locations": [
      {
        "role": "keyframes",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_221709/artifacts/keyframes/keyframes_exec_3.json"
      },
      {
        "role": "img_char_001_global",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_221709/artifacts/media/KeyFrameAgent/image/img_char_001_global.png"
      },
      {
        "role": "img_loc_001_global",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_221709/artifacts/media/KeyFrameAgent/image/img_loc_001_global.png"
      },
      {
        "role": "img_loc_001_sc_003",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_221709/artifacts/media/KeyFrameAgent/image/img_loc_001_sc_003.png"
      },
      {
        "role": "img_char_001_sc_003",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_221709/artifacts/media/KeyFrameAgent/image/img_char_001_sc_003.png"
      },
      {
        "role": "img_char_001_sc_001",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_221709/artifacts/media/KeyFrameAgent/image/img_char_001_sc_001.png"
      },
      {
        "role": "img_char_001_sc_002",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_221709/artifacts/media/KeyFrameAgent/image/img_char_001_sc_002.png"
      },
      {
        "role": "img_loc_001_sc_001",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_221709/artifacts/media/KeyFrameAgent/image/img_loc_001_sc_001.png"
      },
      {
        "role": "img_loc_001_sc_002",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_221709/artifacts/media/KeyFrameAgent/image/img_loc_001_sc_002.png"
      },
      {
        "role": "img_sh_006_kf_006",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_221709/artifacts/media/KeyFrameAgent/image/img_sh_006_kf_006.png"
      },
      {
        "role": "img_sh_009_kf_009",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_221709/artifacts/media/KeyFrameAgent/image/img_sh_009_kf_009.png"
      },
      {
        "role": "img_sh_008_kf_008",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_221709/artifacts/media/KeyFrameAgent/image/img_sh_008_kf_008.png"
      },
      {
        "role": "img_sh_003_kf_003",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_221709/artifacts/media/KeyFrameAgent/image/img_sh_003_kf_003.png"
      },
      {
        "role": "img_sh_007_kf_007",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_221709/artifacts/media/KeyFrameAgent/image/img_sh_007_kf_007.png"
      },
      {
        "role": "img_sh_004_kf_004",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_221709/artifacts/media/KeyFrameAgent/image/img_sh_004_kf_004.png"
      },
      {
        "role": "img_sh_002_kf_002",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_221709/artifacts/media/KeyFrameAgent/image/img_sh_002_kf_002.png"
      },
      {
        "role": "img_sh_005_kf_005",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_221709/artifacts/media/KeyFrameAgent/image/img_sh_005_kf_005.png"
      },
      {
        "role": "img_sh_001_kf_001",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_221709/artifacts/media/KeyFrameAgent/image/img_sh_001_kf_001.png"
      },
      {
        "role": "keyframes_manifest",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_221709/artifacts/keyframes/keyframes_manifest.json"
      }
    ]
  },
  {
    "content": "global_memory test summary",
    "agent_id": "VideoAgent",
    "task_id": "task_1_921a02d6",
    "created_at": "2026-04-03T22:22:13.255102+00:00",
    "execution_result": {
      "status": "COMPLETED",
      "execution_id": "exec_4_3485a32e",
      "persist_plan_meta": {
        "naming_policy_version": "v2.0",
        "persist_plan_digest": "698d8246ccd46deb555033f127ac6b38044ea7bdf935b36042077c242906ea5f"
      }
    },
    "artifact_locations": [
      {
        "role": "video",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_221709/artifacts/video/video_exec_4.json"
      }
    ]
  },
  {
    "content": "global_memory test summary",
    "agent_id": "AudioAgent",
    "task_id": "task_1_921a02d6",
    "created_at": "2026-04-03T22:22:45.099487+00:00",
    "execution_result": {
      "status": "COMPLETED",
      "execution_id": "exec_5_34c31ca2",
      "persist_plan_meta": {
        "naming_policy_version": "v2.0",
        "persist_plan_digest": "a05747e2198d98993afb2d3459d2f62c7df9f4369aa00cf386accfdedcc9f298"
      }
    },
    "artifact_locations": [
      {
        "role": "audio",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_221709/artifacts/audio/audio_exec_5.json"
      },
      {
        "role": "aud_music_sc_001",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_221709/artifacts/media/AudioAgent/audio/aud_music_sc_001.wav"
      },
      {
        "role": "aud_amb_sc_001",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_221709/artifacts/media/AudioAgent/audio/aud_amb_sc_001.wav"
      },
      {
        "role": "aud_mix_sc_001",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_221709/artifacts/media/AudioAgent/audio/aud_mix_sc_001.wav"
      },
      {
        "role": "aud_music_sc_002",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_221709/artifacts/media/AudioAgent/audio/aud_music_sc_002.wav"
      },
      {
        "role": "aud_amb_sc_002",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_221709/artifacts/media/AudioAgent/audio/aud_amb_sc_002.wav"
      },
      {
        "role": "aud_mix_sc_002",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_221709/artifacts/media/AudioAgent/audio/aud_mix_sc_002.wav"
      },
      {
        "role": "aud_music_sc_003",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_221709/artifacts/media/AudioAgent/audio/aud_music_sc_003.wav"
      },
      {
        "role": "aud_amb_sc_003",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_221709/artifacts/media/AudioAgent/audio/aud_amb_sc_003.wav"
      },
      {
        "role": "aud_mix_sc_003",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_221709/artifacts/media/AudioAgent/audio/aud_mix_sc_003.wav"
      },
      {
        "role": "aud_final",
        "path": "/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260403_221709/artifacts/media/AudioAgent/audio/aud_final.wav"
      }
    ]
  }
]
```
