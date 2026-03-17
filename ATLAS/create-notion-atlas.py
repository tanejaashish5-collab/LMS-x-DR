#!/usr/bin/env python3
"""
Create ATLAS workspace and databases in Notion
"""

import requests
import json
from datetime import datetime

# Notion API configuration
import os
NOTION_TOKEN = os.getenv("NOTION_INTEGRATION_TOKEN", "YOUR_NOTION_TOKEN")
NOTION_VERSION = "2022-06-28"

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": NOTION_VERSION
}

def create_atlas_page():
    """Create the main ATLAS page"""

    # First, search for existing pages to find a parent
    search_url = "https://api.notion.com/v1/search"
    search_data = {
        "query": "",
        "filter": {
            "property": "object",
            "value": "page"
        },
        "page_size": 1
    }

    response = requests.post(search_url, headers=headers, json=search_data)

    if response.status_code == 200 and response.json().get("results"):
        # Get first page as parent
        parent_id = response.json()["results"][0]["id"]
    else:
        print("Could not find parent page, using workspace root")
        parent_id = None
        return None

    # Create ATLAS main page
    create_url = "https://api.notion.com/v1/pages"
    page_data = {
        "parent": {"type": "page_id", "page_id": parent_id},
        "icon": {"type": "emoji", "emoji": "🚀"},
        "properties": {
            "title": {
                "title": [
                    {
                        "type": "text",
                        "text": {"content": "ATLAS - Autonomous Business System"}
                    }
                ]
            }
        },
        "children": [
            {
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [{
                        "type": "text",
                        "text": {"content": "🤖 ATLAS Agent Swarm Control Center"}
                    }]
                }
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{
                        "type": "text",
                        "text": {"content": f"System activated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Budget: $250/month | Status: LIVE"}
                    }]
                }
            },
            {
                "object": "block",
                "type": "divider",
                "divider": {}
            },
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{
                        "type": "text",
                        "text": {"content": "📊 System Metrics"}
                    }]
                }
            },
            {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{
                        "type": "text",
                        "text": {"content": "Active Experiments: 0"}
                    }]
                }
            },
            {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{
                        "type": "text",
                        "text": {"content": "Monthly Spend: $0 / $250"}
                    }]
                }
            },
            {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{
                        "type": "text",
                        "text": {"content": "Revenue Generated: $0"}
                    }]
                }
            }
        ]
    }

    response = requests.post(create_url, headers=headers, json=page_data)

    if response.status_code == 200:
        page_id = response.json()["id"]
        page_url = response.json()["url"]
        print(f"✅ Created ATLAS main page")
        print(f"   URL: {page_url}")
        print(f"   ID: {page_id}")
        return page_id
    else:
        print(f"❌ Failed to create page: {response.status_code}")
        print(response.text[:500])
        return None

def create_database(parent_id, name, emoji, properties):
    """Create a database in Notion"""

    create_url = "https://api.notion.com/v1/databases"

    db_data = {
        "parent": {"type": "page_id", "page_id": parent_id},
        "title": [
            {
                "type": "text",
                "text": {"content": name}
            }
        ],
        "icon": {"type": "emoji", "emoji": emoji},
        "properties": properties
    }

    response = requests.post(create_url, headers=headers, json=db_data)

    if response.status_code == 200:
        db_id = response.json()["id"]
        db_url = response.json()["url"]
        print(f"✅ Created database: {name}")
        print(f"   URL: {db_url}")
        print(f"   ID: {db_id}")
        return db_id
    else:
        print(f"❌ Failed to create {name}: {response.status_code}")
        print(response.text[:500])
        return None

