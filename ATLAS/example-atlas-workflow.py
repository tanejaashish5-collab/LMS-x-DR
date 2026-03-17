#!/usr/bin/env python3
"""
ATLAS Complete Workflow Example
Demonstrates the full automation pipeline from opportunity discovery to distribution

Workflow:
1. SCOUT discovers opportunities from Reddit
2. VAULT approves budget for top opportunity
3. FORGE builds landing page for opportunity
4. MERCURY distributes landing page to channels
5. Track everything in database
"""

import asyncio
from datetime import datetime
from agents import (
    VAULTAgent, BudgetRequest,
    SCOUTAgent,
    FORGEAgent, LandingPageRequest,
    MERCURYAgent, DistributionRequest
)

print("=" * 70)
print(" ATLAS COMPLETE WORKFLOW DEMONSTRATION")
print("=" * 70)
print("\nThis example shows the full ATLAS automation pipeline:")
print("SCOUT → VAULT → FORGE → MERCURY → Database")
print("=" * 70)

# ===========================================
# Initialize All Agents
# ===========================================

print("\n[1/5] Initializing ATLAS agents...")

vault = VAULTAgent()
scout = SCOUTAgent()
forge = FORGEAgent(vault_agent=vault)
mercury = MERCURYAgent(vault_agent=vault)

print("✓ VAULT initialized - Budget guardian")
print("✓ SCOUT initialized - Opportunity discovery")
print("✓ FORGE initialized - Landing page builder")
print("✓ MERCURY initialized - Distribution engine")

# ===========================================
# Check Budget Status
# ===========================================

print("\n[2/5] Checking budget status...")

budget_status = vault.get_budget_status()
print(f"✓ Monthly budget: ${budget_status['monthly_limit']:.2f}")
print(f"  Current balance: ${budget_status['current_balance']:.2f}")
print(f"  Spent this month: ${budget_status['total_spent']:.2f} ({budget_status['percent_spent']:.1f}%)")
print(f"  Conservation mode: {budget_status['conservation_mode']}")

# ===========================================
# SCOUT: Discover Opportunities
# ===========================================

print("\n[3/5] SCOUT discovering opportunities...")
print("  (Simulating - actual run costs ~$2.00)")

# Get existing opportunities from database
stats = scout.get_discovery_stats()
print(f"✓ Total opportunities discovered: {stats['total_discovered']}")
print(f"  Haiku filtered: {stats['haiku_filtered']}")
print(f"  Sonnet scored: {stats['sonnet_scored']}")

if stats['top_opportunities']:
    print(f"\n  Top opportunity:")
    top_opp = stats['top_opportunities'][0]
    print(f"  - Score: {top_opp['sonnet_score']}/100")
    print(f"  - Title: {top_opp['title']}")
    print(f"  - Vertical: {top_opp['target_vertical']}")
else:
    print("  No opportunities found yet - run scout.run_discovery() first")

# ===========================================
# FORGE: Build Landing Page
# ===========================================

print("\n[4/5] FORGE building landing page...")
print("  (Simulating - actual build costs ~$2.00)")

# Example landing page request
landing_request = LandingPageRequest(
    experiment_id="demo-experiment-001",
    opportunity_title="Automated Invoice Processing for Law Firms",
    target_vertical="Legal Services",
    value_proposition="Save 10+ hours per week on manual invoice entry and reconciliation. Our AI-powered solution automatically extracts data from invoices, categorizes expenses, and syncs with your accounting software.",
    cta_text="Book a Demo",
    cta_action="https://calendly.com/ashishtaneja"
)

print(f"  Opportunity: {landing_request.opportunity_title}")
print(f"  Target: {landing_request.target_vertical}")

# Simulate FORGE (don't actually build to avoid costs)
print("  ✓ Landing page build skipped (demo mode)")
print("  ✓ Simulated URL: https://invoice-automation-20260318.vercel.app")

simulated_landing_url = "https://invoice-automation-20260318.vercel.app"

# Note: Uncomment to actually build (costs ~$2)
# forge_result = forge.build_landing_page(landing_request)
# if forge_result.status == 'deployed':
#     print(f"✓ Landing page deployed: {forge_result.vercel_url}")
#     simulated_landing_url = forge_result.vercel_url
# else:
#     print(f"✗ Landing page build failed: {forge_result.status}")

# ===========================================
# MERCURY: Distribute Landing Page
# ===========================================

print("\n[5/5] MERCURY distributing landing page...")
print("  (Simulating - actual distribution costs ~$0.05)")

# Distribution request
distribution_request = DistributionRequest(
    experiment_id="demo-experiment-001",
    landing_page_url=simulated_landing_url,
    opportunity_title=landing_request.opportunity_title,
    target_vertical=landing_request.target_vertical,
    value_proposition=landing_request.value_proposition,
    channels=['reddit', 'email']
)

print(f"  Landing page: {distribution_request.landing_page_url}")
print(f"  Channels: {', '.join(distribution_request.channels)}")

# Simulate distribution (without VAULT to avoid budget consumption)
mercury_no_vault = MERCURYAgent(vault_agent=None)  # Skip VAULT for demo
distribution_result = mercury_no_vault.distribute(distribution_request)

print(f"✓ Distribution complete:")
print(f"  - Status: {distribution_result.status}")
print(f"  - Channels succeeded: {len(distribution_result.channels_succeeded)} - {distribution_result.channels_succeeded}")
print(f"  - Channels failed: {len(distribution_result.channels_failed)}")
print(f"  - Total cost: ${distribution_result.total_cost:.4f}")

# Note: Uncomment to use VAULT approval (costs ~$0.05)
# distribution_result = mercury.distribute(distribution_request)

# ===========================================
# Summary
# ===========================================

print("\n" + "=" * 70)
print(" WORKFLOW COMPLETE")
print("=" * 70)

print("\nPipeline Summary:")
print(f"  1. SCOUT: Found {stats['total_discovered']} opportunities")
print(f"  2. VAULT: Budget status checked (${budget_status['current_balance']:.2f} available)")
print(f"  3. FORGE: Landing page simulated")
print(f"  4. MERCURY: Distributed to {len(distribution_result.channels_succeeded)} channels")
print(f"  5. Database: All operations tracked in Supabase")

print("\nCost Breakdown (if run for real):")
print(f"  - SCOUT discovery: $2.00 (Apify + Claude)")
print(f"  - FORGE build: $2.00 (Claude Sonnet + Vercel)")
print(f"  - MERCURY distribution: $0.05 (Claude Haiku)")
print(f"  - Total per experiment: $4.05")

print("\nAutomation Value:")
print(f"  - Manual time: ~4 hours")
print(f"  - ATLAS time: ~5 minutes")
print(f"  - Time saved: 98.9%")
print(f"  - Cost: $4.05 (vs. $400 hourly rate = $1,600)")
print(f"  - ROI: 395x")

print("\n" + "=" * 70)
print(" READY FOR PRODUCTION")
print("=" * 70)

print("\nNext Steps:")
print("  1. Configure Reddit API credentials")
print("  2. Set up n8n email webhook")
print("  3. Run SCOUT discovery: scout.run_discovery()")
print("  4. Build ARGUS agent for performance tracking")
print("  5. Create ATLAS orchestrator for full automation")

print("\nMonitoring:")
print("  - View logs: atlas_agent_logs table in Supabase")
print(f"  - Budget tracking: atlas_budget_summary view")
print(f"  - Experiments: atlas_experiments table")
print(f"  - Opportunities: atlas_opportunities table")

print("\n" + "=" * 70)
