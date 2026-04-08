# API routes for Assistant System

import base64
import binascii
from typing import Any, Dict, Optional, Tuple

from flask import Blueprint, request, jsonify

from ..common_http import bad_request, json_body_or_error
from .service import (
    AssistantService,
    AssistantBadExecuteFieldsError,
)
from .state_store import assistant_state_store
from .response_serializers import (
    serialize_response_value,
    log_entry_to_dict,
)
from agents import get_agent_registry


def _execute_fields_from_http_body(data: Dict[str, Any]) -> Dict[str, Any]:
    """Return the nested ``execute_fields`` object from ``POST /api/assistant/execute``.

    Root JSON must expose ``execute_fields`` as a JSON object (may be empty ``{}``).
    """
    raw = data.get("execute_fields")
    if raw is None:
        return {}
    if not isinstance(raw, dict):
        raise ValueError("execute_fields must be a JSON object")
    return dict(raw)


def _execute_error_response(
    message: str,
    status: int,
    *,
    error_reasoning: Optional[str] = None,
) -> Tuple[Any, int]:
    """Uniform error JSON for ``POST /execute`` (``error_reasoning`` reserved for richer context)."""
    return jsonify({"error": message, "error_reasoning": error_reasoning}), status


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
    
    # Global Assistant routes (singleton, pre-defined)
    @bp.route('/api/assistant', methods=['GET'])
    def get_assistant():
        """
        Get the global assistant instance (singleton, pre-defined)
        
        The assistant is a pre-defined singleton that manages all sub-agents.
        All sub-agents are automatically discovered from the registry.
        """
        assistant = assistant_state_store.get_global_assistant()
        return jsonify(serialize_response_value(assistant))
    
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
    
    @bp.route('/api/assistant/sub-agents/<agent_id>', methods=['GET'])
    def get_sub_agent(agent_id: str):
        """Get information about a specific sub-agent"""
        registry = get_agent_registry()
        agents_info = registry.gather_agents_info().get("agents", [])
        agent = next((item for item in agents_info if item.get("id") == agent_id), None)
        if agent is None:
            return jsonify({'error': 'Sub-agent not found'}), 404
        return jsonify(agent)
    
    # Execution routes
    @bp.route('/api/assistant/execute', methods=['POST'])
    def execute_agent():
        """
        Execute an agent for a task.

        JSON body: ``agent_id``, ``task_id`` (required), and ``execute_fields`` (object,
        optional keys ``text``, ``image``, ``video``, ``audio``, …).

        Success body: ``task_id``, ``execution_id``, ``status``, ``error``, ``error_reasoning``,
        ``workspace_id``, ``global_memory_brief`` (no ``content`` in rows). Sub-agent ``results``
        are on ``GET /api/assistant/executions/task/<task_id>``. ``error_reasoning`` is reserved
        for structured/longer failure explanation (currently often ``null``).

        Error body (4xx/5xx on this route): ``error``, ``error_reasoning`` (placeholder, often ``null``).
        """
        data, error = json_body_or_error()
        if error:
            return error
        
        agent_id = data.get('agent_id')
        task_id = data.get('task_id')
        try:
            execute_fields = _execute_fields_from_http_body(data)
        except ValueError as e:
            return _execute_error_response(str(e), 400)

        if not agent_id or not task_id:
            return _execute_error_response(
                "Missing required fields: agent_id, task_id", 400
            )

        try:
            results = service.execute_agent_for_task(
                agent_id=agent_id,
                task_id=task_id,
                execute_fields=execute_fields
            )
            return jsonify(serialize_response_value(results)), 200
        except AssistantBadExecuteFieldsError as e:
            return _execute_error_response(str(e), 400)
        except ValueError as e:
            return _execute_error_response(str(e), 404)
        except Exception as e:
            return _execute_error_response(f"Execution failed: {str(e)}", 500)
    
    @bp.route('/api/assistant/executions/task/<task_id>', methods=['GET'])
    def get_executions_by_task(task_id: str):
        """Get all executions for a task"""
        executions = assistant_state_store.get_executions_by_task(task_id)
        return jsonify([serialize_response_value(e) for e in executions])
    
    # Workspace upload route (B2 strict separation: raw uploads go through here,
    # then an Intake agent converts them into caption-rich workspace artifacts)
    @bp.route('/api/workspace/upload', methods=['POST'])
    def upload_user_file():
        """Persist a raw user upload as a workspace artifact + placeholder caption.

        JSON body fields:
          - mime: required string, e.g. "text/plain", "image/png", "video/mp4".
          - user_intent: required free-form string describing what the upload is for.
          - For text uploads: ``text`` (a string).
          - For binary uploads (image/video/audio): ``data_b64`` (base64-encoded bytes).
          - filename: optional original filename hint.

        Returns: ``{"file_id": "...", "path": "...", "filename": "...",
                    "mime": "...", "caption": {what, why, scope}}``.
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
        user_intent = str(data.get("user_intent") or "").strip()
        if not mime:
            return _execute_error_response("Missing required field: mime", 400)
        if not user_intent:
            return _execute_error_response(
                "Missing required field: user_intent (free-text describing what this upload is for)",
                400,
            )

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
                user_intent=user_intent,
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
        (agent_id/task_id/execution_id/created_at). There is no separate
        file index; the registry is the single source of truth.
        """
        workspace, error = _get_workspace_or_404()
        if error:
            return error
        return jsonify(workspace.list_workspace_artifacts())
    
    @bp.route('/api/assistant/workspace/memory/brief', methods=['GET'])
    def get_workspace_global_memory_brief():
        """Director-facing brief over the workspace's ``global_memory.md``.

        Returns ``{"global_memory_brief": [{execution_id, agent_id, task_id, status,
        created_at}, ...]}`` — chronological, oldest → newest. Each row is one execution that
        successfully wrote artifacts; failed executions don't appear here
        (query ``GET /api/assistant/workspace/logs?event=execution.failed``
        for those).

        Query params: ``task_id`` / ``agent_id`` / ``limit`` (omit → use
        ``ASSISTANT_GLOBAL_MEMORY_CONTEXT_ENTRIES_MAX``, default 20 rows;
        ``limit=0`` → all matching rows).

        URL kept for director-client backward compatibility — the endpoint
        no longer touches a separate "memory" file, it derives the brief
        directly from ``global_memory.md``.
        """
        workspace, error = _get_workspace_or_404()
        if error:
            return error

        task_id = request.args.get('task_id')
        agent_id = request.args.get('agent_id')
        limit_raw = request.args.get('limit', type=int)
        limit: Optional[int]
        if limit_raw is None:
            limit = None
        elif limit_raw < 0:
            return bad_request('limit must be >= 0 (0 = no cap)')
        else:
            limit = limit_raw

        rows = workspace.get_global_memory_brief(
            task_id=task_id,
            agent_id=agent_id,
            limit=limit,
        )
        return jsonify({"global_memory_brief": rows})
    
    @bp.route('/api/assistant/workspace/logs', methods=['GET'])
    def get_workspace_logs():
        """Get logs from workspace, filtered by namespaced ``event`` (and
        optionally ``agent_id`` / ``task_id`` / ``execution_id`` / ``level``).
        """
        workspace, error = _get_workspace_or_404()
        if error:
            return error

        event = request.args.get('event')
        agent_id = request.args.get('agent_id')
        task_id = request.args.get('task_id')
        execution_id = request.args.get('execution_id')
        level = request.args.get('level')
        limit = request.args.get('limit', type=int)

        logs = workspace.get_logs(
            event=event,
            agent_id=agent_id,
            task_id=task_id,
            execution_id=execution_id,
            level=level,
            limit=limit,
        )

        return jsonify([log_entry_to_dict(log) for log in logs])

    return bp
