# Security Deny Rules
# Inspired by Trail of Bits' security-first Claude Code configuration

## File Access Deny Rules (NEVER read or write these)

### Credentials & Secrets
- `**/.env` — Environment variables with secrets
- `**/.env.*` — Environment variant files
- `**/credentials.json` — Service credentials
- `**/service-account*.json` — GCP service accounts
- `**/*.pem` — Private keys
- `**/*.key` — Private keys
- `**/*.p12` — PKCS12 keystores
- `**/*.pfx` — PKCS12 keystores
- `**/.npmrc` — NPM auth tokens
- `**/.pypirc` — PyPI auth tokens
- `**/token.json` — OAuth tokens
- `**/*secret*` — Any file with "secret" in the name
- `**/.aws/credentials` — AWS credentials
- `**/.ssh/*` — SSH keys
- `**/.gnupg/*` — GPG keys

### Configuration That May Contain Secrets
- `**/docker-compose*.yml` — May contain DB passwords
- `**/Dockerfile` — May contain build secrets
- `**/.github/workflows/*.yml` — May contain secret refs

## Command Deny Rules (NEVER execute these)

### Destructive Operations
- `rm -rf /` — System destruction
- `rm -rf ~` — Home directory destruction
- `rm -rf .git` — Repository destruction
- `git push --force` to main/master — Force push to primary branches
- `git reset --hard` — Without explicit user confirmation
- `DROP DATABASE` — Database destruction
- `DROP TABLE` — Table destruction
- `TRUNCATE` — Data destruction

### Exfiltration Prevention
- `curl` with POST containing file contents to unknown URLs
- `wget` uploading files to unknown URLs
- Piping secrets/env vars to external services
- `nc` (netcat) to external hosts
- Base64 encoding + sending credentials

### Privilege Escalation
- `sudo` — Unless explicitly requested
- `chmod 777` — World-writable permissions
- `chown root` — Changing file ownership to root

## Sandbox Rules

### Read-Only Paths (never modify)
- `/etc/` — System configuration
- `/usr/` — System binaries
- `/var/log/` — System logs
- `~/.bashrc`, `~/.zshrc` — Shell config (unless asked)
- `~/.gitconfig` — Git config (unless asked)

### Network Rules
- No outbound connections to unknown hosts with credentials
- No downloading executables from untrusted sources
- No installing packages from non-standard registries
