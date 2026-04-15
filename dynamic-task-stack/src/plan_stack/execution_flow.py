"""Execution pointer flow logic for Plan Stack."""

from typing import Any, Dict, Optional

from .models import ExecutionPointer
from .state_store import PlanStackStateStore


class PlanStackExecutionFlow:
    """Encapsulates execution pointer state transitions."""

    def __init__(self, state_store: PlanStackStateStore) -> None:
        self._state = state_store

    def get_execution_pointer(self) -> Optional[ExecutionPointer]:
        with self._state.lock:
            return self._state.execution_pointer

    def set_execution_pointer(
        self,
        layer_index: int,
        step_index: int,
    ) -> bool:
        with self._state.lock:
            if layer_index < 0 or layer_index >= len(self._state.plan_layers):
                return False
            layer = self._state.plan_layers[layer_index]
            if step_index < 0 or step_index >= len(layer.steps):
                return False
            self._state.execution_pointer = ExecutionPointer(
                current_layer_index=layer_index,
                current_step_index=step_index,
            )
            return True

    def get_next_step(self) -> Optional[Dict[str, Any]]:
        with self._state.lock:
            if self._state.execution_pointer is None:
                if not self._state.plan_layers:
                    return None
                layer = self._state.plan_layers[0]
                if not layer.steps:
                    return None
                return {
                    "layer_index": 0,
                    "step_index": 0,
                    "step_id": layer.steps[0].step_id,
                    "layer": layer,
                }
            pointer = self._state.execution_pointer
            layer_idx = pointer.current_layer_index
            step_idx = pointer.current_step_index
            if layer_idx < len(self._state.plan_layers):
                layer = self._state.plan_layers[layer_idx]
                if step_idx < len(layer.steps):
                    return {
                        "layer_index": layer_idx,
                        "step_index": step_idx,
                        "step_id": layer.steps[step_idx].step_id,
                        "layer": layer,
                    }
            return None

    def advance_execution_pointer(self) -> bool:
        with self._state.lock:
            if self._state.execution_pointer is None:
                if not self._state.plan_layers:
                    return False
                self._state.execution_pointer = ExecutionPointer(
                    current_layer_index=0,
                    current_step_index=0,
                )
                return True
            layer_idx = self._state.execution_pointer.current_layer_index
            step_idx = self._state.execution_pointer.current_step_index
            if layer_idx >= len(self._state.plan_layers):
                return False
            layer = self._state.plan_layers[layer_idx]
            if step_idx + 1 < len(layer.steps):
                self._state.execution_pointer.current_step_index = step_idx + 1
                return True
            if layer_idx + 1 < len(self._state.plan_layers):
                next_layer = self._state.plan_layers[layer_idx + 1]
                if next_layer.steps:
                    self._state.execution_pointer.current_layer_index = layer_idx + 1
                    self._state.execution_pointer.current_step_index = 0
                    return True
            return False
