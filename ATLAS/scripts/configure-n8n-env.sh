#!/bin/bash
# ATLAS n8n Environment Configuration Script
# Configures all required environment variables and credentials in n8n

set -e

echo "=========================================="
echo "ATLAS n8n Environment Configuration"
echo "=========================================="
echo ""

# Load environment variables from .env file
if [ -f "/Users/ashishtaneja/Desktop/Business Opp/ATLAS/config/.env" ]; then
    export $(cat "/Users/ashishtaneja/Desktop/Business Opp/ATLAS/config/.env" | grep -v '^#' | xargs)
    echo "✓ Loaded environment variables from .env file"
else
    echo "✗ Error: .env file not found"
    exit 1
fi

# n8n API Configuration
N8N_HOST="http://localhost:5678"
N8N_API_KEY="${N8N_API_KEY}"

echo ""
echo "Target n8n instance: $N8N_HOST"
echo ""

# Function to create or update credential
create_credential() {
    local cred_name="$1"
    local cred_type="$2"
    local cred_data="$3"

    echo "Setting up credential: $cred_name ($cred_type)..."

    # Try to create the credential
    response=$(curl -s -w "\n%{http_code}" -X POST "$N8N_HOST/api/v1/credentials" \
        -H "X-N8N-API-KEY: $N8N_API_KEY" \
        -H "Content-Type: application/json" \
        -d "{
            \"name\": \"$cred_name\",
            \"type\": \"$cred_type\",
            \"data\": $cred_data
        }")

    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    if [ "$http_code" -eq 201 ] || [ "$http_code" -eq 200 ]; then
        echo "  ✓ Created successfully"
    else
        echo "  ℹ Already exists or failed (code: $http_code)"
    fi
}

# Configure Anthropic API
echo ""
echo "1. Configuring Anthropic (Claude API)..."
create_credential "ATLAS Claude API" "anthropicApi" "{
    \"apiKey\": \"$ANTHROPIC_API_KEY\"
}"

# Configure Supabase
echo ""
echo "2. Configuring Supabase..."
create_credential "ATLAS Supabase" "supabaseApi" "{
    \"host\": \"$SUPABASE_URL\",
    \"serviceRole\": \"$SUPABASE_SERVICE_ROLE_KEY\"
}"

# Configure Notion
echo ""
echo "3. Configuring Notion..."
create_credential "ATLAS Notion" "notionApi" "{
    \"apiKey\": \"$NOTION_INTEGRATION_TOKEN\"
}"

# Configure Vercel (Generic HTTP Header Auth)
echo ""
echo "4. Configuring Vercel API..."
create_credential "ATLAS Vercel" "httpHeaderAuth" "{
    \"name\": \"Authorization\",
    \"value\": \"Bearer $VERCEL_API_TOKEN\"
}"

# Configure Apify
echo ""
echo "5. Configuring Apify..."
create_credential "ATLAS Apify" "apifyApi" "{
    \"apiKey\": \"$APIFY_API_TOKEN\"
}"

echo ""
echo "=========================================="
echo "Credential Configuration Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Verify credentials in n8n UI at http://localhost:5678/credentials"
echo "2. Activate workflows WF-04 (VAULT) and WF-05 (Orchestrator)"
echo "3. Test VAULT webhook endpoint"
echo ""
