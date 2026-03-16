---
name: security-scan
description: OWASP-focused security vulnerability scan
arguments: optional_file_or_scope
---

# Security Scan Workflow

When the user invokes `/security-scan`, perform a thorough security review:

## Step 1: Scope
- Identify files touching auth, APIs, user input, database, payments
- If a specific file/scope is provided, focus there
- Otherwise, scan all recently changed files

## Step 2: Automated Checks
Use the Security Reviewer agent (`.claude/agents/security-reviewer.md`) to scan for:

- Hardcoded credentials and API keys
- String-concatenated SQL/NoSQL queries
- Shell commands with unsanitized user input
- Unescaped HTML output (XSS risk)
- Missing authentication on routes
- Missing rate limiting
- Unvalidated file uploads
- SSRF-vulnerable URL fetching
- Sensitive data in logs

## Step 3: OWASP Compliance
Check against the OWASP Top 10:
- A01: Broken Access Control
- A02: Cryptographic Failures
- A03: Injection
- A04: Insecure Design
- A05: Security Misconfiguration
- A06: Vulnerable Components
- A07: Auth Failures
- A08: Data Integrity
- A09: Logging Failures
- A10: SSRF

## Step 4: Report
Output with risk level, findings by severity, and remediation code.

## Rules
- CRITICAL findings = block merge
- Always provide the fix, not just the problem
- Check dependencies for known CVEs when possible
