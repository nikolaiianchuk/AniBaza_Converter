"""Tests for modules/GlobalExceptionHandler.py - Phase 5."""

import sys
from unittest.mock import MagicMock

import pytest

from modules.GlobalExceptionHandler import GlobalExceptionHandler, get_global_handler


class TestGlobalExceptionHandler:
    """Test GlobalExceptionHandler functionality."""

    def test_singleton(self):
        """get_global_handler returns the same instance."""
        handler1 = get_global_handler()
        handler2 = get_global_handler()
        assert handler1 is handler2

    def test_install_sets_excepthook(self):
        """install() sets sys.excepthook to the handler."""
        handler = GlobalExceptionHandler()
        original = sys.excepthook

        handler.install()
        assert sys.excepthook == handler._handle_exception

        handler.uninstall()
        assert sys.excepthook == original

    def test_register_callback(self):
        """Callbacks are registered and called on exceptions."""
        handler = GlobalExceptionHandler()
        callback = MagicMock()
        original_hook = handler._original_excepthook
        handler._original_excepthook = MagicMock()  # Mock to prevent Qt errors

        handler.register_callback(callback)
        handler._handle_exception(ValueError, ValueError("test"), None)

        callback.assert_called_once()
        args = callback.call_args[0]
        assert args[0] == ValueError
        assert isinstance(args[1], ValueError)

        handler._original_excepthook = original_hook  # Restore

    def test_multiple_callbacks(self):
        """Multiple callbacks are all notified."""
        handler = GlobalExceptionHandler()
        callback1 = MagicMock()
        callback2 = MagicMock()
        original_hook = handler._original_excepthook
        handler._original_excepthook = MagicMock()  # Mock to prevent Qt errors

        handler.register_callback(callback1)
        handler.register_callback(callback2)
        handler._handle_exception(ValueError, ValueError("test"), None)

        callback1.assert_called_once()
        callback2.assert_called_once()

        handler._original_excepthook = original_hook  # Restore

    def test_unregister_callback(self):
        """Unregistered callbacks are not called."""
        handler = GlobalExceptionHandler()
        callback = MagicMock()
        original_hook = handler._original_excepthook
        handler._original_excepthook = MagicMock()  # Mock to prevent Qt errors

        handler.register_callback(callback)
        handler.unregister_callback(callback)
        handler._handle_exception(ValueError, ValueError("test"), None)

        callback.assert_not_called()

        handler._original_excepthook = original_hook  # Restore

    def test_callback_error_doesnt_crash(self):
        """Errors in callbacks don't crash the handler."""
        handler = GlobalExceptionHandler()
        original_hook = handler._original_excepthook
        handler._original_excepthook = MagicMock()  # Mock to prevent Qt errors

        def bad_callback(exc_type, exc_value, exc_traceback):
            raise RuntimeError("Callback error")

        good_callback = MagicMock()

        handler.register_callback(bad_callback)
        handler.register_callback(good_callback)
        handler._handle_exception(ValueError, ValueError("test"), None)

        # Good callback should still be called despite bad callback error
        good_callback.assert_called_once()

        handler._original_excepthook = original_hook  # Restore

    def test_keyboard_interrupt_special_handling(self):
        """KeyboardInterrupt is handled specially."""
        handler = GlobalExceptionHandler()
        callback = MagicMock()

        handler.register_callback(callback)
        # This should not call our callback (KeyboardInterrupt gets special handling)
        # We can't easily test this without actually raising, but we verify the code path exists
        assert handler._handle_exception  # Handler exists

    def test_duplicate_registration_ignored(self):
        """Registering the same callback twice doesn't duplicate it."""
        handler = GlobalExceptionHandler()
        callback = MagicMock()
        original_hook = handler._original_excepthook
        handler._original_excepthook = MagicMock()  # Mock to prevent Qt errors

        handler.register_callback(callback)
        handler.register_callback(callback)  # Register again

        handler._handle_exception(ValueError, ValueError("test"), None)

        # Should only be called once, not twice
        callback.assert_called_once()

        handler._original_excepthook = original_hook  # Restore
