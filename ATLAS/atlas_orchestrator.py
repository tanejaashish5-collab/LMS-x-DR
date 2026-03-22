#!/usr/bin/env python3
"""
ATLAS Main Orchestrator
Coordinates all agents: SCOUT, VAULT, FORGE, MERCURY, CLOSER, CONTENT_CREATOR
Pure Python - No n8n, No workflows, Just intelligent agents
"""

import os
import sys
import json
import asyncio
from datetime import date, datetime, timedelta
from typing import Dict, Any, List, Optional
import logging
import uuid
import threading
import time

# Add agents directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'agents'))

# Import all ATLAS agents
from agents.vault import VAULTAgent, BudgetRequest
from agents.scout import SCOUTAgent
from agents.forge import FORGEAgent, LandingPageRequest
from agents.mercury import MERCURYAgent, DistributionRequest
from agents.closer import CLOSERAgent
from agents.content_creator import ContentCreatorAgent

# Third-party imports
from supabase import create_client, Client
from anthropic import Anthropic
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import schedule
import uvicorn

# Load environment
from dotenv import load_dotenv

# Load .env from config/ relative to this file (works locally and on Railway)
_env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config', '.env')
if os.path.exists(_env_path):
    load_dotenv(_env_path)
# On Railway, env vars are injected directly — no .env file needed

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ATLAS-ORCHESTRATOR')

# Initialize Supabase
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_ANON_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY environment variables are required")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Initialize Claude
ANTHROPIC_KEY = os.getenv('ANTHROPIC_API_KEY')
if not ANTHROPIC_KEY:
    raise ValueError("ANTHROPIC_API_KEY environment variable is required")

claude = Anthropic(api_key=ANTHROPIC_KEY)

# FastAPI app
app = FastAPI(title="ATLAS Orchestrator", version="2.0")

# ===========================================
# ATLAS Orchestrator Class
# ===========================================

