---
name: continuous-learning
description: Extract patterns and learnings from each session for future improvement
---

# Continuous Learning System
# Inspired by everything-claude-code's learning extraction

## What to Capture

### Code Patterns
- Reusable solutions discovered during implementation
- Performance optimizations that worked
- Bug fix patterns (root cause → fix mapping)
- Framework-specific tricks and gotchas

### Architectural Insights
- Design decisions and their rationale
- Trade-offs evaluated and outcomes
- Scaling strategies that proved effective
- Integration patterns between services

### Failure Patterns
- Common errors and their root causes
- Debugging approaches that worked
- Time-wasting approaches to avoid
- Misunderstandings about APIs or libraries

## When to Learn

### After Bug Fixes
```markdown
## Bug: [Description]
- **Root Cause**: [What actually caused it]
- **Fix**: [What solved it]
- **Prevention**: [How to prevent recurrence]
- **Time Spent**: [How long debugging took]
```

### After Feature Completion
```markdown
## Feature: [Name]
- **What Worked**: [Approaches that succeeded]
- **What Didn't**: [Approaches that failed]
- **Reusable Pattern**: [Code/approach to reuse]
- **Improvement**: [What to do differently next time]
```

### After Refactoring
```markdown
## Refactor: [What was refactored]
- **Before**: [Old pattern/structure]
- **After**: [New pattern/structure]
- **Why**: [Motivation for the change]
- **Impact**: [Measurable improvement]
```

## Storage

Append learnings to `.claude/memory/learnings.md` in chronological order.
Keep the file under 200 lines — archive old entries to `.claude/memory/archive/`.

## Usage

At session start, scan learnings for patterns relevant to the current task.
Before implementing, check if a similar problem was solved before.
