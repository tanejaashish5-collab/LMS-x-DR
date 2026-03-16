# Testing Standards

## Coverage
- Target: 80%+ for branches, functions, lines, statements
- New code must include tests — no exceptions
- Bug fixes must include a regression test

## Test Structure
- Use Arrange-Act-Assert (AAA) pattern
- One assertion per concept (multiple asserts OK if testing same behavior)
- Test names describe behavior: `should [expected] when [condition]`

## Unit Tests
- Test functions in isolation
- Mock external dependencies (APIs, databases, file system)
- Fast execution: < 100ms per test
- No network calls, no file I/O

## Integration Tests
- Test component interactions
- Use test database with known seed data
- Clean up after each test (transactions or truncation)
- Test both success and error paths

## E2E Tests
- Cover critical user journeys only (auth, core features, payments)
- Keep stable — avoid flaky selectors
- Use data-testid attributes for element selection
- Run in CI before merge

## What to Test
- Happy path (expected inputs → expected outputs)
- Edge cases (null, empty, boundary values)
- Error scenarios (invalid input, network failure, timeout)
- Security cases (injection, unauthorized access)

## What NOT to Test
- Framework internals or third-party library behavior
- Private implementation details
- Trivial getters/setters with no logic
- Constants
