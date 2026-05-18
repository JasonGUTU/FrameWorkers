# Global memory — `workspace_global_20260510_212627`

Per-execution record of every artifact persisted in this workspace. Each entry below is one agent execution; its `artifacts` array carries the natural-language `caption`, `scope`, absolute `path` and `mime` for every file that execution wrote.

`InputResolver` reads this index to match artifacts against each consumer agent's `[label]` slots. Execution history (including failures) lives in the assistant executions table, not here.

## Entries

```json
[
  {
    "execution_id": "upload_20260510_212628_545475",
    "agent_id": "user",
    "step_id": "",
    "created_at": "2026-05-10T21:26:28.548132+00:00",
    "artifacts": [
      {
        "caption": "Global character reference image. Visual identity anchor for downstream keyframe generation.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_019/_workspace/workspace_global_20260510_212627/inputs/20260510_212628_545475_intake_img_019.png",
        "mime": "image/png"
      }
    ]
  },
  {
    "execution_id": "brief_20260510_212628_561185",
    "agent_id": "user",
    "step_id": "",
    "created_at": "2026-05-10T21:26:28.563305+00:00",
    "artifacts": [
      {
        "caption": "Structured metadata document (JSON) for a user-submitted text brief. Payload carries the raw text verbatim. Pipeline entry point — consumed by story / screenplay / narration agents.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_019/_workspace/workspace_global_20260510_212627/inputs/brief_20260510_212628_561185.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_1_7feaba69",
    "agent_id": "IntakeImageAgent",
    "step_id": "step_1_48b2cd24",
    "created_at": "2026-05-10T21:26:36.726795+00:00",
    "artifacts": [
      {
        "caption": "Structured metadata document (JSON) for a user-uploaded image. Payload carries the visual description and image-asset metadata.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_019/_workspace/workspace_global_20260510_212627/artifacts/IntakeImageAgent/step_1_48b2cd24_intakeimageagent_exec_1.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_2_4059029f",
    "agent_id": "BriefEnricherAgent",
    "step_id": "step_2_fc7ba7ca",
    "created_at": "2026-05-10T21:26:49.677801+00:00",
    "artifacts": [
      {
        "caption": "Enriched creative brief with visual reference descriptions integrated. Supersedes the raw user brief for story generation — contains the user's original concept plus detailed visual descriptions of uploaded reference images.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_019/_workspace/workspace_global_20260510_212627/artifacts/BriefEnricherAgent/step_2_fc7ba7ca_briefenricheragent_exec_2.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_3_4b27fa1f",
    "agent_id": "StoryAgent",
    "step_id": "step_3_ea4873b3",
    "created_at": "2026-05-10T21:27:23.521481+00:00",
    "artifacts": [
      {
        "caption": "Story blueprint: 3 scene(s), 2 character(s). Structured input for screenplay generation.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_019/_workspace/workspace_global_20260510_212627/artifacts/StoryAgent/step_3_ea4873b3_storyagent_exec_3.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_4_809b868b",
    "agent_id": "ScreenplayAgent",
    "step_id": "step_4_bbcf4bc9",
    "created_at": "2026-05-10T21:28:18.843938+00:00",
    "artifacts": [
      {
        "caption": "Screenplay: 3 scene(s), 12 shot(s). Input for keyframe planning and audio scoring.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_019/_workspace/workspace_global_20260510_212627/artifacts/ScreenplayAgent/step_4_bbcf4bc9_screenplayagent_exec_4.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_5_6a4df797",
    "agent_id": "KeyFrameAgent",
    "step_id": "step_5_c466acc3",
    "created_at": "2026-05-10T21:30:57.629110+00:00",
    "artifacts": [
      {
        "caption": "Global character reference image for char_001. Visual identity anchor — not a video frame.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_019/_workspace/workspace_global_20260510_212627/artifacts/media/KeyFrameAgent/image/step_5_c466acc3_img_char_001_global.png",
        "mime": "image/png"
      },
      {
        "caption": "Global character reference image for char_002. Visual identity anchor — not a video frame.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_019/_workspace/workspace_global_20260510_212627/artifacts/media/KeyFrameAgent/image/step_5_c466acc3_img_char_002_global.png",
        "mime": "image/png"
      },
      {
        "caption": "Global location reference image for loc_001. Visual identity anchor — not a video frame.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_019/_workspace/workspace_global_20260510_212627/artifacts/media/KeyFrameAgent/image/step_5_c466acc3_img_loc_001_global.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level character reference for char_001 in scene sc_001. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_001",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_019/_workspace/workspace_global_20260510_212627/artifacts/media/KeyFrameAgent/image/step_5_c466acc3_img_char_001_sc_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level location reference for loc_001 in scene sc_001. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_001",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_019/_workspace/workspace_global_20260510_212627/artifacts/media/KeyFrameAgent/image/step_5_c466acc3_img_loc_001_sc_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level character reference for char_002 in scene sc_003. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_003",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_019/_workspace/workspace_global_20260510_212627/artifacts/media/KeyFrameAgent/image/step_5_c466acc3_img_char_002_sc_003.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level location reference for loc_001 in scene sc_003. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_003",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_019/_workspace/workspace_global_20260510_212627/artifacts/media/KeyFrameAgent/image/step_5_c466acc3_img_loc_001_sc_003.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level character reference for char_002 in scene sc_002. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_002",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_019/_workspace/workspace_global_20260510_212627/artifacts/media/KeyFrameAgent/image/step_5_c466acc3_img_char_002_sc_002.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level location reference for loc_001 in scene sc_002. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_002",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_019/_workspace/workspace_global_20260510_212627/artifacts/media/KeyFrameAgent/image/step_5_c466acc3_img_loc_001_sc_002.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level character reference for char_001 in scene sc_003. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_003",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_019/_workspace/workspace_global_20260510_212627/artifacts/media/KeyFrameAgent/image/step_5_c466acc3_img_char_001_sc_003.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level character reference for char_001 in scene sc_002. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_002",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_019/_workspace/workspace_global_20260510_212627/artifacts/media/KeyFrameAgent/image/step_5_c466acc3_img_char_001_sc_002.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_001 in scene sc_001. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_001",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_019/_workspace/workspace_global_20260510_212627/artifacts/media/KeyFrameAgent/image/step_5_c466acc3_img_sh_001_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_011 in scene sc_003. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_011",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_019/_workspace/workspace_global_20260510_212627/artifacts/media/KeyFrameAgent/image/step_5_c466acc3_img_sh_011_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_007 in scene sc_002. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_007",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_019/_workspace/workspace_global_20260510_212627/artifacts/media/KeyFrameAgent/image/step_5_c466acc3_img_sh_007_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_005 in scene sc_002. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_005",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_019/_workspace/workspace_global_20260510_212627/artifacts/media/KeyFrameAgent/image/step_5_c466acc3_img_sh_005_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_010 in scene sc_003. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_010",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_019/_workspace/workspace_global_20260510_212627/artifacts/media/KeyFrameAgent/image/step_5_c466acc3_img_sh_010_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_006 in scene sc_002. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_006",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_019/_workspace/workspace_global_20260510_212627/artifacts/media/KeyFrameAgent/image/step_5_c466acc3_img_sh_006_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_009 in scene sc_003. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_009",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_019/_workspace/workspace_global_20260510_212627/artifacts/media/KeyFrameAgent/image/step_5_c466acc3_img_sh_009_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_008 in scene sc_002. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_008",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_019/_workspace/workspace_global_20260510_212627/artifacts/media/KeyFrameAgent/image/step_5_c466acc3_img_sh_008_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_004 in scene sc_001. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_004",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_019/_workspace/workspace_global_20260510_212627/artifacts/media/KeyFrameAgent/image/step_5_c466acc3_img_sh_004_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_003 in scene sc_001. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_003",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_019/_workspace/workspace_global_20260510_212627/artifacts/media/KeyFrameAgent/image/step_5_c466acc3_img_sh_003_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_002 in scene sc_001. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_002",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_019/_workspace/workspace_global_20260510_212627/artifacts/media/KeyFrameAgent/image/step_5_c466acc3_img_sh_002_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_012 in scene sc_003. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_012",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_019/_workspace/workspace_global_20260510_212627/artifacts/media/KeyFrameAgent/image/step_5_c466acc3_img_sh_012_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Keyframe planning document: 3 scene(s), 12 shot(s), with per-shot frame descriptions and motion hints. Consumed by a downstream image-to-video generation step.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_019/_workspace/workspace_global_20260510_212627/artifacts/KeyFrameAgent/step_5_c466acc3_keyframeagent_exec_5.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_6_b3ffd379",
    "agent_id": "VideoAgent",
    "step_id": "step_6_ae3508fc",
    "created_at": "2026-05-11T02:06:40.413306+00:00",
    "artifacts": [
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_001] Video clip bytes for shot sh_001. One segment of the final video.",
        "scope": "shot:sh_001",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_019/_workspace/workspace_global_20260510_212627/artifacts/media/VideoAgent/video/step_6_ae3508fc_clip_sh_001.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_002] Video clip bytes for shot sh_002. One segment of the final video.",
        "scope": "shot:sh_002",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_019/_workspace/workspace_global_20260510_212627/artifacts/media/VideoAgent/video/step_6_ae3508fc_clip_sh_002.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_003] Video clip bytes for shot sh_003. One segment of the final video.",
        "scope": "shot:sh_003",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_019/_workspace/workspace_global_20260510_212627/artifacts/media/VideoAgent/video/step_6_ae3508fc_clip_sh_003.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_004] Video clip bytes for shot sh_004. One segment of the final video.",
        "scope": "shot:sh_004",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_019/_workspace/workspace_global_20260510_212627/artifacts/media/VideoAgent/video/step_6_ae3508fc_clip_sh_004.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_005] Video clip bytes for shot sh_005. One segment of the final video.",
        "scope": "shot:sh_005",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_019/_workspace/workspace_global_20260510_212627/artifacts/media/VideoAgent/video/step_6_ae3508fc_clip_sh_005.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_006] Video clip bytes for shot sh_006. One segment of the final video.",
        "scope": "shot:sh_006",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_019/_workspace/workspace_global_20260510_212627/artifacts/media/VideoAgent/video/step_6_ae3508fc_clip_sh_006.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_007] Video clip bytes for shot sh_007. One segment of the final video.",
        "scope": "shot:sh_007",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_019/_workspace/workspace_global_20260510_212627/artifacts/media/VideoAgent/video/step_6_ae3508fc_clip_sh_007.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_008] Video clip bytes for shot sh_008. One segment of the final video.",
        "scope": "shot:sh_008",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_019/_workspace/workspace_global_20260510_212627/artifacts/media/VideoAgent/video/step_6_ae3508fc_clip_sh_008.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_009] Video clip bytes for shot sh_009. One segment of the final video.",
        "scope": "shot:sh_009",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_019/_workspace/workspace_global_20260510_212627/artifacts/media/VideoAgent/video/step_6_ae3508fc_clip_sh_009.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_010] Video clip bytes for shot sh_010. One segment of the final video.",
        "scope": "shot:sh_010",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_019/_workspace/workspace_global_20260510_212627/artifacts/media/VideoAgent/video/step_6_ae3508fc_clip_sh_010.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_011] Video clip bytes for shot sh_011. One segment of the final video.",
        "scope": "shot:sh_011",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_019/_workspace/workspace_global_20260510_212627/artifacts/media/VideoAgent/video/step_6_ae3508fc_clip_sh_011.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_012] Video clip bytes for shot sh_012. One segment of the final video.",
        "scope": "shot:sh_012",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_019/_workspace/workspace_global_20260510_212627/artifacts/media/VideoAgent/video/step_6_ae3508fc_clip_sh_012.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sc_001] Scene-cut bytes for scene sc_001 — all shots concatenated. Intermediate assembly, not final.",
        "scope": "scene:sc_001",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_019/_workspace/workspace_global_20260510_212627/artifacts/media/VideoAgent/video/step_6_ae3508fc_clip_sc_001.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sc_002] Scene-cut bytes for scene sc_002 — all shots concatenated. Intermediate assembly, not final.",
        "scope": "scene:sc_002",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_019/_workspace/workspace_global_20260510_212627/artifacts/media/VideoAgent/video/step_6_ae3508fc_clip_sc_002.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sc_003] Scene-cut bytes for scene sc_003 — all shots concatenated. Intermediate assembly, not final.",
        "scope": "scene:sc_003",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_019/_workspace/workspace_global_20260510_212627/artifacts/media/VideoAgent/video/step_6_ae3508fc_clip_sc_003.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_final] Complete assembled video bytes (12 shots). Final visual deliverable — consumed by a downstream audio-mix step's materializer via ffmpeg for audio extraction + muxing.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_019/_workspace/workspace_global_20260510_212627/artifacts/media/VideoAgent/video/step_6_ae3508fc_clip_final.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[JSON MANIFEST] Video-assembly planning metadata: 3 scene(s), 12 shot clip(s) with timing. Read by a downstream audio-mix step's LLM for mix planning.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_019/_workspace/workspace_global_20260510_212627/artifacts/VideoAgent/step_6_ae3508fc_videoagent_exec_6.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_7_1c269673",
    "agent_id": "CompositorAgent",
    "step_id": "step_7_e9827a77",
    "created_at": "2026-05-11T02:06:56.440157+00:00",
    "artifacts": [
      {
        "caption": "Final delivered video binary (mp4) — the complete composited output with audio mix and (optional) subtitle burn-in. Terminal deliverable of the creative pipeline.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_019/_workspace/workspace_global_20260510_212627/artifacts/media/CompositorAgent/video/step_7_e9827a77_compositor_final.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "Final composited video (1920x1080): audio mix, subtitle burn-in. Ready for delivery.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_019/_workspace/workspace_global_20260510_212627/artifacts/CompositorAgent/step_7_e9827a77_compositoragent_exec_7.json",
        "mime": "application/json"
      }
    ]
  }
]
```
