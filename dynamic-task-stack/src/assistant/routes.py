# API routes for Assistant System

from flask import Blueprint, request, jsonify
from typing import Optional
from datetime import datetime

from .service import AssistantService
from .storage import assistant_storage
from .models import (
    Assistant, Agent, AgentExecution,
    ExecutionStatus
)
from .workspace import Workspace
from .agent_core import get_agent_registry


def create_assistant_blueprint():
    """Create and configure the Flask blueprint for assistant system"""
    bp = Blueprint('assistant', __name__)
    
    # Initialize assistant service
    service = AssistantService(assistant_storage)
    
    # Helper function to serialize enums and dataclasses
    def serialize_assistant_enum(obj):
        """Convert enum to its value"""
        if isinstance(obj, (ExecutionStatus,)):
            return obj.value
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, (Assistant, Agent, AgentExecution)):
            result = {}
            for k, v in obj.__dict__.items():
                if isinstance(v, (ExecutionStatus,)):
                    result[k] = v.value
                elif isinstance(v, datetime):
                    result[k] = v.isoformat()
                elif isinstance(v, list):
                    result[k] = [serialize_assistant_enum(item) for item in v]
                elif isinstance(v, dict):
                    result[k] = {key: serialize_assistant_enum(val) for key, val in v.items()}
                else:
                    result[k] = v
            return result
        if isinstance(obj, list):
            return [serialize_assistant_enum(item) for item in obj]
        if isinstance(obj, dict):
            return {k: serialize_assistant_enum(v) for k, v in obj.items()}
        return obj
    
    # Assistant routes
    @bp.route('/api/assistant/create', methods=['POST'])
    def create_assistant():
        """Create a new assistant"""
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON body'}), 400
        
        name = data.get('name')
        description = data.get('description', '')
        agent_ids = data.get('agent_ids', [])
        
        if not name:
            return jsonify({'error': 'Missing required field: name'}), 400
        
        assistant = assistant_storage.create_assistant(name, description, agent_ids)
        return jsonify(serialize_assistant_enum(assistant)), 201
    
    @bp.route('/api/assistant/<assistant_id>', methods=['GET'])
    def get_assistant(assistant_id: str):
        """Get an assistant by ID"""
        assistant = assistant_storage.get_assistant(assistant_id)
        if assistant is None:
            return jsonify({'error': 'Assistant not found'}), 404
        return jsonify(serialize_assistant_enum(assistant))
    
    @bp.route('/api/assistant/list', methods=['GET'])
    def get_all_assistants():
        """Get all assistants"""
        assistants = assistant_storage.get_all_assistants()
        return jsonify([serialize_assistant_enum(a) for a in assistants])
    
    @bp.route('/api/assistant/<assistant_id>/agents', methods=['POST'])
    def add_agent_to_assistant(assistant_id: str):
        """Add an agent to an assistant"""
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON body'}), 400
        
        agent_id = data.get('agent_id')
        if not agent_id:
            return jsonify({'error': 'Missing required field: agent_id'}), 400
        
        success = assistant_storage.add_agent_to_assistant(assistant_id, agent_id)
        if not success:
            return jsonify({'error': 'Assistant not found'}), 404
        
        assistant = assistant_storage.get_assistant(assistant_id)
        return jsonify(serialize_assistant_enum(assistant))
    
    # Agent routes
    @bp.route('/api/assistant/agents/create', methods=['POST'])
    def create_agent():
        """Create a new agent"""
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON body'}), 400
        
        name = data.get('name')
        description = data.get('description', '')
        input_schema = data.get('input_schema', {})
        capabilities = data.get('capabilities', [])
        
        if not name:
            return jsonify({'error': 'Missing required field: name'}), 400
        
        agent = assistant_storage.create_agent(name, description, input_schema, capabilities)
        return jsonify(serialize_assistant_enum(agent)), 201
    
    @bp.route('/api/assistant/agents/list', methods=['GET'])
    def get_all_agents():
        """Get all agents (from storage)"""
        agents = assistant_storage.get_all_agents()
        return jsonify([serialize_assistant_enum(a) for a in agents])
    
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
    
    @bp.route('/api/assistant/agents/<agent_id>', methods=['GET'])
    def get_agent(agent_id: str):
        """Get an agent by ID"""
        agent = assistant_storage.get_agent(agent_id)
        if agent is None:
            return jsonify({'error': 'Agent not found'}), 404
        return jsonify(serialize_assistant_enum(agent))
    
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
        
        assistant_id = data.get('assistant_id')
        agent_id = data.get('agent_id')
        task_id = data.get('task_id')
        additional_inputs = data.get('additional_inputs')
        
        if not assistant_id or not agent_id or not task_id:
            return jsonify({
                'error': 'Missing required fields: assistant_id, agent_id, task_id'
            }), 400
        
        try:
            results = service.execute_agent_for_task(
                assistant_id=assistant_id,
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
        return jsonify(serialize_assistant_enum(execution))
    
    @bp.route('/api/assistant/executions/task/<task_id>', methods=['GET'])
    def get_executions_by_task(task_id: str):
        """Get all executions for a task"""
        executions = assistant_storage.get_executions_by_task(task_id)
        return jsonify([serialize_assistant_enum(e) for e in executions])
    
    # Workspace routes
    @bp.route('/api/assistant/workspace', methods=['GET'])
    def get_workspace():
        """Get the global workspace shared by all agents"""
        workspace = assistant_storage.get_global_workspace()
        if workspace is None:
            return jsonify({'error': 'Workspace not found'}), 404
        summary = workspace.get_summary()
        return jsonify(summary)
    
    @bp.route('/api/assistant/workspace/summary', methods=['GET'])
    def get_workspace_summary():
        """Get workspace summary with statistics"""
        workspace = assistant_storage.get_global_workspace()
        if workspace is None:
            return jsonify({'error': 'Workspace not found'}), 404
        return jsonify(workspace.get_summary())
    
    @bp.route('/api/assistant/workspace/files', methods=['GET'])
    def list_workspace_files():
        """List files in workspace"""
        workspace = assistant_storage.get_global_workspace()
        if workspace is None:
            return jsonify({'error': 'Workspace not found'}), 404
        
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
        
        return jsonify([
            {
                "id": f.id,
                "filename": f.filename,
                "description": f.description,
                "file_type": f.file_type,
                "file_extension": f.file_extension,
                "file_path": f.file_path,
                "size_bytes": f.size_bytes,
                "created_at": f.created_at.isoformat(),
                "created_by": f.created_by,
                "tags": f.tags,
                "metadata": f.metadata
            }
            for f in files
        ])
    
    @bp.route('/api/assistant/workspace/files/<file_id>', methods=['GET'])
    def get_workspace_file(file_id: str):
        """Get file metadata by ID"""
        workspace = assistant_storage.get_global_workspace()
        if workspace is None:
            return jsonify({'error': 'Workspace not found'}), 404
        
        file_meta = workspace.get_file(file_id)
        if file_meta is None:
            return jsonify({'error': 'File not found'}), 404
        
        return jsonify({
            "id": file_meta.id,
            "filename": file_meta.filename,
            "description": file_meta.description,
            "file_type": file_meta.file_type,
            "file_extension": file_meta.file_extension,
            "file_path": file_meta.file_path,
            "size_bytes": file_meta.size_bytes,
            "created_at": file_meta.created_at.isoformat(),
            "created_by": file_meta.created_by,
            "tags": file_meta.tags,
            "metadata": file_meta.metadata
        })
    
    @bp.route('/api/assistant/workspace/files/search', methods=['GET'])
    def search_workspace_files():
        """Search files in workspace"""
        workspace = assistant_storage.get_global_workspace()
        if workspace is None:
            return jsonify({'error': 'Workspace not found'}), 404
        
        query = request.args.get('query', '')
        file_type = request.args.get('file_type')
        limit = request.args.get('limit', type=int, default=10)
        
        if not query:
            return jsonify({'error': 'Query parameter required'}), 400
        
        files = workspace.search_files(query, file_type=file_type, limit=limit)
        
        return jsonify([
            {
                "id": f.id,
                "filename": f.filename,
                "description": f.description,
                "file_type": f.file_type,
                "file_path": f.file_path,
                "created_at": f.created_at.isoformat()
            }
            for f in files
        ])
    
    @bp.route('/api/assistant/workspace/memory', methods=['GET'])
    def get_workspace_memory():
        """Get Global Memory"""
        workspace = assistant_storage.get_global_workspace()
        if workspace is None:
            return jsonify({'error': 'Workspace not found'}), 404
        
        memory = workspace.read_memory()
        info = workspace.get_memory_info()
        
        return jsonify({
            "content": memory,
            "info": info
        })
    
    @bp.route('/api/assistant/workspace/memory', methods=['POST'])
    def write_workspace_memory():
        """Write to Global Memory"""
        workspace = assistant_storage.get_global_workspace()
        if workspace is None:
            return jsonify({'error': 'Workspace not found'}), 404
        
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
        workspace = assistant_storage.get_global_workspace()
        if workspace is None:
            return jsonify({'error': 'Workspace not found'}), 404
        
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
        
        return jsonify([
            {
                "id": log.id,
                "timestamp": log.timestamp.isoformat(),
                "operation_type": log.operation_type,
                "resource_type": log.resource_type,
                "resource_id": log.resource_id,
                "details": log.details,
                "agent_id": log.agent_id,
                "task_id": log.task_id
            }
            for log in logs
        ])
    
    @bp.route('/api/assistant/workspace/search', methods=['GET'])
    def search_workspace():
        """Comprehensive search across workspace"""
        workspace = assistant_storage.get_global_workspace()
        if workspace is None:
            return jsonify({'error': 'Workspace not found'}), 404
        
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
    
    @bp.route('/api/assistant/<assistant_id>/workspace', methods=['GET'])
    def get_workspace_by_assistant(assistant_id: str):
        """
        Legacy endpoint - returns global workspace summary
        
        Deprecated: Use /api/assistant/workspace instead
        """
        workspace = assistant_storage.get_global_workspace()
        if workspace is None:
            return jsonify({'error': 'Workspace not found'}), 404
        return jsonify(workspace.get_summary())
    
    return bp
