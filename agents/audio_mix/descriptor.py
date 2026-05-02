"""AudioMixAgent descriptor — built from a single AgentSpec."""

from __future__ import annotations

import json

from pydantic import BaseModel

from inference.generation import select_audio_service

from ..common_schema import ResolvedArtifactEntry
from ..descriptor import AgentSpec, InputLabelSpec, SubAgentDescriptor
from .agent import AudioMixAgent
from .evaluator import AudioMixEvaluator
from .labels import (
    INPUT_LABEL_AMBIENCE,
    INPUT_LABEL_AMBIENCE_FILE,
    INPUT_LABEL_MUSIC,
    INPUT_LABEL_MUSIC_FILE,
    INPUT_LABEL_NARRATOR_AUDIO,
    INPUT_LABEL_VIDEO_FILE,
    INPUT_LABEL_VIDEO_PACKAGE,
)
from .materializer import FINAL_AUDIO_SYS_ID, AudioMixMaterializer
from .schema import AudioMixAgentInput


def build_input(_step_id: str, resolved_artifacts: dict) -> BaseModel:
    video_pkg = ResolvedArtifactEntry.coerce(
        resolved_artifacts.get(INPUT_LABEL_VIDEO_PACKAGE)
    )
    video_file = ResolvedArtifactEntry.coerce(
        resolved_artifacts.get(INPUT_LABEL_VIDEO_FILE)
    )
    music = ResolvedArtifactEntry.coerce(resolved_artifacts.get(INPUT_LABEL_MUSIC))
    music_file = ResolvedArtifactEntry.coerce(
        resolved_artifacts.get(INPUT_LABEL_MUSIC_FILE)
    )
    amb = ResolvedArtifactEntry.coerce(resolved_artifacts.get(INPUT_LABEL_AMBIENCE))
    amb_file = ResolvedArtifactEntry.coerce(
        resolved_artifacts.get(INPUT_LABEL_AMBIENCE_FILE)
    )
    narrator_file = ResolvedArtifactEntry.coerce(
        resolved_artifacts.get(INPUT_LABEL_NARRATOR_AUDIO)
    )
    return AudioMixAgentInput(
        video_json_text=json.dumps(video_pkg.payload or {}, ensure_ascii=False, indent=2),
        video_file_path=video_file.path or "",
        music_json_text=json.dumps(music.payload or {}, ensure_ascii=False, indent=2),
        music_file_path=music_file.path or "",
        ambience_json_text=json.dumps(amb.payload or {}, ensure_ascii=False, indent=2),
        ambience_file_path=amb_file.path or "",
        narrator_file_path=narrator_file.path or "",
    )


def build_captions(agent_id: str, output_dict: dict) -> dict:
    tracks = output_dict.get("metrics", {}).get("source_track_count", 0)
    return {
        agent_id: {
            "caption": (
                f"[JSON MANIFEST] Final-audio-mix envelope: amix of "
                f"{tracks} source track(s) (video dialogue+foley + "
                f"optional global music/ambience/narrator). Planning "
                f"manifest only; the wav is a sibling artifact."
            ),
            "scope": "global",
        },
        FINAL_AUDIO_SYS_ID: {
            "caption": (
                "[BINARY WAV FILE · mime=audio/wav · sys_id aud_final] "
                "Final-mix audio bytes — all source audio tracks "
                "(dialogue / foley / music / ambience / narrator) "
                "merged. Ready to be muxed onto the delivered video "
                "by a downstream compositing step."
            ),
            "scope": "global",
        },
    }


def materializer_factory(services: dict) -> AudioMixMaterializer:
    return AudioMixMaterializer(audio_service=services["audio_service"])


