# 🚀 ATLAS Quick Start Guide

## You Have 30 Minutes? Let's Launch ATLAS!

### Minute 0-5: Credentials Check

Open `config/.env.template` and check you have:
- [ ] Anthropic API key (Claude)
- [ ] Supabase service_role key
- [ ] Gmail OAuth credentials
- [ ] Notion integration token

```bash
cp config/.env.template config/.env
nano config/.env  # Add your keys
```

### Minute 5-10: Notion Setup

1. Go to Notion.so
2. Create new page: "ATLAS Dashboard"
3. Add 4 databases (use /database):
   - Daily Briefings
   - Active Experiments
   - Weekly P&L Reports
   - Opportunity Pipeline

See `docs/notion-setup.md` for exact properties.

### Minute 10-15: Deploy Core Workflows

```bash
# Make sure n8n is running
open http://localhost:5678

# Import these workflows (drag & drop JSON files):
1. workflows/WF-04-Budget-Guardian-VAULT.json  # MUST BE FIRST
2. workflows/WF-06-Daily-Briefing-Sender.json
3. workflows/WF-01-SCOUT-Pipeline.json
```

### Minute 15-20: Test Budget Guardian

In n8n:
1. Open WF-04 Budget Guardian
2. Click "Execute Workflow"
3. Open webhook URL in new tab
4. Send test request:

```bash
curl -X POST http://localhost:5678/webhook/vault-budget-guardian \
  -H "Content-Type: application/json" \
  -d '{"agent":"TEST","amount":10,"experiment_id":"test-1","description":"Test"}'
```

Should return: `{"status":"approved","newBalance":240}`

### Minute 20-25: Configure ForgeVoice Website

The blueprint says to fix these issues on forgevoice.studio:
1. Remove "0 workflows audited" metrics
2. Add 3 service cards for target verticals
3. Create blog section

Quick fix for now:
- Hide the metrics section entirely
- Add "Currently accepting 3 projects" banner

### Minute 25-30: Final Checklist

Before activating ATLAS:

- [ ] Budget Guardian webhook works
- [ ] Notion databases created
- [ ] Daily Briefing workflow imported
- [ ] Your email in Gmail node: taneja.ashish5@gmail.com
- [ ] $250 deposited in Supabase (already done!)

## Activation Sequence

**⚠️ WARNING: Once activated, ATLAS will start spending money!**

### Safe Test Mode First:

1. Keep all workflows INACTIVE
2. Manually execute WF-01 SCOUT once
3. Check Supabase for opportunities
4. Manually execute WF-06 Daily Briefing
5. Check your email

### Full Activation:

1. In n8n, activate workflows in this order:
   - WF-04 Budget Guardian (always on)
   - WF-06 Daily Briefing
   - WF-01 SCOUT Pipeline
   - WF-03 EHS Calculator
   - WF-05 ATLAS Orchestrator

2. Set your veto window:
   - Briefings arrive at 7:30 AM
   - You have until 9:30 AM to VETO
   - Reply "VETO" to stop any action

## What Happens Next?

### Day 1-3:
- SCOUT finds opportunities
- No money spent yet
- Daily briefings start arriving

### Day 3-7:
- ATLAS approves first experiments
- FORGE builds landing pages
- MERCURY starts $5/day ads

### Day 7-14:
- First metrics come in
- Kill/scale decisions made
- Winners get more budget

### Month 1 Target:
- 10-15 experiments launched
- 2-3 winners identified
- First client inquiry

## Emergency Stop

To halt everything immediately:

```bash
# 1. Deactivate all workflows in n8n
# 2. Set all experiments to 'killed' in Supabase:

UPDATE atlas_experiments
SET status = 'killed', killed_at = NOW()
WHERE status IN ('live', 'measuring', 'scaled');

# 3. Pause all Meta ads manually
```

## Support Contacts

- **Technical**: Your n8n instance logs
- **Budget**: Check atlas_budget_summary view
- **Experiments**: Check atlas_experiment_dashboard view
- **Daily Status**: 7:30 AM email + Notion

## The Golden Rules

1. **Budget Guardian must work** - Test it 3 times
2. **Veto window is sacred** - Check email 7:30-9:30 AM
3. **$50 max per experiment** - Hard coded limit
4. **EHS < 20 = auto-kill** - Let it work
5. **First revenue = double budget** - Automatic scaling

---

Ready? Start with Safe Test Mode. Once comfortable, activate SCOUT for real opportunities.

Remember: **This system is designed to fail fast and scale winners.**

Good luck! 🎯