def main():
    print("🚀 Creating ATLAS Workspace in Notion")
    print("="*60)

    # Create main ATLAS page
    atlas_page_id = create_atlas_page()

    if not atlas_page_id:
        print("\n⚠️  Could not create ATLAS page. Creating databases in workspace root...")
        # Use a search to get any page as parent
        search_response = requests.post(
            "https://api.notion.com/v1/search",
            headers=headers,
            json={"page_size": 1}
        )
        if search_response.status_code == 200 and search_response.json().get("results"):
            atlas_page_id = search_response.json()["results"][0]["id"]

    if not atlas_page_id:
        print("❌ Cannot create databases without a parent page")
        return

    print("\n📦 Creating ATLAS Databases...")

    # 1. Briefings Database
    briefings_props = {
        "Title": {"title": {}},
        "Date": {"date": {}},
        "Type": {
            "select": {
                "options": [
                    {"name": "Daily", "color": "blue"},
                    {"name": "Weekly", "color": "green"},
                    {"name": "Alert", "color": "red"},
                    {"name": "Decision", "color": "purple"}
                ]
            }
        },
        "Status": {
            "select": {
                "options": [
                    {"name": "Sent", "color": "green"},
                    {"name": "Draft", "color": "gray"},
                    {"name": "Scheduled", "color": "yellow"}
                ]
            }
        },
        "Decisions": {"multi_select": {}},
        "Content": {"rich_text": {}}
    }

    briefings_id = create_database(
        atlas_page_id,
        "ATLAS Briefings",
        "📋",
        briefings_props
    )

    # 2. Experiments Database
    experiments_props = {
        "Name": {"title": {}},
        "Status": {
            "select": {
                "options": [
                    {"name": "Active", "color": "green"},
                    {"name": "Paused", "color": "yellow"},
                    {"name": "Killed", "color": "red"},
                    {"name": "Scaled", "color": "purple"},
                    {"name": "Planning", "color": "gray"}
                ]
            }
        },
        "EHS Score": {"number": {"format": "number"}},
        "Total Spend": {"number": {"format": "dollar"}},
        "Total Revenue": {"number": {"format": "dollar"}},
        "ROI": {"formula": {"expression": "if(prop(\"Total Spend\") > 0, (prop(\"Total Revenue\") - prop(\"Total Spend\")) / prop(\"Total Spend\") * 100, 0)"}},
        "Landing Page": {"url": {}},
        "Start Date": {"date": {}},
        "End Date": {"date": {}},
        "Vertical": {
            "select": {
                "options": [
                    {"name": "Review Autopilot", "color": "blue"},
                    {"name": "Client Intake", "color": "green"},
                    {"name": "AR Collections", "color": "orange"},
                    {"name": "Home Services", "color": "purple"},
                    {"name": "AI Bookkeeping", "color": "pink"},
                    {"name": "Legal Ops", "color": "red"},
                    {"name": "Healthcare", "color": "yellow"},
                    {"name": "Real Estate", "color": "brown"},
                    {"name": "E-commerce", "color": "default"},
                    {"name": "SaaS", "color": "gray"}
                ]
            }
        },
        "Kill Reason": {
            "select": {
                "options": [
                    {"name": "GHOST_TOWN", "color": "gray"},
                    {"name": "LEAKY_BUCKET", "color": "blue"},
                    {"name": "BUDGET_BLEED", "color": "red"},
                    {"name": "EHS_FLATLINE", "color": "orange"},
                    {"name": "HARD_DEADLINE", "color": "purple"},
                    {"name": "MANUAL_VETO", "color": "pink"}
                ]
            }
        }
    }

    experiments_id = create_database(
        atlas_page_id,
        "ATLAS Experiments",
        "🧪",
        experiments_props
    )

    # 3. P&L Database
    pnl_props = {
        "Month": {"title": {}},
        "Deposits": {"number": {"format": "dollar"}},
        "Total Spend": {"number": {"format": "dollar"}},
        "Total Revenue": {"number": {"format": "dollar"}},
        "Net Profit": {"formula": {"expression": "prop(\"Total Revenue\") - prop(\"Total Spend\")"}},
        "Profit Margin": {"formula": {"expression": "if(prop(\"Total Revenue\") > 0, prop(\"Net Profit\") / prop(\"Total Revenue\") * 100, 0)"}},
        "Active Experiments": {"number": {"format": "number"}},
        "Successful Conversions": {"number": {"format": "number"}},
        "Notes": {"rich_text": {}}
    }

    pnl_id = create_database(
        atlas_page_id,
        "ATLAS P&L",
        "💰",
        pnl_props
    )

    print("\n" + "="*60)
    print("✅ ATLAS WORKSPACE CREATED!")
    print("\n📝 Database IDs for .env file:")
    print(f"NOTION_WORKSPACE_ID={atlas_page_id}")
    print(f"NOTION_DATABASE_ID_BRIEFINGS={briefings_id}")
    print(f"NOTION_DATABASE_ID_EXPERIMENTS={experiments_id}")
    print(f"NOTION_DATABASE_ID_PNL={pnl_id}")

    # Update .env file
    print("\n📝 Updating .env file...")
    env_file = "/Users/ashishtaneja/Desktop/Business Opp/ATLAS/config/.env"

    with open(env_file, 'r') as f:
        lines = f.readlines()

    # Update the specific lines
    for i, line in enumerate(lines):
        if line.startswith("NOTION_WORKSPACE_ID="):
            lines[i] = f"NOTION_WORKSPACE_ID={atlas_page_id}\n"
        elif line.startswith("NOTION_DATABASE_ID_BRIEFINGS="):
            lines[i] = f"NOTION_DATABASE_ID_BRIEFINGS={briefings_id}\n"
        elif line.startswith("NOTION_DATABASE_ID_EXPERIMENTS="):
            lines[i] = f"NOTION_DATABASE_ID_EXPERIMENTS={experiments_id}\n"
        elif line.startswith("NOTION_DATABASE_ID_PNL="):
            lines[i] = f"NOTION_DATABASE_ID_PNL={pnl_id}\n"

    with open(env_file, 'w') as f:
        f.writelines(lines)

    print("✅ .env file updated with new database IDs")

    print("\n🎉 Your ATLAS Notion workspace is ready!")
    print(f"\n🔗 Open your ATLAS dashboard:")
    print(f"   https://notion.so/{atlas_page_id.replace('-', '')}")

if __name__ == "__main__":
    main()