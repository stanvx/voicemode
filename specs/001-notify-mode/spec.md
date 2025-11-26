# Feature Specification: Notify Mode - Text-Based Conversation via System Notifications

**Feature Branch**: `001-notify-mode`
**Created**: 2025-11-26
**Status**: Draft
**Input**: User description: "Add notification-based conversation mode with system notifications for text input instead of voice prompts"

## Overview

This feature introduces an alternative conversation mode that uses native system notifications instead of voice prompts. Users can interact with the LLM through notification pop-ups that display summaries (normally spoken) and accept text input responses. This enables silent, text-based interaction without requiring the terminal or application window focus.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Silent Notification Conversation (Priority: P1)

As a user who cannot use voice (in meetings, quiet environments, or with hearing impairments), I want to converse with the LLM through system notifications so that I can get responses and provide input without audio.

**Why this priority**: This is the core value proposition - enabling LLM conversation without voice, addressing accessibility and situational constraints.

**Independent Test**: Can be fully tested by triggering a `/notify` command and verifying a notification appears with the LLM response and input field, then submitting a text response and receiving the next notification.

**Acceptance Scenarios**:

1. **Given** the user has voicemode running, **When** they invoke the `/notify` tool or command, **Then** a system notification appears displaying the LLM's message with an input field for response.
2. **Given** a notification is displayed with an input field, **When** the user types a response and submits, **Then** the response is sent to the LLM and a new notification appears with the LLM's reply.
3. **Given** the user is in notify mode, **When** the LLM would normally speak a response, **Then** the response appears as a notification instead of being spoken.

---

### User Story 2 - Multi-line Input Support (Priority: P2)

As a user providing detailed context or code snippets, I want to enter multiple lines of text in the notification input so that I can provide comprehensive responses without character limitations.

**Why this priority**: Text input often requires more detail than voice, making multi-line support essential for practical use.

**Independent Test**: Can be tested by entering a multi-line response (using shift+enter or similar) in the notification input and verifying all lines are captured and sent to the LLM.

**Acceptance Scenarios**:

1. **Given** a notification with input field is displayed, **When** the user enters text with line breaks, **Then** all lines are preserved in the submitted response.
2. **Given** the user is composing a multi-line response, **When** they use the standard multi-line input gesture (shift+enter), **Then** a new line is added without submitting the response.

---

### User Story 3 - Cross-Platform Support (Priority: P2)

As a user on macOS, Windows, or Linux, I want the notify popup to work on my operating system so that I can use notify mode regardless of my platform.

**Why this priority**: Voicemode already supports multiple platforms; notify mode must also work cross-platform to maintain feature parity.

**Independent Test**: Can be tested on each platform by triggering notify mode and verifying the popup appears with correct styling and text input capabilities.

**Acceptance Scenarios**:

1. **Given** the user is on macOS, **When** notify mode is triggered, **Then** a popup window appears with the LLM response and input field.
2. **Given** the user is on Windows, **When** notify mode is triggered, **Then** a popup window appears with the LLM response and input field.
3. **Given** the user is on Linux, **When** notify mode is triggered, **Then** a popup window appears with the LLM response and input field.

---

### User Story 4 - Seamless Mode Switching (Priority: P3)

As a user who sometimes uses voice and sometimes needs silent mode, I want to easily switch between voice and notify modes so that I can adapt to my current environment.

**Why this priority**: Flexibility between modes enhances overall usability but is not required for initial functionality.

**Independent Test**: Can be tested by starting in voice mode, switching to notify mode mid-conversation, and verifying context is preserved.

**Acceptance Scenarios**:

1. **Given** the user is in voice conversation mode, **When** they invoke a switch command, **Then** subsequent interactions use notifications instead of voice.
2. **Given** the user switches from voice to notify mode, **When** the conversation continues, **Then** conversation context and history are preserved.

---

### User Story 5 - Conversation History Display (Priority: P3)

As a user in an ongoing conversation, I want to see recent message history in the popup so that I can maintain context without remembering previous exchanges.

**Why this priority**: Enhances usability but core functionality works without it.

**Independent Test**: Can be tested by conducting multiple exchanges and verifying previous messages are visible in the popup.

