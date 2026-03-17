#!/usr/bin/env python3
"""
ATLAS Autonomous Business System
Pure Python implementation - no n8n, no workflows, just intelligent agents
"""

import os
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging
from dataclasses import dataclass
from enum import Enum

# Third-party imports (install with: pip install supabase anthropic fastapi uvicorn schedule)
from supabase import create_client, Client
from anthropic import Anthropic
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import schedule
import time
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ATLAS')

# Load environment variables
from dotenv import load_dotenv
load_dotenv('/Users/ashishtaneja/Desktop/Business Opp/ATLAS/config/.env')

# Initialize clients
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://yozmayslzckaczdfohll.supabase.co')
SUPABASE_KEY = os.getenv('SUPABASE_ANON_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inlvem1heXNsemNrYWN6ZGZvaGxsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM2OTgzNTAsImV4cCI6MjA4OTI3NDM1MH0.uQd-f3nH6DBWz3g8lFftsA9Ql37TxE5zxMkMUbAQX0M')
ANTHROPIC_KEY = os.getenv('ANTHROPIC_API_KEY')

if not ANTHROPIC_KEY:
    raise ValueError("ANTHROPIC_API_KEY environment variable is required")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
claude = Anthropic(api_key=ANTHROPIC_KEY)

# FastAPI app for webhooks
app = FastAPI(title="ATLAS Backend")

# ===========================================
# Data Models
# ===========================================

class AgentType(Enum):
    ATLAS = "ATLAS"
    SCOUT = "SCOUT"
    VAULT = "VAULT"
    FORGE = "FORGE"
    MERCURY = "MERCURY"
    ARGUS = "ARGUS"

class ExperimentStatus(Enum):
    PLANNING = "planning"
    ACTIVE = "active"
    MEASURING = "measuring"
    KILLED = "killed"
    SCALED = "scaled"

@dataclass
class BudgetRequest:
    amount: float
    experiment_id: str
    agent: str
    description: str
    type: str = "api_call"

# ===========================================
# VAULT Agent - Budget Guardian
# ===========================================

