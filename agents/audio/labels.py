"""Consumer-declared input label names for AudioAgent.

Single source of truth shared by descriptor, materializer, and evaluator
within this package.  Each label corresponds to a ``[label_name]`` header
in ``descriptor.input_needs_description`` and is used as the dict key in
the ``resolved_artifacts`` dict that ``descriptor.build_input`` receives.
"""

INPUT_LABEL_SCREENPLAY = "screenplay"
INPUT_LABEL_FINAL_VIDEO = "final_video"
