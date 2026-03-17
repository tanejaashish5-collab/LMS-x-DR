#!/usr/bin/env python3
"""
Automated n8n Import Script for ATLAS
Imports all workflows and creates credentials automatically
"""

import requests
import json
import os
from pathlib import Path
import time

# n8n connection details
N8N_URL = "http://localhost:5678"
N8N_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2ZTJmOTYwNi02NTc3LTQzZDktODVlMy04NjM2YjdlM2ExNDMiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZDM5YzI2ODYtMDQxMC00MmFjLTg4NTktMjdmYTI3YmExY2EwIiwiaWF0IjoxNzczNzMzNDQ0fQ.UCU_ADDJfJnnlFMVzmsy7UsnTW7ExLZqIYy75fv8SMs"

headers = {
    "X-N8N-API-KEY": N8N_TOKEN,
    "Content-Type": "application/json"
}

# Load environment variables
env_file = Path(__file__).parent / "config" / ".env"
env_vars = {}
with open(env_file, 'r') as f:
    for line in f:
        if '=' in line and not line.strip().startswith('#'):
            key, value = line.strip().split('=', 1)
            env_vars[key] = value

def import_workflow(workflow_file):
    """Import a single workflow to n8n"""
    try:
        with open(workflow_file, 'r') as f:
            workflow_data = json.load(f)

        # Clean up workflow data for import
        if 'id' in workflow_data:
            del workflow_data['id']
        if 'createdAt' in workflow_data:
            del workflow_data['createdAt']
        if 'updatedAt' in workflow_data:
            del workflow_data['updatedAt']

        # Remove read-only fields
        if 'active' in workflow_data:
            del workflow_data['active']
        if 'versionId' in workflow_data:
            del workflow_data['versionId']

        response = requests.post(
            f"{N8N_URL}/api/v1/workflows",
            headers=headers,
            json=workflow_data
        )

        if response.status_code in [200, 201]:
            result = response.json()
            # Handle different response formats
            if 'data' in result:
                workflow_id = result['data']['id']
            else:
                workflow_id = result.get('id', 'unknown')
            print(f"  ✅ Imported: {workflow_data['name']} (ID: {workflow_id})")
            return workflow_id
        else:
            print(f"  ❌ Failed to import {workflow_file.name}: {response.status_code}")
            if response.text:
                print(f"     Response: {response.text[:300]}")
            return None
    except json.JSONDecodeError as e:
        print(f"  ❌ JSON error in {workflow_file.name}: {e}")
        return None
    except KeyError as e:
        print(f"  ❌ Missing key in response for {workflow_file.name}: {e}")
        # Try without 'data' wrapper
        try:
            if response and response.status_code in [200, 201]:
                result_text = response.text
                result = json.loads(result_text) if result_text else {}
                workflow_id = result.get('id', 'unknown')
                print(f"  ✅ Imported (alt format): {workflow_file.stem} (ID: {workflow_id})")
                return workflow_id
        except:
            pass
        return None
    except Exception as e:
        print(f"  ❌ Error importing {workflow_file.name}: {e}")
        return None

def create_credentials():
    """Create all required credentials in n8n"""
    print("\n📦 Creating credentials...")

    credentials_to_create = [
        {
            "name": "ATLAS Supabase REST",
            "type": "httpHeaderAuth",
            "data": json.dumps({
                "name": "apikey",
                "value": env_vars['SUPABASE_ANON_KEY']
            })
        },
        {
            "name": "ATLAS Claude API",
            "type": "httpHeaderAuth",
            "data": json.dumps({
                "name": "x-api-key",
                "value": env_vars['ANTHROPIC_API_KEY']
            })
        },
        {
            "name": "ATLAS Notion",
            "type": "notionApi",
            "data": json.dumps({
                "apiKey": env_vars['NOTION_INTEGRATION_TOKEN']
            })
        },
        {
            "name": "ATLAS Gemini",
            "type": "httpHeaderAuth",
            "data": json.dumps({
                "name": "x-goog-api-key",
                "value": env_vars['GEMINI_API_KEY']
            })
        }
    ]

    created_creds = {}

    for cred in credentials_to_create:
        try:
            response = requests.post(
                f"{N8N_URL}/api/v1/credentials",
                headers=headers,
                json=cred
            )

            if response.status_code in [200, 201]:
                cred_id = response.json()['data']['id']
                created_creds[cred['name']] = cred_id
                print(f"  ✅ Created credential: {cred['name']} (ID: {cred_id})")
            else:
                # Check if credential already exists
                existing_response = requests.get(
                    f"{N8N_URL}/api/v1/credentials",
                    headers=headers
                )
                if existing_response.status_code == 200:
                    existing = existing_response.json().get('data', [])
                    for existing_cred in existing:
                        if existing_cred['name'] == cred['name']:
                            created_creds[cred['name']] = existing_cred['id']
                            print(f"  ↳ Credential '{cred['name']}' already exists (ID: {existing_cred['id']})")
                            break
                else:
                    print(f"  ❌ Failed to create {cred['name']}: {response.status_code}")
        except Exception as e:
            print(f"  ❌ Error creating {cred['name']}: {e}")

    return created_creds

