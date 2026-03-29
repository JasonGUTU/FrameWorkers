# API routes for Assistant System

from typing import Any, Dict

from flask import Blueprint, request, jsonify

from ..common_http import bad_request, json_body_or_error
from .service import (
    AssistantService,
    AssistantBadExecuteFieldsError,
    AssistantGlobalMemorySyncError,
)
from .state_store import assistant_state_store
from .response_serializers import (
    serialize_response_value,
    file_metadata_to_dict,
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
        """
        data, error = json_body_or_error()
        if error:
            return error
        
        agent_id = data.get('agent_id')
        task_id = data.get('task_id')
        try:
            execute_fields = _execute_fields_from_http_body(data)
        except ValueError as e:
            return jsonify({'error': str(e)}), 400

        if not agent_id or not task_id:
            return jsonify({
                'error': 'Missing required fields: agent_id, task_id'
            }), 400

        try:
            results = service.execute_agent_for_task(
                agent_id=agent_id,
                task_id=task_id,
                execute_fields=execute_fields
            )
            return jsonify(serialize_response_value(results)), 200
        except AssistantBadExecuteFieldsError as e:
            return jsonify({'error': str(e)}), 400
        except AssistantGlobalMemorySyncError as e:
            return jsonify({'error': str(e)}), 500
        except ValueError as e:
            return jsonify({'error': str(e)}), 404
        except Exception as e:
            return jsonify({'error': f'Execution failed: {str(e)}'}), 500
    
    @bp.route('/api/assistant/executions/task/<task_id>', methods=['GET'])
    def get_executions_by_task(task_id: str):
        """Get all executions for a task"""
        executions = assistant_state_store.get_executions_by_task(task_id)
        return jsonify([serialize_response_value(e) for e in executions])
    
    # Workspace routes
    @bp.route('/api/assistant/workspace/files', methods=['GET'])
    def list_workspace_files():
        """List files in workspace"""
        workspace, error = _get_workspace_or_404()
        if error:
            return error
        files = workspace.list_files()
        
        return jsonify([file_metadata_to_dict(f) for f in files])
    
    @bp.route('/api/assistant/workspace/files/<file_id>', methods=['GET'])
    def get_workspace_file(file_id: str):
        """Get file metadata by ID"""
        workspace, error = _get_workspace_or_404()
        if error:
            return error
        
        file_meta = workspace.get_file(file_id)
        if file_meta is None:
            return jsonify({'error': 'File not found'}), 404
        
        return jsonify(file_metadata_to_dict(file_meta))
    
    @bp.route('/api/assistant/workspace/memory/entries', methods=['GET'])
    def list_workspace_memory_entries():
        """List global memory entries."""
        workspace, error = _get_workspace_or_404()
        if error:
            return error

        task_id = request.args.get('task_id')
        agent_id = request.args.get('agent_id')
        limit = request.args.get('limit', type=int, default=20)
        if limit <= 0:
            return bad_request('limit must be a positive integer')

        entries = workspace.list_memory_entries(
            task_id=task_id,
            agent_id=agent_id,
            limit=limit,
        )
        return jsonify(entries)

    @bp.route('/api/assistant/workspace/memory/entries', methods=['POST'])
    def add_workspace_memory_entry():
        """Add one structured memory entry."""
        workspace, error = _get_workspace_or_404()
        if error:
            return error

        data, error = json_body_or_error()
        if error:
            return error

        content = data.get('content')
        if content is None:
            return jsonify({'error': 'Missing required field: content'}), 400

        try:
            entry = workspace.add_memory_entry(
                content=content,
                task_id=data.get('task_id'),
                agent_id=data.get('agent_id'),
                execution_result=data.get('execution_result'),
                artifact_locations=data.get('artifact_locations'),
            )
        except ValueError as exc:
            return jsonify({'error': str(exc)}), 400
        return jsonify(entry), 201

    @bp.route('/api/assistant/workspace/memory/brief', methods=['GET'])
    def get_workspace_memory_brief():
        """Memory brief: ``{"global_memory": [...]}`` (no ``content`` keys; all matches, ``created_at`` desc)."""
        workspace, error = _get_workspace_or_404()
        if error:
            return error

        task_id = request.args.get('task_id')
        agent_id = request.args.get('agent_id')

        brief = workspace.get_memory_brief(
            task_id=task_id,
            agent_id=agent_id,
        )
        return jsonify(brief)
    
    @bp.route('/api/assistant/workspace/logs', methods=['GET'])
    def get_workspace_logs():
        """Get logs from workspace"""
        workspace, error = _get_workspace_or_404()
        if error:
            return error
        
        operation_type = request.args.get('operation_type')
        resource_type = request.args.get('resource_type')
        agent_id = request.args.get('agent_id')
        task_id = request.args.get('task_id')
        limit = request.args.get('limit', type=int)
        
        logs = workspace.get_logs(
            operation_type=operation_type,
            resource_type=resource_type,
            agent_id=agent_id,
            task_id=task_id,
            limit=limit
        )
        
        return jsonify([log_entry_to_dict(log) for log in logs])

    return bp
