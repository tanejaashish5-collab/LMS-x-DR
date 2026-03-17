#!/usr/bin/env python3
"""
ATLAS Supabase Database Initializer
Tests connection, verifies tables, initializes budget, and adds test data
"""

import os
from datetime import datetime
from supabase import create_client, Client

# Supabase credentials
SUPABASE_URL = "https://yozmayslzckaczdfohll.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inlvem1heXNsemNrYWN6ZGZvaGxsIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MzY5ODM1MCwiZXhwIjoyMDg5Mjc0MzUwfQ.JV5UqyoWsUNDFKASZucbwpZRoedcYoqT87_oUNN2J68"

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("=" * 60)
print("ATLAS SUPABASE DATABASE INITIALIZATION")
print("=" * 60)

# Test 1: Connection Test
print("\n[1/5] Testing Supabase connection...")
try:
    # Simple query to test connection
    result = supabase.table('atlas_budget_summary').select("*").limit(1).execute()
    print("✓ Connection successful!")
except Exception as e:
    print(f"✗ Connection failed: {e}")
    exit(1)

# Test 2: Check Tables and Row Counts
print("\n[2/5] Checking tables and row counts...")
tables = [
    'atlas_experiments',
    'atlas_budget_summary',
    'atlas_agent_logs',
    'atlas_briefings',
    'atlas_opportunities'
]

table_status = {}
for table in tables:
    try:
        result = supabase.table(table).select("*", count='exact').execute()
        count = result.count if hasattr(result, 'count') else len(result.data)
        table_status[table] = count
        print(f"  ✓ {table}: {count} rows")
    except Exception as e:
        table_status[table] = f"ERROR: {e}"
        print(f"  ✗ {table}: {e}")

# Test 3: Check Budget Status
print("\n[3/5] Checking budget status...")
try:
    budget_result = supabase.table('atlas_budget_summary').select("*").execute()

    if len(budget_result.data) == 0:
        print("  No budget record found. Initializing with $250...")

        # Initialize budget with correct schema
        budget_data = {
            "month_key": datetime.now().strftime("%Y-%m"),
            "total_deposited": 250.00,
            "total_spent": 0,
            "total_revenue": 0,
            "current_balance": 250.00,
            "transaction_count": 0
        }

        insert_result = supabase.table('atlas_budget_summary').insert(budget_data).execute()
        print(f"  ✓ Budget initialized: ${budget_data['total_deposited']}")
    else:
        budget = budget_result.data[0]
        print(f"  ✓ Current budget found:")
        print(f"    - Month: {budget.get('month_key', 'N/A')}")
        print(f"    - Total Deposited: ${budget.get('total_deposited', 0)}")
        print(f"    - Total Spent: ${budget.get('total_spent', 0)}")
        print(f"    - Total Revenue: ${budget.get('total_revenue', 0)}")
        print(f"    - Current Balance: ${budget.get('current_balance', 0)}")
        print(f"    - Transactions: {budget.get('transaction_count', 0)}")

except Exception as e:
    print(f"  ✗ Budget check failed: {e}")

# Test 4: Check for Test Opportunities
print("\n[4/5] Checking for test opportunities...")
try:
    opp_result = supabase.table('atlas_opportunities').select("*").execute()

    # Filter out the test opportunity we just created to see real ones
    real_opps = [opp for opp in opp_result.data if opp.get('source') != 'test']

    if len(real_opps) == 0:
        print("  No real opportunities found. Creating test opportunity to trigger ATLAS...")

        test_opportunity = {
            "source": "reddit",
            "source_url": "https://reddit.com/r/entrepreneur/test",
            "title": "Need AI automation for lead generation - $500 budget",
            "description": "Small business owner looking for AI workflow automation. Budget: $500. Timeline: 2 weeks. Stack: n8n preferred.",
            "category": "other",
            "target_vertical": "small_business",
            "status": "discovered"
        }

        insert_result = supabase.table('atlas_opportunities').insert(test_opportunity).execute()
        print(f"  ✓ Test opportunity created: {test_opportunity['title']}")
        print(f"    - This should trigger the ATLAS orchestrator workflow")
    else:
        print(f"  ✓ Found {len(real_opps)} existing opportunities:")
        for opp in real_opps[:3]:  # Show first 3
            print(f"    - {opp.get('title', 'Untitled')} [{opp.get('status', 'unknown')}]")

except Exception as e:
    print(f"  ✗ Opportunity check failed: {e}")

# Test 5: Verify Data Accessibility
print("\n[5/5] Verifying data accessibility...")
try:
    # Test reading from multiple tables
    tests = [
        ('atlas_budget_summary', 'budget data'),
        ('atlas_opportunities', 'opportunities'),
        ('atlas_agent_logs', 'agent logs'),
        ('atlas_briefings', 'briefings')
    ]

    for table_name, description in tests:
        result = supabase.table(table_name).select("*").limit(1).execute()
        print(f"  ✓ Can read {description} from {table_name}")

except Exception as e:
    print(f"  ✗ Data accessibility test failed: {e}")

# Final Summary
print("\n" + "=" * 60)
print("INITIALIZATION COMPLETE")
print("=" * 60)
print("\nTable Status:")
for table, status in table_status.items():
    if isinstance(status, int):
        print(f"  {table}: {status} rows")
    else:
        print(f"  {table}: {status}")

print("\nNext Steps:")
print("  1. Verify tables in Supabase dashboard")
print("  2. Check that budget is initialized")
print("  3. Run WF-05-ATLAS-Orchestrator workflow in n8n")
print("  4. Monitor atlas_agent_logs for activity")
print("\n" + "=" * 60)
