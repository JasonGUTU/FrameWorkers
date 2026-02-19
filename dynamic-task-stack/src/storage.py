# In-memory storage for Dynamic Task Stack
# In production, this should be replaced with a proper database

from threading import Lock
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid

from .models import (
    UserMessage, Task, TaskStackEntry, TaskLayer, ExecutionPointer,
    TaskStatus, ReadingStatus
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
                worker_read_status=ReadingStatus.UNREAD,
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
        worker_read_status: Optional[ReadingStatus] = None,
        user_read_status: Optional[ReadingStatus] = None
    ) -> Optional[UserMessage]:
        """Update read status of a message"""
        with self.lock:
            msg = self.user_messages.get(msg_id)
            if msg is None:
                return None
            
            new_worker_status = (
                worker_read_status if worker_read_status is not None
                else msg.worker_read_status
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
                worker_read_status=new_worker_status,
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


# Global storage instance
storage = TaskStackStorage()
