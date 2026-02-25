"""Shared base registry for generator discovery and management."""

from __future__ import annotations

import importlib
import inspect
from pathlib import Path
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

TGenerator = TypeVar("TGenerator")


class BaseGeneratorRegistry(Generic[TGenerator]):
    """
    Generic registry with shared discovery/loading logic.

    Subclasses provide:
    - `base_generator_cls`: expected base class for `issubclass` checks
    - `package_root`: import root package for dynamic module loading
    - `registry_label`: label used in warning messages
    """

    base_generator_cls: type[Any]
    package_root: str
    registry_label: str = "generator"

    def __init__(self, generators_dir: Optional[str] = None):
        if generators_dir is None:
            generators_dir = Path(__file__).parent
        self.generators_dir = Path(generators_dir)
        self._generators: Dict[str, TGenerator] = {}
        self._generator_classes: Dict[str, Type[TGenerator]] = {}
        self.generators_dir.mkdir(parents=True, exist_ok=True)
        self._discover_generators()

    def _discover_generators(self):
        if not self.generators_dir.exists():
            return
        for item in self.generators_dir.iterdir():
            if not item.is_dir():
                continue
            if item.name.startswith("_") or item.name.startswith("."):
                continue
            try:
                self._load_generator_from_directory(item)
            except Exception as e:
                print(
                    f"Warning: Failed to load {self.registry_label} generator from {item.name}: {e}"
                )

    def _load_generator_from_directory(self, generator_dir: Path):
        generator_name = generator_dir.name
        module_paths = [
            (generator_dir / "generator.py", "generator"),
            (generator_dir / "__init__.py", "__init__"),
        ]
        for module_path, module_file in module_paths:
            if not module_path.exists():
                continue
            try:
                import_strategies = [
                    f"{self.package_root}.{generator_name}.{module_file}",
                    f"{self.package_root}.{generator_name}",
                ]
                for module_name in import_strategies:
                    try:
                        module = importlib.import_module(module_name)
                        for _, obj in inspect.getmembers(module, inspect.isclass):
                            if (
                                issubclass(obj, self.base_generator_cls)
                                and obj != self.base_generator_cls
                                and obj.__module__ == module.__name__
                            ):
                                generator_instance = obj()
                                generator_id = generator_instance.metadata.id
                                self._generators[generator_id] = generator_instance
                                self._generator_classes[generator_id] = obj
                                return
                    except ImportError:
                        continue
            except Exception as e:
                print(f"Warning: Failed to load generator from {generator_name}: {e}")
                continue

    def register_generator(self, generator: TGenerator):
        generator_id = generator.metadata.id
        self._generators[generator_id] = generator
        self._generator_classes[generator_id] = type(generator)

    def get_generator(self, generator_id: str) -> Optional[TGenerator]:
        return self._generators.get(generator_id)

    def get_generator_class(self, generator_id: str) -> Optional[Type[TGenerator]]:
        return self._generator_classes.get(generator_id)

    def list_generators(self) -> List[str]:
        return list(self._generators.keys())

    def _generate_with_inputs(self, generator_id: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        generator = self.get_generator(generator_id)
        if not generator:
            raise ValueError(f"{self.registry_label.title()} generator '{generator_id}' not found")
        validated_inputs = generator.validate_inputs(inputs)
        return generator.generate(**validated_inputs)

    def get_all_generators_info(self) -> List[Dict[str, Any]]:
        return [generator.get_info() for generator in self._generators.values()]

    def reload(self):
        self._generators.clear()
        self._generator_classes.clear()
        self._discover_generators()
