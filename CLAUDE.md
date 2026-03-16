# FVS-Dash-Claude

## Project Overview
FVS-Dash-Claude — an AI-powered dashboard application.

## Tech Stack
<!-- Update these as your stack is decided -->
- Frontend: TBD
- Backend: TBD
- Database: TBD
- AI: Claude API (Anthropic)

## Key Conventions
- Write clean, readable code with meaningful variable names
- Keep functions small and focused (< 50 lines)
- All public APIs must have error handling
- No hardcoded secrets — use environment variables
- Test coverage target: 80%+

## Development Workflow
1. Plan first: use `/plan` or the Planner agent before building
2. Build with TDD: write tests before implementation
3. Review: use `/code-review` before committing
4. Secure: use `/security-scan` on any code touching auth, APIs, or user input

## Architecture Principles
- Modularity: single responsibility, clear interfaces
- Security: defense in depth, least privilege
- Performance: optimize queries, minimize bundle size
- Simplicity: avoid premature abstraction

## Git Conventions
- Branch naming: `feature/`, `fix/`, `refactor/` prefixes
- Commit messages: imperative mood, explain the "why"
- PR descriptions: summary + test plan

## Agents (on-demand, separate context)
- `.claude/agents/planner.md` — Feature planning
- `.claude/agents/code-reviewer.md` — Code review
- `.claude/agents/security-reviewer.md` — Security audit
- `.claude/agents/architect.md` — System design
- `.claude/agents/tdd-guide.md` — Test-driven development
- `.claude/agents/build-error-resolver.md` — Fix build/type errors

## Skills (loaded only when invoked)
- `.claude/skills/plan.md` — Structured planning workflow
- `.claude/skills/tdd.md` — TDD red-green-refactor cycle
- `.claude/skills/code-review.md` — Comprehensive review checklist
- `.claude/skills/security-scan.md` — OWASP vulnerability scan

## Rules (per-language, loaded when relevant)
- `.claude/rules/common/` — Universal standards
- `.claude/rules/typescript/` — TS-specific rules
- `.claude/rules/python/` — Python-specific rules
