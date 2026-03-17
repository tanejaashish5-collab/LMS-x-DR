# ATLAS Agents

Autonomous agents that power the ATLAS business automation system.

## SCOUT Agent - Opportunity Discovery

### Overview
SCOUT discovers business automation opportunities from Reddit and other sources. It uses Claude Haiku for fast, cheap filtering and Claude Sonnet for deep scoring of top opportunities.

### Schedule
- **Runs**: Mon/Wed/Fri at 5 AM
- **Sources**: Reddit (r/Entrepreneur, r/smallbusiness, r/SaaS, etc.)
- **Max Posts**: 50 per subreddit

### Features

#### 1. Reddit Discovery via Apify
- Scans multiple subreddits for automation pain points
- Search terms: "automation", "manual process", "spending hours", etc.
- Uses Apify Reddit Scraper for reliable data extraction
- Deduplicates by source URL

#### 2. Claude Haiku Filtering (Fast & Cheap)
- Filters opportunities for business viability
- Categorizes: automation_service, template_product, software_product, other
- Identifies target vertical (Legal, Real Estate, Healthcare, etc.)
- Cost: ~$0.02 per 100 opportunities

#### 3. Database Persistence
- Saves qualified opportunities to `atlas_opportunities` table
- Tracks discovery timestamp, source, category, vertical
- Prevents duplicates via URL matching

#### 4. Claude Sonnet Deep Scoring (Top 10)
- Scores automation potential (0-10)
- Estimates market size (0-10)
- Evaluates pain level (0-10)
- Overall score: 0-100 (weighted)
- Cost: ~$0.15 per opportunity

### Usage

#### Standalone Testing
```bash
python3 agents/scout.py
```

#### Import in Python
```python
from agents import SCOUTAgent

# Initialize agent
scout = SCOUTAgent()

# Run discovery (default subreddits, 50 posts each)
result = scout.run_discovery()

print(f"Scanned: {result['scanned']}")
print(f"Filtered: {result['filtered']}")
print(f"Saved: {result['saved']}")
print(f"Scored: {result['scored']}")
```

#### Custom Discovery
```python
# Custom subreddits and limits
result = scout.run_discovery(
    subreddits=['entrepreneur', 'SaaS', 'freelance'],
    max_posts=25
)
```

#### Get Statistics
```python
stats = scout.get_discovery_stats()
print(f"Total discovered: {stats['total_discovered']}")
print(f"Top opportunities: {stats['top_opportunities']}")
```

### Configuration

Default subreddits:
- r/Entrepreneur
- r/smallbusiness
- r/SaaS
- r/consulting
- r/freelance
- r/marketing
- r/sales
- r/accounting
- r/realestate
- r/legaladvice

Search terms:
- "automation"
- "manual process"
- "spending hours"
- "repetitive task"
- "workflow"
- "integration"
- "data entry"

### Database Schema

**atlas_opportunities**
- `id` - UUID primary key
- `title` - Opportunity title (max 200 chars)
- `source` - Source platform ('reddit')
- `source_url` - Original post URL (unique)
- `description` - Full description/context
- `category` - automation_service, template_product, etc.
- `target_vertical` - Business vertical
- `haiku_filter_pass` - Boolean (passed Haiku filter)
- `status` - discovered, haiku_filtered, sonnet_scored
- `sonnet_score` - Overall score (0-100)
- `sonnet_reasoning` - Detailed explanation
- `automation_potential` - Score 0-10
- `market_size` - Score 0-10
- `pain_level` - Score 0-10
- `discovered_at` - Discovery timestamp

### Cost Analysis

Per discovery run (10 subreddits, 50 posts each):
- Reddit scraping via Apify: ~$0.50
- Haiku filtering (100 opportunities): ~$0.02
- Sonnet scoring (top 10): ~$1.50
- **Total per run**: ~$2.00

3 runs per week = ~$6/week = ~$25/month

### Error Handling

SCOUT handles errors gracefully:
- Apify failures → Skip subreddit, continue with others
- Claude API errors → Mark as failed, log to agent_logs
- Database errors → Log error, continue processing
- Duplicate URLs → Skip silently
- All errors logged to `atlas_agent_logs`

### Integration with ATLAS

SCOUT is called by the main ATLAS orchestrator on schedule:

```python
from agents import SCOUTAgent, VAULTAgent, BudgetRequest

class ATLASAgent:
    def __init__(self):
        self.scout = SCOUTAgent()
        self.vault = VAULTAgent()

    def run_scout_discovery(self):
        # Check budget first
        request = BudgetRequest(
            amount=2.00,
            agent='scout',
            description='Mon/Wed/Fri discovery run'
        )

        approval = self.vault.check_budget(request)

        if not approval['approved']:
            logger.error(f"Budget blocked: {approval['reason']}")
            return

        # Run discovery
        result = self.scout.run_discovery()

        return result
```

