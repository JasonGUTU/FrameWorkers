from __future__ import annotations

import sys
import types
from pathlib import Path


# Make `dynamic-task-stack/src` package importable.
_repo_root = Path(__file__).resolve().parents[2]
_pkg_root = _repo_root / "dynamic-task-stack"
if str(_pkg_root) not in sys.path:
    sys.path.insert(0, str(_pkg_root))

# `src/__init__.py` imports app.py -> flask_cors.
if "flask_cors" not in sys.modules:
    flask_cors_stub = types.ModuleType("flask_cors")
    flask_cors_stub.CORS = lambda *args, **kwargs: None
    sys.modules["flask_cors"] = flask_cors_stub

from src.app import create_app


def test_create_app_registers_core_routes():
    app = create_app({"TESTING": True})

    with app.test_client() as client:
        health_resp = client.get("/health")
        assert health_resp.status_code == 200

        assistant_resp = client.get("/api/assistant")
        assert assistant_resp.status_code == 200
        assert assistant_resp.get_json()["id"] == "assistant_global"


def test_create_app_accepts_runtime_config_override():
    app = create_app(
        {
            "TESTING": True,
            "CUSTOM_FLAG": "enabled",
        }
    )

    assert app.config["TESTING"] is True
    assert app.config["CUSTOM_FLAG"] == "enabled"
