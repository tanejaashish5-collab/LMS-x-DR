# ATLAS Supabase Database Setup - COMPLETE

**Date:** 2026-03-17
**Status:** ✅ FULLY INITIALIZED AND READY

---

## Connection Details

- **Supabase URL:** https://yozmayslzckaczdfohll.supabase.co
- **Project ID:** yozmayslzckaczdfohll
- **Environment:** Production
- **Connection Status:** ✅ VERIFIED

---

## Database Status

### Tables Found (5/5)

| Table | Rows | Status | Purpose |
|-------|------|--------|---------|
| `atlas_budget_summary` | 1 | ✅ ACTIVE | Track monthly budget, spend, revenue |
| `atlas_opportunities` | 1 | ✅ ACTIVE | Store discovered opportunities |
| `atlas_experiments` | 0 | ✅ READY | Track validation experiments |
| `atlas_briefings` | 0 | ✅ READY | Store daily briefings for Ashish |
| `atlas_agent_logs` | 0 | ✅ READY | Log all agent activities |

---

## Budget Initialization

**✅ BUDGET ACTIVE**

```
Month: 2026-03
Total Deposited: $250.00
Total Spent: $0.00
Total Revenue: $0.00
Current Balance: $250.00
Transactions: 0
```

The system is funded and ready to run experiments.

---

## Test Opportunity Created

**✅ TRIGGER OPPORTUNITY INSERTED**

```json
{
  "id": "0cf1edc6-053c-49a0-a480-c90ded22dc0c",
  "title": "Need AI automation for lead generation - $500 budget",
  "source": "reddit",
  "description": "Small business owner looking for AI workflow automation. Budget: $500. Timeline: 2 weeks. Stack: n8n preferred.",
  "category": "other",
  "target_vertical": "small_business",
  "status": "discovered"
}
```

This opportunity should trigger the ATLAS orchestrator workflow when it runs.

---

## Table Schemas Discovered

### atlas_budget_summary
- `month_key` (string) - Format: "YYYY-MM"
- `total_deposited` (decimal)
- `total_spent` (integer)
- `total_revenue` (integer)
- `current_balance` (decimal)
- `transaction_count` (integer)

### atlas_opportunities
- `id` (uuid)
- `title` (string)
- `source` (string) - e.g., "reddit", "manual_test"
- `source_url` (string, nullable)
- `description` (string)
- `category` (enum) - Known values: "other"
- `target_vertical` (string, nullable)
- `haiku_filter_pass` (boolean)
- `sonnet_score` (nullable)
- `competition_level` (nullable)
- `buildability` (nullable)
- `estimated_market` (nullable)
- `claude_analysis` (json object)
- `status` (enum) - "discovered", etc.
- `discovered_at` (timestamp)
- `scored_at` (timestamp, nullable)
- `created_at` (timestamp)

---

## Scripts Created

### 1. initialize-supabase.py
**Location:** `/Users/ashishtaneja/Desktop/Business Opp/ATLAS/initialize-supabase.py`

**Purpose:** Full database initialization and verification
- Tests connection
- Checks all tables
- Initializes budget if needed
- Creates test opportunity
- Verifies data accessibility

**Usage:**
```bash
cd "/Users/ashishtaneja/Desktop/Business Opp/ATLAS"
python3 initialize-supabase.py
```

### 2. check-supabase-status.py
**Location:** `/Users/ashishtaneja/Desktop/Business Opp/ATLAS/check-supabase-status.py`

**Purpose:** Quick status check anytime
- Budget overview
- Opportunity count and list
- Experiment summary
- Recent briefings
- Agent activity logs

**Usage:**
```bash
cd "/Users/ashishtaneja/Desktop/Business Opp/ATLAS"
python3 check-supabase-status.py
```

---

## Next Steps

### Immediate (Next 5 minutes)
1. **Start n8n** (if not already running):
   ```bash
   n8n start
   ```

2. **Open n8n dashboard**: http://localhost:5678

3. **Activate WF-05-ATLAS-Orchestrator workflow**:
   - Find workflow in n8n
   - Click "Active" toggle
   - Verify webhook is listening

### Testing (Next 15 minutes)
1. **Monitor for automatic trigger**:
   - The test opportunity should trigger the orchestrator
   - Check agent logs: `python3 check-supabase-status.py`

2. **Manual trigger** (if needed):
   - Click "Execute Workflow" in n8n
   - Watch the execution flow

3. **Verify data flow**:
   - Check if opportunity status changed from "discovered"
   - Look for new agent_logs entries
   - Check for Claude analysis in opportunity record

### Validation (Next hour)
1. **Wait for briefing generation**:
   - Should happen automatically
   - Check `atlas_briefings` table

2. **Add real opportunity**:
   - Insert actual Reddit/forum opportunity
   - Watch ATLAS process it

3. **Monitor budget tracking**:
   - Any API calls should update budget
   - Verify spend tracking works

---

## Troubleshooting

### If workflows don't trigger:
```bash
# Check n8n is running
curl http://localhost:5678

# Check workflow is active
# In n8n UI, verify WF-05-ATLAS-Orchestrator shows "Active"

# Manually trigger via n8n UI
# Or re-run initialize script to create fresh opportunity
```

### If data isn't updating:
```bash
# Run status check
python3 check-supabase-status.py

# Check credentials in n8n
# Verify Supabase nodes have correct URL and API key

# Check agent logs for errors
# Look in atlas_agent_logs table
```

### If budget tracking fails:
```bash
# Verify budget record exists
python3 -c "from supabase import create_client; \
  supabase = create_client('https://yozmayslzckaczdfohll.supabase.co', 'YOUR_KEY'); \
  print(supabase.table('atlas_budget_summary').select('*').execute().data)"
```

---

## Success Criteria

✅ **Database connected and accessible**
✅ **All 5 tables present and verified**
✅ **Budget initialized with $250**
✅ **Test opportunity created**
✅ **Data read/write working**
⏳ **Waiting for first workflow execution**
⏳ **Waiting for first briefing**
⏳ **Waiting for first experiment**

---

## Dependencies Installed

- `supabase-py` - Python client for Supabase

---

## Files in This Directory

```
/Users/ashishtaneja/Desktop/Business Opp/ATLAS/
├── initialize-supabase.py           # Full setup script
├── check-supabase-status.py         # Quick status checker
├── SUPABASE-SETUP-COMPLETE.md       # This file
├── config/.env                      # Environment variables
└── workflows/
    ├── WF-05-ATLAS-Orchestrator.json
    └── WF-05-ATLAS-Orchestrator-FIXED.json
```

---

## Support

If issues arise:
1. Run `python3 check-supabase-status.py` to see current state
2. Check n8n workflow execution logs
3. Verify credentials in `config/.env`
4. Check Supabase dashboard for table activity

---

**Setup completed by:** Claude (Supabase Database Specialist)
**Completion time:** 2026-03-17 10:33 UTC
**Status:** READY FOR PRODUCTION
