"""Consumer-declared input label names for VideoAgent.

Single source of truth shared by descriptor, materializer, and evaluator
within this package.  Each label corresponds to a ``[label_name]`` header
in ``descriptor.input_needs_description`` and is used as the dict key in
``input_bundle_v2.resolved_artifacts``.
"""

INPUT_LABEL_SCREENPLAY = "screenplay"
INPUT_LABEL_KEYFRAMES_METADATA = "keyframes_metadata"
INPUT_LABEL_SHOT_STILLS = "shot_stills"
