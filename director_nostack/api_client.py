"""HTTP client: chat messages + Assistant only (no Task Stack endpoints)."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

import requests

from .config import BACKEND_BASE_URL

logger = logging.getLogger(__name__)


class BackendAPIError(RuntimeError):
    """Invalid or unexpected backend response."""


class NoStackAPIClient:
    def __init__(self, base_url: str = BACKEND_BASE_URL, timeout: float = 60.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {"Content-Type": "application/json", "Accept": "application/json"}
        )

    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=self.timeout,
            )
            response.raise_for_status()
            try:
                return response.json()
            except ValueError as exc:
                raise BackendAPIError(
                    f"Non-JSON response from backend: {method} {endpoint}"
                ) from exc
        except requests.exceptions.RequestException as e:
            logger.error("API request failed: %s %s - %s", method, url, e)
            raise

    def health_check(self) -> Dict[str, Any]:
        return self._request("GET", "/health")

    def list_messages(self) -> List[Dict[str, Any]]:
        """All chat messages (same store as unread/create). Used to recover prior user lines for merge."""
        response = self._request("GET", "/api/messages/list")
        if isinstance(response, list):
            return response
        raise BackendAPIError("Expected list from /api/messages/list")

    def get_unread_messages(
        self,
        *,
        sender_type: Optional[str] = "user",
        check_director_read: bool = True,
        check_user_read: bool = False,
    ) -> List[Dict[str, Any]]:
        params: Dict[str, Any] = {
            "check_director_read": str(check_director_read).lower(),
            "check_user_read": str(check_user_read).lower(),
        }
        if sender_type:
            params["sender_type"] = sender_type
        response = self._request("GET", "/api/messages/unread", params=params)
        if isinstance(response, list):
            return response
        raise BackendAPIError("Expected list from /api/messages/unread")

    def update_message_read_status(
        self,
        msg_id: str,
        *,
        director_read_status: Optional[str] = None,
        user_read_status: Optional[str] = None,
    ) -> Dict[str, Any]:
        data: Dict[str, Any] = {}
        if director_read_status:
            data["director_read_status"] = director_read_status
        if user_read_status:
            data["user_read_status"] = user_read_status
        return self._request("PUT", f"/api/messages/{msg_id}/read-status", data=data)

    def create_message(self, content: str, sender_type: str = "director") -> Dict[str, Any]:
        """Post a chat line (frontend lists all messages)."""
        return self._request(
            "POST",
            "/api/messages/create",
            data={"content": content, "sender_type": sender_type},
        )

    def execute_agent(
        self,
        agent_id: str,
        task_id: str,
        execute_fields: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        ``POST /api/assistant/execute`` — on **HTTP 200**, the body is ``process_results`` output:
        ``task_id``, ``execution_id``, ``status``, ``error``, ``error_reasoning`` (reserved, often
        ``null``), ``workspace_id``, ``global_memory_brief`` (``{"global_memory": [...]}`` rows
        **without** ``content`` / ``artifact_locations``, same as ``GET .../memory/brief``). Sub-agent output is **not**
        inlined; use ``GET /api/assistant/executions/task/{task_id}`` and read the latest row's
        ``results``.

        On **4xx/5xx**, ``requests`` raises; body is ``{"error": "...", "error_reasoning": ...}``
        (``error_reasoning`` often ``null`` until populated server-side).

        Director uses ``status`` / ``error`` / ``global_memory_brief`` for chat previews; **re-planning**
        still refreshes ``memory/brief`` and ``executions`` as today.
        """
        data: Dict[str, Any] = {
            "agent_id": agent_id,
            "task_id": task_id,
            "execute_fields": dict(execute_fields) if execute_fields else {},
        }
        return self._request("POST", "/api/assistant/execute", data=data)

    def get_executions_by_task(self, task_id: str) -> List[Dict[str, Any]]:
        response = self._request("GET", f"/api/assistant/executions/task/{task_id}")
        if isinstance(response, list):
            return response
        raise BackendAPIError(f"Expected list from executions/task/{task_id}")

    def get_all_agents(self) -> List[Dict[str, Any]]:
        response = self._request("GET", "/api/assistant/sub-agents")
        if isinstance(response, dict):
            agents = response.get("agents")
            if isinstance(agents, list):
                return agents
        if isinstance(response, list):
            return response
        raise BackendAPIError("Unexpected response from /api/assistant/sub-agents")

    def get_workspace_memory_brief(
        self,
        *,
        task_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        """``global_memory`` slim rows (newest first). Omit ``limit`` to use server default (20)."""
        params: Dict[str, Any] = {}
        if task_id:
            params["task_id"] = task_id
        if agent_id:
            params["agent_id"] = agent_id
        if limit is not None:
            params["limit"] = limit
        response = self._request(
            "GET", "/api/assistant/workspace/memory/brief", params=params
        )
        if isinstance(response, dict):
            return response
        raise BackendAPIError("Expected object from /api/assistant/workspace/memory/brief")
