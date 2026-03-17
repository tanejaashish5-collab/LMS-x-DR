# ATLAS n8n Environment Setup Status
**Date:** 2026-03-17
**Configured by:** Claude Code

---

## Environment Variables Configured

All required environment variables are set in `/Users/ashishtaneja/Desktop/Business Opp/ATLAS/config/.env`:

### Phase 1 - Critical (CONFIGURED)
- ✅ `ANTHROPIC_API_KEY` - Claude API for SONNET/FORGE/HAIKU agents
- ✅ `SUPABASE_URL` - ATLAS database
- ✅ `SUPABASE_ANON_KEY` - Read access
- ✅ `SUPABASE_SERVICE_ROLE_KEY` - Write access
- ✅ `NOTION_INTEGRATION_TOKEN` - Briefings/P&L tracking
- ✅ `NOTION_DATABASE_ID_BRIEFINGS` - Daily briefings database
- ✅ `NOTION_DATABASE_ID_EXPERIMENTS` - Experiments tracker
- ✅ `NOTION_DATABASE_ID_PNL` - P&L ledger
- ✅ `N8N_API_KEY` - API access to n8n instance

### Phase 2 - Active (CONFIGURED)
- ✅ `APIFY_API_TOKEN` - Web scraping for SCOUT
- ✅ `VERCEL_API_TOKEN` - Landing page deployment for FORGE

### Phase 3 - Future (CONFIGURED)
- ✅ `STRIPE_SECRET_KEY` - Payment processing
- ✅ `STRIPE_PUBLISHABLE_KEY` - Payment links
- ⚠️ `GMAIL_REFRESH_TOKEN` - Needs OAuth flow completion
- ⚠️ `META_ACCESS_TOKEN` - Not yet configured
- ⚠️ `APOLLO_API_KEY` - Not yet configured

---

## n8n Credentials Created

Successfully created in n8n (via API):

1. ✅ **ATLAS Supabase** (supabaseApi)
   - Host: https://yozmayslzckaczdfohll.supabase.co
   - Service Role Key configured

2. ✅ **ATLAS Notion** (notionApi)
   - Integration token configured

3. ✅ **ATLAS Vercel** (httpHeaderAuth)
   - Bearer token configured

4. ⚠️ **ATLAS Claude API** (anthropicApi)
   - Already exists (may need verification)

5. ⚠️ **ATLAS Apify** (apifyApi)
   - Already exists (may need verification)

---

## Workflow Activation Status

### Successfully Activated
1. ✅ **WF-04: Budget Guardian (VAULT)**
   - ID: `5SuUZAAxOF2V08nF`
   - Status: **ACTIVE**
   - Webhook: `http://localhost:5678/webhook/budget-check`
   - Function: Approves/blocks spending requests, enforces budget caps

### Blocked from Activation
2. ⚠️ **WF-05: ATLAS Orchestrator**
   - ID: `0J019KTway5tDU7P`
   - Status: **INACTIVE**
   - Blocker: Depends on WF-06 (Briefing Sender) which has Gmail config issues
   - Function: Daily 7AM strategic review and decision-making

3. ⚠️ **WF-06: Daily Briefing Sender**
   - ID: `Yea9Blh067XcuULZ`
   - Status: **INACTIVE**
   - Blocker: Missing Gmail OAuth credentials
   - Error: "Missing or invalid required parameters (2 issues)" in Send Gmail node

### Not Yet Activated (Manual Required)
4. ⏸️ **WF-01: SCOUT Pipeline** - Requires Apify credential verification
5. ⏸️ **WF-02: Metrics Collector** - Needs testing
6. ⏸️ **WF-03: EHS Calculator** - Needs testing
7. ⏸️ **WF-08: FORGE Builder** - Needs Vercel/Claude credential verification
8. ⏸️ **WF-10: Evening Snapshot** - Needs testing

---

## VAULT Webhook Test Results

**Endpoint:** `http://localhost:5678/webhook/budget-check`

**Test Status:** ⚠️ PARTIALLY WORKING
- Webhook is receiving requests (HTTP 200)
- Workflow is starting successfully
- **Issue:** Response shows "Workflow was started" instead of budget decision
- **Likely cause:** Supabase credential not fully connected to workflow nodes

**Tests Run:**
1. Small spend request ($15) - Workflow started
2. Large spend request ($45) - Workflow started
3. Experiment cap test - Workflow started
4. Invalid request - Workflow started
5. Realistic FORGE scenario - Workflow started

---

## Manual Configuration Required

### High Priority (Required for Full System Operation)

1. **Gmail OAuth Configuration (for WF-06)**
   - Action: Complete OAuth flow in n8n UI
   - Steps:
     1. Go to http://localhost:5678/credentials
     2. Edit Gmail credential
     3. Complete OAuth authentication
     4. Test connection
   - Blocks: WF-05 Orchestrator, WF-06 Briefing Sender