class ATLASOrchestrator:
    """
    Main orchestrator - coordinates all agents
    This is the CEO of the autonomous system
    """

    def __init__(self):
        """Initialize all agents"""
        self.vault = VAULTAgent()
        self.scout = SCOUTAgent()
        self.forge = FORGEAgent(vault_agent=self.vault)
        self.mercury = MERCURYAgent(vault_agent=self.vault)
        self.closer = CLOSERAgent(vault_agent=self.vault)
        self.content_creator = ContentCreatorAgent(vault_agent=self.vault)

        logger.info("ATLAS Orchestrator initialized with all agents (including CLOSER, CONTENT_CREATOR)")

    async def run_discovery_pipeline(self) -> Dict[str, Any]:
        """
        Run the full discovery pipeline (Mon/Wed/Fri at 5 AM)
        SCOUT discovers → Filter → Score → Save
        """
        logger.info("=" * 60)
        logger.info("Starting Discovery Pipeline")
        logger.info("=" * 60)

        try:
            # Request budget for discovery
            budget_request = BudgetRequest(
                amount=2.00,  # Discovery costs ~$2
                agent="scout",
                description="Reddit discovery and filtering"
            )

            budget_result = self.vault.check_budget(budget_request)
            if not budget_result['approved']:
                logger.warning(f"Discovery blocked: {budget_result['reason']}")
                return {"status": "blocked", "reason": budget_result['reason']}

            # Run SCOUT discovery (sync method)
            discovery_result = self.scout.run_discovery()

            logger.info(f"Discovery complete: {discovery_result}")

            # Log to agent logs
            supabase.table('atlas_agent_logs').insert({
                'agent_name': 'atlas',
                'action_type': 'discovery_pipeline',
                'details': f"Discovered {discovery_result.get('discovered', 0)} opportunities",
                'created_at': datetime.now().isoformat()
            }).execute()

            return {
                "status": "success",
                "discovered": discovery_result.get('discovered', 0),
                "filtered": discovery_result.get('filtered', 0),
                "scored": discovery_result.get('scored', 0)
            }

        except Exception as e:
            logger.error(f"Discovery pipeline error: {e}")
            return {"status": "error", "error": str(e)}

    async def run_experiment_creation(self, opportunity_id: str) -> Dict[str, Any]:
        """
        Create an experiment from an opportunity
        FORGE builds → MERCURY distributes
        """
        logger.info(f"Creating experiment for opportunity: {opportunity_id}")

        try:
            # Get opportunity details
            opp_result = supabase.table('atlas_opportunities').select("*").eq('id', opportunity_id).execute()
            if not opp_result.data:
                return {"status": "error", "error": "Opportunity not found"}

            opportunity = opp_result.data[0]

            # Generate experiment ID
            experiment_id = f"exp-{uuid.uuid4().hex[:8]}"

            # Create experiment record
            experiment_data = {
                'id': str(uuid.uuid4()),
                'opportunity_id': opportunity_id,
                'name': f"Test: {opportunity['title'][:50]}",
                'vertical': opportunity.get('target_vertical', 'general'),
                'status': 'pending',
                'budget_allocated': 50.00,
                'budget_spent': 0,
                'started_at': datetime.now().isoformat()
            }

            exp_result = supabase.table('atlas_experiments').insert(experiment_data).execute()
            if not exp_result.data:
                return {"status": "error", "error": "Failed to create experiment"}

            experiment = exp_result.data[0]

            # Build landing page with FORGE
            landing_request = LandingPageRequest(
                experiment_id=experiment['id'],
                opportunity_title=opportunity['title'],
                target_vertical=opportunity.get('target_vertical', 'general'),
                value_proposition=opportunity.get('value_proposition', 'Save time and money'),
                cta_text="Get Started",
                cta_action="https://calendly.com/ashishtaneja"
            )

            forge_result = self.forge.build_landing_page(landing_request)

            if forge_result.status != "deployed":
                # Update experiment as failed
                supabase.table('atlas_experiments').update({
                    'status': 'failed',
                    'ended_at': datetime.now().isoformat()
                }).eq('id', experiment['id']).execute()

                return {"status": "error", "error": f"Landing page build failed: {forge_result.error}"}

            # Distribute with MERCURY
            distribution_request = DistributionRequest(
                experiment_id=experiment['id'],
                landing_page_url=forge_result.vercel_url,
                opportunity_title=opportunity['title'],
                target_vertical=opportunity.get('target_vertical', 'general'),
                value_proposition=opportunity.get('value_proposition', 'Save time and money'),
                channels=['reddit', 'email']
            )

            mercury_result = self.mercury.distribute(distribution_request)

            # Update experiment status
            supabase.table('atlas_experiments').update({
                'status': 'running' if mercury_result.success else 'failed',
                'landing_page_url': forge_result.vercel_url
            }).eq('id', experiment['id']).execute()

            logger.info(f"Experiment created: {experiment['id']}")

            return {
                "status": "success",
                "experiment_id": experiment['id'],
                "landing_page_url": forge_result.vercel_url,
                "distribution_channels": mercury_result.channels_posted,
                "total_cost": forge_result.cost + mercury_result.total_cost
            }

        except Exception as e:
            logger.error(f"Experiment creation error: {e}")
            return {"status": "error", "error": str(e)}

    async def run_daily_orchestration(self) -> Dict[str, Any]:
        """
        Daily orchestration at 7 AM
        Reviews all experiments, makes strategic decisions
        """
        logger.info("=" * 60)
        logger.info("Starting Daily Orchestration")
        logger.info("=" * 60)

        try:
            # Get system state
            experiments = self._get_active_experiments()
            opportunities = self._get_top_opportunities()
            budget_status = self._get_budget_status()

            # Make strategic decisions with Claude Sonnet
            decisions = await self._make_strategic_decisions(
                experiments, opportunities, budget_status
            )

            # Execute decisions
            results = []
            for decision in decisions:
                if decision['action'] == 'create_experiment':
                    result = await self.run_experiment_creation(decision['opportunity_id'])
                    results.append(result)
                elif decision['action'] == 'kill_experiment':
                    self._kill_experiment(decision['experiment_id'], decision['reason'])
                    results.append({"killed": decision['experiment_id']})

            # Run CLOSER pipeline: qualify, propose, follow up
            logger.info("Running CLOSER sales pipeline...")
            closer_results = self.closer.run_pipeline()
            results.append({"closer": closer_results})

            # Get pipeline summary for briefing
            pipeline_summary = self.closer.get_pipeline_summary()

            # Get content stats for briefing
            content_stats = await self.content_creator.get_content_stats()

            # Create daily briefing
            briefing = self._create_briefing(experiments, opportunities, budget_status, decisions, results, pipeline_summary, content_stats)

            logger.info("Daily orchestration complete")
            return {
                "status": "success",
                "decisions": len(decisions),
                "briefing": briefing
            }

        except Exception as e:
            logger.error(f"Daily orchestration error: {e}")
            return {"status": "error", "error": str(e)}

    def _get_active_experiments(self) -> List[Dict]:
        """Get all active experiments"""
        try:
            result = supabase.table('atlas_experiments').select("*").execute()
            # Filter for active experiments in code since enum might vary
            active_experiments = [
                exp for exp in (result.data or [])
                if exp.get('status') in ['active', 'measuring', 'running', 'deployed']
            ]
            return active_experiments
        except Exception as e:
            logger.warning(f"Error fetching experiments: {e}")
            return []

    def _get_top_opportunities(self) -> List[Dict]:
        """Get top scored opportunities not yet tested"""
        result = supabase.table('atlas_opportunities').select("*")\
            .eq('status', 'sonnet_scored')\
            .gte('sonnet_score', 70)\
            .order('sonnet_score.desc')\
            .limit(5)\
            .execute()
        return result.data or []

    def _get_budget_status(self) -> Dict:
        """Get current month budget status"""
        month_key = datetime.now().strftime("%Y-%m")

        # Get ledger transactions for this month
        ledger_result = supabase.table('atlas_budget_ledger')\
            .select("*")\
            .gte('created_at', f"{month_key}-01")\
            .execute()

        if ledger_result.data:
            total_spent = sum(t['amount'] for t in ledger_result.data if t['type'] == 'spend')
            total_revenue = sum(t['amount'] for t in ledger_result.data if t['type'] == 'revenue')
            balance = 250.00 - total_spent + total_revenue
        else:
            total_spent = 0
            total_revenue = 0
            balance = 250.00

        return {
            'month_key': month_key,
            'current_balance': balance,
            'total_spent': total_spent,
            'total_revenue': total_revenue,
            'transaction_count': len(ledger_result.data) if ledger_result.data else 0
        }

    async def _make_strategic_decisions(self, experiments, opportunities, budget_status) -> List[Dict]:
        """Use Claude Sonnet to make strategic decisions"""
        decisions = []

        # Kill underperforming experiments (simple rule for now)
        for exp in experiments:
            days_running = (datetime.now() - datetime.fromisoformat(exp['started_at'])).days
            if days_running > 7 and float(exp.get('total_revenue', 0)) == 0:
                decisions.append({
                    'action': 'kill_experiment',
                    'experiment_id': exp['id'],
                    'reason': 'No revenue after 7 days'
                })

        # Start new experiments if budget allows
        if budget_status['current_balance'] > 100 and len(experiments) < 3:
            for opp in opportunities[:1]:  # Start 1 new experiment
                decisions.append({
                    'action': 'create_experiment',
                    'opportunity_id': opp['id']
                })

        return decisions

    def _kill_experiment(self, experiment_id: str, reason: str):
        """Terminate an experiment"""
        supabase.table('atlas_experiments').update({
            'status': 'killed',
            'kill_reason': reason,
            'ended_at': datetime.now().isoformat()
        }).eq('id', experiment_id).execute()

        logger.info(f"Killed experiment {experiment_id}: {reason}")

    def _create_briefing(self, experiments, opportunities, budget_status, decisions, results, pipeline_summary=None, content_stats=None) -> str:
        """Create daily briefing including sales pipeline and content status"""
        # Build pipeline section
        pipeline_section = ""
        if pipeline_summary and 'error' not in pipeline_summary:
            by_stage = pipeline_summary.get('by_stage', {})
            pipeline_section = f"""
## Sales Pipeline (CLOSER)
- Total Deals: {pipeline_summary.get('total_deals', 0)}
- Pipeline Value: ${pipeline_summary.get('total_pipeline_value', 0):,.2f} AUD
- Closed Won: ${pipeline_summary.get('closed_won_value', 0):,.2f} AUD
- Proposals Pending: {pipeline_summary.get('proposals_pending', 0)}
- Follow-ups Due: {pipeline_summary.get('followups_due', 0)}
- Stages: {', '.join(f'{k}: {v}' for k, v in by_stage.items())}
"""

        # Build content section
        content_section = ""
        if content_stats and 'error' not in content_stats:
            upcoming = content_stats.get('upcoming_week', [])
            upcoming_lines = [
                f"  - {c.get('scheduled_for', '?')}: [{c.get('pillar', '?')}] {c.get('topic', '?')[:50]}"
                for c in upcoming[:5]
            ]
            content_section = f"""
## Content Calendar (CONTENT_CREATOR)
- Total Content: {content_stats.get('total_content', 0)}
- Drafts Pending Review: {content_stats.get('drafts', 0)}
- Posted: {content_stats.get('posted', 0)}
- Upcoming This Week:
{chr(10).join(upcoming_lines) if upcoming_lines else '  - No content scheduled'}
"""

        briefing = f"""
# ATLAS Daily Briefing
Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Budget Status
- Balance: ${budget_status['current_balance']:.2f}
- Spent: ${budget_status['total_spent']:.2f}
- Revenue: ${budget_status['total_revenue']:.2f}

## Active Experiments: {len(experiments)}
{chr(10).join([f"- {e['name']}" for e in experiments[:5]])}

## Top Opportunities: {len(opportunities)}
{chr(10).join([f"- {o['title']} (Score: {o.get('sonnet_score', 'N/A')})" for o in opportunities[:3]])}
{pipeline_section}{content_section}
## Decisions Made: {len(decisions)}
{chr(10).join([f"- {d['action']}: {d.get('reason', 'Strategic')}" for d in decisions])}

## Results
{chr(10).join([f"- {json.dumps(r)}" for r in results[:5]])}
"""

        # Save briefing
        supabase.table('atlas_briefings').insert({
            'briefing_type': 'daily',
            'content': briefing,
            'decisions': json.dumps(decisions),
            'status': 'sent',
            'created_at': datetime.now().isoformat()
        }).execute()

        return briefing

