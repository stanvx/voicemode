# Data Model: Notify Mode

**Feature**: 001-notify-mode
**Date**: 2025-11-26

## Entities

### NotifySession

Represents an active popup-based conversation session.

| Field | Type | Description |
|-------|------|-------------|
| session_id | str | Unique identifier (UUID) |
| started_at | datetime | Session start timestamp |
| conversation_history | list[dict] | List of message exchanges |
| is_active | bool | Whether session is currently active |

**Notes**:
- **Conceptual entity** - not implemented as a separate class
- Handled by existing `conversation_logger` infrastructure
- Reuses existing conversation logging patterns
- Stored in `~/.voicemode/logs/conversations/` (existing infrastructure)

### NotifyMessage

A single message in the notification conversation.

| Field | Type | Description |
|-------|------|-------------|
| role | str | "assistant" or "user" |
| content | str | Message text content |
| timestamp | datetime | When message was created |

**Notes**:
- **Conceptual entity** - logged via existing conversation_logger, not a separate implementation
- Follows same message format as voice mode exchanges

### PopupConfig

Configuration for popup appearance and behavior.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| title | str | "VoiceMode" | Window title |
| width | int | 500 | Window width in pixels |
| height | int | 400 | Window height in pixels |
| topmost | bool | True | Always on top |
| timeout | float | None | Auto-close timeout in seconds (5-300, optional) |
| show_history | bool | True | Show conversation history |
| history_limit | int | 5 | Max messages to show in history |
| chime_enabled | bool | False | Play sounds on popup events |
| theme | str | "auto" | "auto", "light", or "dark" |
| input_rows | int | 4 | Number of visible rows in text input area |
| initial_focus | str | "input" | Element receiving initial focus ("input" or "submit") |

### ThemeColors

Color scheme for popup appearance.

| Field | Type | Description |
|-------|------|-------------|
| bg | str | Background color (hex) |
| fg | str | Foreground/text color (hex) |
| input_bg | str | Input field background |
| button_bg | str | Button background |
| accent | str | Accent color for focus states |

## State Transitions

```
[Idle] --invoke notify--> [Popup Shown]
   |                           |
   |                           +--user submits--> [Processing] --return--> [Idle]
   |                           |
   |                           +--user cancels--> [Idle]
   |                           |
   |                           +--window closed-> [Idle]
```

## Validation Rules

1. **Message Content**:
   - Minimum length: 1 character
   - Maximum length: 10,000 characters (reasonable for text conversation)

2. **Timeout**:
   - Minimum: 5 seconds
   - Maximum: 300 seconds (5 minutes)
   - Default: No timeout (waits indefinitely)

3. **Popup Behavior**:
   - Only one popup active at a time
   - New popup request closes existing popup (returns cancelled)
   - Cancel/close returns `None` to indicate dismissal
   - Empty input submission is treated as valid response (returns empty string)

4. **Focus and Visibility**:
   - Text input receives initial focus
   - Window positioned center of primary display
   - Always-on-top enabled by default

## Integration Points

### Existing Infrastructure Reuse

| Component | Location | Usage |
|-----------|----------|-------|
| Conversation Logger | `voice_mode/conversation_logger.py` | Log text exchanges |
| MCP Server | `voice_mode/server.py` | Tool registration |
| Config Module | `voice_mode/config.py` | Shared configuration |
| Event Logger | `voice_mode/utils/` | Optional event tracking |
