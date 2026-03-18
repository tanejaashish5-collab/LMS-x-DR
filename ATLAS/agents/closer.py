#!/usr/bin/env python3
"""
CLOSER Agent - Sales Pipeline Manager for ATLAS
Qualifies opportunities, generates proposals, tracks pipeline, handles follow-ups.

Cost structure:
- Claude Sonnet proposal generation: ~$0.50-1.00 per proposal
- Claude Haiku qualification: ~$0.01 per opportunity
- VAULT approval required before generating proposals

Pipeline stages:
    discovered -> qualified -> proposed -> responded -> negotiating -> closed_won / closed_lost -> delivering
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from supabase import create_client, Client
import anthropic

from services.email_service import get_email_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('CLOSER')


# ===========================================
# Constants
# ===========================================

PIPELINE_STAGES = [
    "discovered",
    "qualified",
    "proposed",
    "responded",
    "negotiating",
    "closed_won",
    "closed_lost",
    "delivering",
]

STAGE_ORDER = {stage: idx for idx, stage in enumerate(PIPELINE_STAGES)}

MINIMUM_SCORE_FOR_QUALIFICATION = 70

FOLLOWUP_SCHEDULE_DAYS = {
    "followup_1": 3,
    "followup_2": 7,
    "followup_3": 14,
}


# ===========================================
# Data Models
# ===========================================

@dataclass
class QualificationResult:
    """Result from opportunity qualification"""
    qualified: bool
    enrichment: Dict[str, Any]
    reason: str
    estimated_deal_value: float = 0.0
    contact_info: Optional[Dict[str, str]] = None


@dataclass
class ProposalContent:
    """Generated proposal content"""
    executive_summary: str
    problem_statement: str
    proposed_solution: str
    pricing: Dict[str, Any]
    roi_estimate: Dict[str, Any]
    timeline: str
    next_steps: str


@dataclass
class PipelineSummary:
    """Daily pipeline summary"""
    total_deals: int
    by_stage: Dict[str, int]
    total_value: float
    proposals_pending: int
    followups_due: int
    closed_won_value: float
    closed_lost_count: int


# ===========================================
# CLOSER Agent Class
# ===========================================

class CLOSERAgent:
    """
    Sales pipeline agent that converts discoveries into revenue.

    Responsibilities:
    - Qualify high-scoring opportunities (score > 70)
    - Generate personalized proposals with Claude Sonnet
    - Track pipeline stages from discovery to close
    - Generate follow-up emails for non-responsive leads
    - Produce daily pipeline reports
    - Respect VAULT budget limits for all API calls
    """

    def __init__(
        self,
        supabase_url: Optional[str] = None,
        supabase_key: Optional[str] = None,
        anthropic_key: Optional[str] = None,
        vault_agent: Optional[Any] = None,
    ):
        """
        Initialize CLOSER agent.

        Args:
            supabase_url: Supabase project URL
            supabase_key: Supabase anon key
            anthropic_key: Anthropic API key
            vault_agent: VAULT agent instance for budget checks
        """
        # Initialize Supabase
        self.supabase_url = supabase_url or os.getenv('SUPABASE_URL')
        self.supabase_key = supabase_key or os.getenv('SUPABASE_ANON_KEY')

        if not self.supabase_url or not self.supabase_key:
            raise ValueError(
                "SUPABASE_URL and SUPABASE_ANON_KEY environment variables are required"
            )

        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)

        # Initialize Anthropic
        self.anthropic_key = anthropic_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.anthropic_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
        self.client = anthropic.Anthropic(api_key=self.anthropic_key)

        # VAULT integration
        self.vault = vault_agent

        # Email service (real sending via Resend)
        self.email_service = get_email_service(self.supabase)

        logger.info("CLOSER initialized - Ready to close deals")

    # ===========================================
    # Main Pipeline Operations
    # ===========================================

    def run_pipeline(self) -> Dict[str, Any]:
        """
        Run the full pipeline cycle: qualify, propose, follow up.

        Returns:
            Summary of pipeline actions taken.
        """
        logger.info("=" * 60)
        logger.info("CLOSER: Starting pipeline cycle")
        logger.info("=" * 60)

        results: Dict[str, Any] = {
            "qualified": 0,
            "proposals_generated": 0,
            "followups_sent": 0,
            "errors": [],
            "timestamp": datetime.now().isoformat(),
        }

        try:
            # Step 1: Qualify new high-scoring opportunities
            qualified_count = self._qualify_new_opportunities()
            results["qualified"] = qualified_count

            # Step 2: Generate proposals for qualified leads without one
            proposals_count = self._generate_pending_proposals()
            results["proposals_generated"] = proposals_count

            # Step 3: Check for follow-ups due
            followups_count = self._process_followups()
            results["followups_sent"] = followups_count

            # Step 4: Log the run
            self._log_pipeline_run(results)

        except Exception as e:
            logger.error(f"CLOSER: Pipeline cycle error: {e}", exc_info=True)
            results["errors"].append(str(e))

        logger.info(
            f"CLOSER: Pipeline cycle complete - "
            f"Qualified: {results['qualified']}, "
            f"Proposals: {results['proposals_generated']}, "
            f"Follow-ups: {results['followups_sent']}"
        )

        return results

    # ===========================================
    # Step 1: Qualification
    # ===========================================

    def _qualify_new_opportunities(self) -> int:
        """
        Find scored opportunities (score >= 70) not yet in pipeline,
        qualify them with Claude Haiku, and create pipeline entries.

        Returns:
            Number of newly qualified opportunities.
        """
        try:
            # Get high-scoring opportunities not yet in pipeline
            opps = self.supabase.table('atlas_opportunities').select(
                'id, title, description, category, target_vertical, sonnet_score, source_url'
            ).gte(
                'sonnet_score', MINIMUM_SCORE_FOR_QUALIFICATION
            ).eq(
                'status', 'sonnet_scored'
            ).order(
                'sonnet_score', desc=True
            ).limit(10).execute()

            if not opps.data:
                logger.info("CLOSER: No new opportunities to qualify")
                return 0

            # Filter out ones already in pipeline
            opp_ids = [o['id'] for o in opps.data]
            existing = self.supabase.table('atlas_pipeline').select(
                'opportunity_id'
            ).in_('opportunity_id', opp_ids).execute()

            existing_ids = {e['opportunity_id'] for e in (existing.data or [])}
            new_opps = [o for o in opps.data if o['id'] not in existing_ids]

            if not new_opps:
                logger.info("CLOSER: All high-scoring opportunities already in pipeline")
                return 0

            qualified_count = 0
            for opp in new_opps:
                result = self._qualify_opportunity(opp)
                if result.qualified:
                    self._create_pipeline_entry(opp, result)
                    qualified_count += 1

            return qualified_count

        except Exception as e:
            logger.error(f"CLOSER: Qualification error: {e}", exc_info=True)
            return 0

    def _qualify_opportunity(self, opp: Dict[str, Any]) -> QualificationResult:
        """
        Qualify a single opportunity using Claude Haiku for enrichment.

        Args:
            opp: Opportunity data from database.

        Returns:
            QualificationResult with enrichment data.
        """
        try:
            prompt = f"""Analyze this business opportunity for sales outreach qualification.

