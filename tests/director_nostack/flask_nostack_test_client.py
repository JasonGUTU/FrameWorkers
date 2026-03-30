"""Flask ``test_client`` adapter for :class:`director_nostack.api_client.NoStackAPIClient` (shared by e2e tests)."""

from __future__ import annotations

import logging

import requests

from director_nostack.api_client import BackendAPIError, NoStackAPIClient

logger = logging.getLogger(__name__)


class FlaskTestNoStackClient(NoStackAPIClient):
    """Send the same HTTP shapes as :class:`NoStackAPIClient`, through Flask ``test_client``."""

    def __init__(self, flask_client):
        super().__init__(base_url="http://e2e.test", timeout=120.0)
        self._fc = flask_client

    def _request(
        self,
        method: str,
        endpoint: str,
        data=None,
        params=None,
    ):
        path = endpoint
        try:
            if method == "GET":
                rv = self._fc.get(path, query_string=params or None)
            elif method == "POST":
                rv = self._fc.post(path, json=data)
            elif method == "PUT":
                rv = self._fc.put(path, json=data)
            else:
                raise NotImplementedError(method)
        except Exception as e:
            logger.error("Flask test request failed: %s %s - %s", method, path, e)
            raise

        if rv.status_code >= 400:
            raise requests.exceptions.HTTPError(
                f"{method} {path} -> {rv.status_code}: {rv.get_data(as_text=True)[:800]}",
            )

        if rv.status_code == 204 or not rv.data:
            return None
        try:
            out = rv.get_json()
        except Exception as exc:
            raise BackendAPIError(
                f"Non-JSON response from Flask test client: {method} {path}"
            ) from exc
        return out


def post_user_chat_line(flask_client, text: str) -> str:
    """Simulate Vue ``ChatWindow`` posting a user message."""
    rv = flask_client.post(
        "/api/messages/create",
        json={"content": text, "sender_type": "user"},
    )
    assert rv.status_code == 201, rv.get_data(as_text=True)
    body = rv.get_json()
    assert body and body.get("id")
    return str(body["id"])
