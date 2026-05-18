# Global memory — `workspace_global_20260510_033630`

Per-execution record of every artifact persisted in this workspace. Each entry below is one agent execution; its `artifacts` array carries the natural-language `caption`, `scope`, absolute `path` and `mime` for every file that execution wrote.

`InputResolver` reads this index to match artifacts against each consumer agent's `[label]` slots. Execution history (including failures) lives in the assistant executions table, not here.

## Entries

```json
[
  {
    "execution_id": "upload_20260510_033631_479835",
    "agent_id": "user",
    "step_id": "",
    "created_at": "2026-05-10T03:36:31.482429+00:00",
    "artifacts": [
      {
        "caption": "Global character reference image. Visual identity anchor for downstream keyframe generation.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_008/_workspace/workspace_global_20260510_033630/inputs/20260510_033631_479835_intake_img_008.png",
        "mime": "image/png"
      }
    ]
  },
  {
    "execution_id": "brief_20260510_033631_491230",
    "agent_id": "user",
    "step_id": "",
    "created_at": "2026-05-10T03:36:31.492428+00:00",
    "artifacts": [
      {
        "caption": "Structured metadata document (JSON) for a user-submitted text brief. Payload carries the raw text verbatim. Pipeline entry point — consumed by story / screenplay / narration agents.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_008/_workspace/workspace_global_20260510_033630/inputs/brief_20260510_033631_491230.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_1_0ea9261f",
    "agent_id": "IntakeImageAgent",
    "step_id": "step_1_68cb82f6",
    "created_at": "2026-05-10T03:36:40.046790+00:00",
    "artifacts": [
      {
        "caption": "Structured metadata document (JSON) for a user-uploaded image. Payload carries the visual description and image-asset metadata.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_008/_workspace/workspace_global_20260510_033630/artifacts/IntakeImageAgent/step_1_68cb82f6_intakeimageagent_exec_1.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_2_4ec8b8f3",
    "agent_id": "BriefEnricherAgent",
    "step_id": "step_2_d3110367",
    "created_at": "2026-05-10T03:36:51.740066+00:00",
    "artifacts": [
      {
        "caption": "Enriched creative brief with visual reference descriptions integrated. Supersedes the raw user brief for story generation — contains the user's original concept plus detailed visual descriptions of uploaded reference images.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_008/_workspace/workspace_global_20260510_033630/artifacts/BriefEnricherAgent/step_2_d3110367_briefenricheragent_exec_2.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_3_370dfc17",
    "agent_id": "StoryAgent",
    "step_id": "step_3_653539c8",
    "created_at": "2026-05-10T03:37:26.006835+00:00",
    "artifacts": [
      {
        "caption": "Story blueprint: 3 scene(s), 2 character(s). Structured input for screenplay generation.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_008/_workspace/workspace_global_20260510_033630/artifacts/StoryAgent/step_3_653539c8_storyagent_exec_3.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_4_bcd6fe9d",
    "agent_id": "ScreenplayAgent",
    "step_id": "step_4_1b8ceb99",
    "created_at": "2026-05-10T03:38:13.601936+00:00",
    "artifacts": [
      {
        "caption": "Screenplay: 3 scene(s), 11 shot(s). Input for keyframe planning and audio scoring.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_008/_workspace/workspace_global_20260510_033630/artifacts/ScreenplayAgent/step_4_1b8ceb99_screenplayagent_exec_4.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_5_ba3f759e",
    "agent_id": "KeyFrameAgent",
    "step_id": "step_5_937dc156",
    "created_at": "2026-05-10T03:40:41.933483+00:00",
    "artifacts": [
      {
        "caption": "Global character reference image for char_001. Visual identity anchor — not a video frame.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_008/_workspace/workspace_global_20260510_033630/artifacts/media/KeyFrameAgent/image/step_5_937dc156_img_char_001_global.png",
        "mime": "image/png"
      },
      {
        "caption": "Global character reference image for char_002. Visual identity anchor — not a video frame.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_008/_workspace/workspace_global_20260510_033630/artifacts/media/KeyFrameAgent/image/step_5_937dc156_img_char_002_global.png",
        "mime": "image/png"
      },
      {
        "caption": "Global prop reference image for prop_001. Visual identity anchor — not a video frame.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_008/_workspace/workspace_global_20260510_033630/artifacts/media/KeyFrameAgent/image/step_5_937dc156_img_prop_001_global.png",
        "mime": "image/png"
      },
      {
        "caption": "Global location reference image for loc_002. Visual identity anchor — not a video frame.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_008/_workspace/workspace_global_20260510_033630/artifacts/media/KeyFrameAgent/image/step_5_937dc156_img_loc_002_global.png",
        "mime": "image/png"
      },
      {
        "caption": "Global location reference image for loc_001. Visual identity anchor — not a video frame.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_008/_workspace/workspace_global_20260510_033630/artifacts/media/KeyFrameAgent/image/step_5_937dc156_img_loc_001_global.png",
        "mime": "image/png"
      },
      {
        "caption": "Global location reference image for loc_003. Visual identity anchor — not a video frame.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_008/_workspace/workspace_global_20260510_033630/artifacts/media/KeyFrameAgent/image/step_5_937dc156_img_loc_003_global.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level character reference for char_001 in scene sc_003. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_003",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_008/_workspace/workspace_global_20260510_033630/artifacts/media/KeyFrameAgent/image/step_5_937dc156_img_char_001_sc_003.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level character reference for char_001 in scene sc_002. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_002",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_008/_workspace/workspace_global_20260510_033630/artifacts/media/KeyFrameAgent/image/step_5_937dc156_img_char_001_sc_002.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level character reference for char_002 in scene sc_003. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_003",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_008/_workspace/workspace_global_20260510_033630/artifacts/media/KeyFrameAgent/image/step_5_937dc156_img_char_002_sc_003.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level character reference for char_001 in scene sc_001. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_001",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_008/_workspace/workspace_global_20260510_033630/artifacts/media/KeyFrameAgent/image/step_5_937dc156_img_char_001_sc_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level location reference for loc_003 in scene sc_003. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_003",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_008/_workspace/workspace_global_20260510_033630/artifacts/media/KeyFrameAgent/image/step_5_937dc156_img_loc_003_sc_003.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level location reference for loc_001 in scene sc_002. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_002",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_008/_workspace/workspace_global_20260510_033630/artifacts/media/KeyFrameAgent/image/step_5_937dc156_img_loc_001_sc_002.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level prop reference for prop_001 in scene sc_003. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_003",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_008/_workspace/workspace_global_20260510_033630/artifacts/media/KeyFrameAgent/image/step_5_937dc156_img_prop_001_sc_003.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level location reference for loc_002 in scene sc_001. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_001",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_008/_workspace/workspace_global_20260510_033630/artifacts/media/KeyFrameAgent/image/step_5_937dc156_img_loc_002_sc_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_007 in scene sc_002. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_007",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_008/_workspace/workspace_global_20260510_033630/artifacts/media/KeyFrameAgent/image/step_5_937dc156_img_sh_007_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_008 in scene sc_003. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_008",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_008/_workspace/workspace_global_20260510_033630/artifacts/media/KeyFrameAgent/image/step_5_937dc156_img_sh_008_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_006 in scene sc_002. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_006",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_008/_workspace/workspace_global_20260510_033630/artifacts/media/KeyFrameAgent/image/step_5_937dc156_img_sh_006_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_002 in scene sc_001. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_002",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_008/_workspace/workspace_global_20260510_033630/artifacts/media/KeyFrameAgent/image/step_5_937dc156_img_sh_002_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_004 in scene sc_001. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_004",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_008/_workspace/workspace_global_20260510_033630/artifacts/media/KeyFrameAgent/image/step_5_937dc156_img_sh_004_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_010 in scene sc_003. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_010",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_008/_workspace/workspace_global_20260510_033630/artifacts/media/KeyFrameAgent/image/step_5_937dc156_img_sh_010_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_003 in scene sc_001. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_003",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_008/_workspace/workspace_global_20260510_033630/artifacts/media/KeyFrameAgent/image/step_5_937dc156_img_sh_003_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_005 in scene sc_002. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_005",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_008/_workspace/workspace_global_20260510_033630/artifacts/media/KeyFrameAgent/image/step_5_937dc156_img_sh_005_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_011 in scene sc_003. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_011",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_008/_workspace/workspace_global_20260510_033630/artifacts/media/KeyFrameAgent/image/step_5_937dc156_img_sh_011_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_001 in scene sc_001. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_001",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_008/_workspace/workspace_global_20260510_033630/artifacts/media/KeyFrameAgent/image/step_5_937dc156_img_sh_001_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_009 in scene sc_003. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_009",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_008/_workspace/workspace_global_20260510_033630/artifacts/media/KeyFrameAgent/image/step_5_937dc156_img_sh_009_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Keyframe planning document: 3 scene(s), 11 shot(s), with per-shot frame descriptions and motion hints. Consumed by a downstream image-to-video generation step.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_008/_workspace/workspace_global_20260510_033630/artifacts/KeyFrameAgent/step_5_937dc156_keyframeagent_exec_5.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_6_ed07d8e4",
    "agent_id": "VideoAgent",
    "step_id": "step_6_2e0a817b",
    "created_at": "2026-05-10T07:52:52.933467+00:00",
    "artifacts": [
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_001] Video clip bytes for shot sh_001. One segment of the final video.",
        "scope": "shot:sh_001",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_008/_workspace/workspace_global_20260510_033630/artifacts/media/VideoAgent/video/step_6_2e0a817b_clip_sh_001.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_002] Video clip bytes for shot sh_002. One segment of the final video.",
        "scope": "shot:sh_002",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_008/_workspace/workspace_global_20260510_033630/artifacts/media/VideoAgent/video/step_6_2e0a817b_clip_sh_002.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_003] Video clip bytes for shot sh_003. One segment of the final video.",
        "scope": "shot:sh_003",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_008/_workspace/workspace_global_20260510_033630/artifacts/media/VideoAgent/video/step_6_2e0a817b_clip_sh_003.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_004] Video clip bytes for shot sh_004. One segment of the final video.",
        "scope": "shot:sh_004",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_008/_workspace/workspace_global_20260510_033630/artifacts/media/VideoAgent/video/step_6_2e0a817b_clip_sh_004.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_005] Video clip bytes for shot sh_005. One segment of the final video.",
        "scope": "shot:sh_005",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_008/_workspace/workspace_global_20260510_033630/artifacts/media/VideoAgent/video/step_6_2e0a817b_clip_sh_005.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_006] Video clip bytes for shot sh_006. One segment of the final video.",
        "scope": "shot:sh_006",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_008/_workspace/workspace_global_20260510_033630/artifacts/media/VideoAgent/video/step_6_2e0a817b_clip_sh_006.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_007] Video clip bytes for shot sh_007. One segment of the final video.",
        "scope": "shot:sh_007",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_008/_workspace/workspace_global_20260510_033630/artifacts/media/VideoAgent/video/step_6_2e0a817b_clip_sh_007.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_008] Video clip bytes for shot sh_008. One segment of the final video.",
        "scope": "shot:sh_008",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_008/_workspace/workspace_global_20260510_033630/artifacts/media/VideoAgent/video/step_6_2e0a817b_clip_sh_008.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_009] Video clip bytes for shot sh_009. One segment of the final video.",
        "scope": "shot:sh_009",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_008/_workspace/workspace_global_20260510_033630/artifacts/media/VideoAgent/video/step_6_2e0a817b_clip_sh_009.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_010] Video clip bytes for shot sh_010. One segment of the final video.",
        "scope": "shot:sh_010",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_008/_workspace/workspace_global_20260510_033630/artifacts/media/VideoAgent/video/step_6_2e0a817b_clip_sh_010.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_011] Video clip bytes for shot sh_011. One segment of the final video.",
        "scope": "shot:sh_011",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_008/_workspace/workspace_global_20260510_033630/artifacts/media/VideoAgent/video/step_6_2e0a817b_clip_sh_011.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sc_001] Scene-cut bytes for scene sc_001 — all shots concatenated. Intermediate assembly, not final.",
        "scope": "scene:sc_001",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_008/_workspace/workspace_global_20260510_033630/artifacts/media/VideoAgent/video/step_6_2e0a817b_clip_sc_001.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sc_002] Scene-cut bytes for scene sc_002 — all shots concatenated. Intermediate assembly, not final.",
        "scope": "scene:sc_002",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_008/_workspace/workspace_global_20260510_033630/artifacts/media/VideoAgent/video/step_6_2e0a817b_clip_sc_002.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sc_003] Scene-cut bytes for scene sc_003 — all shots concatenated. Intermediate assembly, not final.",
        "scope": "scene:sc_003",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_008/_workspace/workspace_global_20260510_033630/artifacts/media/VideoAgent/video/step_6_2e0a817b_clip_sc_003.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_final] Complete assembled video bytes (11 shots). Final visual deliverable — consumed by a downstream audio-mix step's materializer via ffmpeg for audio extraction + muxing.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_008/_workspace/workspace_global_20260510_033630/artifacts/media/VideoAgent/video/step_6_2e0a817b_clip_final.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[JSON MANIFEST] Video-assembly planning metadata: 3 scene(s), 11 shot clip(s) with timing. Read by a downstream audio-mix step's LLM for mix planning.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_008/_workspace/workspace_global_20260510_033630/artifacts/VideoAgent/step_6_2e0a817b_videoagent_exec_6.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_7_d591767b",
    "agent_id": "CompositorAgent",
    "step_id": "step_7_081af2e3",
    "created_at": "2026-05-10T07:53:10.669440+00:00",
    "artifacts": [
      {
        "caption": "Final delivered video binary (mp4) — the complete composited output with audio mix and (optional) subtitle burn-in. Terminal deliverable of the creative pipeline.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_008/_workspace/workspace_global_20260510_033630/artifacts/media/CompositorAgent/video/step_7_081af2e3_compositor_final.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "Final composited video (1920x1080): audio mix, subtitle burn-in. Ready for delivery.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_008/_workspace/workspace_global_20260510_033630/artifacts/CompositorAgent/step_7_081af2e3_compositoragent_exec_7.json",
        "mime": "application/json"
      }
    ]
  }
]
```
