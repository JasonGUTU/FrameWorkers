"""Consumer-declared input label names for AudioMixAgent.

The video package carries dialogue + foley baked into each clip by
Kling's ``generate_audio``; AudioMixAgent amix'es that base track with
optional global music / ambience underlays.

Every media side comes in as TWO distinct labels — the InputResolver is
caption-driven and cannot route a single label to both the JSON
manifest (which the LLM needs to read) and the wav file (which the
materializer needs to read bytes from). Each agent's JSON package and
its generated wav coexist at scope=global under distinct captions, so
we declare one label per representation:

  * ``video_package`` — the VideoAgent JSON manifest (scenes /
    shot_segments / timing). Consumed by the LLM for structural context.
  * ``video_file`` — the final assembled mp4 on disk (binary, no JSON
    payload). Consumed by the materializer via ffmpeg to extract the
    Kling-baked audio track (dialogue + foley).
  * ``music`` — the MusicAgent JSON package (mood + duration target).
    Consumed by the LLM for mix planning context.
  * ``music_file`` — the generated music wav file on disk (sys_id
    ``aud_music_film``). Consumed by the materializer as a second
    amix input.
  * ``ambience`` — the AmbienceAgent JSON package (description +
    duration target). Consumed by the LLM for mix planning context.
  * ``ambience_file`` — the generated ambience wav file on disk
    (sys_id ``aud_amb_film``). Consumed by the materializer as a third
    amix input.
"""

INPUT_LABEL_VIDEO_PACKAGE = "video_package"
INPUT_LABEL_VIDEO_FILE = "video_file"
INPUT_LABEL_MUSIC = "music"
INPUT_LABEL_MUSIC_FILE = "music_file"
INPUT_LABEL_AMBIENCE = "ambience"
INPUT_LABEL_AMBIENCE_FILE = "ambience_file"
