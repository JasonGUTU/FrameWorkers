"""Reusable image backend services for agents."""

from __future__ import annotations

import asyncio
import base64
import logging
import os
from typing import Any

import httpx

from .._mock_data import MOCK_PNG
from ..fal_helpers import (
    LazyHttpxClientMixin,
    extract_fal_media_url,
    fal_subscribe,
    http_download_bytes,
    require_fal_model_var,
)
from .types import ImageResult, ImageSemanticContext

logger = logging.getLogger(__name__)

_DEFAULT_OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# ---------------------------------------------------------------------------
# Prompt templating — owned entirely by the inference layer.
#
# These strings are the **only** fal/Gemini-flavored image prompt templating
# in the codebase. Agent-layer materializers never see them; they just pack
# a language-neutral ``ImageSemanticContext`` and let the service render it.
# ---------------------------------------------------------------------------

# Prepended to image-edit prompts. The reference image already encodes the
# global visual style, so the instruction tells the model to preserve
# subject identity while applying the text-described changes.
_EDIT_INSTRUCTION_PREFIX = (
    "Edit the attached reference to match the text below; keep subject identity "
    "recognizable; apply lighting, framing, pose, and environment as described.\n\n"
)

# L1 identity-reference prompt scaffolding. The L1 global anchor must
# be a clean isolated portrait of the entity so it can serve as an
# i2i reference downstream — without these guards the model leaks
# atmospheric / in-scene composition from ``style_notes`` into the
# anchor and L2/L3 then inherit a polluted reference.
_IDENTITY_PROMPT_PREFIX = (
    "Photorealistic cinematic identity-reference still, shot on Arri Alexa 35 "
    "with 50mm prime, shallow depth of field, neutral matte gray studio "
    "backdrop, three-point cinematic lighting (soft key, cool rim, gentle fill).\n"
    "Subject (centered, three-quarter-angle portrait, full upper body in frame): "
)
_IDENTITY_PROMPT_SUFFIX = (
    "\nFraming: identity reference shot only — neutral pose, neutral expression, "
    "subject isolated against the studio backdrop. The image will be used as a "
    "downstream i2i anchor, so visual identity (face, hair, wardrobe, body) "
    "must be unambiguously legible."
)
_IDENTITY_AVOID_DEFAULTS = (
    "anime",
    "cartoon",
    "illustration",
    "painterly rendering",
    "3D CGI render",
    "in-scene composition",
    "environmental setting",
    "props in frame",
    "other people in frame",
    "dramatic horror lighting",
    "atmospheric haze",
    "color grade other than neutral",
)

# L1 identity-reference scaffolding for LOCATION anchors. Mirrors the
# character/prop scaffold in shape but flips every framing decision —
# locations need wide framing, deep focus, and the environment IS the
# subject, not something to be avoided. The character-side
# ``_IDENTITY_AVOID_DEFAULTS`` is unusable here because it forbids
# ``"environmental setting"`` and ``"props in frame"`` — both load-bearing
# for an establishing plate. Edit-path counterpart:
# ``_EDIT_PREFIX_LOCATION_ONLY`` already preserves architecture / geometry /
# materials / lighting, so this t2i prefix uses the same vocabulary.
_IDENTITY_LOCATION_PROMPT_PREFIX = (
    "Photorealistic cinematic establishing-shot location plate, shot on Arri "
    "Alexa 35 with a wide-angle lens (24-35mm), deep focus so foreground, "
    "midground, and background are all sharp, natural ambient lighting "
    "appropriate to the setting, full architectural and geometric context "
    "visible end-to-end.\n"
    "Setting (composed for spatial legibility — clear sense of scale and "
    "depth, no human figure obstructing the geometry): "
)
_IDENTITY_LOCATION_PROMPT_SUFFIX = (
    "\nFraming: location reference plate only — no central character, no "
    "narrative action, no portrait composition. The image will be used as a "
    "downstream i2i anchor, so the location's identity (architecture, "
    "geometry, materials, color grade, lighting character) must be "
    "unambiguously legible across the whole frame."
)
_IDENTITY_LOCATION_AVOID_DEFAULTS = (
    "anime",
    "cartoon",
    "illustration",
    "painterly rendering",
    "3D CGI render",
    "portrait framing",
    "shallow depth of field",
    "studio backdrop",
    "human subject in foreground",
    "characters posed for portrait",
    "dramatic horror lighting",
    "atmospheric haze obscuring geometry",
)

