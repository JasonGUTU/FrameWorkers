# API routes for Assistant System

from flask import Blueprint, request, jsonify

from .service import AssistantService
from .storage import assistant_storage
from .serializers import (
    serialize_assistant_value,
    file_metadata_to_dict,
    file_search_item_to_dict,
    log_entry_to_dict,
)
from agents import get_agent_registry


def create_assistant_blueprint():
    """Create and configure the Flask blueprint for assistant system"""
    bp = Blueprint('assistant', __name__)
    
    # Initialize assistant service
    service = AssistantService(assistant_storage)

    def _get_workspace_or_404():
        workspace = assistant_storage.get_global_workspace()
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
        assistant = assistant_storage.get_global_assistant()
        return jsonify(serialize_assistant_value(assistant))
    
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
        agent = registry.get_agent(agent_id)
        if agent is None:
            return jsonify({'error': 'Sub-agent not found'}), 404
        return jsonify(agent.get_info())
    
    @bp.route('/api/assistant/agents/<agent_id>/inputs', methods=['GET'])
    def get_agent_inputs(agent_id: str):
        """Get agent input requirements"""
        try:
            input_info = service.query_agent_inputs(agent_id)
            return jsonify(input_info)
        except ValueError as e:
            return jsonify({'error': str(e)}), 404
    
    # Execution routes
    @bp.route('/api/assistant/execute', methods=['POST'])
    def execute_agent():
        """
        Execute an agent for a task
        
        This is the main entry point for agent execution.
        It orchestrates the full workflow:
        1. Query agent inputs
        2. Prepare environment
        3. Package data
        4. Execute agent
        5. Process results
        """
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON body'}), 400
        
        agent_id = data.get('agent_id')
        task_id = data.get('task_id')
        additional_inputs = data.get('additional_inputs')
        
        if not agent_id or not task_id:
            return jsonify({
                'error': 'Missing required fields: agent_id, task_id'
            }), 400
        
        try:
            results = service.execute_agent_for_task(
                agent_id=agent_id,
                task_id=task_id,
                additional_inputs=additional_inputs
            )
            return jsonify(results), 200
        except ValueError as e:
            return jsonify({'error': str(e)}), 404
        except Exception as e:
            return jsonify({'error': f'Execution failed: {str(e)}'}), 500
    
    @bp.route('/api/assistant/executions/<execution_id>', methods=['GET'])
    def get_execution(execution_id: str):
        """Get an execution by ID"""
        execution = assistant_storage.get_execution(execution_id)
        if execution is None:
            return jsonify({'error': 'Execution not found'}), 404
        return jsonify(serialize_assistant_value(execution))
    
    @bp.route('/api/assistant/executions/task/<task_id>', methods=['GET'])
    def get_executions_by_task(task_id: str):
        """Get all executions for a task"""
        executions = assistant_storage.get_executions_by_task(task_id)
        return jsonify([serialize_assistant_value(e) for e in executions])
    
    # Workspace routes
    @bp.route('/api/assistant/workspace', methods=['GET'])
    def get_workspace():
        """Get the global workspace shared by all agents"""
        workspace, error = _get_workspace_or_404()
        if error:
            return error
        summary = workspace.get_summary()
        return jsonify(summary)
    
    @bp.route('/api/assistant/workspace/summary', methods=['GET'])
    def get_workspace_summary():
        """Get workspace summary with statistics"""
        workspace, error = _get_workspace_or_404()
        if error:
            return error
        return jsonify(workspace.get_summary())
    
    @bp.route('/api/assistant/workspace/files', methods=['GET'])
    def list_workspace_files():
        """List files in workspace"""
        workspace, error = _get_workspace_or_404()
        if error:
            return error
        
        file_type = request.args.get('file_type')
        tags = request.args.getlist('tags')
        created_by = request.args.get('created_by')
        limit = request.args.get('limit', type=int)
        
        files = workspace.list_files(
            file_type=file_type,
            tags=tags if tags else None,
            created_by=created_by,
            limit=limit
        )
        
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
    
    @bp.route('/api/assistant/workspace/files/search', methods=['GET'])
    def search_workspace_files():
        """Search files in workspace"""
        workspace, error = _get_workspace_or_404()
        if error:
            return error
        
        query = request.args.get('query', '')
        file_type = request.args.get('file_type')
        limit = request.args.get('limit', type=int, default=10)
        
        if not query:
            return jsonify({'error': 'Query parameter required'}), 400
        
        files = workspace.search_files(query, file_type=file_type, limit=limit)
        
        return jsonify([file_search_item_to_dict(f) for f in files])
    
    @bp.route('/api/assistant/workspace/memory', methods=['GET'])
    def get_workspace_memory():
        """Get Global Memory"""
        workspace, error = _get_workspace_or_404()
        if error:
            return error
        
        memory = workspace.read_memory()
        info = workspace.get_memory_info()
        
        return jsonify({
            "content": memory,
            "info": info
        })
    
    @bp.route('/api/assistant/workspace/memory', methods=['POST'])
    def write_workspace_memory():
        """Write to Global Memory"""
        workspace, error = _get_workspace_or_404()
        if error:
            return error
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON body'}), 400
        
        content = data.get('content')
        append = data.get('append', False)
        
        if content is None:
            return jsonify({'error': 'Missing required field: content'}), 400
        
        result = workspace.write_memory(content, append=append)
        return jsonify(result)
    
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
    
    @bp.route('/api/assistant/workspace/search', methods=['GET'])
    def search_workspace():
        """Comprehensive search across workspace"""
        workspace, error = _get_workspace_or_404()
        if error:
            return error
        
        query = request.args.get('query', '')
        search_types = request.args.getlist('types') or ['files', 'memory', 'logs']
        
        if not query:
            return jsonify({'error': 'Query parameter required'}), 400
        
        results = workspace.search_all(
            query=query,
            search_files='files' in search_types,
            search_memory='memory' in search_types,
            search_logs='logs' in search_types,
            limit=10
        )
        
        return jsonify(results)
    
    
    return bp
