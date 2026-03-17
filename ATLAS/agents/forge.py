#!/usr/bin/env python3
"""
FORGE Agent - Landing Page Builder for ATLAS
Builds high-converting landing pages for experiments using Claude Sonnet
Deploys to Vercel automatically and tracks in database

Cost structure:
- Claude Sonnet API call: ~$0.50-2.00 per page
- Vercel deployment: Free (Hobby plan)
- Total per landing page: ~$2.00

VAULT approval required before building.
"""

import os
import logging
import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from supabase import create_client, Client
import anthropic

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('FORGE')


# ===========================================
# Data Models
# ===========================================

@dataclass
class LandingPageRequest:
    """Request to build a landing page"""
    experiment_id: str
    opportunity_title: str
    target_vertical: str
    value_proposition: str
    cta_text: str = "Get Started"
    cta_action: str = "https://calendly.com/ashishtaneja"  # Default booking link


@dataclass
class LandingPageResult:
    """Result from landing page generation"""
    html_content: str
    vercel_url: Optional[str]
    deployment_id: Optional[str]
    cost: float
    status: str


# ===========================================
# FORGE Agent Class
# ===========================================

class FORGEAgent:
    """
    Landing page builder that creates and deploys pages for experiments

    Responsibilities:
    - Generate high-converting HTML with Claude Sonnet
    - Deploy to Vercel automatically
    - Track experiments in database
    - Request budget from VAULT before building
    - Log all operations for audit trail
    """

    def __init__(
        self,
        supabase_url: str = None,
        supabase_key: str = None,
        anthropic_key: str = None,
        vercel_token: str = None,
        vault_agent = None
    ):
        """
        Initialize FORGE agent

        Args:
            supabase_url: Supabase project URL
            supabase_key: Supabase anon key
            anthropic_key: Anthropic API key
            vercel_token: Vercel API token
            vault_agent: VAULT agent instance (optional)
        """
        # Initialize Supabase
        self.supabase_url = supabase_url or os.getenv('SUPABASE_URL')
        self.supabase_key = supabase_key or os.getenv('SUPABASE_ANON_KEY')
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY environment variables are required")

        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)

        # Initialize Anthropic
        self.anthropic_key = anthropic_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.anthropic_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
        self.client = anthropic.Anthropic(api_key=self.anthropic_key)

        # Initialize Vercel
        self.vercel_token = vercel_token or os.getenv('VERCEL_API_TOKEN')
        if not self.vercel_token:
            logger.warning("VERCEL_API_TOKEN not set - deployment will be unavailable")

        # VAULT integration
        self.vault = vault_agent

        logger.info("FORGE initialized - Ready to build landing pages")

    # ===========================================
    # Main Landing Page Pipeline
    # ===========================================

    def build_landing_page(
        self,
        request: LandingPageRequest
    ) -> LandingPageResult:
        """
        Build and deploy a complete landing page

        Args:
            request: LandingPageRequest with experiment details

        Returns:
            LandingPageResult with HTML, URL, and deployment info
        """
        logger.info(f"FORGE: Building landing page for experiment {request.experiment_id}")

        # Step 1: Request budget from VAULT
        if self.vault:
            budget_approved = self._request_budget(request.experiment_id)
            if not budget_approved:
                logger.error("FORGE: Budget request denied by VAULT")
                return LandingPageResult(
                    html_content="",
                    vercel_url=None,
                    deployment_id=None,
                    cost=0.0,
                    status="budget_denied"
                )

        # Step 2: Generate HTML with Claude Sonnet
        html_result = self._generate_html_with_sonnet(request)

        if not html_result['success']:
            logger.error(f"FORGE: HTML generation failed: {html_result['error']}")
            return LandingPageResult(
                html_content="",
                vercel_url=None,
                deployment_id=None,
                cost=html_result['cost'],
                status="generation_failed"
            )

        # Step 3: Deploy to Vercel
        deployment = self._deploy_to_vercel(
            html_content=html_result['html'],
            experiment_id=request.experiment_id,
            project_name=self._slugify(request.opportunity_title)
        )

        if not deployment['success']:
            logger.error(f"FORGE: Deployment failed: {deployment['error']}")
            return LandingPageResult(
                html_content=html_result['html'],
                vercel_url=None,
                deployment_id=None,
                cost=html_result['cost'],
                status="deployment_failed"
            )

        # Step 4: Update experiment in database
        self._update_experiment(
            experiment_id=request.experiment_id,
            landing_page_url=deployment['url'],
            html_content=html_result['html']
        )

        # Step 5: Log to agent logs
        self._log_build(
            experiment_id=request.experiment_id,
            url=deployment['url'],
            cost=html_result['cost']
        )

        logger.info(f"FORGE: Landing page deployed to {deployment['url']}")

        return LandingPageResult(
            html_content=html_result['html'],
            vercel_url=deployment['url'],
            deployment_id=deployment['deployment_id'],
            cost=html_result['cost'],
            status="deployed"
        )

    # ===========================================
    # Budget Integration with VAULT
    # ===========================================

    def _request_budget(self, experiment_id: str) -> bool:
        """
        Request budget from VAULT before building

        Args:
            experiment_id: Experiment ID

        Returns:
            True if approved, False if denied
        """
        try:
            # Import here to avoid circular dependency
            from .vault import BudgetRequest

            # Estimate cost: $2.00 per landing page (Sonnet API call)
            estimated_cost = 2.00

            budget_request = BudgetRequest(
                amount=estimated_cost,
                experiment_id=experiment_id,
                agent="FORGE",
                description=f"Build landing page for experiment {experiment_id}",
                type="api_call"
            )

            result = self.vault.check_budget(budget_request)

            if result['approved']:
                logger.info(f"FORGE: Budget approved - ${estimated_cost:.2f}")
                return True
            else:
                logger.warning(f"FORGE: Budget denied - {result.get('reason', 'Unknown')}")
                return False

        except Exception as e:
            logger.error(f"FORGE: Budget request failed: {e}")
            return False

    # ===========================================
    # HTML Generation with Claude Sonnet
    # ===========================================

    def _generate_html_with_sonnet(
        self,
        request: LandingPageRequest
    ) -> Dict[str, Any]:
        """
        Generate complete HTML landing page with Claude Sonnet

        Args:
            request: LandingPageRequest with page details

        Returns:
            Dict with html, success, cost, error
        """
        try:
            prompt = f"""You are an expert landing page designer. Create a high-converting, modern landing page for this automation service opportunity.

BUSINESS OPPORTUNITY:
- Title: {request.opportunity_title}
- Target Vertical: {request.target_vertical}
- Value Proposition: {request.value_proposition}
- CTA Text: {request.cta_text}
- CTA Action: {request.cta_action}

REQUIREMENTS:
1. Single-page HTML with embedded CSS and JavaScript (no external files)
2. Modern, professional design with dark theme
3. Mobile-responsive (works on all devices)
4. Clear value proposition in hero section
5. Benefits section (3-4 key benefits)
6. Social proof section (testimonials/stats)
7. Pricing/offer section (clear pricing)
8. Strong call-to-action button that links to {request.cta_action}
9. Footer with contact info and links
10. Fast loading (no heavy images or external dependencies)

DESIGN STYLE:
- Clean, modern design inspired by Stripe, Linear, or Vercel
- Dark theme with accent color
- Professional typography
- Subtle animations and micro-interactions
- High contrast for readability

COPY WRITING:
- Focus on benefits, not features
- Address pain points directly
- Use action-oriented language
- Build trust with social proof
- Create urgency without being pushy

OUTPUT FORMAT:
Return ONLY the complete HTML code. No explanations, no markdown code blocks.
Start with <!DOCTYPE html> and include everything in a single file.

The HTML should be production-ready and deployable as-is."""

            # Call Claude Sonnet
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}]
            )

            html_content = message.content[0].text.strip()

            # Calculate cost
            cost = self._calculate_sonnet_cost(
                message.usage.input_tokens,
                message.usage.output_tokens
            )

            # Log API call
            self._log_api_call(
                action='generate_landing_page',
                model='claude-3-5-sonnet-20240620',
                input_tokens=message.usage.input_tokens,
                output_tokens=message.usage.output_tokens,
                cost=cost,
                status='success'
            )

            logger.info(
                f"FORGE: Generated HTML - {message.usage.output_tokens} tokens, ${cost:.2f}"
            )

            return {
                "success": True,
                "html": html_content,
                "cost": cost,
                "tokens_in": message.usage.input_tokens,
                "tokens_out": message.usage.output_tokens
            }

        except Exception as e:
            logger.error(f"FORGE: HTML generation failed: {e}")
            return {
                "success": False,
                "html": "",
                "cost": 0.0,
                "error": str(e)
            }

    def _calculate_sonnet_cost(
        self,
        input_tokens: int,
        output_tokens: int
    ) -> float:
        """
        Calculate cost for Claude Sonnet API call

        Pricing (as of 2024):
        - Input: $3.00 per 1M tokens
        - Output: $15.00 per 1M tokens
        """
        input_cost = (input_tokens / 1_000_000) * 3.00
        output_cost = (output_tokens / 1_000_000) * 15.00
        return input_cost + output_cost

    # ===========================================
    # Vercel Deployment
    # ===========================================

    def _deploy_to_vercel(
        self,
        html_content: str,
        experiment_id: str,
        project_name: str
    ) -> Dict[str, Any]:
        """
        Deploy HTML to Vercel using their API

        Args:
            html_content: Complete HTML code
            experiment_id: Experiment ID
            project_name: Project name slug

        Returns:
            Dict with success, url, deployment_id, error
        """
        try:
            # Prepare deployment files
            files = [
                {
                    "file": "index.html",
                    "data": html_content
                },
                {
                    "file": "vercel.json",
                    "data": json.dumps({
                        "version": 2,
                        "builds": [
                            {
                                "src": "index.html",
                                "use": "@vercel/static"
                            }
                        ]
                    })
                }
            ]

            # Vercel API endpoint
            url = "https://api.vercel.com/v13/deployments"

            headers = {
                "Authorization": f"Bearer {self.vercel_token}",
                "Content-Type": "application/json"
            }

            # Create deployment payload
            payload = {
                "name": project_name,
                "files": files,
                "projectSettings": {
                    "framework": None
                },
                "target": "production"
            }

            # Deploy to Vercel
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()

            deployment_data = response.json()
            deployment_url = f"https://{deployment_data['url']}"
            deployment_id = deployment_data['id']

            logger.info(f"FORGE: Deployed to Vercel - {deployment_url}")

            return {
                "success": True,
                "url": deployment_url,
                "deployment_id": deployment_id
            }

        except Exception as e:
            logger.error(f"FORGE: Vercel deployment failed: {e}")
            return {
                "success": False,
                "url": None,
                "deployment_id": None,
                "error": str(e)
            }

    # ===========================================
    # Database Operations
    # ===========================================

    def _update_experiment(
        self,
        experiment_id: str,
        landing_page_url: str,
        html_content: str
    ):
        """
        Update experiment with landing page details

        Args:
            experiment_id: Experiment ID
            landing_page_url: Deployed URL
            html_content: HTML code
        """
        try:
            self.supabase.table('atlas_experiments').update({
                'landing_page_url': landing_page_url,
                'landing_page_html': html_content,
                'status': 'active',
                'started_at': datetime.now().isoformat()
            }).eq('id', experiment_id).execute()

            logger.info(f"FORGE: Updated experiment {experiment_id} in database")

        except Exception as e:
            logger.error(f"FORGE: Failed to update experiment: {e}")

    def _log_build(
        self,
        experiment_id: str,
        url: str,
        cost: float
    ):
        """
        Log landing page build to agent logs

        Args:
            experiment_id: Experiment ID
            url: Deployed URL
            cost: Total cost
        """
        try:
            self.supabase.table('atlas_agent_logs').insert({
                'agent': 'forge',
                'action': 'build_landing_page',
                'input': f"Experiment: {experiment_id}",
                'output': f"Deployed to {url}",
                'cost_usd': cost,
                'status': 'success'
            }).execute()

        except Exception as e:
            logger.error(f"FORGE: Failed to log build: {e}")

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
            self.supabase.table('atlas_agent_logs').insert({
                'agent': 'forge',
                'action': action,
                'model_used': model,
                'tokens_in': input_tokens,
                'tokens_out': output_tokens,
                'cost_usd': cost,
                'status': status
            }).execute()

        except Exception as e:
            logger.error(f"FORGE: Failed to log API call: {e}")

    # ===========================================
    # Helper Methods
    # ===========================================

    def _slugify(self, text: str) -> str:
        """
        Convert text to URL-safe slug

        Args:
            text: Text to slugify

        Returns:
            URL-safe slug
        """
        import re

        # Convert to lowercase
        slug = text.lower()

        # Replace spaces and special chars with hyphens
        slug = re.sub(r'[^a-z0-9]+', '-', slug)

        # Remove leading/trailing hyphens
        slug = slug.strip('-')

        # Limit length
        slug = slug[:50]

        # Add timestamp to ensure uniqueness
        timestamp = datetime.now().strftime("%Y%m%d")
        slug = f"{slug}-{timestamp}"

        return slug

    # ===========================================
    # Reporting & Analytics
    # ===========================================

    def get_build_stats(self) -> Dict[str, Any]:
        """Get landing page build statistics"""
        try:
            # Total builds
            logs = self.supabase.table('atlas_agent_logs').select(
                'id, cost_usd, created_at', count='exact'
            ).eq('agent', 'forge').eq('action', 'build_landing_page').execute()

            total_builds = logs.count or 0
            total_cost = sum(float(log.get('cost_usd', 0)) for log in logs.data) if logs.data else 0.0

            # Active experiments with landing pages
            experiments = self.supabase.table('atlas_experiments').select(
                'id, name, landing_page_url', count='exact'
            ).not_.is_('landing_page_url', 'null').execute()

            return {
                'total_builds': total_builds,
                'total_cost': total_cost,
                'average_cost': total_cost / total_builds if total_builds > 0 else 0.0,
                'active_pages': experiments.count or 0,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"FORGE: Failed to get stats: {e}")
            return {'error': str(e)}


