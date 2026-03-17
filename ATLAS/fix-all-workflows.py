#!/usr/bin/env python3
"""
ATLAS Workflow Fixer - Automatically configures all Supabase nodes
No manual configuration needed!
"""

import json
import os
from pathlib import Path
import shutil

# Configuration
WORKFLOWS_DIR = Path('/Users/ashishtaneja/Desktop/Business Opp/ATLAS/workflows')
FIXED_DIR = Path('/Users/ashishtaneja/Desktop/Business Opp/ATLAS/workflows-fixed')

# Known Supabase credential ID from n8n
SUPABASE_CRED_ID = 'w05bozuBPL3v3rAc'

# Table configurations
TABLE_CONFIGS = {
    'atlas_opportunities': {
        'columns': ['id', 'title', 'source', 'source_url', 'description', 'category',
                   'target_vertical', 'haiku_filter_pass', 'sonnet_score', 'status',
                   'discovered_at', 'scored_at', 'created_at', 'claude_analysis'],
        'id_field': 'id'
    },
    'atlas_experiments': {
        'columns': ['id', 'experiment_id', 'opportunity_id', 'name', 'vertical',
                   'status', 'landing_page_url', 'budget_allocated', 'budget_spent',
                   'total_revenue', 'ehs_score', 'kill_reason', 'started_at',
                   'ended_at', 'created_at'],
        'id_field': 'experiment_id'
    },
    'atlas_budget_summary': {
        'columns': ['month_key', 'total_deposited', 'total_spent', 'total_revenue',
                   'current_balance', 'transaction_count'],
        'id_field': 'month_key'
    },
    'atlas_budget_ledger': {
        'columns': ['id', 'transaction_type', 'amount', 'experiment_id', 'agent',
                   'description', 'balance_after', 'created_at'],
        'id_field': 'id'
    },
    'atlas_agent_logs': {
        'columns': ['id', 'agent_name', 'action_type', 'details', 'experiment_id',
                   'created_at'],
        'id_field': 'id'
    },
    'atlas_briefings': {
        'columns': ['id', 'briefing_type', 'content', 'decisions', 'status',
                   'sent_at', 'created_at'],
        'id_field': 'id'
    }
}

# SQL queries for different operations
SQL_QUERIES = {
    'WF-01_top_opportunities': """
SELECT * FROM atlas_opportunities
WHERE haiku_filter_pass = true
  AND sonnet_score IS NULL
  AND status = 'discovered'
ORDER BY discovered_at DESC
LIMIT 5
""",
    'WF-02_active_experiments': """
SELECT * FROM atlas_experiments
WHERE status IN ('active', 'measuring')
ORDER BY started_at DESC
""",
    'WF-02_upsert_metrics': """
INSERT INTO atlas_experiments (experiment_id, budget_spent, total_revenue)
VALUES ('{{ $json.experiment_id }}', {{ $json.budget_spent }}, {{ $json.total_revenue }})
ON CONFLICT (experiment_id)
DO UPDATE SET
  budget_spent = EXCLUDED.budget_spent,
  total_revenue = EXCLUDED.total_revenue
""",
    'WF-03_active_experiments': """
SELECT * FROM atlas_experiments
WHERE status = 'active'
""",
    'WF-03_metrics_7days': """
SELECT experiment_id,
       SUM(budget_spent) as total_spend,
       SUM(total_revenue) as total_revenue,
       COUNT(*) as data_points
FROM atlas_experiments
WHERE created_at >= NOW() - INTERVAL '7 days'
  AND experiment_id = '{{ $json.experiment_id }}'
GROUP BY experiment_id
""",
    'WF-04_budget_status': """
SELECT * FROM atlas_budget_summary
WHERE month_key = TO_CHAR(NOW(), 'YYYY-MM')
""",
    'WF-04_experiment_spend': """
SELECT COALESCE(SUM(budget_spent), 0) as total_spent
FROM atlas_experiments
WHERE experiment_id = '{{ $json.experiment_id }}'
""",
    'WF-05_all_experiments': """
SELECT * FROM atlas_experiments
ORDER BY started_at DESC
""",
    'WF-05_budget_status': """
SELECT * FROM atlas_budget_summary
WHERE month_key = TO_CHAR(NOW(), 'YYYY-MM')
""",
    'WF-05_new_opportunities': """
SELECT * FROM atlas_opportunities
WHERE status = 'discovered'
  AND haiku_filter_pass = true
ORDER BY discovered_at DESC
LIMIT 10
""",
    'WF-05_recent_logs': """
SELECT * FROM atlas_agent_logs
WHERE created_at >= NOW() - INTERVAL '24 hours'
ORDER BY created_at DESC
LIMIT 20
""",
    'WF-05_yesterday_metrics': """
SELECT experiment_id,
       SUM(budget_spent) as daily_spend,
       SUM(total_revenue) as daily_revenue
FROM atlas_experiments
WHERE DATE(created_at) = CURRENT_DATE - INTERVAL '1 day'
GROUP BY experiment_id
""",
    'WF-07_mark_vetoed': """
UPDATE atlas_briefings
SET status = 'vetoed'
WHERE DATE(created_at) = CURRENT_DATE
  AND status = 'sent'
""",
    'WF-07_mark_approved': """
UPDATE atlas_briefings
SET status = 'approved'
WHERE DATE(created_at) = CURRENT_DATE
  AND status = 'sent'
""",
    'WF-08_update_live': """
UPDATE atlas_experiments
SET status = 'active',
    landing_page_url = '{{ $json.landing_page_url }}'
WHERE experiment_id = '{{ $json.experiment_id }}'
""",
    'WF-08_update_failed': """
UPDATE atlas_experiments
SET status = 'failed',
    kill_reason = '{{ $json.error_message }}'
WHERE experiment_id = '{{ $json.experiment_id }}'
""",
    'WF-09_update_measuring': """
UPDATE atlas_experiments
SET status = 'measuring'
WHERE experiment_id = '{{ $json.experiment_id }}'
""",
    'WF-12_update_killed': """
UPDATE atlas_experiments
SET status = 'killed',
    kill_reason = '{{ $json.kill_reason }}',
    ended_at = NOW()
WHERE experiment_id = '{{ $json.experiment_id }}'
"""
}

