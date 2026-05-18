# InputResolver view — `workspace_global_20260510_040416`

This file is auto-generated every time global_memory changes.
It shows exactly what InputResolver's LLM receives as the artifact registry. The LLM returns #N ids; the path mapping below resolves them.

---

#0  Global character reference image. Visual identity anchor for downstream keyframe generation. Produced by user on 2026-05-10 04:04.

#1  Structured metadata document (JSON) for a user-submitted text brief. Payload carries the raw text verbatim. Pipeline entry point — consumed by story / screenplay / narration agents. Produced by user on 2026-05-10 04:04.

#2  Structured metadata document (JSON) for a user-uploaded image. Payload carries the visual description and image-asset metadata. Produced by IntakeImageAgent on 2026-05-10 04:04.

#3  Enriched creative brief with visual reference descriptions integrated. Supersedes the raw user brief for story generation — contains the user's original concept plus detailed visual descriptions of uploaded reference images. Produced by BriefEnricherAgent on 2026-05-10 04:04.

#4  Story blueprint: 3 scene(s), 2 character(s). Structured input for screenplay generation. Produced by StoryAgent on 2026-05-10 04:05.

#5  Screenplay: 3 scene(s), 12 shot(s). Input for keyframe planning and audio scoring. Produced by ScreenplayAgent on 2026-05-10 04:06.

#6  Global character reference image for char_001. Visual identity anchor — not a video frame. Produced by KeyFrameAgent on 2026-05-10 04:07.

#7  Global character reference image for char_002. Visual identity anchor — not a video frame. Produced by KeyFrameAgent on 2026-05-10 04:07.

#8  Global prop reference image for prop_001. Visual identity anchor — not a video frame. Produced by KeyFrameAgent on 2026-05-10 04:07.

#9  Global location reference image for loc_001. Visual identity anchor — not a video frame. Produced by KeyFrameAgent on 2026-05-10 04:07.

#10  Global location reference image for loc_002. Visual identity anchor — not a video frame. Produced by KeyFrameAgent on 2026-05-10 04:07.

#11  Scene-level character reference for char_001 in scene sc_001. Intermediate consistency rendering — not a video frame. Produced by KeyFrameAgent on 2026-05-10 04:07.

#12  Scene-level character reference for char_002 in scene sc_003. Intermediate consistency rendering — not a video frame. Produced by KeyFrameAgent on 2026-05-10 04:07.

#13  Scene-level character reference for char_002 in scene sc_001. Intermediate consistency rendering — not a video frame. Produced by KeyFrameAgent on 2026-05-10 04:07.

#14  Scene-level character reference for char_001 in scene sc_003. Intermediate consistency rendering — not a video frame. Produced by KeyFrameAgent on 2026-05-10 04:07.

#15  Scene-level location reference for loc_001 in scene sc_003. Intermediate consistency rendering — not a video frame. Produced by KeyFrameAgent on 2026-05-10 04:07.

#16  Scene-level location reference for loc_001 in scene sc_002. Intermediate consistency rendering — not a video frame. Produced by KeyFrameAgent on 2026-05-10 04:07.

#17  Scene-level prop reference for prop_001 in scene sc_003. Intermediate consistency rendering — not a video frame. Produced by KeyFrameAgent on 2026-05-10 04:07.

#18  Scene-level character reference for char_001 in scene sc_002. Intermediate consistency rendering — not a video frame. Produced by KeyFrameAgent on 2026-05-10 04:07.

#19  Scene-level location reference for loc_002 in scene sc_001. Intermediate consistency rendering — not a video frame. Produced by KeyFrameAgent on 2026-05-10 04:07.

#20  Scene-level character reference for char_002 in scene sc_002. Intermediate consistency rendering — not a video frame. Produced by KeyFrameAgent on 2026-05-10 04:07.

#21  Rendered starting frame for shot sh_005 in scene sc_002. To be animated into a video clip by an image-to-video generation step. Produced by KeyFrameAgent on 2026-05-10 04:07.

#22  Rendered starting frame for shot sh_002 in scene sc_001. To be animated into a video clip by an image-to-video generation step. Produced by KeyFrameAgent on 2026-05-10 04:07.

