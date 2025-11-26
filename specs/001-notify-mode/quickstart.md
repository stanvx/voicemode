# Quickstart: Notify Mode

**Feature**: 001-notify-mode
**Date**: 2025-11-26

## Overview

Notify Mode provides a text-based conversation alternative to voice interaction. Instead of speaking and listening, messages appear in a popup window where you can type responses.

## Prerequisites

- VoiceMode installed and configured
- Graphical display available (not headless/SSH without X forwarding)
- Python with Tkinter (included in standard Python installation)

## Usage

### Basic Conversation

The `/notify` tool works similarly to `/converse` but uses text instead of voice:

```
Claude: I'll ask you a question using the notify popup.
[Uses notify tool with message: "What would you like me to help you with?"]
[Popup appears with message and text input field]
[User types response and clicks Submit]
Response: "I need help with my Python project"
```

### Display-Only Mode

To show information without waiting for a response:

```
[Uses notify tool with message: "Task completed!", wait_for_response: false]
[Popup appears briefly showing the message]
```

### With Timeout

For time-sensitive prompts:

```
[Uses notify tool with message: "Enter your choice (1-3):", timeout: 30]
[User has 30 seconds to respond before timeout]
```

## When to Use

| Use Case | Tool |
|----------|------|
| Voice conversation | `/converse` |
| Silent/text conversation | `/notify` |
| In meetings or quiet environments | `/notify` |
| Accessibility (hearing impairment) | `/notify` |
| Quick status notifications | `/notify` with `wait_for_response: false` |

## Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Submit response | Enter or click Submit |
| New line in response | Shift+Enter |
| Cancel/dismiss | Escape or click Cancel |

## Troubleshooting

### Popup doesn't appear

1. Check if you have a display available (`echo $DISPLAY` on Linux)
2. Ensure Tkinter is installed: `python -c "import tkinter; print('OK')"`
3. On Linux, install if missing: `sudo apt install python3-tk`

### Focus issues

The popup should appear on top of other windows. If it doesn't:
- Look in your taskbar/dock for "VoiceMode"
- The popup should grab focus automatically

### No response after timeout

If you see "No response within Xs timeout":
- The popup was displayed but no input was received
- Increase the timeout value if needed
