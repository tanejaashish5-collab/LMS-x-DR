---
name: security-scan
description: Run an OWASP security scan on code
user_invocable: true
arguments: optional_scope
---

Load and execute the security scan skill from `.claude/skills/security-scan.md`.

Scan for security vulnerabilities in: $ARGUMENTS

If no scope provided, scan all recently changed files.
