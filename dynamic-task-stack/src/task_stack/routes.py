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
    TaskStatus, ReadingStatus, MessageSenderType,
    BatchOperation, BatchOperationType
)


def create_blueprint():
    """Create and configure the Flask blueprint"""
    bp = Blueprint('task_stack', __name__)

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
    
    @bp.route('/api/messages/<msg_id>/check', methods=['GET'])
    def check_user_message(msg_id: str):
        """Check user message (data structure, read status, is new task)"""
        message = storage.get_user_message(msg_id)
        if message is None:
            return jsonify({'error': 'Message not found'}), 404
        
        is_new = storage.is_new_task(msg_id)
        
        response = {
            'message': serialize_for_api(message),
            'is_new_task': is_new,
            'task_state': 'new_task' if is_new else 'existing_or_no_task',
        }
        return jsonify(response)
    
    # Task routes
    @bp.route('/api/tasks/create', methods=['POST'])
    def create_task():
        """Create a new task (does not add to stack automatically)"""
        data, error = json_body_or_error()
        if error:
            return error
        
        description = data.get('description')
        
        if not description or not isinstance(description, dict):
            return bad_request(
                'Missing or invalid required field: description (must be a dictionary)'
            )

        task = storage.create_task(description)
        return jsonify(serialize_for_api(task)), 201
    
    @bp.route('/api/tasks/<task_id>', methods=['GET'])
    def get_task(task_id: str):
        """Get a task by ID"""
        task = storage.get_task(task_id)
        if task is None:
            return jsonify({'error': 'Task not found'}), 404
        return jsonify(serialize_for_api(task))
    
    @bp.route('/api/tasks/list', methods=['GET'])
    def get_all_tasks():
        """Get all tasks"""
        tasks = storage.get_all_tasks()
        return jsonify([serialize_for_api(task) for task in tasks])
    
    @bp.route('/api/tasks/<task_id>', methods=['PUT'])
    def update_task(task_id: str):
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
            TaskStatus,
            status_str,
            field_name="status",
            normalizer=str.upper,
        )
        if error:
            return error
        
        updated_task = storage.update_task(
            task_id, description, status, progress, results
        )
        if updated_task is None:
            return jsonify({'error': 'Task not found'}), 404
        return jsonify(serialize_for_api(updated_task))
    
    @bp.route('/api/tasks/<task_id>', methods=['DELETE'])
    def delete_task(task_id: str):
        """Delete a task"""
        success = storage.delete_task(task_id)
        if not success:
            return jsonify({'error': 'Task not found'}), 404
        return jsonify({'message': 'Task deleted successfully'})
    
    # Task Layer routes
    @bp.route('/api/layers/create', methods=['POST'])
    def create_layer():
        """Create a new task layer"""
        data, error = json_body_or_error(allow_empty=True)
        if error:
            return error
        layer_index = data.get('layer_index')
        pre_hook = data.get('pre_hook')
        post_hook = data.get('post_hook')
        
        try:
            layer = storage.create_layer(layer_index, pre_hook, post_hook)
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
    
    @bp.route('/api/layers/<int:layer_index>/hooks', methods=['PUT'])
    def update_layer_hooks(layer_index: int):
        """Update hooks for a layer"""
        data, error = json_body_or_error()
        if error:
            return error
        
        pre_hook = data.get('pre_hook')
        post_hook = data.get('post_hook')
        
        success = storage.update_layer_hooks(layer_index, pre_hook, post_hook)
        if not success:
            return jsonify({
                'error': 'Layer not found or layer has already been executed'
            }), 404
        
        layer = storage.get_layer(layer_index)
        return jsonify(serialize_for_api(layer))
    
    @bp.route('/api/layers/<int:layer_index>/tasks', methods=['POST'])
    def add_task_to_layer(layer_index: int):
        """Add a task to a layer"""
        data, error = json_body_or_error()
        if error:
            return error
        
        task_id = data.get('task_id')
        if not task_id:
            return bad_request('Missing required field: task_id')

        insert_index = data.get('insert_index')
        success = storage.add_task_to_layer(layer_index, task_id, insert_index)
        if not success:
            return jsonify({
                'error': 'Layer not found or task not found or task already in layer or cannot add to executed layer'
            }), 404
        
        layer = storage.get_layer(layer_index)
        return jsonify(serialize_for_api(layer))
    
    @bp.route('/api/layers/<int:layer_index>/tasks/<task_id>', methods=['DELETE'])
    def remove_task_from_layer(layer_index: int, task_id: str):
        """Remove a task from a layer (only if not executed)"""
        success = storage.remove_task_from_layer(layer_index, task_id)
        if not success:
            return jsonify({
                'error': 'Layer or task not found, or task has already been executed'
            }), 404
        return jsonify({'message': 'Task removed from layer successfully'})
    
    @bp.route('/api/layers/<int:layer_index>/tasks/replace', methods=['POST'])
    def replace_task_in_layer(layer_index: int):
        """Atomically replace a task in a layer (cancel old, add new)"""
        data, error = json_body_or_error()
        if error:
            return error
        
        old_task_id = data.get('old_task_id')
        new_task_id = data.get('new_task_id')
        
        if not old_task_id or not new_task_id:
            return bad_request('Missing required fields: old_task_id, new_task_id')

        success = storage.replace_task_in_layer(layer_index, old_task_id, new_task_id)
        if not success:
            return jsonify({
                'error': 'Layer not found, task not found, or task has already been executed'
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
        task_index = data.get('task_index')
        is_executing_pre_hook = data.get('is_executing_pre_hook', False)
        is_executing_post_hook = data.get('is_executing_post_hook', False)
        
        if layer_index is None or task_index is None:
            return bad_request('Missing required fields: layer_index, task_index')

        try:
            success = storage.set_execution_pointer(
                int(layer_index),
                int(task_index),
                bool(is_executing_pre_hook),
                bool(is_executing_post_hook)
            )
            if not success:
                return bad_request('Invalid layer_index or task_index')

            pointer = storage.get_execution_pointer()
            return jsonify(serialize_for_api(pointer))
        except (ValueError, TypeError):
            return bad_request('Invalid layer_index or task_index format')

    @bp.route('/api/execution-pointer/advance', methods=['POST'])
    def advance_execution_pointer():
        """Advance execution pointer to next task"""
        success = storage.advance_execution_pointer()
        if not success:
            return bad_request('Cannot advance pointer')

        pointer = storage.get_execution_pointer()
        return jsonify(serialize_for_api(pointer))
    
    # Task Stack routes
    @bp.route('/api/task-stack/next', methods=['GET'])
    def get_next_task():
        """Get the next task to execute based on execution pointer"""
        next_task_info = storage.get_next_task()
        if next_task_info is None:
            return jsonify({'message': 'No tasks in stack'})
        
        task = storage.get_task(next_task_info['task_id'])
        response = {
            'layer_index': next_task_info['layer_index'],
            'task_index': next_task_info['task_index'],
            'task_id': next_task_info['task_id'],
            'task': serialize_for_api(task) if task else None,
            'layer': serialize_for_api(next_task_info['layer']),
            'is_pre_hook': next_task_info.get('is_pre_hook', False)
        }
        return jsonify(response)
    
    @bp.route('/api/task-stack', methods=['GET'])
    def get_task_stack():
        """Get all layers in the task stack"""
        layers = storage.get_all_layers()
        return jsonify([serialize_for_api(layer) for layer in layers])
    
    @bp.route('/api/task-stack/insert-layer', methods=['POST'])
    def insert_layer_with_tasks():
        """
        Atomically insert a new layer at specified index and add tasks to it
        
        Request body:
        {
            "insert_layer_index": int,           # Index where to insert the new layer
            "task_ids": Optional[List[str]],     # Optional list of task IDs to add to the new layer (can be empty or omitted to insert empty layer)
            "pre_hook": Optional[Dict],          # Optional pre-hook for the new layer
            "post_hook": Optional[Dict]          # Optional post-hook for the new layer
        }
        
        This is an atomic operation that:
        - Inserts a new layer at the specified index
        - Optionally adds all specified tasks to the new layer (if task_ids provided)
        - Re-indexes all layers after insertion
        
        Examples:
        
        # Insert empty layer
        {
            "insert_layer_index": 3,
            "pre_hook": {"type": "middleware", "action": "prepare"},
            "post_hook": {"type": "hook", "action": "cleanup"}
        }
        
        # Insert layer with tasks
        {
            "insert_layer_index": 3,
            "task_ids": ["task_1_xxx", "task_2_xxx", "task_3_xxx"],
            "pre_hook": {"type": "middleware", "action": "prepare"},
            "post_hook": {"type": "hook", "action": "cleanup"}
        }
        """
        data, error = json_body_or_error()
        if error:
            return error
        
        insert_layer_index = data.get('insert_layer_index')
        task_ids = data.get('task_ids')  # Optional, can be None or empty list
        pre_hook = data.get('pre_hook')
        post_hook = data.get('post_hook')
        
        if insert_layer_index is None:
            return bad_request('Missing required field: insert_layer_index')

        # Validate task_ids if provided
        if task_ids is not None and not isinstance(task_ids, list):
            return bad_request('task_ids must be a list or omitted')

        try:
            insert_layer_index = int(insert_layer_index)
        except (ValueError, TypeError):
            return bad_request('insert_layer_index must be an integer')

        layer = storage.insert_layer_with_tasks(
            insert_layer_index=insert_layer_index,
            task_ids=task_ids,
            pre_hook=pre_hook,
            post_hook=post_hook
        )
        
        if layer is None:
            return bad_request(
                'Failed to insert layer. Possible reasons: invalid index, task not found, '
                'or cannot insert before executed layers'
            )

        return jsonify(serialize_for_api(layer)), 201
    
    @bp.route('/api/tasks/<task_id>/status', methods=['PUT'])
    def update_task_status(task_id: str):
        """Update task status"""
        data, error = json_body_or_error()
        if error:
            return error
        
        status_str = data.get('status')
        if not status_str:
            return bad_request('Missing required field: status')

        status, error = parse_enum_or_error(
            TaskStatus,
            status_str,
            field_name="status",
            normalizer=str.upper,
        )
        if error:
            return error
        
        updated_task = storage.update_task(task_id, None, status, None, None)
        if updated_task is None:
            return jsonify({'error': 'Task not found'}), 404
        return jsonify(serialize_for_api(updated_task))
    
    @bp.route('/api/tasks/<task_id>/messages', methods=['POST'])
    def push_user_message_to_task(task_id: str):
        """Push a user message to a task"""
        data, error = json_body_or_error()
        if error:
            return error
        
        content = data.get('content')
        sender_type_str = data.get('sender_type', 'user')
        
        if not content:
            return bad_request('Missing required field: content')

        # Verify task exists
        task = storage.get_task(task_id)
        if task is None:
            return jsonify({'error': 'Task not found'}), 404
        
        # Convert sender_type string to enum
        sender_type, error = _parse_sender_type_or_error(sender_type_str)
        if error:
            return error
        
        message = storage.create_user_message(content, sender_type, task_id)
        return jsonify(serialize_for_api(message)), 201
    
    # Batch operations route
    @bp.route('/api/task-stack/modify', methods=['POST'])
    def modify_task_stack():
        """
        Execute multiple operations atomically in a single transaction (Batch Operation)
        
        This is the unified batch operation interface for TaskStack modifications.
        All operations are executed within a single lock, ensuring atomicity.
        
        Request body:
        {
            "operations": [
                {
                    "type": "create_tasks",
                    "params": {
                        "tasks": [
                            {"description": {...}},
                            ...
                        ]
                    }
                },
                {
                    "type": "create_layers",
                    "params": {
                        "layers": [
                            {
                                "layer_index": Optional[int],
                                "pre_hook": Optional[Dict],
                                "post_hook": Optional[Dict]
                            },
                            ...
                        ]
                    }
                },
                {
                    "type": "add_tasks_to_layers",
                    "params": {
                        "additions": [
                            {
                                "layer_index": int,
                                "task_id": str,
                                "insert_index": Optional[int]
                            },
                            ...
                        ]
                    }
                },
                {
                    "type": "remove_tasks_from_layers",
                    "params": {
                        "removals": [
                            {
                                "layer_index": int,
                                "task_id": str
                            },
                            ...
                        ]
                    }
                },
                {
                    "type": "replace_tasks_in_layers",
                    "params": {
                        "replacements": [
                            {
                                "layer_index": int,
                                "old_task_id": str,
                                "new_task_id": str
                            },
                            ...
                        ]
                    }
                },
                {
                    "type": "update_layer_hooks",
                    "params": {
                        "updates": [
                            {
                                "layer_index": int,
                                "pre_hook": Optional[Dict],
                                "post_hook": Optional[Dict]
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
            "created_task_ids": [...],
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
        result = storage.modify_task_stack(operations)
        
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
