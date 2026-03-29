# Configuration for Director Agent

import os

# Backend API base URL
BACKEND_BASE_URL = os.getenv('BACKEND_BASE_URL', 'http://localhost:5002')

# Polling interval in seconds
POLLING_INTERVAL = float(os.getenv('POLLING_INTERVAL', '2.0'))

# Director Agent settings
DIRECTOR_AGENT_NAME = os.getenv('DIRECTOR_AGENT_NAME', 'Director Agent')
DIRECTOR_AGENT_DESCRIPTION = os.getenv(
    'DIRECTOR_AGENT_DESCRIPTION',
    'Director Agent responsible for reasoning, planning, and task orchestration'
)
# Legacy alias: `AssistantService` reads `ASSISTANT_MEMORY_MODEL` first for global_memory summary LLM.
DIRECTOR_MEMORY_MODEL = os.getenv(
    'DIRECTOR_MEMORY_MODEL',
    os.getenv('INFERENCE_DEFAULT_MODEL', 'google-ai-studio/gemini-2.5-flash')
)

# Sub-agent routing (LLM picks one registered ``agent_id`` for ``POST /api/assistant/execute``).
DIRECTOR_ROUTING_MODEL = os.getenv(
    'DIRECTOR_ROUTING_MODEL',
    DIRECTOR_MEMORY_MODEL,
).strip()

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
