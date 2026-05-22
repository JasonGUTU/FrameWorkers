"""Demo-driven sub-agent set (standalone prototype).

Not integrated with Director / Assistant / Workspace / InputResolver.
Chain via ``sub_agents/pipeline.py`` for testing demo quality.

Three sub-agents:
  - StoryAgent       : richer story + entity variants + per-shot panel intents
  - KeyframeAgent    : identity anchor images (multiple per entity allowed)
  - ShotPromptAgent  : per-shot (storyboard image, BLACK SUN-style text prompt)
                       → fed to the configured video backend (pipeline.py owns backend choice)
"""

# Default LLM for sub_agents — kept separate from project-wide .env
# INFERENCE_DEFAULT_MODEL so agents/ etc. keep using their own default.
DEFAULT_LLM_MODEL = "gemini-3-pro-preview"
