"""Shared types for image generation services.

``ImageSemanticContext`` is the language-neutral description of "what
this image should depict" that a caller (typically an agents/materializer)
passes to an ``ImageService``. It contains **purely semantic** fields —
the content description plus the screenplay-level style constraints —
and deliberately contains **zero model-specific prompt templating**.

Each ``ImageService`` implementation is responsible for turning a
``ImageSemanticContext`` into whatever text prompt its underlying
backend wants. This is how we keep model-specific prompt vocabulary
(e.g. the "Edit the attached reference..." instruction prefix, or the
"Visual style: ... Do NOT use: ..." suffix) out of the agents layer.

``ImageResult`` is what ``generate_image`` / ``edit_image`` return:
the raw image bytes plus the text prompt the service actually sent to
the backend, so the caller can write that prompt back into its own
schema for audit/inspection.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ImageSemanticContext:
    """Language-neutral description of one image's content + style.

    Populated by the caller from upstream artifacts (the producing
    agent's output + screenplay-level style locks). A concrete
    ``ImageService`` reads whichever fields it needs and renders them
    into a backend-specific text prompt.

    Fields
    ------
    prompt_summary:
        The core "what this image shows" description — comes from the
        agent's own output (e.g. a character / location / scene anchor
        or a per-shot L3 still's ``prompt_summary``).
    style_notes:
        Global visual-style directives pulled from the screenplay's
        ``style_lock.global_style_notes``. The service renders these
        into a prompt suffix for **text-to-image** (generate) paths
        only — image-edit paths rely on the reference to carry style.
    must_avoid:
        Things to stay away from, pulled from the screenplay's
        ``style_lock.must_avoid``. Applied on both generate and edit
        paths (style refs don't encode "don't do X" information).
    is_identity_reference:
        Set True for L1 global character / location / prop anchors —
        the service then composes a portrait-oriented prompt with a
        neutral studio backdrop and forbids in-scene composition, so
        the resulting image is usable as a clean i2i reference
        downstream. Default False = scene-grounded composition.
    """

    prompt_summary: str = ""
    style_notes: list[str] = field(default_factory=list)
    must_avoid: list[str] = field(default_factory=list)
    is_identity_reference: bool = False


@dataclass
class ImageResult:
    """Return value of ``ImageService.generate_image`` / ``edit_image``.

    ``bytes`` is the generated image payload.

    ``resolved_prompt`` is the text prompt the service *actually* sent
    to its backend, so the caller can persist it alongside the image
    for audit/inspection. May be empty when the service has nothing
    semantically meaningful to report (e.g. ``MockImageService``).
    """

    bytes: bytes
    resolved_prompt: str = ""
