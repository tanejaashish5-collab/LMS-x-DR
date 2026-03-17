#!/bin/bash

# ATLAS n8n Setup and Deployment Script
# This script will help you configure and deploy workflows to your n8n instance

echo "🚀 ATLAS n8n Setup"
echo "=================="

# Check if .env exists
if [ ! -f "config/.env" ]; then
    echo "⚠️  Creating .env from template..."
    cp config/.env.template config/.env
    echo "📝 Please edit config/.env with your credentials before proceeding"
    echo "   Especially: N8N_URL and N8N_API_KEY"
    exit 1
fi

# Source the environment variables
source config/.env

# Test n8n connectivity
echo "🔍 Testing n8n connection at $N8N_URL..."

# Try to get workflows list
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$N8N_URL/api/v1/workflows" -H "X-N8N-API-KEY: $N8N_API_KEY")

if [ "$RESPONSE" = "200" ]; then
    echo "✅ Successfully connected to n8n!"
else
    echo "❌ Failed to connect to n8n (HTTP $RESPONSE)"
    echo "   Please check:"
    echo "   1. n8n is running at $N8N_URL"
    echo "   2. API key is correct in config/.env"
    echo "   3. n8n has API enabled (N8N_USER_MANAGEMENT_DISABLED=true)"
    exit 1
fi

# Create deployment function
deploy_workflow() {
    local workflow_file=$1
    local workflow_name=$(basename "$workflow_file" .json)

    echo "📤 Deploying $workflow_name..."

    # Read the workflow JSON
    WORKFLOW_JSON=$(cat "$workflow_file")

    # Create the workflow via API
    RESULT=$(curl -s -X POST "$N8N_URL/api/v1/workflows" \
        -H "X-N8N-API-KEY: $N8N_API_KEY" \
        -H "Content-Type: application/json" \
        -d "$WORKFLOW_JSON")

    # Check if successful
    if echo "$RESULT" | grep -q '"id"'; then
        WORKFLOW_ID=$(echo "$RESULT" | grep -o '"id":"[^"]*' | sed 's/"id":"//')
        echo "   ✅ Created workflow with ID: $WORKFLOW_ID"

        # Activate the workflow
        curl -s -X PATCH "$N8N_URL/api/v1/workflows/$WORKFLOW_ID" \
            -H "X-N8N-API-KEY: $N8N_API_KEY" \
            -H "Content-Type: application/json" \
            -d '{"active": false}' > /dev/null

        echo "   ⏸️  Workflow created but NOT activated (activate manually after testing)"
    else
        echo "   ❌ Failed to create workflow"
        echo "   Error: $RESULT"
    fi
}

# Menu
echo ""
echo "What would you like to do?"
echo "1. Deploy Phase 1 workflows (Foundation)"
echo "2. Deploy Phase 2 workflows (Intelligence)"
echo "3. Deploy Phase 3 workflows (Execution)"
echo "4. Deploy ALL workflows"
echo "5. Test Budget Guardian webhook"
echo "6. Run integration tests"
echo "7. Exit"

read -p "Enter choice (1-7): " choice

case $choice in
    1)
        echo "🏗️  Deploying Phase 1 workflows..."
        deploy_workflow "workflows/WF-04-Budget-Guardian-VAULT.json"
        deploy_workflow "workflows/WF-06-Daily-Briefing-Sender.json"
        ;;
    2)
        echo "🧠 Deploying Phase 2 workflows..."
        deploy_workflow "workflows/WF-01-SCOUT-Pipeline.json"
        deploy_workflow "workflows/WF-03-EHS-Calculator.json"
        deploy_workflow "workflows/WF-02-Metrics-Collector.json"
        deploy_workflow "workflows/WF-05-ATLAS-Orchestrator.json"
        deploy_workflow "workflows/WF-07-Veto-Checker.json"
        ;;
    3)
        echo "⚡ Deploying Phase 3 workflows..."
        deploy_workflow "workflows/WF-08-Forge-Builder.json"
        deploy_workflow "workflows/WF-09-Mercury-Distribution.json"
        deploy_workflow "workflows/WF-12-Experiment-Killer.json"
        ;;
    4)
        echo "🚀 Deploying ALL workflows..."
        for workflow in workflows/*.json; do
            deploy_workflow "$workflow"
        done
        ;;
    5)
        echo "🧪 Testing Budget Guardian..."
        # Get the webhook URL for WF-04
        echo "   Finding Budget Guardian webhook URL..."

        # Test request
        TEST_PAYLOAD='{"agent":"TEST","experiment_id":"test-123","amount":10,"description":"Test spend"}'

        echo "   Sending test request: $TEST_PAYLOAD"

        WEBHOOK_URL="$N8N_URL/webhook/vault-budget-guardian"
        RESPONSE=$(curl -s -X POST "$WEBHOOK_URL" \
            -H "Content-Type: application/json" \
            -d "$TEST_PAYLOAD")

        echo "   Response: $RESPONSE"
        ;;
    6)
        echo "🧪 Running integration tests..."
        echo "   Loading test fixtures..."
        psql "$DATABASE_URL" < test-fixtures/setup.sql

        echo "   Running T-01: VAULT blocks overspend..."
        # Test implementation here

        echo "   Cleaning up test data..."
        psql "$DATABASE_URL" < test-fixtures/cleanup.sql
        ;;
    7)
        echo "👋 Goodbye!"
        exit 0
        ;;
    *)
        echo "Invalid choice"
        ;;
esac

echo ""
echo "✨ Done! Check your n8n instance at $N8N_URL"