_IDENTITY_REF_KIND_LOCATION = "location"
_IDENTITY_REF_KIND_CHARACTER = "character"
_IDENTITY_REF_KIND_PROP = "prop"
_IDENTITY_REF_KIND_CHARACTER_PICTUREBOOK = "character_picturebook"

# Picture-book identity-reference scaffolding for the storytelling line.
# Mirrors `_IDENTITY_PROMPT_*` in shape but flips the aesthetic axis from
# photoreal cinematic to painterly picture-book — character anchors generated
# this way must visually match the storytelling segments (also painterly,
# also generated under the picture_book ref_kind on the edit path), or
# downstream i2i has a style ref that contradicts the character ref.
_IDENTITY_PICTUREBOOK_PROMPT_PREFIX = (
    "Picture-book illustrated identity-reference portrait, painterly "
    "hand-drawn rendering — flat shapes, decorative outlines, stylized "
    "features matching a children's storybook / watercolor / folk-illustration "
    "plate. Plain neutral background, no in-scene props or other figures.\n"
    "Subject (centered, three-quarter-angle portrait, full upper body "
    "in frame): "
)
_IDENTITY_PICTUREBOOK_PROMPT_SUFFIX = (
    "\nFraming: identity reference plate only — neutral pose, neutral "
    "expression, subject isolated against the plain background. The image "
    "will be used as a downstream i2i anchor for cross-segment character "
    "identity in a picture-book illustrated audiobook, so visual features "
    "(face, hair, wardrobe, body) must be unambiguously legible AND the "
    "whole image must be rendered in the same painterly illustration style "
    "as the story's overall_style — never as a photograph or cinematic still."
)
_IDENTITY_PICTUREBOOK_AVOID_DEFAULTS = (
    "photorealistic",
    "photographic still",
    "cinematic still",
    "Arri Alexa render",
    "shallow depth of field studio photo",
    "3D CGI render",
    "in-scene composition",
    "environmental setting",
    "props in frame",
    "other people in frame",
    "dramatic horror lighting",
)

# Edit-path instruction prefixes, picked by ``ref_kind`` so the model
# knows what to preserve from each reference image.
_EDIT_PREFIX_LOCATION_ONLY = (
    "Edit using the attached reference image, which is a LOCATION anchor: "
    "preserve its architecture, geometry, materials, and lighting / color "
    "grade exactly. Modify only the foreground subjects and framing as the "
    "text below describes. If the text describes a setting that contradicts "
    "the reference geometry (e.g. text says exterior but reference is "
    "interior), ignore the conflicting text and stay faithful to the "
    "reference geometry — the planner intends the same physical place.\n\n"
)
_EDIT_PREFIX_CHARACTER_ONLY = (
    "Edit using the attached reference image, which is a CHARACTER anchor: "
    "preserve face, hair, body type, and wardrobe identity exactly. Apply "
    "only pose, framing, expression, and environment changes as the text "
    "below describes.\n\n"
)
_EDIT_PREFIX_PROP_ONLY = (
    "Edit using the attached reference image, which is a PROP anchor: "
    "preserve the prop's shape, color, materials, and distinctive markings "
    "exactly. Apply only the lighting / environment / framing changes as "
    "the text below describes.\n\n"
)
_EDIT_PREFIX_MULTI_SUBJECT = (
    "Edit using the attached reference images. Each reference is named in "
    "the text below as 'Reference N: <kind> <entity_id>'. Preserve each "
    "reference's identity exactly within its own kind:\n"
    "  * STYLE refs → preserve palette, brush stroke quality, mood, "
    "lighting character ONLY. DO NOT carry over subjects, locations, or "
    "compositional structure from a STYLE ref.\n"
    "  * LOCATION refs → preserve architecture, geometry, lighting / color grade\n"
    "  * CHARACTER refs → preserve face, hair, body type, wardrobe\n"
    "  * PROP refs → preserve shape, color, distinctive markings\n"
    "Compose them together according to the text. Where the text and a "
    "reference disagree on identity-level features (face, architecture, "
    "wardrobe), trust the reference.\n\n"
)
_EDIT_PREFIX_GENERIC = _EDIT_INSTRUCTION_PREFIX

