# Global memory — `workspace_global_20260510_212627`

Per-execution record of every artifact persisted in this workspace. Each entry below is one agent execution; its `artifacts` array carries the natural-language `caption`, `scope`, absolute `path` and `mime` for every file that execution wrote.

`InputResolver` reads this index to match artifacts against each consumer agent's `[label]` slots. Execution history (including failures) lives in the assistant executions table, not here.

## Entries

```json
[
  {
    "execution_id": "upload_20260510_212628_547911",
    "agent_id": "user",
    "step_id": "",
    "created_at": "2026-05-10T21:26:28.550411+00:00",
    "artifacts": [
      {
        "caption": "Global character reference image. Visual identity anchor for downstream keyframe generation.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_037/_workspace/workspace_global_20260510_212627/inputs/20260510_212628_547911_intake_img_037.png",
        "mime": "image/png"
      }
    ]
  },
  {
    "execution_id": "brief_20260510_212628_566122",
    "agent_id": "user",
    "step_id": "",
    "created_at": "2026-05-10T21:26:28.568499+00:00",
    "artifacts": [
      {
        "caption": "Structured metadata document (JSON) for a user-submitted text brief. Payload carries the raw text verbatim. Pipeline entry point — consumed by story / screenplay / narration agents.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_037/_workspace/workspace_global_20260510_212627/inputs/brief_20260510_212628_566122.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_1_b936f743",
    "agent_id": "IntakeImageAgent",
    "step_id": "step_1_87f1a417",
    "created_at": "2026-05-10T21:26:37.907082+00:00",
    "artifacts": [
      {
        "caption": "Structured metadata document (JSON) for a user-uploaded image. Payload carries the visual description and image-asset metadata.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_037/_workspace/workspace_global_20260510_212627/artifacts/IntakeImageAgent/step_1_87f1a417_intakeimageagent_exec_1.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_2_e0cc082a",
    "agent_id": "BriefEnricherAgent",
    "step_id": "step_2_c1c2d6a8",
    "created_at": "2026-05-10T21:26:54.215232+00:00",
    "artifacts": [
      {
        "caption": "Enriched creative brief with visual reference descriptions integrated. Supersedes the raw user brief for story generation — contains the user's original concept plus detailed visual descriptions of uploaded reference images.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_037/_workspace/workspace_global_20260510_212627/artifacts/BriefEnricherAgent/step_2_c1c2d6a8_briefenricheragent_exec_2.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_3_f117cdbd",
    "agent_id": "StoryAgent",
    "step_id": "step_3_3cdf2b5a",
    "created_at": "2026-05-10T21:27:24.697104+00:00",
    "artifacts": [
      {
        "caption": "Story blueprint: 3 scene(s), 3 character(s). Structured input for screenplay generation.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_037/_workspace/workspace_global_20260510_212627/artifacts/StoryAgent/step_3_3cdf2b5a_storyagent_exec_3.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_4_914047de",
    "agent_id": "ScreenplayAgent",
    "step_id": "step_4_8fb41e98",
    "created_at": "2026-05-10T21:28:17.926941+00:00",
    "artifacts": [
      {
        "caption": "Screenplay: 3 scene(s), 10 shot(s). Input for keyframe planning and audio scoring.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_037/_workspace/workspace_global_20260510_212627/artifacts/ScreenplayAgent/step_4_8fb41e98_screenplayagent_exec_4.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_5_87deb197",
    "agent_id": "KeyFrameAgent",
    "step_id": "step_5_da7ced85",
    "created_at": "2026-05-10T21:30:20.428847+00:00",
    "artifacts": [
      {
        "caption": "Global character reference image for char_001. Visual identity anchor — not a video frame.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_037/_workspace/workspace_global_20260510_212627/artifacts/media/KeyFrameAgent/image/step_5_da7ced85_img_char_001_global.png",
        "mime": "image/png"
      },
      {
        "caption": "Global prop reference image for prop_001. Visual identity anchor — not a video frame.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_037/_workspace/workspace_global_20260510_212627/artifacts/media/KeyFrameAgent/image/step_5_da7ced85_img_prop_001_global.png",
        "mime": "image/png"
      },
      {
        "caption": "Global location reference image for loc_001. Visual identity anchor — not a video frame.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_037/_workspace/workspace_global_20260510_212627/artifacts/media/KeyFrameAgent/image/step_5_da7ced85_img_loc_001_global.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level prop reference for prop_001 in scene sc_003. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_003",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_037/_workspace/workspace_global_20260510_212627/artifacts/media/KeyFrameAgent/image/step_5_da7ced85_img_prop_001_sc_003.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level location reference for loc_001 in scene sc_002. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_002",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_037/_workspace/workspace_global_20260510_212627/artifacts/media/KeyFrameAgent/image/step_5_da7ced85_img_loc_001_sc_002.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level character reference for char_001 in scene sc_003. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_003",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_037/_workspace/workspace_global_20260510_212627/artifacts/media/KeyFrameAgent/image/step_5_da7ced85_img_char_001_sc_003.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level location reference for loc_001 in scene sc_003. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_003",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_037/_workspace/workspace_global_20260510_212627/artifacts/media/KeyFrameAgent/image/step_5_da7ced85_img_loc_001_sc_003.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level character reference for char_001 in scene sc_002. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_002",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_037/_workspace/workspace_global_20260510_212627/artifacts/media/KeyFrameAgent/image/step_5_da7ced85_img_char_001_sc_002.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level character reference for char_001 in scene sc_001. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_001",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_037/_workspace/workspace_global_20260510_212627/artifacts/media/KeyFrameAgent/image/step_5_da7ced85_img_char_001_sc_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level location reference for loc_001 in scene sc_001. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_001",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_037/_workspace/workspace_global_20260510_212627/artifacts/media/KeyFrameAgent/image/step_5_da7ced85_img_loc_001_sc_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_006 in scene sc_002. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_006",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_037/_workspace/workspace_global_20260510_212627/artifacts/media/KeyFrameAgent/image/step_5_da7ced85_img_sh_006_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_008 in scene sc_003. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_008",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_037/_workspace/workspace_global_20260510_212627/artifacts/media/KeyFrameAgent/image/step_5_da7ced85_img_sh_008_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_007 in scene sc_003. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_007",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_037/_workspace/workspace_global_20260510_212627/artifacts/media/KeyFrameAgent/image/step_5_da7ced85_img_sh_007_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_002 in scene sc_001. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_002",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_037/_workspace/workspace_global_20260510_212627/artifacts/media/KeyFrameAgent/image/step_5_da7ced85_img_sh_002_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_010 in scene sc_003. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_010",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_037/_workspace/workspace_global_20260510_212627/artifacts/media/KeyFrameAgent/image/step_5_da7ced85_img_sh_010_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_004 in scene sc_002. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_004",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_037/_workspace/workspace_global_20260510_212627/artifacts/media/KeyFrameAgent/image/step_5_da7ced85_img_sh_004_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_009 in scene sc_003. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_009",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_037/_workspace/workspace_global_20260510_212627/artifacts/media/KeyFrameAgent/image/step_5_da7ced85_img_sh_009_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_001 in scene sc_001. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_001",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_037/_workspace/workspace_global_20260510_212627/artifacts/media/KeyFrameAgent/image/step_5_da7ced85_img_sh_001_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_003 in scene sc_001. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_003",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_037/_workspace/workspace_global_20260510_212627/artifacts/media/KeyFrameAgent/image/step_5_da7ced85_img_sh_003_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_005 in scene sc_002. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_005",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_037/_workspace/workspace_global_20260510_212627/artifacts/media/KeyFrameAgent/image/step_5_da7ced85_img_sh_005_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Keyframe planning document: 3 scene(s), 10 shot(s), with per-shot frame descriptions and motion hints. Consumed by a downstream image-to-video generation step.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_037/_workspace/workspace_global_20260510_212627/artifacts/KeyFrameAgent/step_5_da7ced85_keyframeagent_exec_5.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_6_d89f5568",
    "agent_id": "VideoAgent",
    "step_id": "step_6_ffab05e3",
    "created_at": "2026-05-11T01:18:30.255797+00:00",
    "artifacts": [
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_001] Video clip bytes for shot sh_001. One segment of the final video.",
        "scope": "shot:sh_001",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_037/_workspace/workspace_global_20260510_212627/artifacts/media/VideoAgent/video/step_6_ffab05e3_clip_sh_001.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_002] Video clip bytes for shot sh_002. One segment of the final video.",
        "scope": "shot:sh_002",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_037/_workspace/workspace_global_20260510_212627/artifacts/media/VideoAgent/video/step_6_ffab05e3_clip_sh_002.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_003] Video clip bytes for shot sh_003. One segment of the final video.",
        "scope": "shot:sh_003",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_037/_workspace/workspace_global_20260510_212627/artifacts/media/VideoAgent/video/step_6_ffab05e3_clip_sh_003.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_004] Video clip bytes for shot sh_004. One segment of the final video.",
        "scope": "shot:sh_004",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_037/_workspace/workspace_global_20260510_212627/artifacts/media/VideoAgent/video/step_6_ffab05e3_clip_sh_004.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_005] Video clip bytes for shot sh_005. One segment of the final video.",
        "scope": "shot:sh_005",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_037/_workspace/workspace_global_20260510_212627/artifacts/media/VideoAgent/video/step_6_ffab05e3_clip_sh_005.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_006] Video clip bytes for shot sh_006. One segment of the final video.",
        "scope": "shot:sh_006",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_037/_workspace/workspace_global_20260510_212627/artifacts/media/VideoAgent/video/step_6_ffab05e3_clip_sh_006.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_007] Video clip bytes for shot sh_007. One segment of the final video.",
        "scope": "shot:sh_007",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_037/_workspace/workspace_global_20260510_212627/artifacts/media/VideoAgent/video/step_6_ffab05e3_clip_sh_007.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_008] Video clip bytes for shot sh_008. One segment of the final video.",
        "scope": "shot:sh_008",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_037/_workspace/workspace_global_20260510_212627/artifacts/media/VideoAgent/video/step_6_ffab05e3_clip_sh_008.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_009] Video clip bytes for shot sh_009. One segment of the final video.",
        "scope": "shot:sh_009",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_037/_workspace/workspace_global_20260510_212627/artifacts/media/VideoAgent/video/step_6_ffab05e3_clip_sh_009.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_010] Video clip bytes for shot sh_010. One segment of the final video.",
        "scope": "shot:sh_010",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_037/_workspace/workspace_global_20260510_212627/artifacts/media/VideoAgent/video/step_6_ffab05e3_clip_sh_010.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sc_001] Scene-cut bytes for scene sc_001 — all shots concatenated. Intermediate assembly, not final.",
        "scope": "scene:sc_001",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_037/_workspace/workspace_global_20260510_212627/artifacts/media/VideoAgent/video/step_6_ffab05e3_clip_sc_001.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sc_002] Scene-cut bytes for scene sc_002 — all shots concatenated. Intermediate assembly, not final.",
        "scope": "scene:sc_002",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_037/_workspace/workspace_global_20260510_212627/artifacts/media/VideoAgent/video/step_6_ffab05e3_clip_sc_002.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sc_003] Scene-cut bytes for scene sc_003 — all shots concatenated. Intermediate assembly, not final.",
        "scope": "scene:sc_003",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_037/_workspace/workspace_global_20260510_212627/artifacts/media/VideoAgent/video/step_6_ffab05e3_clip_sc_003.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_final] Complete assembled video bytes (10 shots). Final visual deliverable — consumed by a downstream audio-mix step's materializer via ffmpeg for audio extraction + muxing.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_037/_workspace/workspace_global_20260510_212627/artifacts/media/VideoAgent/video/step_6_ffab05e3_clip_final.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[JSON MANIFEST] Video-assembly planning metadata: 3 scene(s), 10 shot clip(s) with timing. Read by a downstream audio-mix step's LLM for mix planning.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_037/_workspace/workspace_global_20260510_212627/artifacts/VideoAgent/step_6_ffab05e3_videoagent_exec_6.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_8_d9773bd5",
    "agent_id": "TranslationAgent",
    "step_id": "step_8_545c4757",
    "created_at": "2026-05-11T01:19:32.833834+00:00",
    "artifacts": [
      {
        "caption": "Translation (en → en). Full structured text translated with original structure preserved (keys / ids / timing / ordering). Output shape mirrors input shape — a translated SRT remains an SRT, a translated screenplay remains a screenplay.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_037/_workspace/workspace_global_20260510_212627/artifacts/TranslationAgent/step_8_545c4757_translationagent_exec_8.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_9_6edddc67",
    "agent_id": "CompositorAgent",
    "step_id": "step_9_ab7b5a96",
    "created_at": "2026-05-11T01:19:50.886928+00:00",
    "artifacts": [
      {
        "caption": "Final delivered video binary (mp4) — the complete composited output with audio mix and (optional) subtitle burn-in. Terminal deliverable of the creative pipeline.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_037/_workspace/workspace_global_20260510_212627/artifacts/media/CompositorAgent/video/step_9_ab7b5a96_compositor_final.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "Final composited video (1920x1080): audio mix, subtitle burn-in. Ready for delivery.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_037/_workspace/workspace_global_20260510_212627/artifacts/CompositorAgent/step_9_ab7b5a96_compositoragent_exec_9.json",
        "mime": "application/json"
      }
    ]
  }
]
```
