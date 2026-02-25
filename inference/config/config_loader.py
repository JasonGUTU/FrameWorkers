"""
Configuration Loader Utility

Provides utilities for loading and managing configuration files.
"""

from typing import Dict, Any, Optional
from pathlib import Path
import yaml
import json
import os


class ConfigLoader:
    """
    Utility class for loading configuration files

    Supports YAML and JSON formats, with environment variable substitution.
    """

    @staticmethod
    def load(config_path: str, use_env: bool = True) -> Dict[str, Any]:
        """
        Load configuration from file

        Args:
            config_path: Path to configuration file
            use_env: Whether to substitute environment variables

        Returns:
            Dictionary containing configuration
        """
        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with open(path, "r", encoding="utf-8") as f:
            if path.suffix.lower() in [".yaml", ".yml"]:
                config = yaml.safe_load(f) or {}
            elif path.suffix.lower() == ".json":
                config = json.load(f)
            else:
                raise ValueError(f"Unsupported configuration file format: {path.suffix}")

        if use_env:
            config = ConfigLoader._substitute_env_vars(config)

        return config

    @staticmethod
    def _substitute_env_vars(obj: Any) -> Any:
        """
        Recursively substitute environment variables in configuration

        Supports ${VAR_NAME} and $VAR_NAME syntax.

        Args:
            obj: Configuration object (dict, list, or string)

        Returns:
            Object with environment variables substituted
        """
        if isinstance(obj, dict):
            return {k: ConfigLoader._substitute_env_vars(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [ConfigLoader._substitute_env_vars(item) for item in obj]
        if isinstance(obj, str):
            # Support ${VAR_NAME} syntax
            if "${" in obj:
                import re

                pattern = r"\$\{([^}]+)\}"

                def replace_var(match):
                    var_name = match.group(1)
                    return os.getenv(var_name, match.group(0))

                return re.sub(pattern, replace_var, obj)
            # Support $VAR_NAME syntax
            if obj.startswith("$") and len(obj) > 1:
                var_name = obj[1:]
                return os.getenv(var_name, obj)
            return obj
        return obj

    @staticmethod
    def save(config: Dict[str, Any], config_path: str, format: str = "yaml"):
        """
        Save configuration to file

        Args:
            config: Configuration dictionary
            config_path: Path to save configuration file
            format: File format ('yaml' or 'json')
        """
        path = Path(config_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            if format.lower() == "yaml":
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
            elif format.lower() == "json":
                json.dump(config, f, indent=2, ensure_ascii=False)
            else:
                raise ValueError(f"Unsupported format: {format}")

    @staticmethod
    def find_config_file(
        filename: str, search_paths: Optional[list] = None
    ) -> Optional[str]:
        """
        Find configuration file in common locations

        Args:
            filename: Name of configuration file
            search_paths: Optional list of paths to search

        Returns:
            Path to configuration file if found, None otherwise
        """
        if search_paths is None:
            # Default search paths
            search_paths = [
                ".",
                "~/.config/inference",
                "/etc/inference",
            ]

        for search_path in search_paths:
            expanded_path = Path(search_path).expanduser()
            config_file = expanded_path / filename
            if config_file.exists():
                return str(config_file)

        return None
