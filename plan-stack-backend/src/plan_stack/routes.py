# API routes for Frameworks Backend

import logging
from flask import Blueprint, request, jsonify
from typing import Optional

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

logger = logging.getLogger(__name__)


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

        sender_type, error = _parse_sender_type_or_error(sender_type_str)
        if error:
            return error

        message = storage.create_user_message(content, sender_type)

        # Auto-register user chat text as a creative_brief in the
        # workspace. Post IntakeTextAgent retirement (2026-04-23) this
        # is the glue that turns chat messages into workspace artifacts
        # the downstream story/screenplay/narration agents can resolve
        # via ``[creative_brief]``. Only user-sourced non-empty messages
        # trigger; director/subagent chatter stays out of the artifact
        # pool so it doesn't compete with real briefs during resolution.
        if sender_type == MessageSenderType.USER and (content or "").strip():
            try:
                from ..assistant.state_store import assistant_state_store
                workspace = assistant_state_store.get_global_workspace()
                if workspace is not None:
                    workspace.persist_raw_upload(
                        file_content=content.encode("utf-8"),
                        mime="text/plain",
                        original_filename="",
                    )
            except Exception as exc:
                # Never block message creation on the glue failing; the
                # chat record itself is independent of the artifact.
                logger.warning(
                    "Failed to auto-persist chat text as workspace brief: %s",
                    exc,
                )

        return jsonify(serialize_for_api(message)), 201

    @bp.route('/api/messages/list', methods=['GET'])
    def get_all_user_messages():
        """Get all user messages"""
        messages = storage.get_all_user_messages()
        return jsonify([serialize_for_api(msg) for msg in messages])

    @bp.route('/api/messages/unread', methods=['GET'])
    def get_unread_messages():
        """
        Get unread messages with optional filters.

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

        updated_step = storage.update_step_status(step_id, status)
        if updated_step is None:
            return jsonify({'error': 'Step not found'}), 404
        return jsonify(serialize_for_api(updated_step))

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

    # Plan Stack routes
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

    # Batch operations route
    @bp.route('/api/plan-stack/modify', methods=['POST'])
    def modify_plan_stack():
        """Execute multiple operations atomically in a single transaction.

        Sole mutation surface for Plan Stack state. All step / layer /
        slot creation and removal flows through here; per-resource
        create/update routes have been removed.

        Request body:
        {
            "operations": [
                {"type": "create_steps",            "params": {"steps": [...]}},
                {"type": "create_layers",           "params": {"layers": [...]}},
                {"type": "add_steps_to_layers",     "params": {"additions": [...]}},
                {"type": "remove_steps_from_layers","params": {"removals": [...]}}
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

        result = storage.modify_plan_stack(operations)
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