OPPORTUNITY:
Title: {opp.get('title', '')}
Description: {opp.get('description', '')}
Category: {opp.get('category', '')}
Vertical: {opp.get('target_vertical', '')}
Score: {opp.get('sonnet_score', 0)}/100

TASKS:
1. Identify the specific pain point (one sentence)
2. Estimate the business size (solo/small/medium/large)
3. Estimate deal value in AUD (Basic $997, Pro $2497, Enterprise $4997 -- pick most likely)
4. Identify the most likely job title of the decision maker
5. Determine urgency level (low/medium/high)
6. Write a one-sentence outreach hook

Respond in this exact JSON format:
{{
  "pain_point": "...",
  "business_size": "small",
  "estimated_deal_value": 2497,
  "decision_maker_title": "...",
  "urgency": "medium",
  "outreach_hook": "...",
  "process_name": "...",
  "hours_lost_weekly": 10,
  "qualified": true
}}"""

            message = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )

            response_text = message.content[0].text.strip()

            # Log API call
            self._log_api_call(
                action='qualify_opportunity',
                model='claude-3-haiku-20240307',
                input_tokens=message.usage.input_tokens,
                output_tokens=message.usage.output_tokens,
                status='success'
            )

            # Parse JSON response
            try:
                # Handle potential markdown code blocks
                if response_text.startswith('```'):
                    response_text = response_text.split('```')[1]
                    if response_text.startswith('json'):
                        response_text = response_text[4:]
                enrichment = json.loads(response_text.strip())
            except json.JSONDecodeError:
                logger.warning(f"CLOSER: Failed to parse qualification JSON, using defaults")
                enrichment = {
                    "pain_point": opp.get('title', 'Unknown'),
                    "business_size": "small",
                    "estimated_deal_value": 997,
                    "decision_maker_title": "Business Owner",
                    "urgency": "medium",
                    "outreach_hook": f"Saw your post about {opp.get('title', 'automation')}",
                    "process_name": "manual process",
                    "hours_lost_weekly": 10,
                    "qualified": True,
                }

            is_qualified = enrichment.get('qualified', True)

            return QualificationResult(
                qualified=is_qualified,
                enrichment=enrichment,
                reason="Score meets threshold and Haiku qualified" if is_qualified else "Haiku rejected",
                estimated_deal_value=float(enrichment.get('estimated_deal_value', 997)),
            )

        except Exception as e:
            logger.error(f"CLOSER: Qualification failed for {opp.get('id')}: {e}")
            return QualificationResult(
                qualified=False,
                enrichment={},
                reason=f"Qualification error: {str(e)}",
            )

    def _create_pipeline_entry(
        self,
        opp: Dict[str, Any],
        qual: QualificationResult,
    ) -> Optional[str]:
        """
        Create a pipeline entry for a qualified opportunity.

        Args:
            opp: Opportunity data.
            qual: Qualification result.

        Returns:
            Pipeline entry ID or None on failure.
        """
        try:
            enrichment = qual.enrichment
            pipeline_data = {
                'opportunity_id': opp['id'],
                'stage': 'qualified',
                'qualified_at': datetime.now().isoformat(),
                'deal_value': qual.estimated_deal_value,
                'currency': 'AUD',
                'notes': json.dumps(enrichment),
                'company_name': enrichment.get('company_name', ''),
                'contact_name': enrichment.get('decision_maker_title', ''),
                'followup_count': 0,
            }

            result = self.supabase.table('atlas_pipeline').insert(
                pipeline_data
            ).execute()

            if result.data:
                pipeline_id = result.data[0]['id']
                logger.info(
                    f"CLOSER: Pipeline entry created - {pipeline_id} "
                    f"(${qual.estimated_deal_value} AUD)"
                )

                # Update opportunity status
                self.supabase.table('atlas_opportunities').update({
                    'status': 'in_pipeline'
                }).eq('id', opp['id']).execute()

                return pipeline_id

            return None

        except Exception as e:
            logger.error(f"CLOSER: Failed to create pipeline entry: {e}")
            return None

    # ===========================================
    # Step 2: Proposal Generation
    # ===========================================

    def _generate_pending_proposals(self) -> int:
        """
        Generate proposals for qualified pipeline entries that lack one.

        Returns:
            Number of proposals generated.
        """
        try:
            # Get qualified entries with no proposal
            pipeline_entries = self.supabase.table('atlas_pipeline').select(
                '*, atlas_opportunities(*)'
            ).eq('stage', 'qualified').execute()

            if not pipeline_entries.data:
                logger.info("CLOSER: No qualified leads awaiting proposals")
                return 0

            # Check which already have proposals
            pipeline_ids = [p['id'] for p in pipeline_entries.data]
            existing_proposals = self.supabase.table('atlas_proposals').select(
                'pipeline_id'
            ).in_('pipeline_id', pipeline_ids).execute()

            has_proposal = {p['pipeline_id'] for p in (existing_proposals.data or [])}
            needs_proposal = [
                p for p in pipeline_entries.data
                if p['id'] not in has_proposal
            ]

            if not needs_proposal:
                logger.info("CLOSER: All qualified leads already have proposals")
                return 0

            generated = 0
            for entry in needs_proposal:
                success = self.generate_proposal(entry)
                if success:
                    generated += 1

            return generated

        except Exception as e:
            logger.error(f"CLOSER: Proposal generation error: {e}", exc_info=True)
            return 0

    def generate_proposal(self, pipeline_entry: Dict[str, Any]) -> bool:
        """
        Generate a personalized proposal for a pipeline entry using Claude Sonnet.

        Args:
            pipeline_entry: Pipeline entry with nested opportunity data.

        Returns:
            True if proposal generated successfully.
        """
        pipeline_id = pipeline_entry['id']
        opportunity = pipeline_entry.get('atlas_opportunities', {})
        notes = {}
        try:
            notes = json.loads(pipeline_entry.get('notes', '{}') or '{}')
        except (json.JSONDecodeError, TypeError):
            pass

        # Budget check via VAULT
        if self.vault:
            budget_ok = self._request_budget(
                amount=1.00,
                description=f"Generate proposal for pipeline {pipeline_id}",
            )
            if not budget_ok:
                logger.warning(f"CLOSER: Budget denied for proposal {pipeline_id}")
                return False

        try:
            # Determine vertical for template selection
            vertical = (
                opportunity.get('target_vertical', '')
                or notes.get('vertical', '')
                or 'general'
            ).lower()

            # Load the right proposal template context
            template_context = self._get_template_context(vertical)

            prompt = f"""You are a senior business development consultant. Generate a compelling, personalized proposal for this automation service opportunity.

