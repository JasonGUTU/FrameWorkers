"""
Configuration Loader Utility

Provides utilities for loading and managing configuration files.
"""

from typing import Dict, Any, Optional
from pathlib import Path
import yaml
import json
import os
import re


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
    def find_file_upwards(
        filename: str,
        start_path: Optional[str] = None,
    ) -> Optional[str]:
        """
        Find a file by searching current directory upwards.

        Args:
            filename: File name to search for.
            start_path: Optional starting directory. Defaults to cwd.

        Returns:
            Absolute path to file if found, None otherwise.
        """
        current = Path(start_path).expanduser().resolve() if start_path else Path.cwd().resolve()
        for candidate_dir in [current, *current.parents]:
            candidate = candidate_dir / filename
            if candidate.exists() and candidate.is_file():
                return str(candidate)
        return None

    @staticmethod
    def load_env_file(
        env_path: Optional[str] = None,
        *,
        override: bool = False,
    ) -> Optional[str]:
        """
        Load key/value pairs from a .env file into process environment.

        Supports lines like:
        - KEY=value
        - export KEY=value
        - empty lines / comments

        Args:
            env_path: Optional explicit env file path. If not provided,
                search from cwd upwards for ".env".
            override: If True, override existing environment variables.

        Returns:
            Loaded env file path if found and parsed; otherwise None.
        """
        resolved_path = env_path
        if not resolved_path:
            resolved_path = ConfigLoader.find_file_upwards(filename=".env")
        if not resolved_path:
            return None

        path = Path(resolved_path)
        if not path.exists() or not path.is_file():
            return None

        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("export "):
                line = line[len("export ") :].strip()
            if "=" not in line:
                continue

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()
            if not key:
                continue

            # Strip paired quotes for common .env styles.
            if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
                value = value[1:-1]

            if override or key not in os.environ:
                os.environ[key] = value

        return str(path)
