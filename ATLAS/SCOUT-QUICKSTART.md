# SCOUT Agent - Quick Start

## Test It Now
```bash
cd /Users/ashishtaneja/Desktop/Business\ Opp/ATLAS
python3 test-scout.py
```

## Use in Code
```python
from agents import SCOUTAgent

scout = SCOUTAgent()

# Run discovery
result = scout.run_discovery()
print(f"Found {result['scored']} opportunities")

# Get stats
stats = scout.get_discovery_stats()
print(f"Top score: {stats['top_opportunities'][0]['sonnet_score']}/100")
```

## What It Does

1. **Scans Reddit** for business automation pain points
2. **Filters with Haiku** (cheap, fast) - PASS/FAIL
3. **Saves to database** (atlas_opportunities)
4. **Scores with Sonnet** (or Haiku) - 0-100 rating
5. **Logs everything** (atlas_agent_logs)

## Cost
- ~$2 per run
- 3 runs/week = $24/month

## Schedule
Mon/Wed/Fri at 5 AM

## Files
- Agent: `agents/scout.py`
- Test: `test-scout.py`
- Docs: `agents/README.md`

## Integration
```python
from agents import SCOUTAgent, VAULTAgent, BudgetRequest

scout = SCOUTAgent()
vault = VAULTAgent()

# Check budget
request = BudgetRequest(amount=2.00, agent='scout', description='Discovery run')
if vault.check_budget(request)['approved']:
    result = scout.run_discovery()
```

## Status
Production ready. Tested and working.

Database connected: yozmayslzckaczdfohll.supabase.co
API working: Claude Haiku (filtering + scoring fallback)
