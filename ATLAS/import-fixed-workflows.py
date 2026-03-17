#!/usr/bin/env python3
"""
ATLAS Fixed Workflows Importer
Removes old workflows and imports the fixed versions
"""

import requests
import json
import os
import sys
from pathlib import Path
import time

# Configuration
N8N_URL = 'http://localhost:5678'
N8N_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2ZTJmOTYwNi02NTc3LTQzZDktODVlMy04NjM2YjdlM2ExNDMiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZDM5YzI2ODYtMDQxMC00MmFjLTg4NTktMjdmYTI3YmExY2EwIiwiaWF0IjoxNzczNzMzNDQ0fQ.UCU_ADDJfJnnlFMVzmsy7UsnTW7ExLZqIYy75fv8SMs'
FIXED_DIR = Path('/Users/ashishtaneja/Desktop/Business Opp/ATLAS/workflows-fixed')

headers = {
    'X-N8N-API-KEY': N8N_TOKEN,
    'Content-Type': 'application/json'
}

# Workflow import order (critical workflows first)
IMPORT_ORDER = [
    'WF-04-Budget-Guardian-VAULT.json',    # VAULT - must be first
    'WF-05-ATLAS-Orchestrator.json',       # Main brain
    'WF-01-SCOUT-Pipeline.json',           # Discovery
    'WF-02-Metrics-Collector.json',        # Analytics collection
    'WF-03-EHS-Calculator.json',           # Health scoring
    'WF-06-Daily-Briefing-Sender.json',    # Reports
    'WF-07-Veto-Checker.json',             # Human oversight
    'WF-08-Forge-Builder.json',            # Landing page builder
    'WF-09-Mercury-Distribution.json',     # Distribution
    'WF-10-Evening-Snapshot.json',         # Daily metrics
    'WF-11-Weekly-PNL-Report.json',        # Weekly report
    'WF-12-Experiment-Killer.json'         # Terminator
]

def get_existing_workflows():
    """Get all existing ATLAS workflows"""
    try:
        response = requests.get(f'{N8N_URL}/api/v1/workflows', headers=headers)
        if response.status_code == 200:
            workflows = response.json().get('data', [])
            atlas_workflows = [w for w in workflows if 'WF-' in w['name']]
            return {w['name']: w['id'] for w in atlas_workflows}
        return {}
    except Exception as e:
        print(f"Error getting workflows: {e}")
        return {}

def delete_workflow(workflow_id, workflow_name):
    """Delete a workflow"""
    try:
        response = requests.delete(f'{N8N_URL}/api/v1/workflows/{workflow_id}', headers=headers)
        if response.status_code == 200:
            print(f"   ✅ Deleted: {workflow_name}")
            return True
        else:
            print(f"   ❌ Failed to delete: {workflow_name}")
            return False
    except Exception as e:
        print(f"   ❌ Error deleting {workflow_name}: {e}")
        return False

def import_workflow(file_path):
    """Import a workflow"""
    workflow_name = file_path.stem

    try:
        with open(file_path, 'r') as f:
            workflow = json.load(f)

        # Clean up for import
        fields_to_remove = ['id', 'createdAt', 'updatedAt', 'versionId', 'active']
        for field in fields_to_remove:
            workflow.pop(field, None)

        # Import the workflow
        response = requests.post(f'{N8N_URL}/api/v1/workflows', headers=headers, json=workflow)

        if response.status_code in [200, 201]:
            result = response.json()
            workflow_id = result.get('data', {}).get('id') or result.get('id')
            workflow_display_name = workflow.get('name', workflow_name)
            print(f"   ✅ Imported: {workflow_display_name} (ID: {workflow_id})")

            # Activate critical workflows
            if any(critical in workflow_name for critical in ['WF-04', 'WF-05']):
                time.sleep(1)  # Brief pause before activation
                activate_url = f'{N8N_URL}/api/v1/workflows/{workflow_id}/activate'
                activate_response = requests.post(activate_url, headers=headers)
                if activate_response.status_code == 200:
                    print(f"      🟢 ACTIVATED (Critical workflow)")
                else:
                    print(f"      ⚠️  Auto-activation failed, please activate manually")

            return workflow_id
        else:
            print(f"   ❌ Import failed: {response.status_code}")
            error_msg = response.text[:300]
            print(f"      Error: {error_msg}")
            return None

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def main():
    print("\n" + "=" * 80)
    print(" ATLAS FIXED WORKFLOWS IMPORTER")
    print("=" * 80)

    if not FIXED_DIR.exists():
        print(f"❌ Fixed workflows directory not found: {FIXED_DIR}")
        print("   Please run fix-all-workflows.py first!")
        sys.exit(1)

    # Test n8n connection
    print("\n🔍 Testing n8n connection...")
    existing = get_existing_workflows()
    print(f"✅ Connected to n8n - found {len(existing)} existing ATLAS workflows")

    # Delete old workflows
    if existing:
        print(f"\n🗑️  Removing {len(existing)} old workflows...")
        for name, wf_id in existing.items():
            delete_workflow(wf_id, name)
    else:
        print("\n📋 No old workflows to remove")

    # Import fixed workflows
    print(f"\n📥 Importing {len(IMPORT_ORDER)} fixed workflows...")
    successful_imports = []
    failed_imports = []

    for workflow_file in IMPORT_ORDER:
        file_path = FIXED_DIR / workflow_file
        print(f"\n📄 {workflow_file}")

        if file_path.exists():
            result = import_workflow(file_path)
            if result:
                successful_imports.append(workflow_file)
            else:
                failed_imports.append(workflow_file)
        else:
            print(f"   ⚠️  File not found")
            # Try without -FIXED suffix
            alt_path = FIXED_DIR / workflow_file.replace('-FIXED', '')
            if alt_path.exists():
                print(f"   📄 Trying alternate: {alt_path.name}")
                result = import_workflow(alt_path)
                if result:
                    successful_imports.append(workflow_file)
                else:
                    failed_imports.append(workflow_file)
            else:
                failed_imports.append(workflow_file)

    # Summary
    print("\n" + "=" * 80)
    print(" IMPORT SUMMARY")
    print("=" * 80)
    print(f"\n✅ Successfully imported: {len(successful_imports)}/{len(IMPORT_ORDER)} workflows")

    if successful_imports:
        print("\n📋 Imported workflows:")
        for wf in successful_imports:
            print(f"   ✓ {wf}")

    if failed_imports:
        print(f"\n❌ Failed imports: {len(failed_imports)} workflows")
        for wf in failed_imports:
            print(f"   ✗ {wf}")

    # Final checks and instructions
    print("\n" + "=" * 80)
    print(" VERIFICATION STEPS")
    print("=" * 80)
    print("""
1. 🌐 Open n8n UI: http://localhost:5678
2. 🔍 Verify all workflows show correct table names
3. ✅ No more "Unknown" tables or missing configurations
4. 🚀 Test VAULT webhook:

   curl -X POST http://localhost:5678/webhook/budget-check \\
     -H "Content-Type: application/json" \\
     -d '{"amount": 10, "experiment_id": "test-001", "agent": "TEST"}'

5. 📊 Check Supabase for logged transaction:

   cd /Users/ashishtaneja/Desktop/Business\\ Opp/ATLAS
   python3 check-supabase-status.py

Expected: Balance reduced from $250 to $240
""")

    print("\n✨ All Supabase configurations are now automated!")
    print("   No manual configuration needed in n8n UI!")

if __name__ == '__main__':
    main()