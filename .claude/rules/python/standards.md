# Python Standards

## Style
- Follow PEP 8 conventions
- Use type hints on all function signatures
- Use f-strings for string formatting
- Maximum line length: 88 characters (Black formatter)
- Use snake_case for functions/variables, PascalCase for classes

## Patterns
- Use context managers (`with`) for resource management
- Prefer list/dict comprehensions over loops for transformations
- Use `pathlib.Path` over `os.path`
- Use `dataclasses` or `pydantic` for data structures
- Use `enum.Enum` for fixed sets of values

## Error Handling
- Catch specific exceptions, never bare `except:`
- Use custom exception classes for domain errors
- Log exceptions with `logger.exception()` for full traceback
- Use `raise ... from` to chain exceptions

## Async
- Use `asyncio` for I/O-bound concurrency
- Use `async with` for async context managers
- Gather independent coroutines with `asyncio.gather()`
- Set timeouts on external calls

## Testing
- Use `pytest` as the test framework
- Use fixtures for setup/teardown
- Use `pytest.mark.parametrize` for data-driven tests
- Mock with `unittest.mock` or `pytest-mock`
- Use `factory_boy` or fixtures for test data

## Dependencies
- Pin exact versions in `requirements.txt` or use `poetry.lock`
- Separate dev dependencies from production
- Use virtual environments (venv, poetry, or conda)
- Keep dependencies minimal — audit regularly

## Security
- Use `secrets` module for token generation, not `random`
- Sanitize all user input before database queries
- Use parameterized queries with ORMs
- Never `eval()` or `exec()` user input
