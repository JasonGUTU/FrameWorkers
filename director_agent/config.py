"""Environment configuration for director_agent (Upfront planner + Plan Stack)."""

import os

BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL", "http://localhost:5002").rstrip("/")
POLLING_INTERVAL = float(os.getenv("POLLING_INTERVAL", "2.0"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

DIRECTOR_AGENT_NAME = os.getenv("DIRECTOR_AGENT_NAME", "DirectorAgent")

# Planner LLM (the one that produces the full plan array + optional replan).
DIRECTOR_MEMORY_MODEL = os.getenv(
    "DIRECTOR_MEMORY_MODEL",
    os.getenv("INFERENCE_DEFAULT_MODEL", "gemini-2.5-flash"),
)
DIRECTOR_ROUTING_MODEL = os.getenv(
    "DIRECTOR_ROUTING_MODEL",
    DIRECTOR_MEMORY_MODEL,
).strip()

# Max number of PlanSteps a single user turn can add to the stack.
try:
    MAX_PIPELINE_STEPS = max(1, int(os.getenv("DIRECTOR_MAX_PIPELINE_STEPS", "20")))
except ValueError:
    MAX_PIPELINE_STEPS = 20

# Max executions director will tolerate running through per cycle (safety guard).
try:
    MAX_EXECUTIONS_PER_CYCLE = max(1, int(os.getenv("DIRECTOR_MAX_EXECUTIONS_PER_CYCLE", "30")))
except ValueError:
    MAX_EXECUTIONS_PER_CYCLE = 30

# How many prior user chat lines (oldest→newest tail) to pass into merge_session_goal.
try:
    MERGE_PRIOR_USER_LINES_MAX = max(0, int(os.getenv("DIRECTOR_MERGE_PRIOR_USER_LINES_MAX", "10")))
except ValueError:
    MERGE_PRIOR_USER_LINES_MAX = 10

# How many recent stack steps to surface as slim memory for planner / replanner prompts.
try:
    DIRECTOR_MEMORY_WINDOW = max(1, int(os.getenv("DIRECTOR_MEMORY_WINDOW", "20")))
except ValueError:
    DIRECTOR_MEMORY_WINDOW = 20

# How many times replanner can rewrite the stack tail per user turn (0 = disabled).
try:
    MAX_REPLAN_ROUNDS = max(0, int(os.getenv("DIRECTOR_MAX_REPLAN_ROUNDS", "2")))
except ValueError:
    MAX_REPLAN_ROUNDS = 2
