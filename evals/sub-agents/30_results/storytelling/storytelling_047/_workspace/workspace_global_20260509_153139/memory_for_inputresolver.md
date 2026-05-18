# InputResolver view — `workspace_global_20260509_153139`

This file is auto-generated every time global_memory changes.
It shows exactly what InputResolver's LLM receives as the artifact registry. The LLM returns #N ids; the path mapping below resolves them.

---

#0  Structured metadata document (JSON) for a user-submitted text brief. Payload carries the raw text verbatim. Pipeline entry point — consumed by story / screenplay / narration agents. Produced by user on 2026-05-09 15:31.

#1  Illustrated-storytelling narration script: 15 segment(s), 42 narrator line(s). Carries per-segment image_prompt + per-line TTS text + cross-segment art-style anchor. Consumed by an illustration image step and a narrator TTS step. Produced by NarrationAgent on 2026-05-09 15:32.

#2  (no caption) Produced by IllustrationAgent on 2026-05-09 15:34.

#3  (no caption) Produced by IllustrationAgent on 2026-05-09 15:34.

#4  Illustration image (png) for narration segment seg_001 (order 1/15). One frame of an illustrated-storytelling video; consumed by the compositor step as part of the image sequence that fills the video track. Produced by IllustrationAgent on 2026-05-09 15:34.

#5  Illustration image (png) for narration segment seg_002 (order 2/15). One frame of an illustrated-storytelling video; consumed by the compositor step as part of the image sequence that fills the video track. Produced by IllustrationAgent on 2026-05-09 15:34.

#6  Illustration image (png) for narration segment seg_003 (order 3/15). One frame of an illustrated-storytelling video; consumed by the compositor step as part of the image sequence that fills the video track. Produced by IllustrationAgent on 2026-05-09 15:34.

#7  Illustration image (png) for narration segment seg_004 (order 4/15). One frame of an illustrated-storytelling video; consumed by the compositor step as part of the image sequence that fills the video track. Produced by IllustrationAgent on 2026-05-09 15:34.

#8  Illustration image (png) for narration segment seg_005 (order 5/15). One frame of an illustrated-storytelling video; consumed by the compositor step as part of the image sequence that fills the video track. Produced by IllustrationAgent on 2026-05-09 15:34.

#9  Illustration image (png) for narration segment seg_006 (order 6/15). One frame of an illustrated-storytelling video; consumed by the compositor step as part of the image sequence that fills the video track. Produced by IllustrationAgent on 2026-05-09 15:34.

#10  Illustration image (png) for narration segment seg_007 (order 7/15). One frame of an illustrated-storytelling video; consumed by the compositor step as part of the image sequence that fills the video track. Produced by IllustrationAgent on 2026-05-09 15:34.

#11  Illustration image (png) for narration segment seg_008 (order 8/15). One frame of an illustrated-storytelling video; consumed by the compositor step as part of the image sequence that fills the video track. Produced by IllustrationAgent on 2026-05-09 15:34.

#12  Illustration image (png) for narration segment seg_009 (order 9/15). One frame of an illustrated-storytelling video; consumed by the compositor step as part of the image sequence that fills the video track. Produced by IllustrationAgent on 2026-05-09 15:34.

#13  Illustration image (png) for narration segment seg_010 (order 10/15). One frame of an illustrated-storytelling video; consumed by the compositor step as part of the image sequence that fills the video track. Produced by IllustrationAgent on 2026-05-09 15:34.

#14  Illustration image (png) for narration segment seg_011 (order 11/15). One frame of an illustrated-storytelling video; consumed by the compositor step as part of the image sequence that fills the video track. Produced by IllustrationAgent on 2026-05-09 15:34.

#15  Illustration image (png) for narration segment seg_012 (order 12/15). One frame of an illustrated-storytelling video; consumed by the compositor step as part of the image sequence that fills the video track. Produced by IllustrationAgent on 2026-05-09 15:34.

#16  Illustration image (png) for narration segment seg_013 (order 13/15). One frame of an illustrated-storytelling video; consumed by the compositor step as part of the image sequence that fills the video track. Produced by IllustrationAgent on 2026-05-09 15:34.

