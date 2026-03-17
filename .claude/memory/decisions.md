# Architecture Decision Records

## ADR-001: Modular Claude Code Configuration

### Status: Accepted

### Context
User previously experienced context window errors from a monolithic CLAUDE.md. Needed a system that provides the power of comprehensive configuration without the context cost.

### Decision
Adopt a modular architecture inspired by everything-claude-code:
- Slim CLAUDE.md (~55 lines) for per-turn loading
- Agents in `.claude/agents/` running in isolated contexts
- Skills in `.claude/skills/` loaded on-demand only
- Commands in `.claude/commands/` as thin wrappers
- Rules in `.claude/rules/` per-language
- Hooks in `.claude/hooks.json` running externally

### Consequences
**Positive:**
- Context window stays clean
- Tools available on-demand without constant cost
- Agents get isolated context (no cross-contamination)
- Easy to add/remove components

**Negative:**
- More files to manage
- Need to know which skill/agent to invoke

## ADR-002: Multi-Source Best Practices

### Status: Accepted

### Context
Single-source configurations reflect one person's perspective. The ecosystem has 80+ repos with different strengths.

### Decision
Extract best components from multiple sources:
- Security: Trail of Bits
- Memory: claude-cognitive + memory-mcp
- Workflows: claude-code-spec-workflow
- Design Review: OneRedOak
- Core System: everything-claude-code

### Consequences
**Positive:**
- Best-in-class for each domain
- No single point of failure in methodology
- Diverse perspectives improve quality

**Negative:**
- Integration effort between different approaches
- May need adaptation as sources update independently
