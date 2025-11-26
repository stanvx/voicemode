"""Notify popup implementation using CustomTkinter.

Provides a modern, polished popup window for text-based conversations.
Features:
- Chat-style message bubbles
- Markdown rendering (code blocks, bold text)
- Selectable/copyable text
- Modern dark/light theme styling
- Keyboard shortcuts (Enter to send, Esc to close)

NOTE: On macOS, Tkinter MUST run on the main thread due to Cocoa framework
requirements. The implementation handles this by spawning a subprocess.
"""

import asyncio
import json
import logging
import platform
import queue
import re
import subprocess
import sys
import threading
from dataclasses import dataclass, asdict
from typing import Literal, Optional

logger = logging.getLogger("voicemode")

_IS_MACOS = platform.system() == "Darwin"


@dataclass
class ThemeColors:
    """Color scheme for modern popup appearance."""

    # Window
    window_bg: str
    surface_bg: str

    # Text
    text_primary: str
    text_secondary: str
    text_placeholder: str

    # Bubbles
    user_bubble_bg: str
    user_bubble_fg: str
    assistant_bubble_bg: str
    assistant_bubble_fg: str

    # Code blocks
    code_bg: str
    code_fg: str

    # Input
    input_bg: str
    input_border: str
    input_fg: str

    # Buttons
    accent: str
    accent_hover: str

    @classmethod
    def dark(cls) -> "ThemeColors":
        """Dark theme - Apple-style."""
        return cls(
            window_bg="#1c1c1e",
            surface_bg="#2c2c2e",
            text_primary="#ffffff",
            text_secondary="#98989d",
            text_placeholder="#555555",
            user_bubble_bg="#0a84ff",
            user_bubble_fg="#ffffff",
            assistant_bubble_bg="#2c2c2e",
            assistant_bubble_fg="#ffffff",
            code_bg="#111111",
            code_fg="#e5e5e7",
            input_bg="#000000",
            input_border="#3a3a3c",
            input_fg="#ffffff",
            accent="#0a84ff",
            accent_hover="#409cff",
        )

    @classmethod
    def light(cls) -> "ThemeColors":
        """Light theme - Apple-style."""
        return cls(
            window_bg="#f5f5f7",
            surface_bg="#ffffff",
            text_primary="#1d1d1f",
            text_secondary="#6e6e73",
            text_placeholder="#aeaeb2",
            user_bubble_bg="#007aff",
            user_bubble_fg="#ffffff",
            assistant_bubble_bg="#e9e9eb",
            assistant_bubble_fg="#1d1d1f",
            code_bg="#f4f4f4",
            code_fg="#1d1d1f",
            input_bg="#ffffff",
            input_border="#d1d1d6",
            input_fg="#1d1d1f",
            accent="#007aff",
            accent_hover="#0066cc",
        )


@dataclass
class PopupConfig:
    """Configuration for popup appearance and behavior."""

    title: str = "VoiceMode"
    width: int = 500
    height: int = 600
    topmost: bool = True
    timeout: Optional[float] = None
    show_history: bool = True
    history_limit: int = 5
    chime_enabled: bool = False
    theme: Literal["auto", "light", "dark"] = "auto"
    font_family: str = "SF Pro Text"
    font_size: int = 14


@dataclass
class NotifyPopupResult:
    """Result from popup interaction."""

    result_type: Literal["success", "cancelled", "dismissed", "timeout", "empty"]
    response: Optional[str] = None


def detect_dark_mode() -> bool:
    """Detect system dark mode."""
    if platform.system() == "Darwin":
        try:
            result = subprocess.run(
                ["defaults", "read", "-g", "AppleInterfaceStyle"],
                capture_output=True,
                text=True,
                timeout=1,
            )
            return result.stdout.strip().lower() == "dark"
        except Exception:
            return True  # Default to dark on macOS
    elif platform.system() == "Windows":
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
            )
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            winreg.CloseKey(key)
            return value == 0
        except Exception:
            return True
    return True  # Default to dark