#23  Rendered starting frame for shot sh_004 in scene sc_001. To be animated into a video clip by an image-to-video generation step. Produced by KeyFrameAgent on 2026-05-10 04:07.

#24  Rendered starting frame for shot sh_010 in scene sc_003. To be animated into a video clip by an image-to-video generation step. Produced by KeyFrameAgent on 2026-05-10 04:07.

#25  Rendered starting frame for shot sh_011 in scene sc_003. To be animated into a video clip by an image-to-video generation step. Produced by KeyFrameAgent on 2026-05-10 04:07.

#26  Rendered starting frame for shot sh_003 in scene sc_001. To be animated into a video clip by an image-to-video generation step. Produced by KeyFrameAgent on 2026-05-10 04:07.

#27  Rendered starting frame for shot sh_007 in scene sc_002. To be animated into a video clip by an image-to-video generation step. Produced by KeyFrameAgent on 2026-05-10 04:07.

#28  Rendered starting frame for shot sh_012 in scene sc_003. To be animated into a video clip by an image-to-video generation step. Produced by KeyFrameAgent on 2026-05-10 04:07.

#29  Rendered starting frame for shot sh_008 in scene sc_002. To be animated into a video clip by an image-to-video generation step. Produced by KeyFrameAgent on 2026-05-10 04:07.

#30  Rendered starting frame for shot sh_006 in scene sc_002. To be animated into a video clip by an image-to-video generation step. Produced by KeyFrameAgent on 2026-05-10 04:07.

#31  Rendered starting frame for shot sh_001 in scene sc_001. To be animated into a video clip by an image-to-video generation step. Produced by KeyFrameAgent on 2026-05-10 04:07.

#32  Rendered starting frame for shot sh_009 in scene sc_003. To be animated into a video clip by an image-to-video generation step. Produced by KeyFrameAgent on 2026-05-10 04:07.

#33  Keyframe planning document: 3 scene(s), 12 shot(s), with per-shot frame descriptions and motion hints. Consumed by a downstream image-to-video generation step. Produced by KeyFrameAgent on 2026-05-10 04:07.

#34  [BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_001] Video clip bytes for shot sh_001. One segment of the final video. Produced by VideoAgent on 2026-05-10 08:48.

#35  [BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_002] Video clip bytes for shot sh_002. One segment of the final video. Produced by VideoAgent on 2026-05-10 08:48.

#36  [BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_003] Video clip bytes for shot sh_003. One segment of the final video. Produced by VideoAgent on 2026-05-10 08:48.

#37  [BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_004] Video clip bytes for shot sh_004. One segment of the final video. Produced by VideoAgent on 2026-05-10 08:48.

#38  [BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_005] Video clip bytes for shot sh_005. One segment of the final video. Produced by VideoAgent on 2026-05-10 08:48.

#39  [BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_006] Video clip bytes for shot sh_006. One segment of the final video. Produced by VideoAgent on 2026-05-10 08:48.

#40  [BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_007] Video clip bytes for shot sh_007. One segment of the final video. Produced by VideoAgent on 2026-05-10 08:48.

#41  [BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_008] Video clip bytes for shot sh_008. One segment of the final video. Produced by VideoAgent on 2026-05-10 08:48.

#42  [BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_009] Video clip bytes for shot sh_009. One segment of the final video. Produced by VideoAgent on 2026-05-10 08:48.

#43  [BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_010] Video clip bytes for shot sh_010. One segment of the final video. Produced by VideoAgent on 2026-05-10 08:48.

#44  [BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_011] Video clip bytes for shot sh_011. One segment of the final video. Produced by VideoAgent on 2026-05-10 08:48.

#45  [BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sh_012] Video clip bytes for shot sh_012. One segment of the final video. Produced by VideoAgent on 2026-05-10 08:48.

#46  [BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sc_001] Scene-cut bytes for scene sc_001 — all shots concatenated. Intermediate assembly, not final. Produced by VideoAgent on 2026-05-10 08:48.

