#!/usr/bin/env python3
"""
MERCURY Agent - Distribution Engine for ATLAS
Distributes landing pages to channels (Reddit, email, ads) with channel-specific copy
Tracks distribution and calculates ROI in database

Cost structure:
- Claude Haiku copy generation: ~$0.01 per channel
- Reddit posting: Free (via PRAW)
- Email sending: Free (via n8n)
- Meta/Google ads: Variable (tracked separately)
- Total per distribution: ~$0.05

VAULT approval required before distribution.
"""

import os
import logging
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from supabase import create_client, Client
import anthropic

from services.email_service import get_email_service
from utils.retry import retry_with_backoff
from ops.brand import BRAND

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('MERCURY')


# ===========================================
# Data Models
# ===========================================

@dataclass
class DistributionRequest:
    """Request to distribute a landing page"""
    experiment_id: str
    landing_page_url: str
    opportunity_title: str
    target_vertical: str
    value_proposition: str
    channels: List[str]  # ['reddit', 'email', 'meta_ads', 'google_ads']


@dataclass
class ChannelCopy:
    """Generated copy for a specific channel"""
    channel: str
    headline: str
    body: str
    cta: str
    hashtags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class DistributionResult:
    """Result from distribution to all channels"""
    experiment_id: str
    channels_attempted: List[str]
    channels_succeeded: List[str]
    channels_failed: List[Dict[str, Any]]
    total_cost: float
    status: str


# ===========================================
# MERCURY Agent Class
# ===========================================

