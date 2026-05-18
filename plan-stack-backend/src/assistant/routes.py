# API routes for Assistant System

import base64
import binascii
from typing import Any, Tuple

from flask import Blueprint, request, jsonify

from ..common_http import json_body_or_error
from ..plan_stack.api_serialize import serialize_for_api
from .service import AssistantService
from .state_store import assistant_state_store
from agents import get_agent_registry


def _execute_error_response(message: str, status: int) -> Tuple[Any, int]:
    """Uniform error JSON for ``POST /execute`` and similar routes."""
    return jsonify({"error": message}), status


def create_assistant_blueprint():
    """Create and configure the Flask blueprint for assistant system"""
    bp = Blueprint('assistant', __name__)
    
    # Initialize assistant service
    service = AssistantService(assistant_state_store)

    def _get_workspace_or_404():
        workspace = assistant_state_store.get_global_workspace()
        if workspace is None:
            return None, (jsonify({'error': 'Workspace not found'}), 404)
        return workspace, None
    
    # Sub-Agent routes (from registry)
    @bp.route('/api/assistant/sub-agents', methods=['GET'])
    def get_all_sub_agents():
        """
        Get all installed sub-agents (from registry)

        Returns aggregated information about all available sub-agents
        """
        registry = get_agent_registry()
        agents_info = registry.gather_agents_info()
        return jsonify(agents_info)
    
    # Execution routes
    @bp.route('/api/assistant/execute', methods=['POST'])
    def execute_agent():
        """
        Execute an agent for a task.

        JSON body: ``agent_id`` and ``step_id`` (both required). Sub-agents
        only see workspace artifacts selected by ``InputResolver`` —
        any user input must already be persisted as a workspace artifact
        (e.g. via an Intake agent or ``POST /api/workspace/upload``)
        before this route is called.

        Success body: the serialized current :class:`AgentExecution`
        ``{id, agent_id, step_id, status, error, inputs, results,
        started_at, completed_at, created_at}`` — same shape as one row
        of ``GET /api/assistant/executions/step/<step_id>``. Directors
        that need cross-turn history query that endpoint directly.

        Error body (4xx/5xx): ``{"error": "..."}``.
        """
        data, error = json_body_or_error()
        if error:
            return error

        agent_id = data.get('agent_id')
        step_id = data.get('step_id')

        if not agent_id or not step_id:
            return _execute_error_response(
                "Missing required fields: agent_id, step_id", 400
            )

        try:
            results = service.execute_agent_for_step(
                agent_id=agent_id,
                step_id=step_id,
            )
            response_body = serialize_for_api(results)
            try:
                from inference import trace as _fw_trace
                _fw_trace.dump_step(
                    "assistant_to_director",
                    agent_id,
                    step_id,
                    {
                        "http_status": 200,
                        "response_body": response_body,
                    },
                )
            except Exception:
                pass
            return jsonify(response_body), 200
        except ValueError as e:
            try:
                from inference import trace as _fw_trace
                _fw_trace.dump_step(
                    "assistant_to_director",
                    agent_id,
                    step_id,
                    {"http_status": 404, "error": str(e)},
                )
            except Exception:
                pass
            return _execute_error_response(str(e), 404)
        except Exception as e:
            try:
                from inference import trace as _fw_trace
                _fw_trace.dump_step(
                    "assistant_to_director",
                    agent_id,
                    step_id,
                    {"http_status": 500, "error": str(e)},
                )
            except Exception:
                pass
            return _execute_error_response(f"Execution failed: {str(e)}", 500)
    
    @bp.route('/api/assistant/executions/step/<step_id>', methods=['GET'])
    def get_executions_by_step(step_id: str):
        """Get all executions for one PlanStep."""
        executions = assistant_state_store.get_executions_by_step(step_id)
        return jsonify([serialize_for_api(e) for e in executions])
    
    # Workspace upload route (B2 strict separation: raw uploads go through here,
    # then an Intake agent converts them into caption-rich workspace artifacts)
    @bp.route('/api/workspace/upload', methods=['POST'])
    def upload_user_file():
        """Persist a raw user upload as a workspace artifact + placeholder caption.

        JSON body fields:
          - mime: required string, e.g. "text/plain", "image/png", "video/mp4".
          - For text uploads: ``text`` (a string).
          - For binary uploads (image/video/audio): ``data_b64`` (base64-encoded bytes).
          - filename: optional original filename hint.
        Caller (or director) is then expected to invoke the appropriate
        IntakeXxxAgent so the placeholder is upgraded to a caption-rich
        artifact that downstream content agents can find via their labels.
        """
        workspace, error = _get_workspace_or_404()
        if error:
            return error

        data, error = json_body_or_error()
        if error:
            return error

        mime = str(data.get("mime") or "").strip()
        if not mime:
            return _execute_error_response("Missing required field: mime", 400)

        # Resolve the byte payload from either ``text`` or ``data_b64``.
        text_value = data.get("text")
        data_b64 = data.get("data_b64")
        file_bytes: bytes
        if text_value is not None:
            if not isinstance(text_value, str):
                return _execute_error_response("text must be a string", 400)
            file_bytes = text_value.encode("utf-8")
        elif data_b64 is not None:
            if not isinstance(data_b64, str):
                return _execute_error_response("data_b64 must be a base64 string", 400)
            try:
                file_bytes = base64.b64decode(data_b64, validate=True)
            except (binascii.Error, ValueError) as exc:
                return _execute_error_response(f"data_b64 invalid base64: {exc}", 400)
        else:
            return _execute_error_response(
                "Missing payload: provide either `text` (string) or `data_b64` (base64 string)",
                400,
            )

        if not file_bytes:
            return _execute_error_response("Upload payload is empty", 400)

        original_filename = str(data.get("filename") or "").strip()
        try:
            result = workspace.persist_raw_upload(
                file_content=file_bytes,
                mime=mime,
                original_filename=original_filename,
            )
        except Exception as exc:
            return _execute_error_response(
                f"Failed to persist upload: {exc}", 500,
            )
        return jsonify(result), 201

    # Workspace routes
    @bp.route('/api/assistant/workspace/files', methods=['GET'])
    def list_workspace_files():
        """List artifacts registered in this workspace.

        Each entry is the artifact registry view of one file: caption,
        path, mime, and the producing execution's metadata
        (agent_id/step_id/execution_id/created_at). There is no separate
        file index; the registry is the single source of truth.
        """
        workspace, error = _get_workspace_or_404()
        if error:
            return error
        return jsonify(workspace.list_workspace_artifacts())

    @bp.route('/api/assistant/workspace/logs', methods=['GET'])
    def get_workspace_logs():
        """Get logs from workspace, filtered by namespaced ``event`` (and
        optionally ``agent_id`` / ``step_id`` / ``execution_id`` / ``level``).
        """
        workspace, error = _get_workspace_or_404()
        if error:
            return error

        event = request.args.get('event')
        agent_id = request.args.get('agent_id')
        step_id = request.args.get('step_id')
        execution_id = request.args.get('execution_id')
        level = request.args.get('level')
        limit = request.args.get('limit', type=int)

        logs = workspace.get_logs(
            event=event,
            agent_id=agent_id,
            step_id=step_id,
            execution_id=execution_id,
            level=level,
            limit=limit,
        )

        return jsonify([serialize_for_api(log) for log in logs])

    return bp
