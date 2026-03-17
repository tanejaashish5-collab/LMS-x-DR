# Complete ATLAS Workflow Configuration Guide

## ⚠️ CRITICAL: All Supabase Node Configurations

You should NOT have to guess these values. Here's the exact configuration for every Supabase node across all 12 workflows.

---

## WF-01: SCOUT Pipeline

### Node: "Insert to Supabase"
**Operation**: Create
**Table**: `atlas_opportunities`
**Columns to Send**:
```
title → {{ $json.title }}
source → {{ $json.source }}
source_url → {{ $json.source_url }}
description → {{ $json.description }}
category → other
target_vertical → {{ $json.vertical }}
haiku_filter_pass → true
status → discovered
discovered_at → {{ $now.toISO() }}
```

### Node: "Get Top 5 for Scoring"
**Operation**: Get Many
**Table**: `atlas_opportunities`
**Filters**:
- haiku_filter_pass = true
- sonnet_score IS NULL
- status = discovered
**Sort**: discovered_at (Descending)
**Limit**: 5

### Node: "Update with Score"
**Operation**: Update
**Table**: `atlas_opportunities`
**Filter**: id = {{ $json.id }}
**Update Fields**:
```
sonnet_score → {{ $json.score }}
claude_analysis → {{ $json.analysis }}
scored_at → {{ $now.toISO() }}
status → scored
```

### Node: "Log SCOUT Run"
**Operation**: Create
**Table**: `atlas_agent_logs`
**Columns**:
```
agent_name → SCOUT
action_type → discovery_run
details → Found {{ $json.count }} opportunities
created_at → {{ $now.toISO() }}
```

---

## WF-02: Metrics Collector

### Node: "Get Active Experiments"
**Operation**: Get Many
**Table**: `atlas_experiments`
**Filters**:
- status IN ('active', 'measuring')
**Sort**: started_at (Descending)

### Node: "Upsert Metrics"
**Operation**: Upsert
**Table**: `atlas_experiments`
**Identifier**: experiment_id
**Columns**:
```
experiment_id → {{ $json.experiment_id }}
budget_spent → {{ $json.budget_spent }}
total_revenue → {{ $json.total_revenue }}
updated_at → {{ $now.toISO() }}
```

---

## WF-03: EHS Calculator

### Node: "Get Active Experiments"
**Operation**: Get Many
**Table**: `atlas_experiments`
**Filters**:
- status = active

### Node: "Get Last 7 Days Metrics"
**Operation**: Get Many
**Table**: `atlas_experiments`
**Filters**:
- experiment_id = {{ $json.experiment_id }}
- created_at >= {{ $today.minus(7, 'days').toISO() }}

### Node: "Update EHS"
**Operation**: Update
**Table**: `atlas_experiments`
**Filter**: experiment_id = {{ $json.experiment_id }}
**Update Fields**:
```
ehs_score → {{ $json.ehs_score }}
updated_at → {{ $now.toISO() }}
```

### Node: "Kill Experiment"
**Operation**: Update
**Table**: `atlas_experiments`
**Filter**: experiment_id = {{ $json.experiment_id }}
**Update Fields**:
```
status → killed
kill_reason → {{ $json.kill_reason }}
ended_at → {{ $now.toISO() }}
```

### Node: "Flag for ATLAS Review"
**Operation**: Create
**Table**: `atlas_agent_logs`
**Columns**:
```
agent_name → ARGUS
action_type → flag_for_review
details → Experiment {{ $json.experiment_id }} flagged: {{ $json.reason }}
experiment_id → {{ $json.experiment_id }}
created_at → {{ $now.toISO() }}
```

---

## WF-04: Budget Guardian (VAULT) - YOUR MANUAL FIXES

### Node: "Get Current Budget Status"
**Operation**: Get
**Table**: `atlas_budget_summary`
**Filter**: month_key = {{ $now.format('yyyy-MM') }}

### Node: "Check Experiment Spend"
**Operation**: Get
**Table**: `atlas_experiments`
**Filter**: experiment_id = {{ $json.experiment_id }}
**Select**: budget_spent

### Node: "Log Spend to Ledger" ✅ (Your fix)
**Operation**: Create
**Table**: `atlas_budget_ledger`
**Columns**:
```
transaction_type → spend
amount → {{ $json.requestedAmount }}
experiment_id → {{ $json.experimentId }}
agent → {{ $json.agent }}
description → {{ $json.description }}
balance_after → {{ $json.newBalance }}
created_at → {{ $now.toISO() }}
```

