# ATLAS Notion Dashboard Setup Guide

## Structure to Create in Notion

Create the following page hierarchy in your Notion workspace:

```
📊 ATLAS Dashboard (Main Page)
├── 📅 Daily Briefings (Database)
├── 🧪 Active Experiments (Database)
├── 📈 Weekly P&L Reports (Database)
└── 🎯 Opportunity Pipeline (Database)
```

## 1. ATLAS Dashboard (Main Page)

Create a new page called "ATLAS Dashboard" with:
- **Gallery View**: Active Experiments (filtered by status = 'live' or 'measuring')
- **Calendar View**: Daily Briefings
- **Board View**: Opportunity Pipeline (grouped by status)
- **Summary Stats**: Total experiments, current budget, monthly revenue

## 2. Daily Briefings Database

Properties:
- **Date** (Date) - Primary, unique per day
- **Summary** (Text) - Brief overview of the day
- **Decisions** (Multi-select) - kill, scale, launch, maintain
- **Veto Status** (Select) - pending, approved, vetoed, overridden
- **Portfolio Status** (Text) - JSON of current state
- **Actions Taken** (Text) - What ATLAS did
- **User Response** (Text) - Any VETO/OVERRIDE message

Views:
- **This Week**: Filter by Date >= start of week
- **Pending Veto**: Filter by Veto Status = pending
- **Calendar**: Calendar view by Date

## 3. Active Experiments Database

Properties:
- **Name** (Title) - Experiment name
- **Status** (Select) - approved, building, live, measuring, scaled, killed
- **EHS** (Number) - Current Experiment Health Score (0-100)
- **Budget Allocated** (Currency) - Total budget for this experiment
- **Budget Spent** (Currency) - Amount spent so far
- **Revenue** (Currency) - Total revenue generated
- **ROI** (Formula) - (Revenue - Budget Spent) / Budget Spent * 100
- **URL** (URL) - Vercel deployment URL
- **Launched** (Date) - When it went live
- **Days Live** (Formula) - Today - Launched
- **Target Vertical** (Select) - Review Autopilot, Client Intake, etc.

Views:
- **Active Only**: Filter by Status in (live, measuring, scaled)
- **High Performers**: Filter by EHS > 60
- **Kill Candidates**: Filter by EHS < 30
- **Board by Status**: Kanban board grouped by Status

## 4. Weekly P&L Reports Database

Properties:
- **Week** (Title) - Week of [Date]
- **Period Start** (Date)
- **Period End** (Date)
- **Total Revenue** (Currency)
- **Total Spend** (Currency)
- **Net Profit** (Currency)
- **Active Experiments** (Number)
- **Experiments Killed** (Number)
- **Experiments Launched** (Number)
- **Strategic Analysis** (Text) - Sonnet's weekly analysis
- **Recommendations** (Text) - Next week's focus

Views:
- **Timeline**: Timeline view by Period Start
- **Profitable Weeks**: Filter by Net Profit > 0
- **Monthly Roll-up**: Grouped by month

## 5. Opportunity Pipeline Database

Properties:
- **Title** (Title) - Opportunity name
- **Source** (Select) - Reddit, LinkedIn, ProductHunt, Google Trends
- **Source URL** (URL) - Link to original post/page
- **Vertical** (Select) - Which of the 12 target verticals
- **Status** (Select) - discovered, haiku_filtered, sonnet_scored, atlas_approved, building
- **Haiku Pass** (Checkbox) - Did it pass initial filter?
- **Sonnet Score** (Number) - 0-100 scoring
- **Competition Level** (Select) - none, low, moderate, high, saturated
- **Buildability** (Number) - 1-10 score
- **Market Size** (Number) - 1-10 score
- **Claude Analysis** (Text) - Full AI analysis
- **Discovered** (Date) - When SCOUT found it

Views:
- **High Scores**: Filter by Sonnet Score > 70
- **This Week's Finds**: Filter by Discovered >= start of week
- **By Vertical**: Board view grouped by Vertical
- **Approved Only**: Filter by Status = atlas_approved

## Setup Instructions

1. **Create Main Page**:
   - New page → Title: "ATLAS Dashboard"
   - Add icon: 📊

2. **Create Each Database**:
   - Type `/database` → "Inline database"
   - Add properties as listed above
   - Create views as specified

3. **Link to Main Dashboard**:
   - Use `/linked` to embed database views on main page
   - Arrange in a grid layout

4. **Share with Integration**:
   - Settings → Connections → Add connection
   - Search for your ATLAS integration
   - Give edit access to all databases

5. **Get Database IDs**:
   - Open each database as full page
   - Copy ID from URL: notion.so/workspace/[DATABASE_ID]
   - Add to your .env file

## Automation Rules (Optional)

If you have Notion automations available:
- When Daily Briefing added → Send Slack notification
- When Experiment EHS < 20 → Add "🚨 At Risk" tag
- When Weekly P&L Net Profit > $1000 → Add "🎯 Goal Met" tag

## Color Coding

Use these colors for visual clarity:
- 🟢 Green: EHS > 60, Status = scaled, ROI > 100%
- 🟡 Yellow: EHS 30-60, Status = measuring
- 🔴 Red: EHS < 30, Status = killed, Budget Spent > Budget Allocated
- 🔵 Blue: Status = building, newly discovered
- 🟣 Purple: High potential (Sonnet Score > 80)