OPPORTUNITY:
Title: {opportunity.get('title', 'Business Automation')}
Description: {opportunity.get('description', '')}
Vertical: {opportunity.get('target_vertical', 'General')}
Score: {opportunity.get('sonnet_score', 0)}/100

QUALIFICATION DATA:
Pain Point: {notes.get('pain_point', 'Manual processes')}
Business Size: {notes.get('business_size', 'small')}
Decision Maker: {notes.get('decision_maker_title', 'Business Owner')}
Urgency: {notes.get('urgency', 'medium')}
Hours Lost Weekly: {notes.get('hours_lost_weekly', 10)}
Process: {notes.get('process_name', 'manual process')}

PRICING TIERS (AUD):
- Basic ($997): Single workflow, 2 integrations, 30-day warranty
- Pro ($2,497): Up to 3 workflows, 5 integrations, monitoring, 90-day warranty
- Enterprise ($4,997): Unlimited workflows, custom dev, SLA, 12-month warranty

TEMPLATE CONTEXT:
{template_context}

Generate a proposal in this exact JSON format:
{{
  "executive_summary": "2-3 sentences referencing their specific pain point",
  "problem_statement": "3-5 bullet points about their specific challenges",
  "proposed_solution": "What we will build, which tools we connect, how it works",
  "pricing_recommendation": "basic|pro|enterprise",
  "pricing_justification": "Why this tier is right for them",
  "roi_estimate": {{
    "hours_saved_weekly": 10,
    "hourly_rate_aud": 50,
    "monthly_savings_aud": 2000,
    "annual_savings_aud": 24000,
    "payback_weeks": 4
  }},
  "timeline": "Week-by-week delivery plan",
  "next_steps": "Clear call to action",
  "intro_paragraph": "Personalized opening paragraph for the proposal email"
}}

