#!/usr/bin/env python3
# Entry point for the Plan Stack + Assistant Flask backend

import os

from src.app import create_app

if __name__ == '__main__':
    app = create_app()
    # use_reloader=False: keep Werkzeug from killing the backend mid-run
    # when an unrelated file in the repo changes (we lost an e2e run when
    # the stat-watcher restarted the backend on a wrapper-script edit and
    # the in-memory plan stack + active workspace were both wiped).
    # debug=True still useful for tracebacks; only the reloader is off.
    # Port via FW_BACKEND_PORT env var so multiple backends can run side
    # by side (e.g. one driver on 5002, another on 5050); default 5002.
    port = int(os.getenv("FW_BACKEND_PORT", "5002"))
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)