### Testing

Run the standalone test:
```bash
cd /Users/ashishtaneja/Desktop/Business\ Opp/ATLAS
python3 agents/scout.py
```

Expected output:
```
============================================================
 SCOUT Agent - Opportunity Discovery
============================================================

1. Current Discovery Stats:
   Total Discovered: 15
   Haiku Filtered: 8
   Sonnet Scored: 5

   Top 5 Opportunities:
   - [87/100] Legal Services: Law firm spending 8 hours weekly...
   - [76/100] Real Estate: Manual property listing updates...
   - [68/100] E-commerce: Order processing automation needed...

2. Running Test Discovery (5 posts from r/entrepreneur):
   Status: completed
   Scanned: 5
   Filtered: 2
   Saved: 2
   Scored: 2

============================================================
 SCOUT agent ready for ATLAS orchestrator
============================================================
```

### Troubleshooting

**"Apify API rate limit exceeded"**
- Reduce max_posts per subreddit
- Spread discovery runs across time

**"Claude API error: overloaded_error"**
- Implement retry with exponential backoff
- Reduce batch size

**"Duplicate opportunity: URL already exists"**
- This is expected behavior
- SCOUT automatically deduplicates

**"No opportunities found"**
- Check search terms relevance
- Try different subreddits
- Verify Apify actor is active

### Next Steps

1. Add more data sources (Twitter, LinkedIn, forums)
2. Implement retry logic for API failures
3. Add webhook notifications for high-score opportunities
4. Create dashboard for discovery analytics
5. Fine-tune filtering prompts based on results

---

## VAULT Agent - Budget Guardian

### Overview
VAULT is the budget guardian that controls all spending in the ATLAS system. It enforces monthly budgets, per-experiment limits, and activates conservation mode when needed.

### Configuration
- **Monthly Budget**: $250
- **Per-Experiment Limit**: $50
- **Conservation Threshold**: 80% of monthly budget
- **Minimum Reserve**: $10

### Features

#### 1. Budget Checking
- Validates all spending requests before approval
- Checks against monthly and per-experiment limits
- Maintains minimum reserve balance
- Activates conservation mode at 80% spend

#### 2. Automatic Tracking
- Logs all transactions to `atlas_budget_ledger`
- Updates experiment budgets in `atlas_experiments`
- Records all decisions in `atlas_agent_logs`
- Budget summary auto-updates via database VIEW

#### 3. Conservation Mode
When 80% of monthly budget is spent, VAULT enters conservation mode:
- Only high-priority agents (SONNET, ATLAS, VAULT) can spend
- Lower-priority requests are blocked
- Protects remaining budget for critical operations

### Usage

#### Standalone Testing
```bash
python3 agents/vault.py
```

#### Import in Python
```python
from agents import VAULTAgent, BudgetRequest

# Initialize agent
vault = VAULTAgent()

# Check budget request
request = BudgetRequest(
    amount=10.00,
    experiment_id="experiment-uuid-here",  # Optional
    agent="SCOUT",
    description="API call for opportunity discovery"
)

result = vault.check_budget(request)

if result['approved']:
    print(f"Approved! New balance: ${result['new_balance']:.2f}")
else:
    print(f"Blocked: {result['reason']}")
```

#### Get Budget Status
```python
status = vault.get_budget_status()
print(f"Current balance: ${status['current_balance']:.2f}")
print(f"Spent: {status['percent_spent']:.1f}%")
print(f"Conservation mode: {status['conservation_mode']}")
```

#### Get Experiment Spending
```python
exp_status = vault.get_experiment_spend("experiment-uuid")
print(f"Experiment: {exp_status['name']}")
print(f"Spent: ${exp_status['budget_spent']:.2f} / ${exp_status['budget_limit']:.2f}")
print(f"Remaining: ${exp_status['remaining']:.2f}")
```

### Custom Configuration
```python
from agents import VAULTAgent, BudgetLimits

# Custom limits
custom_limits = BudgetLimits(
    monthly_limit=500.00,
    experiment_limit=100.00,
    conservation_threshold=0.9,  # 90%
    minimum_balance=20.00
)

vault = VAULTAgent(limits=custom_limits)
```

### Database Schema

#### Required Tables

**atlas_budget_summary** (VIEW - auto-calculated)
- `month_key` - Format: "YYYY-MM"
- `total_deposited` - Monthly budget
- `total_spent` - Total spent this month
- `current_balance` - Remaining balance
- `transaction_count` - Number of transactions

**atlas_budget_ledger** (TABLE - source of truth)
- `id` - UUID primary key
- `type` - Transaction type (spend/deposit)
- `amount` - Transaction amount
- `experiment_id` - Related experiment UUID
- `agent` - Agent name (lowercase enum)
- `description` - Transaction description
- `balance_after` - Balance after transaction
- `month_key` - Month key for aggregation
- `created_at` - Timestamp

