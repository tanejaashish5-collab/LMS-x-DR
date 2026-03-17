#!/usr/bin/env python3
"""
ATLAS Workflow Importer for n8n
Imports all 12 ATLAS workflows with correct credential mappings
"""

import requests
import json
import os
import sys
from pathlib import Path

# n8n Configuration
N8N_URL = 'http://localhost:5678'
N8N_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2ZTJmOTYwNi02NTc3LTQzZDktODVlMy04NjM2YjdlM2ExNDMiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZDM5YzI2ODYtMDQxMC00MmFjLTg4NTktMjdmYTI3YmExY2EwIiwiaWF0IjoxNzczNzMzNDQ0fQ.UCU_ADDJfJnnlFMVzmsy7UsnTW7ExLZqIYy75fv8SMs'

headers = {
    'X-N8N-API-KEY': N8N_TOKEN,
    'Content-Type': 'application/json'
}

# Known credential IDs from n8n
CREDENTIAL_MAPPING = {
    'ATLAS Supabase': 'cbOITfdnZcDuTRJZ',
    'ATLAS Claude API': 'mwxp7qfMsdDAus5I',
    'ATLAS Notion': 'bVZmIj9sDENAidkO',
    'ATLAS Gmail': 'GMAIL_OAUTH_NEEDS_CONFIG'  # Will need manual config
}

# Workflow import order (critical workflows first)
WORKFLOW_ORDER = [
    'WF-04-Budget-Guardian-VAULT.json', # VAULT - must be first
    'WF-05-ATLAS-Orchestrator.json',   # Main brain
    'WF-01-SCOUT-Pipeline.json',       # Discovery
    'WF-02-Metrics-Collector.json',    # Analytics collection
    'WF-03-EHS-Calculator.json',       # Health scoring
    'WF-06-Daily-Briefing-Sender.json', # Reports
    'WF-07-Veto-Checker.json',         # Human oversight
    'WF-08-Forge-Builder.json',        # Landing page builder
    'WF-09-Mercury-Distribution.json',  # Distribution
    'WF-10-Evening-Snapshot.json',     # Daily metrics
    'WF-11-Weekly-PNL-Report.json',    # Weekly report
    'WF-12-Experiment-Killer.json'     # Terminator
]

def get_existing_workflows():
    """Get list of existing workflows in n8n"""
    try:
        response = requests.get(f'{N8N_URL}/api/v1/workflows', headers=headers)
        if response.status_code == 200:
            workflows = response.json().get('data', [])
            return {w['name']: w['id'] for w in workflows}
        return {}
    except Exception as e:
        print(f"Error getting workflows: {e}")
        return {}

def delete_workflow(workflow_id):
    """Delete a workflow by ID"""
    try:
        response = requests.delete(f'{N8N_URL}/api/v1/workflows/{workflow_id}', headers=headers)
        return response.status_code == 200
    except:
        return False

def update_credential_references(workflow_data):
    """Update credential placeholders with actual IDs"""
    workflow_str = json.dumps(workflow_data)

    # Replace credential placeholders
    for cred_name, cred_id in CREDENTIAL_MAPPING.items():
        workflow_str = workflow_str.replace('{{credentialId}}', cred_id)

    # Parse back to dict
    workflow_data = json.loads(workflow_str)

    # Update specific credential references in nodes
    if 'nodes' in workflow_data:
        for node in workflow_data['nodes']:
            if 'credentials' in node:
                for cred_type, cred_info in node['credentials'].items():
                    # Map credential names to IDs
                    if 'name' in cred_info:
                        cred_name = cred_info['name']
                        if cred_name in CREDENTIAL_MAPPING:
                            cred_info['id'] = CREDENTIAL_MAPPING[cred_name]
                        elif 'Supabase' in cred_name:
                            cred_info['id'] = CREDENTIAL_MAPPING['ATLAS Supabase']
                        elif 'Claude' in cred_name or 'Anthropic' in cred_name:
                            cred_info['id'] = CREDENTIAL_MAPPING['ATLAS Claude API']
                        elif 'Notion' in cred_name:
                            cred_info['id'] = CREDENTIAL_MAPPING['ATLAS Notion']

    return workflow_data