class VAULTAgent:
    """Budget guardian - controls all spending"""

    def __init__(self):
        self.monthly_limit = 250.00
        self.experiment_limit = 50.00
        self.conservation_threshold = 0.8  # 80% of budget

    def check_budget(self, request: BudgetRequest) -> Dict[str, Any]:
        """Check if budget request should be approved"""
        try:
            # Get current month budget
            month_key = datetime.now().strftime("%Y-%m")
            budget_result = supabase.table('atlas_budget_summary').select("*").eq('month_key', month_key).execute()

            if not budget_result.data:
                # Initialize budget if not exists
                self._initialize_budget(month_key)
                budget_result = supabase.table('atlas_budget_summary').select("*").eq('month_key', month_key).execute()

            budget = budget_result.data[0]
            current_balance = float(budget.get('current_balance', 0))
            total_spent = float(budget.get('total_spent', 0))

            # Check if we have enough balance
            if current_balance < request.amount:
                return self._block_request(request, f"Insufficient balance: ${current_balance:.2f} < ${request.amount:.2f}")

            # Check experiment limit if applicable
            if request.experiment_id:
                exp_result = supabase.table('atlas_experiments').select("budget_spent").eq('experiment_id', request.experiment_id).execute()

                if exp_result.data:
                    experiment_spent = float(exp_result.data[0].get('budget_spent', 0))
                    if (experiment_spent + request.amount) > self.experiment_limit:
                        return self._block_request(request, f"Experiment limit exceeded: ${experiment_spent:.2f} + ${request.amount:.2f} > ${self.experiment_limit:.2f}")

            # Check conservation mode
            if total_spent > (self.monthly_limit * self.conservation_threshold):
                logger.warning(f"Conservation mode active: ${total_spent:.2f} > ${self.monthly_limit * self.conservation_threshold:.2f}")
                # In conservation mode, only allow high-priority spending
                if request.agent != "SONNET":
                    return self._block_request(request, "Conservation mode: Only high-priority spending allowed")

            # Approved! Update budget
            return self._approve_request(request, budget, current_balance)

        except Exception as e:
            logger.error(f"Budget check error: {e}")
            return self._block_request(request, f"Error: {str(e)}")

    def _initialize_budget(self, month_key: str):
        """Initialize budget for new month"""
        budget_data = {
            "month_key": month_key,
            "total_deposited": self.monthly_limit,
            "total_spent": 0,
            "total_revenue": 0,
            "current_balance": self.monthly_limit,
            "transaction_count": 0
        }
        supabase.table('atlas_budget_summary').insert(budget_data).execute()
        logger.info(f"Initialized budget for {month_key}: ${self.monthly_limit}")

    def _approve_request(self, request: BudgetRequest, budget: Dict, current_balance: float) -> Dict[str, Any]:
        """Approve and log the budget request"""
        new_balance = current_balance - request.amount

        # Update budget summary
        supabase.table('atlas_budget_summary').update({
            'current_balance': new_balance,
            'total_spent': float(budget.get('total_spent', 0)) + request.amount,
            'transaction_count': budget.get('transaction_count', 0) + 1
        }).eq('month_key', budget['month_key']).execute()

        # Log to ledger
        supabase.table('atlas_budget_ledger').insert({
            'transaction_type': 'spend',
            'amount': request.amount,
            'experiment_id': request.experiment_id,
            'agent': request.agent,
            'description': request.description,
            'balance_after': new_balance,
            'created_at': datetime.now().isoformat()
        }).execute()

        # Update experiment spend if applicable
        if request.experiment_id:
            exp_result = supabase.table('atlas_experiments').select("budget_spent").eq('experiment_id', request.experiment_id).execute()
            if exp_result.data:
                current_exp_spend = float(exp_result.data[0].get('budget_spent', 0))
                supabase.table('atlas_experiments').update({
                    'budget_spent': current_exp_spend + request.amount
                }).eq('experiment_id', request.experiment_id).execute()

        logger.info(f"Approved ${request.amount:.2f} for {request.agent}: {request.description}")

        return {
            "approved": True,
            "amount": request.amount,
            "new_balance": new_balance,
            "message": f"Approved ${request.amount:.2f}",
            "timestamp": datetime.now().isoformat()
        }

    def _block_request(self, request: BudgetRequest, reason: str) -> Dict[str, Any]:
        """Block and log the rejected request"""
        # Log to agent logs
        supabase.table('atlas_agent_logs').insert({
            'agent_name': 'VAULT',
            'action_type': 'budget_block',
            'details': f"Blocked ${request.amount:.2f}: {reason}",
            'experiment_id': request.experiment_id,
            'created_at': datetime.now().isoformat()
        }).execute()

        logger.warning(f"Blocked ${request.amount:.2f} for {request.agent}: {reason}")

        return {
            "approved": False,
            "amount": request.amount,
            "reason": reason,
            "message": f"Blocked: {reason}",
            "timestamp": datetime.now().isoformat()
        }

# ===========================================
# SCOUT Agent - Opportunity Discovery
# ===========================================

class SCOUTAgent:
    """Discovers opportunities from various sources"""

    def __init__(self):
        self.sources = ['reddit', 'trends', 'forums']
        self.search_keywords = [
            'automate', 'manual process', 'workflow',
            'hours wasted', 'repetitive', 'spending hours',
            'invoice', 'review management', 'client onboarding'
        ]

    async def discover_opportunities(self):
        """Run discovery pipeline"""
        logger.info("SCOUT: Starting opportunity discovery...")

        # For now, we'll simulate discovery with a simple example
        # In production, this would use Apify or other scraping tools
        opportunities = self._mock_discover()

        # Filter with Haiku
        filtered = []
        for opp in opportunities:
            if await self._haiku_filter(opp):
                filtered.append(opp)

        # Save to database
        for opp in filtered:
            self._save_opportunity(opp)

        # Log the run
        supabase.table('atlas_agent_logs').insert({
            'agent_name': 'SCOUT',
            'action_type': 'discovery_run',
            'details': f"Found {len(filtered)} opportunities from {len(opportunities)} candidates",
            'created_at': datetime.now().isoformat()
        }).execute()

        logger.info(f"SCOUT: Discovered {len(filtered)} qualified opportunities")
        return filtered

    def _mock_discover(self):
        """Mock discovery for testing"""
        return [
            {
                'title': 'Law firm needs automated invoice processing',
                'source': 'reddit',
                'source_url': 'https://reddit.com/r/smallbusiness/example',
                'description': 'Spending 10 hours/week on manual invoice entry and reconciliation',
                'category': 'other',
                'target_vertical': 'legal'
            }
        ]

    async def _haiku_filter(self, opportunity: Dict) -> bool:
        """Use Claude Haiku to filter opportunities"""
        try:
            response = claude.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=100,
                messages=[{
                    "role": "user",
                    "content": f"""Is this a real business automation opportunity?
                    Title: {opportunity['title']}
                    Description: {opportunity['description']}

                    Reply YES or NO with a 1-sentence reason."""
                }]
            )

            result = response.content[0].text
            return result.upper().startswith('YES')

        except Exception as e:
            logger.error(f"Haiku filter error: {e}")
            return False

    def _save_opportunity(self, opportunity: Dict):
        """Save opportunity to database"""
        opportunity['haiku_filter_pass'] = True
        opportunity['status'] = 'discovered'
        opportunity['discovered_at'] = datetime.now().isoformat()

        supabase.table('atlas_opportunities').insert(opportunity).execute()