def get_theme_colors(theme: Literal["auto", "light", "dark"]) -> ThemeColors:
    """Get colors based on theme setting."""
    if theme == "auto":
        return ThemeColors.dark() if detect_dark_mode() else ThemeColors.light()
    elif theme == "dark":
        return ThemeColors.dark()
    return ThemeColors.light()


def _run_popup_subprocess(
    message: str,
    config: PopupConfig,
    history: list[dict],
    wait_for_response: bool,
) -> NotifyPopupResult:
    """Run popup in subprocess with CustomTkinter UI."""

    popup_data = {
        "message": message,
        "config": asdict(config),
        "history": history,
        "wait_for_response": wait_for_response,
    }

    subprocess_code = '''
import sys
import json
import platform
import re

data = json.loads(sys.stdin.read())
message = data["message"]
config = data["config"]
history = data["history"]
wait_for_response = data["wait_for_response"]

try:
    import customtkinter as ctk
except ImportError:
    # Fallback to basic tkinter if customtkinter not available
    import tkinter as tk
    result = {"type": "dismissed", "response": None}
    root = tk.Tk()
    root.title("VoiceMode")
    tk.Label(root, text="CustomTkinter not installed").pack(padx=20, pady=20)
    root.after(2000, root.quit)
    root.mainloop()
    print(json.dumps(result))
    sys.exit(0)

# Theme detection
def detect_dark_mode():
    if platform.system() == "Darwin":
        import subprocess as sp
        try:
            result = sp.run(
                ["defaults", "read", "-g", "AppleInterfaceStyle"],
                capture_output=True, text=True, timeout=1
            )
            return result.stdout.strip().lower() == "dark"
        except Exception:
            return True
    return True

# Theme colors
class Colors:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

def get_colors(theme):
    is_dark = theme == "dark" or (theme == "auto" and detect_dark_mode())
    if is_dark:
        return Colors(
            window_bg="#1c1c1e",
            surface_bg="#2c2c2e",
            text_primary="#ffffff",
            text_secondary="#98989d",
            text_placeholder="#555555",
            user_bubble_bg="#0a84ff",
            user_bubble_fg="#ffffff",
            assistant_bubble_bg="#2c2c2e",
            assistant_bubble_fg="#ffffff",
            code_bg="#111111",
            code_fg="#e5e5e7",
            input_bg="#000000",
            input_border="#3a3a3c",
            input_fg="#ffffff",
            accent="#0a84ff",
            accent_hover="#409cff",
        )
    else:
        return Colors(
            window_bg="#f5f5f7",
            surface_bg="#ffffff",
            text_primary="#1d1d1f",
            text_secondary="#6e6e73",
            text_placeholder="#aeaeb2",
            user_bubble_bg="#007aff",
            user_bubble_fg="#ffffff",
            assistant_bubble_bg="#e9e9eb",
            assistant_bubble_fg="#1d1d1f",
            code_bg="#f4f4f4",
            code_fg="#1d1d1f",
            input_bg="#ffffff",
            input_border="#d1d1d6",
            input_fg="#1d1d1f",
            accent="#007aff",
            accent_hover="#0066cc",
        )

colors = get_colors(config.get("theme", "auto"))

# Configure CustomTkinter
ctk.set_appearance_mode("dark" if detect_dark_mode() else "light")

# Font configuration
IS_MACOS = platform.system() == "Darwin"
FONT_MAIN = ("SF Pro Text" if IS_MACOS else "Segoe UI", config.get("font_size", 14))
FONT_BOLD = ("SF Pro Text" if IS_MACOS else "Segoe UI", config.get("font_size", 14), "bold")
FONT_CODE = ("Menlo" if IS_MACOS else "Consolas", config.get("font_size", 14) - 1)
FONT_SMALL = ("SF Pro Text" if IS_MACOS else "Segoe UI", config.get("font_size", 14) - 2)

result = {"type": "dismissed", "response": None}


class MarkdownBubble(ctk.CTkFrame):
    """Chat bubble with markdown rendering support."""

    def __init__(self, master, text, is_user=False, colors=None, width=380, **kwargs):
        bg_color = colors.user_bubble_bg if is_user else colors.assistant_bubble_bg

        super().__init__(master, fg_color=bg_color, corner_radius=16, **kwargs)

        # Calculate height based on content - more compact
        lines = text.count("\\n") + 1
        char_lines = len(text) // 40 + 1  # Reduced from 50 for tighter layout
        estimated_height = min((lines + char_lines) * 18 + 20, 300)  # Reduced from 22+30, capped at 300

        self.textbox = ctk.CTkTextbox(
            self,
            text_color=colors.user_bubble_fg if is_user else colors.assistant_bubble_fg,
            fg_color="transparent",
            font=FONT_MAIN,
            height=estimated_height,
            width=width,
            wrap="word",
            activate_scrollbars=False,
        )
        self.textbox.pack(padx=14, pady=10)

        # Configure markdown tags
        self.textbox._textbox.tag_configure(
            "code",
            font=FONT_CODE,
            background=colors.code_bg,
            foreground=colors.code_fg,
            lmargin1=8,
            lmargin2=8,
            rmargin=8,
            spacing1=4,
            spacing3=4,
        )
        self.textbox._textbox.tag_configure("bold", font=FONT_BOLD)

        self._render_markdown(text)
        self.textbox.configure(state="disabled")

    def _render_markdown(self, text):
        """Parse and render markdown (code blocks and bold)."""
        # Split by code blocks
        parts = re.split(r"(```[\\s\\S]*?```)", text)

        for part in parts:
            if part.startswith("```") and part.endswith("```"):
                # Code block - strip markers and first line (language hint)
                code = part[3:-3].strip()
                if "\\n" in code:
                    # Remove language hint on first line
                    first_newline = code.find("\\n")
                    code = code[first_newline + 1:]
                self.textbox._textbox.insert("end", "\\n" + code + "\\n", "code")
            else:
                # Process bold text
                bold_parts = re.split(r"(\\*\\*[^*]+\\*\\*)", part)
                for subpart in bold_parts:
                    if subpart.startswith("**") and subpart.endswith("**"):
                        self.textbox._textbox.insert("end", subpart[2:-2], "bold")
                    else:
                        self.textbox._textbox.insert("end", subpart)


class VoiceModePopup(ctk.CTk):
    """Modern chat-style popup for VoiceMode notifications."""

    def __init__(self, message, config, history, wait_for_response, colors):
        super().__init__()

        self.colors = colors
        self.wait_for_response = wait_for_response
        self.result = {"type": "dismissed", "response": None}

        # Window setup
        width = config.get("width", 500)
        height = config.get("height", 600)

        self.title(config.get("title", "VoiceMode"))
        self.geometry(f"{width}x{height}")
        self.configure(fg_color=colors.window_bg)
        self.minsize(400, 400)

        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() - width) // 2
        y = (self.winfo_screenheight() - height) // 2 - 50
        self.geometry(f"{width}x{height}+{x}+{y}")

        # Always on top
        if config.get("topmost", True):
            self.wm_attributes("-topmost", True)
            self.lift()
            self.focus_force()

        # Close handler
        self.protocol("WM_DELETE_WINDOW", self._on_dismiss)

        # Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        header = ctk.CTkFrame(self, fg_color="transparent", height=50)
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(15, 5))
        header.grid_propagate(False)

        ctk.CTkLabel(
            header,
            text="✨ VoiceMode Chat",
            font=FONT_BOLD,
            text_color=colors.text_primary,
        ).pack(side="left")

        # Chat area
        self.chat_area = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=colors.accent,
            scrollbar_button_hover_color=colors.accent_hover,
        )
        self.chat_area.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)

        # Add history (current session only - no multi-message conversations)
        if config.get("show_history", True) and history:
            # Filter to show only the assistant's initial message and user responses
            # to keep it clean and focused on current session
            for entry in history[-config.get("history_limit", 3):]:
                role = entry.get("role", "unknown")
                content = entry.get("content", "")
                self._add_message(content, is_user=(role == "user"))

        # Add current message
        self._add_message(message, is_user=False)

        # Input area
        if wait_for_response:
            input_frame = ctk.CTkFrame(self, fg_color="transparent")
            input_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(5, 10))

            self.input_field = ctk.CTkTextbox(
                input_frame,
                height=60,
                corner_radius=16,
                border_width=1,
                border_color=colors.input_border,
                fg_color=colors.input_bg,
                text_color=colors.input_fg,
                font=FONT_MAIN,
            )
            self.input_field.pack(fill="both", side="left", expand=True, padx=(0, 10))

            # Send button
            send_btn = ctk.CTkButton(
                input_frame,
                text="→",
                width=50,
                height=50,
                corner_radius=25,
                fg_color=colors.accent,
                font=("SF Pro Text" if IS_MACOS else "Segoe UI", 20, "bold"),
                command=self._on_submit,
            )
            send_btn.pack(side="right")

            # Keyboard bindings
            self.input_field.bind("<Return>", self._on_enter)
            self.input_field.bind("<Shift-Return>", self._on_shift_enter)
            self.bind("<Escape>", self._on_escape)

            self.input_field.focus_set()

            # Bind text changes to auto-resize input field
            self.input_field.bind("<<Change>>", self._on_input_change)
        else:
            # Non-interactive mode - show dismiss button only
            footer = ctk.CTkFrame(self, fg_color="transparent", height=50)
            footer.grid(row=2, column=0, sticky="ew", padx=20, pady=(5, 20))

            ctk.CTkButton(
                footer,
                text="Dismiss",
                corner_radius=12,
                fg_color=colors.accent,
                font=FONT_MAIN,
                command=self._on_dismiss,
            ).pack(side="right")

            # Esc to close
            self.bind("<Escape>", lambda e: self._on_dismiss())

            # Note: No auto-close - notification stays until manually dismissed

        # Timeout (only if explicitly set)
        timeout = config.get("timeout")
        if timeout:
            self.after(int(timeout * 1000), self._on_timeout)

    def _add_message(self, text, is_user=False):
        """Add a message bubble to the chat."""
        container = ctk.CTkFrame(self.chat_area, fg_color="transparent")
        container.pack(fill="x", pady=5, padx=5)

        if not is_user:
            # Avatar for assistant
            avatar_frame = ctk.CTkFrame(container, fg_color="transparent")
            avatar_frame.pack(side="left", anchor="n", padx=(0, 8))

            ctk.CTkLabel(
                avatar_frame,
                text="🤖",
                font=("SF Pro Text" if IS_MACOS else "Segoe UI", 20),
            ).pack()

        bubble = MarkdownBubble(
            container,
            text,
            is_user=is_user,
            colors=self.colors,
            width=350 if is_user else 380,
        )
        bubble.pack(side="right" if is_user else "left", anchor="e" if is_user else "w")

        # Scroll to bottom
        self.after(50, lambda: self.chat_area._parent_canvas.yview_moveto(1.0))

    def _on_submit(self, event=None):
        global result
        text = self.input_field.get("1.0", "end-1c").strip()
        if text:
            result = {"type": "success", "response": text}
        else:
            result = {"type": "empty", "response": ""}
        self.quit()

    def _on_input_change(self, event=None):
        """Auto-resize input field based on content."""
        if not hasattr(self, 'input_field'):
            return

        # Get line count
        content = self.input_field.get("1.0", "end-1c")
        lines = content.count("\\n") + 1

        # Calculate height: min 60, max 200, with 20px per line
        new_height = min(max(60, lines * 20 + 20), 200)

        # Update height
        self.input_field.configure(height=new_height)

    def _on_enter(self, event):
        self._on_submit()
        return "break"

    def _on_shift_enter(self, event):
        # Allow default behavior (insert newline)
        return None

    def _on_escape(self, event=None):
        global result
        result = {"type": "cancelled", "response": None}
        self.quit()

    def _on_dismiss(self):
        global result
        result = {"type": "dismissed", "response": None}
        self.quit()

    def _on_timeout(self):
        global result
        result = {"type": "timeout", "response": None}
        self.quit()

    def _auto_close(self):
        global result
        result = {"type": "success", "response": None}
        self.quit()


# Run the popup
app = VoiceModePopup(message, config, history, wait_for_response, colors)
app.mainloop()

try:
    app.destroy()
except Exception:
    pass

print(json.dumps(result))
'''

    try:
        # Log subprocess execution for debugging
        logger.debug(f"Running popup subprocess with: {sys.executable}")

        process = subprocess.run(
            [sys.executable, "-c", subprocess_code],
            input=json.dumps(popup_data),
            capture_output=True,
            text=True,
            timeout=config.timeout + 10 if config.timeout else 600,
        )

        # Log all subprocess output for debugging
        if process.stderr:
            logger.debug(f"Subprocess stderr: {process.stderr}")
        if process.stdout:
            logger.debug(f"Subprocess stdout: {process.stdout[:500]}")
        logger.debug(f"Subprocess return code: {process.returncode}")

        if process.returncode == 0 and process.stdout.strip():
            result_data = json.loads(process.stdout.strip())
            return NotifyPopupResult(
                result_type=result_data.get("type", "dismissed"),
                response=result_data.get("response"),
            )
        else:
            logger.error(f"Subprocess failed - stderr: {process.stderr}, stdout: {process.stdout}")
            return NotifyPopupResult(result_type="dismissed", response=None)

    except subprocess.TimeoutExpired:
        return NotifyPopupResult(result_type="timeout", response=None)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse subprocess output: {e}")
        return NotifyPopupResult(result_type="dismissed", response=None)
    except Exception as e:
        logger.error(f"Subprocess popup failed: {e}")
        return NotifyPopupResult(result_type="dismissed", response=None)


