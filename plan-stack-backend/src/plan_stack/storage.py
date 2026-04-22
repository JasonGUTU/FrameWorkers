# In-memory Plan Stack domain service.
# It operates on a thread-safe in-memory state store.
# One PlanStep <-> one planned agent execution; step_id is the canonical id.

from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid

from .models import (
    UserMessage, PlanStep, PlanLayer, ExecutionPointer,
    PlanStepStatus, ReadingStatus, MessageSenderType, BatchOperation
)
from .batch_mutator import PlanStackBatchMutator
from .execution_flow import PlanStackExecutionFlow
from .state_store import PlanStackStateStore


class PlanStackService:
    """Plan Stack domain service backed by an in-memory state store."""

    def __init__(self, state_store: Optional[PlanStackStateStore] = None):
        self._state = state_store or PlanStackStateStore()
        self._batch_mutator = PlanStackBatchMutator(self._state)
        self._execution_flow = PlanStackExecutionFlow(self._state)

    # User Message operations
    def create_user_message(
        self,
        content: str,
        sender_type: MessageSenderType = MessageSenderType.USER,
        step_id: Optional[str] = None,
    ) -> UserMessage:
        """Create a new user message."""
        with self._state.lock:
            self._state.user_message_counter += 1
            msg_id = f"msg_{self._state.user_message_counter}_{uuid.uuid4().hex[:8]}"
            message = UserMessage(
                id=msg_id,
                content=content,
                timestamp=datetime.now(),
                sender_type=sender_type,
                director_read_status=ReadingStatus.UNREAD,
                user_read_status=ReadingStatus.UNREAD,
                step_id=step_id,
            )
            self._state.user_messages[msg_id] = message
            return message

    def get_all_user_messages(self) -> List[UserMessage]:
        """Get all user messages."""
        with self._state.lock:
            return list(self._state.user_messages.values())

    def get_unread_messages(
        self,
        sender_type: Optional[MessageSenderType] = None,
        check_director_read: bool = False,
        check_user_read: bool = False,
    ) -> List[UserMessage]:
        """Get unread messages filtered by sender_type and reader-role flags.

        ``check_director_read`` / ``check_user_read`` select which read-status
        field to match against ``UNREAD``. Caller is expected to pass at
        least one as True — this layer does no fallback defaulting.
        """
        with self._state.lock:
            messages = list(self._state.user_messages.values())

            if sender_type is not None:
                messages = [msg for msg in messages if msg.sender_type == sender_type]

            result = []
            for msg in messages:
                is_unread = False
                if check_director_read and msg.director_read_status == ReadingStatus.UNREAD:
                    is_unread = True
                if check_user_read and msg.user_read_status == ReadingStatus.UNREAD:
                    is_unread = True
                if is_unread:
                    result.append(msg)
            return result

    def update_message_read_status(
        self,
        msg_id: str,
        director_read_status: Optional[ReadingStatus] = None,
        user_read_status: Optional[ReadingStatus] = None,
    ) -> Optional[UserMessage]:
        """Update read status of a message (mutates in place; None = leave alone)."""
        with self._state.lock:
            msg = self._state.user_messages.get(msg_id)
            if msg is None:
                return None
            if director_read_status is not None:
                msg.director_read_status = director_read_status
            if user_read_status is not None:
                msg.user_read_status = user_read_status
            return msg

    # Task operations
    def get_step(self, step_id: str) -> Optional[PlanStep]:
        """Get a task by ID."""
        with self._state.lock:
            return self._state.plan_steps.get(step_id)

    def get_all_steps(self) -> List[PlanStep]:
        """Get all tasks."""
        with self._state.lock:
            return list(self._state.plan_steps.values())

    def update_step_status(
        self,
        step_id: str,
        status: PlanStepStatus,
    ) -> Optional[PlanStep]:
        """Update a plan step's status (mutates in place)."""
        with self._state.lock:
            step = self._state.plan_steps.get(step_id)
            if step is None:
                return None
            step.status = status
            step.updated_at = datetime.now()
            return step

    # Plan Layer operations
    def get_all_layers(self) -> List[PlanLayer]:
        """Get all layers."""
        with self._state.lock:
            return self._state.plan_layers.copy()

    # Execution pointer operations
    def get_execution_pointer(self) -> Optional[ExecutionPointer]:
        return self._execution_flow.get_execution_pointer()

    def set_execution_pointer(
        self,
        layer_index: int,
        step_index: int,
    ) -> bool:
        return self._execution_flow.set_execution_pointer(
            layer_index=layer_index,
            step_index=step_index,
        )

    def get_next_step(self) -> Optional[Dict[str, Any]]:
        return self._execution_flow.get_next_step()

    def advance_execution_pointer(self) -> bool:
        return self._execution_flow.advance_execution_pointer()

    def modify_plan_stack(self, operations: List[BatchOperation]) -> Dict[str, Any]:
        """Execute batch modifications in one atomic operation."""
        return self._batch_mutator.modify_plan_stack(operations)


# Preferred global service instance (single canonical name)
storage = PlanStackService()
