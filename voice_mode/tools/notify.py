"""Notify mode tool for text-based popup conversations."""

import logging
import os
import platform
from typing import Optional, Literal

from voice_mode.server import mcp
from voice_mode.conversation_logger import get_conversation_logger
from voice_mode.utils.notify_popup import (
    PopupConfig,
    show_popup,
    NotifyPopupResult,
)

logger = logging.getLogger("voicemode")


def _detect_headless_environment() -> bool:
    """Detect if running in a headless environment without display."""
    system = platform.system()

    if system == "Darwin":
        # macOS: Check if we're in a login session with a display
        # SSH without X11 forwarding won't have DISPLAY
        session_type = os.environ.get("XPC_SERVICE_NAME", "")
        return "com.openssh" in session_type and not os.environ.get("DISPLAY")

    elif system == "Linux":
        # Linux: Check for DISPLAY or WAYLAND_DISPLAY
        has_display = bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))
        return not has_display

    elif system == "Windows":
        # Windows: Check for session type
        # In most cases, if Python can run with tkinter, there's a display
        try:
            import ctypes
            return ctypes.windll.user32.GetDesktopWindow() == 0
        except (AttributeError, OSError):
            return False

    return False


@mcp.tool()
async def notify(
    message: str,
    wait_for_response: bool = True,
    timeout: Optional[float] = None,
    title: str = "VoiceMode",
    show_history: bool = True,
    chime_enabled: bool = False,
    theme: Literal["auto", "light", "dark"] = "auto",
) -> str:
    """Display a message in a popup window and optionally wait for user text response.

Use this for silent, text-based conversation instead of voice.

KEY PARAMETERS:
• message (required): The message to display in the popup (1-10,000 characters)
• wait_for_response (bool, default: true): Whether to wait for user input
• timeout (number, optional): Timeout in seconds for user response (5-300 seconds)
• title (string, default: "VoiceMode"): Window title for the popup
• show_history (bool, default: true): Whether to show recent conversation history
• chime_enabled (bool, default: false): Whether to play sound feedback
• theme ("auto"|"light"|"dark", default: "auto"): Color theme for the popup

RESPONSE FORMATS:
• Success with response: "User response: <text>"
• Success without response (wait_for_response=false): "✓ Message displayed successfully"
• User cancelled: "User cancelled the popup"
• User dismissed: "User dismissed the popup"
• Timeout: "No response within <timeout>s timeout"
• Empty input: "User submitted empty response"
• Headless error: "Error: Cannot display popup - no display available"

USAGE:
- Silent conversation in meetings or quiet environments
- Accessibility alternative to voice interaction
- Quick status notifications with wait_for_response=false
    """
    logger.info(f"Notify tool called: '{message[:50]}{'...' if len(message) > 50 else ''}'")

    # Validate message length
    if not message or len(message) < 1:
        return "Error: Message cannot be empty"
    if len(message) > 10000:
        return "Error: Message exceeds maximum length of 10,000 characters"

    # Validate timeout
    if timeout is not None:
        if timeout < 5 or timeout > 300:
            return "Error: Timeout must be between 5 and 300 seconds"

    # Check for headless environment
    if _detect_headless_environment():
        return "Error: Cannot display popup - no display available. This feature requires a graphical environment."

    # Get conversation history if enabled
    history = []
    if show_history:
        try:
            conversation_logger = get_conversation_logger()
            # Get recent exchanges from the logger
            history = conversation_logger.get_recent_exchanges(limit=5)
        except Exception as e:
            logger.warning(f"Failed to get conversation history: {e}")
            history = []

    # Play start chime if enabled
    if chime_enabled:
        try:
            from voice_mode.core import play_chime_start
            await play_chime_start()
        except Exception as e:
            logger.debug(f"Failed to play start chime: {e}")

    # Build popup configuration
    config = PopupConfig(
        title=title,
        timeout=timeout,
        show_history=show_history,
        chime_enabled=chime_enabled,
        theme=theme,
    )

    # Show popup and wait for response
    try:
        result: NotifyPopupResult = await show_popup(
            message=message,
            config=config,
            history=history,
            wait_for_response=wait_for_response,
        )
    except Exception as e:
        logger.error(f"Popup error: {e}")
        return f"Error: Failed to display popup - {str(e)}"

    # Log the exchange
    try:
        conversation_logger = get_conversation_logger()
        conversation_logger.log_notify_exchange(
            assistant_message=message,
            user_response=result.response if result.response else None,
            result_type=result.result_type,
        )
    except Exception as e:
        logger.warning(f"Failed to log notify exchange: {e}")

    # Play end chime if enabled and we got a response
    if chime_enabled and result.response:
        try:
            from voice_mode.core import play_chime_end
            await play_chime_end()
        except Exception as e:
            logger.debug(f"Failed to play end chime: {e}")

    # Format response based on result type
    if result.result_type == "success":
        if wait_for_response:
            return f"User response: {result.response}"
        else:
            return "✓ Message displayed successfully"
    elif result.result_type == "cancelled":
        return "User cancelled the popup"
    elif result.result_type == "dismissed":
        return "User dismissed the popup"
    elif result.result_type == "timeout":
        return f"No response within {timeout}s timeout"
    elif result.result_type == "empty":
        return "User submitted empty response"
    else:
        return f"Error: Unknown result type: {result.result_type}"