#17  Illustration image (png) for narration segment seg_014 (order 14/15). One frame of an illustrated-storytelling video; consumed by the compositor step as part of the image sequence that fills the video track. Produced by IllustrationAgent on 2026-05-09 15:34.

#18  Illustration image (png) for narration segment seg_015 (order 15/15). One frame of an illustrated-storytelling video; consumed by the compositor step as part of the image sequence that fills the video track. Produced by IllustrationAgent on 2026-05-09 15:34.

#19  Illustration manifest (JSON): 15 image(s) aligned to narration segments. Consumed by the compositor step when assembling an illustrated-storytelling slideshow. Produced by IllustrationAgent on 2026-05-09 15:34.

#20  [BINARY WAV FILE · mime=audio/wav · sys_id aud_narrator_full] Narrator voiceover audio bytes (345.3s, language=es-MX). Concatenated TTS for an illustrated-storytelling video. Consumed by the audio-mix or compositor materializer. Produced by NarratorAgent on 2026-05-09 15:38.

#21  [JSON MANIFEST · SRT cues] Narrator subtitle track (language=es-MX): one cue per narration line, timed against the narrator audio. Consumed by the compositor step as a burn-in subtitle source. Produced by NarratorAgent on 2026-05-09 15:38.

#22  [JSON MANIFEST] Narrator per-segment timing: 15 segment(s) with start / end / duration seconds. Used by a slideshow compositor to set how long each illustration stays on screen. Produced by NarratorAgent on 2026-05-09 15:38.

#23  [JSON MANIFEST] Narrator session manifest: 42 line(s), 15 segment(s), total 345.3s. Per-line / per-segment timing. Dev/debug view; downstream consumption goes through the sibling audio / srt / timing artifacts. Produced by NarratorAgent on 2026-05-09 15:38.

#24  [BINARY WAV FILE · mime=audio/wav · sys_id aud_music_film] Background-music audio bytes for the film-wide BGM underlay. Consumed by the audio-mix materializer via ffmpeg. Produced by MusicAgent on 2026-05-09 15:38.

#25  [JSON MANIFEST] Background-music planning metadata: 1 cue(s) carrying the LLM-chosen mood for the film-wide BGM underlay. Read by the audio-mix LLM for mix planning. Produced by MusicAgent on 2026-05-09 15:38.

#26  [BINARY WAV FILE · mime=audio/wav · sys_id aud_amb_film] Ambient room-tone audio bytes for the film-wide atmospheric underlay. Consumed by the audio-mix materializer via ffmpeg. Produced by AmbienceAgent on 2026-05-09 15:39.

#27  [JSON MANIFEST] Ambience planning metadata: 1 bed(s) carrying the LLM-chosen description for the film-wide room-tone underlay. Read by the audio-mix LLM for mix planning. Produced by AmbienceAgent on 2026-05-09 15:39.

#28  Translation (en → en). Full structured text translated with original structure preserved (keys / ids / timing / ordering). Output shape mirrors input shape — a translated SRT remains an SRT, a translated screenplay remains a screenplay. Produced by TranslationAgent on 2026-05-09 15:39.

#29  [BINARY WAV FILE · mime=audio/wav · sys_id aud_final] Final-mix audio bytes — all source audio tracks (dialogue / foley / music / ambience / narrator) merged. Ready to be muxed onto the delivered video by a downstream compositing step. Produced by AudioMixAgent on 2026-05-09 15:40.

#30  [JSON MANIFEST] Final-audio-mix envelope: amix of 3 source track(s) (video dialogue+foley + optional global music/ambience/narrator). Planning manifest only; the wav is a sibling artifact. Produced by AudioMixAgent on 2026-05-09 15:40.

#31  Final delivered video binary (mp4) — the complete composited output with audio mix and (optional) subtitle burn-in. Terminal deliverable of the creative pipeline. Produced by CompositorAgent on 2026-05-09 15:42.

#32  Final composited video (1920x1080): audio mix, subtitle burn-in. Ready for delivery. Produced by CompositorAgent on 2026-05-09 15:42.

---

## Path mapping

