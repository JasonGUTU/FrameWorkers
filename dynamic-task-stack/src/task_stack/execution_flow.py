"""Execution pointer flow logic for Task Stack."""

from typing import Any, Dict, Optional

from .models import ExecutionPointer
from .state_store import TaskStackStateStore


class TaskStackExecutionFlow:
    """Encapsulates execution pointer state transitions."""

    def __init__(self, state_store: TaskStackStateStore) -> None:
        self._state = state_store

    def get_execution_pointer(self) -> Optional[ExecutionPointer]:
        """Get current execution pointer."""
        with self._state.lock:
            return self._state.execution_pointer

    def set_execution_pointer(
        self,
        layer_index: int,
        task_index: int,
        is_executing_pre_hook: bool = False,
        is_executing_post_hook: bool = False,
    ) -> bool:
        """Set execution pointer."""
        with self._state.lock:
            if layer_index < 0 or layer_index >= len(self._state.task_layers):
                return False

            layer = self._state.task_layers[layer_index]
            if task_index < 0 or task_index >= len(layer.tasks):
                return False

            self._state.execution_pointer = ExecutionPointer(
                current_layer_index=layer_index,
                current_task_index=task_index,
                is_executing_pre_hook=is_executing_pre_hook,
                is_executing_post_hook=is_executing_post_hook,
            )
            return True

    def get_next_task(self) -> Optional[Dict[str, Any]]:
        """Get next task based on execution pointer and hook state."""
        with self._state.lock:
            if self._state.execution_pointer is None:
                if not self._state.task_layers:
                    return None
                layer = self._state.task_layers[0]
                if not layer.tasks:
                    return None
                return {
                    "layer_index": 0,
                    "task_index": 0,
                    "task_id": layer.tasks[0].task_id,
                    "layer": layer,
                }

            pointer = self._state.execution_pointer
            layer_idx = pointer.current_layer_index
            task_idx = pointer.current_task_index

            if pointer.is_executing_pre_hook:
                if layer_idx < len(self._state.task_layers):
                    layer = self._state.task_layers[layer_idx]
                    if task_idx < len(layer.tasks):
                        return {
                            "layer_index": layer_idx,
                            "task_index": task_idx,
                            "task_id": layer.tasks[task_idx].task_id,
                            "layer": layer,
                            "is_pre_hook": True,
                        }

            if pointer.is_executing_post_hook:
                if layer_idx < len(self._state.task_layers):
                    layer = self._state.task_layers[layer_idx]
                    if task_idx + 1 < len(layer.tasks):
                        return {
                            "layer_index": layer_idx,
                            "task_index": task_idx + 1,
                            "task_id": layer.tasks[task_idx + 1].task_id,
                            "layer": layer,
                        }
                    if layer_idx + 1 < len(self._state.task_layers):
                        next_layer = self._state.task_layers[layer_idx + 1]
                        if next_layer.tasks:
                            return {
                                "layer_index": layer_idx + 1,
                                "task_index": 0,
                                "task_id": next_layer.tasks[0].task_id,
                                "layer": next_layer,
                            }

            if layer_idx < len(self._state.task_layers):
                layer = self._state.task_layers[layer_idx]
                if task_idx < len(layer.tasks):
                    return {
                        "layer_index": layer_idx,
                        "task_index": task_idx,
                        "task_id": layer.tasks[task_idx].task_id,
                        "layer": layer,
                    }

            return None

    def advance_execution_pointer(self) -> bool:
        """Advance execution pointer to next executable task."""
        with self._state.lock:
            if self._state.execution_pointer is None:
                if not self._state.task_layers:
                    return False
                self._state.execution_pointer = ExecutionPointer(
                    current_layer_index=0,
                    current_task_index=0,
                    is_executing_pre_hook=False,
                    is_executing_post_hook=False,
                )
                return True

            layer_idx = self._state.execution_pointer.current_layer_index
            task_idx = self._state.execution_pointer.current_task_index

            if layer_idx >= len(self._state.task_layers):
                return False

            layer = self._state.task_layers[layer_idx]

            if task_idx + 1 < len(layer.tasks):
                self._state.execution_pointer.current_task_index = task_idx + 1
                self._state.execution_pointer.is_executing_pre_hook = False
                self._state.execution_pointer.is_executing_post_hook = False
                return True

            if layer_idx + 1 < len(self._state.task_layers):
                next_layer = self._state.task_layers[layer_idx + 1]
                if next_layer.tasks:
                    self._state.execution_pointer.current_layer_index = layer_idx + 1
                    self._state.execution_pointer.current_task_index = 0
                    self._state.execution_pointer.is_executing_pre_hook = False
                    self._state.execution_pointer.is_executing_post_hook = False
                    return True

            return False
