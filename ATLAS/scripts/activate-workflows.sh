#!/bin/bash
# ATLAS Workflow Activation Script
# Activates critical workflows: WF-04 (VAULT) and WF-05 (Orchestrator)

set -e

echo "=========================================="
echo "ATLAS Workflow Activation"
echo "=========================================="
echo ""

# Load environment variables
if [ -f "/Users/ashishtaneja/Desktop/Business Opp/ATLAS/config/.env" ]; then
    export $(cat "/Users/ashishtaneja/Desktop/Business Opp/ATLAS/config/.env" | grep -v '^#' | xargs)
fi

N8N_HOST="http://localhost:5678"
N8N_API_KEY="${N8N_API_KEY}"

# Workflow IDs
VAULT_ID="5SuUZAAxOF2V08nF"
ORCHESTRATOR_ID="0J019KTway5tDU7P"

echo "Target n8n instance: $N8N_HOST"
echo ""

# Function to activate a workflow
activate_workflow() {
    local workflow_id="$1"
    local workflow_name="$2"

    echo "Activating $workflow_name (ID: $workflow_id)..."

    response=$(curl -s -w "\n%{http_code}" -X POST "$N8N_HOST/api/v1/workflows/$workflow_id/activate" \
        -H "X-N8N-API-KEY: $N8N_API_KEY")

    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    if [ "$http_code" -eq 200 ]; then
        echo "  ✓ Activated successfully"
        return 0
    else
        echo "  ✗ Activation failed (HTTP $http_code)"
        echo "  Response: $body"
        return 1
    fi
}

# Function to check workflow status
check_workflow() {
    local workflow_id="$1"
    local workflow_name="$2"

    echo "Checking $workflow_name status..."

    response=$(curl -s -w "\n%{http_code}" -X GET "$N8N_HOST/api/v1/workflows/$workflow_id" \
        -H "X-N8N-API-KEY: $N8N_API_KEY")

    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    if [ "$http_code" -eq 200 ]; then
        active=$(echo "$body" | jq -r '.active')
        if [ "$active" = "true" ]; then
            echo "  ✓ Currently ACTIVE"
        else
            echo "  ⚠ Currently INACTIVE"
        fi
    else
        echo "  ✗ Check failed (HTTP $http_code)"
    fi
}

# Check current status
echo "Current Status:"
echo "---------------"
check_workflow "$VAULT_ID" "WF-04 VAULT"
check_workflow "$ORCHESTRATOR_ID" "WF-05 Orchestrator"
echo ""

# Activate workflows
echo "Activating workflows..."
echo "----------------------"
activate_workflow "$VAULT_ID" "WF-04 VAULT"
activate_workflow "$ORCHESTRATOR_ID" "WF-05 Orchestrator"
echo ""

# Verify activation
echo "Verification:"
echo "-------------"
check_workflow "$VAULT_ID" "WF-04 VAULT"
check_workflow "$ORCHESTRATOR_ID" "WF-05 Orchestrator"
echo ""

echo "=========================================="
echo "Activation Complete!"
echo "=========================================="
echo ""
echo "VAULT webhook endpoint: $N8N_HOST/webhook/budget-check"
echo "Orchestrator: Scheduled for daily 7:00 AM AEST"
echo ""
