"""Batch mutation and internal write helpers for Plan Stack (historical alias: "task stack")."""

from datetime import datetime
from typing import Any, Dict, List, Optional
import uuid

from .models import (
    BatchOperation,
    BatchOperationType,
    PlanStep,
    PlanLayer,
    PlanStepEntry,
    PlanStepStatus,
)
from .state_store import PlanStackStateStore


class PlanStackBatchMutator:
    """Encapsulates atomic multi-step Plan Stack mutations."""

    def __init__(self, state_store: PlanStackStateStore) -> None:
        self._state = state_store

    def is_step_executed(self, layer_index: int, step_index: int) -> bool:
        """Check whether a step position has already been executed."""
        pointer = self._state.execution_pointer
        if pointer is None:
            return False

        if layer_index < pointer.current_layer_index:
            return True
        if layer_index == pointer.current_layer_index and step_index < pointer.current_step_index:
            return True

        return False

    def create_step_internal(self, description: Dict[str, Any]) -> PlanStep:
        """Create plan step (assumes lock is held)."""
        self._state.plan_step_counter += 1
        step_id = f"step_{self._state.plan_step_counter}_{uuid.uuid4().hex[:8]}"
        now_time = datetime.now()
        step = PlanStep(
            id=step_id,
            description=description,
            status=PlanStepStatus.PENDING,
            progress={},
            results=None,
            created_at=now_time,
            updated_at=now_time,
        )
        self._state.plan_steps[step_id] = step
        return step

    def create_layer_internal(
        self,
        layer_index: Optional[int] = None,
    ) -> PlanLayer:
        """Create layer (assumes lock is held)."""
        if layer_index is None:
            layer_index = len(self._state.plan_layers)

        layer = PlanLayer(
            layer_index=layer_index,
            steps=[],
            created_at=datetime.now(),
        )

        if layer_index < len(self._state.plan_layers):
            self._state.plan_layers.insert(layer_index, layer)
            for i, existing_layer in enumerate(self._state.plan_layers):
                existing_layer.layer_index = i
        else:
            self._state.plan_layers.append(layer)

        return layer

    def add_step_to_layer_internal(
        self,
        layer_index: int,
        step_id: str,
        insert_index: Optional[int] = None,
    ) -> bool:
        """Add step to layer (assumes lock is held)."""
        if layer_index < 0 or layer_index >= len(self._state.plan_layers):
            return False

        if step_id not in self._state.plan_steps:
            return False

        layer = self._state.plan_layers[layer_index]

        if self._state.execution_pointer is not None:
            if layer_index < self._state.execution_pointer.current_layer_index:
                return False

        if any(entry.step_id == step_id for entry in layer.steps):
            return False

        entry = PlanStepEntry(step_id=step_id, created_at=datetime.now())

        if insert_index is not None:
            if insert_index < 0 or insert_index > len(layer.steps):
                return False
            if self._state.execution_pointer is not None:
                if layer_index == self._state.execution_pointer.current_layer_index:
                    if insert_index <= self._state.execution_pointer.current_step_index:
                        return False
            layer.steps.insert(insert_index, entry)
        else:
            layer.steps.append(entry)

        return True

    def remove_step_from_layer_internal(self, layer_index: int, step_id: str) -> bool:
        """Remove step from layer (assumes lock is held)."""
        if layer_index < 0 or layer_index >= len(self._state.plan_layers):
            return False

        layer = self._state.plan_layers[layer_index]
        step_index = None
        for idx, entry in enumerate(layer.steps):
            if entry.step_id == step_id:
                step_index = idx
                break

        if step_index is None:
            return False

        if self.is_step_executed(layer_index, step_index):
            return False

        layer.steps.pop(step_index)
        return True

    def modify_plan_stack(self, operations: List[BatchOperation]) -> Dict[str, Any]:
        """Execute multiple operations atomically in a single lock."""
        results = []
        errors = []
        created_step_ids = []
        created_layer_indices = []

        with self._state.lock:
            for idx, operation in enumerate(operations):
                try:
                    if operation.type == BatchOperationType.CREATE_STEPS:
                        step_descriptions = operation.params.get("steps", [])
                        if not isinstance(step_descriptions, list):
                            raise ValueError("CREATE_STEPS requires 'steps' as a list")

                        created_ids = []
                        for step_desc in step_descriptions:
                            if not isinstance(step_desc, dict) or "description" not in step_desc:
                                raise ValueError("Each step must have a 'description' field")

                            step = self.create_step_internal(step_desc["description"])
                            created_ids.append(step.id)
                            created_step_ids.append(step.id)

                        results.append(
                            {
                                "operation_index": idx,
                                "type": operation.type.value,
                                "success": True,
                                "data": {"created_step_ids": created_ids},
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

                    elif operation.type == BatchOperationType.ADD_STEPS_TO_LAYERS:
                        additions = operation.params.get("additions", [])
                        if not isinstance(additions, list):
                            raise ValueError("ADD_TASKS_TO_LAYERS requires 'additions' as a list")

                        success_list = []
                        for addition in additions:
                            if not isinstance(addition, dict):
                                raise ValueError("Each addition must be a dictionary")

                            layer_index = addition.get("layer_index")
                            step_id = addition.get("step_id")
                            insert_index = addition.get("insert_index")
                            if layer_index is None or step_id is None:
                                raise ValueError("Each addition must have 'layer_index' and 'step_id'")

                            success = self.add_step_to_layer_internal(
                                layer_index, step_id, insert_index
                            )
                            success_list.append(success)
                            if not success:
                                raise ValueError(
                                    f"Failed to add step {step_id} to layer {layer_index}"
                                )

                        results.append(
                            {
                                "operation_index": idx,
                                "type": operation.type.value,
                                "success": True,
                                "data": {"success_list": success_list},
                            }
                        )

                    elif operation.type == BatchOperationType.REMOVE_STEPS_FROM_LAYERS:
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
                            step_id = removal.get("step_id")
                            if layer_index is None or step_id is None:
                                raise ValueError("Each removal must have 'layer_index' and 'step_id'")

                            success = self.remove_step_from_layer_internal(layer_index, step_id)
                            success_list.append(success)
                            if not success:
                                raise ValueError(
                                    f"Failed to remove step {step_id} from layer {layer_index}"
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
            "created_step_ids": created_step_ids,
            "created_layer_indices": created_layer_indices,
        }
