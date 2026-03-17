---
name: memory-management
description: Smart context and memory management using attention tiers
---

# Memory Management System
# Inspired by claude-cognitive's HOT/WARM/COLD attention tiers

## Attention Tier System

### HOT (Attention > 0.8) — Full Context
Files and information actively being worked on:
- Currently edited files → load full content
- Active test files → load full content
- Current error messages → load full content
- Files mentioned in the last 3 turns → load full content

### WARM (Attention 0.25-0.8) — Summary Only
Files recently relevant but not actively edited:
- Files edited in this session but not recently → load headers/signatures only
- Related test files → load test names only
- Import dependencies of HOT files → load interfaces/types only
- Architecture decisions → load ADR titles only

### COLD (Attention < 0.25) — Reference Only
Files not touched in this session:
- Don't load into context
- Reference by file path only
- Load on-demand if specifically needed

## Session Persistence Protocol

### On Session Start
1. Read `.claude/memory/session-context.md` if it exists
2. Load project state summary (last known good state)
3. Load active TODO items and their status
4. Load recent architectural decisions

### During Session
1. Track which files are being actively worked on (HOT)
2. Decay attention scores as time passes
3. When context gets large, suggest `/compact`
4. Save important findings to memory file

### On Session End / Before Compact
1. Save current state to `.claude/memory/session-context.md`:
   - What was being worked on
   - Key decisions made
   - Unresolved issues
   - Next steps
2. Save learned patterns to `.claude/memory/learnings.md`
3. Update project status

## Memory File Structure

```
.claude/memory/
├── session-context.md    ← current session state (auto-updated)
├── learnings.md          ← patterns and insights (append-only)
├── decisions.md          ← architectural decisions log
└── project-status.md     ← high-level project status
```

## Token Optimization Rules

1. Never load more than 3 full files simultaneously
2. Use file summaries (first 20 lines) for orientation
3. Prefer grep/search over full file reads
4. Compact early (at ~40% context, not 80%)
5. Offload deep analysis to subagents (separate context)
6. Keep CLAUDE.md under 100 lines (it loads every turn)
