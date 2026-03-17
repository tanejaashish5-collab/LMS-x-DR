#!/bin/bash
# ATLAS Orchestrator Test Script
# Manually triggers the orchestrator workflow for testing

set -e

echo "=========================================="
echo "ATLAS Orchestrator Manual Test"
echo "=========================================="
echo ""

# Load environment variables
if [ -f "/Users/ashishtaneja/Desktop/Business Opp/ATLAS/config/.env" ]; then
    export $(cat "/Users/ashishtaneja/Desktop/Business Opp/ATLAS/config/.env" | grep -v '^#' | xargs)
fi

N8N_HOST="http://localhost:5678"
N8N_API_KEY="${N8N_API_KEY}"
ORCHESTRATOR_ID="0J019KTway5tDU7P"

echo "Triggering Orchestrator workflow..."
echo "Workflow ID: $ORCHESTRATOR_ID"
echo ""

# Method 1: Try to execute workflow via API
echo "Method 1: API Execution"
echo "-----------------------"
response=$(curl -s -w "\n%{http_code}" -X POST "$N8N_HOST/api/v1/workflows/$ORCHESTRATOR_ID/execute" \
    -H "X-N8N-API-KEY: $N8N_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{}')

http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" -eq 200 ] || [ "$http_code" -eq 201 ]; then
    echo "✓ Orchestrator triggered successfully"
    echo "Response: $body" | jq '.' 2>/dev/null || echo "$body"
else
    echo "✗ Trigger failed (HTTP $http_code)"
    echo "Response: $body"
    echo ""
    echo "Note: The Orchestrator uses a CRON trigger (daily at 7:00 AM AEST)"
    echo "      Manual execution may not be supported via API."
    echo ""
    echo "Alternative: Wait for scheduled execution or trigger via n8n UI"
fi

echo ""
echo "=========================================="
echo "Orchestrator Test Complete"
echo "=========================================="
echo ""
echo "The Orchestrator workflow performs these actions daily:"
echo "1. Fetches all experiment data from Supabase"
echo "2. Gets budget status and recent opportunities"
echo "3. Reviews agent logs and metrics"
echo "4. Uses Haiku to summarize data"
echo "5. Uses Sonnet to make strategic decisions"
echo "6. Saves briefing to Supabase"
echo "7. Executes approved decisions"
echo ""
echo "To verify operation:"
echo "  - Check Supabase atlas_briefings table for new entries"
echo "  - Monitor n8n execution history at http://localhost:5678/executions"
echo "  - Review atlas_agent_logs for decision outcomes"
echo ""
