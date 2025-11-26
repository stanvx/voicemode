# Tasks: Notify Mode

**Input**: Design documents from `/specs/001-notify-mode/`
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, contracts/ ✓

**Tests**: Not explicitly requested in feature specification - test tasks omitted.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Project structure**: `voice_mode/` for source, `tests/` for tests (per plan.md)

---

## Phase 1: Setup

**Purpose**: Project initialization and basic structure

- [ ] T001 Create notify tool module structure at voice_mode/tools/notify.py
- [ ] T002 [P] Create popup utility module at voice_mode/utils/notify_popup.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T003 Implement base PopupConfig dataclass in voice_mode/utils/notify_popup.py with all configuration fields from data-model.md
- [ ] T004 [P] Implement ThemeColors dataclass with light/dark theme definitions in voice_mode/utils/notify_popup.py
- [ ] T005 [P] Implement system theme detection function (detect_dark_mode) in voice_mode/utils/notify_popup.py for macOS, Linux, and Windows
- [ ] T006 Implement base NotifyPopup class skeleton with threading pattern (queue-based communication) in voice_mode/utils/notify_popup.py
- [ ] T007 Register notify tool with MCP server using @mcp.tool() decorator in voice_mode/tools/notify.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Silent Notification Conversation (Priority: P1) 🎯 MVP

**Goal**: Enable basic popup-based conversation with LLM - display message and capture user text response

**Independent Test**: Trigger `/notify` tool, verify popup appears with message and input field, submit response, verify response is returned

### Implementation for User Story 1

- [ ] T008 [US1] Implement Tkinter window creation with title, size, and always-on-top positioning in voice_mode/utils/notify_popup.py
- [ ] T009 [US1] Implement message display area using ttk.Label or readonly Text widget in voice_mode/utils/notify_popup.py
- [ ] T010 [US1] Implement text input area using tk.Text widget with multi-line support in voice_mode/utils/notify_popup.py
- [ ] T011 [US1] Implement Submit and Cancel buttons with ttk.Button in voice_mode/utils/notify_popup.py
- [ ] T012 [US1] Implement keyboard bindings (Enter for submit, Escape for cancel) in voice_mode/utils/notify_popup.py
- [ ] T013 [US1] Implement async wrapper show_popup() using threading and queue pattern in voice_mode/utils/notify_popup.py
- [ ] T014 [US1] Implement notify tool handler with message parameter and wait_for_response logic in voice_mode/tools/notify.py
- [ ] T015 [US1] Implement response formatting (success, cancelled, empty input) per contracts/notify-tool.md in voice_mode/tools/notify.py
- [ ] T016 [US1] Add headless environment detection and error handling in voice_mode/tools/notify.py

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Multi-line Input Support (Priority: P2)

**Goal**: Support multi-line text input with Shift+Enter for new lines

**Independent Test**: Enter text with Shift+Enter, verify newlines are preserved in submitted response

### Implementation for User Story 2

- [ ] T017 [US2] Implement Shift+Enter binding for newline insertion in voice_mode/utils/notify_popup.py
- [ ] T018 [US2] Configure Text widget with appropriate height (input_rows from config) for multi-line visibility in voice_mode/utils/notify_popup.py
- [ ] T019 [US2] Add message length validation (1-10,000 characters per contract) in voice_mode/tools/notify.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Cross-Platform Support (Priority: P2)

**Goal**: Ensure popup works correctly on macOS, Windows, and Linux

**Independent Test**: Run on each platform, verify popup appears with correct styling and input capabilities

### Implementation for User Story 3

- [ ] T020 [P] [US3] Add platform-specific wm_attributes handling for always-on-top in voice_mode/utils/notify_popup.py
- [ ] T021 [P] [US3] Add platform-specific focus grabbing (lift, focus_force) in voice_mode/utils/notify_popup.py
- [ ] T022 [US3] Use ttk themed widgets for native OS appearance in voice_mode/utils/notify_popup.py
- [ ] T023 [US3] Add window centering logic for primary display in voice_mode/utils/notify_popup.py
- [ ] T042 [P] [US3] Verify clipboard operations (Ctrl+C/V on Windows/Linux, Cmd+C/V on macOS) work in Text widget - FR-013 coverage

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently

---

## Phase 6: User Story 4 - Seamless Mode Switching (Priority: P3)

**Goal**: Allow switching between voice and notify modes while preserving context

**Independent Test**: Start voice conversation, switch to notify, verify context preserved

### Implementation for User Story 4

- [ ] T024 [US4] Integrate with existing conversation_logger for logging text exchanges in voice_mode/tools/notify.py
- [ ] T025 [US4] Ensure conversation context flows between converse and notify tools via shared logging in voice_mode/tools/notify.py

**Checkpoint**: Mode switching preserves conversation context

---

## Phase 7: User Story 5 - Conversation History Display (Priority: P3)

**Goal**: Display recent conversation history in popup window

