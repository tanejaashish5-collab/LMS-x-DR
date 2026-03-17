# FVS-Dash-Claude

## Project Overview
FVS-Dash-Claude — AI-powered autonomous business platform.

## Tech Stack
- Frontend: Next.js 15 (App Router) + Tailwind + shadcn/ui
- Backend: Next.js API Routes + Supabase
- Database: Supabase (Postgres)
- Payments: Stripe
- AI: Claude API (Anthropic)
- Hosting: Vercel

## Key Conventions
- Clean, readable code with meaningful names
- Functions < 50 lines, nesting < 4 levels
- All APIs have error handling + input validation
- No hardcoded secrets — env vars only
- Test coverage: 80%+
- Security: see `.claude/rules/security/`

## Development Workflow
1. Spec first → `.claude/skills/spec-driven-dev.md`
2. Plan → `/plan` or Planner agent
3. Build with TDD → `/tdd`
4. Review → `/code-review`
5. Security → `/security-scan`
6. Design review → `.claude/skills/design-review.md`

## Memory System
- Session context: `.claude/memory/session-context.md`
- Learnings: `.claude/memory/learnings.md`
- Decisions: `.claude/memory/decisions.md`
- Attention tiers: HOT (full load) / WARM (headers) / COLD (reference)

## Agents (9 specialists, separate context)
- `planner.md` — Feature planning
- `architect.md` — System design
- `code-reviewer.md` — Code review
- `security-reviewer.md` — Security audit
- `tdd-guide.md` — Test-driven development
- `build-error-resolver.md` — Fix build errors
- `research-agent.md` — Market & tech research
- `fullstack-builder.md` — Rapid MVP building
- `automation-architect.md` — Autonomous pipeline design

## Skills (8 workflows, on-demand)
- `plan.md` / `tdd.md` / `code-review.md` / `security-scan.md`
- `spec-driven-dev.md` — Spec → Design → Build
- `multi-agent.md` — Parallel agent orchestration
- `design-review.md` — Visual UI/UX review
- `memory-management.md` — Context & attention tiers
- `continuous-learning.md` — Pattern extraction

## Rules
- `rules/security/` — Deny rules, injection protection, sandbox
- `rules/common/` — Coding + testing standards
- `rules/typescript/` — TS-specific
- `rules/python/` — Python-specific

## MCP Servers (see `.claude/mcp-configs/`)
- GitHub, Playwright, DBHub, Context7, Memory, Stripe, Supabase, Vercel
