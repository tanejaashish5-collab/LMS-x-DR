# FORGE Agent - Quick Start

Build landing pages in 3 steps.

## Prerequisites

1. Database columns added:
```bash
# Run in Supabase SQL Editor
cat add-landing-page-columns.sql
```

2. Python packages installed:
```bash
pip install supabase anthropic requests
```

## Usage

### 1. Test Agent (No Cost)

```bash
cd /Users/ashishtaneja/Desktop/Business\ Opp/ATLAS
python3 test-forge.py
```

Shows stats and usage pattern. No API calls.

### 2. Build a Landing Page

```python
from agents.forge import FORGEAgent, LandingPageRequest
from agents.vault import VAULTAgent

# Initialize
vault = VAULTAgent()
forge = FORGEAgent(vault_agent=vault)

# Create request
request = LandingPageRequest(
    experiment_id="exp-001",
    opportunity_title="Automated Invoice Processing",
    target_vertical="Legal Services",
    value_proposition="Save 10+ hours/week",
    cta_text="Book Demo",
    cta_action="https://calendly.com/ashishtaneja"
)

# Build and deploy (~$2.00)
result = forge.build_landing_page(request)

if result.status == "deployed":
    print(f"Live: {result.vercel_url}")
```

### 3. Check Stats

```python
stats = forge.get_build_stats()
print(f"Builds: {stats['total_builds']}")
print(f"Cost: ${stats['total_cost']:.2f}")
```

## That's It

FORGE is ready. Next: Integrate with ATLAS orchestrator.

See `FORGE-AGENT-COMPLETE.md` for full documentation.