#47  [BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sc_002] Scene-cut bytes for scene sc_002 — all shots concatenated. Intermediate assembly, not final. Produced by VideoAgent on 2026-05-10 08:48.

#48  [BINARY MP4 FILE · mime=video/mp4 · sys_id clip_sc_003] Scene-cut bytes for scene sc_003 — all shots concatenated. Intermediate assembly, not final. Produced by VideoAgent on 2026-05-10 08:48.

#49  [BINARY MP4 FILE · mime=video/mp4 · sys_id clip_final] Complete assembled video bytes (12 shots). Final visual deliverable — consumed by a downstream audio-mix step's materializer via ffmpeg for audio extraction + muxing. Produced by VideoAgent on 2026-05-10 08:48.

#50  [JSON MANIFEST] Video-assembly planning metadata: 3 scene(s), 12 shot clip(s) with timing. Read by a downstream audio-mix step's LLM for mix planning. Produced by VideoAgent on 2026-05-10 08:48.

#51  [BINARY WAV FILE · mime=audio/wav · sys_id aud_music_film] Background-music audio bytes for the film-wide BGM underlay. Consumed by the audio-mix materializer via ffmpeg. Produced by MusicAgent on 2026-05-10 08:50.

#52  [JSON MANIFEST] Background-music planning metadata: 1 cue(s) carrying the LLM-chosen mood for the film-wide BGM underlay. Read by the audio-mix LLM for mix planning. Produced by MusicAgent on 2026-05-10 08:50.

#53  [BINARY WAV FILE · mime=audio/wav · sys_id aud_final] Final-mix audio bytes — all source audio tracks (dialogue / foley / music / ambience / narrator) merged. Ready to be muxed onto the delivered video by a downstream compositing step. Produced by AudioMixAgent on 2026-05-10 08:50.

#54  [JSON MANIFEST] Final-audio-mix envelope: amix of 3 source track(s) (video dialogue+foley + optional global music/ambience/narrator). Planning manifest only; the wav is a sibling artifact. Produced by AudioMixAgent on 2026-05-10 08:50.

#55  Final delivered video binary (mp4) — the complete composited output with audio mix and (optional) subtitle burn-in. Terminal deliverable of the creative pipeline. Produced by CompositorAgent on 2026-05-10 08:51.

#56  Final composited video (1920x1080): audio mix, subtitle burn-in. Ready for delivery. Produced by CompositorAgent on 2026-05-10 08:51.

---

## Path mapping

