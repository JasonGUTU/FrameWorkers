# Global memory — `workspace_global_20260509_212514`

Per-execution record of every artifact persisted in this workspace. Each entry below is one agent execution; its `artifacts` array carries the natural-language `caption`, `scope`, absolute `path` and `mime` for every file that execution wrote.

`InputResolver` reads this index to match artifacts against each consumer agent's `[label]` slots. Execution history (including failures) lives in the assistant executions table, not here.

## Entries

```json
[
  {
    "execution_id": "brief_20260509_212516_341484",
    "agent_id": "user",
    "step_id": "",
    "created_at": "2026-05-09T21:25:16.344339+00:00",
    "artifacts": [
      {
        "caption": "Structured metadata document (JSON) for a user-submitted text brief. Payload carries the raw text verbatim. Pipeline entry point — consumed by story / screenplay / narration agents.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_059/_workspace/workspace_global_20260509_212514/inputs/brief_20260509_212516_341484.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_1_d262d39f",
    "agent_id": "StoryAgent",
    "step_id": "step_1_0a944b92",
    "created_at": "2026-05-09T21:25:46.318203+00:00",
    "artifacts": [
      {
        "caption": "Story blueprint: 3 scene(s), 2 character(s). Structured input for screenplay generation.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_059/_workspace/workspace_global_20260509_212514/artifacts/StoryAgent/step_1_0a944b92_storyagent_exec_1.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_2_dfa95aeb",
    "agent_id": "ScreenplayAgent",
    "step_id": "step_2_5a18f4ef",
    "created_at": "2026-05-09T21:26:36.222534+00:00",
    "artifacts": [
      {
        "caption": "Screenplay: 3 scene(s), 11 shot(s). Input for keyframe planning and audio scoring.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_059/_workspace/workspace_global_20260509_212514/artifacts/ScreenplayAgent/step_2_5a18f4ef_screenplayagent_exec_2.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_3_a6455d59",
    "agent_id": "KeyFrameAgent",
    "step_id": "step_3_f6c1b56f",
    "created_at": "2026-05-09T21:29:51.951287+00:00",
    "artifacts": [
      {
        "caption": "Global character reference image for char_001. Visual identity anchor — not a video frame.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_059/_workspace/workspace_global_20260509_212514/artifacts/media/KeyFrameAgent/image/step_3_f6c1b56f_img_char_001_global.png",
        "mime": "image/png"
      },
      {
        "caption": "Global character reference image for char_002. Visual identity anchor — not a video frame.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_059/_workspace/workspace_global_20260509_212514/artifacts/media/KeyFrameAgent/image/step_3_f6c1b56f_img_char_002_global.png",
        "mime": "image/png"
      },
      {
        "caption": "Global location reference image for loc_001. Visual identity anchor — not a video frame.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_059/_workspace/workspace_global_20260509_212514/artifacts/media/KeyFrameAgent/image/step_3_f6c1b56f_img_loc_001_global.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level character reference for char_002 in scene sc_002. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_002",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_059/_workspace/workspace_global_20260509_212514/artifacts/media/KeyFrameAgent/image/step_3_f6c1b56f_img_char_002_sc_002.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level character reference for char_001 in scene sc_001. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_001",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_059/_workspace/workspace_global_20260509_212514/artifacts/media/KeyFrameAgent/image/step_3_f6c1b56f_img_char_001_sc_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level character reference for char_001 in scene sc_002. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_002",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_059/_workspace/workspace_global_20260509_212514/artifacts/media/KeyFrameAgent/image/step_3_f6c1b56f_img_char_001_sc_002.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level location reference for loc_001 in scene sc_003. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_003",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_059/_workspace/workspace_global_20260509_212514/artifacts/media/KeyFrameAgent/image/step_3_f6c1b56f_img_loc_001_sc_003.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level location reference for loc_001 in scene sc_002. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_002",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_059/_workspace/workspace_global_20260509_212514/artifacts/media/KeyFrameAgent/image/step_3_f6c1b56f_img_loc_001_sc_002.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level location reference for loc_001 in scene sc_001. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_001",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_059/_workspace/workspace_global_20260509_212514/artifacts/media/KeyFrameAgent/image/step_3_f6c1b56f_img_loc_001_sc_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level character reference for char_002 in scene sc_001. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_001",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_059/_workspace/workspace_global_20260509_212514/artifacts/media/KeyFrameAgent/image/step_3_f6c1b56f_img_char_002_sc_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level character reference for char_002 in scene sc_003. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_003",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_059/_workspace/workspace_global_20260509_212514/artifacts/media/KeyFrameAgent/image/step_3_f6c1b56f_img_char_002_sc_003.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level character reference for char_001 in scene sc_003. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_003",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_059/_workspace/workspace_global_20260509_212514/artifacts/media/KeyFrameAgent/image/step_3_f6c1b56f_img_char_001_sc_003.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_001 in scene sc_001. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_001",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_059/_workspace/workspace_global_20260509_212514/artifacts/media/KeyFrameAgent/image/step_3_f6c1b56f_img_sh_001_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_009 in scene sc_003. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_009",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_059/_workspace/workspace_global_20260509_212514/artifacts/media/KeyFrameAgent/image/step_3_f6c1b56f_img_sh_009_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_006 in scene sc_002. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_006",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_059/_workspace/workspace_global_20260509_212514/artifacts/media/KeyFrameAgent/image/step_3_f6c1b56f_img_sh_006_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_011 in scene sc_003. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_011",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_059/_workspace/workspace_global_20260509_212514/artifacts/media/KeyFrameAgent/image/step_3_f6c1b56f_img_sh_011_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_004 in scene sc_002. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_004",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_059/_workspace/workspace_global_20260509_212514/artifacts/media/KeyFrameAgent/image/step_3_f6c1b56f_img_sh_004_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_003 in scene sc_001. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_003",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_059/_workspace/workspace_global_20260509_212514/artifacts/media/KeyFrameAgent/image/step_3_f6c1b56f_img_sh_003_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_005 in scene sc_002. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_005",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_059/_workspace/workspace_global_20260509_212514/artifacts/media/KeyFrameAgent/image/step_3_f6c1b56f_img_sh_005_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_007 in scene sc_002. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_007",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_059/_workspace/workspace_global_20260509_212514/artifacts/media/KeyFrameAgent/image/step_3_f6c1b56f_img_sh_007_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_010 in scene sc_003. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_010",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_059/_workspace/workspace_global_20260509_212514/artifacts/media/KeyFrameAgent/image/step_3_f6c1b56f_img_sh_010_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_002 in scene sc_001. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_002",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_059/_workspace/workspace_global_20260509_212514/artifacts/media/KeyFrameAgent/image/step_3_f6c1b56f_img_sh_002_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_008 in scene sc_003. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_008",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_059/_workspace/workspace_global_20260509_212514/artifacts/media/KeyFrameAgent/image/step_3_f6c1b56f_img_sh_008_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Keyframe planning document: 3 scene(s), 11 shot(s), with per-shot frame descriptions and motion hints. Consumed by a downstream image-to-video generation step.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_059/_workspace/workspace_global_20260509_212514/artifacts/KeyFrameAgent/step_3_f6c1b56f_keyframeagent_exec_3.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_1_3c7e90d2",
    "agent_id": "VideoAgent",
    "step_id": "step_4_5b0d7cca",
    "created_at": "2026-05-10T04:06:20.459194+00:00",
    "artifacts": [
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_001] Video clip bytes for shot sh_001. One segment of the final video.",
        "scope": "shot:sh_001",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_059/_workspace/workspace_global_20260509_212514/artifacts/media/VideoAgent/video/step_4_5b0d7cca_clip_sh_001.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_002] Video clip bytes for shot sh_002. One segment of the final video.",
        "scope": "shot:sh_002",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_059/_workspace/workspace_global_20260509_212514/artifacts/media/VideoAgent/video/step_4_5b0d7cca_clip_sh_002.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_003] Video clip bytes for shot sh_003. One segment of the final video.",
        "scope": "shot:sh_003",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_059/_workspace/workspace_global_20260509_212514/artifacts/media/VideoAgent/video/step_4_5b0d7cca_clip_sh_003.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_004] Video clip bytes for shot sh_004. One segment of the final video.",
        "scope": "shot:sh_004",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_059/_workspace/workspace_global_20260509_212514/artifacts/media/VideoAgent/video/step_4_5b0d7cca_clip_sh_004.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_005] Video clip bytes for shot sh_005. One segment of the final video.",
        "scope": "shot:sh_005",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_059/_workspace/workspace_global_20260509_212514/artifacts/media/VideoAgent/video/step_4_5b0d7cca_clip_sh_005.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_006] Video clip bytes for shot sh_006. One segment of the final video.",
        "scope": "shot:sh_006",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_059/_workspace/workspace_global_20260509_212514/artifacts/media/VideoAgent/video/step_4_5b0d7cca_clip_sh_006.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_007] Video clip bytes for shot sh_007. One segment of the final video.",
        "scope": "shot:sh_007",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_059/_workspace/workspace_global_20260509_212514/artifacts/media/VideoAgent/video/step_4_5b0d7cca_clip_sh_007.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_008] Video clip bytes for shot sh_008. One segment of the final video.",
        "scope": "shot:sh_008",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_059/_workspace/workspace_global_20260509_212514/artifacts/media/VideoAgent/video/step_4_5b0d7cca_clip_sh_008.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_009] Video clip bytes for shot sh_009. One segment of the final video.",
        "scope": "shot:sh_009",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_059/_workspace/workspace_global_20260509_212514/artifacts/media/VideoAgent/video/step_4_5b0d7cca_clip_sh_009.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_010] Video clip bytes for shot sh_010. One segment of the final video.",
        "scope": "shot:sh_010",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_059/_workspace/workspace_global_20260509_212514/artifacts/media/VideoAgent/video/step_4_5b0d7cca_clip_sh_010.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_011] Video clip bytes for shot sh_011. One segment of the final video.",
        "scope": "shot:sh_011",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_059/_workspace/workspace_global_20260509_212514/artifacts/media/VideoAgent/video/step_4_5b0d7cca_clip_sh_011.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sc_001] Scene-cut bytes for scene sc_001 — all shots concatenated. Intermediate assembly, not final.",
        "scope": "scene:sc_001",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_059/_workspace/workspace_global_20260509_212514/artifacts/media/VideoAgent/video/step_4_5b0d7cca_clip_sc_001.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sc_002] Scene-cut bytes for scene sc_002 — all shots concatenated. Intermediate assembly, not final.",
        "scope": "scene:sc_002",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_059/_workspace/workspace_global_20260509_212514/artifacts/media/VideoAgent/video/step_4_5b0d7cca_clip_sc_002.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sc_003] Scene-cut bytes for scene sc_003 — all shots concatenated. Intermediate assembly, not final.",
        "scope": "scene:sc_003",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_059/_workspace/workspace_global_20260509_212514/artifacts/media/VideoAgent/video/step_4_5b0d7cca_clip_sc_003.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_final] Complete assembled video bytes (11 shots). Final visual deliverable — consumed by a downstream audio-mix step's materializer via ffmpeg for audio extraction + muxing.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_059/_workspace/workspace_global_20260509_212514/artifacts/media/VideoAgent/video/step_4_5b0d7cca_clip_final.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[JSON MANIFEST] Video-assembly planning metadata: 3 scene(s), 11 shot clip(s) with timing. Read by a downstream audio-mix step's LLM for mix planning.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_059/_workspace/workspace_global_20260509_212514/artifacts/VideoAgent/step_4_5b0d7cca_videoagent_exec_1.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_2_a78c19c6",
    "agent_id": "MusicAgent",
    "step_id": "step_5_e0c4960a",
    "created_at": "2026-05-10T04:08:15.981288+00:00",
    "artifacts": [
      {
        "caption": "[BINARY WAV FILE · mime=audio/wav · sys_id aud_music_film] Background-music audio bytes for the film-wide BGM underlay. Consumed by the audio-mix materializer via ffmpeg.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_059/_workspace/workspace_global_20260509_212514/artifacts/media/MusicAgent/audio/step_5_e0c4960a_aud_music_film.wav",
        "mime": "audio/wav"
      },
      {
        "caption": "[JSON MANIFEST] Background-music planning metadata: 1 cue(s) carrying the LLM-chosen mood for the film-wide BGM underlay. Read by the audio-mix LLM for mix planning.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_059/_workspace/workspace_global_20260509_212514/artifacts/MusicAgent/step_5_e0c4960a_musicagent_exec_2.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_3_665a9d7e",
    "agent_id": "AudioMixAgent",
    "step_id": "step_6_50843de0",
    "created_at": "2026-05-10T04:08:24.100759+00:00",
    "artifacts": [
      {
        "caption": "[BINARY WAV FILE · mime=audio/wav · sys_id aud_final] Final-mix audio bytes — all source audio tracks (dialogue / foley / music / ambience / narrator) merged. Ready to be muxed onto the delivered video by a downstream compositing step.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_059/_workspace/workspace_global_20260509_212514/artifacts/media/AudioMixAgent/audio/step_6_50843de0_aud_final.wav",
        "mime": "audio/wav"
      },
      {
        "caption": "[JSON MANIFEST] Final-audio-mix envelope: amix of 3 source track(s) (video dialogue+foley + optional global music/ambience/narrator). Planning manifest only; the wav is a sibling artifact.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_059/_workspace/workspace_global_20260509_212514/artifacts/AudioMixAgent/step_6_50843de0_audiomixagent_exec_3.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_4_7a13a8f9",
    "agent_id": "CompositorAgent",
    "step_id": "step_7_5d869ea5",
    "created_at": "2026-05-10T04:08:39.970724+00:00",
    "artifacts": [
      {
        "caption": "Final delivered video binary (mp4) — the complete composited output with audio mix and (optional) subtitle burn-in. Terminal deliverable of the creative pipeline.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_059/_workspace/workspace_global_20260509_212514/artifacts/media/CompositorAgent/video/step_7_5d869ea5_compositor_final.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "Final composited video (1920x1080): audio mix, subtitle burn-in. Ready for delivery.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_059/_workspace/workspace_global_20260509_212514/artifacts/CompositorAgent/step_7_5d869ea5_compositoragent_exec_4.json",
        "mime": "application/json"
      }
    ]
  }
]
```
