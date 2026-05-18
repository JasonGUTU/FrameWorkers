# Global memory — `workspace_global_20260509_212514`

Per-execution record of every artifact persisted in this workspace. Each entry below is one agent execution; its `artifacts` array carries the natural-language `caption`, `scope`, absolute `path` and `mime` for every file that execution wrote.

`InputResolver` reads this index to match artifacts against each consumer agent's `[label]` slots. Execution history (including failures) lives in the assistant executions table, not here.

## Entries

```json
[
  {
    "execution_id": "brief_20260509_212516_332700",
    "agent_id": "user",
    "step_id": "",
    "created_at": "2026-05-09T21:25:16.335965+00:00",
    "artifacts": [
      {
        "caption": "Structured metadata document (JSON) for a user-submitted text brief. Payload carries the raw text verbatim. Pipeline entry point — consumed by story / screenplay / narration agents.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_049/_workspace/workspace_global_20260509_212514/inputs/brief_20260509_212516_332700.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_1_6dbc8a7e",
    "agent_id": "StoryAgent",
    "step_id": "step_1_3ef2d36e",
    "created_at": "2026-05-09T21:25:43.275686+00:00",
    "artifacts": [
      {
        "caption": "Story blueprint: 2 scene(s), 2 character(s). Structured input for screenplay generation.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_049/_workspace/workspace_global_20260509_212514/artifacts/StoryAgent/step_1_3ef2d36e_storyagent_exec_1.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_2_9c1891de",
    "agent_id": "ScreenplayAgent",
    "step_id": "step_2_85a9a7da",
    "created_at": "2026-05-09T21:26:30.756739+00:00",
    "artifacts": [
      {
        "caption": "Screenplay: 2 scene(s), 10 shot(s). Input for keyframe planning and audio scoring.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_049/_workspace/workspace_global_20260509_212514/artifacts/ScreenplayAgent/step_2_85a9a7da_screenplayagent_exec_2.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_3_0cc33b12",
    "agent_id": "KeyFrameAgent",
    "step_id": "step_3_f9772ea6",
    "created_at": "2026-05-09T21:30:06.855763+00:00",
    "artifacts": [
      {
        "caption": "Global location reference image for loc_002. Visual identity anchor — not a video frame.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_049/_workspace/workspace_global_20260509_212514/artifacts/media/KeyFrameAgent/image/step_3_f9772ea6_img_loc_002_global.png",
        "mime": "image/png"
      },
      {
        "caption": "Global prop reference image for prop_001. Visual identity anchor — not a video frame.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_049/_workspace/workspace_global_20260509_212514/artifacts/media/KeyFrameAgent/image/step_3_f9772ea6_img_prop_001_global.png",
        "mime": "image/png"
      },
      {
        "caption": "Global location reference image for loc_003. Visual identity anchor — not a video frame.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_049/_workspace/workspace_global_20260509_212514/artifacts/media/KeyFrameAgent/image/step_3_f9772ea6_img_loc_003_global.png",
        "mime": "image/png"
      },
      {
        "caption": "Global character reference image for char_001. Visual identity anchor — not a video frame.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_049/_workspace/workspace_global_20260509_212514/artifacts/media/KeyFrameAgent/image/step_3_f9772ea6_img_char_001_global.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level character reference for char_001 in scene sc_002. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_002",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_049/_workspace/workspace_global_20260509_212514/artifacts/media/KeyFrameAgent/image/step_3_f9772ea6_img_char_001_sc_002.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level prop reference for prop_001 in scene sc_001. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_001",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_049/_workspace/workspace_global_20260509_212514/artifacts/media/KeyFrameAgent/image/step_3_f9772ea6_img_prop_001_sc_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level location reference for loc_002 in scene sc_001. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_001",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_049/_workspace/workspace_global_20260509_212514/artifacts/media/KeyFrameAgent/image/step_3_f9772ea6_img_loc_002_sc_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level character reference for char_001 in scene sc_001. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_001",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_049/_workspace/workspace_global_20260509_212514/artifacts/media/KeyFrameAgent/image/step_3_f9772ea6_img_char_001_sc_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level location reference for loc_003 in scene sc_002. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_002",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_049/_workspace/workspace_global_20260509_212514/artifacts/media/KeyFrameAgent/image/step_3_f9772ea6_img_loc_003_sc_002.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_006 in scene sc_002. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_006",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_049/_workspace/workspace_global_20260509_212514/artifacts/media/KeyFrameAgent/image/step_3_f9772ea6_img_sh_006_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_010 in scene sc_002. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_010",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_049/_workspace/workspace_global_20260509_212514/artifacts/media/KeyFrameAgent/image/step_3_f9772ea6_img_sh_010_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_005 in scene sc_001. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_005",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_049/_workspace/workspace_global_20260509_212514/artifacts/media/KeyFrameAgent/image/step_3_f9772ea6_img_sh_005_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_004 in scene sc_001. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_004",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_049/_workspace/workspace_global_20260509_212514/artifacts/media/KeyFrameAgent/image/step_3_f9772ea6_img_sh_004_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_008 in scene sc_002. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_008",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_049/_workspace/workspace_global_20260509_212514/artifacts/media/KeyFrameAgent/image/step_3_f9772ea6_img_sh_008_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_002 in scene sc_001. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_002",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_049/_workspace/workspace_global_20260509_212514/artifacts/media/KeyFrameAgent/image/step_3_f9772ea6_img_sh_002_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_001 in scene sc_001. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_001",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_049/_workspace/workspace_global_20260509_212514/artifacts/media/KeyFrameAgent/image/step_3_f9772ea6_img_sh_001_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_007 in scene sc_002. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_007",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_049/_workspace/workspace_global_20260509_212514/artifacts/media/KeyFrameAgent/image/step_3_f9772ea6_img_sh_007_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_009 in scene sc_002. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_009",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_049/_workspace/workspace_global_20260509_212514/artifacts/media/KeyFrameAgent/image/step_3_f9772ea6_img_sh_009_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_003 in scene sc_001. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_003",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_049/_workspace/workspace_global_20260509_212514/artifacts/media/KeyFrameAgent/image/step_3_f9772ea6_img_sh_003_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Keyframe planning document: 2 scene(s), 10 shot(s), with per-shot frame descriptions and motion hints. Consumed by a downstream image-to-video generation step.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_049/_workspace/workspace_global_20260509_212514/artifacts/KeyFrameAgent/step_3_f9772ea6_keyframeagent_exec_3.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_1_00c610de",
    "agent_id": "VideoAgent",
    "step_id": "step_4_621d5cca",
    "created_at": "2026-05-10T03:36:12.105038+00:00",
    "artifacts": [
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_001] Video clip bytes for shot sh_001. One segment of the final video.",
        "scope": "shot:sh_001",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_049/_workspace/workspace_global_20260509_212514/artifacts/media/VideoAgent/video/step_4_621d5cca_clip_sh_001.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_002] Video clip bytes for shot sh_002. One segment of the final video.",
        "scope": "shot:sh_002",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_049/_workspace/workspace_global_20260509_212514/artifacts/media/VideoAgent/video/step_4_621d5cca_clip_sh_002.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_003] Video clip bytes for shot sh_003. One segment of the final video.",
        "scope": "shot:sh_003",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_049/_workspace/workspace_global_20260509_212514/artifacts/media/VideoAgent/video/step_4_621d5cca_clip_sh_003.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_004] Video clip bytes for shot sh_004. One segment of the final video.",
        "scope": "shot:sh_004",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_049/_workspace/workspace_global_20260509_212514/artifacts/media/VideoAgent/video/step_4_621d5cca_clip_sh_004.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_005] Video clip bytes for shot sh_005. One segment of the final video.",
        "scope": "shot:sh_005",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_049/_workspace/workspace_global_20260509_212514/artifacts/media/VideoAgent/video/step_4_621d5cca_clip_sh_005.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_006] Video clip bytes for shot sh_006. One segment of the final video.",
        "scope": "shot:sh_006",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_049/_workspace/workspace_global_20260509_212514/artifacts/media/VideoAgent/video/step_4_621d5cca_clip_sh_006.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_007] Video clip bytes for shot sh_007. One segment of the final video.",
        "scope": "shot:sh_007",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_049/_workspace/workspace_global_20260509_212514/artifacts/media/VideoAgent/video/step_4_621d5cca_clip_sh_007.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_008] Video clip bytes for shot sh_008. One segment of the final video.",
        "scope": "shot:sh_008",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_049/_workspace/workspace_global_20260509_212514/artifacts/media/VideoAgent/video/step_4_621d5cca_clip_sh_008.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_009] Video clip bytes for shot sh_009. One segment of the final video.",
        "scope": "shot:sh_009",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_049/_workspace/workspace_global_20260509_212514/artifacts/media/VideoAgent/video/step_4_621d5cca_clip_sh_009.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_010] Video clip bytes for shot sh_010. One segment of the final video.",
        "scope": "shot:sh_010",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_049/_workspace/workspace_global_20260509_212514/artifacts/media/VideoAgent/video/step_4_621d5cca_clip_sh_010.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sc_001] Scene-cut bytes for scene sc_001 — all shots concatenated. Intermediate assembly, not final.",
        "scope": "scene:sc_001",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_049/_workspace/workspace_global_20260509_212514/artifacts/media/VideoAgent/video/step_4_621d5cca_clip_sc_001.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sc_002] Scene-cut bytes for scene sc_002 — all shots concatenated. Intermediate assembly, not final.",
        "scope": "scene:sc_002",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_049/_workspace/workspace_global_20260509_212514/artifacts/media/VideoAgent/video/step_4_621d5cca_clip_sc_002.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_final] Complete assembled video bytes (10 shots). Final visual deliverable — consumed by a downstream audio-mix step's materializer via ffmpeg for audio extraction + muxing.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_049/_workspace/workspace_global_20260509_212514/artifacts/media/VideoAgent/video/step_4_621d5cca_clip_final.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[JSON MANIFEST] Video-assembly planning metadata: 2 scene(s), 10 shot clip(s) with timing. Read by a downstream audio-mix step's LLM for mix planning.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_049/_workspace/workspace_global_20260509_212514/artifacts/VideoAgent/step_4_621d5cca_videoagent_exec_1.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_2_966370d6",
    "agent_id": "CompositorAgent",
    "step_id": "step_5_7f7940b5",
    "created_at": "2026-05-10T03:36:28.237908+00:00",
    "artifacts": [
      {
        "caption": "Final delivered video binary (mp4) — the complete composited output with audio mix and (optional) subtitle burn-in. Terminal deliverable of the creative pipeline.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_049/_workspace/workspace_global_20260509_212514/artifacts/media/CompositorAgent/video/step_5_7f7940b5_compositor_final.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "Final composited video (1920x1080): audio mix, subtitle burn-in. Ready for delivery.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_049/_workspace/workspace_global_20260509_212514/artifacts/CompositorAgent/step_5_7f7940b5_compositoragent_exec_2.json",
        "mime": "application/json"
      }
    ]
  }
]
```