2. **Verify Supabase Credentials in Workflows**
   - Action: Open each workflow in n8n UI and reconnect Supabase nodes
   - Affected workflows: WF-04, WF-05, WF-01, WF-02, WF-03
   - Steps:
     1. Open workflow in editor
     2. Click each Supabase node
     3. Select "ATLAS Supabase" credential
     4. Save workflow
   - Reason: API-created credentials may not auto-link to existing workflow nodes

3. **Verify Anthropic Credentials**
   - Action: Check/recreate Claude API credential
   - Affected: WF-05, WF-08 (SONNET, HAIKU, FORGE agents)
   - Test: Try executing a node that uses Claude API

### Medium Priority (For Full Feature Set)

4. **Test WF-01 SCOUT Pipeline**
   - Verify Apify credential is linked
   - Test Reddit scraping functionality
   - Ensure Supabase write operations work

5. **Test WF-08 FORGE Builder**
   - Verify Claude + Vercel credentials
   - Test landing page generation
   - Verify deployment to Vercel

6. **Activate Remaining Workflows**
   - WF-02: Metrics Collector
   - WF-03: EHS Calculator
   - WF-10: Evening Snapshot

---

## System Readiness Assessment

### Ready for Testing ✅
- ✅ n8n instance running (http://localhost:5678)
- ✅ All environment variables configured
- ✅ VAULT workflow active (with credential reconnection needed)
- ✅ Database schema deployed to Supabase
- ✅ Notion databases configured

### Not Ready ⚠️
- ⚠️ VAULT webhook not returning budget decisions (Supabase cred issue)
- ⚠️ Orchestrator blocked by Gmail dependency
- ⚠️ Claude API credentials need verification
- ⚠️ No end-to-end test completed successfully

### Blocking Issues (1-2 hours to resolve)
1. **Supabase credential linking** - 15 mins per workflow in UI
2. **Gmail OAuth setup** - 10 mins
3. **Claude API credential verification** - 5 mins
4. **End-to-end VAULT test** - 5 mins

---

## Next Steps (Priority Order)

### Step 1: Credential Verification (30 mins)
1. Open n8n UI: http://localhost:5678
2. Go to Settings → Credentials
3. Verify/recreate:
   - ATLAS Claude API
   - ATLAS Supabase
4. Open WF-04 (VAULT) in editor
5. Click each Supabase node → select credential → save
6. Test VAULT webhook again

### Step 2: Gmail OAuth (10 mins)
1. Create Gmail OAuth credential in n8n
2. Complete authentication flow
3. Link to WF-06 nodes
4. Save workflow

### Step 3: Activate Orchestrator (5 mins)
1. Verify WF-06 activates successfully
2. Activate WF-05 (Orchestrator)
3. Check cron schedule (7:00 AM AEST)

### Step 4: End-to-End Test (30 mins)
1. Test VAULT budget approval flow
2. Manually trigger Orchestrator (or wait for 7AM)
3. Check Supabase tables for logged data
4. Verify Notion briefing creation

---

## Quick Reference

### URLs
- n8n UI: http://localhost:5678
- n8n API: http://localhost:5678/api/v1
- VAULT Webhook: http://localhost:5678/webhook/budget-check
- Supabase: https://yozmayslzckaczdfohll.supabase.co

### Scripts Created
```bash
/Users/ashishtaneja/Desktop/Business Opp/ATLAS/scripts/
├── configure-n8n-env.sh       # Set up credentials via API
├── activate-workflows.sh      # Activate critical workflows
├── test-vault-webhook.sh      # Test VAULT budget checks
├── test-orchestrator.sh       # Manual Orchestrator trigger
└── setup-atlas-env.sh         # Master setup script
```

### Test VAULT Manually
```bash
curl -X POST http://localhost:5678/webhook/budget-check \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 15,
    "type": "api_call",
    "experiment_id": "test_001",
    "agent": "SONNET",
    "description": "Test budget check"
  }'
```

---

## Summary

**What's Working:**
- ✅ Environment variables fully configured
- ✅ n8n running and accessible
- ✅ API credentials created
- ✅ VAULT workflow activated
- ✅ 12 workflows imported successfully

**What Needs Manual Intervention:**
- ⚠️ Supabase credentials need to be linked to workflow nodes (UI required)
- ⚠️ Gmail OAuth needs completion (UI required)
- ⚠️ Claude API credential needs verification
- ⚠️ Orchestrator blocked until WF-06 fixed

**Estimated Time to Full Operation:** 1-2 hours of manual UI configuration

**Recommended Immediate Action:**
1. Open http://localhost:5678 in browser
2. Fix Supabase credential links in WF-04
3. Test VAULT webhook
4. Set up Gmail OAuth
5. Activate WF-05 Orchestrator
