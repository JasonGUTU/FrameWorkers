"""Environment configuration for director_nostack (no Task Stack)."""

import os

BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL", "http://localhost:5002").rstrip("/")
POLLING_INTERVAL = float(os.getenv("POLLING_INTERVAL", "2.0"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Single logical task_id for all Assistant executes (global_memory / executions scoped per task).
STANDALONE_TASK_ID = os.getenv("DIRECTOR_STANDALONE_TASK_ID", "standalone_chat").strip()

DIRECTOR_AGENT_NAME = os.getenv("DIRECTOR_AGENT_NAME", "DirectorNoStack")

# Routing LLM (aligned with director_agent.config naming).
DIRECTOR_MEMORY_MODEL = os.getenv(
    "DIRECTOR_MEMORY_MODEL",
    os.getenv("INFERENCE_DEFAULT_MODEL", "google-ai-studio/gemini-2.5-flash"),
)
DIRECTOR_ROUTING_MODEL = os.getenv(
    "DIRECTOR_ROUTING_MODEL",
    DIRECTOR_MEMORY_MODEL,
).strip()

# How many prior user chat lines (oldest→newest tail) to pass into merge_session_goal.
try:
    MERGE_PRIOR_USER_LINES_MAX = max(0, int(os.getenv("DIRECTOR_MERGE_PRIOR_USER_LINES_MAX", "10")))
except ValueError:
    MERGE_PRIOR_USER_LINES_MAX = 10
