---
name: multi-agent
description: Multi-agent orchestration — decompose tasks and run agents in parallel
---

# Multi-Agent Orchestration
# Inspired by claude-squad and claude-swarm patterns

## When to Use Multi-Agent

Use when a task can be decomposed into independent subtasks:
- Building multiple features simultaneously
- Running code review + security scan + tests in parallel
- Researching multiple topics concurrently
- Processing multiple files independently

## Orchestration Pattern

### Step 1: Decompose
Break the task into independent units:
```
Main Task: "Build user authentication system"
├── Subtask A: Design database schema (Architect agent)
├── Subtask B: Research auth libraries (Explore agent)
├── Subtask C: Write auth middleware tests (TDD agent)
└── Subtask D: Security threat model (Security agent)
```

### Step 2: Identify Dependencies
```
A (schema) ──→ C (tests need schema)
B (research) ──→ independent
D (security) ──→ independent
```

### Step 3: Parallelize Independent Work
```
PARALLEL:
  Launch Agent B (research) ──→ results
  Launch Agent D (security) ──→ results

SEQUENTIAL (after A completes):
  Launch Agent A (schema) ──→ schema
  Launch Agent C (tests, using schema) ──→ tests
```

### Step 4: Synthesize
Combine all agent results into a unified implementation plan.

## Agent Selection Guide

| Task Type | Agent | Model |
|-----------|-------|-------|
| Architecture decisions | Architect | Opus |
| Feature planning | Planner | Opus |
| Code quality review | Code Reviewer | Opus |
| Security audit | Security Reviewer | Opus |
| Test writing | TDD Guide | Opus |
| Build error fixes | Build Error Resolver | Sonnet |
| File exploration | Explore subagent | Sonnet |
| Simple code changes | General subagent | Sonnet |

## Cost Optimization

- Use Sonnet for simple, well-defined tasks
- Reserve Opus for complex reasoning and architecture
- Each agent runs in its own context → no cross-contamination
- Agents see only what they need → less token waste
- Prefer 3 focused agents over 1 overloaded agent

## Anti-Patterns

- Don't spawn agents for trivial tasks (< 3 steps)
- Don't have agents duplicate each other's work
- Don't spawn more than 5 agents simultaneously
- Don't have agents modify the same files in parallel
- Always synthesize results before acting on them
