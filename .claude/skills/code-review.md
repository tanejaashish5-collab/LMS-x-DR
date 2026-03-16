---
name: code-review
description: Comprehensive code review with severity classification
arguments: optional_file_or_branch
---

# Code Review Workflow

When the user invokes `/code-review`, perform a structured review:

## Step 1: Gather Changes
- Get the diff (staged changes, or branch diff against main)
- Identify all modified/added files
- Understand the scope and purpose of changes

## Step 2: Review by Severity
Use the Code Reviewer agent (`.claude/agents/code-reviewer.md`) to check:

### CRITICAL — Security & Data
- Hardcoded secrets, SQL injection, XSS
- Auth bypasses, data exposure

### HIGH — Code Quality
- Functions > 50 lines, nesting > 4 levels
- Missing error handling, dead code
- Debug statements left in

### MEDIUM — Performance
- Inefficient algorithms, missing caching
- Unbounded queries, N+1 patterns

### LOW — Style
- Naming, documentation, consistency

## Step 3: Report
Output findings with:
- File and line references
- Problematic code snippet
- Suggested fix
- Severity classification
- Overall verdict: APPROVE / WARNING / BLOCK

## Rules
- Only flag issues with >80% confidence
- Acknowledge good patterns (positive feedback)
- Provide fix suggestions, not just complaints