# Global popup management
_current_popup = None
_popup_lock = threading.Lock()


class NotifyPopup:
    """Thread-based popup for non-macOS systems."""

    def __init__(
        self,
        message: str,
        config: PopupConfig,
        history: list[dict],
        wait_for_response: bool = True,
    ):
        self.message = message
        self.config = config
        self.history = history or []
        self.wait_for_response = wait_for_response
        self.result_queue: queue.Queue[NotifyPopupResult] = queue.Queue()
        self._thread: Optional[threading.Thread] = None
        self._closed = False

    def show(self) -> queue.Queue[NotifyPopupResult]:
        """Show popup in separate thread."""
        global _current_popup

        with _popup_lock:
            if _current_popup is not None and _current_popup != self:
                _current_popup.close(result_type="cancelled")
            _current_popup = self

        self._thread = threading.Thread(target=self._run_popup, daemon=True)
        self._thread.start()
        return self.result_queue

    def close(self, result_type: str = "dismissed", response: Optional[str] = None):
        """Close the popup."""
        if self._closed:
            return
        self._closed = True
        self.result_queue.put(NotifyPopupResult(result_type=result_type, response=response))

    def _run_popup(self):
        """Run the CustomTkinter popup."""
        # Use subprocess approach even on non-macOS for consistency
        result = _run_popup_subprocess(
            self.message,
            self.config,
            self.history,
            self.wait_for_response,
        )
        self.result_queue.put(result)

        global _current_popup
        with _popup_lock:
            if _current_popup == self:
                _current_popup = None


async def show_popup(
    message: str,
    config: PopupConfig,
    history: Optional[list[dict]] = None,
    wait_for_response: bool = True,
) -> NotifyPopupResult:
    """Show popup and wait for result asynchronously.

    Main entry point for displaying the notify popup.
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        _run_popup_subprocess,
        message,
        config,
        history or [],
        wait_for_response,
    )
