# Base Agent Import Helper
# This file allows agents in the root-level agents/ directory
# to easily import BaseAgent and AgentMetadata

import sys
from pathlib import Path

# Add dynamic-task-stack/src to path
agents_dir = Path(__file__).parent
project_root = agents_dir.parent
backend_src = project_root / "dynamic-task-stack" / "src"

if str(backend_src) not in sys.path:
    sys.path.insert(0, str(backend_src))

# Import and re-export BaseAgent from agent_core framework
from assistant.agent_core.base_agent import BaseAgent, AgentMetadata

__all__ = ['BaseAgent', 'AgentMetadata']
