"""Global exception handler for the application.

Phase 5: Centralized exception handling to avoid multiple sys.excepthook overrides.
Each window/thread registers a callback instead of overriding sys.excepthook directly.
"""

import sys
import traceback
from typing import Callable, Optional, Type


class GlobalExceptionHandler:
    """Centralized exception handler that manages callbacks from different components."""

    def __init__(self):
        self._callbacks: list[Callable[[Type[BaseException], BaseException, object], None]] = []
        self._original_excepthook = sys.excepthook
        self._installed = False

    def install(self) -> None:
        """Install this handler as the global exception hook."""
        if not self._installed:
            sys.excepthook = self._handle_exception
            self._installed = True

    def uninstall(self) -> None:
        """Restore the original exception hook."""
        if self._installed:
            sys.excepthook = self._original_excepthook
            self._installed = False

    def register_callback(self, callback: Callable[[Type[BaseException], BaseException, object], None]) -> None:
        """Register a callback to be notified of exceptions.

        Args:
            callback: Function taking (exc_type, exc_value, exc_traceback) and returning None
        """
        if callback not in self._callbacks:
            self._callbacks.append(callback)

    def unregister_callback(self, callback: Callable[[Type[BaseException], BaseException, object], None]) -> None:
        """Unregister a previously registered callback."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    def _handle_exception(self, exc_type: Type[BaseException], exc_value: BaseException, exc_traceback: object) -> None:
        """Internal handler that notifies all registered callbacks."""
        # Handle KeyboardInterrupt specially - don't log it
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        # Notify all registered callbacks
        for callback in self._callbacks:
            try:
                callback(exc_type, exc_value, exc_traceback)
            except Exception as e:
                # Don't let callback errors crash the handler
                print(f"Error in exception callback: {e}", file=sys.stderr)

        # Also call the original hook to ensure default behavior
        self._original_excepthook(exc_type, exc_value, exc_traceback)


# Global singleton instance
_global_handler: Optional[GlobalExceptionHandler] = None


def get_global_handler() -> GlobalExceptionHandler:
    """Get the global exception handler singleton."""
    global _global_handler
    if _global_handler is None:
        _global_handler = GlobalExceptionHandler()
    return _global_handler
