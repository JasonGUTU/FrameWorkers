# Global memory

Global memory for workspace `workspace_global_20260330_113441_853472`. The **Entries** section is the canonical JSON array. The **File tree** below is a **human-readable snapshot** at write time (may be truncated); for **automation** (persist paths, input packaging, Director), use **live** workspace file-tree APIs and ``artifact_locations`` — the snapshot is not authoritative.

## File tree

<!-- FW_FILE_TREE_BEGIN -->
```
.file_metadata.json
    nostack_live_e2e_tid_keyframes_exec_4.json
    nostack_live_e2e_tid_keyframes_manifest.json
        nostack_live_e2e_tid_img_char_001_global.png
        nostack_live_e2e_tid_img_char_001_sc_001.png
        nostack_live_e2e_tid_img_loc_001_global.png
        nostack_live_e2e_tid_img_loc_001_sc_001.png
        nostack_live_e2e_tid_img_sh_001_kf_01.png
        nostack_live_e2e_tid_img_sh_001_kf_02.png
        nostack_live_e2e_tid_img_sh_002_kf_01.png
        nostack_live_e2e_tid_img_sh_002_kf_02.png
        nostack_live_e2e_tid_img_sh_003_kf_01.png
        nostack_live_e2e_tid_img_sh_003_kf_02.png
        nostack_live_e2e_tid_img_sh_004_kf_01.png
    nostack_live_e2e_tid_screenplay_exec_1.json
    nostack_live_e2e_tid_story_blueprint_exec_1.json
    nostack_live_e2e_tid_storyboard_exec_3.json
global_memory.md
logs.jsonl
```
<!-- FW_FILE_TREE_END -->

## Entries

```json
[
  {
    "content": "A solitary cyclist finds a fleeting moment of warmth and solitude beneath a single streetlight on a rain-slicked cobblestone street.",
    "agent_id": "StoryAgent",
    "task_id": "nostack_live_e2e_tid",
    "created_at": "2026-03-30T11:35:08.772313+00:00",
    "execution_result": {
      "status": "COMPLETED",
      "execution_id": "exec_1_c9ef3d73",
      "persist_plan_meta": {
        "naming_policy_version": "v2.0",
        "persist_plan_digest": "723eac71bb0210975c032c63b1a4543c5b9107fd28054524c33f6e319da8806e"
      },
      "artifact_briefs": [
        {
          "path": "/home/zhendong_li/frameworkers/FrameWorkers/Runtime/nostack_live_e2e_outputs/workspace_global_20260330_113441_853472/artifacts/story_blueprint/nostack_live_e2e_tid_story_blueprint_exec_1.json",
          "brief": "A detailed story blueprint outlining the narrative, characters, locations, and scene structure for the planned short clip."
        }
      ]
    },
    "artifact_locations": [
      {
        "role": "story_blueprint",
        "path": "/home/zhendong_li/frameworkers/FrameWorkers/Runtime/nostack_live_e2e_outputs/workspace_global_20260330_113441_853472/artifacts/story_blueprint/nostack_live_e2e_tid_story_blueprint_exec_1.json"
      }
    ]
  },
  {
    "content": "Screenplay 'A Fleeting Glow' detailing a solitary cyclist's fleeting encounter with warmth in a rainy alley was successfully generated.",
    "agent_id": "ScreenplayAgent",
    "task_id": "nostack_live_e2e_tid",
    "created_at": "2026-03-30T11:35:39.478229+00:00",
    "execution_result": {
      "status": "COMPLETED",
      "execution_id": "exec_2_df1d4d10",
      "persist_plan_meta": {
        "naming_policy_version": "v2.0",
        "persist_plan_digest": "9359becc61b8032a5c022c3012d9bac5460cbebe08288bb9322a9b101fb70590"
      },
      "artifact_briefs": [
        {
          "path": "/home/zhendong_li/frameworkers/FrameWorkers/Runtime/nostack_live_e2e_outputs/workspace_global_20260330_113441_853472/artifacts/screenplay/nostack_live_e2e_tid_screenplay_exec_1.json",
          "brief": "The generated screenplay script for 'A Fleeting Glow'."
        }
      ]
    },
    "artifact_locations": [
      {
        "role": "screenplay",
        "path": "/home/zhendong_li/frameworkers/FrameWorkers/Runtime/nostack_live_e2e_outputs/workspace_global_20260330_113441_853472/artifacts/screenplay/nostack_live_e2e_tid_screenplay_exec_1.json"
      }
    ]
  },
  {
    "content": "The StoryboardAgent successfully generated a visually coherent storyboard, detailing scenes and shots that effectively portray the screenplay's thematic and pacing goals, including the 'fleeting glow' concept.",
    "agent_id": "StoryboardAgent",
    "task_id": "nostack_live_e2e_tid",
    "created_at": "2026-03-30T11:36:56.966413+00:00",
    "execution_result": {
      "status": "COMPLETED",
      "execution_id": "exec_3_cccf6926",
      "persist_plan_meta": {
        "naming_policy_version": "v2.0",
        "persist_plan_digest": "2942867ee3429bcfce79609d98e4c0eed0414e5088d27482bc7ecf9eeddf26fb"
      },
      "artifact_briefs": [
        {
          "path": "/home/zhendong_li/frameworkers/FrameWorkers/Runtime/nostack_live_e2e_outputs/workspace_global_20260330_113441_853472/artifacts/storyboard/nostack_live_e2e_tid_storyboard_exec_3.json",
          "brief": "Detailed storyboard outlining scenes and shots, including camera angles, movements, visual goals, and keyframe plans, for the given screenplay."
        }
      ]
    },
    "artifact_locations": [
      {
        "role": "storyboard",
        "path": "/home/zhendong_li/frameworkers/FrameWorkers/Runtime/nostack_live_e2e_outputs/workspace_global_20260330_113441_853472/artifacts/storyboard/nostack_live_e2e_tid_storyboard_exec_3.json"
      }
    ]
  }
]
```
