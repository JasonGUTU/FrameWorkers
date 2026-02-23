"""Compatibility shim — agent_core has been migrated to the root-level agents/ package.

All code now lives in ``agents/`` at the project root for easier access.
This shim re-exports everything so that existing relative imports in
``service.py`` and ``routes.py`` (``from .agent_core import ...``)
continue to work without modification.
"""

import sys
from pathlib import Path

_project_root = str(Path(__file__).resolve().parent.parent.parent.parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from agents import *  # noqa: F401, F403
from agents import __all__  # noqa: F401
