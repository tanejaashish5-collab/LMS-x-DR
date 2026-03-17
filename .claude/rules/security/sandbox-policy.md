# Sandbox Enforcement Policy

## Principle: Defense in Depth

Every action should be constrained to the minimum necessary permissions.

## File System Boundaries

### Allowed (read + write)
- Project directory and subdirectories
- `/tmp/` for temporary files (clean up after use)
- Test output directories

### Allowed (read only)
- Node modules (`node_modules/`)
- System package documentation
- Installed binary help text

### Denied (never access)
- Home directory dotfiles (unless project-related)
- System directories (`/etc`, `/usr`, `/var`)
- Other project directories
- SSH keys, GPG keys, AWS credentials

## Process Boundaries

### Allowed
- Language runtimes (node, python, go, etc.)
- Package managers (npm, pip, cargo, etc.)
- Build tools (webpack, vite, tsc, etc.)
- Test runners (jest, pytest, go test, etc.)
- Git operations (within project scope)
- Linters and formatters

### Restricted (ask user first)
- Docker operations (may affect system state)
- Database migrations (may affect shared state)
- Cloud CLI tools (may incur costs)
- Process management (pm2, systemd)

### Denied
- System administration commands
- Network scanning tools
- Package publishing (npm publish, etc.)
- Production deployments (without explicit approval)

## Network Boundaries

### Allowed
- Package registry fetches (npm, pypi, crates.io)
- Git remote operations (project repo only)
- localhost connections (dev servers, test databases)
- Documentation fetches (official docs sites)

### Denied
- Arbitrary outbound connections with project data
- Webhook registration to external services
- DNS changes or network configuration
- Downloading and executing remote scripts
