# ATLAS Quick Start Guide
**5-Minute Setup Completion**

---

## Current Status
- ✅ All environment variables configured
- ✅ n8n running at http://localhost:5678
- ✅ VAULT workflow active (partially working)
- ⚠️ Manual steps needed for full operation

---

## Complete Setup in 4 Steps (1-2 hours)

### STEP 1: Fix VAULT Webhook (15 mins)
**Problem:** VAULT returns "Workflow was started" instead of budget decision

**Solution:**
1. Open http://localhost:5678
2. Click Workflows → "WF-04: Budget Guardian (VAULT)"
3. For each Supabase node (5 total), select credential "ATLAS Supabase"
4. Save workflow
5. Test:
   ```bash
   curl -X POST http://localhost:5678/webhook/budget-check \
     -H "Content-Type: application/json" \
     -d '{"amount": 15, "type": "test", "experiment_id": "test_001", "agent": "TEST", "description": "Test"}'
   ```
6. Should return: `{"status": "approved", "newBalance": 235, ...}`

---

### STEP 2: Set Up Gmail (10 mins)
**Why:** Needed for WF-06 (Briefing Sender), which blocks WF-05 (Orchestrator)

**Solution:**
1. In n8n: Settings → Credentials → Add Credential
2. Type: "Gmail OAuth2"
3. Name: "ATLAS Gmail"
4. Click "Sign in with Google"
5. Choose: taneja.ashish5@gmail.com
6. Grant permissions → Save
7. Open WF-06 workflow → "Send Gmail" node → Select "ATLAS Gmail" → Save
8. Activate WF-06 (toggle in top right)

---

### STEP 3: Activate Orchestrator (5 mins)
**Once WF-06 is active:**

1. Open WF-05 (Orchestrator)
2. Click "Active" toggle
3. Or run:
   ```bash
   curl -X POST http://localhost:5678/api/v1/workflows/0J019KTway5tDU7P/activate \
     -H "X-N8N-API-KEY: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2ZTJmOTYwNi02NTc3LTQzZDktODVlMy04NjM2YjdlM2ExNDMiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiNTYzYzE3NjEtODNlMi00NmU1LThlZGMtNjU3OTBlYWU3YjdlIiwiaWF0IjoxNzczMTEyMDMzLCJleHAiOjE4MDQ2NDgwMzMxNDh9.FWcl2H6vnpScsRSpfbO6AMorje0HVx-aONksrYj1oig"
   ```

---

### STEP 4: Test System (30 mins)

#### Test 1: VAULT Budget Check
```bash
# Should APPROVE
curl -X POST http://localhost:5678/webhook/budget-check \
  -H "Content-Type: application/json" \
  -d '{"amount": 15, "type": "api_call", "experiment_id": "test_001", "agent": "SONNET", "description": "Small test"}'

# Should BLOCK (exceeds $50 cap)
curl -X POST http://localhost:5678/webhook/budget-check \
  -H "Content-Type: application/json" \
  -d '{"amount": 60, "type": "deployment", "experiment_id": "test_001", "agent": "FORGE", "description": "Large test"}'
```

#### Test 2: Check Database Logging
1. Open https://yozmayslzckaczdfohll.supabase.co
2. Table Editor → `atlas_budget_ledger` (should have new rows)
3. Table Editor → `atlas_agent_logs` (should show VAULT actions)

#### Test 3: Verify Orchestrator Schedule
- Check Workflows → WF-05 → Executions tab
- Next run: Tomorrow 7:00 AM AEST

---

## Quick Commands

### Check All Workflows
```bash
curl -s -H "X-N8N-API-KEY: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2ZTJmOTYwNi02NTc3LTQzZDktODVlMy04NjM2YjdlM2ExNDMiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiNTYzYzE3NjEtODNlMi00NmU1LThlZGMtNjU3OTBlYWU3YjdlIiwiaWF0IjoxNzczMTEyMDMzLCJleHAiOjE4MDQ2NDgwMzMxNDh9.FWcl2H6vnpScsRSpfbO6AMorje0HVx-aONksrYj1oig" \
  http://localhost:5678/api/v1/workflows | \
  jq -r '.data[] | select(.name | startswith("WF-")) | "\(.name): \(.active)"'
```

### View Recent Executions
```bash
curl -s -H "X-N8N-API-KEY: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2ZTJmOTYwNi02NTc3LTQzZDktODVlMy04NjM2YjdlM2ExNDMiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiNTYzYzE3NjEtODNlMi00NmU1LThlZGMtNjU3OTBlYWU3YjdlIiwiaWF0IjoxNzczMTEyMDMzLCJleHAiOjE4MDQ2NDgwMzMxNDh9.FWcl2H6vnpScsRSpfbO6AMorje0HVx-aONksrYj1oig" \
  http://localhost:5678/api/v1/executions | \
  jq -r '.data[0:5] | .[] | "\(.finished ? "✓" : "✗") \(.workflowData.name) - \(.status)"'
```

---

## Success Checklist

- [ ] VAULT returns `{"status": "approved"}` (not "Workflow was started")
- [ ] Gmail OAuth configured
- [ ] WF-06 (Briefing Sender) active
- [ ] WF-05 (Orchestrator) active
- [ ] Budget approval test passes
- [ ] Budget rejection test passes
- [ ] Supabase tables show new data
- [ ] Orchestrator scheduled for 7:00 AM

---

## Key URLs

- n8n UI: http://localhost:5678
- VAULT Webhook: http://localhost:5678/webhook/budget-check
- Supabase: https://yozmayslzckaczdfohll.supabase.co

---

## Detailed Guides

- **Full Setup Status:** `docs/n8n-setup-status.md`
- **Step-by-Step Manual:** `docs/n8n-manual-activation-guide.md`
- **Complete Summary:** `ENVIRONMENT_CONFIGURATION_SUMMARY.md`

---

## What's Working Now

✅ n8n running
✅ All 12 workflows imported
✅ All environment variables set
✅ VAULT workflow active (receiving webhooks)
✅ Database schema deployed
✅ Test scripts ready

---

## What Needs 1-2 Hours

⚠️ Supabase credential linking (UI required)
⚠️ Gmail OAuth setup (UI required)
⚠️ Orchestrator activation (blocked by Gmail)
⚠️ End-to-end testing

---

**Start here:** http://localhost:5678
**First task:** Link Supabase credentials to WF-04 nodes
**Time:** 15 minutes
**Result:** VAULT fully operational
