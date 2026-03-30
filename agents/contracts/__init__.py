"""Shared contracts for decoupled assistant/agent IO."""

from .input_bundle_v2 import ArtifactRefV2, InputBundleV2
from .output_envelope_v2 import BinaryOutputV2, OutputEnvelopeV2, StructuredOutputV2
from .naming_spec_v2 import NamingRuleV2, NamingSpecV2

__all__ = [
    "ArtifactRefV2",
    "InputBundleV2",
    "BinaryOutputV2",
    "OutputEnvelopeV2",
    "StructuredOutputV2",
    "NamingRuleV2",
    "NamingSpecV2",
]
