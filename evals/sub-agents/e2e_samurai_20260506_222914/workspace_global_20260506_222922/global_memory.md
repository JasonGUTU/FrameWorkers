# Global memory — `workspace_global_20260506_222922`

Per-execution record of every artifact persisted in this workspace. Each entry below is one agent execution; its `artifacts` array carries the natural-language `caption`, `scope`, absolute `path` and `mime` for every file that execution wrote.

`InputResolver` reads this index to match artifacts against each consumer agent's `[label]` slots. Execution history (including failures) lives in the assistant executions table, not here.

## Entries

```json
[
  {
    "execution_id": "upload_20260506_223011_925031",
    "agent_id": "user",
    "step_id": "",
    "created_at": "2026-05-06T22:30:11.927949+00:00",
    "artifacts": [
      {
        "caption": "Global character reference image. Visual identity anchor for downstream keyframe generation.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/e2e_samurai_20260506_222914/workspace_global_20260506_222922/inputs/20260506_223011_925031_samurai_reference.png",
        "mime": "image/png"
      }
    ]
  },
  {
    "execution_id": "brief_20260506_223011_981900",
    "agent_id": "user",
    "step_id": "",
    "created_at": "2026-05-06T22:30:11.983703+00:00",
    "artifacts": [
      {
        "caption": "Structured metadata document (JSON) for a user-submitted text brief. Payload carries the raw text verbatim. Pipeline entry point — consumed by story / screenplay / narration agents.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/e2e_samurai_20260506_222914/workspace_global_20260506_222922/inputs/brief_20260506_223011_981900.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_1_06d16bf4",
    "agent_id": "IntakeImageAgent",
    "step_id": "step_1_2fbb8c22",
    "created_at": "2026-05-06T22:30:29.708785+00:00",
    "artifacts": [
      {
        "caption": "Structured metadata document (JSON) for a user-uploaded image. Payload carries the visual description and image-asset metadata.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/e2e_samurai_20260506_222914/workspace_global_20260506_222922/artifacts/IntakeImageAgent/step_1_2fbb8c22_intakeimageagent_exec_1.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_2_253acc50",
    "agent_id": "BriefEnricherAgent",
    "step_id": "step_2_2b3ce8d9",
    "created_at": "2026-05-06T22:30:43.384999+00:00",
    "artifacts": [
      {
        "caption": "Enriched creative brief with visual reference descriptions integrated. Supersedes the raw user brief for story generation — contains the user's original concept plus detailed visual descriptions of uploaded reference images.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/e2e_samurai_20260506_222914/workspace_global_20260506_222922/artifacts/BriefEnricherAgent/step_2_2b3ce8d9_briefenricheragent_exec_2.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_3_c363ca21",
    "agent_id": "StoryAgent",
    "step_id": "step_3_9bf36bb6",
    "created_at": "2026-05-06T22:31:12.181610+00:00",
    "artifacts": [
      {
        "caption": "Story blueprint: 3 scene(s), 2 character(s). Structured input for screenplay generation.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/e2e_samurai_20260506_222914/workspace_global_20260506_222922/artifacts/StoryAgent/step_3_9bf36bb6_storyagent_exec_3.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_4_5a5eaf85",
    "agent_id": "ScreenplayAgent",
    "step_id": "step_4_aabe1dc0",
    "created_at": "2026-05-06T22:32:00.502547+00:00",
    "artifacts": [
      {
        "caption": "Screenplay: 3 scene(s), 10 shot(s). Input for keyframe planning and audio scoring.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/e2e_samurai_20260506_222914/workspace_global_20260506_222922/artifacts/ScreenplayAgent/step_4_aabe1dc0_screenplayagent_exec_4.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_5_99f05bf0",
    "agent_id": "KeyFrameAgent",
    "step_id": "step_5_a32bfb40",
    "created_at": "2026-05-06T22:35:28.593513+00:00",
    "artifacts": [
      {
        "caption": "Global character reference image for char_001. Visual identity anchor — not a video frame.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/e2e_samurai_20260506_222914/workspace_global_20260506_222922/artifacts/media/KeyFrameAgent/image/step_5_a32bfb40_img_char_001_global.png",
        "mime": "image/png"
      },
      {
        "caption": "Global location reference image for loc_001. Visual identity anchor — not a video frame.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/e2e_samurai_20260506_222914/workspace_global_20260506_222922/artifacts/media/KeyFrameAgent/image/step_5_a32bfb40_img_loc_001_global.png",
        "mime": "image/png"
      },
      {
        "caption": "Global prop reference image for prop_002. Visual identity anchor — not a video frame.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/e2e_samurai_20260506_222914/workspace_global_20260506_222922/artifacts/media/KeyFrameAgent/image/step_5_a32bfb40_img_prop_002_global.png",
        "mime": "image/png"
      },
      {
        "caption": "Global character reference image for char_002. Visual identity anchor — not a video frame.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/e2e_samurai_20260506_222914/workspace_global_20260506_222922/artifacts/media/KeyFrameAgent/image/step_5_a32bfb40_img_char_002_global.png",
        "mime": "image/png"
      },
      {
        "caption": "Global location reference image for loc_002. Visual identity anchor — not a video frame.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/e2e_samurai_20260506_222914/workspace_global_20260506_222922/artifacts/media/KeyFrameAgent/image/step_5_a32bfb40_img_loc_002_global.png",
        "mime": "image/png"
      },
      {
        "caption": "Global prop reference image for prop_001. Visual identity anchor — not a video frame.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/e2e_samurai_20260506_222914/workspace_global_20260506_222922/artifacts/media/KeyFrameAgent/image/step_5_a32bfb40_img_prop_001_global.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level character reference for char_001 in scene sc_001. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_001",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/e2e_samurai_20260506_222914/workspace_global_20260506_222922/artifacts/media/KeyFrameAgent/image/step_5_a32bfb40_img_char_001_sc_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level character reference for char_002 in scene sc_003. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_003",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/e2e_samurai_20260506_222914/workspace_global_20260506_222922/artifacts/media/KeyFrameAgent/image/step_5_a32bfb40_img_char_002_sc_003.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level location reference for loc_001 in scene sc_001. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_001",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/e2e_samurai_20260506_222914/workspace_global_20260506_222922/artifacts/media/KeyFrameAgent/image/step_5_a32bfb40_img_loc_001_sc_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level character reference for char_002 in scene sc_002. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_002",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/e2e_samurai_20260506_222914/workspace_global_20260506_222922/artifacts/media/KeyFrameAgent/image/step_5_a32bfb40_img_char_002_sc_002.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level location reference for loc_002 in scene sc_002. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_002",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/e2e_samurai_20260506_222914/workspace_global_20260506_222922/artifacts/media/KeyFrameAgent/image/step_5_a32bfb40_img_loc_002_sc_002.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level character reference for char_001 in scene sc_003. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_003",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/e2e_samurai_20260506_222914/workspace_global_20260506_222922/artifacts/media/KeyFrameAgent/image/step_5_a32bfb40_img_char_001_sc_003.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level prop reference for prop_001 in scene sc_003. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_003",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/e2e_samurai_20260506_222914/workspace_global_20260506_222922/artifacts/media/KeyFrameAgent/image/step_5_a32bfb40_img_prop_001_sc_003.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level prop reference for prop_002 in scene sc_002. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_002",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/e2e_samurai_20260506_222914/workspace_global_20260506_222922/artifacts/media/KeyFrameAgent/image/step_5_a32bfb40_img_prop_002_sc_002.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level prop reference for prop_002 in scene sc_003. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_003",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/e2e_samurai_20260506_222914/workspace_global_20260506_222922/artifacts/media/KeyFrameAgent/image/step_5_a32bfb40_img_prop_002_sc_003.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level prop reference for prop_001 in scene sc_001. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_001",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/e2e_samurai_20260506_222914/workspace_global_20260506_222922/artifacts/media/KeyFrameAgent/image/step_5_a32bfb40_img_prop_001_sc_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level character reference for char_001 in scene sc_002. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_002",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/e2e_samurai_20260506_222914/workspace_global_20260506_222922/artifacts/media/KeyFrameAgent/image/step_5_a32bfb40_img_char_001_sc_002.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level location reference for loc_002 in scene sc_003. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_003",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/e2e_samurai_20260506_222914/workspace_global_20260506_222922/artifacts/media/KeyFrameAgent/image/step_5_a32bfb40_img_loc_002_sc_003.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level prop reference for prop_001 in scene sc_002. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_002",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/e2e_samurai_20260506_222914/workspace_global_20260506_222922/artifacts/media/KeyFrameAgent/image/step_5_a32bfb40_img_prop_001_sc_002.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_009 in scene sc_003. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_009",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/e2e_samurai_20260506_222914/workspace_global_20260506_222922/artifacts/media/KeyFrameAgent/image/step_5_a32bfb40_img_sh_009_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_001 in scene sc_001. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_001",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/e2e_samurai_20260506_222914/workspace_global_20260506_222922/artifacts/media/KeyFrameAgent/image/step_5_a32bfb40_img_sh_001_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_007 in scene sc_002. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_007",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/e2e_samurai_20260506_222914/workspace_global_20260506_222922/artifacts/media/KeyFrameAgent/image/step_5_a32bfb40_img_sh_007_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_002 in scene sc_001. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_002",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/e2e_samurai_20260506_222914/workspace_global_20260506_222922/artifacts/media/KeyFrameAgent/image/step_5_a32bfb40_img_sh_002_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_003 in scene sc_001. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_003",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/e2e_samurai_20260506_222914/workspace_global_20260506_222922/artifacts/media/KeyFrameAgent/image/step_5_a32bfb40_img_sh_003_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_008 in scene sc_003. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_008",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/e2e_samurai_20260506_222914/workspace_global_20260506_222922/artifacts/media/KeyFrameAgent/image/step_5_a32bfb40_img_sh_008_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_004 in scene sc_002. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_004",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/e2e_samurai_20260506_222914/workspace_global_20260506_222922/artifacts/media/KeyFrameAgent/image/step_5_a32bfb40_img_sh_004_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_005 in scene sc_002. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_005",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/e2e_samurai_20260506_222914/workspace_global_20260506_222922/artifacts/media/KeyFrameAgent/image/step_5_a32bfb40_img_sh_005_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_006 in scene sc_002. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_006",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/e2e_samurai_20260506_222914/workspace_global_20260506_222922/artifacts/media/KeyFrameAgent/image/step_5_a32bfb40_img_sh_006_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_010 in scene sc_003. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_010",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/e2e_samurai_20260506_222914/workspace_global_20260506_222922/artifacts/media/KeyFrameAgent/image/step_5_a32bfb40_img_sh_010_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Keyframe planning document: 3 scene(s), 10 shot(s), with per-shot frame descriptions and motion hints. Consumed by a downstream image-to-video generation step.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/e2e_samurai_20260506_222914/workspace_global_20260506_222922/artifacts/KeyFrameAgent/step_5_a32bfb40_keyframeagent_exec_5.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_6_63e15908",
    "agent_id": "VideoAgent",
    "step_id": "step_6_ba98d70b",
    "created_at": "2026-05-06T22:49:24.797366+00:00",
    "artifacts": [
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_001] Video clip bytes for shot sh_001. One segment of the final video.",
        "scope": "shot:sh_001",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/e2e_samurai_20260506_222914/workspace_global_20260506_222922/artifacts/media/VideoAgent/video/step_6_ba98d70b_clip_sh_001.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_002] Video clip bytes for shot sh_002. One segment of the final video.",
        "scope": "shot:sh_002",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/e2e_samurai_20260506_222914/workspace_global_20260506_222922/artifacts/media/VideoAgent/video/step_6_ba98d70b_clip_sh_002.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_003] Video clip bytes for shot sh_003. One segment of the final video.",
        "scope": "shot:sh_003",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/e2e_samurai_20260506_222914/workspace_global_20260506_222922/artifacts/media/VideoAgent/video/step_6_ba98d70b_clip_sh_003.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sc_001] Scene-cut bytes for scene sc_001 — all shots concatenated. Intermediate assembly, not final.",
        "scope": "scene:sc_001",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/e2e_samurai_20260506_222914/workspace_global_20260506_222922/artifacts/media/VideoAgent/video/step_6_ba98d70b_clip_sc_001.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_004] Video clip bytes for shot sh_004. One segment of the final video.",
        "scope": "shot:sh_004",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/e2e_samurai_20260506_222914/workspace_global_20260506_222922/artifacts/media/VideoAgent/video/step_6_ba98d70b_clip_sh_004.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_005] Video clip bytes for shot sh_005. One segment of the final video.",
        "scope": "shot:sh_005",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/e2e_samurai_20260506_222914/workspace_global_20260506_222922/artifacts/media/VideoAgent/video/step_6_ba98d70b_clip_sh_005.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_006] Video clip bytes for shot sh_006. One segment of the final video.",
        "scope": "shot:sh_006",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/e2e_samurai_20260506_222914/workspace_global_20260506_222922/artifacts/media/VideoAgent/video/step_6_ba98d70b_clip_sh_006.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_007] Video clip bytes for shot sh_007. One segment of the final video.",
        "scope": "shot:sh_007",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/e2e_samurai_20260506_222914/workspace_global_20260506_222922/artifacts/media/VideoAgent/video/step_6_ba98d70b_clip_sh_007.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sc_002] Scene-cut bytes for scene sc_002 — all shots concatenated. Intermediate assembly, not final.",
        "scope": "scene:sc_002",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/e2e_samurai_20260506_222914/workspace_global_20260506_222922/artifacts/media/VideoAgent/video/step_6_ba98d70b_clip_sc_002.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_008] Video clip bytes for shot sh_008. One segment of the final video.",
        "scope": "shot:sh_008",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/e2e_samurai_20260506_222914/workspace_global_20260506_222922/artifacts/media/VideoAgent/video/step_6_ba98d70b_clip_sh_008.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_009] Video clip bytes for shot sh_009. One segment of the final video.",
        "scope": "shot:sh_009",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/e2e_samurai_20260506_222914/workspace_global_20260506_222922/artifacts/media/VideoAgent/video/step_6_ba98d70b_clip_sh_009.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_010] Video clip bytes for shot sh_010. One segment of the final video.",
        "scope": "shot:sh_010",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/e2e_samurai_20260506_222914/workspace_global_20260506_222922/artifacts/media/VideoAgent/video/step_6_ba98d70b_clip_sh_010.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sc_003] Scene-cut bytes for scene sc_003 — all shots concatenated. Intermediate assembly, not final.",
        "scope": "scene:sc_003",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/e2e_samurai_20260506_222914/workspace_global_20260506_222922/artifacts/media/VideoAgent/video/step_6_ba98d70b_clip_sc_003.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_final] Complete assembled video bytes (10 shots). Final visual deliverable — consumed by a downstream audio-mix step's materializer via ffmpeg for audio extraction + muxing.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/e2e_samurai_20260506_222914/workspace_global_20260506_222922/artifacts/media/VideoAgent/video/step_6_ba98d70b_clip_final.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[JSON MANIFEST] Video-assembly planning metadata: 3 scene(s), 10 shot clip(s) with timing. Read by a downstream audio-mix step's LLM for mix planning.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/e2e_samurai_20260506_222914/workspace_global_20260506_222922/artifacts/VideoAgent/step_6_ba98d70b_videoagent_exec_6.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_7_0d64f4a8",
    "agent_id": "TranscriptionAgent",
    "step_id": "step_7_a9aa59ba",
    "created_at": "2026-05-06T22:49:55.157270+00:00",
    "artifacts": [
      {
        "caption": "Transcript (en): 4 segment(s) with timestamps. Speech-to-text from source media. Usable as the 'timed source text' input to a downstream subtitle step, or as the 'source text' input to a downstream translation step.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/e2e_samurai_20260506_222914/workspace_global_20260506_222922/artifacts/TranscriptionAgent/step_7_a9aa59ba_transcriptionagent_exec_7.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_8_28576887",
    "agent_id": "AmbienceAgent",
    "step_id": "step_8_27801609",
    "created_at": "2026-05-06T22:51:54.576548+00:00",
    "artifacts": [
      {
        "caption": "[BINARY WAV FILE · mime=audio/wav · sys_id aud_amb_film] Ambient room-tone audio bytes for the film-wide atmospheric underlay. Consumed by the audio-mix materializer via ffmpeg.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/e2e_samurai_20260506_222914/workspace_global_20260506_222922/artifacts/media/AmbienceAgent/audio/step_8_27801609_aud_amb_film.wav",
        "mime": "audio/wav"
      },
      {
        "caption": "[JSON MANIFEST] Ambience planning metadata: 1 bed(s) carrying the LLM-chosen description for the film-wide room-tone underlay. Read by the audio-mix LLM for mix planning.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/e2e_samurai_20260506_222914/workspace_global_20260506_222922/artifacts/AmbienceAgent/step_8_27801609_ambienceagent_exec_8.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_9_76d652d7",
    "agent_id": "AudioMixAgent",
    "step_id": "step_9_854bd899",
    "created_at": "2026-05-06T22:52:06.421507+00:00",
    "artifacts": [
      {
        "caption": "[BINARY WAV FILE · mime=audio/wav · sys_id aud_final] Final-mix audio bytes — all source audio tracks (dialogue / foley / music / ambience / narrator) merged. Ready to be muxed onto the delivered video by a downstream compositing step.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/e2e_samurai_20260506_222914/workspace_global_20260506_222922/artifacts/media/AudioMixAgent/audio/step_9_854bd899_aud_final.wav",
        "mime": "audio/wav"
      },
      {
        "caption": "[JSON MANIFEST] Final-audio-mix envelope: amix of 3 source track(s) (video dialogue+foley + optional global music/ambience/narrator). Planning manifest only; the wav is a sibling artifact.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/e2e_samurai_20260506_222914/workspace_global_20260506_222922/artifacts/AudioMixAgent/step_9_854bd899_audiomixagent_exec_9.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_10_b1fc7cd7",
    "agent_id": "CompositorAgent",
    "step_id": "step_10_6cb1d3ae",
    "created_at": "2026-05-06T22:52:27.447445+00:00",
    "artifacts": [
      {
        "caption": "Final delivered video binary (mp4) — the complete composited output with audio mix and (optional) subtitle burn-in. Terminal deliverable of the creative pipeline.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/e2e_samurai_20260506_222914/workspace_global_20260506_222922/artifacts/media/CompositorAgent/video/step_10_6cb1d3ae_compositor_final.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "Final composited video (1920x1080): audio mix, subtitle burn-in. Ready for delivery.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/e2e_samurai_20260506_222914/workspace_global_20260506_222922/artifacts/CompositorAgent/step_10_6cb1d3ae_compositoragent_exec_10.json",
        "mime": "application/json"
      }
    ]
  }
]
```