Make it specific to their situation. No generic filler. Sound human, not AI."""

            message = self.client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )

            response_text = message.content[0].text.strip()

            # Calculate cost
            cost = self._calculate_sonnet_cost(
                message.usage.input_tokens,
                message.usage.output_tokens,
            )

            # Log API call
            self._log_api_call(
                action='generate_proposal',
                model='claude-3-5-sonnet-20240620',
                input_tokens=message.usage.input_tokens,
                output_tokens=message.usage.output_tokens,
                status='success',
                cost=cost,
            )

            # Parse response
            try:
                if response_text.startswith('```'):
                    response_text = response_text.split('```')[1]
                    if response_text.startswith('json'):
                        response_text = response_text[4:]
                proposal_data = json.loads(response_text.strip())
            except json.JSONDecodeError:
                logger.error("CLOSER: Failed to parse proposal JSON from Sonnet")
                return False

            # Build pricing structure
            pricing = {
                "basic": {"price": 997, "currency": "AUD"},
                "pro": {"price": 2497, "currency": "AUD"},
                "enterprise": {"price": 4997, "currency": "AUD"},
                "recommended": proposal_data.get('pricing_recommendation', 'pro'),
                "justification": proposal_data.get('pricing_justification', ''),
            }

            roi_estimate = proposal_data.get('roi_estimate', {})

            # Save proposal to database
            proposal_record = {
                'pipeline_id': pipeline_id,
                'opportunity_id': opportunity.get('id'),
                'proposal_type': 'initial',
                'content': json.dumps(proposal_data),
                'pricing': json.dumps(pricing),
                'roi_estimate': json.dumps(roi_estimate),
                'status': 'draft',
            }

            result = self.supabase.table('atlas_proposals').insert(
                proposal_record
            ).execute()

            if result.data:
                logger.info(
                    f"CLOSER: Proposal generated for {pipeline_id} "
                    f"(recommended: {pricing['recommended']}, cost: ${cost:.2f})"
                )

                # Advance pipeline stage to proposed
                self._advance_stage(pipeline_id, 'proposed')
                return True

            return False

        except Exception as e:
            logger.error(f"CLOSER: Proposal generation failed: {e}", exc_info=True)
            return False

    def _get_template_context(self, vertical: str) -> str:
        """
        Load proposal template context for a vertical.

        Args:
            vertical: Business vertical name.

        Returns:
            Template context string for the prompt.
        """
        try:
            from templates.proposals import VERTICAL_TEMPLATES, GENERIC_PROPOSAL

            # Find matching template
            template_data = VERTICAL_TEMPLATES.get(vertical, GENERIC_PROPOSAL)
            tmpl = template_data.get('template', {})

            return (
                f"Vertical: {template_data.get('vertical', 'generic')}\n"
                f"Solution style: {tmpl.get('proposed_solution', '')[:200]}\n"
                f"Timeline style: {tmpl.get('timeline', '')[:200]}"
            )
        except ImportError:
            return f"Vertical: {vertical}"

    # ===========================================
    # Step 3: Follow-ups
    # ===========================================

    def _process_followups(self) -> int:
        """
        Check for pipeline entries needing follow-up and generate emails.

        Returns:
            Number of follow-ups generated.
        """
        try:
            # Get proposed entries that need follow-up
            proposed = self.supabase.table('atlas_pipeline').select(
                '*, atlas_opportunities(*)'
            ).eq('stage', 'proposed').execute()

            if not proposed.data:
                return 0

            followup_count = 0
            now = datetime.now()

            for entry in proposed.data:
                proposed_at = entry.get('proposed_at')
                if not proposed_at:
                    continue

                proposed_date = datetime.fromisoformat(
                    proposed_at.replace('Z', '+00:00')
                ).replace(tzinfo=None)
                days_since_proposal = (now - proposed_date).days
                current_followup_count = entry.get('followup_count', 0)
                last_followup = entry.get('last_followup_at')

                # Determine which follow-up is due
                followup_type = None
                if current_followup_count == 0 and days_since_proposal >= 3:
                    followup_type = "followup_1"
                elif current_followup_count == 1 and days_since_proposal >= 7:
                    followup_type = "followup_2"
                elif current_followup_count == 2 and days_since_proposal >= 14:
                    followup_type = "followup_3"

                if followup_type:
                    success = self._generate_followup(entry, followup_type)
                    if success:
                        followup_count += 1

                # Auto-close after 3 follow-ups with no response (21+ days)
                if current_followup_count >= 3 and days_since_proposal >= 21:
                    self._advance_stage(entry['id'], 'closed_lost')
                    self.supabase.table('atlas_pipeline').update({
                        'notes': json.dumps({
                            **json.loads(entry.get('notes', '{}') or '{}'),
                            'close_reason': 'No response after 3 follow-ups',
                        })
                    }).eq('id', entry['id']).execute()
                    logger.info(
                        f"CLOSER: Auto-closed {entry['id']} - no response after 3 follow-ups"
                    )

            return followup_count

        except Exception as e:
            logger.error(f"CLOSER: Follow-up processing error: {e}", exc_info=True)
            return 0

    def _generate_followup(
        self,
        pipeline_entry: Dict[str, Any],
        followup_type: str,
    ) -> bool:
        """
        Generate a follow-up email for a pipeline entry.

        Args:
            pipeline_entry: Pipeline entry data.
            followup_type: One of followup_1, followup_2, followup_3.

        Returns:
            True if follow-up generated successfully.
        """
        pipeline_id = pipeline_entry['id']
        opportunity = pipeline_entry.get('atlas_opportunities', {})
        notes = {}
        try:
            notes = json.loads(pipeline_entry.get('notes', '{}') or '{}')
        except (json.JSONDecodeError, TypeError):
            pass

        try:
            # Load email template
            from templates.emails import (
                FOLLOWUP_1_EMAIL,
                FOLLOWUP_2_EMAIL,
                FOLLOWUP_3_EMAIL,
            )

            templates = {
                "followup_1": FOLLOWUP_1_EMAIL,
                "followup_2": FOLLOWUP_2_EMAIL,
                "followup_3": FOLLOWUP_3_EMAIL,
            }

            template = templates.get(followup_type, FOLLOWUP_1_EMAIL)

            # Build substitution data
            sub_data = {
                'contact_name': pipeline_entry.get('contact_name', 'there'),
                'company_name': pipeline_entry.get('company_name', 'your company'),
                'pain_point': notes.get('pain_point', 'manual processes'),
                'process_name': notes.get('process_name', 'manual tasks'),
                'vertical': opportunity.get('target_vertical', 'your industry'),
                'basic_price': '997',
                'payback_weeks': str(notes.get('payback_weeks', 4)),
            }

            subject = template['subject']
            body = template['body']
            for key, value in sub_data.items():
                subject = subject.replace('{' + key + '}', str(value))
                body = body.replace('{' + key + '}', str(value))

            # Save outreach record
            to_email = pipeline_entry.get('contact_email', '')
            outreach_data = {
                'pipeline_id': pipeline_id,
                'email_type': followup_type,
                'subject': subject,
                'body': body,
                'to_email': to_email,
                'status': 'draft',
            }

            self.supabase.table('atlas_outreach').insert(outreach_data).execute()

            # Send real email via Resend
            if to_email:
                email_result = self.email_service.send_email_sync(
                    to=to_email,
                    subject=subject,
                    body=body,
                    pipeline_id=pipeline_id,
                    email_type=followup_type,
                )
                if email_result.success:
                    # Update outreach status to sent
                    self.supabase.table('atlas_outreach').update({
                        'status': 'sent',
                        'sent_at': datetime.now().isoformat(),
                    }).eq('pipeline_id', pipeline_id).eq(
                        'email_type', followup_type
                    ).execute()
                    logger.info(
                        f"CLOSER: {followup_type} SENT to {to_email} "
                        f"(message_id={email_result.message_id})"
                    )
                else:
                    logger.warning(
                        f"CLOSER: {followup_type} send failed for {to_email}: "
                        f"{email_result.error}"
                    )

            # Update pipeline follow-up tracking
            self.supabase.table('atlas_pipeline').update({
                'followup_count': (pipeline_entry.get('followup_count', 0) + 1),
                'last_followup_at': datetime.now().isoformat(),
            }).eq('id', pipeline_id).execute()

            logger.info(
                f"CLOSER: {followup_type} generated for {pipeline_id}"
            )
            return True

        except ImportError:
            logger.warning("CLOSER: Email templates not available, generating with Haiku")
            return self._generate_followup_with_haiku(pipeline_entry, followup_type)
        except Exception as e:
            logger.error(f"CLOSER: Follow-up generation failed: {e}")
            return False

    def _generate_followup_with_haiku(
        self,
        pipeline_entry: Dict[str, Any],
        followup_type: str,
    ) -> bool:
        """
        Fallback: generate follow-up email with Claude Haiku.

        Args:
            pipeline_entry: Pipeline entry data.
            followup_type: Type of follow-up.

        Returns:
            True if generated successfully.
        """
        pipeline_id = pipeline_entry['id']
        opportunity = pipeline_entry.get('atlas_opportunities', {})
        notes = {}
        try:
            notes = json.loads(pipeline_entry.get('notes', '{}') or '{}')
        except (json.JSONDecodeError, TypeError):
            pass

        try:
            followup_number = followup_type.split('_')[1]
            prompt = f"""Write a short follow-up email for a business automation proposal.

