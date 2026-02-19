#!/usr/bin/env python3
# Main entry point for Director Agent

import sys
import logging
import signal
from .director import DirectorAgent
from .config import LOG_LEVEL, DIRECTOR_AGENT_NAME

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)


def main():
    """Main entry point"""
    logger.info(f"Starting {DIRECTOR_AGENT_NAME}...")
    
    # Create Director Agent instance
    director = DirectorAgent()
    
    # Setup signal handlers for graceful shutdown
    def signal_handler(sig, frame):
        logger.info("Received shutdown signal")
        director.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start the Director Agent
    try:
        director.start()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