# ===========================================
# API Endpoints
# ===========================================

@app.get("/health")
async def health():
    """Health check for Railway/Docker"""
    return {"status": "healthy"}

@app.get("/")
async def root():
    """Root endpoint with system info"""
    return {
        "system": "ATLAS Autonomous Business System",
        "version": "2.0",
        "status": "operational",
        "agents": ["SCOUT", "VAULT", "FORGE", "MERCURY", "CLOSER", "CONTENT_CREATOR"],
        "message": "No n8n. No workflows. Just intelligent agents."
    }

@app.get("/api/status")
async def get_status():
    """Get system status"""
    orchestrator = ATLASOrchestrator()
    budget_status = orchestrator._get_budget_status()
    experiments = orchestrator._get_active_experiments()

    return {
        "status": "operational",
        "budget": budget_status,
        "active_experiments": len(experiments),
        "agents": {
            "scout": "ready",
            "vault": "ready",
            "forge": "ready",
            "mercury": "ready",
            "closer": "ready",
            "content_creator": "ready"
        },
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/discover")
async def trigger_discovery(background_tasks: BackgroundTasks):
    """Manually trigger discovery pipeline"""
    orchestrator = ATLASOrchestrator()
    background_tasks.add_task(orchestrator.run_discovery_pipeline)
    return {"status": "discovery started"}

@app.post("/api/experiment/{opportunity_id}")
async def create_experiment(opportunity_id: str, background_tasks: BackgroundTasks):
    """Create experiment from opportunity"""
    orchestrator = ATLASOrchestrator()
    result = await orchestrator.run_experiment_creation(opportunity_id)
    return result

@app.post("/api/orchestrate")
async def trigger_orchestration(background_tasks: BackgroundTasks):
    """Manually trigger daily orchestration"""
    orchestrator = ATLASOrchestrator()
    background_tasks.add_task(orchestrator.run_daily_orchestration)
    return {"status": "orchestration started"}

# ===========================================
# CLOSER / Pipeline Endpoints
# ===========================================

@app.get("/api/pipeline")
async def list_pipeline():
    """List all pipeline entries"""
    orchestrator = ATLASOrchestrator()
    result = orchestrator.closer.supabase.table('atlas_pipeline').select(
        '*, atlas_opportunities(title, target_vertical, sonnet_score)'
    ).order('created_at', desc=True).execute()
    return {"pipeline": result.data or [], "count": len(result.data or [])}


@app.get("/api/pipeline/pending")
async def get_pending_approvals():
    """Get all pipeline entries pending human review."""
    orchestrator = ATLASOrchestrator()
    sb = orchestrator.closer.supabase

    pending = sb.table('atlas_pipeline').select(
        '*, atlas_opportunities(title, target_vertical, source_url, sonnet_score)'
    ).eq('stage', 'pending_review').order('created_at', desc=True).execute()

    results = []
    for entry in (pending.data or []):
        proposals = sb.table('atlas_proposals').select('*').eq(
            'pipeline_id', entry['id']
        ).order('created_at', desc=True).execute()
        entry['proposals'] = proposals.data or []
        results.append(entry)

    return {"pending": results, "count": len(results)}


@app.post("/api/pipeline/{pipeline_id}/approve")
async def approve_proposal(pipeline_id: str):
    """Approve a proposal -- moves to 'proposed' stage and triggers email send."""
    orchestrator = ATLASOrchestrator()
    sb = orchestrator.closer.supabase

    # Verify it's in pending_review
    entry = sb.table('atlas_pipeline').select('*').eq('id', pipeline_id).execute()
    if not entry.data or entry.data[0]['stage'] != 'pending_review':
        raise HTTPException(status_code=400, detail="Entry not in pending_review stage")

    # Move to proposed
    sb.table('atlas_pipeline').update({
        'stage': 'proposed',
        'proposed_at': datetime.now().isoformat(),
    }).eq('id', pipeline_id).execute()

    # Now trigger email send for the proposal
    proposal = sb.table('atlas_proposals').select('*').eq(
        'pipeline_id', pipeline_id
    ).order('created_at', desc=True).limit(1).execute()

    email_sent = False
    if proposal.data:
        to_email = entry.data[0].get('contact_email', '')
        if to_email and to_email != 'MANUAL_DM_REQUIRED':
            try:
                from services.email_service import get_email_service
                email_svc = get_email_service(sb)
                content = proposal.data[0].get('content', '{}')
                if isinstance(content, str):
                    content = json.loads(content)
                subject = content.get('subject', f"Your Custom Automation Solution")
                intro = content.get('intro_paragraph', content.get('executive_summary', ''))
                email_svc.send_email_sync(
                    to=to_email,
                    subject=subject,
                    body=intro,
                    pipeline_id=pipeline_id,
                    email_type='proposal',
                )
                email_sent = True
            except Exception as e:
                logger.warning(f"Approval email send failed: {e}")

    # Log the approval
    sb.table('atlas_communications').insert({
        'pipeline_id': pipeline_id,
        'channel': 'system',
        'direction': 'outbound',
        'subject': 'Proposal approved by Ashish',
        'content': f'Proposal approved and moved to proposed stage. Email sent: {email_sent}',
        'sentiment': 'positive',
    }).execute()

    return {
        "status": "approved",
        "pipeline_id": pipeline_id,
        "stage": "proposed",
        "email_sent": email_sent,
    }


@app.post("/api/pipeline/{pipeline_id}/reject")
async def reject_proposal(pipeline_id: str):
    """Reject a proposal -- moves to 'closed_lost'."""
    orchestrator = ATLASOrchestrator()
    sb = orchestrator.closer.supabase

    # Verify it's in pending_review
    entry = sb.table('atlas_pipeline').select('*').eq('id', pipeline_id).execute()
    if not entry.data or entry.data[0]['stage'] != 'pending_review':
        raise HTTPException(status_code=400, detail="Entry not in pending_review stage")

    sb.table('atlas_pipeline').update({
        'stage': 'closed_lost',
        'closed_at': datetime.now().isoformat(),
        'notes': json.dumps({"reason": "Rejected in review by Ashish"}),
    }).eq('id', pipeline_id).execute()

    # Log the rejection
    sb.table('atlas_communications').insert({
        'pipeline_id': pipeline_id,
        'channel': 'system',
        'direction': 'outbound',
        'subject': 'Proposal rejected by Ashish',
        'content': 'Proposal rejected in human review and moved to closed_lost',
        'sentiment': 'negative',
    }).execute()

    return {"status": "rejected", "pipeline_id": pipeline_id, "stage": "closed_lost"}


@app.get("/api/pipeline/{pipeline_id}")
async def get_pipeline_detail(pipeline_id: str):
    """Get pipeline entry detail with proposals and outreach"""
    orchestrator = ATLASOrchestrator()
    sb = orchestrator.closer.supabase

    entry = sb.table('atlas_pipeline').select(
        '*, atlas_opportunities(*)'
    ).eq('id', pipeline_id).execute()

    if not entry.data:
        raise HTTPException(status_code=404, detail="Pipeline entry not found")

    proposals = sb.table('atlas_proposals').select('*').eq(
        'pipeline_id', pipeline_id
    ).order('created_at', desc=True).execute()

    outreach = sb.table('atlas_outreach').select('*').eq(
        'pipeline_id', pipeline_id
    ).order('created_at', desc=True).execute()

    comms = sb.table('atlas_communications').select('*').eq(
        'pipeline_id', pipeline_id
    ).order('created_at', desc=True).execute()

    return {
        "pipeline": entry.data[0],
        "proposals": proposals.data or [],
        "outreach": outreach.data or [],
        "communications": comms.data or [],
    }


@app.post("/api/pipeline/{pipeline_id}/advance")
async def advance_pipeline(pipeline_id: str):
    """Advance pipeline entry to next stage"""
    orchestrator = ATLASOrchestrator()
    result = orchestrator.closer.advance_pipeline(pipeline_id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.get("/api/proposals")
async def list_proposals():
    """List all proposals"""
    orchestrator = ATLASOrchestrator()
    result = orchestrator.closer.supabase.table('atlas_proposals').select(
        '*, atlas_pipeline(stage, company_name, deal_value)'
    ).order('created_at', desc=True).execute()
    return {"proposals": result.data or [], "count": len(result.data or [])}


@app.get("/api/outreach")
async def list_outreach():
    """List all outreach emails"""
    orchestrator = ATLASOrchestrator()
    result = orchestrator.closer.supabase.table('atlas_outreach').select(
        '*, atlas_pipeline(stage, company_name)'
    ).order('created_at', desc=True).execute()
    return {"outreach": result.data or [], "count": len(result.data or [])}


@app.post("/api/closer/run")
async def trigger_closer(background_tasks: BackgroundTasks):
    """Manually trigger CLOSER pipeline"""
    orchestrator = ATLASOrchestrator()
    background_tasks.add_task(orchestrator.closer.run_pipeline)
    return {"status": "closer pipeline started"}


@app.get("/api/closer/summary")
async def closer_summary():
    """Get CLOSER pipeline summary"""
    orchestrator = ATLASOrchestrator()
    return orchestrator.closer.get_pipeline_summary()


@app.get("/api/closer/report")
async def closer_report():
    """Get CLOSER daily report"""
    orchestrator = ATLASOrchestrator()
    return {"report": orchestrator.closer.get_daily_report()}


@app.post("/webhook/budget-check")
async def budget_check(request: Dict[str, Any]):
    """VAULT budget check webhook"""
    vault = VAULTAgent()

    budget_request = BudgetRequest(
        amount=request.get('amount', 0),
        experiment_id=request.get('experiment_id', ''),
        agent=request.get('agent', 'unknown'),
        description=request.get('description', 'Budget request')
    )

    result = vault.check_budget(budget_request)

    if not result['approved']:
        raise HTTPException(status_code=403, detail=result['reason'])

    return result

# ===========================================
# Memory Endpoints
# ===========================================

@app.get("/api/memory/{agent_name}")
async def get_agent_memory(agent_name: str, memory_type: Optional[str] = None, limit: int = 50):
    """Get agent memory entries"""
    from agents.memory import AgentMemory

    memory = AgentMemory(agent_name, supabase)
    if memory_type:
        entries = memory.recall(memory_type, limit=limit)
    else:
        entries = memory.recall_all(limit=limit)
    return {"agent": agent_name, "memories": entries, "count": len(entries)}


@app.get("/api/memory/{agent_name}/performance")
async def get_agent_performance(agent_name: str):
    """Get agent performance insights (vertical conversion data)"""
    from agents.memory import AgentMemory

    memory = AgentMemory(agent_name, supabase)
    insights = memory.get_performance_insights()
    best_verticals = memory.get_best_verticals()
    return {
        "agent": agent_name,
        "verticals": insights,
        "best_verticals": best_verticals,
    }


# ===========================================
# Content Creator Endpoints
# ===========================================

@app.get("/api/content")
async def list_content():
    """List all pending (draft) content"""
    orchestrator = ATLASOrchestrator()
    content = await orchestrator.content_creator.get_pending_content()
    return {"content": content, "count": len(content)}


@app.get("/api/content/stats")
async def content_stats():
    """Get content generation statistics"""
    orchestrator = ATLASOrchestrator()
    return await orchestrator.content_creator.get_content_stats()


class ContentGenerateRequest(BaseModel):
    start_date: Optional[str] = None
    days: int = 7


@app.post("/api/content/generate")
async def trigger_content_generation(
    request: ContentGenerateRequest,
    background_tasks: BackgroundTasks,
):
    """Trigger batch content generation"""
    orchestrator = ATLASOrchestrator()

    if request.start_date:
        start = date.fromisoformat(request.start_date)
    else:
        start = date.today() + timedelta(days=1)

    background_tasks.add_task(
        orchestrator.content_creator.generate_batch,
        start,
        request.days,
    )
    return {
        "status": "content generation started",
        "start_date": start.isoformat(),
        "days": request.days,
    }


# ===========================================
# Scheduler
# ===========================================

def run_scheduler():
    """Background scheduler for automated tasks"""
    orchestrator = ATLASOrchestrator()

    # Discovery: Mon/Wed/Fri at 5 AM
    schedule.every().monday.at("05:00").do(
        lambda: asyncio.run(orchestrator.run_discovery_pipeline())
    )
    schedule.every().wednesday.at("05:00").do(
        lambda: asyncio.run(orchestrator.run_discovery_pipeline())
    )
    schedule.every().friday.at("05:00").do(
        lambda: asyncio.run(orchestrator.run_discovery_pipeline())
    )

    # Orchestration: Daily at 7 AM
    schedule.every().day.at("07:00").do(
        lambda: asyncio.run(orchestrator.run_daily_orchestration())
    )

    # CLOSER pipeline: Daily at 8 AM (after orchestration completes)
    schedule.every().day.at("08:00").do(
        lambda: orchestrator.closer.run_pipeline()
    )

    # CLOSER follow-up check: Also at 2 PM for afternoon follow-ups
    schedule.every().day.at("14:00").do(
        lambda: orchestrator.closer._process_followups()
    )

    # Content generation: Daily at 8 PM AEST (generate next day's content)
    schedule.every().day.at("20:00").do(
        lambda: asyncio.run(
            orchestrator.content_creator.generate_daily_content(
                date.today() + timedelta(days=1)
            )
        )
    )

    while True:
        schedule.run_pending()
        time.sleep(60)

# ===========================================
# Main Entry Point
# ===========================================

if __name__ == "__main__":
    print("=" * 60)
    print(" ATLAS AUTONOMOUS BUSINESS SYSTEM v2.0")
    print("=" * 60)
    print(" Pure Python. No n8n. No workflows.")
    print(" Just intelligent agents working together.")
    print("=" * 60)
    print()
    print(" Agents:")
    print("   * SCOUT           - Opportunity discovery")
    print("   * VAULT           - Budget management ($250/mo)")
    print("   * FORGE           - Landing page builder")
    print("   * MERCURY         - Multi-channel distribution")
    print("   * CLOSER          - Sales pipeline manager")
    print("   * CONTENT_CREATOR - Social media content generation")
    print()
    print(" Endpoints:")
    print("   * http://localhost:8000/                    - System info")
    print("   * http://localhost:8000/api/status          - Current status")
    print("   * http://localhost:8000/api/discover        - Run discovery")
    print("   * http://localhost:8000/api/pipeline        - Pipeline list")
    print("   * http://localhost:8000/api/proposals       - Proposals list")
    print("   * http://localhost:8000/api/outreach        - Outreach list")
    print("   * http://localhost:8000/api/closer/run      - Trigger CLOSER")
    print("   * http://localhost:8000/api/closer/summary  - Pipeline summary")
    print("   * http://localhost:8000/api/content         - Pending content")
    print("   * http://localhost:8000/api/content/stats   - Content stats")
    print("   * http://localhost:8000/api/content/generate - Generate batch")
    print("   * http://localhost:8000/api/memory/{agent}  - Agent memory")
    print("   * http://localhost:8000/api/memory/{agent}/performance - Insights")
    print("   * http://localhost:8000/webhook/budget-check")
    print()
    print(" Schedule:")
    print("   * Discovery: Mon/Wed/Fri at 5:00 AM")
    print("   * Orchestration: Daily at 7:00 AM")
    print("   * CLOSER Pipeline: Daily at 8:00 AM")
    print("   * CLOSER Follow-ups: Daily at 2:00 PM")
    print("   * Content Generation: Daily at 8:00 PM")
    print("=" * 60)

    # Start scheduler in background
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()

    # Run FastAPI (Railway injects PORT env var)
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)