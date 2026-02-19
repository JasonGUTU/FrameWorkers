# API routes for Frameworks Backend

from flask import Blueprint, request, jsonify
from typing import Optional
from datetime import datetime

from .storage import storage
from .models import (
    TaskStatus, ReadingStatus, MessageSenderType,
    UserMessage, Task, TaskStackEntry, TaskLayer, ExecutionPointer,
    BatchOperation, BatchOperationType, BatchOperationsRequest
)


def create_blueprint():
    """Create and configure the Flask blueprint"""
    bp = Blueprint('task_stack', __name__)
    
    # Helper function to serialize enums
    def serialize_enum(obj):
        """Convert enum to its value"""
        if isinstance(obj, (TaskStatus, ReadingStatus, MessageSenderType)):
            return obj.value
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, (UserMessage, Task, TaskStackEntry, TaskLayer, ExecutionPointer)):
            return {
                k: serialize_enum(v) for k, v in obj.__dict__.items()
            }
        if isinstance(obj, list):
            return [serialize_enum(item) for item in obj]
        if isinstance(obj, dict):
            return {k: serialize_enum(v) for k, v in obj.items()}
        return obj
    
    # User Message routes
    @bp.route('/api/messages/create', methods=['POST'])
    def create_user_message():
        """Create a new user message"""
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON body'}), 400
        
        content = data.get('content')
        sender_type_str = data.get('sender_type', 'user')
        
        if not content:
            return jsonify({
                'error': 'Missing required field: content'
            }), 400
        
        # Convert sender_type string to enum
        try:
            sender_type = MessageSenderType(sender_type_str.lower())
        except ValueError:
            return jsonify({
                'error': f'Invalid sender_type: {sender_type_str}. Must be one of: director, subagent, user'
            }), 400
        
        message = storage.create_user_message(content, sender_type)
        return jsonify(serialize_enum(message)), 201
    
    @bp.route('/api/messages/<msg_id>', methods=['GET'])
    def get_user_message(msg_id: str):
        """Get a user message by ID"""
        message = storage.get_user_message(msg_id)
        if message is None:
            return jsonify({'error': 'Message not found'}), 404
        return jsonify(serialize_enum(message))
    
    @bp.route('/api/messages/list', methods=['GET'])
    def get_all_user_messages():
        """Get all user messages"""
        messages = storage.get_all_user_messages()
        return jsonify([serialize_enum(msg) for msg in messages])
    
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
        check_director_read_str = request.args.get('check_director_read')
        check_user_read_str = request.args.get('check_user_read')
        
        # Parse check flags
        check_director_read = False
        check_user_read = False
        
        if check_director_read_str is not None:
            check_director_read = check_director_read_str.lower() == 'true'
        if check_user_read_str is not None:
            check_user_read = check_user_read_str.lower() == 'true'
        
        # Default to check_director_read if neither is specified
        if check_director_read_str is None and check_user_read_str is None:
            check_director_read = True
        
        sender_type = None
        if sender_type_str:
            try:
                sender_type = MessageSenderType(sender_type_str.lower())
            except ValueError:
                return jsonify({
                    'error': f'Invalid sender_type: {sender_type_str}. Must be one of: director, subagent, user'
                }), 400
        
        messages = storage.get_unread_messages(
            sender_type=sender_type,
            check_director_read=check_director_read,
            check_user_read=check_user_read
        )
        return jsonify([serialize_enum(msg) for msg in messages])
    
    @bp.route('/api/messages/<msg_id>/read-status', methods=['PUT'])
    def update_message_read_status(msg_id: str):
        """Update read status of a message"""
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON body'}), 400
        
        director_status_str = data.get('director_read_status')
        user_status_str = data.get('user_read_status')
        
        # Convert string to enum
        director_status = None
        if director_status_str:
            try:
                director_status = ReadingStatus(director_status_str.upper())
            except ValueError:
                return jsonify({
                    'error': f'Invalid director_read_status: {director_status_str}'
                }), 400
        
        user_status = None
        if user_status_str:
            try:
                user_status = ReadingStatus(user_status_str.upper())
            except ValueError:
                return jsonify({
                    'error': f'Invalid user_read_status: {user_status_str}'
                }), 400
        
        updated_msg = storage.update_message_read_status(
            msg_id, director_status, user_status
        )
        if updated_msg is None:
            return jsonify({'error': 'Message not found'}), 404
        return jsonify(serialize_enum(updated_msg))
    
    @bp.route('/api/messages/<msg_id>/check', methods=['GET'])
    def check_user_message(msg_id: str):
        """Check user message (data structure, read status, is new task)"""
        message = storage.get_user_message(msg_id)
        if message is None:
            return jsonify({'error': 'Message not found'}), 404
        
        is_new = storage.is_new_task(msg_id)
        
        response = {
            'message': serialize_enum(message),
            'is_new_task': is_new,
            'data_structure': {
                'id': message.id,
                'content': message.content,
                'timestamp': message.timestamp.isoformat(),
                'user_id': message.user_id,
                'sender_type': message.sender_type.value,
                'director_read_status': message.director_read_status.value,
                'user_read_status': message.user_read_status.value,
                'task_id': message.task_id
            }
        }
        return jsonify(response)
    
    # Task routes
    @bp.route('/api/tasks/create', methods=['POST'])
    def create_task():
        """Create a new task (does not add to stack automatically)"""
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON body'}), 400
        
        description = data.get('description')
        
        if not description or not isinstance(description, dict):
            return jsonify({
                'error': 'Missing or invalid required field: description (must be a dictionary)'
            }), 400
        
        task = storage.create_task(description)
        return jsonify(serialize_enum(task)), 201
    
    @bp.route('/api/tasks/<task_id>', methods=['GET'])
    def get_task(task_id: str):
        """Get a task by ID"""
        task = storage.get_task(task_id)
        if task is None:
            return jsonify({'error': 'Task not found'}), 404
        return jsonify(serialize_enum(task))
    
    @bp.route('/api/tasks/list', methods=['GET'])
    def get_all_tasks():
        """Get all tasks"""
        tasks = storage.get_all_tasks()
        return jsonify([serialize_enum(task) for task in tasks])
    
    @bp.route('/api/tasks/<task_id>', methods=['PUT'])
    def update_task(task_id: str):
        """Update a task"""
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON body'}), 400
        
        description = data.get('description')
        status_str = data.get('status')
        progress = data.get('progress')
        results = data.get('results')
        
        # Validate description and progress are dicts if provided
        if description is not None and not isinstance(description, dict):
            return jsonify({
                'error': 'description must be a dictionary'
            }), 400
        
        if progress is not None and not isinstance(progress, dict):
            return jsonify({
                'error': 'progress must be a dictionary'
            }), 400
        
        # Convert status string to enum
        status = None
        if status_str:
            try:
                status = TaskStatus(status_str.upper())
            except ValueError:
                return jsonify({
                    'error': f'Invalid status: {status_str}'
                }), 400
        
        updated_task = storage.update_task(
            task_id, description, status, progress, results
        )
        if updated_task is None:
            return jsonify({'error': 'Task not found'}), 404
        return jsonify(serialize_enum(updated_task))
    
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
        data = request.get_json() or {}
        layer_index = data.get('layer_index')
        pre_hook = data.get('pre_hook')
        post_hook = data.get('post_hook')
        
        try:
            layer = storage.create_layer(layer_index, pre_hook, post_hook)
            return jsonify(serialize_enum(layer)), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    
    @bp.route('/api/layers/list', methods=['GET'])
    def get_all_layers():
        """Get all task layers"""
        layers = storage.get_all_layers()
        return jsonify([serialize_enum(layer) for layer in layers])
    
    @bp.route('/api/layers/<int:layer_index>', methods=['GET'])
    def get_layer(layer_index: int):
        """Get a specific layer"""
        layer = storage.get_layer(layer_index)
        if layer is None:
            return jsonify({'error': 'Layer not found'}), 404
        return jsonify(serialize_enum(layer))
    
    @bp.route('/api/layers/<int:layer_index>/hooks', methods=['PUT'])
    def update_layer_hooks(layer_index: int):
        """Update hooks for a layer"""
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON body'}), 400
        
        pre_hook = data.get('pre_hook')
        post_hook = data.get('post_hook')
        
        success = storage.update_layer_hooks(layer_index, pre_hook, post_hook)
        if not success:
            return jsonify({
                'error': 'Layer not found or layer has already been executed'
            }), 404
        
        layer = storage.get_layer(layer_index)
        return jsonify(serialize_enum(layer))
    
    @bp.route('/api/layers/<int:layer_index>/tasks', methods=['POST'])
    def add_task_to_layer(layer_index: int):
        """Add a task to a layer"""
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON body'}), 400
        
        task_id = data.get('task_id')
        if not task_id:
            return jsonify({'error': 'Missing required field: task_id'}), 400
        
        insert_index = data.get('insert_index')
        success = storage.add_task_to_layer(layer_index, task_id, insert_index)
        if not success:
            return jsonify({
                'error': 'Layer not found or task not found or task already in layer or cannot add to executed layer'
            }), 404
        
        layer = storage.get_layer(layer_index)
        return jsonify(serialize_enum(layer))
    
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
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON body'}), 400
        
        old_task_id = data.get('old_task_id')
        new_task_id = data.get('new_task_id')
        
        if not old_task_id or not new_task_id:
            return jsonify({
                'error': 'Missing required fields: old_task_id, new_task_id'
            }), 400
        
        success = storage.replace_task_in_layer(layer_index, old_task_id, new_task_id)
        if not success:
            return jsonify({
                'error': 'Layer not found, task not found, or task has already been executed'
            }), 404
        
        layer = storage.get_layer(layer_index)
        return jsonify(serialize_enum(layer))
    
    # Execution pointer routes
    @bp.route('/api/execution-pointer/get', methods=['GET'])
    def get_execution_pointer():
        """Get current execution pointer"""
        pointer = storage.get_execution_pointer()
        if pointer is None:
            return jsonify({'message': 'No execution pointer set'})
        return jsonify(serialize_enum(pointer))
    
    @bp.route('/api/execution-pointer/set', methods=['PUT'])
    def set_execution_pointer():
        """Set execution pointer"""
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON body'}), 400
        
        layer_index = data.get('layer_index')
        task_index = data.get('task_index')
        is_executing_pre_hook = data.get('is_executing_pre_hook', False)
        is_executing_post_hook = data.get('is_executing_post_hook', False)
        
        if layer_index is None or task_index is None:
            return jsonify({
                'error': 'Missing required fields: layer_index, task_index'
            }), 400
        
        try:
            success = storage.set_execution_pointer(
                int(layer_index),
                int(task_index),
                bool(is_executing_pre_hook),
                bool(is_executing_post_hook)
            )
            if not success:
                return jsonify({'error': 'Invalid layer_index or task_index'}), 400
            
            pointer = storage.get_execution_pointer()
            return jsonify(serialize_enum(pointer))
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid layer_index or task_index format'}), 400
    
    @bp.route('/api/execution-pointer/advance', methods=['POST'])
    def advance_execution_pointer():
        """Advance execution pointer to next task"""
        success = storage.advance_execution_pointer()
        if not success:
            return jsonify({'error': 'Cannot advance pointer'}), 400
        
        pointer = storage.get_execution_pointer()
        return jsonify(serialize_enum(pointer))
    
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
            'task': serialize_enum(task) if task else None,
            'layer': serialize_enum(next_task_info['layer']),
            'is_pre_hook': next_task_info.get('is_pre_hook', False)
        }
        return jsonify(response)
    
    @bp.route('/api/task-stack', methods=['GET'])
    def get_task_stack():
        """Get all layers in the task stack"""
        layers = storage.get_all_layers()
        return jsonify([serialize_enum(layer) for layer in layers])
    
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
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON body'}), 400
        
        insert_layer_index = data.get('insert_layer_index')
        task_ids = data.get('task_ids')  # Optional, can be None or empty list
        pre_hook = data.get('pre_hook')
        post_hook = data.get('post_hook')
        
        if insert_layer_index is None:
            return jsonify({
                'error': 'Missing required field: insert_layer_index'
            }), 400
        
        # Validate task_ids if provided
        if task_ids is not None and not isinstance(task_ids, list):
            return jsonify({
                'error': 'task_ids must be a list or omitted'
            }), 400
        
        try:
            insert_layer_index = int(insert_layer_index)
        except (ValueError, TypeError):
            return jsonify({
                'error': 'insert_layer_index must be an integer'
            }), 400
        
        layer = storage.insert_layer_with_tasks(
            insert_layer_index=insert_layer_index,
            task_ids=task_ids,
            pre_hook=pre_hook,
            post_hook=post_hook
        )
        
        if layer is None:
            return jsonify({
                'error': 'Failed to insert layer. Possible reasons: invalid index, task not found, or cannot insert before executed layers'
            }), 400
        
        return jsonify(serialize_enum(layer)), 201
    
    @bp.route('/api/tasks/<task_id>/status', methods=['PUT'])
    def update_task_status(task_id: str):
        """Update task status"""
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON body'}), 400
        
        status_str = data.get('status')
        if not status_str:
            return jsonify({'error': 'Missing required field: status'}), 400
        
        try:
            status = TaskStatus(status_str.upper())
        except ValueError:
            return jsonify({
                'error': f'Invalid status: {status_str}'
            }), 400
        
        updated_task = storage.update_task(task_id, None, status, None, None)
        if updated_task is None:
            return jsonify({'error': 'Task not found'}), 404
        return jsonify(serialize_enum(updated_task))
    
    @bp.route('/api/tasks/<task_id>/messages', methods=['POST'])
    def push_user_message_to_task(task_id: str):
        """Push a user message to a task"""
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON body'}), 400
        
        content = data.get('content')
        sender_type_str = data.get('sender_type', 'user')
        
        if not content:
            return jsonify({
                'error': 'Missing required field: content'
            }), 400
        
        # Verify task exists
        task = storage.get_task(task_id)
        if task is None:
            return jsonify({'error': 'Task not found'}), 404
        
        # Convert sender_type string to enum
        try:
            sender_type = MessageSenderType(sender_type_str.lower())
        except ValueError:
            return jsonify({
                'error': f'Invalid sender_type: {sender_type_str}. Must be one of: director, subagent, user'
            }), 400
        
        message = storage.create_user_message(content, sender_type, task_id)
        return jsonify(serialize_enum(message)), 201
    
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
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON body'}), 400
        
        operations_data = data.get('operations', [])
        if not isinstance(operations_data, list):
            return jsonify({'error': 'operations must be a list'}), 400
        
        if not operations_data:
            return jsonify({'error': 'operations list cannot be empty'}), 400
        
        # Parse operations
        operations = []
        for op_data in operations_data:
            if not isinstance(op_data, dict):
                return jsonify({
                    'error': 'Each operation must be a dictionary'
                }), 400
            
            op_type_str = op_data.get('type')
            if not op_type_str:
                return jsonify({
                    'error': 'Each operation must have a "type" field'
                }), 400
            
            try:
                op_type = BatchOperationType(op_type_str)
            except ValueError:
                return jsonify({
                    'error': f'Invalid operation type: {op_type_str}. Must be one of: {[e.value for e in BatchOperationType]}'
                }), 400
            
            params = op_data.get('params', {})
            if not isinstance(params, dict):
                return jsonify({
                    'error': 'Each operation must have "params" as a dictionary'
                }), 400
            
            operations.append(BatchOperation(type=op_type, params=params))
        
        # Execute batch operations
        result = storage.modify_task_stack(operations)
        
        # Serialize result
        return jsonify(serialize_enum(result))
    
    # Health check route
    @bp.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return jsonify({
            'status': 'ok',
            'service': 'Frameworks Backend'
        })
    
    return bp
