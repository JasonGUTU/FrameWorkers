#!/usr/bin/env python3
"""
Process entry for the no-stack Director.

Configures logging, registers SIGINT/SIGTERM to stop ``DirectorNoStack`` cleanly, then runs
``DirectorNoStack.start`` (poll chat → ``run_nostack_pipeline`` per user line).

Run from repo root: ``PYTHONPATH=. python -m director_nostack.main`` or ``python director_nostack/run.py``.
"""

from __future__ import annotations

import logging
import signal
import sys

from .config import DIRECTOR_AGENT_NAME, LOG_LEVEL
from .director import DirectorNoStack

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


def main() -> None:
    director = DirectorNoStack()

    def handler(_sig, _frame):
        logger.info("Shutdown signal")
        director.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)

    try:
        director.start()
    except Exception as e:
        logger.error("Fatal: %s", e, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