def fix_supabase_node(node, workflow_name):
    """Fix a single Supabase node with proper configuration"""
    node_name = node.get('name', '').lower()
    params = node.get('parameters', {})
    operation = params.get('operation', '')

    # Ensure credential is set
    if 'credentials' not in node:
        node['credentials'] = {}
    if 'supabaseApi' not in node['credentials']:
        node['credentials']['supabaseApi'] = {
            'id': SUPABASE_CRED_ID,
            'name': 'ATLAS Supabase'
        }

    # Fix based on operation type
    if operation == 'create':
        # Determine table from context
        if 'opportunity' in node_name or 'opportunities' in node_name:
            params['table'] = 'atlas_opportunities'
            params['columns'] = 'title,source,source_url,description,category,target_vertical,haiku_filter_pass,status,discovered_at'
        elif 'experiment' in node_name:
            params['table'] = 'atlas_experiments'
            params['columns'] = 'experiment_id,opportunity_id,name,vertical,status,budget_allocated,started_at'
        elif 'ledger' in node_name or 'spend' in node_name:
            params['table'] = 'atlas_budget_ledger'
            params['columns'] = 'transaction_type,amount,experiment_id,agent,description,balance_after'
        elif 'log' in node_name or 'agent' in node_name:
            params['table'] = 'atlas_agent_logs'
            params['columns'] = 'agent_name,action_type,details,experiment_id'
        elif 'briefing' in node_name:
            params['table'] = 'atlas_briefings'
            params['columns'] = 'briefing_type,content,decisions,status'

    elif operation == 'update':
        # Determine table and conditions
        if 'opportunity' in node_name or 'opportunities' in node_name:
            params['table'] = 'atlas_opportunities'
            params['filterType'] = 'manual'
            params['filters'] = {
                'conditions': [{
                    'field': 'id',
                    'operator': '=',
                    'value': '={{ $json.id }}'
                }]
            }
        elif 'experiment' in node_name:
            params['table'] = 'atlas_experiments'
            params['filterType'] = 'manual'
            params['filters'] = {
                'conditions': [{
                    'field': 'experiment_id',
                    'operator': '=',
                    'value': '={{ $json.experiment_id }}'
                }]
            }
        elif 'briefing' in node_name:
            params['table'] = 'atlas_briefings'
            params['filterType'] = 'manual'
            params['filters'] = {
                'conditions': [{
                    'field': 'id',
                    'operator': '=',
                    'value': '={{ $json.id }}'
                }]
            }

    elif operation == 'get' or operation == 'getAll':
        # Set table based on context
        if 'budget' in node_name:
            params['table'] = 'atlas_budget_summary'
        elif 'experiment' in node_name:
            params['table'] = 'atlas_experiments'
        elif 'opportunity' in node_name:
            params['table'] = 'atlas_opportunities'
        elif 'briefing' in node_name:
            params['table'] = 'atlas_briefings'
        elif 'log' in node_name:
            params['table'] = 'atlas_agent_logs'

    elif operation == 'executeQuery':
        # Map SQL queries based on workflow and node name
        query_key = None

        if 'WF-01' in workflow_name:
            if 'top' in node_name or '5' in node_name:
                query_key = 'WF-01_top_opportunities'
        elif 'WF-02' in workflow_name:
            if 'active' in node_name:
                query_key = 'WF-02_active_experiments'
            elif 'upsert' in node_name or 'metrics' in node_name:
                query_key = 'WF-02_upsert_metrics'
        elif 'WF-03' in workflow_name:
            if 'active' in node_name:
                query_key = 'WF-03_active_experiments'
            elif '7' in node_name or 'days' in node_name:
                query_key = 'WF-03_metrics_7days'
        elif 'WF-04' in workflow_name:
            if 'budget' in node_name and 'status' in node_name:
                query_key = 'WF-04_budget_status'
            elif 'experiment' in node_name and 'spend' in node_name:
                query_key = 'WF-04_experiment_spend'
        elif 'WF-05' in workflow_name:
            if 'all' in node_name and 'experiment' in node_name:
                query_key = 'WF-05_all_experiments'
            elif 'budget' in node_name:
                query_key = 'WF-05_budget_status'
            elif 'opportunities' in node_name:
                query_key = 'WF-05_new_opportunities'
            elif 'log' in node_name:
                query_key = 'WF-05_recent_logs'
            elif 'yesterday' in node_name or 'metrics' in node_name:
                query_key = 'WF-05_yesterday_metrics'
        elif 'WF-07' in workflow_name:
            if 'veto' in node_name:
                query_key = 'WF-07_mark_vetoed'
            elif 'approved' in node_name:
                query_key = 'WF-07_mark_approved'
        elif 'WF-08' in workflow_name:
            if 'live' in node_name:
                query_key = 'WF-08_update_live'
            elif 'failed' in node_name:
                query_key = 'WF-08_update_failed'
        elif 'WF-09' in workflow_name:
            if 'measuring' in node_name:
                query_key = 'WF-09_update_measuring'
        elif 'WF-12' in workflow_name:
            if 'killed' in node_name:
                query_key = 'WF-12_update_killed'

        if query_key and query_key in SQL_QUERIES:
            params['query'] = SQL_QUERIES[query_key].strip()

    # Update node parameters
    node['parameters'] = params
    return node

