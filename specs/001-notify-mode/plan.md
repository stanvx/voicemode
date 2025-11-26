# Implementation Plan: Notify Mode

**Branch**: `001-notify-mode` | **Date**: 2025-11-26 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-notify-mode/spec.md`

## Summary

Add a `/notify` MCP tool that provides text-based LLM conversation via a lightweight Tkinter popup window, enabling silent interaction without voice. The popup displays LLM messages and accepts multi-line text input, functioning as an alternative to the voice-based `/converse` tool.

## Technical Context

**Language/Version**: Python 3.10+ (matches existing project requirements)  
**Primary Dependencies**: 
- Tkinter (Python standard library - no additional dependency)
- FastMCP (existing - for MCP tool registration)
- Existing conversation/logging infrastructure from `voice_mode`

**Storage**: N/A (reuses existing conversation logging in `~/.voicemode/logs/`)  
**Testing**: pytest with pytest-asyncio (existing test infrastructure)  
**Target Platform**: macOS, Linux, Windows (cross-platform via Tkinter)
**Project Type**: Single project - extends existing `voice_mode/tools/` structure  
**Performance Goals**: Popup appears within 1 second of invocation  
**Constraints**: Non-blocking operation, always-on-top window behavior  
**Scale/Scope**: Single new MCP tool with supporting popup module

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. OpenAI API Compatibility | ✅ N/A | No voice service endpoints involved - text only |
| II. MCP-First Architecture | ✅ PASS | Implementing as MCP tool in `voice_mode/tools/notify.py` |
| III. Provider Resilience | ✅ N/A | No external providers - uses built-in Tkinter |
| IV. Privacy-Aware Design | ✅ PASS | Text input local; reuses existing conversation logging |
| V. Cross-Platform Consistency | ✅ PASS | Tkinter is cross-platform; follows existing platform patterns |

**Technical Standards Compliance:**
- Code size: Tool will be < 300 lines (following 100-300 line guideline)
- Popup module separate from tool (separation of concerns)
- Follows existing tool pattern from `converse.py`

## Project Structure

### Documentation (this feature)

```text
specs/001-notify-mode/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (MCP tool schema)
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

```text
voice_mode/
├── tools/
│   └── notify.py            # NEW: MCP tool for notify mode
├── utils/
│   └── notify_popup.py      # NEW: Tkinter popup implementation
└── [existing files unchanged]

tests/
├── test_notify.py           # NEW: Unit tests for notify tool
└── test_notify_popup.py     # NEW: Popup behavior tests
```

**Structure Decision**: Extends existing single project structure. New tool follows established pattern in `voice_mode/tools/`. Popup UI logic isolated in `voice_mode/utils/` to maintain separation of concerns.

## Complexity Tracking

No Constitution violations - minimal complexity addition:
- Single new MCP tool (follows existing pattern)
- Single utility module for UI (Tkinter - no new dependencies)
- Reuses existing logging infrastructure
