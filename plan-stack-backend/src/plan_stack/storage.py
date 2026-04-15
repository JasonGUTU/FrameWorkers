# In-memory Plan Stack domain service.
# It operates on a thread-safe in-memory state store.
# One PlanStep <-> one planned agent execution; step_id is the canonical id.

from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid

from .models import (
    UserMessage, PlanStep, PlanStepEntry, PlanLayer, ExecutionPointer,
    PlanStepStatus, ReadingStatus, MessageSenderType, BatchOperation
)
from .batch_mutator import PlanStackBatchMutator
from .execution_flow import PlanStackExecutionFlow
from .state_store import PlanStackStateStore


class PlanStackService:
    """Plan Stack domain service backed by an in-memory state store."""

    def __init__(self, state_store: Optional[PlanStackStateStore] = None):
        self._state = state_store or PlanStackStateStore()
        # Keep attribute names stable to avoid touching method bodies.
        self.user_messages = self._state.user_messages
        self.plan_steps = self._state.plan_steps
        self.plan_layers = self._state.plan_layers
        self.lock = self._state.lock
        self._batch_mutator = PlanStackBatchMutator(self._state)
        self._execution_flow = PlanStackExecutionFlow(self._state)

    @property
    def execution_pointer(self) -> Optional[ExecutionPointer]:
        return self._state.execution_pointer

    @execution_pointer.setter
    def execution_pointer(self, value: Optional[ExecutionPointer]) -> None:
        self._state.execution_pointer = value

    @property
    def user_message_counter(self) -> int:
        return self._state.user_message_counter

    @user_message_counter.setter
    def user_message_counter(self, value: int) -> None:
        self._state.user_message_counter = value

    @property
    def plan_step_counter(self) -> int:
        return self._state.plan_step_counter

    @plan_step_counter.setter
    def plan_step_counter(self, value: int) -> None:
        self._state.plan_step_counter = value
    
    # User Message operations
    def create_user_message(
        self,
        content: str,
        sender_type: MessageSenderType = MessageSenderType.USER,
        step_id: Optional[str] = None
    ) -> UserMessage:
        """Create a new user message"""
        with self.lock:
            self.user_message_counter += 1
            msg_id = f"msg_{self.user_message_counter}_{uuid.uuid4().hex[:8]}"
            message = UserMessage(
                id=msg_id,
                content=content,
                timestamp=datetime.now(),
                user_id="user",  # Single user system, fixed user_id
                sender_type=sender_type,
                director_read_status=ReadingStatus.UNREAD,
                user_read_status=ReadingStatus.UNREAD,
                step_id=step_id
            )
            self.user_messages[msg_id] = message
            return message
    
    def get_user_message(self, msg_id: str) -> Optional[UserMessage]:
        """Get a user message by ID"""
        with self.lock:
            return self.user_messages.get(msg_id)
    
    def get_all_user_messages(self) -> List[UserMessage]:
        """Get all user messages"""
        with self.lock:
            return list(self.user_messages.values())
    
    def get_unread_messages(
        self,
        sender_type: Optional[MessageSenderType] = None,
        check_director_read: bool = False,
        check_user_read: bool = False
    ) -> List[UserMessage]:
        """
        Get unread messages with optional filters
        
        Args:
            sender_type: Optional sender type filter (director, subagent, user)
            check_director_read: If True, filter by director_read_status == UNREAD
            check_user_read: If True, filter by user_read_status == UNREAD
            
        Returns:
            List of unread UserMessage objects
            
        Note:
            At least one of check_director_read or check_user_read must be True.
            If neither is specified, defaults to check_director_read=True.
        """
        with self.lock:
            if not check_director_read and not check_user_read:
                # If neither is specified, default to check_director_read
                check_director_read = True
            
            messages = list(self.user_messages.values())
            
            # Filter by sender_type if provided
            if sender_type is not None:
                messages = [msg for msg in messages if msg.sender_type == sender_type]
            
            # Filter by read status
            result = []
            for msg in messages:
                is_unread = False
                
                # Check director read status
                if check_director_read and msg.director_read_status == ReadingStatus.UNREAD:
                    is_unread = True
                
                # Check user read status (single user system, no need to filter by user_id)
                if check_user_read and msg.user_read_status == ReadingStatus.UNREAD:
                    is_unread = True
                
                if is_unread:
                    result.append(msg)
            
            return result
    
    def update_message_read_status(
        self,
        msg_id: str,
        director_read_status: Optional[ReadingStatus] = None,
        user_read_status: Optional[ReadingStatus] = None
    ) -> Optional[UserMessage]:
        """Update read status of a message"""
        with self.lock:
            msg = self.user_messages.get(msg_id)
            if msg is None:
                return None
            
            new_director_status = (
                director_read_status if director_read_status is not None
                else msg.director_read_status
            )
            new_user_status = (
                user_read_status if user_read_status is not None
                else msg.user_read_status
            )
            
            updated_msg = UserMessage(
                id=msg.id,
                content=msg.content,
                timestamp=msg.timestamp,
                user_id=msg.user_id,
                sender_type=msg.sender_type,
                director_read_status=new_director_status,
                user_read_status=new_user_status,
                step_id=msg.step_id
            )
            self.user_messages[msg_id] = updated_msg
            return updated_msg
    
    # Task operations
    def create_step(
        self,
        description: Dict[str, Any]
    ) -> PlanStep:
        """Create a new task (does not add to stack automatically)"""
        with self.lock:
            self.plan_step_counter += 1
            step_id = f"step_{self.plan_step_counter}_{uuid.uuid4().hex[:8]}"
            now_time = datetime.now()
            step = PlanStep(
                id=step_id,
                description=description,
                status=PlanStepStatus.PENDING,
                progress={},  # Empty dict for message collection
                results=None,
                created_at=now_time,
                updated_at=now_time
            )
            self.plan_steps[step_id] = step
            return step
    
    def get_step(self, step_id: str) -> Optional[PlanStep]:
        """Get a task by ID"""
        with self.lock:
            return self.plan_steps.get(step_id)
    
    def get_all_steps(self) -> List[PlanStep]:
        """Get all tasks"""
        with self.lock:
            return list(self.plan_steps.values())
    
    def update_step(
        self,
        step_id: str,
        description: Optional[Dict[str, Any]] = None,
        status: Optional[PlanStepStatus] = None,
        progress: Optional[Dict[str, Any]] = None,
        results: Optional[Dict[str, Any]] = None
    ) -> Optional[PlanStep]:
        """Update a task"""
        with self.lock:
            step = self.plan_steps.get(step_id)
            if step is None:
                return None

            new_description = (
                description if description is not None else step.description
            )
            new_status = status if status is not None else step.status
            new_progress = progress if progress is not None else step.progress
            new_results = results if results is not None else step.results

            updated_step = PlanStep(
                id=step.id,
                description=new_description,
                status=new_status,
                progress=new_progress,
                results=new_results,
                created_at=step.created_at,
                updated_at=datetime.now()
            )
            self.plan_steps[step_id] = updated_step
            return updated_step
    
    # Plan Layer operations
    def create_layer(
        self,
        layer_index: Optional[int] = None,
    ) -> PlanLayer:
        """Create a new plan layer"""
        with self.lock:
            if layer_index is None:
                layer_index = len(self.plan_layers)

            layer = PlanLayer(
                layer_index=layer_index,
                steps=[],
                created_at=datetime.now()
            )
            
            # Adjust layer indices if inserting in the middle
            if layer_index < len(self.plan_layers):
                # Insert at specified position
                self.plan_layers.insert(layer_index, layer)
                # Re-index all layers
                for i, l in enumerate(self.plan_layers):
                    l.layer_index = i
            else:
                # Append to end
                self.plan_layers.append(layer)
            
            return layer
    
    def add_step_to_layer(
        self,
        layer_index: int,
        step_id: str,
        insert_index: Optional[int] = None
    ) -> bool:
        """Add a task to a specific layer (only if layer not executed)"""
        with self.lock:
            if layer_index < 0 or layer_index >= len(self.plan_layers):
                return False
            
            if step_id not in self.plan_steps:
                return False
            
            layer = self.plan_layers[layer_index]
            
            # Check if layer has been executed
            if self.execution_pointer is not None:
                exec_layer = self.execution_pointer.current_layer_index
                if layer_index < exec_layer:
                    return False  # Cannot add to executed layer
            
            # Check if task already exists in this layer
            if any(entry.step_id == step_id for entry in layer.steps):
                return False
            
            entry = PlanStepEntry(step_id=step_id, created_at=datetime.now())
            
            if insert_index is not None:
                # Check if insert position is valid and not executed
                if insert_index < 0 or insert_index > len(layer.steps):
                    return False
                if self.execution_pointer is not None:
                    if layer_index == self.execution_pointer.current_layer_index:
                        if insert_index <= self.execution_pointer.current_step_index:
                            return False  # Cannot insert before executed tasks
                layer.steps.insert(insert_index, entry)
            else:
                layer.steps.append(entry)
            
            return True
    
    def get_layer(self, layer_index: int) -> Optional[PlanLayer]:
        """Get a layer by index"""
        with self.lock:
            if layer_index < 0 or layer_index >= len(self.plan_layers):
                return None
            return self.plan_layers[layer_index]
    
    def get_all_layers(self) -> List[PlanLayer]:
        """Get all layers"""
        with self.lock:
            return self.plan_layers.copy()
    
    # Execution pointer operations
    def get_execution_pointer(self) -> Optional[ExecutionPointer]:
        """Get current execution pointer"""
        return self._execution_flow.get_execution_pointer()
    
    def set_execution_pointer(
        self,
        layer_index: int,
        step_index: int,
    ) -> bool:
        """Set execution pointer"""
        return self._execution_flow.set_execution_pointer(
            layer_index=layer_index,
            step_index=step_index,
        )
    
    def get_next_step(self) -> Optional[Dict[str, Any]]:
        """Get the next task to execute based on execution pointer"""
        return self._execution_flow.get_next_step()
    
    def advance_execution_pointer(self) -> bool:
        """Advance execution pointer to next task"""
        return self._execution_flow.advance_execution_pointer()
    
    def modify_plan_stack(self, operations: List[BatchOperation]) -> Dict[str, Any]:
        """Execute batch modifications in one atomic operation."""
        return self._batch_mutator.modify_plan_stack(operations)


# Preferred global service instance (single canonical name)
storage = PlanStackService()