SPEC = AgentSpec(
    agent_id="AudioMixAgent",
    inputs=[
        InputLabelSpec(
            name=INPUT_LABEL_VIDEO_PACKAGE,
            cardinality="single",
            optional=True,
            description=(
                "Optional — assembled video's JSON manifest (scenes, "
                "shot_segments, per-clip timing). The LLM reads this to "
                "understand the video structure it is mixing audio "
                "onto. This label targets the JSON/manifest artifact "
                "specifically, NOT the mp4 file."
            ),
        ),
        InputLabelSpec(
            name=INPUT_LABEL_VIDEO_FILE,
            cardinality="single",
            optional=True,
            description=(
                "Optional — the final assembled mp4 video file on disk "
                "(binary artifact, mime=video/mp4). When present, the "
                "materializer extracts the clip's baked-in dialogue + "
                "foley audio track and uses it as one source layer in "
                "the mix. This label targets the mp4 binary specifically, "
                "NOT the JSON manifest."
            ),
        ),
        InputLabelSpec(
            name=INPUT_LABEL_MUSIC,
            cardinality="single",
            optional=True,
            description=(
                "Background-music JSON package (mood + duration target "
                "for the global BGM). Present iff a music-generation "
                "step ran. Targets the JSON/manifest artifact "
                "specifically, NOT the wav file — the LLM reads this "
                "for mix-planning context."
            ),
        ),
        InputLabelSpec(
            name=INPUT_LABEL_MUSIC_FILE,
            cardinality="single",
            optional=True,
            description=(
                "Background-music wav on disk (binary artifact, "
                "mime=audio/wav, sys_id 'aud_music_film'). Present iff "
                "a music-generation step ran. The materializer reads "
                "its bytes for amix. Targets the wav binary "
                "specifically, NOT the JSON package."
            ),
        ),
        InputLabelSpec(
            name=INPUT_LABEL_AMBIENCE,
            cardinality="single",
            optional=True,
            description=(
                "Ambience-bed JSON package (description + duration "
                "target for the global room-tone underlay). Present "
                "iff an ambience-generation step ran. Targets the "
                "JSON/manifest artifact specifically, NOT the wav "
                "file — the LLM reads this for mix-planning context."
            ),
        ),
        InputLabelSpec(
            name=INPUT_LABEL_AMBIENCE_FILE,
            cardinality="single",
            optional=True,
            description=(
                "Ambience-bed wav on disk (binary artifact, "
                "mime=audio/wav, sys_id 'aud_amb_film'). Present iff "
                "an ambience-generation step ran. The materializer "
                "reads its bytes for amix. Targets the wav binary "
                "specifically, NOT the JSON package."
            ),
        ),
        InputLabelSpec(
            name=INPUT_LABEL_NARRATOR_AUDIO,
            cardinality="single",
            optional=True,
            description=(
                "Narrator voiceover wav on disk (binary artifact, "
                "mime=audio/wav). Present iff a narrator TTS step ran "
                "(illustrated-storytelling chains where no rendered "
                "video provides the dialogue track). The materializer "
                "reads its bytes for amix as the dialogue base layer "
                "when no [video_file] is available. Targets the wav "
                "binary specifically."
            ),
        ),
    ],
    output_description=(
        "audio_mix (one final film-wide audio track amix'd from "
        "available source layers — the assembled video's baked "
        "dialogue/foley OR narrator voiceover + optional music + "
        "optional ambience; wav registered under sys_id 'aud_final')."
    ),
    purpose_and_trigger=(
        """Combine whichever audio source layers are present (video's baked-in dialogue+foley audio extracted from an upstream assembled mp4, OR a narrator voiceover wav from an illustrated-storytelling chain, plus any global music track, plus any global ambience bed) into ONE final wav. All input layers are individually optional; at least one audio source layer must be available for the mix to produce output. Trigger: the plan needs a single combined audio file from multiple audio sources — typically when the plan adds a music and/or ambience layer onto an assembled video or narrator voiceover, before final composition."""
    ),
    input_preamble=(
        "I amix whichever audio sources are present — the video's own "
        "dialogue+foley track OR a narrator voiceover, with optional "
        "global music / ambience underlays — into one final audio file."
    ),
)


DESCRIPTOR = SubAgentDescriptor.from_spec(
    SPEC,
    agent_factory=lambda llm: AudioMixAgent(llm_client=llm),
    evaluator_factory=AudioMixEvaluator,
    build_input=build_input,
    build_captions=build_captions,
    service_factories={"audio_service": lambda ctx: select_audio_service()},
    materializer_factory=materializer_factory,
)