### Node: "Update Experiment Spend" ✅ (Your fix)
**Operation**: Update
**Table**: `atlas_experiments`
**Filter**: experiment_id = {{ $json.experimentId }}
**Update Fields**:
```
budget_spent → {{ $json.experimentSpent + $json.requestedAmount }}
updated_at → {{ $now.toISO() }}
```

### Node: "Log Block to Agent Logs" ✅ (Your fix)
**Operation**: Create
**Table**: `atlas_agent_logs`
**Columns**:
```
agent_name → VAULT
action_type → budget_block
details → Blocked: {{ $json.blockReason }}
experiment_id → {{ $json.experimentId }}
created_at → {{ $now.toISO() }}
```

---

## WF-05: ATLAS Orchestrator

### Node: "Get All Experiments"
**Operation**: Get Many
**Table**: `atlas_experiments`
**Sort**: started_at (Descending)

### Node: "Get Budget Status"
**Operation**: Get
**Table**: `atlas_budget_summary`
**Filter**: month_key = {{ $now.format('yyyy-MM') }}

### Node: "Get New Opportunities"
**Operation**: Get Many
**Table**: `atlas_opportunities`
**Filters**:
- status = discovered
- haiku_filter_pass = true
**Sort**: discovered_at (Descending)
**Limit**: 10

### Node: "Get Recent Agent Logs"
**Operation**: Get Many
**Table**: `atlas_agent_logs`
**Filter**: created_at >= {{ $now.minus(24, 'hours').toISO() }}
**Sort**: created_at (Descending)
**Limit**: 20

### Node: "Get Yesterday Metrics"
**Operation**: Get Many
**Table**: `atlas_experiments`
**Filter**: DATE(created_at) = {{ $today.minus(1, 'day').format('yyyy-MM-dd') }}

### Node: "Save Briefing"
**Operation**: Create
**Table**: `atlas_briefings`
**Columns**:
```
briefing_type → daily
content → {{ $json.briefing_content }}
decisions → {{ $json.decisions }}
status → draft
created_at → {{ $now.toISO() }}
```

### Node: "Approve Opportunity"
**Operation**: Update
**Table**: `atlas_opportunities`
**Filter**: id = {{ $json.opportunity_id }}
**Update Fields**:
```
status → approved
approved_at → {{ $now.toISO() }}
```

---

## WF-06: Daily Briefing Sender

### Node: "Get Briefing from Supabase"
**Operation**: Get Many
**Table**: `atlas_briefings`
**Filters**:
- status = draft
- DATE(created_at) = {{ $today.format('yyyy-MM-dd') }}
**Sort**: created_at (Descending)
**Limit**: 1

### Node: "Log to Agent Logs"
**Operation**: Create
**Table**: `atlas_agent_logs`
**Columns**:
```
agent_name → ATLAS
action_type → briefing_sent
details → Daily briefing sent to Ashish
created_at → {{ $now.toISO() }}
```

### Node: "Mark Briefing as Sent"
**Operation**: Update
**Table**: `atlas_briefings`
**Filter**: id = {{ $json.id }}
**Update Fields**:
```
status → sent
sent_at → {{ $now.toISO() }}
```

---

## WF-07: Veto Checker

### Node: "Mark Briefing as VETOED"
**Operation**: Update
**Table**: `atlas_briefings`
**Filter**:
- DATE(created_at) = {{ $today.format('yyyy-MM-dd') }}
- status = sent
**Update Fields**:
```
status → vetoed
vetoed_at → {{ $now.toISO() }}
```

### Node: "Mark Briefing as APPROVED"
**Operation**: Update
**Table**: `atlas_briefings`
**Filter**:
- DATE(created_at) = {{ $today.format('yyyy-MM-dd') }}
- status = sent
**Update Fields**:
```
status → approved
approved_at → {{ $now.toISO() }}
```

### Node: "Get Today's Decisions"
**Operation**: Get Many
**Table**: `atlas_briefings`
**Filter**: DATE(created_at) = {{ $today.format('yyyy-MM-dd') }}
**Select**: decisions

### Node: "Log to Database"
**Operation**: Create
**Table**: `atlas_agent_logs`
**Columns**:
```
agent_name → ATLAS
action_type → {{ $json.veto ? 'decisions_vetoed' : 'decisions_approved' }}
details → {{ $json.details }}
created_at → {{ $now.toISO() }}
```

---

## WF-08: Forge Builder (FORGE)

### Node: "Create Experiment Record"
**Operation**: Create
**Table**: `atlas_experiments`
**Columns**:
```
experiment_id → {{ $json.experiment_id }}
opportunity_id → {{ $json.opportunity_id }}
name → {{ $json.name }}
vertical → {{ $json.vertical }}
status → building
budget_allocated → 50
started_at → {{ $now.toISO() }}
```