#0 → /home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_046/_workspace/workspace_global_20260510_040416/inputs/20260510_040418_637086_intake_img_046.png
#1 → /home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_046/_workspace/workspace_global_20260510_040416/inputs/brief_20260510_040418_650554.json
#2 → /home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_046/_workspace/workspace_global_20260510_040416/artifacts/IntakeImageAgent/step_1_a5d8fc92_intakeimageagent_exec_1.json
#3 → /home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_046/_workspace/workspace_global_20260510_040416/artifacts/BriefEnricherAgent/step_2_5658b432_briefenricheragent_exec_2.json
#4 → /home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_046/_workspace/workspace_global_20260510_040416/artifacts/StoryAgent/step_3_ce2fea0e_storyagent_exec_3.json
#5 → /home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_046/_workspace/workspace_global_20260510_040416/artifacts/ScreenplayAgent/step_4_5d058665_screenplayagent_exec_4.json
#6 → /home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_046/_workspace/workspace_global_20260510_040416/artifacts/media/KeyFrameAgent/image/step_5_51aa18a2_img_char_001_global.png
#7 → /home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_046/_workspace/workspace_global_20260510_040416/artifacts/media/KeyFrameAgent/image/step_5_51aa18a2_img_char_002_global.png
#8 → /home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_046/_workspace/workspace_global_20260510_040416/artifacts/media/KeyFrameAgent/image/step_5_51aa18a2_img_prop_001_global.png
#9 → /home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_046/_workspace/workspace_global_20260510_040416/artifacts/media/KeyFrameAgent/image/step_5_51aa18a2_img_loc_001_global.png
#10 → /home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_046/_workspace/workspace_global_20260510_040416/artifacts/media/KeyFrameAgent/image/step_5_51aa18a2_img_loc_002_global.png
#11 → /home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_046/_workspace/workspace_global_20260510_040416/artifacts/media/KeyFrameAgent/image/step_5_51aa18a2_img_char_001_sc_001.png
#12 → /home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_046/_workspace/workspace_global_20260510_040416/artifacts/media/KeyFrameAgent/image/step_5_51aa18a2_img_char_002_sc_003.png
#13 → /home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_046/_workspace/workspace_global_20260510_040416/artifacts/media/KeyFrameAgent/image/step_5_51aa18a2_img_char_002_sc_001.png
#14 → /home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_046/_workspace/workspace_global_20260510_040416/artifacts/media/KeyFrameAgent/image/step_5_51aa18a2_img_char_001_sc_003.png
#15 → /home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_046/_workspace/workspace_global_20260510_040416/artifacts/media/KeyFrameAgent/image/step_5_51aa18a2_img_loc_001_sc_003.png
#16 → /home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_046/_workspace/workspace_global_20260510_040416/artifacts/media/KeyFrameAgent/image/step_5_51aa18a2_img_loc_001_sc_002.png
#17 → /home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_046/_workspace/workspace_global_20260510_040416/artifacts/media/KeyFrameAgent/image/step_5_51aa18a2_img_prop_001_sc_003.png
#18 → /home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_046/_workspace/workspace_global_20260510_040416/artifacts/media/KeyFrameAgent/image/step_5_51aa18a2_img_char_001_sc_002.png
#19 → /home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_046/_workspace/workspace_global_20260510_040416/artifacts/media/KeyFrameAgent/image/step_5_51aa18a2_img_loc_002_sc_001.png
#20 → /home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_046/_workspace/workspace_global_20260510_040416/artifacts/media/KeyFrameAgent/image/step_5_51aa18a2_img_char_002_sc_002.png
#21 → /home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_046/_workspace/workspace_global_20260510_040416/artifacts/media/KeyFrameAgent/image/step_5_51aa18a2_img_sh_005_kf_001.png
#22 → /home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_046/_workspace/workspace_global_20260510_040416/artifacts/media/KeyFrameAgent/image/step_5_51aa18a2_img_sh_002_kf_001.png
#23 → /home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_046/_workspace/workspace_global_20260510_040416/artifacts/media/KeyFrameAgent/image/step_5_51aa18a2_img_sh_004_kf_001.png
#24 → /home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_046/_workspace/workspace_global_20260510_040416/artifacts/media/KeyFrameAgent/image/step_5_51aa18a2_img_sh_010_kf_001.png
#25 → /home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_046/_workspace/workspace_global_20260510_040416/artifacts/media/KeyFrameAgent/image/step_5_51aa18a2_img_sh_011_kf_001.png
#26 → /home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_046/_workspace/workspace_global_20260510_040416/artifacts/media/KeyFrameAgent/image/step_5_51aa18a2_img_sh_003_kf_001.png
#27 → /home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_046/_workspace/workspace_global_20260510_040416/artifacts/media/KeyFrameAgent/image/step_5_51aa18a2_img_sh_007_kf_001.png
#28 → /home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_046/_workspace/workspace_global_20260510_040416/artifacts/media/KeyFrameAgent/image/step_5_51aa18a2_img_sh_012_kf_001.png
#29 → /home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_046/_workspace/workspace_global_20260510_040416/artifacts/media/KeyFrameAgent/image/step_5_51aa18a2_img_sh_008_kf_001.png
#30 → /home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_046/_workspace/workspace_global_20260510_040416/artifacts/media/KeyFrameAgent/image/step_5_51aa18a2_img_sh_006_kf_001.png
#31 → /home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_046/_workspace/workspace_global_20260510_040416/artifacts/media/KeyFrameAgent/image/step_5_51aa18a2_img_sh_001_kf_001.png
#32 → /home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_046/_workspace/workspace_global_20260510_040416/artifacts/media/KeyFrameAgent/image/step_5_51aa18a2_img_sh_009_kf_001.png
#33 → /home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_046/_workspace/workspace_global_20260510_040416/artifacts/KeyFrameAgent/step_5_51aa18a2_keyframeagent_exec_5.json
#34 → /home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_046/_workspace/workspace_global_20260510_040416/artifacts/media/VideoAgent/video/step_6_d34104ae_clip_sh_001.mp4
#35 → /home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_046/_workspace/workspace_global_20260510_040416/artifacts/media/VideoAgent/video/step_6_d34104ae_clip_sh_002.mp4
#36 → /home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_046/_workspace/workspace_global_20260510_040416/artifacts/media/VideoAgent/video/step_6_d34104ae_clip_sh_003.mp4
#37 → /home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_046/_workspace/workspace_global_20260510_040416/artifacts/media/VideoAgent/video/step_6_d34104ae_clip_sh_004.mp4
#38 → /home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_046/_workspace/workspace_global_20260510_040416/artifacts/media/VideoAgent/video/step_6_d34104ae_clip_sh_005.mp4
#39 → /home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_046/_workspace/workspace_global_20260510_040416/artifacts/media/VideoAgent/video/step_6_d34104ae_clip_sh_006.mp4
#40 → /home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_046/_workspace/workspace_global_20260510_040416/artifacts/media/VideoAgent/video/step_6_d34104ae_clip_sh_007.mp4
#41 → /home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_046/_workspace/workspace_global_20260510_040416/artifacts/media/VideoAgent/video/step_6_d34104ae_clip_sh_008.mp4
#42 → /home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_046/_workspace/workspace_global_20260510_040416/artifacts/media/VideoAgent/video/step_6_d34104ae_clip_sh_009.mp4
#43 → /home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_046/_workspace/workspace_global_20260510_040416/artifacts/media/VideoAgent/video/step_6_d34104ae_clip_sh_010.mp4
#44 → /home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_046/_workspace/workspace_global_20260510_040416/artifacts/media/VideoAgent/video/step_6_d34104ae_clip_sh_011.mp4
#45 → /home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_046/_workspace/workspace_global_20260510_040416/artifacts/media/VideoAgent/video/step_6_d34104ae_clip_sh_012.mp4
#46 → /home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_046/_workspace/workspace_global_20260510_040416/artifacts/media/VideoAgent/video/step_6_d34104ae_clip_sc_001.mp4
#47 → /home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_046/_workspace/workspace_global_20260510_040416/artifacts/media/VideoAgent/video/step_6_d34104ae_clip_sc_002.mp4
#48 → /home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_046/_workspace/workspace_global_20260510_040416/artifacts/media/VideoAgent/video/step_6_d34104ae_clip_sc_003.mp4
#49 → /home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_046/_workspace/workspace_global_20260510_040416/artifacts/media/VideoAgent/video/step_6_d34104ae_clip_final.mp4
#50 → /home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_046/_workspace/workspace_global_20260510_040416/artifacts/VideoAgent/step_6_d34104ae_videoagent_exec_6.json
#51 → /home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_046/_workspace/workspace_global_20260510_040416/artifacts/media/MusicAgent/audio/step_7_4d8e6829_aud_music_film.wav
#52 → /home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_046/_workspace/workspace_global_20260510_040416/artifacts/MusicAgent/step_7_4d8e6829_musicagent_exec_7.json
#53 → /home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_046/_workspace/workspace_global_20260510_040416/artifacts/media/AudioMixAgent/audio/step_8_cbcd4d1e_aud_final.wav
#54 → /home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_046/_workspace/workspace_global_20260510_040416/artifacts/AudioMixAgent/step_8_cbcd4d1e_audiomixagent_exec_8.json
#55 → /home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_046/_workspace/workspace_global_20260510_040416/artifacts/media/CompositorAgent/video/step_9_bc002e30_compositor_final.mp4
#56 → /home/zhendong_li/FrameWorkers/evals/sub-agents/30_results/intakeimage/intake_img_046/_workspace/workspace_global_20260510_040416/artifacts/CompositorAgent/step_9_bc002e30_compositoragent_exec_9.json
