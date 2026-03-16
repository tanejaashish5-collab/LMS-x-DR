---
name: tdd
description: Test-Driven Development workflow — Red, Green, Refactor
arguments: feature_or_function
---

# TDD Workflow

When the user invokes `/tdd [feature]`, follow the Red-Green-Refactor cycle:

## Step 1: RED — Write Failing Tests
- Understand what behavior is expected
- Write test(s) that describe the expected behavior
- Run tests — confirm they FAIL for the right reason
- Do NOT write implementation yet

## Step 2: GREEN — Minimal Implementation
- Write the MINIMUM code to make tests pass
- No optimization, no extra features
- Run tests — confirm they PASS

## Step 3: REFACTOR — Clean Up
- Improve code quality (naming, structure, duplication)
- Run tests after each change — they must stay GREEN
- Extract reusable patterns if needed

## Step 4: Edge Cases
- Add tests for null/undefined, empty inputs, boundaries
- Add error scenario tests
- Repeat RED-GREEN-REFACTOR for each

## Step 5: Coverage Check
- Verify 80%+ coverage on new code
- Add missing tests if below threshold

## Rules
- One test at a time — don't batch
- Tests must be independent (no shared state)
- Mock external dependencies, not internal logic
- Test names describe behavior: `should return X when Y`