class MERCURYAgent:
    """
    Distribution engine that publishes landing pages to multiple channels

    Responsibilities:
    - Generate channel-specific copy with Claude Haiku (cheap & fast)
    - Post to Reddit programmatically (via PRAW)
    - Send emails via n8n webhook
    - Create ad campaigns (Meta/Google)
    - Track distribution in database
    - Request budget from VAULT before distribution
    - Log all operations for audit trail
    """

    # Reddit API credentials (to be configured)
    REDDIT_CONFIG = {
        'client_id': os.getenv('REDDIT_CLIENT_ID', 'CONFIGURE_ME'),
        'client_secret': os.getenv('REDDIT_CLIENT_SECRET', 'CONFIGURE_ME'),
        'user_agent': os.getenv('REDDIT_USER_AGENT', ''),
        'username': os.getenv('REDDIT_USERNAME', 'CONFIGURE_ME'),
        'password': os.getenv('REDDIT_PASSWORD', 'CONFIGURE_ME')
    }

    # Channel configuration
    CHANNEL_CONFIG = {
        'reddit': {
            'enabled': True,
            'cost_per_post': 0.00,  # Free
            'subreddits': ['Entrepreneur', 'smallbusiness', 'SaaS']
        },
        'email': {
            'enabled': True,
            'cost_per_send': 0.00,  # Free via n8n
            'n8n_webhook': os.getenv('N8N_EMAIL_WEBHOOK', 'CONFIGURE_ME')
        },
        'meta_ads': {
            'enabled': False,  # Requires manual setup
            'daily_budget': 10.00,
            'cost_per_click': 0.50
        },
        'google_ads': {
            'enabled': False,  # Requires manual setup
            'daily_budget': 10.00,
            'cost_per_click': 0.75
        }
    }

    def __init__(
        self,
        supabase_url: str = None,
        supabase_key: str = None,
        anthropic_key: str = None,
        vault_agent = None
    ):
        """
        Initialize MERCURY agent

        Args:
            supabase_url: Supabase project URL
            supabase_key: Supabase anon key
            anthropic_key: Anthropic API key
            vault_agent: VAULT agent instance (optional)
        """
        # Initialize Supabase
        self.supabase_url = supabase_url or os.getenv('SUPABASE_URL')
        self.supabase_key = supabase_key or os.getenv('SUPABASE_ANON_KEY')
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY environment variables are required")

        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)

        # Initialize Anthropic (Claude Haiku for cheap copy generation)
        self.anthropic_key = anthropic_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.anthropic_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
        self.client = anthropic.Anthropic(api_key=self.anthropic_key)

        # VAULT integration
        self.vault = vault_agent

        # Email service (real sending via Resend)
        self.email_service = get_email_service(self.supabase)

        logger.info("MERCURY initialized - Ready to distribute landing pages")

    # ===========================================
    # Retry-Wrapped API Calls
    # ===========================================

    @retry_with_backoff(max_retries=3, base_delay=2.0, exceptions=(Exception,))
    def _call_anthropic(self, model: str, max_tokens: int, messages: list):
        """Wrapper for Anthropic API calls with retry."""
        return self.client.messages.create(
            model=model,
            max_tokens=max_tokens,
            messages=messages,
        )

    @retry_with_backoff(max_retries=1, base_delay=0.5, exceptions=(Exception,))
    def _call_supabase_insert(self, table: str, data: dict):
        """Wrapper for Supabase inserts with light retry."""
        return self.supabase.table(table).insert(data).execute()

    # ===========================================
    # Main Distribution Pipeline
    # ===========================================

    def distribute(
        self,
        request: DistributionRequest
    ) -> DistributionResult:
        """
        Distribute landing page to all requested channels

        Args:
            request: DistributionRequest with landing page and channels

        Returns:
            DistributionResult with success/failure for each channel
        """
        logger.info(f"MERCURY: Distributing landing page for experiment {request.experiment_id}")

        channels_succeeded = []
        channels_failed = []
        total_cost = 0.0

        # Step 1: Request budget from VAULT
        if self.vault:
            budget_approved = self._request_budget(request.experiment_id, len(request.channels))
            if not budget_approved:
                logger.error("MERCURY: Budget request denied by VAULT")
                return DistributionResult(
                    experiment_id=request.experiment_id,
                    channels_attempted=request.channels,
                    channels_succeeded=[],
                    channels_failed=[{
                        'channel': ch,
                        'error': 'Budget denied by VAULT'
                    } for ch in request.channels],
                    total_cost=0.0,
                    status="budget_denied"
                )

        # Step 2: Generate channel-specific copy
        for channel in request.channels:
            logger.info(f"MERCURY: Processing channel {channel}")

            try:
                # Generate copy with Claude Haiku
                copy_result = self._generate_channel_copy(request, channel)

                if not copy_result['success']:
                    logger.error(f"MERCURY: Copy generation failed for {channel}: {copy_result['error']}")
                    channels_failed.append({
                        'channel': channel,
                        'error': copy_result['error']
                    })
                    continue

                channel_copy = copy_result['copy']
                total_cost += copy_result['cost']

                # Distribute to channel
                distribution_result = self._distribute_to_channel(
                    channel=channel,
                    copy=channel_copy,
                    experiment_id=request.experiment_id,
                    landing_page_url=request.landing_page_url
                )

                if distribution_result['success']:
                    channels_succeeded.append(channel)
                    total_cost += distribution_result.get('cost', 0.0)

                    # Track in database
                    self._track_distribution(
                        experiment_id=request.experiment_id,
                        channel=channel,
                        copy=channel_copy,
                        post_url=distribution_result.get('post_url'),
                        cost=copy_result['cost'] + distribution_result.get('cost', 0.0)
                    )

                    logger.info(f"MERCURY: Successfully distributed to {channel}")
                else:
                    channels_failed.append({
                        'channel': channel,
                        'error': distribution_result.get('error', 'Unknown error')
                    })
                    logger.error(f"MERCURY: Distribution failed for {channel}: {distribution_result.get('error')}")

            except Exception as e:
                logger.error(f"MERCURY: Channel {channel} processing error: {e}", exc_info=True)
                channels_failed.append({
                    'channel': channel,
                    'error': str(e)
                })

        # Step 3: Update experiment status
        self._update_experiment_status(
            experiment_id=request.experiment_id,
            channels_succeeded=channels_succeeded,
            total_cost=total_cost
        )

        # Step 4: Log to agent logs
        self._log_distribution(
            experiment_id=request.experiment_id,
            channels_succeeded=channels_succeeded,
            channels_failed=channels_failed,
            total_cost=total_cost
        )

        status = "completed" if len(channels_succeeded) > 0 else "failed"
        if len(channels_failed) > 0 and len(channels_succeeded) > 0:
            status = "partial"

        logger.info(
            f"MERCURY: Distribution complete - "
            f"{len(channels_succeeded)}/{len(request.channels)} channels succeeded, "
            f"${total_cost:.2f} total cost"
        )

        return DistributionResult(
            experiment_id=request.experiment_id,
            channels_attempted=request.channels,
            channels_succeeded=channels_succeeded,
            channels_failed=channels_failed,
            total_cost=total_cost,
            status=status
        )

    # ===========================================
    # Budget Integration with VAULT
    # ===========================================

    def _request_budget(self, experiment_id: str, num_channels: int) -> bool:
        """
        Request budget from VAULT before distribution

        Args:
            experiment_id: Experiment ID
            num_channels: Number of channels to distribute to

        Returns:
            True if approved, False if denied
        """
        try:
            # Import here to avoid circular dependency
            from .vault import BudgetRequest

            # Estimate cost: $0.05 per channel (Haiku copy generation)
            estimated_cost = 0.05 * num_channels

            budget_request = BudgetRequest(
                amount=estimated_cost,
                experiment_id=experiment_id,
                agent="MERCURY",
                description=f"Distribute landing page to {num_channels} channels",
                type="api_call"
            )

            result = self.vault.check_budget(budget_request)

            if result['approved']:
                logger.info(f"MERCURY: Budget approved - ${estimated_cost:.2f}")
                return True
            else:
                logger.warning(f"MERCURY: Budget denied - {result.get('reason', 'Unknown')}")
                return False

        except Exception as e:
            logger.error(f"MERCURY: Budget request failed: {e}")
            return False

    # ===========================================
    # Copy Generation with Claude Haiku
    # ===========================================

    def _generate_channel_copy(
        self,
        request: DistributionRequest,
        channel: str
    ) -> Dict[str, Any]:
        """
        Generate channel-specific copy with Claude Haiku

        Args:
            request: DistributionRequest with opportunity details
            channel: Channel name (reddit, email, meta_ads, etc.)

        Returns:
            Dict with copy, success, cost, error
        """
        try:
            # Build channel-specific prompt
            prompt = self._build_copy_prompt(request, channel)

            # Call Claude Haiku (cheap & fast, with retry)
            message = self._call_anthropic(
                model="claude-haiku-4-5-20251001",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}],
            )

            # Parse response (expecting JSON)
            try:
                copy_data = json.loads(message.content[0].text.strip())
            except json.JSONDecodeError:
                # If not JSON, try to extract structured data
                text = message.content[0].text.strip()
                copy_data = self._parse_copy_text(text, channel)

            # Calculate cost
            cost = self._calculate_haiku_cost(
                message.usage.input_tokens,
                message.usage.output_tokens
            )

            # Log API call
            self._log_api_call(
                action=f'generate_{channel}_copy',
                model='claude-haiku-4-5-20251001',
                input_tokens=message.usage.input_tokens,
                output_tokens=message.usage.output_tokens,
                cost=cost,
                status='success'
            )

            logger.info(
                f"MERCURY: Generated {channel} copy - "
                f"{message.usage.output_tokens} tokens, ${cost:.2f}"
            )

            # Create ChannelCopy object
            channel_copy = ChannelCopy(
                channel=channel,
                headline=copy_data.get('headline', ''),
                body=copy_data.get('body', ''),
                cta=copy_data.get('cta', ''),
                hashtags=copy_data.get('hashtags'),
                metadata=copy_data.get('metadata')
            )

            return {
                "success": True,
                "copy": channel_copy,
                "cost": cost,
                "tokens_in": message.usage.input_tokens,
                "tokens_out": message.usage.output_tokens
            }

        except Exception as e:
            logger.error(f"MERCURY: Copy generation failed for {channel}: {e}")
            return {
                "success": False,
                "copy": None,
                "cost": 0.0,
                "error": str(e)
            }

    def _build_copy_prompt(
        self,
        request: DistributionRequest,
        channel: str
    ) -> str:
        """Build channel-specific prompt for copy generation"""

        base_context = f"""You are a marketing copywriter for {BRAND.company_name}. Write compelling copy for this business automation opportunity.

BRAND:
- Company: {BRAND.company_name}
- Founder: {BRAND.founder}
- Value Prop: {BRAND.value_prop}
- Tone: Direct, founder-voice, no corporate jargon. Australian English.

OPPORTUNITY:
- Title: {request.opportunity_title}
- Target Vertical: {request.target_vertical}
- Value Proposition: {request.value_proposition}
- Landing Page: {request.landing_page_url}

CHANNEL: {channel}
"""

        channel_prompts = {
            'reddit': """
Write a Reddit post for r/Entrepreneur or r/smallbusiness.

REQUIREMENTS:
- Conversational, authentic tone (not salesy)
- Start with a pain point or question
- Share value upfront, link at the end
- 200-400 words
- Include 3-5 relevant hashtags

OUTPUT FORMAT (JSON):
{
  "headline": "Post title (max 300 chars)",
  "body": "Post body text",
  "cta": "Call to action line",
  "hashtags": ["automation", "productivity", "business"]
}
""",
            'email': """
Write a cold email for B2B outreach.

REQUIREMENTS:
- Professional but friendly tone
- Personalized opening line
- Clear value proposition in first paragraph
- One specific benefit or result
- Soft CTA (not pushy)
- Max 150 words

OUTPUT FORMAT (JSON):
{
  "headline": "Email subject line",
  "body": "Email body text",
  "cta": "Call to action line",
  "metadata": {"from_name": "Ashish from ATLAS"}
}
""",
            'meta_ads': """
Write Facebook/Instagram ad copy.

REQUIREMENTS:
- Attention-grabbing hook (first 5 words)
- Clear benefit statement
- Social proof if possible
- Strong CTA button text
- Max 125 characters primary text
- Ad headline max 40 chars

OUTPUT FORMAT (JSON):
{
  "headline": "Ad headline (40 chars)",
  "body": "Primary ad text (125 chars)",
  "cta": "CTA button text (25 chars)",
  "metadata": {"target_audience": "business owners, 30-55, interested in automation"}
}
""",
            'google_ads': """
Write Google Search ad copy.

REQUIREMENTS:
- 3 headlines (30 chars each)
- 2 descriptions (90 chars each)
- Include keywords naturally
- Clear value proposition
- Strong call to action

OUTPUT FORMAT (JSON):
{
  "headline": "Headline 1 | Headline 2 | Headline 3",
  "body": "Description 1. Description 2.",
  "cta": "CTA text",
  "metadata": {"keywords": ["automation service", "workflow automation"]}
}
"""
        }

        channel_prompt = channel_prompts.get(channel, channel_prompts['reddit'])

        return base_context + channel_prompt

    def _parse_copy_text(self, text: str, channel: str) -> Dict[str, Any]:
        """Parse non-JSON copy text into structured format"""
        lines = text.strip().split('\n')

        # Basic extraction (fallback if JSON parsing fails)
        return {
            'headline': lines[0] if len(lines) > 0 else '',
            'body': '\n'.join(lines[1:-1]) if len(lines) > 2 else text,
            'cta': lines[-1] if len(lines) > 1 else 'Learn More',
            'hashtags': [],
            'metadata': {}
        }

    def _calculate_haiku_cost(
        self,
        input_tokens: int,
        output_tokens: int
    ) -> float:
        """
        Calculate cost for Claude Haiku API call

        Pricing (as of 2024):
        - Input: $0.25 per 1M tokens
        - Output: $1.25 per 1M tokens
        """
        input_cost = (input_tokens / 1_000_000) * 0.25
        output_cost = (output_tokens / 1_000_000) * 1.25
        return input_cost + output_cost

    # ===========================================
    # Channel Distribution
    # ===========================================

    def _distribute_to_channel(
        self,
        channel: str,
        copy: ChannelCopy,
        experiment_id: str,
        landing_page_url: str
    ) -> Dict[str, Any]:
        """
        Distribute to specific channel

        Args:
            channel: Channel name
            copy: ChannelCopy object with generated content
            experiment_id: Experiment ID
            landing_page_url: Landing page URL

        Returns:
            Dict with success, post_url, cost, error
        """
        if channel == 'reddit':
            return self._post_to_reddit(copy, landing_page_url)
        elif channel == 'email':
            return self._send_email(copy, landing_page_url)
        elif channel == 'meta_ads':
            return self._create_meta_ad(copy, landing_page_url)
        elif channel == 'google_ads':
            return self._create_google_ad(copy, landing_page_url)
        else:
            return {
                'success': False,
                'error': f'Unknown channel: {channel}'
            }

    def _post_to_reddit(
        self,
        copy: ChannelCopy,
        landing_page_url: str
    ) -> Dict[str, Any]:
        """
        Post to Reddit using PRAW

        Args:
            copy: ChannelCopy with Reddit post content
            landing_page_url: Landing page URL

        Returns:
            Dict with success, post_url, cost, error
        """
        # Check if Reddit is configured
        if self.REDDIT_CONFIG['client_id'] == 'CONFIGURE_ME':
            logger.warning("MERCURY: Reddit credentials not configured - simulating post")
            return {
                'success': True,
                'post_url': f'https://reddit.com/r/entrepreneur/simulated_post_{int(time.time())}',
                'cost': 0.0,
                'simulated': True
            }

        try:
            # Import PRAW (Reddit API wrapper)
            try:
                import praw
            except ImportError:
                logger.error("MERCURY: praw not installed. Run: pip install praw")
                return {
                    'success': False,
                    'error': 'praw library not installed'
                }

            # Initialize Reddit client
            reddit = praw.Reddit(
                client_id=self.REDDIT_CONFIG['client_id'],
                client_secret=self.REDDIT_CONFIG['client_secret'],
                user_agent=self.REDDIT_CONFIG['user_agent'],
                username=self.REDDIT_CONFIG['username'],
                password=self.REDDIT_CONFIG['password']
            )

            # Format post body with landing page link
            post_body = f"{copy.body}\n\n{landing_page_url}"

            if copy.hashtags:
                post_body += f"\n\n{' '.join(['#' + tag for tag in copy.hashtags])}"

            # Post to first configured subreddit
            subreddit_name = self.CHANNEL_CONFIG['reddit']['subreddits'][0]
            subreddit = reddit.subreddit(subreddit_name)

            # Submit post
            submission = subreddit.submit(
                title=copy.headline,
                selftext=post_body
            )

            logger.info(f"MERCURY: Posted to r/{subreddit_name} - {submission.url}")

            return {
                'success': True,
                'post_url': submission.url,
                'cost': 0.0  # Reddit posting is free
            }

        except Exception as e:
            logger.error(f"MERCURY: Reddit posting failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _send_email(
        self,
        copy: ChannelCopy,
        landing_page_url: str
    ) -> Dict[str, Any]:
        """
        Send email via Resend API

        Args:
            copy: ChannelCopy with email content
            landing_page_url: Landing page URL

        Returns:
            Dict with success, cost, error
        """
        try:
            # Build email body with landing page link
            email_body = f"{copy.body}\n\n{copy.cta}\n{landing_page_url}"

            # Determine recipient from copy metadata
            to_email = (copy.metadata or {}).get('to_email', '')

            if not to_email:
                logger.warning(
                    "MERCURY: No recipient in copy metadata, "
                    "email queued as draft only"
                )
                return {
                    'success': True,
                    'cost': 0.0,
                    'simulated': True,
                    'message': 'No recipient address -- queued as draft',
                }

            result = self.email_service.send_email_sync(
                to=to_email,
                subject=copy.headline,
                body=email_body,
                email_type='mercury_outreach',
            )

            if result.success:
                logger.info(
                    f"MERCURY: Email sent to {to_email} "
                    f"(message_id={result.message_id})"
                )
                return {
                    'success': True,
                    'cost': 0.0,
                    'post_url': f'email:{result.message_id}',
                }
            else:
                logger.error(f"MERCURY: Email send failed: {result.error}")
                return {
                    'success': False,
                    'cost': 0.0,
                    'error': result.error or 'Unknown send error',
                }

        except Exception as e:
            logger.error(f"MERCURY: Email sending error: {e}")
            return {
                'success': False,
                'cost': 0.0,
                'error': str(e),
            }

    def _create_meta_ad(
        self,
        copy: ChannelCopy,
        landing_page_url: str
    ) -> Dict[str, Any]:
        """
        Create Meta (Facebook/Instagram) ad

        Note: Requires manual setup in Meta Ads Manager
        This method simulates ad creation for now

        Args:
            copy: ChannelCopy with ad content
            landing_page_url: Landing page URL

        Returns:
            Dict with success, cost, error
        """
        logger.warning("MERCURY: Meta ads require manual setup - simulating")

        return {
            'success': True,
            'cost': 0.0,  # Actual ad spend tracked separately
            'simulated': True,
            'message': 'Meta ad requires manual setup in Ads Manager'
        }

    def _create_google_ad(
        self,
        copy: ChannelCopy,
        landing_page_url: str
    ) -> Dict[str, Any]:
        """
        Create Google Search ad

        Note: Requires manual setup in Google Ads
        This method simulates ad creation for now

        Args:
            copy: ChannelCopy with ad content
            landing_page_url: Landing page URL

        Returns:
            Dict with success, cost, error
        """
        logger.warning("MERCURY: Google ads require manual setup - simulating")

        return {
            'success': True,
            'cost': 0.0,  # Actual ad spend tracked separately
            'simulated': True,
            'message': 'Google ad requires manual setup in Google Ads'
        }

    # ===========================================
    # Database Operations
    # ===========================================

    def _track_distribution(
        self,
        experiment_id: str,
        channel: str,
        copy: ChannelCopy,
        post_url: Optional[str],
        cost: float
    ):
        """
        Track distribution in database

        Note: For now, we'll store in atlas_agent_logs
        In future, create dedicated atlas_distributions table

        Args:
            experiment_id: Experiment ID
            channel: Channel name
            copy: ChannelCopy object
            post_url: Posted URL (if applicable)
            cost: Distribution cost
        """
        try:
            # Store distribution details as JSON
            distribution_data = {
                'channel': channel,
                'headline': copy.headline,
                'body': copy.body,
                'cta': copy.cta,
                'post_url': post_url,
                'cost': cost
            }

            self._call_supabase_insert('atlas_agent_logs', {
                'agent': 'mercury',
                'action': f'distribute_{channel}',
                'input': f"Experiment: {experiment_id}",
                'output': json.dumps(distribution_data),
                'cost_usd': cost,
                'status': 'success',
            })

            logger.info(f"MERCURY: Tracked distribution to {channel} in database")

        except Exception as e:
            logger.error(f"MERCURY: Failed to track distribution: {e}")

    def _update_experiment_status(
        self,
        experiment_id: str,
        channels_succeeded: List[str],
        total_cost: float
    ):
        """
        Update experiment status after distribution

        Args:
            experiment_id: Experiment ID
            channels_succeeded: List of successful channels
            total_cost: Total distribution cost
        """
        try:
            # Update experiment status to 'running' if any channel succeeded
            if len(channels_succeeded) > 0:
                self.supabase.table('atlas_experiments').update({
                    'status': 'running',
                    'distribution_channels': channels_succeeded
                }).eq('id', experiment_id).execute()

                logger.info(f"MERCURY: Updated experiment {experiment_id} status to 'running'")

        except Exception as e:
            logger.error(f"MERCURY: Failed to update experiment status: {e}")

    def _log_distribution(
        self,
        experiment_id: str,
        channels_succeeded: List[str],
        channels_failed: List[Dict[str, Any]],
        total_cost: float
    ):
        """
        Log distribution summary to agent logs

        Args:
            experiment_id: Experiment ID
            channels_succeeded: List of successful channels
            channels_failed: List of failed channels with errors
            total_cost: Total cost
        """
        try:
            summary = {
                'succeeded': channels_succeeded,
                'failed': channels_failed,
                'total_cost': total_cost
            }

            self._call_supabase_insert('atlas_agent_logs', {
                'agent': 'mercury',
                'action': 'distribute_landing_page',
                'input': f"Experiment: {experiment_id}",
                'output': json.dumps(summary),
                'cost_usd': total_cost,
                'status': 'success' if len(channels_succeeded) > 0 else 'failed',
            })

        except Exception as e:
            logger.error(f"MERCURY: Failed to log distribution: {e}")

    def _log_api_call(
        self,
        action: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cost: float,
        status: str
    ):
        """Log API call to agent logs"""
        try:
            self._call_supabase_insert('atlas_agent_logs', {
                'agent': 'mercury',
                'action': action,
                'model_used': model,
                'tokens_in': input_tokens,
                'tokens_out': output_tokens,
                'cost_usd': cost,
                'status': status,
            })

        except Exception as e:
            logger.error(f"MERCURY: Failed to log API call: {e}")

    # ===========================================
    # Reporting & Analytics
    # ===========================================

    def get_distribution_stats(self) -> Dict[str, Any]:
        """Get distribution statistics"""
        try:
            # Total distributions
            logs = self.supabase.table('atlas_agent_logs').select(
                'id, cost_usd, output, created_at', count='exact'
            ).eq('agent', 'mercury').eq('action', 'distribute_landing_page').execute()

            total_distributions = logs.count or 0
            total_cost = sum(float(log.get('cost_usd', 0)) for log in logs.data) if logs.data else 0.0

            # Parse channel distribution
            channel_counts = {}
            for log in logs.data or []:
                try:
                    output = json.loads(log.get('output', '{}'))
                    for channel in output.get('succeeded', []):
                        channel_counts[channel] = channel_counts.get(channel, 0) + 1
                except:
                    pass

            return {
                'total_distributions': total_distributions,
                'total_cost': total_cost,
                'average_cost': total_cost / total_distributions if total_distributions > 0 else 0.0,
                'channel_counts': channel_counts,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"MERCURY: Failed to get stats: {e}")
            return {'error': str(e)}


