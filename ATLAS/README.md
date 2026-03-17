# ATLAS Autonomous Business System v2.0

## ✅ System Status: OPERATIONAL

Pure Python implementation - No n8n, No workflows, Just intelligent agents.

## Quick Start

```bash
# Start the system
./start_atlas.sh

# Test the system
python3 test_atlas.py

# Check status
curl http://localhost:8000/api/status | python3 -m json.tool
```

## Architecture

### Core Agents

1. **VAULT** - Budget Guardian ($250/mo limit)
   - Approves all spending
   - Tracks ledger in Supabase
   - Conservation mode at 80% spend

2. **SCOUT** - Opportunity Discovery
   - Reddit scraping via Apify
   - Claude Haiku filtering
   - Claude Sonnet scoring
   - Runs Mon/Wed/Fri at 5 AM

3. **FORGE** - Landing Page Builder
   - Claude Sonnet generates HTML
   - Auto-deploys to Vercel
   - Zero manual intervention

4. **MERCURY** - Distribution Engine
   - Multi-channel posting
   - Claude Haiku for copy
   - Budget-controlled

### Orchestrator

The `atlas_orchestrator.py` coordinates all agents:
- Discovery pipeline
- Experiment creation
- Daily orchestration at 7 AM
- Strategic decisions with Claude Sonnet

## API Endpoints

| Endpoint | Method | Description |
|----------|---------|------------|
| `/` | GET | System info |
| `/api/status` | GET | Current status and budget |
| `/api/discover` | POST | Trigger discovery |
| `/api/experiment/{id}` | POST | Create experiment |
| `/api/orchestrate` | POST | Run orchestration |
| `/webhook/budget-check` | POST | VAULT budget approval |

## Database

All data stored in Supabase:
- `atlas_opportunities` - Discovered opportunities
- `atlas_experiments` - Active experiments
- `atlas_budget_ledger` - Financial transactions
- `atlas_agent_logs` - Agent activity
- `atlas_briefings` - Daily briefings

## Configuration

Environment variables in `config/.env`:
```env
ANTHROPIC_API_KEY=sk-ant-...
SUPABASE_URL=https://...
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_ROLE_KEY=eyJ...
APIFY_API_TOKEN=apify_api_...
VERCEL_API_TOKEN=vcp_...
```

## Current Status

- **Budget**: $195 remaining (of $250 monthly)
- **Active Experiments**: 0
- **All Agents**: Ready
- **Database**: Connected
- **Webhooks**: Operational

## Architecture Principles

Following PRINCIPLES.md:
- ✅ No manual configuration
- ✅ Direct API calls (no n8n)
- ✅ Autonomous decision-making
- ✅ Budget-controlled operations
- ✅ Parallel agent deployment

## Files

```
ATLAS/
├── atlas_orchestrator.py    # Main coordinator
├── agents/
│   ├── vault.py             # Budget management
│   ├── scout.py             # Discovery engine
│   ├── forge.py             # Landing page builder
│   └── mercury.py           # Distribution engine
├── config/
│   └── .env                 # API credentials
├── start_atlas.sh           # Startup script
├── test_atlas.py            # System tests
└── README.md               # This file
```

## Monitoring

Check logs:
```bash
# View orchestrator logs
tail -f atlas_orchestrator.log

# Check agent activity in Supabase
curl http://localhost:8000/api/status
```

## Troubleshooting

If the system isn't working:

1. Check if running: `curl http://localhost:8000/`
2. Check logs for errors
3. Verify all API keys in `config/.env`
4. Run tests: `python3 test_atlas.py`
5. Check Supabase connection

## Budget Status

Monthly limit: $250
- Discovery: ~$2 per run
- Experiment: ~$5 per creation
- Distribution: ~$0.05 per channel

Current balance: $195 (as of last check)

---

**Built using PRINCIPLES.md** - No n8n workflows, just Python agents making intelligent decisions.
