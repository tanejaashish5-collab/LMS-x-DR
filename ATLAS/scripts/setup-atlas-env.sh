#!/bin/bash
# ATLAS Complete Environment Setup Master Script
# Runs all configuration steps in sequence

set -e

SCRIPT_DIR="/Users/ashishtaneja/Desktop/Business Opp/ATLAS/scripts"

echo "=========================================="
echo "ATLAS Complete Environment Setup"
echo "=========================================="
echo ""
echo "This script will:"
echo "1. Configure n8n credentials"
echo "2. Activate critical workflows"
echo "3. Test VAULT webhook"
echo "4. Test Orchestrator trigger"
echo ""
read -p "Press Enter to continue or Ctrl+C to cancel..."
echo ""

# Step 1: Configure credentials
echo "STEP 1: Configuring n8n credentials..."
echo "======================================="
bash "$SCRIPT_DIR/configure-n8n-env.sh"
echo ""
read -p "Press Enter to continue to workflow activation..."
echo ""

# Step 2: Activate workflows
echo "STEP 2: Activating critical workflows..."
echo "========================================="
bash "$SCRIPT_DIR/activate-workflows.sh"
echo ""
read -p "Press Enter to continue to VAULT testing..."
echo ""

# Step 3: Test VAULT
echo "STEP 3: Testing VAULT webhook..."
echo "================================="
bash "$SCRIPT_DIR/test-vault-webhook.sh"
echo ""
read -p "Press Enter to continue to Orchestrator testing..."
echo ""

# Step 4: Test Orchestrator
echo "STEP 4: Testing Orchestrator..."
echo "================================"
bash "$SCRIPT_DIR/test-orchestrator.sh"
echo ""

# Final status
echo "=========================================="
echo "ATLAS Environment Setup Complete!"
echo "=========================================="
echo ""
echo "System Status:"
echo "  ✓ n8n running at http://localhost:5678"
echo "  ✓ Credentials configured"
echo "  ✓ Critical workflows activated"
echo "  ✓ VAULT webhook tested"
echo "  ✓ Orchestrator verified"
echo ""
echo "Next Steps:"
echo "1. Open n8n UI: http://localhost:5678"
echo "2. Verify workflow executions in the Executions tab"
echo "3. Check Supabase tables for logged data"
echo "4. Review VAULT webhook responses above"
echo ""
echo "Key Endpoints:"
echo "  VAULT:        http://localhost:5678/webhook/budget-check"
echo "  FORGE:        http://localhost:5678/webhook/forge-builder"
echo "  Orchestrator: Runs daily at 7:00 AM AEST"
echo ""