def fix_workflow(workflow_path):
    """Fix all Supabase nodes in a workflow"""
    with open(workflow_path, 'r') as f:
        workflow = json.load(f)

    workflow_name = workflow.get('name', '')
    modified = False

    # Process each node
    for node in workflow.get('nodes', []):
        if node.get('type') == 'n8n-nodes-base.supabase':
            fix_supabase_node(node, workflow_name)
            modified = True

    return workflow if modified else None

def main():
    print("🔧 ATLAS Workflow Fixer")
    print("=" * 60)

    # Create output directory
    FIXED_DIR.mkdir(exist_ok=True)

    fixed_count = 0

    # Process each workflow
    for workflow_file in WORKFLOWS_DIR.glob('WF-*.json'):
        print(f"\n📄 Processing: {workflow_file.name}")

        fixed_workflow = fix_workflow(workflow_file)

        if fixed_workflow:
            # Save fixed version
            output_path = FIXED_DIR / workflow_file.name
            with open(output_path, 'w') as f:
                json.dump(fixed_workflow, f, indent=2)

            print(f"   ✅ Fixed and saved to workflows-fixed/")
            fixed_count += 1
        else:
            # Copy as-is if no Supabase nodes
            shutil.copy(workflow_file, FIXED_DIR / workflow_file.name)
            print(f"   ➡️  No Supabase nodes, copied as-is")

    print("\n" + "=" * 60)
    print(f"✨ Complete! Fixed {fixed_count} workflows")
    print(f"📁 Fixed workflows saved to: {FIXED_DIR}")
    print("\nNext step: Run import-fixed-workflows.py to import to n8n")

if __name__ == '__main__':
    main()