**atlas_experiments**
- `id` - UUID primary key
- `name` - Experiment name
- `budget_spent` - Total spent on experiment
- Other experiment fields...

**atlas_agent_logs**
- `id` - UUID primary key
- `agent` - Agent name (lowercase enum)
- `action` - Action type
- `input` - Request details
- `output` - Result details
- `status` - Status (success/blocked/error)
- `created_at` - Timestamp

### Agent Enum Values
All agent names must be lowercase:
- `vault` - VAULT agent
- `scout` - SCOUT agent
- `forge` - FORGE agent
- `mercury` - MERCURY agent
- `argus` - ARGUS agent
- `atlas` - ATLAS orchestrator

### Error Handling

VAULT handles errors gracefully:
- Invalid amounts → Blocked with clear message
- Missing experiments → Proceeds without experiment tracking
- Database errors → Blocked to prevent inconsistent state
- All errors logged to `atlas_agent_logs`

### Integration with ATLAS Backend

The main ATLAS orchestrator uses VAULT for all spending:

```python
from agents import VAULTAgent, BudgetRequest

class ATLASAgent:
    def __init__(self):
        self.vault = VAULTAgent()

    async def make_api_call(self, agent_name: str, cost: float):
        # Check budget first
        request = BudgetRequest(
            amount=cost,
            agent=agent_name,
            description="Claude API call"
        )

        result = self.vault.check_budget(request)

        if not result['approved']:
            logger.error(f"Budget blocked: {result['reason']}")
            return None

        # Proceed with API call
        response = await self.call_claude_api()
        return response
```

### Testing

Run the standalone test:
```bash
cd /Users/ashishtaneja/Desktop/Business\ Opp/ATLAS
python3 agents/vault.py
```

Expected output:
```
============================================================
 VAULT Agent - Budget Guardian
============================================================

1. Current Budget Status:
   Balance: $250.00
   Spent: $X.XX (X.X%)
   Conservation: False

2. Testing Budget Request (no experiment):
   Approved: True
   Message: Approved $5.00
   New Balance: $245.00

3. Testing High-Spend Request (conservation mode check):
   Approved: True
   Message: Approved $50.00
   New Balance: $195.00

============================================================
 VAULT agent ready for ATLAS orchestrator
============================================================
```

### Troubleshooting

**"invalid input value for enum atlas_agent_name"**
- Agent names must be lowercase
- Use `.lower()` when passing agent names

**"cannot update view 'atlas_budget_summary'"**
- Don't try to update the VIEW directly
- Insert into `atlas_budget_ledger` instead
- The VIEW updates automatically

**"Experiment not found"**
- Ensure experiment UUID exists in `atlas_experiments`
- Or set `experiment_id=None` for non-experiment spending

**"Invalid amount: must be > 0"**
- Amount must be positive
- Use float values (e.g., 5.00 not "5")

### Next Steps

1. Integrate VAULT into main ATLAS orchestrator
2. Add revenue tracking (deposits to budget)
3. Implement budget alerts and notifications
4. Create budget reporting dashboard

---

**Created**: 2026-03-17
**Status**: Production Ready
**Dependencies**: Supabase, Python 3.9+

---

## MERCURY Agent - Distribution Engine

### Overview
MERCURY distributes landing pages created by FORGE to multiple marketing channels with AI-generated, channel-specific copy. It uses Claude Haiku for fast, cheap copy generation.

### Channels Supported
- **Reddit**: Automated posting to r/Entrepreneur, r/smallbusiness, etc.
- **Email**: B2B cold email outreach via n8n webhook
- **Meta Ads**: Facebook/Instagram ad copy generation
- **Google Ads**: Search ad copy generation

### Features

#### 1. AI-Powered Copy Generation
- Uses Claude Haiku for cost-effective copy generation
- Channel-specific optimization:
  - Reddit: Conversational, authentic tone
  - Email: Professional B2B outreach
  - Meta Ads: Attention-grabbing social media copy
  - Google Ads: Keyword-optimized search ads
- Cost: ~$0.001 per channel

#### 2. Multi-Channel Distribution
- Reddit posting via PRAW (Python Reddit API Wrapper)
- Email sending via n8n webhook integration
- Ad copy generation for Meta and Google (manual campaign setup)
- Simulated mode when credentials not configured

#### 3. VAULT Integration
- Requests budget approval before distribution
- Estimated cost: $0.05 per distribution
- Blocks if budget denied

#### 4. Performance Tracking
- Logs all distributions to database
- Stores generated copy for reference
- Tracks channel success/failure
- Updates experiment status to 'running'

### Usage

#### Standalone Testing
```bash
python3 test-mercury.py
```