# Medium / style anchor that survives into the edit path so i2i isn't
# left to drift on style alone. Kept short — verbose style notes belong
# in t2i where there's no reference to carry the look.
_EDIT_MEDIUM_ANCHOR = (
    "\nMaintain the reference's photorealistic cinematic still aesthetic: "
    "match its color grade, material rendering, and lighting style; do not "
    "drift to anime, cartoon, painterly, or 3D CGI render."
)
# Inverse anchor for picture-book / illustration line (storytelling →
# IllustrationAgent). The cinematic anchor above asserts photoreal and bans
# painterly / cartoon; that's exactly what storytelling needs to PRESERVE,
# so we replace (not remove) the anchor with a positively-worded
# illustration-aesthetic lock and an explicit ban on photoreal drift.
_EDIT_PICTUREBOOK_ANCHOR = (
    "\nMaintain the reference's picture-book illustration aesthetic: "
    "preserve its painterly brush quality, hand-drawn / watercolor feel, "
    "palette, and lighting style; do not drift to photorealistic, "
    "cinematic still, or 3D CGI render."
)

_EDIT_REF_KIND_LOCATION = "location"
_EDIT_REF_KIND_CHARACTER = "character"
_EDIT_REF_KIND_PROP = "prop"
_EDIT_REF_KIND_MULTI = "multi"
_EDIT_REF_KIND_PICTUREBOOK = "picture_book"
_EDIT_REF_KIND_GENERIC = "generic"

_EDIT_PREFIX_BY_KIND = {
    _EDIT_REF_KIND_LOCATION: _EDIT_PREFIX_LOCATION_ONLY,
    _EDIT_REF_KIND_CHARACTER: _EDIT_PREFIX_CHARACTER_ONLY,
    _EDIT_REF_KIND_PROP: _EDIT_PREFIX_PROP_ONLY,
    _EDIT_REF_KIND_MULTI: _EDIT_PREFIX_MULTI_SUBJECT,
    # picture_book reuses the multi-subject prefix (it also has STYLE +
    # CHARACTER refs); the divergence is the medium anchor + visual_style
    # inclusion, handled in _compose_edit_prompt below.
    _EDIT_REF_KIND_PICTUREBOOK: _EDIT_PREFIX_MULTI_SUBJECT,
    _EDIT_REF_KIND_GENERIC: _EDIT_PREFIX_GENERIC,
}


