import sys
from pathlib import Path

_agents_dir = Path(__file__).parent
_project_root = _agents_dir.parent
_assistant_dir = _project_root / "dynamic-task-stack" / "src" / "assistant"

if str(_assistant_dir) not in sys.path:
    sys.path.insert(0, str(_assistant_dir))

__all__ = []
