#!/usr/bin/env python3
"""
Test script for SCOUT agent
Demonstrates filtering and scoring without needing Apify
"""

from agents import SCOUTAgent, Opportunity

print("=" * 60)
print(" SCOUT Agent - Test Run")
print("=" * 60)

# Initialize SCOUT
scout = SCOUTAgent()

# Create test opportunity
test_opp = Opportunity(
    title="Law firm spending 8 hours weekly on client intake forms",
    source="reddit",
    source_url="https://reddit.com/r/lawfirm/test_demo",
    description="""We are a 5-person law firm and our paralegal spends 8+ hours
    every week manually copying client intake forms from Typeform into our
    practice management system. The data includes contact info, case details,
    and billing information. There must be a better way to automate this!"""
)

print("\n1. Test Opportunity:")
print(f"   Title: {test_opp.title}")
print(f"   Source: {test_opp.source}")

# Test Haiku filtering
print("\n2. Filtering with Claude Haiku...")
filter_result = scout._filter_with_haiku(test_opp)

print(f"   Passed: {filter_result.passed}")
print(f"   Category: {filter_result.category}")
print(f"   Vertical: {filter_result.target_vertical}")
print(f"   Reason: {filter_result.reason}")

if filter_result.passed:
    # Save to database
    print("\n3. Saving to database...")
    saved = scout._save_opportunity(test_opp, filter_result)

    if saved:
        print("   Saved successfully!")

        # Get the saved opportunity
        print("\n4. Retrieving from database...")
        unscored = scout._get_unscored_opportunities(limit=1)

        if unscored:
            opp_data = unscored[0]
            print(f"   Found: {opp_data['title'][:50]}...")

            # Score with Sonnet
            print("\n5. Scoring with Claude Sonnet...")
            score_result = scout._score_with_sonnet(opp_data)

            if score_result:
                print(f"   Overall Score: {score_result.score}/100")
                print(f"   Automation Potential: {score_result.automation_potential}/10")
                print(f"   Market Size: {score_result.market_size}/10")
                print(f"   Pain Level: {score_result.pain_level}/10")
                print(f"   Reasoning: {score_result.reasoning}")

                # Save score
                print("\n6. Saving score...")
                score_saved = scout._save_score(opp_data['id'], score_result)

                if score_saved:
                    print("   Score saved successfully!")
    else:
        print("   Already exists (duplicate)")

# Get final stats
print("\n7. Discovery Statistics:")
stats = scout.get_discovery_stats()
print(f"   Total Discovered: {stats['total_discovered']}")
print(f"   Haiku Filtered: {stats['haiku_filtered']}")
print(f"   Sonnet Scored: {stats['sonnet_scored']}")

if stats['top_opportunities']:
    print("\n   Top Opportunities:")
    for opp in stats['top_opportunities'][:3]:
        score = opp.get('sonnet_score', 0)
        vertical = opp.get('target_vertical', 'Unknown')
        title = opp.get('title', '')[:50]
        print(f"   - [{score}/100] {vertical}: {title}...")

print("\n" + "=" * 60)
print(" SCOUT agent test complete")
print("=" * 60)
