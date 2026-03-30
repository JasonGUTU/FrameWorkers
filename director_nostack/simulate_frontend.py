#!/usr/bin/env python3
"""
Simulate the Vue chat client against a **running** Flask backend: post a user line, then run
**one** :meth:`DirectorNoStack._cycle` (same as a single poll tick).

Requires ``BACKEND_BASE_URL`` (default ``http://localhost:5002``), a reachable ``/health``, and
routing LLM credentials (``DIRECTOR_ROUTING_MODEL`` / inference config) unless you only use
``--post-only``.

Usage (repo root, ``PYTHONPATH=.``)::

    python -m director_nostack.simulate_frontend "Write a 2-sentence horror hook."
    python -m director_nostack.simulate_frontend --post-only "Queued for your director process."
"""

from __future__ import annotations

import argparse
import logging
import os
import sys


def _repo_root_on_path() -> None:
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if root not in sys.path:
        sys.path.insert(0, root)


def main() -> int:
    _repo_root_on_path()

    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO"),
        format="%(levelname)s %(name)s %(message)s",
    )

    parser = argparse.ArgumentParser(description="Post a user chat message and optionally run one Director poll.")
    parser.add_argument(
        "message",
        nargs="?",
        default="Simulated frontend: say hello and stop.",
        help="User message content (same as ChatWindow user send).",
    )
    parser.add_argument(
        "--base-url",
        default=os.getenv("BACKEND_BASE_URL", "http://localhost:5002"),
        help="Flask backend base URL.",
    )
    parser.add_argument(
        "--post-only",
        action="store_true",
        help="Only POST /api/messages/create; do not run Director (use when director runs separately).",
    )
    args = parser.parse_args()

    from director_nostack.api_client import NoStackAPIClient
    from director_nostack.director import DirectorNoStack

    client = NoStackAPIClient(base_url=args.base_url)
    try:
        health = client.health_check()
        logging.getLogger(__name__).info("Backend health: %s", health)
    except Exception as e:
        logging.getLogger(__name__).error("Health check failed: %s", e)
        return 1

    created = client.create_message(args.message.strip(), sender_type="user")
    msg_id = created.get("id")
    logging.getLogger(__name__).info("Posted user message id=%s", msg_id)

    if args.post_only:
        return 0

    director = DirectorNoStack(client=client)
    director._cycle()
    logging.getLogger(__name__).info("Director._cycle() finished.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
