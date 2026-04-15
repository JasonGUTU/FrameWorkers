#!/usr/bin/env python3
"""Shim: ``python director_agent/run.py`` when cwd is repo root."""

from director_agent.main import main

if __name__ == "__main__":
    main()
