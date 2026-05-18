# Global memory — `workspace_global_20260509_212514`

Per-execution record of every artifact persisted in this workspace. Each entry below is one agent execution; its `artifacts` array carries the natural-language `caption`, `scope`, absolute `path` and `mime` for every file that execution wrote.

`InputResolver` reads this index to match artifacts against each consumer agent's `[label]` slots. Execution history (including failures) lives in the assistant executions table, not here.

## Entries

```json
[
  {
    "execution_id": "brief_20260509_212516_342120",
    "agent_id": "user",
    "step_id": "",
    "created_at": "2026-05-09T21:25:16.345353+00:00",
    "artifacts": [
      {
        "caption": "Structured metadata document (JSON) for a user-submitted text brief. Payload carries the raw text verbatim. Pipeline entry point — consumed by story / screenplay / narration agents.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_072/_workspace/workspace_global_20260509_212514/inputs/brief_20260509_212516_342120.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_1_3e7584ea",
    "agent_id": "StoryAgent",
    "step_id": "step_1_bec383d9",
    "created_at": "2026-05-09T21:25:43.605665+00:00",
    "artifacts": [
      {
        "caption": "Story blueprint: 3 scene(s), 3 character(s). Structured input for screenplay generation.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_072/_workspace/workspace_global_20260509_212514/artifacts/StoryAgent/step_1_bec383d9_storyagent_exec_1.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_2_e6f7c7da",
    "agent_id": "ScreenplayAgent",
    "step_id": "step_2_918b6d9c",
    "created_at": "2026-05-09T21:26:47.911054+00:00",
    "artifacts": [
      {
        "caption": "Screenplay: 3 scene(s), 10 shot(s). Input for keyframe planning and audio scoring.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_072/_workspace/workspace_global_20260509_212514/artifacts/ScreenplayAgent/step_2_918b6d9c_screenplayagent_exec_2.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_3_0d982ded",
    "agent_id": "KeyFrameAgent",
    "step_id": "step_3_e010202f",
    "created_at": "2026-05-09T21:32:03.163628+00:00",
    "artifacts": [
      {
        "caption": "Global character reference image for char_002. Visual identity anchor — not a video frame.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_072/_workspace/workspace_global_20260509_212514/artifacts/media/KeyFrameAgent/image/step_3_e010202f_img_char_002_global.png",
        "mime": "image/png"
      },
      {
        "caption": "Global character reference image for char_001. Visual identity anchor — not a video frame.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_072/_workspace/workspace_global_20260509_212514/artifacts/media/KeyFrameAgent/image/step_3_e010202f_img_char_001_global.png",
        "mime": "image/png"
      },
      {
        "caption": "Global location reference image for loc_001. Visual identity anchor — not a video frame.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_072/_workspace/workspace_global_20260509_212514/artifacts/media/KeyFrameAgent/image/step_3_e010202f_img_loc_001_global.png",
        "mime": "image/png"
      },
      {
        "caption": "Global character reference image for char_003. Visual identity anchor — not a video frame.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_072/_workspace/workspace_global_20260509_212514/artifacts/media/KeyFrameAgent/image/step_3_e010202f_img_char_003_global.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level character reference for char_003 in scene sc_003. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_003",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_072/_workspace/workspace_global_20260509_212514/artifacts/media/KeyFrameAgent/image/step_3_e010202f_img_char_003_sc_003.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level character reference for char_001 in scene sc_002. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_002",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_072/_workspace/workspace_global_20260509_212514/artifacts/media/KeyFrameAgent/image/step_3_e010202f_img_char_001_sc_002.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level character reference for char_003 in scene sc_002. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_002",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_072/_workspace/workspace_global_20260509_212514/artifacts/media/KeyFrameAgent/image/step_3_e010202f_img_char_003_sc_002.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level location reference for loc_001 in scene sc_002. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_002",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_072/_workspace/workspace_global_20260509_212514/artifacts/media/KeyFrameAgent/image/step_3_e010202f_img_loc_001_sc_002.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level character reference for char_002 in scene sc_002. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_002",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_072/_workspace/workspace_global_20260509_212514/artifacts/media/KeyFrameAgent/image/step_3_e010202f_img_char_002_sc_002.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level location reference for loc_001 in scene sc_001. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_001",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_072/_workspace/workspace_global_20260509_212514/artifacts/media/KeyFrameAgent/image/step_3_e010202f_img_loc_001_sc_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level location reference for loc_001 in scene sc_003. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_003",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_072/_workspace/workspace_global_20260509_212514/artifacts/media/KeyFrameAgent/image/step_3_e010202f_img_loc_001_sc_003.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level character reference for char_001 in scene sc_001. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_001",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_072/_workspace/workspace_global_20260509_212514/artifacts/media/KeyFrameAgent/image/step_3_e010202f_img_char_001_sc_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level character reference for char_001 in scene sc_003. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_003",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_072/_workspace/workspace_global_20260509_212514/artifacts/media/KeyFrameAgent/image/step_3_e010202f_img_char_001_sc_003.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level character reference for char_002 in scene sc_001. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_001",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_072/_workspace/workspace_global_20260509_212514/artifacts/media/KeyFrameAgent/image/step_3_e010202f_img_char_002_sc_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Scene-level character reference for char_002 in scene sc_003. Intermediate consistency rendering — not a video frame.",
        "scope": "scene:sc_003",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_072/_workspace/workspace_global_20260509_212514/artifacts/media/KeyFrameAgent/image/step_3_e010202f_img_char_002_sc_003.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_002 in scene sc_001. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_002",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_072/_workspace/workspace_global_20260509_212514/artifacts/media/KeyFrameAgent/image/step_3_e010202f_img_sh_002_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_006 in scene sc_002. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_006",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_072/_workspace/workspace_global_20260509_212514/artifacts/media/KeyFrameAgent/image/step_3_e010202f_img_sh_006_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_001 in scene sc_001. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_001",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_072/_workspace/workspace_global_20260509_212514/artifacts/media/KeyFrameAgent/image/step_3_e010202f_img_sh_001_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_007 in scene sc_003. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_007",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_072/_workspace/workspace_global_20260509_212514/artifacts/media/KeyFrameAgent/image/step_3_e010202f_img_sh_007_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_010 in scene sc_003. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_010",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_072/_workspace/workspace_global_20260509_212514/artifacts/media/KeyFrameAgent/image/step_3_e010202f_img_sh_010_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_004 in scene sc_002. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_004",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_072/_workspace/workspace_global_20260509_212514/artifacts/media/KeyFrameAgent/image/step_3_e010202f_img_sh_004_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_008 in scene sc_003. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_008",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_072/_workspace/workspace_global_20260509_212514/artifacts/media/KeyFrameAgent/image/step_3_e010202f_img_sh_008_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_003 in scene sc_001. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_003",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_072/_workspace/workspace_global_20260509_212514/artifacts/media/KeyFrameAgent/image/step_3_e010202f_img_sh_003_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_005 in scene sc_002. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_005",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_072/_workspace/workspace_global_20260509_212514/artifacts/media/KeyFrameAgent/image/step_3_e010202f_img_sh_005_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Rendered starting frame for shot sh_009 in scene sc_003. To be animated into a video clip by an image-to-video generation step.",
        "scope": "shot:sh_009",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_072/_workspace/workspace_global_20260509_212514/artifacts/media/KeyFrameAgent/image/step_3_e010202f_img_sh_009_kf_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Keyframe planning document: 3 scene(s), 10 shot(s), with per-shot frame descriptions and motion hints. Consumed by a downstream image-to-video generation step.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_072/_workspace/workspace_global_20260509_212514/artifacts/KeyFrameAgent/step_3_e010202f_keyframeagent_exec_3.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_1_d1b76c1f",
    "agent_id": "VideoAgent",
    "step_id": "step_4_ae78fb63",
    "created_at": "2026-05-10T03:42:59.178599+00:00",
    "artifacts": [
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_001] Video clip bytes for shot sh_001. One segment of the final video.",
        "scope": "shot:sh_001",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_072/_workspace/workspace_global_20260509_212514/artifacts/media/VideoAgent/video/step_4_ae78fb63_clip_sh_001.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_002] Video clip bytes for shot sh_002. One segment of the final video.",
        "scope": "shot:sh_002",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_072/_workspace/workspace_global_20260509_212514/artifacts/media/VideoAgent/video/step_4_ae78fb63_clip_sh_002.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_003] Video clip bytes for shot sh_003. One segment of the final video.",
        "scope": "shot:sh_003",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_072/_workspace/workspace_global_20260509_212514/artifacts/media/VideoAgent/video/step_4_ae78fb63_clip_sh_003.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_004] Video clip bytes for shot sh_004. One segment of the final video.",
        "scope": "shot:sh_004",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_072/_workspace/workspace_global_20260509_212514/artifacts/media/VideoAgent/video/step_4_ae78fb63_clip_sh_004.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_005] Video clip bytes for shot sh_005. One segment of the final video.",
        "scope": "shot:sh_005",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_072/_workspace/workspace_global_20260509_212514/artifacts/media/VideoAgent/video/step_4_ae78fb63_clip_sh_005.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_006] Video clip bytes for shot sh_006. One segment of the final video.",
        "scope": "shot:sh_006",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_072/_workspace/workspace_global_20260509_212514/artifacts/media/VideoAgent/video/step_4_ae78fb63_clip_sh_006.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_007] Video clip bytes for shot sh_007. One segment of the final video.",
        "scope": "shot:sh_007",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_072/_workspace/workspace_global_20260509_212514/artifacts/media/VideoAgent/video/step_4_ae78fb63_clip_sh_007.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_008] Video clip bytes for shot sh_008. One segment of the final video.",
        "scope": "shot:sh_008",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_072/_workspace/workspace_global_20260509_212514/artifacts/media/VideoAgent/video/step_4_ae78fb63_clip_sh_008.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_009] Video clip bytes for shot sh_009. One segment of the final video.",
        "scope": "shot:sh_009",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_072/_workspace/workspace_global_20260509_212514/artifacts/media/VideoAgent/video/step_4_ae78fb63_clip_sh_009.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_010] Video clip bytes for shot sh_010. One segment of the final video.",
        "scope": "shot:sh_010",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_072/_workspace/workspace_global_20260509_212514/artifacts/media/VideoAgent/video/step_4_ae78fb63_clip_sh_010.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sc_001] Scene-cut bytes for scene sc_001 — all shots concatenated. Intermediate assembly, not final.",
        "scope": "scene:sc_001",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_072/_workspace/workspace_global_20260509_212514/artifacts/media/VideoAgent/video/step_4_ae78fb63_clip_sc_001.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sc_002] Scene-cut bytes for scene sc_002 — all shots concatenated. Intermediate assembly, not final.",
        "scope": "scene:sc_002",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_072/_workspace/workspace_global_20260509_212514/artifacts/media/VideoAgent/video/step_4_ae78fb63_clip_sc_002.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sc_003] Scene-cut bytes for scene sc_003 — all shots concatenated. Intermediate assembly, not final.",
        "scope": "scene:sc_003",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_072/_workspace/workspace_global_20260509_212514/artifacts/media/VideoAgent/video/step_4_ae78fb63_clip_sc_003.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_final] Complete assembled video bytes (10 shots). Final visual deliverable — consumed by a downstream audio-mix step's materializer via ffmpeg for audio extraction + muxing.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_072/_workspace/workspace_global_20260509_212514/artifacts/media/VideoAgent/video/step_4_ae78fb63_clip_final.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "[JSON MANIFEST] Video-assembly planning metadata: 3 scene(s), 10 shot clip(s) with timing. Read by a downstream audio-mix step's LLM for mix planning.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_072/_workspace/workspace_global_20260509_212514/artifacts/VideoAgent/step_4_ae78fb63_videoagent_exec_1.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_2_bf9cb428",
    "agent_id": "MusicAgent",
    "step_id": "step_5_ab79742a",
    "created_at": "2026-05-10T03:44:41.821764+00:00",
    "artifacts": [
      {
        "caption": "[BINARY WAV FILE · mime=audio/wav · sys_id aud_music_film] Background-music audio bytes for the film-wide BGM underlay. Consumed by the audio-mix materializer via ffmpeg.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_072/_workspace/workspace_global_20260509_212514/artifacts/media/MusicAgent/audio/step_5_ab79742a_aud_music_film.wav",
        "mime": "audio/wav"
      },
      {
        "caption": "[JSON MANIFEST] Background-music planning metadata: 1 cue(s) carrying the LLM-chosen mood for the film-wide BGM underlay. Read by the audio-mix LLM for mix planning.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_072/_workspace/workspace_global_20260509_212514/artifacts/MusicAgent/step_5_ab79742a_musicagent_exec_2.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_3_e06b2f31",
    "agent_id": "AmbienceAgent",
    "step_id": "step_6_e68290db",
    "created_at": "2026-05-10T03:45:23.063760+00:00",
    "artifacts": [
      {
        "caption": "[BINARY WAV FILE · mime=audio/wav · sys_id aud_amb_film] Ambient room-tone audio bytes for the film-wide atmospheric underlay. Consumed by the audio-mix materializer via ffmpeg.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_072/_workspace/workspace_global_20260509_212514/artifacts/media/AmbienceAgent/audio/step_6_e68290db_aud_amb_film.wav",
        "mime": "audio/wav"
      },
      {
        "caption": "[JSON MANIFEST] Ambience planning metadata: 1 bed(s) carrying the LLM-chosen description for the film-wide room-tone underlay. Read by the audio-mix LLM for mix planning.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_072/_workspace/workspace_global_20260509_212514/artifacts/AmbienceAgent/step_6_e68290db_ambienceagent_exec_3.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_4_8e20240e",
    "agent_id": "AudioMixAgent",
    "step_id": "step_7_e13fa18c",
    "created_at": "2026-05-10T03:45:35.316432+00:00",
    "artifacts": [
      {
        "caption": "[BINARY WAV FILE · mime=audio/wav · sys_id aud_final] Final-mix audio bytes — all source audio tracks (dialogue / foley / music / ambience / narrator) merged. Ready to be muxed onto the delivered video by a downstream compositing step.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_072/_workspace/workspace_global_20260509_212514/artifacts/media/AudioMixAgent/audio/step_7_e13fa18c_aud_final.wav",
        "mime": "audio/wav"
      },
      {
        "caption": "[JSON MANIFEST] Final-audio-mix envelope: amix of 3 source track(s) (video dialogue+foley + optional global music/ambience/narrator). Planning manifest only; the wav is a sibling artifact.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_072/_workspace/workspace_global_20260509_212514/artifacts/AudioMixAgent/step_7_e13fa18c_audiomixagent_exec_4.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_5_51c47166",
    "agent_id": "CompositorAgent",
    "step_id": "step_8_0bda4c5e",
    "created_at": "2026-05-10T03:45:51.281061+00:00",
    "artifacts": [
      {
        "caption": "Final delivered video binary (mp4) — the complete composited output with audio mix and (optional) subtitle burn-in. Terminal deliverable of the creative pipeline.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_072/_workspace/workspace_global_20260509_212514/artifacts/media/CompositorAgent/video/step_8_0bda4c5e_compositor_final.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "Final composited video (1920x1080): audio mix, subtitle burn-in. Ready for delivery.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/creative/cr_072/_workspace/workspace_global_20260509_212514/artifacts/CompositorAgent/step_8_0bda4c5e_compositoragent_exec_5.json",
        "mime": "application/json"
      }
    ]
  }
]
```
