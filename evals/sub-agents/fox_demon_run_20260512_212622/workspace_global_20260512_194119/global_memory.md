# Global memory — `workspace_global_20260512_194119`

Per-execution record of every artifact persisted in this workspace. Each entry below is one agent execution; its `artifacts` array carries the natural-language `caption`, `scope`, absolute `path` and `mime` for every file that execution wrote.

`InputResolver` reads this index to match artifacts against each consumer agent's `[label]` slots. Execution history (including failures) lives in the assistant executions table, not here.

## Entries

```json
[
  {
    "execution_id": "brief_20260512_194249_875467",
    "agent_id": "user",
    "step_id": "",
    "created_at": "2026-05-12T19:42:49.877305+00:00",
    "artifacts": [
      {
        "caption": "Structured metadata document (JSON) for a user-submitted text brief. Payload carries the raw text verbatim. Pipeline entry point — consumed by story / screenplay / narration agents.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260512_194119/inputs/brief_20260512_194249_875467.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_1_53e00908",
    "agent_id": "StoryAgent",
    "step_id": "step_1_1bc74b1f",
    "created_at": "2026-05-12T19:43:32.485689+00:00",
    "artifacts": [
      {
        "caption": "Story blueprint: 5 scene(s), 3 character(s). Structured input for screenplay generation.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260512_194119/artifacts/StoryAgent/step_1_1bc74b1f_storyagent_exec_1.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_2_e8013084",
    "agent_id": "ScreenplayAgent",
    "step_id": "step_2_3d8bb556",
    "created_at": "2026-05-12T19:45:16.004426+00:00",
    "artifacts": [
      {
        "caption": "Screenplay: 5 scene(s), 15 shot(s). Input for keyframe planning and audio scoring.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260512_194119/artifacts/ScreenplayAgent/step_2_3d8bb556_screenplayagent_exec_2.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_3_ecd9477a",
    "agent_id": "KeyFrameAgent",
    "step_id": "step_3_e6b31cc8",
    "created_at": "2026-05-12T19:52:10.100039+00:00",
    "artifacts": [
      {
        "caption": "Global character reference image for char_002. Visual identity anchor — not a video frame.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260512_194119/artifacts/media/KeyFrameAgent/image/step_3_e6b31cc8_img_char_002_global.png",
        "mime": "image/png"
      },
      {
        "caption": "Global character reference image for char_003. Visual identity anchor — not a video frame.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260512_194119/artifacts/media/KeyFrameAgent/image/step_3_e6b31cc8_img_char_003_global.png",
        "mime": "image/png"
      },
      {
        "caption": "Global prop reference image for prop_001. Visual identity anchor — not a video frame.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260512_194119/artifacts/media/KeyFrameAgent/image/step_3_e6b31cc8_img_prop_001_global.png",
        "mime": "image/png"
      },
      {
        "caption": "Global location reference image for loc_001. Visual identity anchor — not a video frame.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260512_194119/artifacts/media/KeyFrameAgent/image/step_3_e6b31cc8_img_loc_001_global.png",
        "mime": "image/png"
      },
      {
        "caption": "Global character reference image for char_001. Visual identity anchor — not a video frame.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260512_194119/artifacts/media/KeyFrameAgent/image/step_3_e6b31cc8_img_char_001_global.png",
        "mime": "image/png"
      },
      {
        "caption": "Global location reference image for loc_002. Visual identity anchor — not a video frame.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260512_194119/artifacts/media/KeyFrameAgent/image/step_3_e6b31cc8_img_loc_002_global.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level location reference for loc_001 in scene sc_004. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_004",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260512_194119/artifacts/media/KeyFrameAgent/image/step_3_e6b31cc8_img_loc_001_sc_004.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level location reference for loc_001 in scene sc_002. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_002",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260512_194119/artifacts/media/KeyFrameAgent/image/step_3_e6b31cc8_img_loc_001_sc_002.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level character reference for char_002 in scene sc_004. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_004",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260512_194119/artifacts/media/KeyFrameAgent/image/step_3_e6b31cc8_img_char_002_sc_004.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level character reference for char_002 in scene sc_005. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_005",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260512_194119/artifacts/media/KeyFrameAgent/image/step_3_e6b31cc8_img_char_002_sc_005.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level prop reference for prop_001 in scene sc_005. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_005",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260512_194119/artifacts/media/KeyFrameAgent/image/step_3_e6b31cc8_img_prop_001_sc_005.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level location reference for loc_002 in scene sc_003. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_003",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260512_194119/artifacts/media/KeyFrameAgent/image/step_3_e6b31cc8_img_loc_002_sc_003.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level character reference for char_001 in scene sc_002. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_002",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260512_194119/artifacts/media/KeyFrameAgent/image/step_3_e6b31cc8_img_char_001_sc_002.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level character reference for char_002 in scene sc_002. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_002",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260512_194119/artifacts/media/KeyFrameAgent/image/step_3_e6b31cc8_img_char_002_sc_002.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level prop reference for prop_001 in scene sc_003. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_003",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260512_194119/artifacts/media/KeyFrameAgent/image/step_3_e6b31cc8_img_prop_001_sc_003.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level character reference for char_001 in scene sc_005. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_005",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260512_194119/artifacts/media/KeyFrameAgent/image/step_3_e6b31cc8_img_char_001_sc_005.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level character reference for char_002 in scene sc_001. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_001",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260512_194119/artifacts/media/KeyFrameAgent/image/step_3_e6b31cc8_img_char_002_sc_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level character reference for char_002 in scene sc_003. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_003",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260512_194119/artifacts/media/KeyFrameAgent/image/step_3_e6b31cc8_img_char_002_sc_003.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level prop reference for prop_001 in scene sc_004. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_004",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260512_194119/artifacts/media/KeyFrameAgent/image/step_3_e6b31cc8_img_prop_001_sc_004.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level character reference for char_001 in scene sc_004. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_004",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260512_194119/artifacts/media/KeyFrameAgent/image/step_3_e6b31cc8_img_char_001_sc_004.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level character reference for char_001 in scene sc_003. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_003",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260512_194119/artifacts/media/KeyFrameAgent/image/step_3_e6b31cc8_img_char_001_sc_003.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level prop reference for prop_001 in scene sc_001. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_001",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260512_194119/artifacts/media/KeyFrameAgent/image/step_3_e6b31cc8_img_prop_001_sc_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level prop reference for prop_001 in scene sc_002. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_002",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260512_194119/artifacts/media/KeyFrameAgent/image/step_3_e6b31cc8_img_prop_001_sc_002.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level character reference for char_003 in scene sc_003. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_003",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260512_194119/artifacts/media/KeyFrameAgent/image/step_3_e6b31cc8_img_char_003_sc_003.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level location reference for loc_001 in scene sc_001. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_001",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260512_194119/artifacts/media/KeyFrameAgent/image/step_3_e6b31cc8_img_loc_001_sc_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level character reference for char_001 in scene sc_001. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_001",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260512_194119/artifacts/media/KeyFrameAgent/image/step_3_e6b31cc8_img_char_001_sc_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level location reference for loc_001 in scene sc_005. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_005",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260512_194119/artifacts/media/KeyFrameAgent/image/step_3_e6b31cc8_img_loc_001_sc_005.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_005 in scene sc_002. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_005",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260512_194119/artifacts/media/KeyFrameAgent/image/step_3_e6b31cc8_img_sh_005_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_002 in scene sc_001. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_002",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260512_194119/artifacts/media/KeyFrameAgent/image/step_3_e6b31cc8_img_sh_002_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_006 in scene sc_002. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_006",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260512_194119/artifacts/media/KeyFrameAgent/image/step_3_e6b31cc8_img_sh_006_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_014 in scene sc_005. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_014",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260512_194119/artifacts/media/KeyFrameAgent/image/step_3_e6b31cc8_img_sh_014_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_011 in scene sc_004. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_011",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260512_194119/artifacts/media/KeyFrameAgent/image/step_3_e6b31cc8_img_sh_011_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_008 in scene sc_003. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_008",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260512_194119/artifacts/media/KeyFrameAgent/image/step_3_e6b31cc8_img_sh_008_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_003 in scene sc_001. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_003",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260512_194119/artifacts/media/KeyFrameAgent/image/step_3_e6b31cc8_img_sh_003_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_012 in scene sc_004. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_012",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260512_194119/artifacts/media/KeyFrameAgent/image/step_3_e6b31cc8_img_sh_012_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_013 in scene sc_005. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_013",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260512_194119/artifacts/media/KeyFrameAgent/image/step_3_e6b31cc8_img_sh_013_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_004 in scene sc_002. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_004",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260512_194119/artifacts/media/KeyFrameAgent/image/step_3_e6b31cc8_img_sh_004_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_001 in scene sc_001. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_001",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260512_194119/artifacts/media/KeyFrameAgent/image/step_3_e6b31cc8_img_sh_001_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_009 in scene sc_003. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_009",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260512_194119/artifacts/media/KeyFrameAgent/image/step_3_e6b31cc8_img_sh_009_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_015 in scene sc_005. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_015",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260512_194119/artifacts/media/KeyFrameAgent/image/step_3_e6b31cc8_img_sh_015_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_007 in scene sc_003. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_007",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260512_194119/artifacts/media/KeyFrameAgent/image/step_3_e6b31cc8_img_sh_007_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_010 in scene sc_003. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_010",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260512_194119/artifacts/media/KeyFrameAgent/image/step_3_e6b31cc8_img_sh_010_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Keyframe planning document: 5 scene(s), 15 shot(s), with per-shot frame descriptions and motion hints. Consumed by a downstream image-to-video generation step.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260512_194119/artifacts/KeyFrameAgent/step_3_e6b31cc8_keyframeagent_exec_3.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_4_7199c8ef",
    "agent_id": "VideoAgent",
    "step_id": "step_4_e5fbf683",
    "created_at": "2026-05-12T20:57:41.037289+00:00",
    "artifacts": [
      {
        "caption": "[JSON MANIFEST] Video-assembly planning metadata: 5 scene(s), 15 shot clip(s) with timing. Read by a downstream audio-mix step's LLM for mix planning.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260512_194119/artifacts/VideoAgent/step_4_e5fbf683_videoagent_exec_4.json",
        "mime": "application/json"
      }
    ]
  }
]
```
