"""ComedyStoryAgent — comedy-specialised variant of StoryAgent.

Same I/O contract as StoryAgent (StoryAgentInput → StoryAgentOutput, reuses
StoryEvaluator); only the system_prompt is overridden to bias output toward
comedic structure (setup/punchline scenes, comic flaws, comic reversals).
"""