**Acceptance Scenarios**:

1. **Given** the user has exchanged multiple messages, **When** a new popup appears, **Then** it displays the current message plus recent history (scrollable).
2. **Given** the popup is showing history, **When** the user scrolls, **Then** they can view earlier messages in the conversation.

---

### User Story 6 - System Theme Integration (Priority: P3)

As a user with dark mode enabled on my system, I want the popup to match my system theme so that it doesn't cause visual jarring.

**Why this priority**: Aesthetic improvement that enhances integration but not required for functionality.

**Independent Test**: Can be tested by switching system theme and verifying popup appearance matches.

**Acceptance Scenarios**:

1. **Given** the user has dark mode enabled, **When** a popup appears, **Then** it uses dark theme colors.
2. **Given** the user has light mode enabled, **When** a popup appears, **Then** it uses light theme colors.

---

### User Story 7 - Optional Sound Feedback (Priority: P4)

As a user who wants audio confirmation, I want optional chime sounds when the popup appears or when I submit so that I have audible feedback like voice mode.

**Why this priority**: Nice-to-have for parity with voice mode but contradicts the silent use case.

**Independent Test**: Can be tested by enabling chime option and verifying sounds play at appropriate times.

**Acceptance Scenarios**:

1. **Given** the user has enabled chime feedback, **When** a popup appears, **Then** a notification sound plays.
2. **Given** the user has disabled chime feedback (default), **When** a popup appears, **Then** no sound is played.

---

### Edge Cases

- What happens when the user closes the popup without responding? The system should treat this as a cancel/dismiss action and allow the conversation to continue on next user-initiated action.
- What happens when multiple popups are requested rapidly? The system should queue or consolidate requests, showing only the most recent LLM response.
- How does the system behave in headless environments without a display? Fallback to terminal output with a clear error message explaining the issue.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a `/notify` tool/command that initiates popup-based conversation mode
- **FR-002**: System MUST display LLM responses in a popup window on the user's platform
- **FR-003**: Popup MUST include a multi-line text input area for user responses
- **FR-004**: Popup MUST appear as an always-on-top window for immediate visibility
- **FR-005**: System MUST preserve conversation context when switching between voice and notify modes
- **FR-006**: System MUST handle popup interactions without blocking the main application
- **FR-007**: Popup MUST include Submit and Cancel actions
- **FR-008**: System MUST support macOS, Windows, and Linux platforms
- **FR-009**: System MUST gracefully handle popup dismissal (Cancel or window close)
- **FR-010**: Popup SHOULD display recent conversation history (scrollable)
- **FR-011**: Popup SHOULD detect and match system theme (light/dark mode)
- **FR-012**: System SHOULD support optional chime sounds on popup events (disabled by default)
- **FR-013**: Popup SHOULD support clipboard operations (copy/paste) in text input

### Key Entities

- **NotifySession**: Represents an active popup-based conversation session, including conversation history and current state
- **NotifyPopup**: A popup window instance containing LLM message display, text input area, and action buttons

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can complete a full conversation exchange (prompt → response → follow-up) using only the popup within 30 seconds per exchange
- **SC-002**: Popup appears within 1 second of LLM response completion on all supported platforms
- **SC-003**: 95% of users can successfully submit text responses through the popup on first attempt
- **SC-004**: Multi-line input works correctly for responses up to 10,000 characters
- **SC-005**: Mode switching preserves 100% of conversation context
- **SC-006**: Notify mode works on all three supported platforms (macOS, Windows, Linux)
- **SC-007**: Popup correctly matches system theme on all supported platforms
- **SC-008**: Conversation history shows at least the last 5 message exchanges

## Design Notes

- A lightweight popup window approach is preferred over native system notifications for reliable multi-line text input across all platforms
- The popup should be non-blocking and appear as an always-on-top window for immediate visibility
- The popup displays the LLM message and provides a multi-line text area for user response

## Assumptions

- Python's built-in GUI capabilities are sufficient for the popup interface (no additional dependencies required)
- The existing voicemode conversation architecture can be extended to support non-voice input/output
- Users can interact with the popup window regardless of which application has focus
