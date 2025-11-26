"""Notify prompts for text-based popup interactions."""

from voice_mode.server import mcp


@mcp.prompt()
def notify() -> str:
    """Have an ongoing text-based conversation using system notifications."""
    return """- You are in an ongoing text-based conversation with the user via system popup windows
- Use the 'notify' tool to display messages and receive user responses
- If this is a new conversation, greet briefly and ask how you can help
- If continuing, acknowledge and proceed
- Keep messages concise as they appear in a popup window
- Use wait_for_response=true (default) when you need input
- Use wait_for_response=false for status updates or final messages
- End the chat when the user indicates they want to end it"""
