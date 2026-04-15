"""Voice clone materializer — clones voice and generates narration."""

from __future__ import annotations

import logging
from typing import Any, TYPE_CHECKING

from ..descriptor import BaseMaterializer, MediaAsset
from inference.generation.voice_clone_service import VoiceCloneService

if TYPE_CHECKING:
    from ..base_agent import MaterializeContext
    from .schema import VoiceCloneAgentInput

logger = logging.getLogger(__name__)


class VoiceCloneMaterializer(BaseMaterializer):
    """Clone voice and generate narration via voice clone service."""

    def __init__(self, voice_clone_service: VoiceCloneService) -> None:
        self.svc = voice_clone_service

    async def materialize(
        self,
        ctx: "MaterializeContext",
        asset_dict: dict[str, Any],
    ) -> list[MediaAsset]:
        typed_input: VoiceCloneAgentInput = ctx.typed_input
        content = asset_dict.get("content", {})
        pending: list[MediaAsset] = []

        # Step 1: Clone voice from reference
        profile = await self.svc.clone(typed_input.reference_audio_path)

        # Write profile back into asset_dict
        vp = content.get("voice_profile", {})
        vp["voice_id"] = profile.voice_id

        # Step 2: Generate each segment
        all_segment_bytes: list[bytes] = []
        for seg in content.get("segments", []):
            text = seg.get("text", "")
            asset_id = seg.get("audio_asset_id", "")

            if text and asset_id:
                try:
                    audio_bytes = await self.svc.synthesize(
                        voice_id=profile.voice_id,
                        text=text,
                    )
                    pending.append(MediaAsset(
                        sys_id=asset_id,
                        data=audio_bytes,
                        extension="wav",
                        uri_holder=seg,
                    ))
                    all_segment_bytes.append(audio_bytes)
                except Exception as exc:
                    logger.error("VoiceClone synthesis failed for %s: %s", asset_id, exc)
                    if ctx.report_failure is not None:
                        ctx.report_failure(
                            kind="voice_clone_synthesis",
                            sys_id=asset_id,
                            error=f"{type(exc).__name__}: {exc}",
                        )

        # Step 3: Assemble final
        final = content.get("final_audio", {})
        final["asset_id"] = "vc_final"
        if all_segment_bytes:
            try:
                final_bytes = await self.svc.concat(all_segment_bytes)
                pending.append(MediaAsset(
                    sys_id="vc_final",
                    data=final_bytes,
                    extension="wav",
                    uri_holder=final,
                ))
            except Exception as exc:
                logger.error("VoiceClone final concat failed: %s", exc)
                if ctx.report_failure is not None:
                    ctx.report_failure(
                        kind="voice_clone_concat",
                        sys_id="vc_final",
                        error=f"{type(exc).__name__}: {exc}",
                    )

        logger.info(
            "VoiceCloneMaterializer: %d assets for task %s",
            len(pending), ctx.step_id,
        )
        return pending
