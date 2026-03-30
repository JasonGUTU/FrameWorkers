# Global memory

Global memory for workspace `workspace_global_20260330_121001_808449`. The **Entries** section is the canonical JSON array. The **File tree** below is a **human-readable snapshot** at write time (may be truncated); for **automation** (persist paths, input packaging, Director), use **live** workspace file-tree APIs and ``artifact_locations`` — the snapshot is not authoritative.

## File tree

<!-- FW_FILE_TREE_BEGIN -->
```
.file_metadata.json
      nostack_live_e2e_tid_screenplay_exec_2.json
    nostack_live_e2e_tid_keyframes_exec_4.json
    nostack_live_e2e_tid_keyframes_manifest.json
        nostack_live_e2e_tid_img_char_001_global.png
        nostack_live_e2e_tid_img_char_001_sc_001.png
        nostack_live_e2e_tid_img_loc_001_global.png
        nostack_live_e2e_tid_img_loc_001_sc_001.png
        nostack_live_e2e_tid_img_sh_001_kf_01.png
        nostack_live_e2e_tid_img_sh_002_kf_01.png
        nostack_live_e2e_tid_img_sh_003_kf_01.png
        nostack_live_e2e_tid_img_sh_003_kf_02.png
        nostack_live_e2e_tid_img_sh_004_kf_01.png
        nostack_live_e2e_tid_img_sh_005_kf_01.png
        nostack_live_e2e_tid_img_sh_006_kf_01.png
        nostack_live_e2e_tid_img_sh_006_kf_02.png
        nostack_live_e2e_tid_clip_final.mp4
        nostack_live_e2e_tid_clip_sc_001.mp4
        nostack_live_e2e_tid_clip_sh_001.mp4
        nostack_live_e2e_tid_clip_sh_002.mp4
        nostack_live_e2e_tid_clip_sh_003.mp4
        nostack_live_e2e_tid_clip_sh_004.mp4
        nostack_live_e2e_tid_clip_sh_005.mp4
        nostack_live_e2e_tid_clip_sh_006.mp4
        story_blueprint_exec_1.json
  nostack_live_e2e_tid_video_exec_5.json
    nostack_live_e2e_tid_storyboard_exec_3.json
global_memory.md
logs.jsonl
```
<!-- FW_FILE_TREE_END -->

## Entries

