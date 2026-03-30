#!/usr/bin/env python3
"""Shim: ``python director_nostack/run.py`` when cwd is repo root."""

from director_nostack.main import main

if __name__ == "__main__":
    main()
