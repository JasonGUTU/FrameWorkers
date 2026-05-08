#!/usr/bin/env python3
# Entry point for the Plan Stack + Assistant Flask backend

from src.app import create_app

if __name__ == '__main__':
    app = create_app()
    # use_reloader=False: keep Werkzeug from killing the backend mid-run
    # when an unrelated file in the repo changes (we lost an e2e run when
    # the stat-watcher restarted the backend on a wrapper-script edit and
    # the in-memory plan stack + active workspace were both wiped).
    # debug=True still useful for tracebacks; only the reloader is off.
    app.run(host='0.0.0.0', port=5002, debug=True, use_reloader=False)