class ImageService(LazyHttpxClientMixin):
    """Image generation + editing service backed by OpenRouter.

    Callers pass either:

    * ``semantic_context``: an ``ImageSemanticContext`` describing the
      image in model-neutral language. The service is responsible for
      turning it into a backend-specific text prompt.
    * ``prompt``: a pre-composed text prompt string (legacy / direct
      path, used by callers that build prompts themselves — e.g. the
      UniVA keyframe materializer, which inherits its prompts from an
      upstream LLM step).

    When both are provided, ``semantic_context`` takes precedence.
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        base_url: str = _DEFAULT_OPENROUTER_BASE_URL,
        timeout: float = 120.0,
        retry_base_delay: float = 2.0,
        retry_max_delay: float = 30.0,
    ) -> None:
        self._api_key = api_key or os.getenv("OPENROUTER_API_KEY", "")
        self.model = model or os.getenv("INFERENCE_IMAGE_MODEL", "")
        if not self.model:
            raise RuntimeError(
                "No image model configured. Set INFERENCE_IMAGE_MODEL in .env "
                "(e.g. google/gemini-2.5-flash-image)"
            )
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.retry_base_delay = retry_base_delay
        self.retry_max_delay = retry_max_delay
        self._http: httpx.AsyncClient | None = None

    async def generate_image(
        self,
        prompt: str = "",
        *,
        semantic_context: ImageSemanticContext | None = None,
    ) -> ImageResult:
        composed = (
            self._compose_generate_prompt(semantic_context)
            if semantic_context is not None
            else prompt
        )
        logger.info("[Layer1] Generating image: %.100s...", composed)
        messages = [{"role": "user", "content": composed}]
        image_bytes = await self._call_and_extract_image(messages, composed)
        return ImageResult(bytes=image_bytes, resolved_prompt=composed)

    async def edit_image(
        self,
        reference_images: bytes | list[bytes],
        prompt: str = "",
        *,
        semantic_context: ImageSemanticContext | None = None,
        ref_kind: str = _EDIT_REF_KIND_GENERIC,
        ref_manifest: list[str] | None = None,
    ) -> ImageResult:
        composed = (
            self._compose_edit_prompt(
                semantic_context, ref_kind=ref_kind, ref_manifest=ref_manifest
            )
            if semantic_context is not None
            else prompt
        )
        refs = [reference_images] if isinstance(reference_images, bytes) else list(reference_images)
        logger.info("[Layer2/3] Editing image (refs=%d, kind=%s): %.100s...",
                    len(refs), ref_kind, composed)

        content_parts: list[dict[str, Any]] = []
        for ref_bytes in refs:
            b64 = base64.b64encode(ref_bytes).decode()
            content_parts.append(
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}}
            )
        content_parts.append({"type": "text", "text": composed})
        messages = [{"role": "user", "content": content_parts}]
        image_bytes = await self._call_and_extract_image(messages, composed)
        return ImageResult(bytes=image_bytes, resolved_prompt=composed)

    # ------------------------------------------------------------------
    # Semantic context → text prompt
    #
    # The two methods below own every fal/Gemini-flavored string that
    # used to live in ``agents/keyframe/materializer.py``. They are the
    # single place in the codebase that knows how to render a
    # ``ImageSemanticContext`` into a wire-format prompt. Subclasses
    # (Fal, Mock) inherit this behavior unchanged.
    # ------------------------------------------------------------------

    @staticmethod
    def _compose_generate_prompt(ctx: ImageSemanticContext) -> str:
        """Render a semantic context into a text-to-image prompt.

        Two modes:
        * ``is_identity_reference=True`` — L1 global anchor path. The
          scaffold splits by ``ctx.ref_kind``:
            - ``"character"`` / ``"prop"`` / ``""`` → portrait-oriented
              studio framing with neutral matte gray backdrop and an
              explicit "no in-scene composition" guard, so the result
              is a clean isolated subject for downstream i2i.
            - ``"location"`` → wide establishing-shot environment plate
              with deep focus and architecture / geometry / lighting
              context preserved; the environment IS the subject.
          Atmospheric ``style_notes`` are intentionally dropped here
          (they leak scene-mood into what should be a clean reference);
          ``must_avoid`` is still applied alongside the kind-specific
          avoid defaults.
        * default — scene-grounded composition; full style suffix
          (atmosphere block + must_avoid) appended.
        """
        if ctx.is_identity_reference:
            if ctx.ref_kind == _IDENTITY_REF_KIND_LOCATION:
                prefix = _IDENTITY_LOCATION_PROMPT_PREFIX
                suffix = _IDENTITY_LOCATION_PROMPT_SUFFIX
                avoid_defaults = _IDENTITY_LOCATION_AVOID_DEFAULTS
                include_style = False
            elif ctx.ref_kind == _IDENTITY_REF_KIND_CHARACTER_PICTUREBOOK:
                # Storytelling line — anchor must visually match the
                # picture-book illustration aesthetic of the segments,
                # NOT the cinematic photoreal default. style_notes
                # carries the overall_style ("watercolor folk illustration")
                # so it must pass through.
                prefix = _IDENTITY_PICTUREBOOK_PROMPT_PREFIX
                suffix = _IDENTITY_PICTUREBOOK_PROMPT_SUFFIX
                avoid_defaults = _IDENTITY_PICTUREBOOK_AVOID_DEFAULTS
                include_style = True
            else:
                # character / prop / "" (legacy default) all share the
                # portrait scaffold — both want an isolated subject
                # against a neutral backdrop.
                prefix = _IDENTITY_PROMPT_PREFIX
                suffix = _IDENTITY_PROMPT_SUFFIX
                avoid_defaults = _IDENTITY_AVOID_DEFAULTS
                include_style = False
            parts = [prefix]
            if ctx.prompt_summary:
                parts.append(ctx.prompt_summary)
            parts.append(suffix)
            avoid_tail = ImageService._compose_style_suffix(
                style_notes=ctx.style_notes if include_style else [],
                must_avoid=list(ctx.must_avoid) + list(avoid_defaults),
                include_visual_style=include_style,
            )
            if avoid_tail:
                parts.append(avoid_tail)
            return "".join(parts)

        parts = []
        if ctx.prompt_summary:
            parts.append(ctx.prompt_summary)
        tail = ImageService._compose_style_suffix(
            style_notes=ctx.style_notes,
            must_avoid=ctx.must_avoid,
            include_visual_style=True,
        )
        if tail:
            parts.append(tail)
        return "".join(parts)

    @staticmethod
    def _compose_edit_prompt(
        ctx: ImageSemanticContext,
        *,
        ref_kind: str = _EDIT_REF_KIND_GENERIC,
        ref_manifest: list[str] | None = None,
    ) -> str:
        """Render a semantic context into an image-edit prompt.

        Prepends the edit instruction that preserves subject identity
        (variant chosen by ``ref_kind``: location-only, character-only,
        multi-subject, or generic). Appends a short medium / aesthetic
        anchor so the i2i path doesn't drift to non-cinematic styles
        when the reference's look is itself shaky. Atmospheric
        ``style_notes`` are still omitted — the reference carries the
        scene-mood. ``must_avoid`` is appended.

        ``ref_manifest`` is a list of human-readable reference labels
        like ``["Reference 1: location anchor for loc_001",
        "Reference 2: character anchor for char_001"]``; when provided
        (typically with ``ref_kind="multi"``), it's spliced in so the
        model can match each attached reference image to its role.
        """
        prefix = _EDIT_PREFIX_BY_KIND.get(ref_kind, _EDIT_PREFIX_GENERIC)
        parts: list[str] = [prefix]
        if ref_manifest:
            parts.append("\n".join(ref_manifest))
            parts.append("\n\n")
        if ctx.prompt_summary:
            parts.append(ctx.prompt_summary)
        # picture_book line gets the inverse anchor (preserve painterly,
        # ban photoreal drift) and lets style_notes through — overall_style
        # is the *only* place "this is folk illustration / watercolor /
        # picture book" is asserted, and dropping it leaves the model with
        # no positive style signal to lock onto.
        if ref_kind == _EDIT_REF_KIND_PICTUREBOOK:
            parts.append(_EDIT_PICTUREBOOK_ANCHOR)
        else:
            parts.append(_EDIT_MEDIUM_ANCHOR)
        tail = ImageService._compose_style_suffix(
            style_notes=ctx.style_notes,
            must_avoid=ctx.must_avoid,
            include_visual_style=(ref_kind == _EDIT_REF_KIND_PICTUREBOOK),
        )
        if tail:
            parts.append(tail)
        return "".join(parts)

    @staticmethod
    def _compose_style_suffix(
        *,
        style_notes: list[str],
        must_avoid: list[str],
        include_visual_style: bool,
    ) -> str:
        """Build the trailing style chunk shared by generate + edit paths.

        Format: ``"\\nVisual style: a; b. Do NOT use: x; y."`` — the
        leading newline separates the suffix from the body summary so
        the model sees a clear section break. Empty input → empty
        suffix (no stray whitespace).
        """
        chunks: list[str] = []
        if include_visual_style and style_notes:
            chunks.append("Visual style: " + "; ".join(style_notes) + ".")
        if must_avoid:
            chunks.append("Do NOT use: " + "; ".join(must_avoid) + ".")
        if not chunks:
            return ""
        return "\n" + " ".join(chunks)

    async def _call_and_extract_image(
        self,
        messages: list[dict[str, Any]],
        prompt_for_log: str,
    ) -> bytes:
        url = f"{self.base_url}/chat/completions"
        headers = {"Authorization": f"Bearer {self._api_key}", "Content-Type": "application/json"}
        payload = {"model": self.model, "messages": messages}

        attempt = 0
        while True:
            attempt += 1
            try:
                resp = await self.http.post(url, headers=headers, json=payload)
                resp.raise_for_status()
                data = resp.json()
                msg = data.get("choices", [{}])[0].get("message", {})
                images = msg.get("images", [])
                if not images:
                    text_content = msg.get("content", "")
                    raise RuntimeError(
                        f"No image returned from {self.model}. Text response: {text_content[:300]}"
                    )
                img_url = images[0].get("image_url", {}).get("url", "")
                if not img_url.startswith("data:image"):
                    raise RuntimeError(f"Unexpected image format from {self.model}: {img_url[:100]}")
                _, b64_data = img_url.split(",", 1)
                image_bytes = base64.b64decode(b64_data)
                logger.info(
                    "Image generated (%d bytes, attempt %d) for: %.80s...",
                    len(image_bytes),
                    attempt,
                    prompt_for_log,
                )
                return image_bytes
            except (
                httpx.HTTPStatusError,
                httpx.TimeoutException,
                httpx.ConnectError,
                RuntimeError,
            ) as exc:
                delay = min(self.retry_base_delay * (2 ** (attempt - 1)), self.retry_max_delay)
                logger.warning(
                    "Image generation attempt %d failed: %s — retrying in %.1fs",
                    attempt,
                    exc,
                    delay,
                )
                await asyncio.sleep(delay)


class MockImageService(ImageService):
    """Mock image service that returns a tiny placeholder PNG."""

    async def generate_image(
        self,
        prompt: str = "",
        *,
        semantic_context: ImageSemanticContext | None = None,
    ) -> ImageResult:
        composed = (
            self._compose_generate_prompt(semantic_context)
            if semantic_context is not None
            else prompt
        )
        logger.info("[MockImageService] Placeholder for: %.80s...", composed)
        return ImageResult(bytes=MOCK_PNG, resolved_prompt=composed)

    async def edit_image(
        self,
        reference_images: bytes | list[bytes],
        prompt: str = "",
        *,
        semantic_context: ImageSemanticContext | None = None,
        ref_kind: str = _EDIT_REF_KIND_GENERIC,
        ref_manifest: list[str] | None = None,
    ) -> ImageResult:
        composed = (
            self._compose_edit_prompt(
                semantic_context, ref_kind=ref_kind, ref_manifest=ref_manifest
            )
            if semantic_context is not None
            else prompt
        )
        logger.info("[MockImageService] Placeholder edit for: %.80s...", composed)
        return ImageResult(bytes=MOCK_PNG, resolved_prompt=composed)


class FalImageService(ImageService):
    """Image generation/editing service backed by fal.ai."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        timeout: float = 120.0,
    ) -> None:
        self._api_key = api_key or os.getenv("FAL_API_KEY", "")
        self.model = require_fal_model_var("FAL_IMAGE_MODEL", explicit=model)
        self.timeout = timeout
        self._http: httpx.AsyncClient | None = None

    async def generate_image(
        self,
        prompt: str = "",
        *,
        semantic_context: ImageSemanticContext | None = None,
    ) -> ImageResult:
        composed = (
            self._compose_generate_prompt(semantic_context)
            if semantic_context is not None
            else prompt
        )
        logger.info("[fal.ai] Generating image with model=%s", self.model)
        result = await fal_subscribe(self._api_key, self.model, {"prompt": composed})
        image_url = extract_fal_media_url(result, media_type="image")
        image_bytes = await http_download_bytes(self.http, image_url)
        return ImageResult(bytes=image_bytes, resolved_prompt=composed)

    async def edit_image(
        self,
        reference_images: bytes | list[bytes],
        prompt: str = "",
        *,
        semantic_context: ImageSemanticContext | None = None,
        ref_kind: str = _EDIT_REF_KIND_GENERIC,
        ref_manifest: list[str] | None = None,
    ) -> ImageResult:
        composed = (
            self._compose_edit_prompt(
                semantic_context, ref_kind=ref_kind, ref_manifest=ref_manifest
            )
            if semantic_context is not None
            else prompt
        )
        refs = [reference_images] if isinstance(reference_images, bytes) else list(reference_images)
        if not refs:
            raise ValueError("reference_images cannot be empty for fal edit_image")

        if self._is_nano_banana2_base_model(self.model):
            # fal-ai/nano-banana-2/edit expects image_urls (list), not image_url.
            image_urls = [
                f"data:image/png;base64,{base64.b64encode(r).decode('utf-8')}" for r in refs
            ]
            edit_model = "fal-ai/nano-banana-2/edit"
            logger.info("[fal.ai] Editing image with model=%s (kind=%s, refs=%d)",
                        edit_model, ref_kind, len(refs))
            result = await fal_subscribe(
                self._api_key, edit_model, {"prompt": composed, "image_urls": image_urls}
            )
        else:
            image_url = f"data:image/png;base64,{base64.b64encode(refs[0]).decode('utf-8')}"
            result = await fal_subscribe(
                self._api_key, self.model, {"prompt": composed, "image_url": image_url}
            )
        out_url = extract_fal_media_url(result, media_type="image")
        image_bytes = await http_download_bytes(self.http, out_url)
        return ImageResult(bytes=image_bytes, resolved_prompt=composed)

    @staticmethod
    def _is_nano_banana2_base_model(model: str) -> bool:
        return model.rstrip("/") == "fal-ai/nano-banana-2"


