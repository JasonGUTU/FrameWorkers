"""Assistant module boundary.

Exports HTTP blueprint factory and runtime state singletons.
Business logic stays in service.py.
"""

from .state_store import assistant_state_store


def create_assistant_blueprint():
    """Lazy import to avoid route side effects on package import."""
    from .routes import create_assistant_blueprint as _factory
    return _factory()


__all__ = [
    'create_assistant_blueprint',
    'assistant_state_store',
]
