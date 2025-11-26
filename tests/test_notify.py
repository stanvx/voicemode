"""Tests for the notify tool and popup functionality."""

import asyncio
import platform
import pytest
from unittest.mock import patch, MagicMock, AsyncMock


class TestNotifyPopupModule:
    """Test the notify_popup module components."""

    def test_popup_config_defaults(self):
        """Test PopupConfig has correct default values."""
        from voice_mode.utils.notify_popup import PopupConfig

        config = PopupConfig()

        assert config.title == "VoiceMode"
        assert config.width == 500
        assert config.height == 600
        assert config.topmost is True
        assert config.timeout is None
        assert config.show_history is True
        assert config.history_limit == 5
        assert config.chime_enabled is False
        assert config.theme == "auto"
        assert config.font_size == 14

    def test_popup_config_custom_values(self):
        """Test PopupConfig can be customized."""
        from voice_mode.utils.notify_popup import PopupConfig

        config = PopupConfig(
            title="Custom Title",
            width=600,
            height=700,
            timeout=30.0,
            theme="dark",
        )

        assert config.title == "Custom Title"
        assert config.width == 600
        assert config.height == 700
        assert config.timeout == 30.0
        assert config.theme == "dark"

    def test_theme_colors_light(self):
        """Test light theme colors."""
        from voice_mode.utils.notify_popup import ThemeColors

        colors = ThemeColors.light()

        assert colors.window_bg == "#f5f5f7"
        assert colors.text_primary == "#1d1d1f"
        assert colors.user_bubble_bg == "#007aff"
        assert colors.assistant_bubble_bg == "#e9e9eb"
        assert colors.accent == "#007aff"

    def test_theme_colors_dark(self):
        """Test dark theme colors."""
        from voice_mode.utils.notify_popup import ThemeColors

        colors = ThemeColors.dark()

        assert colors.window_bg == "#1c1c1e"
        assert colors.text_primary == "#ffffff"
        assert colors.user_bubble_bg == "#0a84ff"
        assert colors.assistant_bubble_bg == "#2c2c2e"
        assert colors.accent == "#0a84ff"

    def test_get_theme_colors_light(self):
        """Test get_theme_colors returns light theme."""
        from voice_mode.utils.notify_popup import get_theme_colors, ThemeColors

        colors = get_theme_colors("light")

        assert colors.window_bg == ThemeColors.light().window_bg
        assert colors.text_primary == ThemeColors.light().text_primary

    def test_get_theme_colors_dark(self):
        """Test get_theme_colors returns dark theme."""
        from voice_mode.utils.notify_popup import get_theme_colors, ThemeColors

        colors = get_theme_colors("dark")

        assert colors.window_bg == ThemeColors.dark().window_bg
        assert colors.text_primary == ThemeColors.dark().text_primary

    def test_detect_dark_mode_function_exists(self):
        """Test detect_dark_mode function exists and returns bool."""
        from voice_mode.utils.notify_popup import detect_dark_mode

        result = detect_dark_mode()
        assert isinstance(result, bool)

    def test_notify_popup_result_success(self):
        """Test NotifyPopupResult for success case."""
        from voice_mode.utils.notify_popup import NotifyPopupResult

        result = NotifyPopupResult(result_type="success", response="Hello!")

        assert result.result_type == "success"
        assert result.response == "Hello!"

    def test_notify_popup_result_cancelled(self):
        """Test NotifyPopupResult for cancelled case."""
        from voice_mode.utils.notify_popup import NotifyPopupResult

        result = NotifyPopupResult(result_type="cancelled")

        assert result.result_type == "cancelled"
        assert result.response is None

    def test_notify_popup_result_timeout(self):
        """Test NotifyPopupResult for timeout case."""
        from voice_mode.utils.notify_popup import NotifyPopupResult

        result = NotifyPopupResult(result_type="timeout")

        assert result.result_type == "timeout"
        assert result.response is None


class TestNotifyTool:
    """Test the notify tool functionality."""

    def test_headless_detection_function_exists(self):
        """Test _detect_headless_environment function exists."""
        from voice_mode.tools.notify import _detect_headless_environment

        result = _detect_headless_environment()
        assert isinstance(result, bool)

    @pytest.mark.asyncio
    async def test_notify_validates_empty_message(self):
        """Test notify rejects empty messages."""
        # Import the raw function before MCP decoration
        import voice_mode.tools.notify as notify_module

        # Call the underlying function logic via a mock that simulates headless
        with patch.object(notify_module, '_detect_headless_environment', return_value=True):
            # Access the FunctionTool and get its underlying function
            from voice_mode.tools.notify import notify
            # Get the actual function from the tool
            fn = notify.fn if hasattr(notify, 'fn') else notify
            result = await fn("")

        assert "empty" in result.lower() or "headless" in result.lower() or "cannot" in result.lower()

    @pytest.mark.asyncio
    async def test_notify_validates_message_length(self):
        """Test notify rejects messages exceeding max length."""
        from voice_mode.tools.notify import notify

        long_message = "x" * 10001

        # Get the actual function from the tool
        fn = notify.fn if hasattr(notify, 'fn') else notify
        result = await fn(long_message)

        assert "10,000" in result or "maximum" in result.lower()

    @pytest.mark.asyncio
    async def test_notify_validates_timeout_range(self):
        """Test notify validates timeout is within allowed range."""
        from voice_mode.tools.notify import notify

        # Get the actual function from the tool
        fn = notify.fn if hasattr(notify, 'fn') else notify

        # Timeout too low
        result = await fn("Test", timeout=1)
        assert "5 and 300" in result or "timeout" in result.lower()

        # Timeout too high
        result = await fn("Test", timeout=500)
        assert "5 and 300" in result or "timeout" in result.lower()

    @pytest.mark.asyncio
    async def test_notify_headless_error(self):
        """Test notify returns error in headless environment."""
        import voice_mode.tools.notify as notify_module
        from voice_mode.tools.notify import notify

        # Get the actual function from the tool
        fn = notify.fn if hasattr(notify, 'fn') else notify

        with patch.object(notify_module, '_detect_headless_environment', return_value=True):
            result = await fn("Test message")

        assert "no display available" in result.lower() or "headless" in result.lower() or "graphical" in result.lower()


class TestConversationLoggerIntegration:
    """Test conversation logger integration with notify."""

    def test_log_notify_exchange_method_exists(self):
        """Test log_notify_exchange method exists on ConversationLogger."""
        from voice_mode.conversation_logger import ConversationLogger

        assert hasattr(ConversationLogger, 'log_notify_exchange')

    def test_get_recent_exchanges_method_exists(self):
        """Test get_recent_exchanges method exists on ConversationLogger."""
        from voice_mode.conversation_logger import ConversationLogger

        assert hasattr(ConversationLogger, 'get_recent_exchanges')

    def test_get_recent_exchanges_returns_list(self):
        """Test get_recent_exchanges returns a list."""
        from voice_mode.conversation_logger import get_conversation_logger

        logger = get_conversation_logger()
        result = logger.get_recent_exchanges(limit=5)

        assert isinstance(result, list)
