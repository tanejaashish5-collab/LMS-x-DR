#!/usr/bin/env python3
"""
Test MERCURY Agent - Distribution Engine
Tests copy generation and distribution simulation
"""

import sys
from agents import MERCURYAgent, DistributionRequest

print("=" * 70)
print(" MERCURY AGENT TEST - Distribution Engine")
print("=" * 70)

# Initialize MERCURY agent (without VAULT for testing)
print("\n[1/4] Initializing MERCURY agent...")
try:
    mercury = MERCURYAgent()
    print("✓ MERCURY agent initialized")
except Exception as e:
    print(f"✗ Failed to initialize MERCURY: {e}")
    sys.exit(1)

# Get current distribution stats
print("\n[2/4] Getting current distribution statistics...")
try:
    stats = mercury.get_distribution_stats()
    if 'error' not in stats:
        print(f"✓ Distribution Stats Retrieved:")
        print(f"  - Total Distributions: {stats['total_distributions']}")
        print(f"  - Total Cost: ${stats['total_cost']:.2f}")
        print(f"  - Average Cost: ${stats['average_cost']:.4f}")
        print(f"  - Channel Breakdown: {stats['channel_counts']}")
    else:
        print(f"✗ Error getting stats: {stats['error']}")
except Exception as e:
    print(f"✗ Failed to get stats: {e}")

# Test copy generation for different channels
print("\n[3/4] Testing copy generation for multiple channels...")
print("  (Testing Claude Haiku API calls - costs ~$0.05 total)\n")

test_request = DistributionRequest(
    experiment_id="test-mercury-001",
    landing_page_url="https://example.com/automated-invoice-processing",
    opportunity_title="Automated Invoice Processing for Law Firms",
    target_vertical="Legal Services",
    value_proposition="Save 10+ hours per week on manual invoice entry and reconciliation. Our AI-powered solution automatically extracts data from invoices, categorizes expenses, and syncs with your accounting software.",
    channels=['reddit', 'email']
)

print(f"  Opportunity: {test_request.opportunity_title}")
print(f"  Target Vertical: {test_request.target_vertical}")
print(f"  Landing Page: {test_request.landing_page_url}")
print(f"  Channels: {', '.join(test_request.channels)}\n")

# Generate copy for each channel
total_cost = 0.0
for channel in test_request.channels:
    print(f"  Generating {channel} copy...")
    try:
        copy_result = mercury._generate_channel_copy(test_request, channel)

        if copy_result['success']:
            copy = copy_result['copy']
            cost = copy_result['cost']
            total_cost += cost

            print(f"  ✓ {channel.upper()} Copy Generated (${cost:.4f}):")
            print(f"    Headline: {copy.headline[:80]}...")
            print(f"    Body: {copy.body[:100]}...")
            print(f"    CTA: {copy.cta}")
            if copy.hashtags:
                print(f"    Hashtags: {', '.join(copy.hashtags)}")
            print()
        else:
            print(f"  ✗ Failed to generate {channel} copy: {copy_result['error']}\n")
    except Exception as e:
        print(f"  ✗ Error generating {channel} copy: {e}\n")

print(f"  Total copy generation cost: ${total_cost:.4f}")

# Test full distribution (simulated)
print("\n[4/4] Testing full distribution pipeline (simulated)...")
print("  (Distribution to Reddit/email will be simulated - no actual posts)")
print()

try:
    # Run distribution WITHOUT VAULT approval (pass vault_agent=None)
    result = mercury.distribute(test_request)

    print(f"✓ Distribution Complete:")
    print(f"  - Status: {result.status}")
    print(f"  - Channels Attempted: {len(result.channels_attempted)}")
    print(f"  - Channels Succeeded: {len(result.channels_succeeded)} - {result.channels_succeeded}")
    print(f"  - Channels Failed: {len(result.channels_failed)}")

    if result.channels_failed:
        print(f"  - Failures:")
        for failure in result.channels_failed:
            print(f"    * {failure['channel']}: {failure['error']}")

    print(f"  - Total Cost: ${result.total_cost:.4f}")

except Exception as e:
    print(f"✗ Distribution failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print(" MERCURY AGENT TEST COMPLETE")
print("=" * 70)
print("\nNEXT STEPS:")
print("1. Configure Reddit API credentials for actual posting")
print("2. Set up n8n email webhook for email distribution")
print("3. Integrate with VAULT for budget approval")
print("4. Add MERCURY to ATLAS orchestrator workflow")
print("\nCONFIGURATION REQUIRED:")
print("  export REDDIT_CLIENT_ID='your_client_id'")
print("  export REDDIT_CLIENT_SECRET='your_client_secret'")
print("  export REDDIT_USERNAME='your_username'")
print("  export REDDIT_PASSWORD='your_password'")
print("  export N8N_EMAIL_WEBHOOK='https://your-n8n-instance.com/webhook/email'")
print("=" * 70)
