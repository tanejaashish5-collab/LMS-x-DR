#!/bin/bash
# ATLAS VAULT Webhook Test Script
# Tests the budget guardian webhook with various scenarios

set -e

echo "=========================================="
echo "ATLAS VAULT Webhook Test Suite"
echo "=========================================="
echo ""

N8N_HOST="http://localhost:5678"
VAULT_WEBHOOK="$N8N_HOST/webhook/budget-check"

echo "Testing endpoint: $VAULT_WEBHOOK"
echo ""

# Test 1: Valid small spend request
echo "Test 1: Valid Small Spend Request ($15)"
echo "----------------------------------------"
response=$(curl -s -w "\n%{http_code}" -X POST "$VAULT_WEBHOOK" \
    -H "Content-Type: application/json" \
    -d '{
        "amount": 15,
        "type": "api_call",
        "experiment_id": "test_exp_001",
        "agent": "SONNET",
        "description": "Claude API calls for opportunity scoring"
    }')

http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

echo "HTTP Status: $http_code"
echo "Response: $body"
echo ""

# Test 2: Large spend request (should trigger warnings)
echo "Test 2: Large Spend Request ($45)"
echo "----------------------------------------"
response=$(curl -s -w "\n%{http_code}" -X POST "$VAULT_WEBHOOK" \
    -H "Content-Type: application/json" \
    -d '{
        "amount": 45,
        "type": "vercel_deployment",
        "experiment_id": "test_exp_002",
        "agent": "FORGE",
        "description": "Vercel hosting for landing page"
    }')

http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

echo "HTTP Status: $http_code"
echo "Response: $body"
echo ""

# Test 3: Spend exceeding experiment cap
echo "Test 3: Experiment Cap Test (same experiment, $45 again)"
echo "--------------------------------------------------------"
response=$(curl -s -w "\n%{http_code}" -X POST "$VAULT_WEBHOOK" \
    -H "Content-Type: application/json" \
    -d '{
        "amount": 45,
        "type": "ad_spend",
        "experiment_id": "test_exp_002",
        "agent": "MERCURY",
        "description": "Reddit ads campaign"
    }')

http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

echo "HTTP Status: $http_code"
echo "Response: $body"
echo ""

# Test 4: Invalid request (missing required fields)
echo "Test 4: Invalid Request (missing fields)"
echo "----------------------------------------"
response=$(curl -s -w "\n%{http_code}" -X POST "$VAULT_WEBHOOK" \
    -H "Content-Type: application/json" \
    -d '{
        "amount": 10,
        "agent": "TEST"
    }')

http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

echo "HTTP Status: $http_code"
echo "Response: $body"
echo ""

# Test 5: Realistic FORGE scenario
echo "Test 5: Realistic FORGE Landing Page Deploy"
echo "-------------------------------------------"
response=$(curl -s -w "\n%{http_code}" -X POST "$VAULT_WEBHOOK" \
    -H "Content-Type: application/json" \
    -d '{
        "amount": 20,
        "type": "vercel_hosting",
        "experiment_id": "exp_plumber_landing",
        "agent": "FORGE",
        "description": "Vercel hosting for plumber booking automation landing page"
    }')

http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

echo "HTTP Status: $http_code"
echo "Response: $body"
echo ""

echo "=========================================="
echo "Test Suite Complete!"
echo "=========================================="
echo ""
echo "Review the responses above to verify VAULT is:"
echo "1. Approving valid requests"
echo "2. Blocking requests exceeding budget caps"
echo "3. Logging all transactions"
echo "4. Updating experiment spend tracking"
echo ""
