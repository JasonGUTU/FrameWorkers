# Base Agent Import Helper
# This file allows agents in the root-level agents/ directory
# to easily import BaseAgent, AgentMetadata, BaseEvaluator, and ExecutionResult

import sys
from pathlib import Path

# Add dynamic-task-stack/src/assistant to path so sub_agent is importable
# as a standalone package (avoids triggering assistant/__init__ which pulls
# in Flask routes and cross-package relative imports).
agents_dir = Path(__file__).parent
project_root = agents_dir.parent
_assistant_dir = project_root / "dynamic-task-stack" / "src" / "assistant"

if str(_assistant_dir) not in sys.path:
    sys.path.insert(0, str(_assistant_dir))

from agent_core.sync_adapter import (
    BaseAgent,
    AgentMetadata,
    BaseEvaluator,
    ExecutionResult,
)

__all__ = ['BaseAgent', 'AgentMetadata', 'BaseEvaluator', 'ExecutionResult']
