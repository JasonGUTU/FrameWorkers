# Global memory — `workspace_global_20260508_041133`

Per-execution record of every artifact persisted in this workspace. Each entry below is one agent execution; its `artifacts` array carries the natural-language `caption`, `scope`, absolute `path` and `mime` for every file that execution wrote.

`InputResolver` reads this index to match artifacts against each consumer agent's `[label]` slots. Execution history (including failures) lives in the assistant executions table, not here.

## Entries

```json
[
  {
    "execution_id": "brief_20260508_041150_409558",
    "agent_id": "user",
    "step_id": "",
    "created_at": "2026-05-08T04:11:50.414816+00:00",
    "artifacts": [
      {
        "caption": "Structured metadata document (JSON) for a user-submitted text brief. Payload carries the raw text verbatim. Pipeline entry point — consumed by story / screenplay / narration agents.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/framework_cr_001_postaudit_20260508_041104/_workspace/workspace_global_20260508_041133/inputs/brief_20260508_041150_409558.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_1_063f97e7",
    "agent_id": "ScreenplayAgent",
    "step_id": "step_1_e2007a40",
    "created_at": "2026-05-08T04:13:13.418909+00:00",
    "artifacts": [
      {
        "caption": "Screenplay: 2 scene(s), 9 shot(s). Input for keyframe planning and audio scoring.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/framework_cr_001_postaudit_20260508_041104/_workspace/workspace_global_20260508_041133/artifacts/ScreenplayAgent/step_1_e2007a40_screenplayagent_exec_1.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_2_f0f0c38b",
    "agent_id": "KeyFrameAgent",
    "step_id": "step_2_d4ca90ac",
    "created_at": "2026-05-08T04:15:30.976436+00:00",
    "artifacts": [
      {
        "caption": "Global prop reference image for prop_001. Visual identity anchor — not a video frame.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/framework_cr_001_postaudit_20260508_041104/_workspace/workspace_global_20260508_041133/artifacts/media/KeyFrameAgent/image/step_2_d4ca90ac_img_prop_001_global.png",
        "mime": "image/png"
      },
      {
        "caption": "Global prop reference image for prop_003. Visual identity anchor — not a video frame.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/framework_cr_001_postaudit_20260508_041104/_workspace/workspace_global_20260508_041133/artifacts/media/KeyFrameAgent/image/step_2_d4ca90ac_img_prop_003_global.png",
        "mime": "image/png"
      },
      {
        "caption": "Global location reference image for loc_002. Visual identity anchor — not a video frame.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/framework_cr_001_postaudit_20260508_041104/_workspace/workspace_global_20260508_041133/artifacts/media/KeyFrameAgent/image/step_2_d4ca90ac_img_loc_002_global.png",
        "mime": "image/png"
      },
      {
        "caption": "Global location reference image for loc_001. Visual identity anchor — not a video frame.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/framework_cr_001_postaudit_20260508_041104/_workspace/workspace_global_20260508_041133/artifacts/media/KeyFrameAgent/image/step_2_d4ca90ac_img_loc_001_global.png",
        "mime": "image/png"
      },
      {
        "caption": "Global character reference image for char_001. Visual identity anchor — not a video frame.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/framework_cr_001_postaudit_20260508_041104/_workspace/workspace_global_20260508_041133/artifacts/media/KeyFrameAgent/image/step_2_d4ca90ac_img_char_001_global.png",
        "mime": "image/png"
      },
      {
        "caption": "Global prop reference image for prop_002. Visual identity anchor — not a video frame.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/framework_cr_001_postaudit_20260508_041104/_workspace/workspace_global_20260508_041133/artifacts/media/KeyFrameAgent/image/step_2_d4ca90ac_img_prop_002_global.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level prop reference for prop_002 in scene sc_001. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_001",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/framework_cr_001_postaudit_20260508_041104/_workspace/workspace_global_20260508_041133/artifacts/media/KeyFrameAgent/image/step_2_d4ca90ac_img_prop_002_sc_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level character reference for char_001 in scene sc_002. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_002",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/framework_cr_001_postaudit_20260508_041104/_workspace/workspace_global_20260508_041133/artifacts/media/KeyFrameAgent/image/step_2_d4ca90ac_img_char_001_sc_002.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level prop reference for prop_001 in scene sc_002. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_002",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/framework_cr_001_postaudit_20260508_041104/_workspace/workspace_global_20260508_041133/artifacts/media/KeyFrameAgent/image/step_2_d4ca90ac_img_prop_001_sc_002.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level location reference for loc_001 in scene sc_001. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_001",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/framework_cr_001_postaudit_20260508_041104/_workspace/workspace_global_20260508_041133/artifacts/media/KeyFrameAgent/image/step_2_d4ca90ac_img_loc_001_sc_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level character reference for char_001 in scene sc_001. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_001",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/framework_cr_001_postaudit_20260508_041104/_workspace/workspace_global_20260508_041133/artifacts/media/KeyFrameAgent/image/step_2_d4ca90ac_img_char_001_sc_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level prop reference for prop_003 in scene sc_002. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_002",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/framework_cr_001_postaudit_20260508_041104/_workspace/workspace_global_20260508_041133/artifacts/media/KeyFrameAgent/image/step_2_d4ca90ac_img_prop_003_sc_002.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level location reference for loc_002 in scene sc_002. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_002",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/framework_cr_001_postaudit_20260508_041104/_workspace/workspace_global_20260508_041133/artifacts/media/KeyFrameAgent/image/step_2_d4ca90ac_img_loc_002_sc_002.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level prop reference for prop_001 in scene sc_001. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_001",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/framework_cr_001_postaudit_20260508_041104/_workspace/workspace_global_20260508_041133/artifacts/media/KeyFrameAgent/image/step_2_d4ca90ac_img_prop_001_sc_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_002 in scene sc_001. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_002",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/framework_cr_001_postaudit_20260508_041104/_workspace/workspace_global_20260508_041133/artifacts/media/KeyFrameAgent/image/step_2_d4ca90ac_img_sh_002_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_003 in scene sc_001. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_003",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/framework_cr_001_postaudit_20260508_041104/_workspace/workspace_global_20260508_041133/artifacts/media/KeyFrameAgent/image/step_2_d4ca90ac_img_sh_003_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_005 in scene sc_002. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_005",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/framework_cr_001_postaudit_20260508_041104/_workspace/workspace_global_20260508_041133/artifacts/media/KeyFrameAgent/image/step_2_d4ca90ac_img_sh_005_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_001 in scene sc_001. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_001",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/framework_cr_001_postaudit_20260508_041104/_workspace/workspace_global_20260508_041133/artifacts/media/KeyFrameAgent/image/step_2_d4ca90ac_img_sh_001_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_004 in scene sc_001. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_004",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/framework_cr_001_postaudit_20260508_041104/_workspace/workspace_global_20260508_041133/artifacts/media/KeyFrameAgent/image/step_2_d4ca90ac_img_sh_004_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_006 in scene sc_002. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_006",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/framework_cr_001_postaudit_20260508_041104/_workspace/workspace_global_20260508_041133/artifacts/media/KeyFrameAgent/image/step_2_d4ca90ac_img_sh_006_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_008 in scene sc_002. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_008",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/framework_cr_001_postaudit_20260508_041104/_workspace/workspace_global_20260508_041133/artifacts/media/KeyFrameAgent/image/step_2_d4ca90ac_img_sh_008_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_007 in scene sc_002. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_007",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/framework_cr_001_postaudit_20260508_041104/_workspace/workspace_global_20260508_041133/artifacts/media/KeyFrameAgent/image/step_2_d4ca90ac_img_sh_007_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_009 in scene sc_002. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_009",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/framework_cr_001_postaudit_20260508_041104/_workspace/workspace_global_20260508_041133/artifacts/media/KeyFrameAgent/image/step_2_d4ca90ac_img_sh_009_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Keyframe planning document: 2 scene(s), 9 shot(s), with per-shot frame descriptions and motion hints. Consumed by a downstream image-to-video generation step.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/framework_cr_001_postaudit_20260508_041104/_workspace/workspace_global_20260508_041133/artifacts/KeyFrameAgent/step_2_d4ca90ac_keyframeagent_exec_2.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_3_437656ec",
    "agent_id": "VideoAgent",
    "step_id": "step_3_3881a70c",
    "created_at": "2026-05-08T04:18:50.414521+00:00",
    "artifacts": [
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_001] Video clip bytes for shot sh_001. One segment of the final video.",
        "scope": "shot:sh_001",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/framework_cr_001_postaudit_20260508_041104/_workspace/workspace_global_20260508_041133/artifacts/media/VideoAgent/video/step_3_3881a70c_clip_sh_001.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_002] Video clip bytes for shot sh_002. One segment of the final video.",
        "scope": "shot:sh_002",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/framework_cr_001_postaudit_20260508_041104/_workspace/workspace_global_20260508_041133/artifacts/media/VideoAgent/video/step_3_3881a70c_clip_sh_002.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_003] Video clip bytes for shot sh_003. One segment of the final video.",
        "scope": "shot:sh_003",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/framework_cr_001_postaudit_20260508_041104/_workspace/workspace_global_20260508_041133/artifacts/media/VideoAgent/video/step_3_3881a70c_clip_sh_003.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_004] Video clip bytes for shot sh_004. One segment of the final video.",
        "scope": "shot:sh_004",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/framework_cr_001_postaudit_20260508_041104/_workspace/workspace_global_20260508_041133/artifacts/media/VideoAgent/video/step_3_3881a70c_clip_sh_004.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_005] Video clip bytes for shot sh_005. One segment of the final video.",
        "scope": "shot:sh_005",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/framework_cr_001_postaudit_20260508_041104/_workspace/workspace_global_20260508_041133/artifacts/media/VideoAgent/video/step_3_3881a70c_clip_sh_005.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_006] Video clip bytes for shot sh_006. One segment of the final video.",
        "scope": "shot:sh_006",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/framework_cr_001_postaudit_20260508_041104/_workspace/workspace_global_20260508_041133/artifacts/media/VideoAgent/video/step_3_3881a70c_clip_sh_006.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_007] Video clip bytes for shot sh_007. One segment of the final video.",
        "scope": "shot:sh_007",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/framework_cr_001_postaudit_20260508_041104/_workspace/workspace_global_20260508_041133/artifacts/media/VideoAgent/video/step_3_3881a70c_clip_sh_007.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_008] Video clip bytes for shot sh_008. One segment of the final video.",
        "scope": "shot:sh_008",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/framework_cr_001_postaudit_20260508_041104/_workspace/workspace_global_20260508_041133/artifacts/media/VideoAgent/video/step_3_3881a70c_clip_sh_008.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_009] Video clip bytes for shot sh_009. One segment of the final video.",
        "scope": "shot:sh_009",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/framework_cr_001_postaudit_20260508_041104/_workspace/workspace_global_20260508_041133/artifacts/media/VideoAgent/video/step_3_3881a70c_clip_sh_009.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sc_001] Scene-cut bytes for scene sc_001 — all shots concatenated. Intermediate assembly, not final.",
        "scope": "scene:sc_001",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/framework_cr_001_postaudit_20260508_041104/_workspace/workspace_global_20260508_041133/artifacts/media/VideoAgent/video/step_3_3881a70c_clip_sc_001.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sc_002] Scene-cut bytes for scene sc_002 — all shots concatenated. Intermediate assembly, not final.",
        "scope": "scene:sc_002",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/framework_cr_001_postaudit_20260508_041104/_workspace/workspace_global_20260508_041133/artifacts/media/VideoAgent/video/step_3_3881a70c_clip_sc_002.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_final] Complete assembled video bytes (9 shots). Final visual deliverable — consumed by a downstream audio-mix step's materializer via ffmpeg for audio extraction + muxing.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/framework_cr_001_postaudit_20260508_041104/_workspace/workspace_global_20260508_041133/artifacts/media/VideoAgent/video/step_3_3881a70c_clip_final.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[JSON MANIFEST] Video-assembly planning metadata: 2 scene(s), 9 shot clip(s) with timing. Read by a downstream audio-mix step's LLM for mix planning.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/framework_cr_001_postaudit_20260508_041104/_workspace/workspace_global_20260508_041133/artifacts/VideoAgent/step_3_3881a70c_videoagent_exec_3.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_4_34ec96ed",
    "agent_id": "MusicAgent",
    "step_id": "step_4_dee4db38",
    "created_at": "2026-05-08T04:21:20.261120+00:00",
    "artifacts": [
      {
        "caption": "[BINARY WAV FILE · mime=audio/wav · sys_id aud_music_film] Background-music audio bytes for the film-wide BGM underlay. Consumed by the audio-mix materializer via ffmpeg.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/framework_cr_001_postaudit_20260508_041104/_workspace/workspace_global_20260508_041133/artifacts/media/MusicAgent/audio/step_4_dee4db38_aud_music_film.wav",
        "mime": "audio/wav"
      },
      {
        "caption": "[JSON MANIFEST] Background-music planning metadata: 1 cue(s) carrying the LLM-chosen mood for the film-wide BGM underlay. Read by the audio-mix LLM for mix planning.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/framework_cr_001_postaudit_20260508_041104/_workspace/workspace_global_20260508_041133/artifacts/MusicAgent/step_4_dee4db38_musicagent_exec_4.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_5_aa61944f",
    "agent_id": "AmbienceAgent",
    "step_id": "step_5_c9b324e4",
    "created_at": "2026-05-08T04:22:10.650955+00:00",
    "artifacts": [
      {
        "caption": "[BINARY WAV FILE · mime=audio/wav · sys_id aud_amb_film] Ambient room-tone audio bytes for the film-wide atmospheric underlay. Consumed by the audio-mix materializer via ffmpeg.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/framework_cr_001_postaudit_20260508_041104/_workspace/workspace_global_20260508_041133/artifacts/media/AmbienceAgent/audio/step_5_c9b324e4_aud_amb_film.wav",
        "mime": "audio/wav"
      },
      {
        "caption": "[JSON MANIFEST] Ambience planning metadata: 1 bed(s) carrying the LLM-chosen description for the film-wide room-tone underlay. Read by the audio-mix LLM for mix planning.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/framework_cr_001_postaudit_20260508_041104/_workspace/workspace_global_20260508_041133/artifacts/AmbienceAgent/step_5_c9b324e4_ambienceagent_exec_5.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_6_7a9cb44e",
    "agent_id": "AudioMixAgent",
    "step_id": "step_6_e5f0dd48",
    "created_at": "2026-05-08T04:22:31.930487+00:00",
    "artifacts": [
      {
        "caption": "[BINARY WAV FILE · mime=audio/wav · sys_id aud_final] Final-mix audio bytes — all source audio tracks (dialogue / foley / music / ambience / narrator) merged. Ready to be muxed onto the delivered video by a downstream compositing step.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/framework_cr_001_postaudit_20260508_041104/_workspace/workspace_global_20260508_041133/artifacts/media/AudioMixAgent/audio/step_6_e5f0dd48_aud_final.wav",
        "mime": "audio/wav"
      },
      {
        "caption": "[JSON MANIFEST] Final-audio-mix envelope: amix of 3 source track(s) (video dialogue+foley + optional global music/ambience/narrator). Planning manifest only; the wav is a sibling artifact.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/framework_cr_001_postaudit_20260508_041104/_workspace/workspace_global_20260508_041133/artifacts/AudioMixAgent/step_6_e5f0dd48_audiomixagent_exec_6.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_7_896ac8f8",
    "agent_id": "CompositorAgent",
    "step_id": "step_7_003ff6d2",
    "created_at": "2026-05-08T04:22:59.971563+00:00",
    "artifacts": [
      {
        "caption": "Final delivered video binary (mp4) — the complete composited output with audio mix and (optional) subtitle burn-in. Terminal deliverable of the creative pipeline.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/framework_cr_001_postaudit_20260508_041104/_workspace/workspace_global_20260508_041133/artifacts/media/CompositorAgent/video/step_7_003ff6d2_compositor_final.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "Final composited video (1920x1080): audio mix, subtitle burn-in. Ready for delivery.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/framework_cr_001_postaudit_20260508_041104/_workspace/workspace_global_20260508_041133/artifacts/CompositorAgent/step_7_003ff6d2_compositoragent_exec_7.json",
        "mime": "application/json"
      }
    ]
  }
]
```
