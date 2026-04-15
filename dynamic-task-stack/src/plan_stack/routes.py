# API routes for Frameworks Backend

from flask import Blueprint, request, jsonify
from typing import Optional, Any

from ..common_http import (
    bad_request,
    json_body_or_error,
    parse_bool_query_param,
    parse_enum_or_error,
)
from .api_serialize import serialize_for_api
from .storage import storage
from .models import (
    PlanStepStatus, ReadingStatus, MessageSenderType,
    BatchOperation, BatchOperationType
)


def create_blueprint():
    """Create and configure the Flask blueprint"""
    bp = Blueprint('plan_stack', __name__)

    def _parse_sender_type_or_error(raw_value: Optional[str]):
        return parse_enum_or_error(
            MessageSenderType,
            raw_value,
            field_name="sender_type",
            normalizer=str.lower,
            choices_hint="director, subagent, user",
        )

    # User Message routes
    @bp.route('/api/messages/create', methods=['POST'])
    def create_user_message():
        """Create a new user message"""
        data, error = json_body_or_error()
        if error:
            return error
        
        content = data.get('content')
        sender_type_str = data.get('sender_type', 'user')
        
        if not content:
            return bad_request('Missing required field: content')

        # Convert sender_type string to enum
        sender_type, error = _parse_sender_type_or_error(sender_type_str)
        if error:
            return error
        
        message = storage.create_user_message(content, sender_type)
        return jsonify(serialize_for_api(message)), 201
    
    @bp.route('/api/messages/<msg_id>', methods=['GET'])
    def get_user_message(msg_id: str):
        """Get a user message by ID"""
        message = storage.get_user_message(msg_id)
        if message is None:
            return jsonify({'error': 'Message not found'}), 404
        return jsonify(serialize_for_api(message))
    
    @bp.route('/api/messages/list', methods=['GET'])
    def get_all_user_messages():
        """Get all user messages"""
        messages = storage.get_all_user_messages()
        return jsonify([serialize_for_api(msg) for msg in messages])
    
    @bp.route('/api/messages/unread', methods=['GET'])
    def get_unread_messages():
        """
        Get unread messages with optional filters
        
        Query parameters:
        - sender_type: Optional (director, subagent, user) - filter by message sender type
        - check_director_read: Optional (true/false, default: false) - check director_read_status
        - check_user_read: Optional (true/false, default: false) - check user_read_status
        
        Note: If neither check_director_read nor check_user_read is specified, 
              defaults to check_director_read=true
        """
        sender_type_str = request.args.get('sender_type')
        check_director_read = parse_bool_query_param('check_director_read')
        check_user_read = parse_bool_query_param('check_user_read')

        # Default to check_director_read if neither is specified
        if check_director_read is None and check_user_read is None:
            check_director_read = True
            check_user_read = False
        else:
            check_director_read = bool(check_director_read)
            check_user_read = bool(check_user_read)

        sender_type = None
        if sender_type_str:
            sender_type, error = _parse_sender_type_or_error(sender_type_str)
            if error:
                return error
        
        messages = storage.get_unread_messages(
            sender_type=sender_type,
            check_director_read=check_director_read,
            check_user_read=check_user_read
        )
        return jsonify([serialize_for_api(msg) for msg in messages])
    
    @bp.route('/api/messages/<msg_id>/read-status', methods=['PUT'])
    def update_message_read_status(msg_id: str):
        """Update read status of a message"""
        data, error = json_body_or_error()
        if error:
            return error
        
        director_status_str = data.get('director_read_status')
        user_status_str = data.get('user_read_status')
        
        # Convert string to enum
        director_status, error = parse_enum_or_error(
            ReadingStatus,
            director_status_str,
            field_name="director_read_status",
            normalizer=str.upper,
        )
        if error:
            return error
        
        user_status, error = parse_enum_or_error(
            ReadingStatus,
            user_status_str,
            field_name="user_read_status",
            normalizer=str.upper,
        )
        if error:
            return error
        
        updated_msg = storage.update_message_read_status(
            msg_id, director_status, user_status
        )
        if updated_msg is None:
            return jsonify({'error': 'Message not found'}), 404
        return jsonify(serialize_for_api(updated_msg))
    
    # Plan step routes
    @bp.route('/api/steps/create', methods=['POST'])
    def create_step():
        """Create a new task (does not add to stack automatically)"""
        data, error = json_body_or_error()
        if error:
            return error
        
        description = data.get('description')
        
        if not description or not isinstance(description, dict):
            return bad_request(
                'Missing or invalid required field: description (must be a dictionary)'
            )

        step = storage.create_step(description)
        return jsonify(serialize_for_api(step)), 201
    
    @bp.route('/api/steps/<step_id>', methods=['GET'])
    def get_step(step_id: str):
        """Get a task by ID"""
        step = storage.get_step(step_id)
        if step is None:
            return jsonify({'error': 'Step not found'}), 404
        return jsonify(serialize_for_api(step))
    
    @bp.route('/api/steps/list', methods=['GET'])
    def get_all_steps():
        """Get all tasks"""
        steps = storage.get_all_steps()
        return jsonify([serialize_for_api(step) for step in steps])
    
    @bp.route('/api/steps/<step_id>', methods=['PUT'])
    def update_step(step_id: str):
        """Update a task"""
        data, error = json_body_or_error()
        if error:
            return error
        
        description = data.get('description')
        status_str = data.get('status')
        progress = data.get('progress')
        results = data.get('results')
        
        # Validate description and progress are dicts if provided
        if description is not None and not isinstance(description, dict):
            return bad_request('description must be a dictionary')

        if progress is not None and not isinstance(progress, dict):
            return bad_request('progress must be a dictionary')
        
        # Convert status string to enum
        status, error = parse_enum_or_error(
            PlanStepStatus,
            status_str,
            field_name="status",
            normalizer=str.upper,
        )
        if error:
            return error
        
        updated_step = storage.update_step(
            step_id, description, status, progress, results
        )
        if updated_step is None:
            return jsonify({'error': 'Step not found'}), 404
        return jsonify(serialize_for_api(updated_step))
    
    # Plan layer routes
    @bp.route('/api/layers/create', methods=['POST'])
    def create_layer():
        """Create a new plan layer"""
        data, error = json_body_or_error(allow_empty=True)
        if error:
            return error
        layer_index = data.get('layer_index')

        try:
            layer = storage.create_layer(layer_index)
            return jsonify(serialize_for_api(layer)), 201
        except Exception as e:
            return bad_request(str(e))

    @bp.route('/api/layers/list', methods=['GET'])
    def get_all_layers():
        """Get all task layers"""
        layers = storage.get_all_layers()
        return jsonify([serialize_for_api(layer) for layer in layers])
    
    @bp.route('/api/layers/<int:layer_index>', methods=['GET'])
    def get_layer(layer_index: int):
        """Get a specific layer"""
        layer = storage.get_layer(layer_index)
        if layer is None:
            return jsonify({'error': 'Layer not found'}), 404
        return jsonify(serialize_for_api(layer))
    
    @bp.route('/api/layers/<int:layer_index>/steps', methods=['POST'])
    def add_step_to_layer(layer_index: int):
        """Add a task to a layer"""
        data, error = json_body_or_error()
        if error:
            return error
        
        step_id = data.get('step_id')
        if not step_id:
            return bad_request('Missing required field: step_id')

        insert_index = data.get('insert_index')
        success = storage.add_step_to_layer(layer_index, step_id, insert_index)
        if not success:
            return jsonify({
                'error': 'Layer not found or step not found or step already in layer or cannot add to executed layer'
            }), 404
        
        layer = storage.get_layer(layer_index)
        return jsonify(serialize_for_api(layer))
    
    # Execution pointer routes
    @bp.route('/api/execution-pointer/get', methods=['GET'])
    def get_execution_pointer():
        """Get current execution pointer"""
        pointer = storage.get_execution_pointer()
        if pointer is None:
            return jsonify({'message': 'No execution pointer set'})
        return jsonify(serialize_for_api(pointer))
    
    @bp.route('/api/execution-pointer/set', methods=['PUT'])
    def set_execution_pointer():
        """Set execution pointer"""
        data, error = json_body_or_error()
        if error:
            return error

        layer_index = data.get('layer_index')
        step_index = data.get('step_index')

        if layer_index is None or step_index is None:
            return bad_request('Missing required fields: layer_index, step_index')

        try:
            success = storage.set_execution_pointer(
                int(layer_index),
                int(step_index),
            )
            if not success:
                return bad_request('Invalid layer_index or step_index')

            pointer = storage.get_execution_pointer()
            return jsonify(serialize_for_api(pointer))
        except (ValueError, TypeError):
            return bad_request('Invalid layer_index or step_index format')

    @bp.route('/api/execution-pointer/advance', methods=['POST'])
    def advance_execution_pointer():
        """Advance execution pointer to next task"""
        success = storage.advance_execution_pointer()
        if not success:
            return bad_request('Cannot advance pointer')

        pointer = storage.get_execution_pointer()
        return jsonify(serialize_for_api(pointer))
    
    # Task Stack routes
    @bp.route('/api/plan-stack/next', methods=['GET'])
    def get_next_step():
        """Get the next task to execute based on execution pointer"""
        next_step_info = storage.get_next_step()
        if next_step_info is None:
            return jsonify({'message': 'No steps in stack'})
        
        step = storage.get_step(next_step_info['step_id'])
        response = {
            'layer_index': next_step_info['layer_index'],
            'step_index': next_step_info['step_index'],
            'step_id': next_step_info['step_id'],
            'step': serialize_for_api(step) if step else None,
            'layer': serialize_for_api(next_step_info['layer']),
        }
        return jsonify(response)
    
    @bp.route('/api/plan-stack', methods=['GET'])
    def get_plan_stack():
        """Get all layers in the task stack"""
        layers = storage.get_all_layers()
        return jsonify([serialize_for_api(layer) for layer in layers])
    
    @bp.route('/api/steps/<step_id>/status', methods=['PUT'])
    def update_step_status(step_id: str):
        """Update step status"""
        data, error = json_body_or_error()
        if error:
            return error
        
        status_str = data.get('status')
        if not status_str:
            return bad_request('Missing required field: status')

        status, error = parse_enum_or_error(
            PlanStepStatus,
            status_str,
            field_name="status",
            normalizer=str.upper,
        )
        if error:
            return error
        
        updated_step = storage.update_step(step_id, None, status, None, None)
        if updated_step is None:
            return jsonify({'error': 'Step not found'}), 404
        return jsonify(serialize_for_api(updated_step))
    
    # Batch operations route
    @bp.route('/api/plan-stack/modify', methods=['POST'])
    def modify_plan_stack():
        """
        Execute multiple operations atomically in a single transaction (Batch Operation)
        
        This is the unified batch operation interface for PlanStack modifications.
        All operations are executed within a single lock, ensuring atomicity.
        
        Request body:
        {
            "operations": [
                {
                    "type": "create_steps",
                    "params": {
                        "steps": [
                            {"description": {...}},
                            ...
                        ]
                    }
                },
                {
                    "type": "create_layers",
                    "params": {
                        "layers": [
                            {"layer_index": Optional[int]},
                            ...
                        ]
                    }
                },
                {
                    "type": "add_steps_to_layers",
                    "params": {
                        "additions": [
                            {
                                "layer_index": int,
                                "step_id": str,
                                "insert_index": Optional[int]
                            },
                            ...
                        ]
                    }
                },
                {
                    "type": "remove_steps_from_layers",
                    "params": {
                        "removals": [
                            {
                                "layer_index": int,
                                "step_id": str
                            },
                            ...
                        ]
                    }
                }
            ]
        }
        
        Response:
        {
            "success": bool,
            "results": [...],
            "errors": [...],
            "created_step_ids": [...],
            "created_layer_indices": [...]
        }
        """
        data, error = json_body_or_error()
        if error:
            return error
        
        operations_data = data.get('operations', [])
        if not isinstance(operations_data, list):
            return bad_request('operations must be a list')

        if not operations_data:
            return bad_request('operations list cannot be empty')

        # Parse operations
        operations = []
        for op_data in operations_data:
            if not isinstance(op_data, dict):
                return bad_request('Each operation must be a dictionary')

            op_type_str = op_data.get('type')
            if not op_type_str:
                return bad_request('Each operation must have a "type" field')
            
            op_type, error = parse_enum_or_error(
                BatchOperationType,
                op_type_str,
                field_name="operation type",
                choices_hint=", ".join(e.value for e in BatchOperationType),
            )
            if error:
                return error
            
            params = op_data.get('params', {})
            if not isinstance(params, dict):
                return bad_request('Each operation must have "params" as a dictionary')

            operations.append(BatchOperation(type=op_type, params=params))
        
        # Execute batch operations
        result = storage.modify_plan_stack(operations)
        
        # Serialize result
        return jsonify(serialize_for_api(result))
    
    # Health check route
    @bp.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return jsonify({
            'status': 'ok',
            'service': 'Frameworks Backend'
        })
    
    return bp