**Independent Test**: Exchange multiple messages, verify previous messages visible in popup

### Implementation for User Story 5

- [ ] T026 [US5] Implement conversation history display area using readonly Text widget with scrollbar in voice_mode/utils/notify_popup.py
- [ ] T027 [US5] Add show_history parameter support (default: true) in voice_mode/utils/notify_popup.py
- [ ] T028 [US5] Implement history_limit configuration (max 5 messages per data-model.md) in voice_mode/utils/notify_popup.py
- [ ] T029 [US5] Add auto-scroll to bottom when history is displayed in voice_mode/utils/notify_popup.py

**Checkpoint**: Conversation history displays correctly in popup

---

## Phase 8: User Story 6 - System Theme Integration (Priority: P3)

**Goal**: Match popup appearance to system light/dark mode

**Independent Test**: Toggle system theme, verify popup colors match

### Implementation for User Story 6

- [ ] T030 [US6] Implement theme parameter support (auto, light, dark) in voice_mode/utils/notify_popup.py
- [ ] T031 [US6] Apply ThemeColors to all widgets (bg, fg, input_bg, button_bg) in voice_mode/utils/notify_popup.py
- [ ] T032 [US6] Connect detect_dark_mode() to auto theme selection in voice_mode/utils/notify_popup.py

**Checkpoint**: Popup correctly matches system theme

---

## Phase 9: User Story 7 - Optional Sound Feedback (Priority: P4)

**Goal**: Play optional chime sounds on popup events

**Independent Test**: Enable chime_enabled, verify sounds play when popup appears

### Implementation for User Story 7

- [ ] T033 [US7] Add chime_enabled parameter support (default: false) in voice_mode/tools/notify.py
- [ ] T034 [US7] Integrate with existing play_chime_start/play_chime_end from voice_mode.core in voice_mode/tools/notify.py

**Checkpoint**: Optional sound feedback works when enabled

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T035 [P] Implement timeout parameter support (5-300 seconds) with auto-close in voice_mode/utils/notify_popup.py
- [ ] T036 [P] Implement concurrent popup handling (new popup closes existing, returns cancelled) in voice_mode/utils/notify_popup.py
- [ ] T037 Add title parameter support for custom window title in voice_mode/utils/notify_popup.py
- [ ] T038 Add comprehensive docstrings and type hints to all functions in voice_mode/tools/notify.py
- [ ] T039 [P] Add comprehensive docstrings and type hints to all functions in voice_mode/utils/notify_popup.py
- [ ] T040 Run quickstart.md validation scenarios manually
- [ ] T041 Update voice_mode module exports if needed for notify tool discovery

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-9)**: All depend on Foundational phase completion
  - User stories can proceed in priority order (P1 → P2 → P3 → P4)
  - US2 and US3 both P2, can run in parallel after US1
  - US4, US5, US6 all P3, can run in parallel
- **Polish (Phase 10)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational - Core popup and tool implementation
- **User Story 2 (P2)**: Depends on US1 - Extends input handling
- **User Story 3 (P2)**: Depends on US1 - Platform-specific enhancements
- **User Story 4 (P3)**: Depends on US1 - Adds logging integration
- **User Story 5 (P3)**: Depends on US1 - Adds history display
- **User Story 6 (P3)**: Depends on Foundational T004, T005 - Applies theme colors
- **User Story 7 (P4)**: Depends on US1 - Adds optional chimes

### Within Each User Story

- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- Setup tasks T001, T002 can run in parallel
- Foundational tasks T004, T005 can run in parallel (within Phase 2)
- US2 and US3 can run in parallel after US1 completes
- US4, US5, US6 can run in parallel after US1-3 complete
- All tasks marked [P] within a phase can run in parallel

---

## Parallel Example: Foundational Phase

```bash
# After T003 completes, launch these in parallel:
Task: "Implement ThemeColors dataclass" (T004)
Task: "Implement system theme detection" (T005)
```

## Parallel Example: User Story 3

```bash
# Launch these in parallel:
Task: "Platform-specific wm_attributes handling" (T020)
Task: "Platform-specific focus grabbing" (T021)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T002)
2. Complete Phase 2: Foundational (T003-T007)
3. Complete Phase 3: User Story 1 (T008-T016)
4. **STOP and VALIDATE**: Test notify tool independently
5. Deploy/demo if ready - basic popup conversation works

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add User Story 1 → Test → MVP ready (basic popup works)
3. Add User Story 2 → Test → Multi-line input works
4. Add User Story 3 → Test → Cross-platform verified
5. Add User Stories 4-6 → Test → Enhanced UX complete
6. Add User Story 7 → Test → Full feature complete

---

## Notes

- All source code in voice_mode/ following existing project structure
- Tkinter is Python stdlib - no new dependencies required
- Follow existing patterns from voice_mode/tools/converse.py
- Reuse conversation_logger for logging text exchanges
- Thread-safe popup implementation using queue pattern from research.md
