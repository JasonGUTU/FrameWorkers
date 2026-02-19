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

# Assistant ID (should match the assistant created in backend)
ASSISTANT_ID = os.getenv('ASSISTANT_ID', 'assistant_1')

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