# ===========================================
# ATLAS Agent - Main Orchestrator
# ===========================================

class ATLASAgent:
    """CEO agent - makes strategic decisions"""

    def __init__(self):
        self.scout = SCOUTAgent()
        self.vault = VAULTAgent()

    async def run_daily_orchestration(self):
        """Main daily orchestration logic"""
        logger.info("ATLAS: Starting daily orchestration...")

        # Get current state
        experiments = self._get_active_experiments()
        opportunities = self._get_new_opportunities()
        budget_status = self._get_budget_status()

        # Make decisions
        decisions = await self._make_strategic_decisions(experiments, opportunities, budget_status)

        # Create and save briefing
        briefing = self._create_briefing(experiments, opportunities, budget_status, decisions)

        # Execute decisions
        for decision in decisions:
            await self._execute_decision(decision)

        logger.info("ATLAS: Daily orchestration complete")
        return briefing

    def _get_active_experiments(self):
        """Get all active experiments"""
        result = supabase.table('atlas_experiments').select("*").in_('status', ['active', 'measuring']).execute()
        return result.data or []

    def _get_new_opportunities(self):
        """Get new discovered opportunities"""
        result = supabase.table('atlas_opportunities').select("*").eq('status', 'discovered').eq('haiku_filter_pass', True).execute()
        return result.data or []

    def _get_budget_status(self):
        """Get current budget status"""
        month_key = datetime.now().strftime("%Y-%m")
        result = supabase.table('atlas_budget_summary').select("*").eq('month_key', month_key).execute()
        return result.data[0] if result.data else None

    async def _make_strategic_decisions(self, experiments, opportunities, budget_status):
        """Use Claude Sonnet to make strategic decisions"""
        # This would use Sonnet for complex decision making
        # For now, simple rule-based decisions
        decisions = []

        # Kill underperforming experiments
        for exp in experiments:
            if float(exp.get('ehs_score', 100)) < 30:
                decisions.append({
                    'action': 'kill_experiment',
                    'experiment_id': exp['experiment_id'],
                    'reason': 'Low EHS score'
                })

        # Start new experiments if budget allows
        if budget_status and float(budget_status['current_balance']) > 100:
            for opp in opportunities[:2]:  # Max 2 new experiments
                decisions.append({
                    'action': 'start_experiment',
                    'opportunity_id': opp['id'],
                    'budget': 50.00
                })

        return decisions

    def _create_briefing(self, experiments, opportunities, budget_status, decisions):
        """Create daily briefing"""
        briefing_content = f"""
# ATLAS Daily Briefing - {datetime.now().strftime('%Y-%m-%d')}

## Budget Status
- Current Balance: ${budget_status['current_balance'] if budget_status else 0:.2f}
- Monthly Spend: ${budget_status['total_spent'] if budget_status else 0:.2f}

## Active Experiments: {len(experiments)}
{chr(10).join([f"- {exp['name']} (EHS: {exp.get('ehs_score', 'N/A')})" for exp in experiments[:5]])}

## New Opportunities: {len(opportunities)}
{chr(10).join([f"- {opp['title']}" for opp in opportunities[:5]])}

## Decisions Made: {len(decisions)}
{chr(10).join([f"- {dec['action']}: {dec.get('reason', 'Strategic')}" for dec in decisions])}
"""

        # Save briefing
        briefing_data = {
            'briefing_type': 'daily',
            'content': briefing_content,
            'decisions': json.dumps(decisions),
            'status': 'draft',
            'created_at': datetime.now().isoformat()
        }

        result = supabase.table('atlas_briefings').insert(briefing_data).execute()
        logger.info("ATLAS: Daily briefing created")

        return briefing_content

    async def _execute_decision(self, decision: Dict):
        """Execute a strategic decision"""
        if decision['action'] == 'kill_experiment':
            supabase.table('atlas_experiments').update({
                'status': 'killed',
                'kill_reason': decision['reason'],
                'ended_at': datetime.now().isoformat()
            }).eq('experiment_id', decision['experiment_id']).execute()

        elif decision['action'] == 'start_experiment':
            # This would trigger FORGE to build landing page
            logger.info(f"Would start experiment for opportunity {decision['opportunity_id']}")

