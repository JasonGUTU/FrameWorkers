# API routes for Assistant System

from flask import Blueprint, request, jsonify
from typing import Optional
from datetime import datetime

from .service import AssistantService
from .storage import assistant_storage
from .models import (
    Assistant, Agent, AgentExecution, Workspace,
    ExecutionStatus
)
from .agents import get_agent_registry


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
        if isinstance(obj, (Assistant, Agent, AgentExecution, Workspace)):
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
    
    # Workspace routes (conceptual for now)
    @bp.route('/api/assistant/<assistant_id>/workspace', methods=['GET'])
    def get_workspace(assistant_id: str):
        """Get workspace for an assistant"""
        workspace = assistant_storage.get_workspace_by_assistant(assistant_id)
        if workspace is None:
            return jsonify({'error': 'Workspace not found'}), 404
        return jsonify(serialize_assistant_enum(workspace))
    
    return bp
