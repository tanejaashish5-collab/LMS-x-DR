#!/usr/bin/env python3
"""
SCOUT Agent - Opportunity Discovery for ATLAS
Discovers business automation opportunities from Reddit and other sources

Schedule: Mon/Wed/Fri at 5 AM
Filters: Claude Haiku (cheap, fast)
Scoring: Claude Sonnet (top opportunities only)
"""

import os
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from supabase import create_client, Client
import anthropic
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('SCOUT')


# ===========================================
# Data Models
# ===========================================

@dataclass
class Opportunity:
    """Business automation opportunity discovered from source"""
    title: str
    source: str
    source_url: str
    description: str
    category: str = "other"
    target_vertical: Optional[str] = None


@dataclass
class FilterResult:
    """Result from Claude Haiku filtering"""
    passed: bool
    category: str
    target_vertical: Optional[str]
    reason: str


@dataclass
class ScoreResult:
    """Result from Claude Sonnet deep scoring"""
    score: int  # 0-100
    reasoning: str
    automation_potential: int  # 0-10
    market_size: int  # 0-10
    pain_level: int  # 0-10


# ===========================================
# SCOUT Agent Class
# ===========================================

class SCOUTAgent:
    """
    Discovery agent that finds business automation opportunities

    Responsibilities:
    - Scan Reddit for automation pain points
    - Filter opportunities with Claude Haiku
    - Save qualified opportunities to database
    - Score top opportunities with Claude Sonnet
    """

    def __init__(
        self,
        supabase_url: str = None,
        supabase_key: str = None,
        anthropic_key: str = None,
        apify_token: str = None
    ):
        """
        Initialize SCOUT agent

        Args:
            supabase_url: Supabase project URL
            supabase_key: Supabase anon key
            anthropic_key: Anthropic API key
            apify_token: Apify API token
        """
        # Initialize Supabase
        self.supabase_url = supabase_url or os.getenv(
            'SUPABASE_URL',
            'https://yozmayslzckaczdfohll.supabase.co'
        )
        self.supabase_key = supabase_key or os.getenv(
            'SUPABASE_ANON_KEY',
            'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inlvem1heXNsemNrYWN6ZGZvaGxsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM2OTgzNTAsImV4cCI6MjA4OTI3NDM1MH0.uQd-f3nH6DBWz3g8lFftsA9Ql37TxE5zxMkMUbAQX0M'
        )
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)

        # Initialize Anthropic
        self.anthropic_key = anthropic_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.anthropic_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
        self.client = anthropic.Anthropic(api_key=self.anthropic_key)

        # Initialize Apify
        self.apify_token = apify_token or os.getenv('APIFY_API_TOKEN')
        if not self.apify_token:
            logger.warning("APIFY_API_TOKEN not set - Reddit scraping will be unavailable")

        logger.info("SCOUT initialized - Ready to discover opportunities")

    # ===========================================
    # Main Discovery Pipeline
    # ===========================================

    def run_discovery(
        self,
        subreddits: List[str] = None,
        max_posts: int = 50
    ) -> Dict[str, Any]:
        """
        Run full discovery pipeline

        Args:
            subreddits: List of subreddits to scan
            max_posts: Maximum posts to scan per subreddit

        Returns:
            Discovery summary with counts and top opportunities
        """
        if subreddits is None:
            subreddits = [
                'Entrepreneur',
                'smallbusiness',
                'SaaS',
                'consulting',
                'freelance',
                'marketing',
                'sales',
                'accounting',
                'realestate',
                'legaladvice'
            ]

        logger.info(f"Starting discovery scan - {len(subreddits)} subreddits, {max_posts} posts each")

        # Step 1: Discover opportunities from Reddit
        raw_opportunities = self._scan_reddit(subreddits, max_posts)
        logger.info(f"Discovered {len(raw_opportunities)} raw opportunities")

        # Step 2: Filter with Claude Haiku
        filtered_opportunities = []
        for opp in raw_opportunities:
            filter_result = self._filter_with_haiku(opp)
            if filter_result.passed:
                filtered_opportunities.append((opp, filter_result))
                logger.info(f"Passed: {opp.title[:60]}...")

        logger.info(f"Haiku filtered: {len(filtered_opportunities)} qualified opportunities")

        # Step 3: Save to database
        saved_count = 0
        for opp, filter_result in filtered_opportunities:
            if self._save_opportunity(opp, filter_result):
                saved_count += 1

        logger.info(f"Saved {saved_count} opportunities to database")

        # Step 4: Score top opportunities with Sonnet
        top_opportunities = self._get_unscored_opportunities(limit=10)
        scored_count = 0
        for opp_data in top_opportunities:
            score_result = self._score_with_sonnet(opp_data)
            if score_result and self._save_score(opp_data['id'], score_result):
                scored_count += 1

        logger.info(f"Scored {scored_count} opportunities with Sonnet")

        # Step 5: Log to agent logs
        self._log_discovery_run(
            scanned=len(raw_opportunities),
            filtered=len(filtered_opportunities),
            saved=saved_count,
            scored=scored_count
        )

        return {
            "status": "completed",
            "scanned": len(raw_opportunities),
            "filtered": len(filtered_opportunities),
            "saved": saved_count,
            "scored": scored_count,
            "timestamp": datetime.now().isoformat()
        }

    # ===========================================
    # Reddit Discovery via Apify
    # ===========================================

    def _scan_reddit(
        self,
        subreddits: List[str],
        max_posts: int
    ) -> List[Opportunity]:
        """
        Scan Reddit for opportunities using Apify

        Args:
            subreddits: List of subreddits to scan
            max_posts: Max posts per subreddit

        Returns:
            List of raw opportunities
        """
        opportunities = []

        # Search terms that indicate automation pain
        search_terms = [
            "automation",
            "manual process",
            "spending hours",
            "repetitive task",
            "workflow",
            "integration",
            "data entry"
        ]

        logger.info(f"Scanning {len(subreddits)} subreddits with {len(search_terms)} search terms")

        for subreddit in subreddits:
            for term in search_terms:
                try:
                    # Use Apify Reddit Scraper
                    posts = self._apify_reddit_search(
                        subreddit=subreddit,
                        search_term=term,
                        max_results=max_posts // len(search_terms)
                    )

                    for post in posts:
                        opp = Opportunity(
                            title=post.get('title', ''),
                            source='reddit',
                            source_url=post.get('url', ''),
                            description=post.get('selftext', '') or post.get('title', '')
                        )
                        opportunities.append(opp)

                except Exception as e:
                    logger.error(f"Error scanning r/{subreddit} for '{term}': {e}")
                    continue

        # Deduplicate by URL
        seen_urls = set()
        unique_opportunities = []
        for opp in opportunities:
            if opp.source_url not in seen_urls:
                seen_urls.add(opp.source_url)
                unique_opportunities.append(opp)

        return unique_opportunities

    def _apify_reddit_search(
        self,
        subreddit: str,
        search_term: str,
        max_results: int
    ) -> List[Dict[str, Any]]:
        """
        Search Reddit using Apify API

        Args:
            subreddit: Subreddit name
            search_term: Search query
            max_results: Max results to return

        Returns:
            List of Reddit posts
        """
        try:
            # Apify Reddit Scraper Actor
            actor_id = "trudax/reddit-scraper"

            # Start actor run
            url = f"https://api.apify.com/v2/acts/{actor_id}/runs"
            headers = {
                "Authorization": f"Bearer {self.apify_token}",
                "Content-Type": "application/json"
            }

            payload = {
                "startUrls": [
                    {
                        "url": f"https://www.reddit.com/r/{subreddit}/search/?q={search_term}&restrict_sr=1&sort=new"
                    }
                ],
                "maxItems": max_results,
                "extendOutputFunction": "",
                "maxPostCount": max_results,
                "skipComments": True
            }

            # Run actor
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()

            run_data = response.json()
            run_id = run_data['data']['id']

            # Wait for completion (timeout after 60 seconds)
            import time
            max_wait = 60
            waited = 0

            while waited < max_wait:
                status_url = f"https://api.apify.com/v2/acts/{actor_id}/runs/{run_id}"
                status_response = requests.get(status_url, headers=headers, timeout=10)
                status_data = status_response.json()

                if status_data['data']['status'] in ['SUCCEEDED', 'FAILED', 'ABORTED']:
                    break

                time.sleep(5)
                waited += 5

            # Get dataset items
            dataset_id = run_data['data']['defaultDatasetId']
            items_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items"
            items_response = requests.get(items_url, headers=headers, timeout=30)
            items_response.raise_for_status()

            return items_response.json()

        except Exception as e:
            logger.error(f"Apify Reddit search failed for r/{subreddit} '{search_term}': {e}")
            return []

    # ===========================================
    # Claude Haiku Filtering
    # ===========================================

    def _filter_with_haiku(self, opportunity: Opportunity) -> FilterResult:
        """
        Filter opportunity with Claude Haiku (cheap, fast)

        Args:
            opportunity: Raw opportunity to filter

        Returns:
            FilterResult with pass/fail and categorization
        """
        try:
            prompt = f"""Analyze this business opportunity and determine if it's worth pursuing for automation services.

OPPORTUNITY:
Title: {opportunity.title}
Description: {opportunity.description}

FILTERING CRITERIA:
1. Must describe a real business pain point (not just asking for recommendations)
2. Must involve repetitive manual work or inefficient processes
3. Must be from someone who could be a paying customer (business owner, manager, professional)
4. Should NOT be: hobbyists, students, or people just looking for free advice

CATEGORIZATION:
- automation_service: Custom automation/integration service opportunity
- template_product: Could be solved with a template/productized service
- software_product: Needs custom software development
- other: Doesn't fit automation service model

TARGET VERTICAL:
Identify the specific business vertical (e.g., "Legal Services", "Real Estate", "E-commerce", "Healthcare")

Respond in this exact format:
PASS: [yes/no]
CATEGORY: [automation_service/template_product/software_product/other]
VERTICAL: [specific vertical or "Unknown"]
REASON: [one sentence explanation]"""

            # Call Claude Haiku
            message = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}]
            )

            response = message.content[0].text.strip()

            # Parse response
            lines = response.split('\n')
            passed = False
            category = "other"
            vertical = None
            reason = ""

            for line in lines:
                if line.startswith('PASS:'):
                    passed = 'yes' in line.lower()
                elif line.startswith('CATEGORY:'):
                    category = line.split(':', 1)[1].strip().lower()
                elif line.startswith('VERTICAL:'):
                    vertical = line.split(':', 1)[1].strip()
                    if vertical.lower() == 'unknown':
                        vertical = None
                elif line.startswith('REASON:'):
                    reason = line.split(':', 1)[1].strip()

            # Log API call
            self._log_api_call(
                action='haiku_filter',
                model='claude-3-haiku-20240307',
                input_tokens=message.usage.input_tokens,
                output_tokens=message.usage.output_tokens,
                status='success' if passed else 'filtered'
            )

            return FilterResult(
                passed=passed,
                category=category,
                target_vertical=vertical,
                reason=reason
            )

        except Exception as e:
            logger.error(f"Haiku filtering failed: {e}")
            return FilterResult(
                passed=False,
                category="other",
                target_vertical=None,
                reason=f"Filter error: {str(e)}"
            )

    # ===========================================
    # Claude Sonnet Deep Scoring
    # ===========================================

    def _score_with_sonnet(self, opportunity_data: Dict[str, Any]) -> Optional[ScoreResult]:
        """
        Deep score opportunity with Claude Sonnet (or Haiku as fallback)

        Args:
            opportunity_data: Opportunity from database

        Returns:
            ScoreResult with detailed scoring
        """
        try:
            prompt = f"""Analyze this business automation opportunity and provide a detailed score.

OPPORTUNITY:
Title: {opportunity_data.get('title')}
Description: {opportunity_data.get('description')}
Category: {opportunity_data.get('category')}
Vertical: {opportunity_data.get('target_vertical')}

SCORING CRITERIA (0-10 for each):
1. Automation Potential: How easily can this be automated with n8n/Zapier/Make?
2. Market Size: How many similar businesses face this problem?
3. Pain Level: How much does this problem cost them (time/money)?

OVERALL SCORE: 0-100 (weighted: 30% automation, 40% market, 30% pain)

Provide your analysis in this format:
AUTOMATION_POTENTIAL: [0-10]
MARKET_SIZE: [0-10]
PAIN_LEVEL: [0-10]
OVERALL_SCORE: [0-100]
REASONING: [2-3 sentences explaining the score and potential]"""

            # Try Sonnet first, fallback to Haiku
            model = "claude-3-5-sonnet-20240620"
            try:
                message = self.client.messages.create(
                    model=model,
                    max_tokens=500,
                    messages=[{"role": "user", "content": prompt}]
                )
            except Exception as sonnet_error:
                logger.warning(f"Sonnet failed, using Haiku: {sonnet_error}")
                model = "claude-3-haiku-20240307"
                message = self.client.messages.create(
                    model=model,
                    max_tokens=500,
                    messages=[{"role": "user", "content": prompt}]
                )

            response = message.content[0].text.strip()

            # Parse response
            lines = response.split('\n')
            automation_potential = 0
            market_size = 0
            pain_level = 0
            score = 0
            reasoning = ""

            for line in lines:
                if line.startswith('AUTOMATION_POTENTIAL:'):
                    automation_potential = int(line.split(':', 1)[1].strip())
                elif line.startswith('MARKET_SIZE:'):
                    market_size = int(line.split(':', 1)[1].strip())
                elif line.startswith('PAIN_LEVEL:'):
                    pain_level = int(line.split(':', 1)[1].strip())
                elif line.startswith('OVERALL_SCORE:'):
                    score = int(line.split(':', 1)[1].strip())
                elif line.startswith('REASONING:'):
                    reasoning = line.split(':', 1)[1].strip()

            # Log API call
            self._log_api_call(
                action='sonnet_score',
                model=model,
                input_tokens=message.usage.input_tokens,
                output_tokens=message.usage.output_tokens,
                status='success'
            )

            return ScoreResult(
                score=score,
                reasoning=reasoning,
                automation_potential=automation_potential,
                market_size=market_size,
                pain_level=pain_level
            )

        except Exception as e:
            logger.error(f"Sonnet scoring failed: {e}")
            return None

    # ===========================================
    # Database Operations
    # ===========================================

    def _save_opportunity(
        self,
        opportunity: Opportunity,
        filter_result: FilterResult
    ) -> bool:
        """
        Save opportunity to database

        Args:
            opportunity: Opportunity to save
            filter_result: Filter result from Haiku

        Returns:
            True if saved successfully
        """
        try:
            # Check for duplicates
            existing = self.supabase.table('atlas_opportunities').select(
                'id'
            ).eq('source_url', opportunity.source_url).execute()

            if existing.data:
                logger.debug(f"Duplicate opportunity: {opportunity.source_url}")
                return False

            # Insert opportunity
            data = {
                'title': opportunity.title[:200],  # Limit title length
                'source': opportunity.source,
                'source_url': opportunity.source_url,
                'description': opportunity.description,
                'category': filter_result.category,
                'target_vertical': filter_result.target_vertical,
                'haiku_filter_pass': filter_result.passed,
                'status': 'haiku_filtered',
                'discovered_at': datetime.now().isoformat()
            }

            result = self.supabase.table('atlas_opportunities').insert(data).execute()

            if result.data:
                logger.info(f"Saved: {opportunity.title[:60]}...")
                return True

            return False

        except Exception as e:
            logger.error(f"Failed to save opportunity: {e}")
            return False

    def _get_unscored_opportunities(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get opportunities that haven't been scored by Sonnet yet

        Args:
            limit: Max opportunities to return

        Returns:
            List of unscored opportunities
        """
        try:
            result = self.supabase.table('atlas_opportunities').select(
                '*'
            ).eq('haiku_filter_pass', True).is_(
                'sonnet_score', 'null'
            ).order('discovered_at', desc=True).limit(limit).execute()

            return result.data or []

        except Exception as e:
            logger.error(f"Failed to get unscored opportunities: {e}")
            return []

    def _save_score(self, opportunity_id: str, score_result: ScoreResult) -> bool:
        """
        Save Sonnet score to database

        Args:
            opportunity_id: Opportunity ID
            score_result: Score from Sonnet

        Returns:
            True if saved successfully
        """
        try:
            # Only save fields that exist in the database schema
            # Store reasoning in a JSON field if available, otherwise just the score
            self.supabase.table('atlas_opportunities').update({
                'sonnet_score': score_result.score,
                'status': 'sonnet_scored'
            }).eq('id', opportunity_id).execute()

            logger.info(
                f"Scored opportunity {opportunity_id}: {score_result.score}/100 "
                f"(AP:{score_result.automation_potential}, "
                f"MS:{score_result.market_size}, "
                f"PL:{score_result.pain_level})"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to save score: {e}")
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
        status: str
    ):
        """Log API call to agent logs"""
        try:
            # Calculate cost (approximate)
            if 'haiku' in model:
                cost = (input_tokens * 0.00025 + output_tokens * 0.00125) / 1000
            else:  # sonnet
                cost = (input_tokens * 0.003 + output_tokens * 0.015) / 1000

            self.supabase.table('atlas_agent_logs').insert({
                'agent': 'scout',
                'action': action,
                'model_used': model,
                'tokens_in': input_tokens,
                'tokens_out': output_tokens,
                'cost_usd': cost,
                'status': status
            }).execute()

        except Exception as e:
            logger.error(f"Failed to log API call: {e}")

    def _log_discovery_run(
        self,
        scanned: int,
        filtered: int,
        saved: int,
        scored: int
    ):
        """Log discovery run summary"""
        try:
            self.supabase.table('atlas_agent_logs').insert({
                'agent': 'scout',
                'action': 'discovery_run',
                'input': f"Scanned: {scanned}, Filtered: {filtered}",
                'output': f"Saved: {saved}, Scored: {scored}",
                'status': 'success'
            }).execute()

        except Exception as e:
            logger.error(f"Failed to log discovery run: {e}")

    def get_discovery_stats(self) -> Dict[str, Any]:
        """Get discovery statistics"""
        try:
            # Total opportunities
            total = self.supabase.table('atlas_opportunities').select(
                'id', count='exact'
            ).execute()

            # By status
            filtered = self.supabase.table('atlas_opportunities').select(
                'id', count='exact'
            ).eq('status', 'haiku_filtered').execute()

            scored = self.supabase.table('atlas_opportunities').select(
                'id', count='exact'
            ).eq('status', 'sonnet_scored').execute()

            # Top scores
            top_opps = self.supabase.table('atlas_opportunities').select(
                'title, sonnet_score, target_vertical'
            ).order('sonnet_score', desc=True).limit(5).execute()

            return {
                'total_discovered': total.count,
                'haiku_filtered': filtered.count,
                'sonnet_scored': scored.count,
                'top_opportunities': top_opps.data or [],
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {'error': str(e)}


# ===========================================
# Standalone Testing
# ===========================================

def main():
    """Test SCOUT agent functionality"""
    print("=" * 60)
    print(" SCOUT Agent - Opportunity Discovery")
    print("=" * 60)

    # Initialize agent
    scout = SCOUTAgent()

    # Get current stats
    print("\n1. Current Discovery Stats:")
    stats = scout.get_discovery_stats()
    if 'error' not in stats:
        print(f"   Total Discovered: {stats['total_discovered']}")
        print(f"   Haiku Filtered: {stats['haiku_filtered']}")
        print(f"   Sonnet Scored: {stats['sonnet_scored']}")
        if stats['top_opportunities']:
            print("\n   Top 5 Opportunities:")
            for opp in stats['top_opportunities']:
                score = opp.get('sonnet_score', 0)
                vertical = opp.get('target_vertical', 'Unknown')
                title = opp.get('title', '')[:50]
                print(f"   - [{score}/100] {vertical}: {title}...")
    else:
        print(f"   Error: {stats['error']}")

    # Test discovery (small batch)
    print("\n2. Running Test Discovery (5 posts from r/entrepreneur):")
    result = scout.run_discovery(
        subreddits=['entrepreneur'],
        max_posts=5
    )

    print(f"   Status: {result['status']}")
    print(f"   Scanned: {result['scanned']}")
    print(f"   Filtered: {result['filtered']}")
    print(f"   Saved: {result['saved']}")
    print(f"   Scored: {result['scored']}")

    print("\n" + "=" * 60)
    print(" SCOUT agent ready for ATLAS orchestrator")
    print("=" * 60)


if __name__ == "__main__":
    main()