# ===========================================
# Standalone Testing
# ===========================================

def main():
    """Test FORGE agent functionality"""
    print("=" * 60)
    print(" FORGE Agent - Landing Page Builder")
    print("=" * 60)

    # Initialize agent
    forge = FORGEAgent()

    # Get current stats
    print("\n1. Current Build Stats:")
    stats = forge.get_build_stats()
    if 'error' not in stats:
        print(f"   Total Builds: {stats['total_builds']}")
        print(f"   Total Cost: ${stats['total_cost']:.2f}")
        print(f"   Average Cost: ${stats['average_cost']:.2f}")
        print(f"   Active Pages: {stats['active_pages']}")
    else:
        print(f"   Error: {stats['error']}")

    # Test landing page generation (without VAULT approval)
    print("\n2. Testing Landing Page Generation:")
    print("   (This is a test - no actual deployment)")

    test_request = LandingPageRequest(
        experiment_id="test-001",
        opportunity_title="Automated Invoice Processing for Law Firms",
        target_vertical="Legal Services",
        value_proposition="Save 10+ hours per week on manual invoice entry and reconciliation",
        cta_text="Book a Demo",
        cta_action="https://calendly.com/ashishtaneja"
    )

    print(f"   Opportunity: {test_request.opportunity_title}")
    print(f"   Vertical: {test_request.target_vertical}")
    print(f"   CTA: {test_request.cta_text}")

    # Note: Uncomment below to test actual build (will cost ~$2)
    # result = forge.build_landing_page(test_request)
    # print(f"\n   Status: {result.status}")
    # print(f"   Cost: ${result.cost:.2f}")
    # if result.vercel_url:
    #     print(f"   URL: {result.vercel_url}")

    print("\n" + "=" * 60)
    print(" FORGE agent ready for ATLAS orchestrator")
    print(" Use build_landing_page() to create new pages")
    print("=" * 60)


if __name__ == "__main__":
    main()
