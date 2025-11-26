# Research: Notify Mode

**Feature**: 001-notify-mode
**Date**: 2025-11-26
**Status**: Complete

## Research Tasks

### 1. Tkinter Cross-Platform Behavior

**Task**: Verify Tkinter availability and behavior across macOS, Linux, Windows

**Decision**: Use Tkinter with platform-specific adaptations for native appearance

**Rationale**:
- Tkinter is included in Python standard library (no additional dependency)
- Already tested on all three target platforms (macOS, Linux, Windows)
- Supports always-on-top windows via `wm_attributes('-topmost', True)`
- Supports multi-line text input via `Text` widget

**Alternatives Considered**:
- **PyQt/PySide**: Rejected - heavy dependency (~150MB), requires separate installation
- **Native notifications (pync, win10toast, libnotify)**: Rejected - limited multi-line input support, inconsistent APIs
- **Gradio**: Already in optional dependencies but too heavy for simple popup

**Platform-Specific Notes**:
- macOS: Use `wm_attributes('-topmost', 1)` and avoid deprecated methods
- Linux: Requires `python3-tk` package (handled by existing installer)
- Windows: Works out of box with Python installer

### 2. Non-Blocking Popup Pattern

**Task**: Research how to run Tkinter popup without blocking asyncio event loop

**Decision**: Use `threading` with queue-based communication

**Rationale**:
- Tkinter mainloop must run in main thread on macOS
- Use `threading.Thread` for Tkinter, `queue.Queue` for result passing
- Pattern already exists in codebase (see `record_audio_with_silence_detection`)

**Implementation Pattern**:
```python
import queue
import threading

def show_popup_sync(message: str) -> queue.Queue:
    """Show popup and return queue for result."""
    result_queue = queue.Queue()

    def run_popup():
        # Tkinter code here
        root = tk.Tk()
        # ... setup
        root.mainloop()
        result_queue.put(user_response)

    thread = threading.Thread(target=run_popup, daemon=True)
    thread.start()
    return result_queue

async def show_popup(message: str) -> str:
    """Async wrapper for popup."""
    result_queue = show_popup_sync(message)

    while result_queue.empty():
        await asyncio.sleep(0.1)

    return result_queue.get()
```

### 3. Existing Codebase Patterns

**Task**: Identify existing patterns to reuse

**Decision**: Follow `converse.py` structure and reuse logging infrastructure

**Findings**:
- **Tool Registration**: Use `@mcp.tool()` decorator from `voice_mode.server`
- **Logging**: Use `get_conversation_logger()` for conversation tracking
- **Configuration**: Access via `voice_mode.config` module
- **Platform Detection**: Reuse `installer/voicemode_install/system.py` patterns

**Key Imports to Reuse**:
```python
from voice_mode.server import mcp
from voice_mode.conversation_logger import get_conversation_logger
import voice_mode.config
```

### 4. OS-Native Appearance

**Task**: Research Tkinter styling for native OS integration

**Decision**: Use `ttk` themed widgets with platform-appropriate styling

**Rationale**:
- `ttk.Style()` provides native look on each platform automatically
- Use `ttk.Label`, `ttk.Button`, `ttk.Frame` instead of `tk.*` widgets
- Text widget (for multi-line input) uses `ttk`-compatible styling

**Styling Approach**:
```python
import tkinter as tk
from tkinter import ttk

root = tk.Tk()
style = ttk.Style()
# Let platform choose appropriate theme
# macOS: 'aqua', Linux: 'clam'/'alt', Windows: 'vista'/'xpnative'

# Modern padding and spacing
style.configure('TButton', padding=10)
style.configure('TLabel', padding=5)
```

### 5. Always-On-Top Behavior

**Task**: Verify always-on-top works on all platforms

**Decision**: Use `wm_attributes('-topmost', True)` with focus grabbing

**Implementation**:
```python
root = tk.Tk()
root.wm_attributes('-topmost', True)  # Stay on top
root.lift()  # Bring to front
root.focus_force()  # Grab focus
```

**Platform Notes**:
- macOS: Works but may require accessibility permissions for focus
- Linux: Works with most window managers (X11, Wayland via XWayland)
- Windows: Works natively

## Summary

| Topic | Decision | Dependencies Added |
|-------|----------|-------------------|
| GUI Framework | Tkinter (stdlib) | None |
| Threading | threading + queue | None (stdlib) |
| Styling | ttk themed widgets | None |
| Tool Pattern | Follow converse.py | None |
| Logging | Reuse conversation_logger | None |
| Theme Detection | Platform-specific detection | None |
| Clipboard | Tkinter built-in | None |
| Sound Feedback | Reuse play_chime_* functions | None |

**Total New Dependencies**: 0 (all stdlib or existing)

---

## Additional Research (Enhancements)

### 6. System Theme Detection

**Task**: Research dark/light mode detection across platforms

**Decision**: Use platform-specific detection with Tkinter fallback

**Implementation**:
```python
import platform
import subprocess

def detect_dark_mode() -> bool:
    """Detect if system is in dark mode."""
    system = platform.system()

    if system == "Darwin":  # macOS
        try:
            result = subprocess.run(
                ["defaults", "read", "-g", "AppleInterfaceStyle"],
                capture_output=True, text=True
            )
            return result.stdout.strip().lower() == "dark"
        except:
            return False

    elif system == "Linux":
        # Check GTK theme or desktop environment settings
        try:
            result = subprocess.run(
                ["gsettings", "get", "org.gnome.desktop.interface", "color-scheme"],
                capture_output=True, text=True
            )
            return "dark" in result.stdout.lower()
        except:
            return False

    elif system == "Windows":
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
            )
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            return value == 0
        except:
            return False

    return False
```

**Theme Colors**:
```python
LIGHT_THEME = {
    'bg': '#ffffff',
    'fg': '#000000',
    'input_bg': '#f5f5f5',
    'button_bg': '#e0e0e0'
}

DARK_THEME = {
    'bg': '#2d2d2d',
    'fg': '#ffffff',
    'input_bg': '#3d3d3d',
    'button_bg': '#4d4d4d'
}
```

### 7. Conversation History Display

**Task**: Research scrollable history in Tkinter

**Decision**: Use `Text` widget with readonly state for history, separate `Text` for input

**Implementation**:
```python
# History display (readonly)
history_frame = ttk.Frame(root)
history_text = tk.Text(history_frame, height=10, state='disabled')
scrollbar = ttk.Scrollbar(history_frame, command=history_text.yview)
history_text['yscrollcommand'] = scrollbar.set

# Add messages to history
history_text.config(state='normal')
history_text.insert('end', f"Assistant: {message}\n\n")
history_text.config(state='disabled')
history_text.see('end')  # Auto-scroll to bottom
```

### 8. Clipboard Support

**Task**: Verify clipboard works in Tkinter Text widget

**Decision**: Built-in support, no additional code needed

**Rationale**:
- Tkinter Text widget supports Ctrl+C/Cmd+C and Ctrl+V/Cmd+V by default
- Right-click context menu can be added optionally
- Works across all platforms

### 9. Optional Sound Feedback

**Task**: Research reusing existing chime functionality

**Decision**: Reuse `play_chime_start` and `play_chime_end` from `voice_mode.core`

**Implementation**:
```python
from voice_mode.core import play_chime_start, play_chime_end

async def show_popup_with_chime(message: str, chime_enabled: bool = False):
    if chime_enabled:
        await play_chime_start()

    response = await show_popup(message)

    if chime_enabled and response:
        await play_chime_end()

    return response
```
