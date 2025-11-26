#!/usr/bin/env python3
"""Manual test for notify popup.

Run with: python tests/manual/test_notify_popup.py

This must be run directly (not via pytest) because Tkinter 
requires the main thread on macOS.
"""

import sys
import asyncio
from voice_mode.utils.notify_popup import show_popup, PopupConfig


def main():
    """Run popup test on main thread."""
    print("Testing notify popup...")
    print("A popup window should appear. Try:")
    print("  1. Type a message and press Enter (or click Submit)")
    print("  2. Press Escape (or click Cancel)")
    print("  3. Use Shift+Enter for multi-line input")
    print()

    config = PopupConfig(
        title="VoiceMode Test",
        timeout=60,
        show_history=False,
        theme="auto",
    )
    
    # Create a test history
    history = [
        {"role": "assistant", "content": "Hello! How can I help you today?"},
        {"role": "user", "content": "I'm testing the notify popup feature."},
    ]

    # We need to run this on the main thread for macOS
    # Use asyncio.run() which handles the event loop properly
    try:
        result = asyncio.run(show_popup(
            message="This is a test message from VoiceMode notify mode. Please type a response below and click Submit (or press Enter).\n\nTry Shift+Enter for a new line!",
            config=config,
            history=history,
            wait_for_response=True,
        ))
        print()
        print(f"Result type: {result.result_type}")
        print(f"Response: {result.response}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
