#!/usr/bin/env python3
"""
Test FORGE Agent
Tests landing page builder without deploying
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.forge import FORGEAgent, LandingPageRequest
from agents.vault import VAULTAgent


def main():
    print("=" * 70)
    print(" FORGE AGENT TEST")
    print("=" * 70)

    # Initialize VAULT (for budget checking)
    print("\n[1/4] Initializing VAULT...")
    vault = VAULTAgent()

    # Initialize FORGE with VAULT integration
    print("[2/4] Initializing FORGE...")
    forge = FORGEAgent(vault_agent=vault)

    # Get current stats
    print("\n[3/4] Current Build Stats:")
    stats = forge.get_build_stats()
    if 'error' not in stats:
        print(f"   Total Builds: {stats['total_builds']}")
        print(f"   Total Cost: ${stats['total_cost']:.2f}")
        print(f"   Average Cost: ${stats['average_cost']:.2f} per page")
        print(f"   Active Pages: {stats['active_pages']}")
    else:
        print(f"   Error: {stats['error']}")

    # Test HTML generation only (no deployment)
    print("\n[4/4] Testing HTML Generation:")
    print("   NOTE: This tests HTML generation without deploying")
    print("   Actual deployment requires: forge.build_landing_page()")

    test_request = LandingPageRequest(
        experiment_id="exp-test-001",
        opportunity_title="Automated Invoice Processing for Law Firms",
        target_vertical="Legal Services",
        value_proposition="Save 10+ hours per week on manual invoice entry and reconciliation with AI-powered automation",
        cta_text="Book a Free Demo",
        cta_action="https://calendly.com/ashishtaneja"
    )

    print(f"\n   Test Opportunity:")
    print(f"   - Title: {test_request.opportunity_title}")
    print(f"   - Vertical: {test_request.target_vertical}")
    print(f"   - Value Prop: {test_request.value_proposition}")
    print(f"   - CTA: {test_request.cta_text} → {test_request.cta_action}")

    # Show how to build a page
    print("\n" + "=" * 70)
    print(" FORGE READY")
    print("=" * 70)
    print("\n To build a landing page:")
    print(" 1. Create a LandingPageRequest with experiment details")
    print(" 2. Call forge.build_landing_page(request)")
    print(" 3. FORGE will:")
    print("    - Request budget from VAULT (~$2.00)")
    print("    - Generate HTML with Claude Sonnet")
    print("    - Deploy to Vercel automatically")
    print("    - Update experiment in database")
    print("    - Return deployed URL")
    print("\n Example:")
    print("   result = forge.build_landing_page(test_request)")
    print("   print(f'Deployed to: {result.vercel_url}')")
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