Context:
- Their pain point: {notes.get('pain_point', 'manual processes')}
- Vertical: {opportunity.get('target_vertical', 'general')}
- This is follow-up #{followup_number}
- Company: {pipeline_entry.get('company_name', 'their company')}

Requirements:
- Under 100 words
- Professional but friendly
- Add new value (case study reference, insight, or tip)
- Soft CTA
- Sign off as Ashish

Return JSON: {{"subject": "...", "body": "..."}}"""

            message = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=400,
                messages=[{"role": "user", "content": prompt}]
            )

            self._log_api_call(
                action=f'generate_{followup_type}',
                model='claude-3-haiku-20240307',
                input_tokens=message.usage.input_tokens,
                output_tokens=message.usage.output_tokens,
                status='success',
            )

            response_text = message.content[0].text.strip()
            try:
                if response_text.startswith('```'):
                    response_text = response_text.split('```')[1]
                    if response_text.startswith('json'):
                        response_text = response_text[4:]
                email_data = json.loads(response_text.strip())
            except json.JSONDecodeError:
                email_data = {
                    "subject": f"Following up on your automation proposal",
                    "body": response_text,
                }

            to_email = pipeline_entry.get('contact_email', '')
            email_subject = email_data.get('subject', '')
            email_body = email_data.get('body', '')

            outreach_data = {
                'pipeline_id': pipeline_id,
                'email_type': followup_type,
                'subject': email_subject,
                'body': email_body,
                'to_email': to_email,
                'status': 'draft',
            }

            self.supabase.table('atlas_outreach').insert(outreach_data).execute()

            # Send real email via Resend
            if to_email:
                email_result = self.email_service.send_email_sync(
                    to=to_email,
                    subject=email_subject,
                    body=email_body,
                    pipeline_id=pipeline_id,
                    email_type=followup_type,
                )
                if email_result.success:
                    self.supabase.table('atlas_outreach').update({
                        'status': 'sent',
                        'sent_at': datetime.now().isoformat(),
                    }).eq('pipeline_id', pipeline_id).eq(
                        'email_type', followup_type
                    ).execute()
                    logger.info(
                        f"CLOSER: {followup_type} SENT via Haiku to {to_email} "
                        f"(message_id={email_result.message_id})"
                    )
                else:
                    logger.warning(
                        f"CLOSER: {followup_type} Haiku send failed: {email_result.error}"
                    )

            self.supabase.table('atlas_pipeline').update({
                'followup_count': (pipeline_entry.get('followup_count', 0) + 1),
                'last_followup_at': datetime.now().isoformat(),
            }).eq('id', pipeline_id).execute()

            logger.info(f"CLOSER: {followup_type} generated via Haiku for {pipeline_id}")
            return True

        except Exception as e:
            logger.error(f"CLOSER: Haiku follow-up generation failed: {e}")
            return False

    # ===========================================
    # Pipeline Stage Management
    # ===========================================

    def advance_pipeline(self, pipeline_id: str) -> Dict[str, Any]:
        """
        Advance a pipeline entry to the next stage.

        Args:
            pipeline_id: Pipeline entry ID.

        Returns:
            Dict with new stage and status.
        """
        try:
            entry = self.supabase.table('atlas_pipeline').select(
                'id, stage'
            ).eq('id', pipeline_id).execute()

            if not entry.data:
                return {"error": "Pipeline entry not found"}

            current_stage = entry.data[0]['stage']
            current_idx = STAGE_ORDER.get(current_stage, 0)

            # Determine next stage
            if current_stage == 'closed_won':
                next_stage = 'delivering'
            elif current_stage in ('closed_lost', 'delivering'):
                return {"error": f"Cannot advance from {current_stage}"}
            else:
                next_idx = current_idx + 1
                if next_idx >= len(PIPELINE_STAGES):
                    return {"error": "Already at final stage"}
                next_stage = PIPELINE_STAGES[next_idx]

            self._advance_stage(pipeline_id, next_stage)

            return {
                "pipeline_id": pipeline_id,
                "previous_stage": current_stage,
                "new_stage": next_stage,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"CLOSER: Stage advance error: {e}")
            return {"error": str(e)}

    def set_pipeline_stage(
        self,
        pipeline_id: str,
        stage: str,
    ) -> Dict[str, Any]:
        """
        Set a specific pipeline stage.

        Args:
            pipeline_id: Pipeline entry ID.
            stage: Target stage name.

        Returns:
            Result dict.
        """
        if stage not in PIPELINE_STAGES:
            return {"error": f"Invalid stage: {stage}"}

        try:
            self._advance_stage(pipeline_id, stage)
            return {
                "pipeline_id": pipeline_id,
                "new_stage": stage,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            return {"error": str(e)}

    def _advance_stage(self, pipeline_id: str, new_stage: str) -> None:
        """
        Update pipeline entry to a new stage with timestamp.

        Args:
            pipeline_id: Pipeline entry ID.
            new_stage: New stage name.
        """
        update_data: Dict[str, Any] = {'stage': new_stage}

        # Set stage-specific timestamps
        timestamp_fields = {
            'qualified': 'qualified_at',
            'proposed': 'proposed_at',
            'responded': 'responded_at',
            'closed_won': 'closed_at',
            'closed_lost': 'closed_at',
        }

        ts_field = timestamp_fields.get(new_stage)
        if ts_field:
            update_data[ts_field] = datetime.now().isoformat()

        self.supabase.table('atlas_pipeline').update(
            update_data
        ).eq('id', pipeline_id).execute()

        # Log stage change
        self.supabase.table('atlas_communications').insert({
            'pipeline_id': pipeline_id,
            'channel': 'system',
            'direction': 'outbound',
            'subject': f'Stage changed to {new_stage}',
            'content': f'Pipeline stage advanced to {new_stage}',
            'sentiment': 'neutral',
        }).execute()

        logger.info(f"CLOSER: Pipeline {pipeline_id} -> {new_stage}")

    # ===========================================
    # Reporting
    # ===========================================

    def get_pipeline_summary(self) -> Dict[str, Any]:
        """
        Generate a summary of the current pipeline state.

        Returns:
            Pipeline summary dict.
        """
        try:
            # Get all pipeline entries
            all_entries = self.supabase.table('atlas_pipeline').select(
                'id, stage, deal_value, followup_count, proposed_at, company_name'
            ).execute()

            entries = all_entries.data or []

            # Count by stage
            by_stage: Dict[str, int] = {}
            total_value = 0.0
            closed_won_value = 0.0
            closed_lost_count = 0
            followups_due = 0

            now = datetime.now()

            for entry in entries:
                stage = entry.get('stage', 'discovered')
                by_stage[stage] = by_stage.get(stage, 0) + 1

                deal_val = float(entry.get('deal_value', 0) or 0)
                if stage not in ('closed_lost',):
                    total_value += deal_val

                if stage == 'closed_won':
                    closed_won_value += deal_val
                elif stage == 'closed_lost':
                    closed_lost_count += 1

                # Check if follow-up is due
                if stage == 'proposed':
                    proposed_at = entry.get('proposed_at')
                    fc = entry.get('followup_count', 0)
                    if proposed_at:
                        proposed_date = datetime.fromisoformat(
                            proposed_at.replace('Z', '+00:00')
                        ).replace(tzinfo=None)
                        days = (now - proposed_date).days
                        if (fc == 0 and days >= 3) or (fc == 1 and days >= 7) or (fc == 2 and days >= 14):
                            followups_due += 1

            # Count draft proposals
            proposals_pending = 0
            try:
                pending_result = self.supabase.table('atlas_proposals').select(
                    'id', count='exact'
                ).eq('status', 'draft').execute()
                proposals_pending = pending_result.count or 0
            except Exception:
                pass

            summary = {
                "total_deals": len(entries),
                "by_stage": by_stage,
                "total_pipeline_value": total_value,
                "closed_won_value": closed_won_value,
                "closed_lost_count": closed_lost_count,
                "proposals_pending": proposals_pending,
                "followups_due": followups_due,
                "timestamp": datetime.now().isoformat(),
            }

            return summary

        except Exception as e:
            logger.error(f"CLOSER: Pipeline summary error: {e}")
            return {"error": str(e)}

    def get_daily_report(self) -> str:
        """
        Generate a text-based daily pipeline report.

        Returns:
            Formatted report string.
        """
        summary = self.get_pipeline_summary()

        if "error" in summary:
            return f"CLOSER Daily Report Error: {summary['error']}"

        by_stage = summary.get('by_stage', {})

        report = f"""