#### Import in Python
```python
from agents import MERCURYAgent, DistributionRequest, VAULTAgent

# Initialize with VAULT
vault = VAULTAgent()
mercury = MERCURYAgent(vault_agent=vault)

# Create distribution request
request = DistributionRequest(
    experiment_id="experiment-uuid",
    landing_page_url="https://your-page.vercel.app",
    opportunity_title="Invoice Automation for Law Firms",
    target_vertical="Legal Services",
    value_proposition="Save 10 hours/week on invoice processing",
    channels=['reddit', 'email']
)

# Distribute
result = mercury.distribute(request)

print(f"Status: {result.status}")
print(f"Succeeded: {result.channels_succeeded}")
print(f"Failed: {result.channels_failed}")
print(f"Cost: ${result.total_cost:.4f}")
```

#### Generate Copy Only
```python
# Generate copy without distribution
copy_result = mercury._generate_channel_copy(request, 'reddit')

if copy_result['success']:
    copy = copy_result['copy']
    print(f"Headline: {copy.headline}")
    print(f"Body: {copy.body}")
    print(f"CTA: {copy.cta}")
```

#### Get Statistics
```python
stats = mercury.get_distribution_stats()
print(f"Total distributions: {stats['total_distributions']}")
print(f"Total cost: ${stats['total_cost']:.2f}")
print(f"By channel: {stats['channel_counts']}")
```

### Configuration

#### Reddit API (Required for posting)
1. Create app at https://www.reddit.com/prefs/apps
2. Set environment variables:
```bash
export REDDIT_CLIENT_ID='your_client_id'
export REDDIT_CLIENT_SECRET='your_client_secret'
export REDDIT_USERNAME='your_username'
export REDDIT_PASSWORD='your_password'
```
3. Install PRAW: `pip install praw`

#### n8n Email Webhook
```bash
export N8N_EMAIL_WEBHOOK='https://your-n8n.com/webhook/email'
```

### Database Schema

MERCURY uses `atlas_agent_logs` for tracking:

```sql
-- Distribution log
INSERT INTO atlas_agent_logs (
    agent,              -- 'mercury'
    action,             -- 'distribute_reddit', 'distribute_email'
    input,              -- Experiment ID
    output,             -- JSON with copy and results
    cost_usd,           -- Distribution cost
    status              -- 'success' or 'failed'
);
```

### Cost Analysis

Per distribution (2 channels: Reddit + Email):
- Copy generation: ~$0.001
- Posting: $0 (free)
- **Total**: ~$0.001 per distribution

Monthly (12 experiments):
- Cost: $0.012/month
- Budget impact: <0.01% of $250 budget

### Integration with ATLAS

```python
class ATLASAgent:
    def __init__(self):
        self.vault = VAULTAgent()
        self.forge = FORGEAgent(vault_agent=self.vault)
        self.mercury = MERCURYAgent(vault_agent=self.vault)

    async def launch_experiment(self, experiment_id):
        # Build landing page
        forge_result = self.forge.build_landing_page(...)

        # Distribute to channels
        mercury_request = DistributionRequest(
            experiment_id=experiment_id,
            landing_page_url=forge_result.vercel_url,
            channels=['reddit', 'email']
        )

        mercury_result = self.mercury.distribute(mercury_request)
        return mercury_result
```

### Error Handling

MERCURY handles errors gracefully:
- Budget denied → Returns budget_denied status
- Copy generation fails → Skips channel, logs error
- Distribution fails → Continues with other channels
- All errors logged to `atlas_agent_logs`

### Testing

Run comprehensive test:
```bash
cd "/Users/ashishtaneja/Desktop/Business Opp/ATLAS"
python3 test-mercury.py
```

Expected output:
```
✓ MERCURY agent initialized
✓ Distribution Stats Retrieved: 0 distributions
✓ REDDIT Copy Generated ($0.0006)
✓ EMAIL Copy Generated ($0.0003)
✓ Distribution Complete: 2/2 channels succeeded
```

### Troubleshooting

**"Reddit credentials not configured"**
- Expected when REDDIT_CLIENT_ID not set
- Set environment variables to enable actual posting
- Simulated mode works for testing

**"Email sending via n8n webhook - simulating"**
- Expected when N8N_EMAIL_WEBHOOK not set
- Configure n8n webhook URL to enable email sending

**"Budget denied by VAULT"**
- VAULT rejected budget request
- Check budget status with vault.get_budget_status()
- Wait for monthly budget refresh

### Next Steps

1. Configure Reddit API credentials
2. Set up n8n email webhook
3. Build ARGUS agent for performance tracking
4. Create ATLAS orchestrator for full automation

---

**Updated**: 2026-03-18
**Status**: Production Ready
**Dependencies**: Supabase, Anthropic (Claude Haiku), PRAW (optional), n8n (optional)

