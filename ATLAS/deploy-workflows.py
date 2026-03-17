#!/usr/bin/env python3
"""
ATLAS Workflow Deployment Script
Automatically deploys all workflows to n8n via API
"""

import json
import requests
import os
import time
from pathlib import Path

# Load environment variables
ENV_PATH = Path(__file__).parent / "config" / ".env"
env_vars = {}
if ENV_PATH.exists():
    with open(ENV_PATH) as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                env_vars[key] = value

N8N_URL = env_vars.get('N8N_URL', 'http://localhost:5678')
N8N_API_KEY = env_vars.get('N8N_API_KEY', '')

# Workflow deployment order (dependencies first)
WORKFLOW_ORDER = [
    "WF-04-Budget-Guardian-VAULT.json",      # Must be first - all agents depend on this
    "WF-06-Daily-Briefing-Sender.json",      # Foundation
    "WF-02-Metrics-Collector.json",          # Metrics before calculator
    "WF-03-EHS-Calculator.json",             # Needs metrics
    "WF-01-SCOUT-Pipeline.json",             # Core discovery
    "WF-05-ATLAS-Orchestrator.json",         # Brain - needs all data workflows
    "WF-07-Veto-Checker.json",               # After orchestrator
    "WF-08-Forge-Builder.json",              # Execution phase
    "WF-09-Mercury-Distribution.json",       # After Forge
    "WF-10-Evening-Snapshot.json",           # End of day
    "WF-11-Weekly-PNL-Report.json",          # Weekly summary
    "WF-12-Experiment-Killer.json"           # Cleanup
]

def test_connection():
    """Test n8n API connection"""
    try:
        response = requests.get(
            f"{N8N_URL}/api/v1/workflows",
            headers={"X-N8N-API-KEY": N8N_API_KEY}
        )
        if response.status_code == 200:
            print("✅ Successfully connected to n8n")
            return True
        else:
            print(f"❌ Failed to connect: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def check_existing_workflow(name):
    """Check if workflow already exists"""
    try:
        response = requests.get(
            f"{N8N_URL}/api/v1/workflows",
            headers={"X-N8N-API-KEY": N8N_API_KEY}
        )
        if response.status_code == 200:
            workflows = response.json()
            for wf in workflows:
                if wf.get('name') == name:
                    return wf['id']
        return None
    except:
        return None

def deploy_workflow(workflow_file):
    """Deploy a single workflow"""
    workflow_path = Path(__file__).parent / "workflows" / workflow_file

    if not workflow_path.exists():
        print(f"   ⚠️  Workflow file not found: {workflow_file}")
        return False

    with open(workflow_path) as f:
        workflow_data = json.load(f)

    workflow_name = workflow_data.get('name', workflow_file)

    # Check if already exists
    existing_id = check_existing_workflow(workflow_name)
    if existing_id:
        print(f"   ⚠️  Workflow already exists with ID: {existing_id}")
        # Update instead of create
        response = requests.put(
            f"{N8N_URL}/api/v1/workflows/{existing_id}",
            headers={
                "X-N8N-API-KEY": N8N_API_KEY,
                "Content-Type": "application/json"
            },
            json=workflow_data
        )
    else:
        # Create new workflow
        response = requests.post(
            f"{N8N_URL}/api/v1/workflows",
            headers={
                "X-N8N-API-KEY": N8N_API_KEY,
                "Content-Type": "application/json"
            },
            json=workflow_data
        )

    if response.status_code in [200, 201]:
        result = response.json()
        workflow_id = result.get('id')
        print(f"   ✅ Deployed with ID: {workflow_id}")

        # Keep inactive for safety
        requests.patch(
            f"{N8N_URL}/api/v1/workflows/{workflow_id}",
            headers={
                "X-N8N-API-KEY": N8N_API_KEY,
                "Content-Type": "application/json"
            },
            json={"active": False}
        )
        return workflow_id
    else:
        print(f"   ❌ Failed to deploy: {response.status_code}")
        print(f"   Error: {response.text}")
        return False

def main():
    """Main deployment process"""
    print("🚀 ATLAS Workflow Deployment")
    print("=" * 50)

    if not N8N_API_KEY:
        print("❌ N8N_API_KEY not found in .env file")
        print("   Please add your n8n API key to config/.env")
        return

    print(f"📍 n8n URL: {N8N_URL}")
    print(f"🔑 API Key: {N8N_API_KEY[:20]}...")
    print()

    if not test_connection():
        print("\n⚠️  Please ensure:")
        print("   1. n8n is running at", N8N_URL)
        print("   2. API is enabled (N8N_USER_MANAGEMENT_DISABLED=true)")
        print("   3. API key is correct")
        return

    print("\n📤 Deploying workflows...")
    print("-" * 50)

    deployed = []
    failed = []

    for workflow_file in WORKFLOW_ORDER:
        print(f"\n▶️  {workflow_file}")
        result = deploy_workflow(workflow_file)
        if result:
            deployed.append(workflow_file)
        else:
            failed.append(workflow_file)
        time.sleep(1)  # Avoid overwhelming the API

    print("\n" + "=" * 50)
    print("📊 Deployment Summary")
    print(f"   ✅ Deployed: {len(deployed)}/{len(WORKFLOW_ORDER)}")
    if failed:
        print(f"   ❌ Failed: {', '.join(failed)}")

    print("\n⚠️  IMPORTANT:")
    print("   • All workflows are INACTIVE by default")
    print("   • Test each workflow manually before activating")
    print("   • Activate WF-04 Budget Guardian FIRST")
    print("   • Check your email is set to: taneja.ashish5@gmail.com")
    print(f"\n✨ Done! Open n8n at {N8N_URL}")

if __name__ == "__main__":
    main()