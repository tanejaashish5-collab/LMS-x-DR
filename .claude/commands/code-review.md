---
name: code-review
description: Run a comprehensive code review on recent changes
user_invocable: true
arguments: optional_scope
---

Load and execute the code review skill from `.claude/skills/code-review.md`.

Review the code changes for: $ARGUMENTS

If no scope provided, review all staged/uncommitted changes.
