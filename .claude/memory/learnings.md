# Learnings Log

## 2026-03-16: Context Window Management
- **Problem**: Large CLAUDE.md caused context window errors
- **Root Cause**: CLAUDE.md loads into every single message
- **Fix**: Keep CLAUDE.md under 100 lines, use modular on-demand loading
- **Prevention**: Skills, agents, and commands load only when invoked; agents run in separate context
- **Pattern**: Modular architecture > monolithic configuration

## 2026-03-16: Multi-Source Configuration
- **Insight**: Don't rely on a single repo for all patterns
- **Pattern**: Survey the ecosystem, extract best components from multiple sources
- **Sources Used**: everything-claude-code, Trail of Bits, claude-cognitive, memory-mcp, claude-code-spec-workflow, OneRedOak workflows
- **Benefit**: Combines security expertise + memory innovation + workflow methodology
