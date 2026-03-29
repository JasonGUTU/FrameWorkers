# In-memory Task Stack domain service.
# It operates on a thread-safe in-memory state store.

from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid

from .models import (
    UserMessage, Task, TaskStackEntry, TaskLayer, ExecutionPointer,
    TaskStatus, ReadingStatus, MessageSenderType, BatchOperation
)
from .batch_mutator import TaskStackBatchMutator
from .execution_flow import TaskStackExecutionFlow
from .state_store import TaskStackStateStore


class TaskStackService:
    """Task Stack domain service backed by an in-memory state store."""

    def __init__(self, state_store: Optional[TaskStackStateStore] = None):
        self._state = state_store or TaskStackStateStore()
        # Keep attribute names stable to avoid touching method bodies.
        self.user_messages = self._state.user_messages
        self.tasks = self._state.tasks
        self.task_layers = self._state.task_layers
        self.lock = self._state.lock
        self._batch_mutator = TaskStackBatchMutator(self._state)
        self._execution_flow = TaskStackExecutionFlow(self._state)

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
    def task_counter(self) -> int:
        return self._state.task_counter

    @task_counter.setter
    def task_counter(self, value: int) -> None:
        self._state.task_counter = value
    
    # User Message operations
    def create_user_message(
        self,
        content: str,
        sender_type: MessageSenderType = MessageSenderType.USER,
        task_id: Optional[str] = None
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
                task_id=task_id
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
                task_id=msg.task_id
            )
            self.user_messages[msg_id] = updated_msg
            return updated_msg
    
    # Task operations
    def create_task(
        self,
        description: Dict[str, Any]
    ) -> Task:
        """Create a new task (does not add to stack automatically)"""
        with self.lock:
            self.task_counter += 1
            task_id = f"task_{self.task_counter}_{uuid.uuid4().hex[:8]}"
            now_time = datetime.now()
            task = Task(
                id=task_id,
                description=description,
                status=TaskStatus.PENDING,
                progress={},  # Empty dict for message collection
                results=None,
                created_at=now_time,
                updated_at=now_time
            )
            self.tasks[task_id] = task
            return task
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID"""
        with self.lock:
            return self.tasks.get(task_id)
    
    def get_all_tasks(self) -> List[Task]:
        """Get all tasks"""
        with self.lock:
            return list(self.tasks.values())
    
    def update_task(
        self,
        task_id: str,
        description: Optional[Dict[str, Any]] = None,
        status: Optional[TaskStatus] = None,
        progress: Optional[Dict[str, Any]] = None,
        results: Optional[Dict[str, Any]] = None
    ) -> Optional[Task]:
        """Update a task"""
        with self.lock:
            task = self.tasks.get(task_id)
            if task is None:
                return None
            
            new_description = (
                description if description is not None else task.description
            )
            new_status = status if status is not None else task.status
            new_progress = progress if progress is not None else task.progress
            new_results = results if results is not None else task.results
            
            updated_task = Task(
                id=task.id,
                description=new_description,
                status=new_status,
                progress=new_progress,
                results=new_results,
                created_at=task.created_at,
                updated_at=datetime.now()
            )
            self.tasks[task_id] = updated_task
            return updated_task
    
    def delete_task(self, task_id: str) -> bool:
        """Delete a task and remove it from all layers"""
        with self.lock:
            if task_id not in self.tasks:
                return False
            
            del self.tasks[task_id]
            
            # Remove task from all layers
            for layer in self.task_layers:
                layer.tasks = [
                    entry for entry in layer.tasks
                    if entry.task_id != task_id
                ]
            
            return True
    
    # Task Layer operations
    def create_layer(
        self,
        layer_index: Optional[int] = None,
        pre_hook: Optional[Dict[str, Any]] = None,
        post_hook: Optional[Dict[str, Any]] = None
    ) -> TaskLayer:
        """Create a new task layer"""
        with self.lock:
            if layer_index is None:
                layer_index = len(self.task_layers)
            
            # Insert layer at specified index
            layer = TaskLayer(
                layer_index=layer_index,
                tasks=[],
                pre_hook=pre_hook,
                post_hook=post_hook,
                created_at=datetime.now()
            )
            
            # Adjust layer indices if inserting in the middle
            if layer_index < len(self.task_layers):
                # Insert at specified position
                self.task_layers.insert(layer_index, layer)
                # Re-index all layers
                for i, l in enumerate(self.task_layers):
                    l.layer_index = i
            else:
                # Append to end
                self.task_layers.append(layer)
            
            return layer
    
    def add_task_to_layer(
        self,
        layer_index: int,
        task_id: str,
        insert_index: Optional[int] = None
    ) -> bool:
        """Add a task to a specific layer (only if layer not executed)"""
        with self.lock:
            if layer_index < 0 or layer_index >= len(self.task_layers):
                return False
            
            if task_id not in self.tasks:
                return False
            
            layer = self.task_layers[layer_index]
            
            # Check if layer has been executed
            if self.execution_pointer is not None:
                exec_layer = self.execution_pointer.current_layer_index
                if layer_index < exec_layer:
                    return False  # Cannot add to executed layer
            
            # Check if task already exists in this layer
            if any(entry.task_id == task_id for entry in layer.tasks):
                return False
            
            entry = TaskStackEntry(task_id=task_id, created_at=datetime.now())
            
            if insert_index is not None:
                # Check if insert position is valid and not executed
                if insert_index < 0 or insert_index > len(layer.tasks):
                    return False
                if self.execution_pointer is not None:
                    if layer_index == self.execution_pointer.current_layer_index:
                        if insert_index <= self.execution_pointer.current_task_index:
                            return False  # Cannot insert before executed tasks
                layer.tasks.insert(insert_index, entry)
            else:
                layer.tasks.append(entry)
            
            return True
    
    def remove_task_from_layer(
        self,
        layer_index: int,
        task_id: str
    ) -> bool:
        """Remove a task from a specific layer (only if not executed)"""
        with self.lock:
            if layer_index < 0 or layer_index >= len(self.task_layers):
                return False
            
            layer = self.task_layers[layer_index]
            # Find task index
            task_index = None
            for idx, entry in enumerate(layer.tasks):
                if entry.task_id == task_id:
                    task_index = idx
                    break
            
            if task_index is None:
                return False
            
            # Check if task has been executed
            if self._batch_mutator.is_task_executed(layer_index, task_index):
                return False  # Cannot remove executed task
            
            # Remove task
            layer.tasks.pop(task_index)
            return True
    
    def get_layer(self, layer_index: int) -> Optional[TaskLayer]:
        """Get a layer by index"""
        with self.lock:
            if layer_index < 0 or layer_index >= len(self.task_layers):
                return None
            return self.task_layers[layer_index]
    
    def get_all_layers(self) -> List[TaskLayer]:
        """Get all layers"""
        with self.lock:
            return self.task_layers.copy()
    
    def replace_task_in_layer(
        self,
        layer_index: int,
        old_task_id: str,
        new_task_id: str
    ) -> bool:
        """Atomically replace a task in a layer (cancel old, add new)"""
        with self.lock:
            if layer_index < 0 or layer_index >= len(self.task_layers):
                return False
            
            if new_task_id not in self.tasks:
                return False
            
            layer = self.task_layers[layer_index]
            
            # Find old task index
            old_task_index = None
            for idx, entry in enumerate(layer.tasks):
                if entry.task_id == old_task_id:
                    old_task_index = idx
                    break
            
            if old_task_index is None:
                return False
            
            # Check if task has been executed
            if self._batch_mutator.is_task_executed(layer_index, old_task_index):
                return False  # Cannot replace executed task
            
            # Check if new task already exists in this layer
            if any(entry.task_id == new_task_id for entry in layer.tasks):
                return False
            
            # Cancel old task
            old_task = self.tasks.get(old_task_id)
            if old_task:
                old_task.status = TaskStatus.CANCELLED
            
            # Replace task entry
            layer.tasks[old_task_index] = TaskStackEntry(
                task_id=new_task_id,
                created_at=datetime.now()
            )
            
            return True
    
    def update_layer_hooks(
        self,
        layer_index: int,
        pre_hook: Optional[Dict[str, Any]] = None,
        post_hook: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update hooks for a layer (only if layer not executed)"""
        with self.lock:
            if layer_index < 0 or layer_index >= len(self.task_layers):
                return False
            
            # Check if layer has been executed
            if self.execution_pointer is not None:
                exec_layer = self.execution_pointer.current_layer_index
                if layer_index < exec_layer:
                    return False  # Cannot update hooks for executed layer
            
            layer = self.task_layers[layer_index]
            if pre_hook is not None:
                layer.pre_hook = pre_hook
            if post_hook is not None:
                layer.post_hook = post_hook
            
            return True
    
    def insert_layer_with_tasks(
        self,
        insert_layer_index: int,
        task_ids: Optional[List[str]] = None,
        pre_hook: Optional[Dict[str, Any]] = None,
        post_hook: Optional[Dict[str, Any]] = None
    ) -> Optional[TaskLayer]:
        """
        Atomically insert a new layer at specified index and optionally add tasks to it
        
        This is an atomic operation that:
        1. Inserts a new layer at the specified index
        2. Optionally adds all specified tasks to the new layer (if task_ids provided)
        3. Re-indexes all layers after insertion
        
        Args:
            insert_layer_index: Index where to insert the new layer
            task_ids: Optional list of task IDs to add to the new layer (can be empty or None to insert empty layer)
            pre_hook: Optional pre-hook for the new layer
            post_hook: Optional post-hook for the new layer
            
        Returns:
            The created TaskLayer if successful, None otherwise
            
        Note:
            - Cannot insert before executed layers
            - If task_ids is provided, all task_ids must exist
            - If task_ids is None or empty, an empty layer will be inserted
        """
        with self.lock:
            # Validate insert index
            if insert_layer_index < 0:
                return None
            
            # Check if we're trying to insert before executed layers
            if self.execution_pointer is not None:
                exec_layer = self.execution_pointer.current_layer_index
                if insert_layer_index < exec_layer:
                    return None  # Cannot insert before executed layer
            
            # Validate all task IDs exist (only if task_ids is provided and not empty)
            if task_ids:
                for task_id in task_ids:
                    if task_id not in self.tasks:
                        return None
            
            # Create new layer
            layer = TaskLayer(
                layer_index=insert_layer_index,
                tasks=[],
                pre_hook=pre_hook,
                post_hook=post_hook,
                created_at=datetime.now()
            )
            
            # Insert layer at specified position
            if insert_layer_index <= len(self.task_layers):
                self.task_layers.insert(insert_layer_index, layer)
                # Re-index all layers
                for i, l in enumerate(self.task_layers):
                    l.layer_index = i
            else:
                # If index is beyond current layers, append to end
                layer.layer_index = len(self.task_layers)
                self.task_layers.append(layer)
            
            # Add all tasks to the new layer (if task_ids provided)
            if task_ids:
                for task_id in task_ids:
                    # Check if task already exists in this layer (shouldn't happen, but safety check)
                    if any(entry.task_id == task_id for entry in layer.tasks):
                        continue
                    
                    entry = TaskStackEntry(task_id=task_id, created_at=datetime.now())
                    layer.tasks.append(entry)
            
            return layer
    
    # Execution pointer operations
    def get_execution_pointer(self) -> Optional[ExecutionPointer]:
        """Get current execution pointer"""
        return self._execution_flow.get_execution_pointer()
    
    def set_execution_pointer(
        self,
        layer_index: int,
        task_index: int,
        is_executing_pre_hook: bool = False,
        is_executing_post_hook: bool = False
    ) -> bool:
        """Set execution pointer"""
        return self._execution_flow.set_execution_pointer(
            layer_index=layer_index,
            task_index=task_index,
            is_executing_pre_hook=is_executing_pre_hook,
            is_executing_post_hook=is_executing_post_hook,
        )
    
    def get_next_task(self) -> Optional[Dict[str, Any]]:
        """Get the next task to execute based on execution pointer"""
        return self._execution_flow.get_next_task()
    
    def advance_execution_pointer(self) -> bool:
        """Advance execution pointer to next task"""
        return self._execution_flow.advance_execution_pointer()
    
    def is_new_task(self, msg_id: str) -> bool:
        """Check if message is associated with a new (pending) task"""
        with self.lock:
            msg = self.user_messages.get(msg_id)
            if msg is None or msg.task_id is None:
                return False
            
            task = self.tasks.get(msg.task_id)
            return (
                task is not None and
                task.status == TaskStatus.PENDING
            )
    
    def modify_task_stack(self, operations: List[BatchOperation]) -> Dict[str, Any]:
        """Execute batch modifications in one atomic operation."""
        return self._batch_mutator.modify_task_stack(operations)


# Preferred global service instance (single canonical name)
storage = TaskStackService()
