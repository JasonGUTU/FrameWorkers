"""Batch mutation and internal write helpers for Task Stack."""

from datetime import datetime
from typing import Any, Dict, List, Optional
import uuid

from .models import (
    BatchOperation,
    BatchOperationType,
    Task,
    TaskLayer,
    TaskStackEntry,
    TaskStatus,
)
from .state_store import TaskStackStateStore


class TaskStackBatchMutator:
    """Encapsulates atomic multi-step Task Stack mutations."""

    def __init__(self, state_store: TaskStackStateStore) -> None:
        self._state = state_store

    def is_task_executed(self, layer_index: int, task_index: int) -> bool:
        """Check whether a task position has already been executed."""
        pointer = self._state.execution_pointer
        if pointer is None:
            return False

        if layer_index < pointer.current_layer_index:
            return True
        if layer_index == pointer.current_layer_index and task_index < pointer.current_task_index:
            return True

        return False

    def create_task_internal(self, description: Dict[str, Any]) -> Task:
        """Create task (assumes lock is held)."""
        self._state.task_counter += 1
        task_id = f"task_{self._state.task_counter}_{uuid.uuid4().hex[:8]}"
        now_time = datetime.now()
        task = Task(
            id=task_id,
            description=description,
            status=TaskStatus.PENDING,
            progress={},
            results=None,
            created_at=now_time,
            updated_at=now_time,
        )
        self._state.tasks[task_id] = task
        return task

    def create_layer_internal(
        self,
        layer_index: Optional[int] = None,
        pre_hook: Optional[Dict[str, Any]] = None,
        post_hook: Optional[Dict[str, Any]] = None,
    ) -> TaskLayer:
        """Create layer (assumes lock is held)."""
        if layer_index is None:
            layer_index = len(self._state.task_layers)

        layer = TaskLayer(
            layer_index=layer_index,
            tasks=[],
            pre_hook=pre_hook,
            post_hook=post_hook,
            created_at=datetime.now(),
        )

        if layer_index < len(self._state.task_layers):
            self._state.task_layers.insert(layer_index, layer)
            for i, existing_layer in enumerate(self._state.task_layers):
                existing_layer.layer_index = i
        else:
            self._state.task_layers.append(layer)

        return layer

    def add_task_to_layer_internal(
        self,
        layer_index: int,
        task_id: str,
        insert_index: Optional[int] = None,
    ) -> bool:
        """Add task to layer (assumes lock is held)."""
        if layer_index < 0 or layer_index >= len(self._state.task_layers):
            return False

        if task_id not in self._state.tasks:
            return False

        layer = self._state.task_layers[layer_index]

        if self._state.execution_pointer is not None:
            if layer_index < self._state.execution_pointer.current_layer_index:
                return False

        if any(entry.task_id == task_id for entry in layer.tasks):
            return False

        entry = TaskStackEntry(task_id=task_id, created_at=datetime.now())

        if insert_index is not None:
            if insert_index < 0 or insert_index > len(layer.tasks):
                return False
            if self._state.execution_pointer is not None:
                if layer_index == self._state.execution_pointer.current_layer_index:
                    if insert_index <= self._state.execution_pointer.current_task_index:
                        return False
            layer.tasks.insert(insert_index, entry)
        else:
            layer.tasks.append(entry)

        return True

    def remove_task_from_layer_internal(self, layer_index: int, task_id: str) -> bool:
        """Remove task from layer (assumes lock is held)."""
        if layer_index < 0 or layer_index >= len(self._state.task_layers):
            return False

        layer = self._state.task_layers[layer_index]
        task_index = None
        for idx, entry in enumerate(layer.tasks):
            if entry.task_id == task_id:
                task_index = idx
                break

        if task_index is None:
            return False

        if self.is_task_executed(layer_index, task_index):
            return False

        layer.tasks.pop(task_index)
        return True

    def replace_task_in_layer_internal(
        self, layer_index: int, old_task_id: str, new_task_id: str
    ) -> bool:
        """Replace task in layer (assumes lock is held)."""
        if layer_index < 0 or layer_index >= len(self._state.task_layers):
            return False

        if new_task_id not in self._state.tasks:
            return False

        layer = self._state.task_layers[layer_index]
        old_task_index = None
        for idx, entry in enumerate(layer.tasks):
            if entry.task_id == old_task_id:
                old_task_index = idx
                break

        if old_task_index is None:
            return False

        if self.is_task_executed(layer_index, old_task_index):
            return False

        if any(entry.task_id == new_task_id for entry in layer.tasks):
            return False

        old_task = self._state.tasks.get(old_task_id)
        if old_task:
            old_task.status = TaskStatus.CANCELLED

        layer.tasks[old_task_index] = TaskStackEntry(
            task_id=new_task_id,
            created_at=datetime.now(),
        )
        return True

    def update_layer_hooks_internal(
        self,
        layer_index: int,
        pre_hook: Optional[Dict[str, Any]] = None,
        post_hook: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Update layer hooks (assumes lock is held)."""
        if layer_index < 0 or layer_index >= len(self._state.task_layers):
            return False

        if self._state.execution_pointer is not None:
            if layer_index < self._state.execution_pointer.current_layer_index:
                return False

        layer = self._state.task_layers[layer_index]
        if pre_hook is not None:
            layer.pre_hook = pre_hook
        if post_hook is not None:
            layer.post_hook = post_hook
        return True

    def modify_task_stack(self, operations: List[BatchOperation]) -> Dict[str, Any]:
        """Execute multiple operations atomically in a single lock."""
        results = []
        errors = []
        created_task_ids = []
        created_layer_indices = []

        with self._state.lock:
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

                            task = self.create_task_internal(task_desc["description"])
                            created_ids.append(task.id)
                            created_task_ids.append(task.id)

                        results.append(
                            {
                                "operation_index": idx,
                                "type": operation.type.value,
                                "success": True,
                                "data": {"created_task_ids": created_ids},
                            }
                        )

                    elif operation.type == BatchOperationType.CREATE_LAYERS:
                        layer_configs = operation.params.get("layers", [])
                        if not isinstance(layer_configs, list):
                            raise ValueError("CREATE_LAYERS requires 'layers' as a list")

                        created_indices = []
                        for layer_config in layer_configs:
                            if not isinstance(layer_config, dict):
                                raise ValueError("Each layer config must be a dictionary")

                            layer = self.create_layer_internal(
                                layer_index=layer_config.get("layer_index"),
                                pre_hook=layer_config.get("pre_hook"),
                                post_hook=layer_config.get("post_hook"),
                            )
                            created_indices.append(layer.layer_index)
                            created_layer_indices.append(layer.layer_index)

                        results.append(
                            {
                                "operation_index": idx,
                                "type": operation.type.value,
                                "success": True,
                                "data": {"created_layer_indices": created_indices},
                            }
                        )

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

                            success = self.add_task_to_layer_internal(
                                layer_index, task_id, insert_index
                            )
                            success_list.append(success)
                            if not success:
                                raise ValueError(
                                    f"Failed to add task {task_id} to layer {layer_index}"
                                )

                        results.append(
                            {
                                "operation_index": idx,
                                "type": operation.type.value,
                                "success": True,
                                "data": {"success_list": success_list},
                            }
                        )

                    elif operation.type == BatchOperationType.REMOVE_TASKS_FROM_LAYERS:
                        removals = operation.params.get("removals", [])
                        if not isinstance(removals, list):
                            raise ValueError(
                                "REMOVE_TASKS_FROM_LAYERS requires 'removals' as a list"
                            )

                        success_list = []
                        for removal in removals:
                            if not isinstance(removal, dict):
                                raise ValueError("Each removal must be a dictionary")

                            layer_index = removal.get("layer_index")
                            task_id = removal.get("task_id")
                            if layer_index is None or task_id is None:
                                raise ValueError("Each removal must have 'layer_index' and 'task_id'")

                            success = self.remove_task_from_layer_internal(layer_index, task_id)
                            success_list.append(success)
                            if not success:
                                raise ValueError(
                                    f"Failed to remove task {task_id} from layer {layer_index}"
                                )

                        results.append(
                            {
                                "operation_index": idx,
                                "type": operation.type.value,
                                "success": True,
                                "data": {"success_list": success_list},
                            }
                        )

                    elif operation.type == BatchOperationType.REPLACE_TASKS_IN_LAYERS:
                        replacements = operation.params.get("replacements", [])
                        if not isinstance(replacements, list):
                            raise ValueError(
                                "REPLACE_TASKS_IN_LAYERS requires 'replacements' as a list"
                            )

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

                            success = self.replace_task_in_layer_internal(
                                layer_index, old_task_id, new_task_id
                            )
                            success_list.append(success)
                            if not success:
                                raise ValueError(
                                    f"Failed to replace task {old_task_id} with {new_task_id} in layer {layer_index}"
                                )

                        results.append(
                            {
                                "operation_index": idx,
                                "type": operation.type.value,
                                "success": True,
                                "data": {"success_list": success_list},
                            }
                        )

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

                            success = self.update_layer_hooks_internal(
                                layer_index,
                                update.get("pre_hook"),
                                update.get("post_hook"),
                            )
                            success_list.append(success)
                            if not success:
                                raise ValueError(
                                    f"Failed to update hooks for layer {layer_index}"
                                )

                        results.append(
                            {
                                "operation_index": idx,
                                "type": operation.type.value,
                                "success": True,
                                "data": {"success_list": success_list},
                            }
                        )

                    else:
                        raise ValueError(f"Unknown operation type: {operation.type}")

                except Exception as exc:
                    errors.append(
                        {
                            "operation_index": idx,
                            "type": operation.type.value if operation else "unknown",
                            "error": str(exc),
                            "params": operation.params if operation else None,
                        }
                    )
                    results.append(
                        {
                            "operation_index": idx,
                            "type": operation.type.value if operation else "unknown",
                            "success": False,
                            "error": str(exc),
                        }
                    )

        return {
            "success": len(errors) == 0,
            "results": results,
            "errors": errors,
            "created_task_ids": created_task_ids,
            "created_layer_indices": created_layer_indices,
        }
