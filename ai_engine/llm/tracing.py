"""LLM call tracing via context variables."""
import contextvars

_current_investigation = contextvars.ContextVar("current_investigation", default=None)


def set_current_investigation(investigation_id):
    """Set the current investigation ID for the duration of an agent run."""
    _current_investigation.set(investigation_id)


def get_current_investigation():
    """Get the current investigation ID, or None."""
    return _current_investigation.get()


def clear_current_investigation():
    """Clear the context."""
    _current_investigation.set(None)