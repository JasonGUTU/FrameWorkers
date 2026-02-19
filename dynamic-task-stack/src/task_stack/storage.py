# In-memory storage for Frameworks Backend
# In production, this should be replaced with a proper database

from threading import Lock
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid

from .models import (
    UserMessage, Task, TaskStackEntry, TaskLayer, ExecutionPointer,
    TaskStatus, ReadingStatus, MessageSenderType, BatchOperation, BatchOperationType
)


class TaskStackStorage:
    """Thread-safe in-memory storage for tasks and messages"""
    
    def __init__(self):
        self.user_messages: Dict[str, UserMessage] = {}
        self.tasks: Dict[str, Task] = {}
        self.task_layers: List[TaskLayer] = []  # Layered task stack
        self.execution_pointer: Optional[ExecutionPointer] = None  # Current execution position
        self.user_message_counter = 0
        self.task_counter = 0
        self.lock = Lock()
    
    # User Message operations
    def create_user_message(
        self,
        content: str,
        user_id: str,
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
                user_id=user_id,
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
    
    def get_all_user_messages(
        self,
        user_id: Optional[str] = None
    ) -> List[UserMessage]:
        """Get all user messages, optionally filtered by user_id"""
        with self.lock:
            if user_id is None:
                return list(self.user_messages.values())
            return [
                msg for msg in self.user_messages.values()
                if msg.user_id == user_id
            ]
    
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
    
    def _is_task_executed(self, layer_index: int, task_index: int) -> bool:
        """Check if a task at given position has been executed"""
        if self.execution_pointer is None:
            return False
        
        exec_layer = self.execution_pointer.current_layer_index
        exec_task = self.execution_pointer.current_task_index
        
        # Task is executed if it's before current execution position
        if layer_index < exec_layer:
            return True
        if layer_index == exec_layer and task_index < exec_task:
            return True
        
        return False
    
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
            if self._is_task_executed(layer_index, task_index):
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
            if self._is_task_executed(layer_index, old_task_index):
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
    
    def modify_task_stack(
        self,
        insert_layer_index: int,
        task_ids: List[str],
        pre_hook: Optional[Dict[str, Any]] = None,
        post_hook: Optional[Dict[str, Any]] = None
    ) -> Optional[TaskLayer]:
        """
        Atomically insert a new layer at specified index and add tasks to it
        
        This is an atomic operation that:
        1. Inserts a new layer at the specified index
        2. Adds all specified tasks to the new layer
        3. Re-indexes all layers after insertion
        
        Args:
            insert_layer_index: Index where to insert the new layer
            task_ids: List of task IDs to add to the new layer
            pre_hook: Optional pre-hook for the new layer
            post_hook: Optional post-hook for the new layer
            
        Returns:
            The created TaskLayer if successful, None otherwise
            
        Note:
            - Cannot insert before executed layers
            - All task_ids must exist
            - All tasks must not already be in any layer (or this check can be relaxed)
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
            
            # Validate all task IDs exist
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
            
            # Add all tasks to the new layer
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
        with self.lock:
            return self.execution_pointer
    
    def set_execution_pointer(
        self,
        layer_index: int,
        task_index: int,
        is_executing_pre_hook: bool = False,
        is_executing_post_hook: bool = False
    ) -> bool:
        """Set execution pointer"""
        with self.lock:
            if layer_index < 0 or layer_index >= len(self.task_layers):
                return False
            
            layer = self.task_layers[layer_index]
            if task_index < 0 or task_index >= len(layer.tasks):
                return False
            
            self.execution_pointer = ExecutionPointer(
                current_layer_index=layer_index,
                current_task_index=task_index,
                is_executing_pre_hook=is_executing_pre_hook,
                is_executing_post_hook=is_executing_post_hook
            )
            return True
    
    def get_next_task(self) -> Optional[Dict[str, Any]]:
        """Get the next task to execute based on execution pointer"""
        with self.lock:
            if self.execution_pointer is None:
                # Start from the beginning
                if not self.task_layers:
                    return None
                layer = self.task_layers[0]
                if not layer.tasks:
                    return None
                return {
                    'layer_index': 0,
                    'task_index': 0,
                    'task_id': layer.tasks[0].task_id,
                    'layer': layer
                }
            
            layer_idx = self.execution_pointer.current_layer_index
            task_idx = self.execution_pointer.current_task_index
            
            # Check if we're executing hooks
            if self.execution_pointer.is_executing_pre_hook:
                # Still in pre-hook, return current task
                if layer_idx < len(self.task_layers):
                    layer = self.task_layers[layer_idx]
                    if task_idx < len(layer.tasks):
                        return {
                            'layer_index': layer_idx,
                            'task_index': task_idx,
                            'task_id': layer.tasks[task_idx].task_id,
                            'layer': layer,
                            'is_pre_hook': True
                        }
            
            if self.execution_pointer.is_executing_post_hook:
                # Still in post-hook, move to next task or layer
                if layer_idx < len(self.task_layers):
                    layer = self.task_layers[layer_idx]
                    if task_idx + 1 < len(layer.tasks):
                        # Next task in same layer
                        return {
                            'layer_index': layer_idx,
                            'task_index': task_idx + 1,
                            'task_id': layer.tasks[task_idx + 1].task_id,
                            'layer': layer
                        }
                    elif layer_idx + 1 < len(self.task_layers):
                        # Move to next layer
                        next_layer = self.task_layers[layer_idx + 1]
                        if next_layer.tasks:
                            return {
                                'layer_index': layer_idx + 1,
                                'task_index': 0,
                                'task_id': next_layer.tasks[0].task_id,
                                'layer': next_layer
                            }
            
            # Normal execution - return current task
            if layer_idx < len(self.task_layers):
                layer = self.task_layers[layer_idx]
                if task_idx < len(layer.tasks):
                    return {
                        'layer_index': layer_idx,
                        'task_index': task_idx,
                        'task_id': layer.tasks[task_idx].task_id,
                        'layer': layer
                    }
            
            return None
    
    def advance_execution_pointer(self) -> bool:
        """Advance execution pointer to next task"""
        with self.lock:
            if self.execution_pointer is None:
                if not self.task_layers:
                    return False
                self.execution_pointer = ExecutionPointer(
                    current_layer_index=0,
                    current_task_index=0,
                    is_executing_pre_hook=False,
                    is_executing_post_hook=False
                )
                return True
            
            layer_idx = self.execution_pointer.current_layer_index
            task_idx = self.execution_pointer.current_task_index
            
            if layer_idx >= len(self.task_layers):
                return False
            
            layer = self.task_layers[layer_idx]
            
            # Move to next task in same layer
            if task_idx + 1 < len(layer.tasks):
                self.execution_pointer.current_task_index = task_idx + 1
                self.execution_pointer.is_executing_pre_hook = False
                self.execution_pointer.is_executing_post_hook = False
                return True
            
            # Move to next layer
            if layer_idx + 1 < len(self.task_layers):
                next_layer = self.task_layers[layer_idx + 1]
                if next_layer.tasks:
                    self.execution_pointer.current_layer_index = layer_idx + 1
                    self.execution_pointer.current_task_index = 0
                    self.execution_pointer.is_executing_pre_hook = False
                    self.execution_pointer.is_executing_post_hook = False
                    return True
            
            # No more tasks
            return False
    
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
    
    # Internal helper methods (assume lock is already held)
    def _create_task_internal(self, description: Dict[str, Any]) -> Task:
        """Internal method to create task (assumes lock is held)"""
        self.task_counter += 1
        task_id = f"task_{self.task_counter}_{uuid.uuid4().hex[:8]}"
        now_time = datetime.now()
        task = Task(
            id=task_id,
            description=description,
            status=TaskStatus.PENDING,
            progress={},
            results=None,
            created_at=now_time,
            updated_at=now_time
        )
        self.tasks[task_id] = task
        return task
    
    def _create_layer_internal(
        self,
        layer_index: Optional[int] = None,
        pre_hook: Optional[Dict[str, Any]] = None,
        post_hook: Optional[Dict[str, Any]] = None
    ) -> TaskLayer:
        """Internal method to create layer (assumes lock is held)"""
        if layer_index is None:
            layer_index = len(self.task_layers)
        
        layer = TaskLayer(
            layer_index=layer_index,
            tasks=[],
            pre_hook=pre_hook,
            post_hook=post_hook,
            created_at=datetime.now()
        )
        
        if layer_index < len(self.task_layers):
            self.task_layers.insert(layer_index, layer)
            for i, l in enumerate(self.task_layers):
                l.layer_index = i
        else:
            self.task_layers.append(layer)
        
        return layer
    
    def _add_task_to_layer_internal(
        self,
        layer_index: int,
        task_id: str,
        insert_index: Optional[int] = None
    ) -> bool:
        """Internal method to add task to layer (assumes lock is held)"""
        if layer_index < 0 or layer_index >= len(self.task_layers):
            return False
        
        if task_id not in self.tasks:
            return False
        
        layer = self.task_layers[layer_index]
        
        if self.execution_pointer is not None:
            exec_layer = self.execution_pointer.current_layer_index
            if layer_index < exec_layer:
                return False
        
        if any(entry.task_id == task_id for entry in layer.tasks):
            return False
        
        entry = TaskStackEntry(task_id=task_id, created_at=datetime.now())
        
        if insert_index is not None:
            if insert_index < 0 or insert_index > len(layer.tasks):
                return False
            if self.execution_pointer is not None:
                if layer_index == self.execution_pointer.current_layer_index:
                    if insert_index <= self.execution_pointer.current_task_index:
                        return False
            layer.tasks.insert(insert_index, entry)
        else:
            layer.tasks.append(entry)
        
        return True
    
    def _remove_task_from_layer_internal(
        self,
        layer_index: int,
        task_id: str
    ) -> bool:
        """Internal method to remove task from layer (assumes lock is held)"""
        if layer_index < 0 or layer_index >= len(self.task_layers):
            return False
        
        layer = self.task_layers[layer_index]
        task_index = None
        for idx, entry in enumerate(layer.tasks):
            if entry.task_id == task_id:
                task_index = idx
                break
        
        if task_index is None:
            return False
        
        if self._is_task_executed(layer_index, task_index):
            return False
        
        layer.tasks.pop(task_index)
        return True
    
    def _replace_task_in_layer_internal(
        self,
        layer_index: int,
        old_task_id: str,
        new_task_id: str
    ) -> bool:
        """Internal method to replace task in layer (assumes lock is held)"""
        if layer_index < 0 or layer_index >= len(self.task_layers):
            return False
        
        if new_task_id not in self.tasks:
            return False
        
        layer = self.task_layers[layer_index]
        
        old_task_index = None
        for idx, entry in enumerate(layer.tasks):
            if entry.task_id == old_task_id:
                old_task_index = idx
                break
        
        if old_task_index is None:
            return False
        
        if self._is_task_executed(layer_index, old_task_index):
            return False
        
        if any(entry.task_id == new_task_id for entry in layer.tasks):
            return False
        
        old_task = self.tasks.get(old_task_id)
        if old_task:
            old_task.status = TaskStatus.CANCELLED
        
        layer.tasks[old_task_index] = TaskStackEntry(
            task_id=new_task_id,
            created_at=datetime.now()
        )
        
        return True
    
    def _update_layer_hooks_internal(
        self,
        layer_index: int,
        pre_hook: Optional[Dict[str, Any]] = None,
        post_hook: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Internal method to update layer hooks (assumes lock is held)"""
        if layer_index < 0 or layer_index >= len(self.task_layers):
            return False
        
        if self.execution_pointer is not None:
            exec_layer = self.execution_pointer.current_layer_index
            if layer_index < exec_layer:
                return False
        
        layer = self.task_layers[layer_index]
        if pre_hook is not None:
            layer.pre_hook = pre_hook
        if post_hook is not None:
            layer.post_hook = post_hook
        
        return True
    
    def batch_operations(self, operations: List[BatchOperation]) -> Dict[str, Any]:
        """
        Execute multiple operations atomically in a single transaction
        
        All operations are executed within a single lock, ensuring atomicity.
        If any operation fails, the entire batch fails and returns error information.
        
        Args:
            operations: List of BatchOperation objects to execute
            
        Returns:
            Dict with:
            - success: bool - Whether all operations succeeded
            - results: List[Dict] - Results for each operation
            - errors: List[Dict] - Error information for failed operations
            - created_task_ids: List[str] - IDs of created tasks (for reference)
            - created_layer_indices: List[int] - Indices of created layers (for reference)
        
        Supported operation types and their params:
        
        1. CREATE_TASKS:
           params: {
               "tasks": [
                   {"description": {...}},
                   ...
               ]
           }
           Returns: List of created task IDs
        
        2. CREATE_LAYERS:
           params: {
               "layers": [
                   {
                       "layer_index": Optional[int],
                       "pre_hook": Optional[Dict],
                       "post_hook": Optional[Dict]
                   },
                   ...
               ]
           }
           Returns: List of created layer indices
        
        3. ADD_TASKS_TO_LAYERS:
           params: {
               "additions": [
                   {
                       "layer_index": int,
                       "task_id": str,
                       "insert_index": Optional[int]
                   },
                   ...
               ]
           }
           Returns: List of success booleans
        
        4. REMOVE_TASKS_FROM_LAYERS:
           params: {
               "removals": [
                   {
                       "layer_index": int,
                       "task_id": str
                   },
                   ...
               ]
           }
           Returns: List of success booleans
        
        5. REPLACE_TASKS_IN_LAYERS:
           params: {
               "replacements": [
                   {
                       "layer_index": int,
                       "old_task_id": str,
                       "new_task_id": str
                   },
                   ...
               ]
           }
           Returns: List of success booleans
        
        6. UPDATE_LAYER_HOOKS:
           params: {
               "updates": [
                   {
                       "layer_index": int,
                       "pre_hook": Optional[Dict],
                       "post_hook": Optional[Dict]
                   },
                   ...
               ]
           }
           Returns: List of success booleans
        
        Note: For inserting a layer in the middle with tasks, use the separate
        modify_task_stack() method instead of batch operations.
        """
        results = []
        errors = []
        created_task_ids = []
        created_layer_indices = []
        
        with self.lock:
            # Execute all operations in sequence
            for idx, operation in enumerate(operations):
                try:
                    if operation.type == BatchOperationType.CREATE_TASKS:
                        task_descriptions = operation.params.get("tasks", [])
                        if not isinstance(task_descriptions, list):
                            raise ValueError("CREATE_TASKS requires 'tasks' as a list")
                        
                        created_ids = []
                        for task_desc in task_descriptions:
                            if not isinstance(task_desc, dict) or "description" not in task_desc:
                                raise ValueError("Each task must have a 'description' field")
                            
                            task = self._create_task_internal(task_desc["description"])
                            created_ids.append(task.id)
                            created_task_ids.append(task.id)
                        
                        results.append({
                            "operation_index": idx,
                            "type": operation.type.value,
                            "success": True,
                            "data": {"created_task_ids": created_ids}
                        })
                    
                    elif operation.type == BatchOperationType.CREATE_LAYERS:
                        layer_configs = operation.params.get("layers", [])
                        if not isinstance(layer_configs, list):
                            raise ValueError("CREATE_LAYERS requires 'layers' as a list")
                        
                        created_indices = []
                        for layer_config in layer_configs:
                            if not isinstance(layer_config, dict):
                                raise ValueError("Each layer config must be a dictionary")
                            
                            layer = self._create_layer_internal(
                                layer_index=layer_config.get("layer_index"),
                                pre_hook=layer_config.get("pre_hook"),
                                post_hook=layer_config.get("post_hook")
                            )
                            created_indices.append(layer.layer_index)
                            created_layer_indices.append(layer.layer_index)
                        
                        results.append({
                            "operation_index": idx,
                            "type": operation.type.value,
                            "success": True,
                            "data": {"created_layer_indices": created_indices}
                        })
                    
                    elif operation.type == BatchOperationType.ADD_TASKS_TO_LAYERS:
                        additions = operation.params.get("additions", [])
                        if not isinstance(additions, list):
                            raise ValueError("ADD_TASKS_TO_LAYERS requires 'additions' as a list")
                        
                        success_list = []
                        for addition in additions:
                            if not isinstance(addition, dict):
                                raise ValueError("Each addition must be a dictionary")
                            
                            layer_index = addition.get("layer_index")
                            task_id = addition.get("task_id")
                            insert_index = addition.get("insert_index")
                            
                            if layer_index is None or task_id is None:
                                raise ValueError("Each addition must have 'layer_index' and 'task_id'")
                            
                            success = self._add_task_to_layer_internal(layer_index, task_id, insert_index)
                            success_list.append(success)
                            
                            if not success:
                                raise ValueError(
                                    f"Failed to add task {task_id} to layer {layer_index}"
                                )
                        
                        results.append({
                            "operation_index": idx,
                            "type": operation.type.value,
                            "success": True,
                            "data": {"success_list": success_list}
                        })
                    
                    elif operation.type == BatchOperationType.REMOVE_TASKS_FROM_LAYERS:
                        removals = operation.params.get("removals", [])
                        if not isinstance(removals, list):
                            raise ValueError("REMOVE_TASKS_FROM_LAYERS requires 'removals' as a list")
                        
                        success_list = []
                        for removal in removals:
                            if not isinstance(removal, dict):
                                raise ValueError("Each removal must be a dictionary")
                            
                            layer_index = removal.get("layer_index")
                            task_id = removal.get("task_id")
                            
                            if layer_index is None or task_id is None:
                                raise ValueError("Each removal must have 'layer_index' and 'task_id'")
                            
                            success = self._remove_task_from_layer_internal(layer_index, task_id)
                            success_list.append(success)
                            
                            if not success:
                                raise ValueError(
                                    f"Failed to remove task {task_id} from layer {layer_index}"
                                )
                        
                        results.append({
                            "operation_index": idx,
                            "type": operation.type.value,
                            "success": True,
                            "data": {"success_list": success_list}
                        })
                    
                    elif operation.type == BatchOperationType.REPLACE_TASKS_IN_LAYERS:
                        replacements = operation.params.get("replacements", [])
                        if not isinstance(replacements, list):
                            raise ValueError("REPLACE_TASKS_IN_LAYERS requires 'replacements' as a list")
                        
                        success_list = []
                        for replacement in replacements:
                            if not isinstance(replacement, dict):
                                raise ValueError("Each replacement must be a dictionary")
                            
                            layer_index = replacement.get("layer_index")
                            old_task_id = replacement.get("old_task_id")
                            new_task_id = replacement.get("new_task_id")
                            
                            if layer_index is None or old_task_id is None or new_task_id is None:
                                raise ValueError(
                                    "Each replacement must have 'layer_index', 'old_task_id', and 'new_task_id'"
                                )
                            
                            success = self._replace_task_in_layer_internal(layer_index, old_task_id, new_task_id)
                            success_list.append(success)
                            
                            if not success:
                                raise ValueError(
                                    f"Failed to replace task {old_task_id} with {new_task_id} in layer {layer_index}"
                                )
                        
                        results.append({
                            "operation_index": idx,
                            "type": operation.type.value,
                            "success": True,
                            "data": {"success_list": success_list}
                        })
                    
                    elif operation.type == BatchOperationType.UPDATE_LAYER_HOOKS:
                        updates = operation.params.get("updates", [])
                        if not isinstance(updates, list):
                            raise ValueError("UPDATE_LAYER_HOOKS requires 'updates' as a list")
                        
                        success_list = []
                        for update in updates:
                            if not isinstance(update, dict):
                                raise ValueError("Each update must be a dictionary")
                            
                            layer_index = update.get("layer_index")
                            
                            if layer_index is None:
                                raise ValueError("Each update must have 'layer_index'")
                            
                            success = self._update_layer_hooks_internal(
                                layer_index,
                                update.get("pre_hook"),
                                update.get("post_hook")
                            )
                            success_list.append(success)
                            
                            if not success:
                                raise ValueError(
                                    f"Failed to update hooks for layer {layer_index}"
                                )
                        
                        results.append({
                            "operation_index": idx,
                            "type": operation.type.value,
                            "success": True,
                            "data": {"success_list": success_list}
                        })
                    
                    else:
                        raise ValueError(f"Unknown operation type: {operation.type}")
                
                except Exception as e:
                    # Record error and continue (or could stop here)
                    errors.append({
                        "operation_index": idx,
                        "type": operation.type.value if operation else "unknown",
                        "error": str(e),
                        "params": operation.params if operation else None
                    })
                    results.append({
                        "operation_index": idx,
                        "type": operation.type.value if operation else "unknown",
                        "success": False,
                        "error": str(e)
                    })
            
            # Return summary
            all_success = len(errors) == 0
            return {
                "success": all_success,
                "results": results,
                "errors": errors,
                "created_task_ids": created_task_ids,
                "created_layer_indices": created_layer_indices
            }


# Global storage instance
storage = TaskStackStorage()