def import_workflow(file_path):
    """Import a single workflow file"""
    workflow_name = os.path.basename(file_path).replace('.json', '')

    print(f"\n{'='*60}")
    print(f"Importing: {workflow_name}")
    print(f"{'='*60}")

    try:
        # Read workflow file
        with open(file_path, 'r') as f:
            workflow_data = json.load(f)

        # Update credential references
        workflow_data = update_credential_references(workflow_data)

        # Clean up for import
        fields_to_remove = ['id', 'createdAt', 'updatedAt', 'versionId', 'active']
        for field in fields_to_remove:
            workflow_data.pop(field, None)

        # Check if workflow exists and delete duplicates
        existing = get_existing_workflows()
        workflow_display_name = workflow_data.get('name', workflow_name)

        # Delete all duplicates
        deleted_count = 0
        for existing_name, existing_id in existing.items():
            if workflow_display_name in existing_name or workflow_name in existing_name:
                if delete_workflow(existing_id):
                    deleted_count += 1
                    print(f"  ✓ Deleted duplicate: {existing_name} (ID: {existing_id})")

        if deleted_count > 0:
            print(f"  → Cleaned up {deleted_count} duplicate(s)")

        # Import the workflow
        response = requests.post(f'{N8N_URL}/api/v1/workflows', headers=headers, json=workflow_data)

        if response.status_code in [200, 201]:
            result = response.json()
            workflow_id = result.get('data', {}).get('id') or result.get('id')
            print(f"  ✅ Successfully imported: {workflow_display_name}")
            print(f"     ID: {workflow_id}")

            # Activate critical workflows
            if any(critical in workflow_name for critical in ['WF-04', 'WF-05', 'VAULT', 'Orchestrator']):
                activate_response = requests.patch(
                    f'{N8N_URL}/api/v1/workflows/{workflow_id}',
                    headers=headers,
                    json={'active': True}
                )
                if activate_response.status_code == 200:
                    print(f"     🟢 ACTIVATED (Critical workflow)")

            return workflow_id
        else:
            print(f"  ❌ Import failed: {response.status_code}")
            error_msg = response.text[:500]
            print(f"     Error: {error_msg}")
            return None

    except Exception as e:
        print(f"  ❌ Error: {e}")
        return None

def main():
    """Main import process"""
    print("\n" + "="*80)
    print(" ATLAS WORKFLOW IMPORTER FOR N8N")
    print("="*80)

    workflows_dir = Path('/Users/ashishtaneja/Desktop/Business Opp/ATLAS/workflows')

    if not workflows_dir.exists():
        print(f"❌ Workflows directory not found: {workflows_dir}")
        sys.exit(1)

    # Test n8n connection
    print("\n🔍 Testing n8n connection...")
    existing = get_existing_workflows()
    print(f"✅ Connected to n8n - found {len(existing)} existing workflows")

    # Import workflows in order
    successful_imports = []
    failed_imports = []

    for workflow_file in WORKFLOW_ORDER:
        file_path = workflows_dir / workflow_file
        if file_path.exists():
            result = import_workflow(file_path)
            if result:
                successful_imports.append(workflow_file)
            else:
                failed_imports.append(workflow_file)
        else:
            print(f"\n⚠️  File not found: {workflow_file}")
            failed_imports.append(workflow_file)

    # Summary
    print("\n" + "="*80)
    print(" IMPORT SUMMARY")
    print("="*80)
    print(f"\n✅ Successfully imported: {len(successful_imports)} workflows")
    for wf in successful_imports:
        print(f"   • {wf}")

    if failed_imports:
        print(f"\n❌ Failed imports: {len(failed_imports)} workflows")
        for wf in failed_imports:
            print(f"   • {wf}")

    print("\n" + "="*80)
    print(" NEXT STEPS")
    print("="*80)
    print("""
1. ✅ VAULT (WF-04) and Orchestrator (WF-05) are auto-activated
2. 📧 Configure Gmail OAuth in n8n UI for WF-06 and WF-07
3. 🔑 Add environment variables to n8n:
   - ANTHROPIC_API_KEY
   - SUPABASE_URL & SUPABASE_ANON_KEY
   - NOTION_INTEGRATION_TOKEN
   - VERCEL_API_TOKEN
   - APIFY_API_TOKEN
   - STRIPE_SECRET_KEY (already added by user)
4. 🚀 Test VAULT webhook: http://localhost:5678/webhook/budget-check
5. 📊 Monitor in Notion: ATLAS Dashboard
""")

if __name__ == '__main__':
    main()