```json
[
  {
    "content": "A story blueprint detailing the poignant discovery of a cryptic bookmark by an elderly librarian, outlining the logline, cast, locations, and a single-scene story arc with internal conflict.",
    "agent_id": "StoryAgent",
    "task_id": "nostack_live_e2e_tid",
    "created_at": "2026-03-30T12:10:32.987979+00:00",
    "execution_result": {
      "status": "COMPLETED",
      "execution_id": "exec_1_f2ca4a04",
      "persist_plan_meta": {
        "naming_policy_version": "v2.0",
        "persist_plan_digest": "f64101fe1d42c6b1e5761f24b83b1a8147cbeab041e81d4d5d6a6e42d0cc04a6"
      },
      "artifact_briefs": [
        {
          "path": "story_blueprint_exec_1.json",
          "brief": "Story blueprint outlining the narrative, characters, and scene structure."
        }
      ]
    },
    "artifact_locations": [
      {
        "role": "story_blueprint",
        "path": "/home/zhendong_li/frameworkers/FrameWorkers/Runtime/nostack_live_e2e_outputs/workspace_global_20260330_121001_808449/artifacts/nostack_live_e2e_tid/StoryAgent/story_blueprint/story_blueprint_exec_1.json"
      }
    ]
  },
  {
    "content": "A screenplay detailing Elara's discovery of a personal bookmark with a cryptic message, aligning with the story blueprint and capturing her emotional shift.",
    "agent_id": "ScreenplayAgent",
    "task_id": "nostack_live_e2e_tid",
    "created_at": "2026-03-30T12:11:12.639397+00:00",
    "execution_result": {
      "status": "COMPLETED",
      "execution_id": "exec_2_31ee17b7",
      "persist_plan_meta": {
        "naming_policy_version": "v2.0",
        "persist_plan_digest": "be97ecb352a3f94ee7e31d0ee4b4843e7262a310833eafe68603f1d825046d43"
      },
      "artifact_briefs": [
        {
          "path": "nostack_live_e2e_tid_screenplay_exec_2.json",
          "brief": "Final screenplay content"
        }
      ]
    },
    "artifact_locations": [
      {
        "role": "screenplay",
        "path": "/home/zhendong_li/frameworkers/FrameWorkers/Runtime/nostack_live_e2e_outputs/workspace_global_20260330_121001_808449/artifacts/ScreenplayAgent/screenplay/nostack_live_e2e_tid_screenplay_exec_2.json"
      }
    ]
  },
  {
    "content": "StoryboardAgent successfully generated a detailed storyboard for a contemplative library scene, focusing on Elara's discovery of a nostalgic bookmark, employing intimate camera work and consistent style, though the pacing was noted as potentially too fast.",
    "agent_id": "StoryboardAgent",
    "task_id": "nostack_live_e2e_tid",
    "created_at": "2026-03-30T12:11:58.519510+00:00",
    "execution_result": {
      "status": "COMPLETED",
      "execution_id": "exec_3_5d84689c",
      "persist_plan_meta": {
        "naming_policy_version": "v2.0",
        "persist_plan_digest": "2942867ee3429bcfce79609d98e4c0eed0414e5088d27482bc7ecf9eeddf26fb"
      },
      "artifact_briefs": [
        {
          "path": "nostack_live_e2e_tid_storyboard_exec_3.json",
          "brief": "Generated storyboard JSON for the scene."
        }
      ]
    },
    "artifact_locations": [
      {
        "role": "storyboard",
        "path": "/home/zhendong_li/frameworkers/FrameWorkers/Runtime/nostack_live_e2e_outputs/workspace_global_20260330_121001_808449/artifacts/storyboard/nostack_live_e2e_tid_storyboard_exec_3.json"
      }
    ]
  },
  {
    "content": "The KeyFrameAgent successfully generated global visual anchors for characters and locations, scene-specific stability keyframes, and a comprehensive set of shot-level keyframes for all scenes and shots.",
    "agent_id": "KeyFrameAgent",
    "task_id": "nostack_live_e2e_tid",
    "created_at": "2026-03-30T12:13:51.402718+00:00",
    "execution_result": {
      "status": "COMPLETED",
      "execution_id": "exec_4_cccef9c0",
      "persist_plan_meta": {
        "naming_policy_version": "v2.0",
        "persist_plan_digest": "47ed607b23c45f0c395a12a14ec4a3a9e5e776b801c211d16832a8fbf69d0dd7"
      },
      "artifact_briefs": [
        {
          "path": "nostack_live_e2e_tid_keyframes_exec_4.json",
          "brief": "Structured keyframe data in JSON format."
        },
        {
          "path": "nostack_live_e2e_tid_img_loc_001_global.png",
          "brief": "Global visual anchor image for location 'loc_001'."
        },
        {
          "path": "nostack_live_e2e_tid_img_char_001_global.png",
          "brief": "Global visual anchor image for character 'char_001'."
        },
        {
          "path": "nostack_live_e2e_tid_img_loc_001_sc_001.png",
          "brief": "Scene-adapted stability keyframe for location 'loc_001' in scene 'sc_001'."
        },
        {
          "path": "nostack_live_e2e_tid_img_char_001_sc_001.png",
          "brief": "Scene-adapted stability keyframe for character 'char_001' in scene 'sc_001'."
        },
        {
          "path": "nostack_live_e2e_tid_img_sh_001_kf_01.png",
          "brief": "Keyframe 1 for shot 'sh_001'."
        },
        {
          "path": "nostack_live_e2e_tid_img_sh_002_kf_01.png",
          "brief": "Keyframe 1 for shot 'sh_002'."
        },
        {
          "path": "nostack_live_e2e_tid_img_sh_003_kf_02.png",
          "brief": "Keyframe 2 for shot 'sh_003'."
        },
        {
          "path": "nostack_live_e2e_tid_img_sh_003_kf_01.png",
          "brief": "Keyframe 1 for shot 'sh_003'."
        },
        {
          "path": "nostack_live_e2e_tid_img_sh_006_kf_02.png",
          "brief": "Keyframe 2 for shot 'sh_006'."
        },
        {
          "path": "nostack_live_e2e_tid_img_sh_006_kf_01.png",
          "brief": "Keyframe 1 for shot 'sh_006'."
        },
        {
          "path": "nostack_live_e2e_tid_img_sh_005_kf_01.png",
          "brief": "Keyframe 1 for shot 'sh_005'."
        },
        {
          "path": "nostack_live_e2e_tid_img_sh_004_kf_01.png",
          "brief": "Keyframe 1 for shot 'sh_004'."
        },
        {
          "path": "nostack_live_e2e_tid_keyframes_manifest.json",
          "brief": "Manifest file for all generated keyframes."
        }
      ]
    },
    "artifact_locations": [
      {
        "role": "keyframes",
        "path": "/home/zhendong_li/frameworkers/FrameWorkers/Runtime/nostack_live_e2e_outputs/workspace_global_20260330_121001_808449/artifacts/keyframes/nostack_live_e2e_tid_keyframes_exec_4.json"
      },
      {
        "role": "img_loc_001_global",
        "path": "/home/zhendong_li/frameworkers/FrameWorkers/Runtime/nostack_live_e2e_outputs/workspace_global_20260330_121001_808449/artifacts/media/KeyFrameAgent/image/nostack_live_e2e_tid_img_loc_001_global.png"
      },
      {
        "role": "img_char_001_global",
        "path": "/home/zhendong_li/frameworkers/FrameWorkers/Runtime/nostack_live_e2e_outputs/workspace_global_20260330_121001_808449/artifacts/media/KeyFrameAgent/image/nostack_live_e2e_tid_img_char_001_global.png"
      },
      {
        "role": "img_loc_001_sc_001",
        "path": "/home/zhendong_li/frameworkers/FrameWorkers/Runtime/nostack_live_e2e_outputs/workspace_global_20260330_121001_808449/artifacts/media/KeyFrameAgent/image/nostack_live_e2e_tid_img_loc_001_sc_001.png"
      },
      {
        "role": "img_char_001_sc_001",
        "path": "/home/zhendong_li/frameworkers/FrameWorkers/Runtime/nostack_live_e2e_outputs/workspace_global_20260330_121001_808449/artifacts/media/KeyFrameAgent/image/nostack_live_e2e_tid_img_char_001_sc_001.png"
      },
      {
        "role": "img_sh_001_kf_01",
        "path": "/home/zhendong_li/frameworkers/FrameWorkers/Runtime/nostack_live_e2e_outputs/workspace_global_20260330_121001_808449/artifacts/media/KeyFrameAgent/image/nostack_live_e2e_tid_img_sh_001_kf_01.png"
      },
      {
        "role": "img_sh_002_kf_01",
        "path": "/home/zhendong_li/frameworkers/FrameWorkers/Runtime/nostack_live_e2e_outputs/workspace_global_20260330_121001_808449/artifacts/media/KeyFrameAgent/image/nostack_live_e2e_tid_img_sh_002_kf_01.png"
      },
      {
        "role": "img_sh_003_kf_02",
        "path": "/home/zhendong_li/frameworkers/FrameWorkers/Runtime/nostack_live_e2e_outputs/workspace_global_20260330_121001_808449/artifacts/media/KeyFrameAgent/image/nostack_live_e2e_tid_img_sh_003_kf_02.png"
      },
      {
        "role": "img_sh_003_kf_01",
        "path": "/home/zhendong_li/frameworkers/FrameWorkers/Runtime/nostack_live_e2e_outputs/workspace_global_20260330_121001_808449/artifacts/media/KeyFrameAgent/image/nostack_live_e2e_tid_img_sh_003_kf_01.png"
      },
      {
        "role": "img_sh_006_kf_02",
        "path": "/home/zhendong_li/frameworkers/FrameWorkers/Runtime/nostack_live_e2e_outputs/workspace_global_20260330_121001_808449/artifacts/media/KeyFrameAgent/image/nostack_live_e2e_tid_img_sh_006_kf_02.png"
      },
      {
        "role": "img_sh_006_kf_01",
        "path": "/home/zhendong_li/frameworkers/FrameWorkers/Runtime/nostack_live_e2e_outputs/workspace_global_20260330_121001_808449/artifacts/media/KeyFrameAgent/image/nostack_live_e2e_tid_img_sh_006_kf_01.png"
      },
      {
        "role": "img_sh_005_kf_01",
        "path": "/home/zhendong_li/frameworkers/FrameWorkers/Runtime/nostack_live_e2e_outputs/workspace_global_20260330_121001_808449/artifacts/media/KeyFrameAgent/image/nostack_live_e2e_tid_img_sh_005_kf_01.png"
      },
      {
        "role": "img_sh_004_kf_01",
        "path": "/home/zhendong_li/frameworkers/FrameWorkers/Runtime/nostack_live_e2e_outputs/workspace_global_20260330_121001_808449/artifacts/media/KeyFrameAgent/image/nostack_live_e2e_tid_img_sh_004_kf_01.png"
      },
      {
        "role": "keyframes_manifest",
        "path": "/home/zhendong_li/frameworkers/FrameWorkers/Runtime/nostack_live_e2e_outputs/workspace_global_20260330_121001_808449/artifacts/keyframes/nostack_live_e2e_tid_keyframes_manifest.json"
      }
    ]
  },
  {
    "content": "VideoAgent successfully created a final video asset (clip_final.mp4) consisting of 1 scene and 6 shot segments, totaling 11.0 seconds, with an average shot duration of 1.83 seconds.",
    "agent_id": "VideoAgent",
    "task_id": "nostack_live_e2e_tid",
    "created_at": "2026-03-30T12:21:56.408548+00:00",
    "execution_result": {
      "status": "COMPLETED",
      "execution_id": "exec_5_4c35efb6",
      "persist_plan_meta": {
        "naming_policy_version": "v2.0",
        "persist_plan_digest": "9b1d237dfb29c0491d513434657eb86699af764dd8f34a4e86a6940f99840bbc"
      },
      "artifact_briefs": [
        {
          "path": "nostack_live_e2e_tid_video_exec_5.json",
          "brief": "Video plan and metadata"
        },
        {
          "path": "nostack_live_e2e_tid_clip_sh_001.mp4",
          "brief": "Video clip for shot sh_001"
        },
        {
          "path": "nostack_live_e2e_tid_clip_sh_002.mp4",
          "brief": "Video clip for shot sh_002"
        },
        {
          "path": "nostack_live_e2e_tid_clip_sh_003.mp4",
          "brief": "Video clip for shot sh_003"
        },
        {
          "path": "nostack_live_e2e_tid_clip_sh_004.mp4",
          "brief": "Video clip for shot sh_004"
        },
        {
          "path": "nostack_live_e2e_tid_clip_sh_005.mp4",
          "brief": "Video clip for shot sh_005"
        },
        {
          "path": "nostack_live_e2e_tid_clip_sh_006.mp4",
          "brief": "Video clip for shot sh_006"
        },
        {
          "path": "nostack_live_e2e_tid_clip_sc_001.mp4",
          "brief": "Assembled video clip for scene sc_001"
        },
        {
          "path": "nostack_live_e2e_tid_clip_final.mp4",
          "brief": "Final assembled video clip"
        }
      ]
    },
    "artifact_locations": [
      {
        "role": "video",
        "path": "/home/zhendong_li/frameworkers/FrameWorkers/Runtime/nostack_live_e2e_outputs/workspace_global_20260330_121001_808449/artifacts/nostack_live_e2e_tid_video_exec_5.json"
      },
      {
        "role": "clip_sh_001",
        "path": "/home/zhendong_li/frameworkers/FrameWorkers/Runtime/nostack_live_e2e_outputs/workspace_global_20260330_121001_808449/artifacts/media/VideoAgent/video/nostack_live_e2e_tid_clip_sh_001.mp4"
      },
      {
        "role": "clip_sh_002",
        "path": "/home/zhendong_li/frameworkers/FrameWorkers/Runtime/nostack_live_e2e_outputs/workspace_global_20260330_121001_808449/artifacts/media/VideoAgent/video/nostack_live_e2e_tid_clip_sh_002.mp4"
      },
      {
        "role": "clip_sh_003",
        "path": "/home/zhendong_li/frameworkers/FrameWorkers/Runtime/nostack_live_e2e_outputs/workspace_global_20260330_121001_808449/artifacts/media/VideoAgent/video/nostack_live_e2e_tid_clip_sh_003.mp4"
      },
      {
        "role": "clip_sh_004",
        "path": "/home/zhendong_li/frameworkers/FrameWorkers/Runtime/nostack_live_e2e_outputs/workspace_global_20260330_121001_808449/artifacts/media/VideoAgent/video/nostack_live_e2e_tid_clip_sh_004.mp4"
      },
      {
        "role": "clip_sh_005",
        "path": "/home/zhendong_li/frameworkers/FrameWorkers/Runtime/nostack_live_e2e_outputs/workspace_global_20260330_121001_808449/artifacts/media/VideoAgent/video/nostack_live_e2e_tid_clip_sh_005.mp4"
      },
      {
        "role": "clip_sh_006",
        "path": "/home/zhendong_li/frameworkers/FrameWorkers/Runtime/nostack_live_e2e_outputs/workspace_global_20260330_121001_808449/artifacts/media/VideoAgent/video/nostack_live_e2e_tid_clip_sh_006.mp4"
      },
      {
        "role": "clip_sc_001",
        "path": "/home/zhendong_li/frameworkers/FrameWorkers/Runtime/nostack_live_e2e_outputs/workspace_global_20260330_121001_808449/artifacts/media/VideoAgent/video/nostack_live_e2e_tid_clip_sc_001.mp4"
      },
      {
        "role": "clip_final",
        "path": "/home/zhendong_li/frameworkers/FrameWorkers/Runtime/nostack_live_e2e_outputs/workspace_global_20260330_121001_808449/artifacts/media/VideoAgent/video/nostack_live_e2e_tid_clip_final.mp4"
      }
    ]
  }
]
```
