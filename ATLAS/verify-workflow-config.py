#!/usr/bin/env python3
"""
ATLAS Workflow Configuration Verifier
Checks all workflows and reports what needs manual configuration
"""

import requests
import json
from pathlib import Path

# n8n Configuration
N8N_URL = 'http://localhost:5678'
N8N_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2ZTJmOTYwNi02NTc3LTQzZDktODVlMy04NjM2YjdlM2ExNDMiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZDM5YzI2ODYtMDQxMC00MmFjLTg4NTktMjdmYTI3YmExY2EwIiwiaWF0IjoxNzczNzMzNDQ0fQ.UCU_ADDJfJnnlFMVzmsy7UsnTW7ExLZqIYy75fv8SMs'

headers = {
    'X-N8N-API-KEY': N8N_TOKEN,
    'Content-Type': 'application/json'
}

def check_workflow(workflow_id, workflow_name):
    """Check a single workflow for configuration issues"""
    try:
        response = requests.get(f'{N8N_URL}/api/v1/workflows/{workflow_id}', headers=headers)
        if response.status_code != 200:
            return f"❌ Could not fetch workflow"

        workflow = response.json()
        issues = []
        supabase_nodes = []

        for node in workflow.get('nodes', []):
            if node.get('type') == 'n8n-nodes-base.supabase':
                node_name = node.get('name', 'Unknown')
                params = node.get('parameters', {})

                # Check for common issues
                if 'table' not in params or params.get('table') == 'Unknown':
                    issues.append(f"  ⚠️  {node_name}: Missing table configuration")
                    supabase_nodes.append(node_name)
                elif params.get('operation') == 'executeQuery' and not params.get('query'):
                    issues.append(f"  ⚠️  {node_name}: Missing SQL query")
                    supabase_nodes.append(node_name)
                else:
                    # Node seems configured
                    supabase_nodes.append(f"✓ {node_name}")

        if supabase_nodes:
            print(f"\n📄 {workflow_name}")
            print(f"   Supabase nodes: {len(supabase_nodes)}")
            for node in supabase_nodes:
                print(f"   {node}")
            if issues:
                print("   Issues found:")
                for issue in issues:
                    print(issue)

        return len(issues) == 0

    except Exception as e:
        return f"❌ Error: {e}"

def main():
    print("=" * 80)
    print(" ATLAS WORKFLOW CONFIGURATION VERIFIER")
    print("=" * 80)

    # Get all workflows
    try:
        response = requests.get(f'{N8N_URL}/api/v1/workflows', headers=headers)
        if response.status_code != 200:
            print("❌ Could not connect to n8n")
            return

        workflows = response.json().get('data', [])
        atlas_workflows = [w for w in workflows if 'WF-' in w['name']]

        print(f"\n Found {len(atlas_workflows)} ATLAS workflows")
        print("-" * 80)

        all_good = True
        workflow_status = {}

        for workflow in sorted(atlas_workflows, key=lambda x: x['name']):
            is_configured = check_workflow(workflow['id'], workflow['name'])
            workflow_status[workflow['name']] = is_configured
            if not is_configured:
                all_good = False

        # Summary
        print("\n" + "=" * 80)
        print(" SUMMARY")
        print("=" * 80)

        configured_count = sum(1 for status in workflow_status.values() if status == True)
        print(f"\n✅ Fully configured: {configured_count}/{len(atlas_workflows)} workflows")

        if not all_good:
            print("\n⚠️  Workflows needing configuration:")
            for name, status in workflow_status.items():
                if status != True:
                    print(f"   • {name}")

            print("\n📖 Refer to COMPLETE-WORKFLOW-CONFIGURATION.md for exact values")
            print("   Location: /Users/ashishtaneja/Desktop/Business Opp/ATLAS/")
        else:
            print("\n🎉 All workflows are properly configured!")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    main()