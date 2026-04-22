"""HTTP client for Plan Stack backend.

Covers: chat messages + sub-agent catalog + Assistant execute + Plan Stack
reads (step / layers / pointer) + status updates + atomic batch modify.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

import requests

from .config import BACKEND_BASE_URL

logger = logging.getLogger(__name__)


class BackendAPIError(RuntimeError):
    """Invalid or unexpected backend response."""


class BackendAPIClient:
    """HTTP facade for the Flask backend (Plan Stack + Assistant)."""

    def __init__(self, base_url: str = BACKEND_BASE_URL, timeout: float = 60.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {"Content-Type": "application/json", "Accept": "application/json"}
        )

    # ------------------------------------------------------------------
    # Low-level request wrapper
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # Health / catalog
    # ------------------------------------------------------------------

    def health_check(self) -> Dict[str, Any]:
        return self._request("GET", "/health")

    def get_all_agents(self) -> List[Dict[str, Any]]:
        response = self._request("GET", "/api/assistant/sub-agents")
        if isinstance(response, dict):
            agents = response.get("agents")
            if isinstance(agents, list):
                return agents
        if isinstance(response, list):
            return response
        raise BackendAPIError("Unexpected response from /api/assistant/sub-agents")

    # ------------------------------------------------------------------
    # Chat messages
    # ------------------------------------------------------------------

    def list_messages(self) -> List[Dict[str, Any]]:
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
        return self._request(
            "POST",
            "/api/messages/create",
            data={"content": content, "sender_type": sender_type},
        )

    # ------------------------------------------------------------------
    # Assistant execute + executions
    # ------------------------------------------------------------------

    def execute_agent(self, agent_id: str, step_id: str) -> Dict[str, Any]:
        """POST /api/assistant/execute — runs one agent for one PlanStep.

        Returns the serialized AgentExecution:
        ``{id, agent_id, step_id, status, error, inputs, results,
           started_at, completed_at, created_at}``.
        """
        return self._request(
            "POST",
            "/api/assistant/execute",
            data={"agent_id": agent_id, "step_id": step_id},
        )

    # ------------------------------------------------------------------
    # Plan Stack — reads
    # ------------------------------------------------------------------

    def get_plan_stack(self) -> List[Dict[str, Any]]:
        """GET /api/plan-stack — list of layers, each with ``steps`` (PlanStepEntry list)."""
        response = self._request("GET", "/api/plan-stack")
        if isinstance(response, list):
            return response
        raise BackendAPIError("Expected list from /api/plan-stack")

    def get_next_step(self) -> Optional[Dict[str, Any]]:
        """GET /api/plan-stack/next — ``{layer_index, step_index, step_id, step, layer}`` or None."""
        response = self._request("GET", "/api/plan-stack/next")
        if isinstance(response, dict) and "message" in response and "No steps" in response["message"]:
            return None
        return response

    def get_step(self, step_id: str) -> Dict[str, Any]:
        return self._request("GET", f"/api/steps/{step_id}")

    def get_execution_pointer(self) -> Optional[Dict[str, Any]]:
        response = self._request("GET", "/api/execution-pointer/get")
        if isinstance(response, dict) and "message" in response and "No execution pointer" in response["message"]:
            return None
        return response

    # ------------------------------------------------------------------
    # Plan Stack — writes
    # ------------------------------------------------------------------

    def update_step_status(self, step_id: str, status: str) -> Dict[str, Any]:
        return self._request(
            "PUT",
            f"/api/steps/{step_id}/status",
            data={"status": status},
        )

    def set_execution_pointer(
        self,
        layer_index: int,
        step_index: int,
    ) -> Dict[str, Any]:
        return self._request(
            "PUT",
            "/api/execution-pointer/set",
            data={
                "layer_index": layer_index,
                "step_index": step_index,
            },
        )

    def advance_execution_pointer(self) -> Dict[str, Any]:
        return self._request("POST", "/api/execution-pointer/advance")

    def modify_plan_stack(self, operations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """POST /api/plan-stack/modify — batch atomic PlanStack mutations.

        ``operations`` is a list of ``{"type": "<op_name>", "params": {...}}``.
        Supported op types (enum ``BatchOperationType``):

        - ``create_steps``          params: {"steps": [{"description": {...}}, ...]}
        - ``create_layers``         params: {"layers": [{"layer_index": Optional[int]}, ...]}
        - ``add_steps_to_layers``   params: {"additions": [{"layer_index": int, "step_id": str, ...}, ...]}
        - ``remove_steps_from_layers``  params: {"removals": [...]}

        Response body includes ``success`` / ``results`` / ``errors`` /
        ``created_step_ids`` / ``created_layer_indices``.
        """
        return self._request(
            "POST",
            "/api/plan-stack/modify",
            data={"operations": operations},
        )