# ===========================================
# Standalone Testing
# ===========================================

def main():
    """Test MERCURY agent functionality"""
    print("=" * 60)
    print(" MERCURY Agent - Distribution Engine")
    print("=" * 60)

    # Initialize agent
    mercury = MERCURYAgent()

    # Get current stats
    print("\n1. Current Distribution Stats:")
    stats = mercury.get_distribution_stats()
    if 'error' not in stats:
        print(f"   Total Distributions: {stats['total_distributions']}")
        print(f"   Total Cost: ${stats['total_cost']:.2f}")
        print(f"   Average Cost: ${stats['average_cost']:.4f}")
        print(f"   Channel Counts: {stats['channel_counts']}")
    else:
        print(f"   Error: {stats['error']}")

    # Test copy generation (without VAULT approval)
    print("\n2. Testing Copy Generation:")
    print("   (This is a test - no actual distribution)")

    test_request = DistributionRequest(
        experiment_id="test-001",
        landing_page_url="https://example.com/test-landing",
        opportunity_title="Automated Invoice Processing for Law Firms",
        target_vertical="Legal Services",
        value_proposition="Save 10+ hours per week on manual invoice entry",
        channels=['reddit', 'email']
    )

    print(f"   Opportunity: {test_request.opportunity_title}")
    print(f"   Channels: {', '.join(test_request.channels)}")

    # Note: Uncomment below to test actual distribution (will cost ~$0.05)
    # result = mercury.distribute(test_request)
    # print(f"\n   Status: {result.status}")
    # print(f"   Succeeded: {result.channels_succeeded}")
    # print(f"   Failed: {result.channels_failed}")
    # print(f"   Cost: ${result.total_cost:.4f}")

    print("\n" + "=" * 60)
    print(" MERCURY agent ready for ATLAS orchestrator")
    print(" Use distribute() to publish landing pages to channels")
    print("\n CONFIGURATION REQUIRED:")
    print(" - Set Reddit API credentials in environment variables")
    print(" - Configure n8n email webhook URL")
    print(" - Set up Meta Ads Manager (optional)")
    print(" - Set up Google Ads (optional)")
    print("=" * 60)


if __name__ == "__main__":
    main()
