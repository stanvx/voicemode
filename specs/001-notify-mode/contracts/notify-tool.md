# MCP Tool Contract: notify

**Feature**: 001-notify-mode
**Date**: 2025-11-26

## Tool Definition

```json
{
  "name": "notify",
  "description": "Display a message in a popup window and optionally wait for user text response. Use this for silent, text-based conversation instead of voice.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "message": {
        "type": "string",
        "minLength": 1,
        "maxLength": 10000,
        "description": "The message to display in the popup (1-10,000 characters)"
      },
      "wait_for_response": {
        "type": "boolean",
        "default": true,
        "description": "Whether to wait for user input. If false, just displays the message."
      },
      "timeout": {
        "type": "number",
        "minimum": 5,
        "maximum": 300,
        "description": "Optional timeout in seconds for user response (5-300 seconds, default: no timeout)"
      },
      "title": {
        "type": "string",
        "default": "VoiceMode",
        "description": "Window title for the popup"
      },
      "show_history": {
        "type": "boolean",
        "default": true,
        "description": "Whether to show recent conversation history in the popup"
      },
      "chime_enabled": {
        "type": "boolean",
        "default": false,
        "description": "Whether to play sound feedback (disabled by default for silent use)"
      },
      "theme": {
        "type": "string",
        "enum": ["auto", "light", "dark"],
        "default": "auto",
        "description": "Color theme for the popup. 'auto' matches system setting."
      }
    },
    "required": ["message"]
  }
}
```

## Response Format

### Success with Response
```json
{
  "content": [
    {
      "type": "text",
      "text": "User response: Hello, this is my reply to the message."
    }
  ]
}
```

### Success without Response (wait_for_response=false)
```json
{
  "content": [
    {
      "type": "text",
      "text": "✓ Message displayed successfully"
    }
  ]
}
```

### User Cancelled (via Cancel button or Escape key)
```json
{
  "content": [
    {
      "type": "text",
      "text": "User cancelled the popup"
    }
  ]
}
```

### User Dismissed (via window close button)
```json
{
  "content": [
    {
      "type": "text",
      "text": "User dismissed the popup"
    }
  ]
}
```

### Timeout
```json
{
  "content": [
    {
      "type": "text",
      "text": "No response within {timeout}s timeout"
    }
  ]
}
```

**Note**: The `{timeout}` value reflects the actual timeout specified in the request.

### Empty Input
```json
{
  "content": [
    {
      "type": "text",
      "text": "User submitted empty response"
    }
  ]
}
```

### Error (Headless Environment)
```json
{
  "content": [
    {
      "type": "text",
      "text": "Error: Cannot display popup - no display available. This feature requires a graphical environment."
    }
  ]
}
```

## Example Usage

### Basic Conversation
```
Tool: notify
Input: {"message": "What would you like me to help you with today?"}
Output: "User response: I need help writing a Python script for data processing."
```

### Display Only (No Response)
```
Tool: notify
Input: {"message": "Task completed successfully!", "wait_for_response": false}
Output: "✓ Message displayed successfully"
```

### With Timeout
```
Tool: notify
Input: {"message": "Please enter your API key:", "timeout": 30}
Output: "User response: sk-1234..."
```

## Behavioral Specifications

### Concurrent Popup Handling

If a new `notify` call is made while a popup is already displayed:
- The existing popup is closed and returns "User cancelled or dismissed the popup"
- The new popup is displayed with the new message
- Only one popup can be active at any time

### Window Positioning

- Popup appears centered on the primary display
- On multi-monitor setups, uses the display containing the active window or mouse cursor

### Focus Behavior

- The text input area receives focus immediately when the popup appears
- The popup window is brought to the foreground (always-on-top)

### Long Message Handling

- Messages exceeding the visible area are displayed in a scrollable region
- The full message is always accessible via scrolling

### Conversation History Scroll Behavior

- History is displayed in a scrollable readonly text area above the input field
- New messages automatically scroll to the bottom (most recent visible)
- User can scroll up to view earlier messages
- Maximum 5 exchanges shown (configurable via `history_limit`)

### Platform-Specific Theme Detection

- **macOS**: Uses `defaults read -g AppleInterfaceStyle` to detect dark mode
- **Windows**: Reads `HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize\AppsUseLightTheme` registry key
- **Linux**: Uses `gsettings get org.gnome.desktop.interface color-scheme` for GNOME/GTK environments
- Fallback: Light theme if detection fails

### Platform-Specific Chime Sound Support

- Reuses existing `play_chime_start` and `play_chime_end` functions from `voice_mode.core`
- Chimes disabled by default for silent use case
- When enabled, plays start chime on popup appear and end chime on successful submit

### Relationship with `converse` Tool

- `notify` is a parallel alternative to `converse`, not a replacement
- Both tools share conversation context via the existing `conversation_logger` infrastructure
- `notify` uses visual popup instead of audio for input/output
- Users can switch between tools mid-conversation; context is preserved

### Mode Switching Behavior

- Switching from voice mode to notify mode preserves all conversation history
- The next interaction uses the newly selected mode
- No explicit "mode switch" command required - simply use the desired tool
- Conversation logger records both voice and notify exchanges in the same session

### Clipboard Operations

- Text input area supports standard clipboard operations:
  - **macOS**: Cmd+C (copy), Cmd+V (paste), Cmd+X (cut), Cmd+A (select all)
  - **Windows/Linux**: Ctrl+C (copy), Ctrl+V (paste), Ctrl+X (cut), Ctrl+A (select all)
- Clipboard operations are handled by Tkinter's built-in Text widget bindings

### Accessibility

- Screen reader compatibility: Tkinter provides basic accessibility through platform accessibility APIs
- High contrast mode: Respects system high contrast settings where supported
- Minimum recommended contrast ratio: 4.5:1 for normal text (WCAG AA)
