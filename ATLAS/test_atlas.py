#!/usr/bin/env python3
"""
ATLAS System Test Script
Tests all major components to verify system is operational
"""

import requests
import json
import sys
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_system_info():
    """Test root endpoint"""
    print("Testing system info...")
    response = requests.get(f"{BASE_URL}/")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ System: {data['system']}")
        print(f"   Version: {data['version']}")
        print(f"   Status: {data['status']}")
        print(f"   Agents: {', '.join(data['agents'])}")
        return True
    else:
        print(f"❌ System info failed: {response.status_code}")
        return False

def test_status():
    """Test status endpoint"""
    print("\nTesting status endpoint...")
    response = requests.get(f"{BASE_URL}/api/status")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Status: {data['status']}")
        print(f"   Budget Balance: ${data['budget']['current_balance']:.2f}")
        print(f"   Active Experiments: {data['active_experiments']}")
        print(f"   Agents Ready: {len([a for a in data['agents'].values() if a == 'ready'])}/4")
        return True
    else:
        print(f"❌ Status check failed: {response.status_code}")
        return False

def test_budget_check():
    """Test budget webhook (without real experiment)"""
    print("\nTesting budget check (will fail on purpose)...")
    payload = {
        "amount": 5.00,
        "agent": "scout",
        "description": "Test budget check"
    }

    response = requests.post(f"{BASE_URL}/webhook/budget-check", json=payload)
    # We expect this to fail due to missing experiment, but it tests the endpoint
    if response.status_code in [403, 422, 400]:
        print(f"✅ Budget endpoint working (expected rejection)")
        return True
    elif response.status_code == 200:
        print(f"✅ Budget check approved")
        return True
    else:
        print(f"❌ Budget check failed unexpectedly: {response.status_code}")
        return False

def test_discovery_trigger():
    """Test discovery trigger (background task)"""
    print("\nTesting discovery trigger...")
    response = requests.post(f"{BASE_URL}/api/discover")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Discovery triggered: {data['status']}")
        return True
    else:
        print(f"❌ Discovery trigger failed: {response.status_code}")
        return False

def main():
    print("=" * 60)
    print(" ATLAS SYSTEM TEST")
    print(f" {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Check if server is running
    try:
        requests.get(BASE_URL, timeout=2)
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: ATLAS is not running!")
        print("   Please run: ./start_atlas.sh")
        sys.exit(1)

    # Run tests
    tests = [
        test_system_info,
        test_status,
        test_budget_check,
        # test_discovery_trigger  # Commented out to avoid triggering real discovery
    ]

    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            results.append(False)

    # Summary
    print("\n" + "=" * 60)
    passed = sum(1 for r in results if r)
    total = len(results)

    if passed == total:
        print(f"✅ ALL TESTS PASSED ({passed}/{total})")
    else:
        print(f"⚠️  SOME TESTS FAILED ({passed}/{total})")

    print("=" * 60)

    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())