#0 → /home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260509_153139/inputs/brief_20260509_153139_656893.json
#1 → /home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260509_153139/artifacts/NarrationAgent/step_1_37c787ce_narrationagent_exec_1.json
#2 → /home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260509_153139/artifacts/media/IllustrationAgent/image/step_2_d7df2bc3_illustration_anchor_char_001.png
#3 → /home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260509_153139/artifacts/media/IllustrationAgent/image/step_2_d7df2bc3_illustration_anchor_char_002.png
#4 → /home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260509_153139/artifacts/media/IllustrationAgent/image/step_2_d7df2bc3_illustration_seg_001.png
#5 → /home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260509_153139/artifacts/media/IllustrationAgent/image/step_2_d7df2bc3_illustration_seg_002.png
#6 → /home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260509_153139/artifacts/media/IllustrationAgent/image/step_2_d7df2bc3_illustration_seg_003.png
#7 → /home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260509_153139/artifacts/media/IllustrationAgent/image/step_2_d7df2bc3_illustration_seg_004.png
#8 → /home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260509_153139/artifacts/media/IllustrationAgent/image/step_2_d7df2bc3_illustration_seg_005.png
#9 → /home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260509_153139/artifacts/media/IllustrationAgent/image/step_2_d7df2bc3_illustration_seg_006.png
#10 → /home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260509_153139/artifacts/media/IllustrationAgent/image/step_2_d7df2bc3_illustration_seg_007.png
#11 → /home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260509_153139/artifacts/media/IllustrationAgent/image/step_2_d7df2bc3_illustration_seg_008.png
#12 → /home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260509_153139/artifacts/media/IllustrationAgent/image/step_2_d7df2bc3_illustration_seg_009.png
#13 → /home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260509_153139/artifacts/media/IllustrationAgent/image/step_2_d7df2bc3_illustration_seg_010.png
#14 → /home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260509_153139/artifacts/media/IllustrationAgent/image/step_2_d7df2bc3_illustration_seg_011.png
#15 → /home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260509_153139/artifacts/media/IllustrationAgent/image/step_2_d7df2bc3_illustration_seg_012.png
#16 → /home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260509_153139/artifacts/media/IllustrationAgent/image/step_2_d7df2bc3_illustration_seg_013.png
#17 → /home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260509_153139/artifacts/media/IllustrationAgent/image/step_2_d7df2bc3_illustration_seg_014.png
#18 → /home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260509_153139/artifacts/media/IllustrationAgent/image/step_2_d7df2bc3_illustration_seg_015.png
#19 → /home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260509_153139/artifacts/IllustrationAgent/step_2_d7df2bc3_illustrationagent_exec_2.json
#20 → /home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260509_153139/artifacts/media/NarratorAgent/audio/step_3_210cdc9d_aud_narrator_full.wav
#21 → /home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260509_153139/artifacts/media/NarratorAgent/other/step_3_210cdc9d_narrator_srt.json
#22 → /home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260509_153139/artifacts/media/NarratorAgent/other/step_3_210cdc9d_narrator_segment_timing.json
#23 → /home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260509_153139/artifacts/NarratorAgent/step_3_210cdc9d_narratoragent_exec_3.json
#24 → /home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260509_153139/artifacts/media/MusicAgent/audio/step_4_0b41fe14_aud_music_film.wav
#25 → /home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260509_153139/artifacts/MusicAgent/step_4_0b41fe14_musicagent_exec_4.json
#26 → /home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260509_153139/artifacts/media/AmbienceAgent/audio/step_5_c111fc13_aud_amb_film.wav
#27 → /home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260509_153139/artifacts/AmbienceAgent/step_5_c111fc13_ambienceagent_exec_5.json
#28 → /home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260509_153139/artifacts/TranslationAgent/step_6_5234b27f_translationagent_exec_6.json
#29 → /home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260509_153139/artifacts/media/AudioMixAgent/audio/step_7_40c11d13_aud_final.wav
#30 → /home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260509_153139/artifacts/AudioMixAgent/step_7_40c11d13_audiomixagent_exec_7.json
#31 → /home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260509_153139/artifacts/media/CompositorAgent/video/step_8_1aa3b00c_compositor_final.mp4
#32 → /home/zhendong_li/FrameWorkers/_workspaces/workspace_global_20260509_153139/artifacts/CompositorAgent/step_8_1aa3b00c_compositoragent_exec_8.json