class GeminiImageService(ImageService):
    """Image generation/editing via google.genai SDK against the CF AI Gateway.

    Reads ``GEMINI_API_KEY`` (CF Worker token) + ``GEMINI_BASE_URL`` (CF Worker
    endpoint) and talks the native Gemini protocol — the same path used by
    chat completions for ``cf_aig`` provider in ``inference_runtime.yaml``.
    Model id comes from ``INFERENCE_IMAGE_MODEL``; the legacy OpenRouter
    ``google/`` prefix is stripped if present so callers can keep one env
    var across providers.
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        base_url: str | None = None,
        retry_base_delay: float = 2.0,
        retry_max_delay: float = 30.0,
        max_attempts: int = 4,
    ) -> None:
        self._api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        raw_model = (model or os.getenv("INFERENCE_IMAGE_MODEL", "") or "").strip()
        if raw_model.startswith("google/"):
            raw_model = raw_model[len("google/"):]
        self.model = raw_model
        if not self.model:
            raise RuntimeError(
                "No image model configured. Set INFERENCE_IMAGE_MODEL in .env "
                "(e.g. gemini-2.5-flash-image)."
            )
        self.base_url = (base_url or os.getenv("GEMINI_BASE_URL", "") or "").strip()
        self.retry_base_delay = retry_base_delay
        self.retry_max_delay = retry_max_delay
        self.max_attempts = max_attempts
        self._client: Any | None = None

    def _get_client(self) -> Any:
        if self._client is None:
            from google import genai

            kwargs: dict[str, Any] = {}
            if self._api_key:
                kwargs["api_key"] = self._api_key
            if self.base_url:
                kwargs["http_options"] = {"base_url": self.base_url}
            self._client = genai.Client(**kwargs)
        return self._client

    async def generate_image(
        self,
        prompt: str = "",
        *,
        semantic_context: ImageSemanticContext | None = None,
    ) -> ImageResult:
        composed = (
            self._compose_generate_prompt(semantic_context)
            if semantic_context is not None
            else prompt
        )
        logger.info("[gemini] Generating image with model=%s", self.model)
        image_bytes = await self._gemini_call(
            contents=composed, prompt_for_log=composed
        )
        return ImageResult(bytes=image_bytes, resolved_prompt=composed)

    async def edit_image(
        self,
        reference_images: bytes | list[bytes],
        prompt: str = "",
        *,
        semantic_context: ImageSemanticContext | None = None,
        ref_kind: str = _EDIT_REF_KIND_GENERIC,
        ref_manifest: list[str] | None = None,
    ) -> ImageResult:
        composed = (
            self._compose_edit_prompt(
                semantic_context, ref_kind=ref_kind, ref_manifest=ref_manifest
            )
            if semantic_context is not None
            else prompt
        )
        refs = (
            [reference_images]
            if isinstance(reference_images, bytes)
            else list(reference_images)
        )
        if not refs:
            raise ValueError("reference_images cannot be empty for gemini edit_image")

        from google.genai import types as genai_types

        contents: list[Any] = [
            genai_types.Part.from_bytes(data=r, mime_type="image/png") for r in refs
        ]
        contents.append(composed)
        logger.info(
            "[gemini] Editing image with model=%s (kind=%s, refs=%d)",
            self.model,
            ref_kind,
            len(refs),
        )
        image_bytes = await self._gemini_call(
            contents=contents, prompt_for_log=composed
        )
        return ImageResult(bytes=image_bytes, resolved_prompt=composed)

    async def _gemini_call(self, *, contents: Any, prompt_for_log: str) -> bytes:
        from google.genai import types as genai_types

        client = self._get_client()
        config = genai_types.GenerateContentConfig(
            response_modalities=["IMAGE", "TEXT"],
        )

        attempt = 0
        while True:
            attempt += 1
            try:
                resp = await asyncio.to_thread(
                    client.models.generate_content,
                    model=self.model,
                    contents=contents,
                    config=config,
                )
                if not resp.candidates:
                    raise RuntimeError(f"No candidates from {self.model}")
                parts = resp.candidates[0].content.parts or []
                for part in parts:
                    inline = getattr(part, "inline_data", None)
                    if inline and inline.data:
                        image_bytes = inline.data
                        logger.info(
                            "Image generated (%d bytes, attempt %d) for: %.80s...",
                            len(image_bytes),
                            attempt,
                            prompt_for_log,
                        )
                        return image_bytes
                text_parts = [
                    p.text for p in parts if getattr(p, "text", None)
                ]
                raise RuntimeError(
                    f"No image returned from {self.model}. Text: "
                    f"{' '.join(text_parts)[:300]}"
                )
            except Exception as exc:
                if attempt >= self.max_attempts:
                    raise
                delay = min(
                    self.retry_base_delay * (2 ** (attempt - 1)),
                    self.retry_max_delay,
                )
                logger.warning(
                    "Gemini image generation attempt %d failed: %s — retrying in %.1fs",
                    attempt,
                    exc,
                    delay,
                )
                await asyncio.sleep(delay)
