"""Consumer-declared input label names for ScreenplayAgent.

Each label corresponds to a ``[label_name]`` header in
``descriptor.input_needs_description`` and is used as the dict key in
the ``resolved_artifacts`` dict that ``descriptor.build_input`` receives.

This agent has only ONE label: ``[story]``. It does NOT accept free-text
directives directly. Any user instruction that should affect the
screenplay flows in via the upstream re-run pattern (the Director re-
runs the story step with the new brief, the new story_blueprint reaches
this agent through the same ``[story]`` label).
"""

INPUT_LABEL_STORY = "story"