CLOSER Daily Pipeline Report
Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}

Pipeline Overview:
  Total Deals: {summary['total_deals']}
  Total Pipeline Value: ${summary['total_pipeline_value']:,.2f} AUD
  Closed Won Value: ${summary['closed_won_value']:,.2f} AUD
  Closed Lost: {summary['closed_lost_count']}

Stage Breakdown:
  Discovered:   {by_stage.get('discovered', 0)}
  Qualified:    {by_stage.get('qualified', 0)}
  Proposed:     {by_stage.get('proposed', 0)}
  Responded:    {by_stage.get('responded', 0)}
  Negotiating:  {by_stage.get('negotiating', 0)}
  Closed Won:   {by_stage.get('closed_won', 0)}
  Closed Lost:  {by_stage.get('closed_lost', 0)}
  Delivering:   {by_stage.get('delivering', 0)}

Actions Needed:
  Proposals Pending: {summary['proposals_pending']}
  Follow-ups Due:    {summary['followups_due']}
"""

        return report

    # ===========================================
    # Budget Integration with VAULT
    # ===========================================

    def _request_budget(self, amount: float, description: str) -> bool:
        """
        Request budget from VAULT before expensive operations.

        Args:
            amount: Estimated cost in USD.
            description: What the budget is for.

        Returns:
            True if approved, False if denied.
        """
        if not self.vault:
            logger.warning("CLOSER: No VAULT agent configured, proceeding without budget check")
            return True

        try:
            from agents.vault import BudgetRequest

            budget_request = BudgetRequest(
                amount=amount,
                agent="closer",
                description=description,
                type="api_call",
            )

            result = self.vault.check_budget(budget_request)

            if result['approved']:
                logger.info(f"CLOSER: Budget approved - ${amount:.2f}")
                return True
            else:
                logger.warning(
                    f"CLOSER: Budget denied - {result.get('reason', 'Unknown')}"
                )
                return False

        except Exception as e:
            logger.error(f"CLOSER: Budget request failed: {e}")
            return False

    # ===========================================
    # Logging & Analytics
    # ===========================================

    def _log_api_call(
        self,
        action: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        status: str,
        cost: Optional[float] = None,
    ) -> None:
        """Log API call to agent logs."""
        try:
            if cost is None:
                if 'haiku' in model:
                    cost = (input_tokens * 0.00025 + output_tokens * 0.00125) / 1000
                else:
                    cost = (input_tokens * 0.003 + output_tokens * 0.015) / 1000

            self.supabase.table('atlas_agent_logs').insert({
                'agent': 'closer',
                'action': action,
                'model_used': model,
                'tokens_in': input_tokens,
                'tokens_out': output_tokens,
                'cost_usd': cost,
                'status': status,
            }).execute()

        except Exception as e:
            logger.error(f"CLOSER: Failed to log API call: {e}")

    def _log_pipeline_run(self, results: Dict[str, Any]) -> None:
        """Log pipeline run summary."""
        try:
            self.supabase.table('atlas_agent_logs').insert({
                'agent': 'closer',
                'action': 'pipeline_run',
                'input': json.dumps({
                    'qualified': results.get('qualified', 0),
                    'proposals': results.get('proposals_generated', 0),
                    'followups': results.get('followups_sent', 0),
                }),
                'output': json.dumps(results),
                'status': 'success' if not results.get('errors') else 'partial',
            }).execute()

        except Exception as e:
            logger.error(f"CLOSER: Failed to log pipeline run: {e}")

    def _calculate_sonnet_cost(
        self,
        input_tokens: int,
        output_tokens: int,
    ) -> float:
        """
        Calculate cost for Claude Sonnet API call.

        Pricing:
        - Input: $3.00 per 1M tokens
        - Output: $15.00 per 1M tokens
        """
        input_cost = (input_tokens / 1_000_000) * 3.00
        output_cost = (output_tokens / 1_000_000) * 15.00
        return input_cost + output_cost

    # ===========================================
    # Pipeline Stats
    # ===========================================

    def get_pipeline_stats(self) -> Dict[str, Any]:
        """Get overall pipeline statistics."""
        try:
            summary = self.get_pipeline_summary()

            # Get recent proposals
            recent_proposals = self.supabase.table('atlas_proposals').select(
                'id, pipeline_id, status, created_at'
            ).order('created_at', desc=True).limit(5).execute()

            # Get recent outreach
            recent_outreach = self.supabase.table('atlas_outreach').select(
                'id, pipeline_id, email_type, status, created_at'
            ).order('created_at', desc=True).limit(5).execute()

            return {
                **summary,
                'recent_proposals': recent_proposals.data or [],
                'recent_outreach': recent_outreach.data or [],
            }

        except Exception as e:
            logger.error(f"CLOSER: Failed to get stats: {e}")
            return {'error': str(e)}


# ===========================================
# Standalone Testing
# ===========================================

def main() -> None:
    """Test CLOSER agent functionality."""
    print("=" * 60)
    print(" CLOSER Agent - Sales Pipeline Manager")
    print("=" * 60)

    closer = CLOSERAgent()

    # Get pipeline summary
    print("\n1. Current Pipeline Summary:")
    summary = closer.get_pipeline_summary()
    if 'error' not in summary:
        print(f"   Total Deals: {summary['total_deals']}")
        print(f"   Pipeline Value: ${summary['total_pipeline_value']:,.2f} AUD")
        print(f"   Closed Won: ${summary['closed_won_value']:,.2f} AUD")
        print(f"   Follow-ups Due: {summary['followups_due']}")
        print(f"   Stages: {summary['by_stage']}")
    else:
        print(f"   Error: {summary['error']}")

    # Get daily report
    print("\n2. Daily Report:")
    report = closer.get_daily_report()
    print(report)

    print("\n3. Running Pipeline Cycle:")
    results = closer.run_pipeline()
    print(f"   Qualified: {results['qualified']}")
    print(f"   Proposals: {results['proposals_generated']}")
    print(f"   Follow-ups: {results['followups_sent']}")
    if results['errors']:
        print(f"   Errors: {results['errors']}")

    print("\n" + "=" * 60)
    print(" CLOSER agent ready for ATLAS orchestrator")
    print("=" * 60)


if __name__ == "__main__":
    main()