def main():
    print("🚀 ATLAS n8n Automated Import Script")
    print("="*60)

    # Test connection
    print("\n🔌 Testing n8n connection...")
    try:
        response = requests.get(f"{N8N_URL}/api/v1/workflows", headers=headers)
        if response.status_code == 200:
            existing_count = len(response.json().get('data', []))
            print(f"  ✅ Connected to n8n (found {existing_count} existing workflows)")
        else:
            print(f"  ❌ Failed to connect: {response.status_code}")
            return
    except Exception as e:
        print(f"  ❌ Connection error: {e}")
        return

    # Create credentials first
    credentials = create_credentials()

    # Import workflows
    print("\n📥 Importing ATLAS workflows...")
    workflows_dir = Path(__file__).parent / "workflows"
    workflow_files = sorted(workflows_dir.glob("WF-*.json"))

    if not workflow_files:
        print(f"  ❌ No workflow files found in {workflows_dir}")
        return

    imported_workflows = []

    # Import in priority order
    priority_order = [
        "WF-04-Budget-Guardian",  # Most critical - controls spending
        "WF-02-Metrics-Collector",
        "WF-03-EHS-Calculator",
        "WF-01-SCOUT-Pipeline",
        "WF-05-ATLAS-Orchestrator",
        "WF-06-Daily-Briefing"
    ]

    # Sort files by priority
    sorted_files = []
    for priority in priority_order:
        for wf_file in workflow_files:
            if priority in wf_file.name:
                sorted_files.append(wf_file)
                break

    # Add any remaining files
    for wf_file in workflow_files:
        if wf_file not in sorted_files:
            sorted_files.append(wf_file)

    for workflow_file in sorted_files:
        print(f"\n  Importing: {workflow_file.name}")
        workflow_id = import_workflow(workflow_file)
        if workflow_id:
            imported_workflows.append({
                'id': workflow_id,
                'name': workflow_file.stem,
                'file': workflow_file.name
            })
        time.sleep(0.5)  # Small delay to avoid overwhelming n8n

    # Summary
    print("\n" + "="*60)
    print("✅ IMPORT COMPLETE!")
    print(f"\n📊 Summary:")
    print(f"  • Workflows imported: {len(imported_workflows)}/{len(workflow_files)}")
    print(f"  • Credentials created: {len(credentials)}")

    if imported_workflows:
        print("\n🎯 Next Steps:")
        print("1. Open n8n at http://localhost:5678")
        print("2. Check each workflow and assign credentials:")
        for cred_name in credentials:
            print(f"   • Use '{cred_name}' for respective nodes")
        print("3. Test Budget Guardian webhook first:")
        print("   curl -X POST http://localhost:5678/webhook/budget-check \\")
        print("     -H 'Content-Type: application/json' \\")
        print("     -d '{\"amount\": 10, \"type\": \"test\", \"agent\": \"VAULT\"}'")
        print("4. Activate workflows in this order:")
        for i, wf in enumerate(imported_workflows[:6], 1):
            print(f"   {i}. {wf['name']}")

    print("\n💡 The ATLAS system is now imported and ready for activation!")
    print("="*60)

if __name__ == "__main__":
    main()