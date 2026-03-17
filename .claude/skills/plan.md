---
name: plan
description: Create a structured implementation plan for a feature or task
arguments: feature_description
---

# Planning Workflow

When the user invokes `/plan [feature]`, follow this structured process:

## Step 1: Understand
- Parse the feature request into concrete requirements
- List assumptions and open questions
- If critical information is missing, ask before proceeding

## Step 2: Explore
- Search the codebase for related files and patterns
- Identify existing code that can be reused or extended
- Map the dependency chain

## Step 3: Plan
Use the Planner agent (`.claude/agents/planner.md`) to generate a structured plan:
- Overview summary
- Phased implementation steps with file paths
- Testing strategy
- Risk assessment

## Step 4: Present
Output the plan in a clear, reviewable format. Wait for user approval before implementing.

## Key Rules
- Never implement without an approved plan
- Each phase must be independently testable
- Prefer extending existing code over creating new files
- Flag any architectural decisions that need input
