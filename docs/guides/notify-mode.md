# Notify Mode Guide

Notify mode provides a text-based popup interface for conversing with the AI assistant when voice isn't appropriate, such as in meetings, quiet environments, or for accessibility needs.

## How to use notify mode

### Basic usage

The notify tool displays a popup window with a message and waits for your text response:

```
/notify "What would you like me to help you with?"
```

A popup window appears with:

- The assistant's message
- A text input area for your response
- Submit and Cancel buttons

### Keyboard shortcuts

| Shortcut | Action |
|----------|--------|
| `Enter` | Submit your response |
| `Shift+Enter` | Insert a new line |
| `Escape` | Cancel and close the popup |

### Available parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `message` | string | required | The message to display (1-10,000 characters) |
| `wait_for_response` | boolean | true | Whether to wait for user input |
| `timeout` | number | none | Auto-close timeout in seconds (5-300) |
| `title` | string | "VoiceMode" | Custom window title |
| `show_history` | boolean | true | Show recent conversation history |
| `chime_enabled` | boolean | false | Play sound feedback |
| `theme` | string | "auto" | Color theme: "auto", "light", or "dark" |

### Examples

#### Quick notification (no response needed)

Display a message without waiting for a response:

```
/notify message="Task completed successfully!" wait_for_response=false
```

#### Set a timeout

Automatically close after 30 seconds if no response:

```
/notify message="Are you still there?" timeout=30
```

#### Custom theme

Force a specific color theme:

```
/notify message="Hello!" theme=dark
```

## Switching between voice and notify mode

You can seamlessly switch between voice (`/converse`) and notify (`/notify`) modes. Conversation history is preserved across both modes, so the assistant maintains context regardless of which mode you're using.

## Platform support

Notify mode works on:

- **macOS**: Uses a subprocess to ensure Tkinter runs on the main thread
- **Windows**: Uses threaded Tkinter popup
- **Linux**: Uses threaded Tkinter popup (requires X11 or Wayland display)

### Headless environments

If you're running in a headless environment (SSH without X11 forwarding, server without display), the notify tool returns an error:

```
Error: Cannot display popup - no display available. This feature requires a graphical environment.
```

## Theme integration

When `theme="auto"` (the default), notify mode detects your system's dark/light mode setting:

- **macOS**: Reads `AppleInterfaceStyle` from system defaults
- **Linux**: Checks GTK theme via `gsettings`
- **Windows**: Reads the registry for `AppsUseLightTheme`

## Troubleshooting

### Popup doesn't appear

1. Ensure you have a graphical display available
2. On Linux, verify `DISPLAY` or `WAYLAND_DISPLAY` is set
3. Try running with `theme="light"` to rule out theme detection issues

### Popup appears but is unresponsive

1. Check that no other modal dialogs are blocking
2. Try clicking the window to ensure it has focus
3. On macOS, the popup should automatically take focus

## Using the notify prompt

You can use the built-in `notify` prompt to start a text-based conversation session:

1. Select the `notify` prompt from your MCP client
2. The assistant will initialize a text-based conversation using popup windows
3. Messages will appear in popups, and you can reply directly in the popup window

This is equivalent to manually instructing the assistant: "Start a text-based conversation using the notify tool."
