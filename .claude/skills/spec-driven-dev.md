---
name: spec-driven-dev
description: Spec-driven development — Requirements → Design → Tasks → Implementation
---

# Spec-Driven Development Workflow
# Inspired by Pimzino/claude-code-spec-workflow

## Overview
Never write code without a spec. The flow is:
Requirements → Design → Task Breakdown → Implementation → Verification

## Phase 1: Requirements Spec

Create `specs/[feature-name]/requirements.md`:
```markdown
# Feature: [Name]

## Problem Statement
What problem does this solve? Who has this problem?

## User Stories
- As a [role], I want [capability] so that [benefit]

## Acceptance Criteria
- [ ] Criterion 1 (testable)
- [ ] Criterion 2 (testable)

## Constraints
- Performance: [requirements]
- Security: [requirements]
- Compatibility: [requirements]

## Out of Scope
- What this feature does NOT do
```

## Phase 2: Design Spec

Create `specs/[feature-name]/design.md`:
```markdown
# Design: [Feature Name]

## Architecture
[How it fits into the system]

## Data Model
[Schema changes, new models]

## API Design
[Endpoints, request/response formats]

## Component Design
[UI components, their props and state]

## Dependencies
[External libraries, services, APIs needed]

## Security Considerations
[Auth, validation, data protection]
```

## Phase 3: Task Breakdown

Create `specs/[feature-name]/tasks.md`:
```markdown
# Tasks: [Feature Name]

## Phase 1: Foundation
- [ ] Task 1 (estimated: S/M/L)
- [ ] Task 2 (depends on: Task 1)

## Phase 2: Core Logic
- [ ] Task 3
- [ ] Task 4

## Phase 3: Integration
- [ ] Task 5
- [ ] Task 6

## Phase 4: Testing & Polish
- [ ] Task 7: Write tests
- [ ] Task 8: Review & refactor
```

## Phase 4: Implementation
- Work through tasks in order
- Each task follows TDD (Red → Green → Refactor)
- Commit after each task completes
- Update task status as you go

## Phase 5: Verification
- Run full test suite
- Security scan
- Code review
- Check all acceptance criteria
- Update project documentation

## Bug Fix Flow
1. **Report**: Document the bug with reproduction steps
2. **Analyze**: Find root cause, write a failing test
3. **Fix**: Minimal change to fix the bug
4. **Verify**: All tests pass, no regressions
