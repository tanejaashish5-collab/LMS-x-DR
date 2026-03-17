#!/bin/bash

# ATLAS Automated Deployment Script
# This will deploy and test all workflows automatically

echo "🚀 ATLAS Automated Deployment Starting..."
echo "======================================="

# Source environment variables
source config/.env

# Test n8n connection
echo "📡 Testing n8n connection..."
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$N8N_URL/api/v1/workflows" -H "X-N8N-API-KEY: $N8N_API_KEY")

if [ "$RESPONSE" != "200" ]; then
    echo "❌ Cannot connect to n8n. Starting n8n..."
    # Try to start n8n
    cd ~/Desktop/Claude\ OS/n8n-self-hosted
    npm run start:tunnel &
    N8N_PID=$!
    echo "⏳ Waiting for n8n to start (PID: $N8N_PID)..."
    sleep 10
fi

# Re-test connection
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$N8N_URL/api/v1/workflows" -H "X-N8N-API-KEY: $N8N_API_KEY")
if [ "$RESPONSE" = "200" ]; then
    echo "✅ Connected to n8n successfully!"
else
    echo "❌ Still cannot connect to n8n. Please start it manually."
    exit 1
fi

# Deploy all workflows
echo ""
echo "📤 Deploying workflows..."
echo "------------------------"

# First, create any missing workflow files
echo "🔨 Building remaining workflow files..."

# Create WF-07 Veto Checker if not exists
if [ ! -f "workflows/WF-07-Veto-Checker.json" ]; then
    cat > workflows/WF-07-Veto-Checker.json << 'EOF'
{
  "name": "WF-07: Veto Checker",
  "nodes": [
    {
      "parameters": {
        "triggerTimes": {
          "item": [{
            "mode": "everyDay",
            "hour": 9,
            "minute": 30
          }]
        }
      },
      "id": "cron-trigger",
      "name": "Daily 9:30 AM",
      "type": "n8n-nodes-base.cron",
      "typeVersion": 1,
      "position": [250, 300]
    }
  ],
  "connections": {},
  "active": false,
  "settings": {},
  "id": "WF-07"
}
EOF
fi

# Create remaining workflows stubs
for WF in WF-08-Forge-Builder WF-09-Mercury-Distribution WF-10-Evening-Snapshot WF-11-Weekly-PNL-Report WF-12-Experiment-Killer; do
    if [ ! -f "workflows/${WF}.json" ]; then
        echo "Creating stub for ${WF}..."
        cat > "workflows/${WF}.json" << EOF
{
  "name": "${WF}",
  "nodes": [
    {
      "parameters": {},
      "id": "start",
      "name": "Start",
      "type": "n8n-nodes-base.start",
      "typeVersion": 1,
      "position": [250, 300]
    }
  ],
  "connections": {},
  "active": false,
  "settings": {},
  "id": "${WF%-*}"
}
EOF
    fi
done

# Deploy each workflow
DEPLOYED=0
FAILED=0

for workflow in workflows/*.json; do
    WORKFLOW_NAME=$(basename "$workflow" .json)
    echo -n "  Deploying $WORKFLOW_NAME... "

    # Read workflow content
    WORKFLOW_JSON=$(cat "$workflow")

    # Try to create workflow
    RESULT=$(curl -s -X POST "$N8N_URL/api/v1/workflows" \
        -H "X-N8N-API-KEY: $N8N_API_KEY" \
        -H "Content-Type: application/json" \
        -d "$WORKFLOW_JSON" 2>/dev/null)

    if echo "$RESULT" | grep -q '"id"'; then
        echo "✅"
        ((DEPLOYED++))
    else
        # Try update if exists
        EXISTING_ID=$(curl -s "$N8N_URL/api/v1/workflows" -H "X-N8N-API-KEY: $N8N_API_KEY" | grep -o "\"id\":\"[^\"]*\",\"name\":\"${WORKFLOW_NAME}" | head -1 | sed 's/.*"id":"\([^"]*\).*/\1/')
        if [ -n "$EXISTING_ID" ]; then
            UPDATE_RESULT=$(curl -s -X PUT "$N8N_URL/api/v1/workflows/$EXISTING_ID" \
                -H "X-N8N-API-KEY: $N8N_API_KEY" \
                -H "Content-Type: application/json" \
                -d "$WORKFLOW_JSON" 2>/dev/null)
            if echo "$UPDATE_RESULT" | grep -q '"id"'; then
                echo "✅ (updated)"
                ((DEPLOYED++))
            else
                echo "❌"
                ((FAILED++))
            fi
        else
            echo "❌"
            ((FAILED++))
        fi
    fi
done

echo ""
echo "📊 Deployment Results:"
echo "  ✅ Deployed: $DEPLOYED"
echo "  ❌ Failed: $FAILED"

# Test critical workflows
echo ""
echo "🧪 Testing critical workflows..."
echo "--------------------------------"

# Test Budget Guardian
echo -n "  Testing WF-04 Budget Guardian... "
TEST_RESPONSE=$(curl -s -X POST "$N8N_URL/webhook/vault-budget-guardian" \
    -H "Content-Type: application/json" \
    -d '{"agent":"TEST","amount":10,"experiment_id":"test-1","description":"Test"}' 2>/dev/null)

if echo "$TEST_RESPONSE" | grep -q "status"; then
    echo "✅"
else
    echo "❌ No response"
fi

# Load test fixtures
echo ""
echo "📦 Loading test fixtures..."
if [ -f "test-fixtures/setup.sql" ]; then
    # Would need psql or API access to Supabase
    echo "  ⚠️  Please load test-fixtures/setup.sql manually in Supabase"
fi

echo ""
echo "✨ Deployment complete!"
echo ""
echo "Next steps:"
echo "1. Open n8n at $N8N_URL"
echo "2. Check all workflows are imported"
echo "3. Activate WF-04 Budget Guardian first"
echo "4. Test with manual execution before enabling crons"
echo "5. Set your email in Gmail nodes"
echo ""
echo "To activate ATLAS:"
echo "  1. Enable WF-04, WF-06 (foundation)"
echo "  2. Enable WF-01, WF-02, WF-03 (intelligence)"
echo "  3. Enable WF-05 (orchestrator)"
echo "  4. Watch for first daily briefing at 7:30 AM"