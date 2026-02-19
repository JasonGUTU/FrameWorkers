#!/usr/bin/env python3
# Entry point for running Director Agent

import sys
import os

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from director_agent.main import main

if __name__ == '__main__':
    main()