# ===========================================
# API Endpoints
# ===========================================

class BudgetCheckRequest(BaseModel):
    amount: float
    experiment_id: Optional[str] = None
    agent: str = "unknown"
    description: str = "Budget request"
    type: str = "api_call"

@app.post("/webhook/budget-check")
async def budget_check(request: BudgetCheckRequest):
    """VAULT webhook endpoint for budget checking"""
    vault = VAULTAgent()

    budget_request = BudgetRequest(
        amount=request.amount,
        experiment_id=request.experiment_id or "",
        agent=request.agent,
        description=request.description,
        type=request.type
    )

    result = vault.check_budget(budget_request)

    if not result['approved']:
        raise HTTPException(status_code=403, detail=result['reason'])

    return result

@app.get("/api/status")
async def get_status():
    """Get system status"""
    month_key = datetime.now().strftime("%Y-%m")
    budget_result = supabase.table('atlas_budget_summary').select("*").eq('month_key', month_key).execute()
    exp_result = supabase.table('atlas_experiments').select("*").in_('status', ['active', 'measuring']).execute()

    return {
        "status": "operational",
        "budget": budget_result.data[0] if budget_result.data else None,
        "active_experiments": len(exp_result.data) if exp_result.data else 0,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/trigger/scout")
async def trigger_scout():
    """Manually trigger SCOUT discovery"""
    scout = SCOUTAgent()
    opportunities = await scout.discover_opportunities()
    return {"discovered": len(opportunities)}

@app.post("/api/trigger/orchestrate")
async def trigger_orchestration():
    """Manually trigger ATLAS orchestration"""
    atlas = ATLASAgent()
    briefing = await atlas.run_daily_orchestration()
    return {"briefing": briefing}

# ===========================================
# Scheduler
# ===========================================

def run_scheduled_tasks():
    """Background thread for scheduled tasks"""
    # Schedule SCOUT for Mon/Wed/Fri at 5 AM
    schedule.every().monday.at("05:00").do(lambda: asyncio.run(SCOUTAgent().discover_opportunities()))
    schedule.every().wednesday.at("05:00").do(lambda: asyncio.run(SCOUTAgent().discover_opportunities()))
    schedule.every().friday.at("05:00").do(lambda: asyncio.run(SCOUTAgent().discover_opportunities()))

    # Schedule ATLAS orchestration daily at 7 AM
    schedule.every().day.at("07:00").do(lambda: asyncio.run(ATLASAgent().run_daily_orchestration()))

    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

# ===========================================
# Main Entry Point
# ===========================================

if __name__ == "__main__":
    import uvicorn

    # Start scheduler in background thread
    scheduler_thread = threading.Thread(target=run_scheduled_tasks, daemon=True)
    scheduler_thread.start()

    logger.info("=" * 60)
    logger.info(" ATLAS BACKEND STARTING")
    logger.info("=" * 60)
    logger.info(" No n8n. No workflows. Just intelligent agents.")
    logger.info(" Budget: $250/month")
    logger.info(" Webhook: http://localhost:8000/webhook/budget-check")
    logger.info(" Status: http://localhost:8000/api/status")
    logger.info("=" * 60)

    # Run FastAPI server
    uvicorn.run(app, host="0.0.0.0", port=8000)