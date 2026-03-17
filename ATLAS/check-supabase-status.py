#!/usr/bin/env python3
"""
Quick Supabase Status Checker for ATLAS
Run this anytime to see current database state
"""

from supabase import create_client
import json

SUPABASE_URL = "https://yozmayslzckaczdfohll.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inlvem1heXNsemNrYWN6ZGZvaGxsIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MzY5ODM1MCwiZXhwIjoyMDg5Mjc0MzUwfQ.JV5UqyoWsUNDFKASZucbwpZRoedcYoqT87_oUNN2J68"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("\n" + "=" * 60)
print("ATLAS SUPABASE STATUS CHECK")
print("=" * 60)

# Budget Summary
print("\n💰 BUDGET STATUS:")
budget = supabase.table('atlas_budget_summary').select("*").execute()
if budget.data:
    b = budget.data[0]
    print(f"  Month: {b['month_key']}")
    print(f"  Balance: ${b['current_balance']} / ${b['total_deposited']}")
    print(f"  Spent: ${b['total_spent']}")
    print(f"  Revenue: ${b['total_revenue']}")
    print(f"  Transactions: {b['transaction_count']}")
else:
    print("  ⚠️  No budget record found!")

# Opportunities
print("\n🎯 OPPORTUNITIES:")
opps = supabase.table('atlas_opportunities').select("*").execute()
print(f"  Total: {len(opps.data)}")
if opps.data:
    for opp in opps.data[:5]:  # Show first 5
        print(f"  - [{opp['status']}] {opp['title'][:50]}...")
        print(f"    Source: {opp['source']} | Score: {opp.get('sonnet_score', 'N/A')}")

# Experiments
print("\n🧪 EXPERIMENTS:")
exps = supabase.table('atlas_experiments').select("*").execute()
print(f"  Total: {len(exps.data)}")
if exps.data:
    for exp in exps.data[:3]:
        print(f"  - [{exp.get('status', 'unknown')}] {exp.get('title', 'Untitled')}")
        print(f"    Budget: ${exp.get('allocated_budget', 0)} | Spent: ${exp.get('actual_spend', 0)}")

# Briefings
print("\n📋 BRIEFINGS:")
briefings = supabase.table('atlas_briefings').select("*").execute()
print(f"  Total: {len(briefings.data)}")
if briefings.data:
    for b in briefings.data[:3]:
        print(f"  - {b.get('briefing_date', 'N/A')}: {b.get('summary', 'No summary')[:60]}...")

# Agent Logs (last 5)
print("\n🤖 RECENT AGENT ACTIVITY:")
logs = supabase.table('atlas_agent_logs').select("*").order('created_at', desc=True).limit(5).execute()
print(f"  Total logs: {len(logs.data)}")
if logs.data:
    for log in logs.data:
        print(f"  - [{log.get('agent_name', 'unknown')}] {log.get('event_type', 'N/A')}")
        print(f"    {log.get('message', 'No message')[:80]}")
else:
    print("  ℹ️  No agent activity yet")

print("\n" + "=" * 60)
print("✅ Status check complete")
print("=" * 60 + "\n")
