# Common Coding Standards

## Code Quality
- Functions should do one thing and do it well
- Maximum function length: 50 lines
- Maximum nesting depth: 4 levels
- Maximum file length: 300 lines (split if larger)
- Use descriptive names — no single-letter variables except loop counters

## Error Handling
- Always handle errors from external calls (API, DB, file I/O)
- Never swallow errors silently — log or propagate
- Use specific error types, not generic `Error`
- Return meaningful error messages to callers
- Never expose stack traces or internal details to end users

## Security
- No hardcoded secrets, tokens, or credentials
- Use environment variables for all configuration
- Validate and sanitize all user input
- Use parameterized queries — never concatenate SQL
- Apply least privilege principle
- Escape output to prevent XSS

## Performance
- Avoid O(n²) when O(n) is possible
- Use pagination for list endpoints
- Cache expensive computations and frequent queries
- Lazy load resources when possible
- Set timeouts on all external requests

## Git & Collaboration
- Commit messages in imperative mood: "Add feature" not "Added feature"
- One logical change per commit
- No commented-out code in commits
- No debug statements (console.log, print, debugger) in commits

## Documentation
- Document the "why", not the "what"
- Add comments only for non-obvious logic
- Keep README up to date with setup instructions
- Document API endpoints and their contracts
