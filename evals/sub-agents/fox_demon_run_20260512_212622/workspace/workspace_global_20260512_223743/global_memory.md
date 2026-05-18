# Global memory — `workspace_global_20260512_223743`

Per-execution record of every artifact persisted in this workspace. Each entry below is one agent execution; its `artifacts` array carries the natural-language `caption`, `scope`, absolute `path` and `mime` for every file that execution wrote.

`InputResolver` reads this index to match artifacts against each consumer agent's `[label]` slots. Execution history (including failures) lives in the assistant executions table, not here.

## Entries

```json
[
  {
    "execution_id": "upload_20260512_223801_048018",
    "agent_id": "user",
    "step_id": "",
    "created_at": "2026-05-12T22:38:01.050159+00:00",
    "artifacts": [
      {
        "caption": "Global character reference image. Visual identity anchor for downstream keyframe generation.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/inputs/20260512_223801_048018_step_3_e6b31cc8_img_char_001_global.png",
        "mime": "image/png"
      }
    ]
  },
  {
    "execution_id": "brief_20260512_223801_057913",
    "agent_id": "user",
    "step_id": "",
    "created_at": "2026-05-12T22:38:01.059360+00:00",
    "artifacts": [
      {
        "caption": "Structured metadata document (JSON) for a user-submitted text brief. Payload carries the raw text verbatim. Pipeline entry point — consumed by story / screenplay / narration agents.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/inputs/brief_20260512_223801_057913.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_1_8b99db26",
    "agent_id": "IntakeImageAgent",
    "step_id": "step_1_81595939",
    "created_at": "2026-05-12T22:38:10.527569+00:00",
    "artifacts": [
      {
        "caption": "Structured metadata document (JSON) for a user-uploaded image. Payload carries the visual description and image-asset metadata.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/IntakeImageAgent/step_1_81595939_intakeimageagent_exec_1.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_2_2f541902",
    "agent_id": "BriefEnricherAgent",
    "step_id": "step_2_4ce0f309",
    "created_at": "2026-05-12T22:38:26.549589+00:00",
    "artifacts": [
      {
        "caption": "Enriched creative brief with visual reference descriptions integrated. Supersedes the raw user brief for story generation — contains the user's original concept plus detailed visual descriptions of uploaded reference images.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/BriefEnricherAgent/step_2_4ce0f309_briefenricheragent_exec_2.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_3_b1cb6e16",
    "agent_id": "StoryAgent",
    "step_id": "step_3_c63b3878",
    "created_at": "2026-05-12T22:39:08.167113+00:00",
    "artifacts": [
      {
        "caption": "Story blueprint: 5 scene(s), 3 character(s). Structured input for screenplay generation.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/StoryAgent/step_3_c63b3878_storyagent_exec_3.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_4_a585afad",
    "agent_id": "ScreenplayAgent",
    "step_id": "step_4_a76cf964",
    "created_at": "2026-05-12T22:40:25.226972+00:00",
    "artifacts": [
      {
        "caption": "Screenplay: 5 scene(s), 15 shot(s). Input for keyframe planning and audio scoring.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/ScreenplayAgent/step_4_a76cf964_screenplayagent_exec_4.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_6_321c6529",
    "agent_id": "KeyFrameAgent",
    "step_id": "step_5_21c87218",
    "created_at": "2026-05-12T22:54:40.167539+00:00",
    "artifacts": [
      {
        "caption": "Global character reference image for char_001. Visual identity anchor — not a video frame.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/media/KeyFrameAgent/image/step_5_21c87218_img_char_001_global.png",
        "mime": "image/png"
      },
      {
        "caption": "Global prop reference image for prop_002. Visual identity anchor — not a video frame.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/media/KeyFrameAgent/image/step_5_21c87218_img_prop_002_global.png",
        "mime": "image/png"
      },
      {
        "caption": "Global character reference image for char_003. Visual identity anchor — not a video frame.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/media/KeyFrameAgent/image/step_5_21c87218_img_char_003_global.png",
        "mime": "image/png"
      },
      {
        "caption": "Global prop reference image for prop_005. Visual identity anchor — not a video frame.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/media/KeyFrameAgent/image/step_5_21c87218_img_prop_005_global.png",
        "mime": "image/png"
      },
      {
        "caption": "Global character reference image for char_002. Visual identity anchor — not a video frame.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/media/KeyFrameAgent/image/step_5_21c87218_img_char_002_global.png",
        "mime": "image/png"
      },
      {
        "caption": "Global location reference image for loc_001. Visual identity anchor — not a video frame.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/media/KeyFrameAgent/image/step_5_21c87218_img_loc_001_global.png",
        "mime": "image/png"
      },
      {
        "caption": "Global prop reference image for prop_001. Visual identity anchor — not a video frame.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/media/KeyFrameAgent/image/step_5_21c87218_img_prop_001_global.png",
        "mime": "image/png"
      },
      {
        "caption": "Global prop reference image for prop_004. Visual identity anchor — not a video frame.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/media/KeyFrameAgent/image/step_5_21c87218_img_prop_004_global.png",
        "mime": "image/png"
      },
      {
        "caption": "Global prop reference image for prop_003. Visual identity anchor — not a video frame.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/media/KeyFrameAgent/image/step_5_21c87218_img_prop_003_global.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level character reference for char_001 in scene sc_004. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_004",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/media/KeyFrameAgent/image/step_5_21c87218_img_char_001_sc_004.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level character reference for char_003 in scene sc_003. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_003",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/media/KeyFrameAgent/image/step_5_21c87218_img_char_003_sc_003.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level character reference for char_001 in scene sc_001. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_001",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/media/KeyFrameAgent/image/step_5_21c87218_img_char_001_sc_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level character reference for char_001 in scene sc_002. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_002",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/media/KeyFrameAgent/image/step_5_21c87218_img_char_001_sc_002.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level prop reference for prop_004 in scene sc_003. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_003",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/media/KeyFrameAgent/image/step_5_21c87218_img_prop_004_sc_003.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level prop reference for prop_003 in scene sc_002. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_002",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/media/KeyFrameAgent/image/step_5_21c87218_img_prop_003_sc_002.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level character reference for char_002 in scene sc_002. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_002",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/media/KeyFrameAgent/image/step_5_21c87218_img_char_002_sc_002.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level prop reference for prop_003 in scene sc_004. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_004",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/media/KeyFrameAgent/image/step_5_21c87218_img_prop_003_sc_004.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level prop reference for prop_005 in scene sc_003. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_003",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/media/KeyFrameAgent/image/step_5_21c87218_img_prop_005_sc_003.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level location reference for loc_001 in scene sc_001. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_001",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/media/KeyFrameAgent/image/step_5_21c87218_img_loc_001_sc_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level character reference for char_001 in scene sc_005. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_005",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/media/KeyFrameAgent/image/step_5_21c87218_img_char_001_sc_005.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level prop reference for prop_001 in scene sc_001. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_001",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/media/KeyFrameAgent/image/step_5_21c87218_img_prop_001_sc_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level character reference for char_002 in scene sc_005. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_005",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/media/KeyFrameAgent/image/step_5_21c87218_img_char_002_sc_005.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level location reference for loc_001 in scene sc_002. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_002",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/media/KeyFrameAgent/image/step_5_21c87218_img_loc_001_sc_002.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level character reference for char_002 in scene sc_004. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_004",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/media/KeyFrameAgent/image/step_5_21c87218_img_char_002_sc_004.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level location reference for loc_001 in scene sc_005. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_005",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/media/KeyFrameAgent/image/step_5_21c87218_img_loc_001_sc_005.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level location reference for loc_001 in scene sc_004. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_004",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/media/KeyFrameAgent/image/step_5_21c87218_img_loc_001_sc_004.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level prop reference for prop_001 in scene sc_004. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_004",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/media/KeyFrameAgent/image/step_5_21c87218_img_prop_001_sc_004.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level location reference for loc_001 in scene sc_003. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_003",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/media/KeyFrameAgent/image/step_5_21c87218_img_loc_001_sc_003.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level character reference for char_001 in scene sc_003. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_003",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/media/KeyFrameAgent/image/step_5_21c87218_img_char_001_sc_003.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level prop reference for prop_003 in scene sc_005. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_005",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/media/KeyFrameAgent/image/step_5_21c87218_img_prop_003_sc_005.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level character reference for char_002 in scene sc_001. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_001",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/media/KeyFrameAgent/image/step_5_21c87218_img_char_002_sc_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level prop reference for prop_002 in scene sc_001. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_001",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/media/KeyFrameAgent/image/step_5_21c87218_img_prop_002_sc_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_004 in scene sc_002. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_004",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/media/KeyFrameAgent/image/step_5_21c87218_img_sh_004_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_006 in scene sc_002. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_006",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/media/KeyFrameAgent/image/step_5_21c87218_img_sh_006_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_007 in scene sc_003. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_007",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/media/KeyFrameAgent/image/step_5_21c87218_img_sh_007_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_010 in scene sc_004. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_010",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/media/KeyFrameAgent/image/step_5_21c87218_img_sh_010_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_015 in scene sc_005. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_015",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/media/KeyFrameAgent/image/step_5_21c87218_img_sh_015_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_009 in scene sc_003. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_009",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/media/KeyFrameAgent/image/step_5_21c87218_img_sh_009_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_002 in scene sc_001. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_002",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/media/KeyFrameAgent/image/step_5_21c87218_img_sh_002_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_005 in scene sc_002. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_005",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/media/KeyFrameAgent/image/step_5_21c87218_img_sh_005_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_012 in scene sc_004. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_012",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/media/KeyFrameAgent/image/step_5_21c87218_img_sh_012_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_011 in scene sc_004. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_011",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/media/KeyFrameAgent/image/step_5_21c87218_img_sh_011_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_001 in scene sc_001. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_001",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/media/KeyFrameAgent/image/step_5_21c87218_img_sh_001_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_008 in scene sc_003. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_008",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/media/KeyFrameAgent/image/step_5_21c87218_img_sh_008_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_013 in scene sc_005. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_013",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/media/KeyFrameAgent/image/step_5_21c87218_img_sh_013_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_003 in scene sc_001. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_003",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/media/KeyFrameAgent/image/step_5_21c87218_img_sh_003_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_014 in scene sc_005. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_014",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/media/KeyFrameAgent/image/step_5_21c87218_img_sh_014_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Keyframe planning document: 5 scene(s), 15 shot(s), with per-shot frame descriptions and motion hints. Consumed by a downstream image-to-video generation step.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/KeyFrameAgent/step_5_21c87218_keyframeagent_exec_6.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_1_f321d4a1",
    "agent_id": "VideoAgent",
    "step_id": "step_1_95d7d1dc",
    "created_at": "2026-05-13T01:08:17.721897+00:00",
    "artifacts": [
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_001] Video clip bytes for shot sh_001. One segment of the final video.",
        "scope": "shot:sh_001",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/media/VideoAgent/video/step_1_95d7d1dc_clip_sh_001.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_002] Video clip bytes for shot sh_002. One segment of the final video.",
        "scope": "shot:sh_002",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/media/VideoAgent/video/step_1_95d7d1dc_clip_sh_002.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_003] Video clip bytes for shot sh_003. One segment of the final video.",
        "scope": "shot:sh_003",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/media/VideoAgent/video/step_1_95d7d1dc_clip_sh_003.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_004] Video clip bytes for shot sh_004. One segment of the final video.",
        "scope": "shot:sh_004",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/media/VideoAgent/video/step_1_95d7d1dc_clip_sh_004.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_005] Video clip bytes for shot sh_005. One segment of the final video.",
        "scope": "shot:sh_005",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/media/VideoAgent/video/step_1_95d7d1dc_clip_sh_005.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_006] Video clip bytes for shot sh_006. One segment of the final video.",
        "scope": "shot:sh_006",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/media/VideoAgent/video/step_1_95d7d1dc_clip_sh_006.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_007] Video clip bytes for shot sh_007. One segment of the final video.",
        "scope": "shot:sh_007",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/media/VideoAgent/video/step_1_95d7d1dc_clip_sh_007.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_008] Video clip bytes for shot sh_008. One segment of the final video.",
        "scope": "shot:sh_008",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/media/VideoAgent/video/step_1_95d7d1dc_clip_sh_008.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_009] Video clip bytes for shot sh_009. One segment of the final video.",
        "scope": "shot:sh_009",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/media/VideoAgent/video/step_1_95d7d1dc_clip_sh_009.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_010] Video clip bytes for shot sh_010. One segment of the final video.",
        "scope": "shot:sh_010",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/media/VideoAgent/video/step_1_95d7d1dc_clip_sh_010.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_011] Video clip bytes for shot sh_011. One segment of the final video.",
        "scope": "shot:sh_011",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/media/VideoAgent/video/step_1_95d7d1dc_clip_sh_011.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_012] Video clip bytes for shot sh_012. One segment of the final video.",
        "scope": "shot:sh_012",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/media/VideoAgent/video/step_1_95d7d1dc_clip_sh_012.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_013] Video clip bytes for shot sh_013. One segment of the final video.",
        "scope": "shot:sh_013",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/media/VideoAgent/video/step_1_95d7d1dc_clip_sh_013.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_014] Video clip bytes for shot sh_014. One segment of the final video.",
        "scope": "shot:sh_014",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/media/VideoAgent/video/step_1_95d7d1dc_clip_sh_014.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_015] Video clip bytes for shot sh_015. One segment of the final video.",
        "scope": "shot:sh_015",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/media/VideoAgent/video/step_1_95d7d1dc_clip_sh_015.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sc_001] Scene-cut bytes for scene sc_001 — all shots concatenated. Intermediate assembly, not final.",
        "scope": "scene:sc_001",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/media/VideoAgent/video/step_1_95d7d1dc_clip_sc_001.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sc_002] Scene-cut bytes for scene sc_002 — all shots concatenated. Intermediate assembly, not final.",
        "scope": "scene:sc_002",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/media/VideoAgent/video/step_1_95d7d1dc_clip_sc_002.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sc_003] Scene-cut bytes for scene sc_003 — all shots concatenated. Intermediate assembly, not final.",
        "scope": "scene:sc_003",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/media/VideoAgent/video/step_1_95d7d1dc_clip_sc_003.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sc_004] Scene-cut bytes for scene sc_004 — all shots concatenated. Intermediate assembly, not final.",
        "scope": "scene:sc_004",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/media/VideoAgent/video/step_1_95d7d1dc_clip_sc_004.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sc_005] Scene-cut bytes for scene sc_005 — all shots concatenated. Intermediate assembly, not final.",
        "scope": "scene:sc_005",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/media/VideoAgent/video/step_1_95d7d1dc_clip_sc_005.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_final] Complete assembled video bytes (15 shots). Final visual deliverable — consumed by a downstream audio-mix step's materializer via ffmpeg for audio extraction + muxing.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/media/VideoAgent/video/step_1_95d7d1dc_clip_final.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[JSON MANIFEST] Video-assembly planning metadata: 5 scene(s), 15 shot clip(s) with timing. Read by a downstream audio-mix step's LLM for mix planning.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/VideoAgent/step_1_95d7d1dc_videoagent_exec_1.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_2_6d76b8a1",
    "agent_id": "TranscriptionAgent",
    "step_id": "step_2_809ce185",
    "created_at": "2026-05-13T01:08:51.997179+00:00",
    "artifacts": [
      {
        "caption": "Transcript (zh): 12 timestamped segment(s). SRT-shaped subtitle artifact — ready for direct burn-in by a compositor's subtitle track (each segment is one SRT cue with start/end seconds + text). Also usable as the 'source text' input to a translation step when bilingual subtitles are needed.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/TranscriptionAgent/step_2_809ce185_transcriptionagent_exec_2.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_3_e46a8619",
    "agent_id": "TranslationAgent",
    "step_id": "step_3_5e035eb4",
    "created_at": "2026-05-13T01:09:08.472331+00:00",
    "artifacts": [
      {
        "caption": "Translation (zh → en). Full structured text translated with original structure preserved (keys / ids / timing / ordering). Output shape mirrors input shape — a translated SRT remains an SRT, a translated screenplay remains a screenplay.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/TranslationAgent/step_3_5e035eb4_translationagent_exec_3.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_4_d87ec989",
    "agent_id": "MusicAgent",
    "step_id": "step_4_9da095c9",
    "created_at": "2026-05-13T01:11:09.743809+00:00",
    "artifacts": [
      {
        "caption": "[BINARY WAV FILE · mime=audio/wav · sys_id aud_music_film] Background-music audio bytes for the film-wide BGM underlay. Consumed by the audio-mix materializer via ffmpeg.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/media/MusicAgent/audio/step_4_9da095c9_aud_music_film.wav",
        "mime": "audio/wav"
      },
      {
        "caption": "[JSON MANIFEST] Background-music planning metadata: 1 cue(s) carrying the LLM-chosen mood for the film-wide BGM underlay. Read by the audio-mix LLM for mix planning.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/MusicAgent/step_4_9da095c9_musicagent_exec_4.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_5_23f2d616",
    "agent_id": "AmbienceAgent",
    "step_id": "step_5_2da27249",
    "created_at": "2026-05-13T01:12:01.001843+00:00",
    "artifacts": [
      {
        "caption": "[BINARY WAV FILE · mime=audio/wav · sys_id aud_amb_film] Ambient room-tone audio bytes for the film-wide atmospheric underlay. Consumed by the audio-mix materializer via ffmpeg.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/media/AmbienceAgent/audio/step_5_2da27249_aud_amb_film.wav",
        "mime": "audio/wav"
      },
      {
        "caption": "[JSON MANIFEST] Ambience planning metadata: 1 bed(s) carrying the LLM-chosen description for the film-wide room-tone underlay. Read by the audio-mix LLM for mix planning.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/AmbienceAgent/step_5_2da27249_ambienceagent_exec_5.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_6_27a50a72",
    "agent_id": "AudioMixAgent",
    "step_id": "step_6_fa515b9d",
    "created_at": "2026-05-13T01:12:16.891720+00:00",
    "artifacts": [
      {
        "caption": "[BINARY WAV FILE · mime=audio/wav · sys_id aud_final] Final-mix audio bytes — all source audio tracks (dialogue / foley / music / ambience / narrator) merged. Ready to be muxed onto the delivered video by a downstream compositing step.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/media/AudioMixAgent/audio/step_6_fa515b9d_aud_final.wav",
        "mime": "audio/wav"
      },
      {
        "caption": "[JSON MANIFEST] Final-audio-mix envelope: amix of 3 source track(s) (video dialogue+foley + optional global music/ambience/narrator). Planning manifest only; the wav is a sibling artifact.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/AudioMixAgent/step_6_fa515b9d_audiomixagent_exec_6.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_7_f864bbe6",
    "agent_id": "CompositorAgent",
    "step_id": "step_7_04ed68a4",
    "created_at": "2026-05-13T01:12:39.057788+00:00",
    "artifacts": [
      {
        "caption": "Final delivered video binary (mp4) — the complete composited output with audio mix and (optional) subtitle burn-in. Terminal deliverable of the creative pipeline.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/media/CompositorAgent/video/step_7_04ed68a4_compositor_final.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "Final composited video (1920x1080): audio mix, subtitle burn-in. Ready for delivery.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/fox_demon_run_20260512_212622/workspace/workspace_global_20260512_223743/artifacts/CompositorAgent/step_7_04ed68a4_compositoragent_exec_7.json",
        "mime": "application/json"
      }
    ]
  }
]
```
