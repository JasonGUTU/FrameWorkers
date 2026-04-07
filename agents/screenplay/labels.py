"""Consumer-declared input label names for ScreenplayAgent.

Each label corresponds to a ``[label_name]`` header in
``descriptor.input_needs_description`` and is used as the dict key in
``input_bundle_v2.resolved_artifacts``.

ScreenplayAgent has only ONE label: ``[story]``. It does NOT accept
free-text directives directly. Any user instruction that should affect
the screenplay flows in via the upstream re-run pattern (Director
re-runs StoryAgent with the new brief, the new story_blueprint reaches
ScreenplayAgent through the same ``[story]`` label).
"""

INPUT_LABEL_STORY = "story"
