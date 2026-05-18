# Global memory — `workspace_global_20260509_153139`

Per-execution record of every artifact persisted in this workspace. Each entry below is one agent execution; its `artifacts` array carries the natural-language `caption`, `scope`, absolute `path` and `mime` for every file that execution wrote.

`InputResolver` reads this index to match artifacts against each consumer agent's `[label]` slots. Execution history (including failures) lives in the assistant executions table, not here.

## Entries

```json
[
  {
    "execution_id": "brief_20260509_153139_656893",
    "agent_id": "user",
    "step_id": "",
    "created_at": "2026-05-09T15:31:39.658734+00:00",
    "artifacts": [
      {
        "caption": "Structured metadata document (JSON) for a user-submitted text brief. Payload carries the raw text verbatim. Pipeline entry point — consumed by story / screenplay / narration agents.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260509_153139/inputs/brief_20260509_153139_656893.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_1_505e7f21",
    "agent_id": "NarrationAgent",
    "step_id": "step_1_37c787ce",
    "created_at": "2026-05-09T15:32:40.952913+00:00",
    "artifacts": [
      {
        "caption": "Illustrated-storytelling narration script: 15 segment(s), 42 narrator line(s). Carries per-segment image_prompt + per-line TTS text + cross-segment art-style anchor. Consumed by an illustration image step and a narrator TTS step.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260509_153139/artifacts/NarrationAgent/step_1_37c787ce_narrationagent_exec_1.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_2_89ebae27",
    "agent_id": "IllustrationAgent",
    "step_id": "step_2_d7df2bc3",
    "created_at": "2026-05-09T15:34:08.524039+00:00",
    "artifacts": [
      {
        "caption": "",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260509_153139/artifacts/media/IllustrationAgent/image/step_2_d7df2bc3_illustration_anchor_char_001.png",
        "mime": "image/png"
      },
      {
        "caption": "",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260509_153139/artifacts/media/IllustrationAgent/image/step_2_d7df2bc3_illustration_anchor_char_002.png",
        "mime": "image/png"
      },
      {
        "caption": "Illustration image (png) for narration segment seg_001 (order 1/15). One frame of an illustrated-storytelling video; consumed by the compositor step as part of the image sequence that fills the video track.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260509_153139/artifacts/media/IllustrationAgent/image/step_2_d7df2bc3_illustration_seg_001.png",
        "mime": "image/png"
      },
      {
        "caption": "Illustration image (png) for narration segment seg_002 (order 2/15). One frame of an illustrated-storytelling video; consumed by the compositor step as part of the image sequence that fills the video track.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260509_153139/artifacts/media/IllustrationAgent/image/step_2_d7df2bc3_illustration_seg_002.png",
        "mime": "image/png"
      },
      {
        "caption": "Illustration image (png) for narration segment seg_003 (order 3/15). One frame of an illustrated-storytelling video; consumed by the compositor step as part of the image sequence that fills the video track.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260509_153139/artifacts/media/IllustrationAgent/image/step_2_d7df2bc3_illustration_seg_003.png",
        "mime": "image/png"
      },
      {
        "caption": "Illustration image (png) for narration segment seg_004 (order 4/15). One frame of an illustrated-storytelling video; consumed by the compositor step as part of the image sequence that fills the video track.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260509_153139/artifacts/media/IllustrationAgent/image/step_2_d7df2bc3_illustration_seg_004.png",
        "mime": "image/png"
      },
      {
        "caption": "Illustration image (png) for narration segment seg_005 (order 5/15). One frame of an illustrated-storytelling video; consumed by the compositor step as part of the image sequence that fills the video track.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260509_153139/artifacts/media/IllustrationAgent/image/step_2_d7df2bc3_illustration_seg_005.png",
        "mime": "image/png"
      },
      {
        "caption": "Illustration image (png) for narration segment seg_006 (order 6/15). One frame of an illustrated-storytelling video; consumed by the compositor step as part of the image sequence that fills the video track.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260509_153139/artifacts/media/IllustrationAgent/image/step_2_d7df2bc3_illustration_seg_006.png",
        "mime": "image/png"
      },
      {
        "caption": "Illustration image (png) for narration segment seg_007 (order 7/15). One frame of an illustrated-storytelling video; consumed by the compositor step as part of the image sequence that fills the video track.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260509_153139/artifacts/media/IllustrationAgent/image/step_2_d7df2bc3_illustration_seg_007.png",
        "mime": "image/png"
      },
      {
        "caption": "Illustration image (png) for narration segment seg_008 (order 8/15). One frame of an illustrated-storytelling video; consumed by the compositor step as part of the image sequence that fills the video track.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260509_153139/artifacts/media/IllustrationAgent/image/step_2_d7df2bc3_illustration_seg_008.png",
        "mime": "image/png"
      },
      {
        "caption": "Illustration image (png) for narration segment seg_009 (order 9/15). One frame of an illustrated-storytelling video; consumed by the compositor step as part of the image sequence that fills the video track.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260509_153139/artifacts/media/IllustrationAgent/image/step_2_d7df2bc3_illustration_seg_009.png",
        "mime": "image/png"
      },
      {
        "caption": "Illustration image (png) for narration segment seg_010 (order 10/15). One frame of an illustrated-storytelling video; consumed by the compositor step as part of the image sequence that fills the video track.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260509_153139/artifacts/media/IllustrationAgent/image/step_2_d7df2bc3_illustration_seg_010.png",
        "mime": "image/png"
      },
      {
        "caption": "Illustration image (png) for narration segment seg_011 (order 11/15). One frame of an illustrated-storytelling video; consumed by the compositor step as part of the image sequence that fills the video track.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260509_153139/artifacts/media/IllustrationAgent/image/step_2_d7df2bc3_illustration_seg_011.png",
        "mime": "image/png"
      },
      {
        "caption": "Illustration image (png) for narration segment seg_012 (order 12/15). One frame of an illustrated-storytelling video; consumed by the compositor step as part of the image sequence that fills the video track.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260509_153139/artifacts/media/IllustrationAgent/image/step_2_d7df2bc3_illustration_seg_012.png",
        "mime": "image/png"
      },
      {
        "caption": "Illustration image (png) for narration segment seg_013 (order 13/15). One frame of an illustrated-storytelling video; consumed by the compositor step as part of the image sequence that fills the video track.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260509_153139/artifacts/media/IllustrationAgent/image/step_2_d7df2bc3_illustration_seg_013.png",
        "mime": "image/png"
      },
      {
        "caption": "Illustration image (png) for narration segment seg_014 (order 14/15). One frame of an illustrated-storytelling video; consumed by the compositor step as part of the image sequence that fills the video track.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260509_153139/artifacts/media/IllustrationAgent/image/step_2_d7df2bc3_illustration_seg_014.png",
        "mime": "image/png"
      },
      {
        "caption": "Illustration image (png) for narration segment seg_015 (order 15/15). One frame of an illustrated-storytelling video; consumed by the compositor step as part of the image sequence that fills the video track.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260509_153139/artifacts/media/IllustrationAgent/image/step_2_d7df2bc3_illustration_seg_015.png",
        "mime": "image/png"
      },
      {
        "caption": "Illustration manifest (JSON): 15 image(s) aligned to narration segments. Consumed by the compositor step when assembling an illustrated-storytelling slideshow.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260509_153139/artifacts/IllustrationAgent/step_2_d7df2bc3_illustrationagent_exec_2.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_3_0a94cb76",
    "agent_id": "NarratorAgent",
    "step_id": "step_3_210cdc9d",
    "created_at": "2026-05-09T15:38:02.326825+00:00",
    "artifacts": [
      {
        "caption": "[BINARY WAV FILE · mime=audio/wav · sys_id aud_narrator_full] Narrator voiceover audio bytes (345.3s, language=es-MX). Concatenated TTS for an illustrated-storytelling video. Consumed by the audio-mix or compositor materializer.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260509_153139/artifacts/media/NarratorAgent/audio/step_3_210cdc9d_aud_narrator_full.wav",
        "mime": "audio/wav"
      },
      {
        "caption": "[JSON MANIFEST · SRT cues] Narrator subtitle track (language=es-MX): one cue per narration line, timed against the narrator audio. Consumed by the compositor step as a burn-in subtitle source.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260509_153139/artifacts/media/NarratorAgent/other/step_3_210cdc9d_narrator_srt.json",
        "mime": "application/json"
      },
      {
        "caption": "[JSON MANIFEST] Narrator per-segment timing: 15 segment(s) with start / end / duration seconds. Used by a slideshow compositor to set how long each illustration stays on screen.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260509_153139/artifacts/media/NarratorAgent/other/step_3_210cdc9d_narrator_segment_timing.json",
        "mime": "application/json"
      },
      {
        "caption": "[JSON MANIFEST] Narrator session manifest: 42 line(s), 15 segment(s), total 345.3s. Per-line / per-segment timing. Dev/debug view; downstream consumption goes through the sibling audio / srt / timing artifacts.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260509_153139/artifacts/NarratorAgent/step_3_210cdc9d_narratoragent_exec_3.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_4_7be69da3",
    "agent_id": "MusicAgent",
    "step_id": "step_4_0b41fe14",
    "created_at": "2026-05-09T15:38:51.600446+00:00",
    "artifacts": [
      {
        "caption": "[BINARY WAV FILE · mime=audio/wav · sys_id aud_music_film] Background-music audio bytes for the film-wide BGM underlay. Consumed by the audio-mix materializer via ffmpeg.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260509_153139/artifacts/media/MusicAgent/audio/step_4_0b41fe14_aud_music_film.wav",
        "mime": "audio/wav"
      },
      {
        "caption": "[JSON MANIFEST] Background-music planning metadata: 1 cue(s) carrying the LLM-chosen mood for the film-wide BGM underlay. Read by the audio-mix LLM for mix planning.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260509_153139/artifacts/MusicAgent/step_4_0b41fe14_musicagent_exec_4.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_5_eb1d16df",
    "agent_id": "AmbienceAgent",
    "step_id": "step_5_c111fc13",
    "created_at": "2026-05-09T15:39:35.603757+00:00",
    "artifacts": [
      {
        "caption": "[BINARY WAV FILE · mime=audio/wav · sys_id aud_amb_film] Ambient room-tone audio bytes for the film-wide atmospheric underlay. Consumed by the audio-mix materializer via ffmpeg.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260509_153139/artifacts/media/AmbienceAgent/audio/step_5_c111fc13_aud_amb_film.wav",
        "mime": "audio/wav"
      },
      {
        "caption": "[JSON MANIFEST] Ambience planning metadata: 1 bed(s) carrying the LLM-chosen description for the film-wide room-tone underlay. Read by the audio-mix LLM for mix planning.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260509_153139/artifacts/AmbienceAgent/step_5_c111fc13_ambienceagent_exec_5.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_6_68974f1e",
    "agent_id": "TranslationAgent",
    "step_id": "step_6_5234b27f",
    "created_at": "2026-05-09T15:39:52.008588+00:00",
    "artifacts": [
      {
        "caption": "Translation (en → en). Full structured text translated with original structure preserved (keys / ids / timing / ordering). Output shape mirrors input shape — a translated SRT remains an SRT, a translated screenplay remains a screenplay.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260509_153139/artifacts/TranslationAgent/step_6_5234b27f_translationagent_exec_6.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_7_4f6123f5",
    "agent_id": "AudioMixAgent",
    "step_id": "step_7_40c11d13",
    "created_at": "2026-05-09T15:40:26.014884+00:00",
    "artifacts": [
      {
        "caption": "[BINARY WAV FILE · mime=audio/wav · sys_id aud_final] Final-mix audio bytes — all source audio tracks (dialogue / foley / music / ambience / narrator) merged. Ready to be muxed onto the delivered video by a downstream compositing step.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260509_153139/artifacts/media/AudioMixAgent/audio/step_7_40c11d13_aud_final.wav",
        "mime": "audio/wav"
      },
      {
        "caption": "[JSON MANIFEST] Final-audio-mix envelope: amix of 3 source track(s) (video dialogue+foley + optional global music/ambience/narrator). Planning manifest only; the wav is a sibling artifact.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260509_153139/artifacts/AudioMixAgent/step_7_40c11d13_audiomixagent_exec_7.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_8_97309020",
    "agent_id": "CompositorAgent",
    "step_id": "step_8_1aa3b00c",
    "created_at": "2026-05-09T15:42:07.946150+00:00",
    "artifacts": [
      {
        "caption": "Final delivered video binary (mp4) — the complete composited output with audio mix and (optional) subtitle burn-in. Terminal deliverable of the creative pipeline.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260509_153139/artifacts/media/CompositorAgent/video/step_8_1aa3b00c_compositor_final.mp4",
        "mime": "video/mp4"
      },
      {
        "caption": "Final composited video (1920x1080): audio mix, subtitle burn-in. Ready for delivery.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260509_153139/artifacts/CompositorAgent/step_8_1aa3b00c_compositoragent_exec_8.json",
        "mime": "application/json"
      }
    ]
  }
]
```