### Node: "Update Experiment - LIVE"
**Operation**: Update
**Table**: `atlas_experiments`
**Filter**: experiment_id = {{ $json.experiment_id }}
**Update Fields**:
```
status → active
landing_page_url → {{ $json.landing_page_url }}
updated_at → {{ $now.toISO() }}
```

### Node: "Update Experiment - FAILED"
**Operation**: Update
**Table**: `atlas_experiments`
**Filter**: experiment_id = {{ $json.experiment_id }}
**Update Fields**:
```
status → failed
kill_reason → Build failed: {{ $json.error }}
ended_at → {{ $now.toISO() }}
```

### Node: "Log FORGE Activity"
**Operation**: Create
**Table**: `atlas_agent_logs`
**Columns**:
```
agent_name → FORGE
action_type → {{ $json.action }}
details → {{ $json.details }}
experiment_id → {{ $json.experiment_id }}
created_at → {{ $now.toISO() }}
```

---

## WF-09: Mercury Distribution (MERCURY)

### Node: "Update Experiment - MEASURING"
**Operation**: Update
**Table**: `atlas_experiments`
**Filter**: experiment_id = {{ $json.experiment_id }}
**Update Fields**:
```
status → measuring
updated_at → {{ $now.toISO() }}
```

### Node: "Log MERCURY Activity"
**Operation**: Create
**Table**: `atlas_agent_logs`
**Columns**:
```
agent_name → MERCURY
action_type → distribution_started
details → Launched: {{ $json.channels }}
experiment_id → {{ $json.experiment_id }}
created_at → {{ $now.toISO() }}
```

### Node: "Log Rejection"
**Operation**: Create
**Table**: `atlas_agent_logs`
**Columns**:
```
agent_name → MERCURY
action_type → distribution_rejected
details → Budget rejected by VAULT
experiment_id → {{ $json.experiment_id }}
created_at → {{ $now.toISO() }}
```

---

## WF-10: Evening Snapshot
*No Supabase nodes - uses other integrations*

---

## WF-11: Weekly P&L Report
*No Supabase nodes - uses other integrations*

---

## WF-12: Experiment Killer

### Node: "Get Experiment Details"
**Operation**: Get
**Table**: `atlas_experiments`
**Filter**: experiment_id = {{ $json.experiment_id }}

### Node: "Update Experiment Status - KILLED"
**Operation**: Update
**Table**: `atlas_experiments`
**Filter**: experiment_id = {{ $json.experiment_id }}
**Update Fields**:
```
status → killed
kill_reason → {{ $json.kill_reason }}
ended_at → {{ $now.toISO() }}
```

### Node: "Log Kill Activity"
**Operation**: Create
**Table**: `atlas_agent_logs`
**Columns**:
```
agent_name → ATLAS
action_type → experiment_killed
details → Killed: {{ $json.kill_reason }}
experiment_id → {{ $json.experiment_id }}
created_at → {{ $now.toISO() }}
```

---

## Common Issues & Solutions

### Issue: "Cannot read properties of undefined"
**Solution**: Use optional chaining: `{{ $json?.experiment_id || '' }}`

### Issue: "Invalid date format"
**Solution**: Use n8n date functions:
- Current time: `{{ $now.toISO() }}`
- Today: `{{ $today.format('yyyy-MM-dd') }}`
- 7 days ago: `{{ $today.minus(7, 'days').toISO() }}`

### Issue: "Column does not exist"
**Solution**: Check exact column names in Supabase:
- Use `experiment_id` not `experimentId`
- Use `budget_spent` not `budgetSpent`
- Use snake_case not camelCase

### Issue: "Webhook not receiving data"
**Solution**: Check webhook body access:
- Correct: `{{ $json.experiment_id }}`
- Wrong: `{{ $node["Webhook Trigger"].json.body.experiment_id }}`

---

## Testing Commands

### Test VAULT (should deduct $10 from budget):
```bash
curl -X POST http://localhost:5678/webhook/budget-check \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 10,
    "experiment_id": "test-001",
    "agent": "SONNET",
    "description": "Test transaction"
  }'
```

### Check if it worked:
```bash
cd /Users/ashishtaneja/Desktop/Business\ Opp/ATLAS
python3 check-supabase-status.py
```

Expected: Balance should be $240, Transactions should be 1

---

## IMPORTANT NOTES

1. **All column names must be snake_case** (not camelCase)
2. **All date fields use ISO format**: `{{ $now.toISO() }}`
3. **Filters use exact column names from database**
4. **For UPDATE operations, always include updated_at field**
5. **For CREATE operations, always include created_at field**

This guide contains EVERY Supabase node configuration across all 12 workflows. You should not need to guess any values!