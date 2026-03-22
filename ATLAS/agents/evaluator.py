#!/usr/bin/env python3
"""
Agent Evaluator - Quality scoring for ATLAS agent outputs.

Evaluates proposals and content against rubrics using Claude Haiku.
Cheap (~$0.01 per eval) and fast. Stores scores in Supabase for
conversion analytics.

Rubric dimensions are weighted 0-1 and scored 0-10 by Haiku,
then normalized to a 0-100 composite score.
"""

import os
import json
import logging
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from supabase import create_client, Client
import anthropic

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('EVALUATOR')


# ===========================================
# Data Models
# ===========================================

@dataclass
class EvalResult:
    """Result from an evaluation run."""
    score: float  # 0-100 composite
    dimensions: Dict[str, float]  # Individual dimension scores (0-10)
    feedback: str
    pass_threshold: bool  # True if score > threshold


# ===========================================
# Rubrics
# ===========================================

PROPOSAL_RUBRIC: Dict[str, Dict[str, Any]] = {
    "personalization": {
        "weight": 0.25,
        "description": "References specific pain point from opportunity",
    },
    "clarity": {
        "weight": 0.20,
        "description": "Value proposition is clear in first 2 sentences",
    },
    "pricing_fit": {
        "weight": 0.20,
        "description": "Pricing tier matches business size/vertical",
    },
    "cta_strength": {
        "weight": 0.15,
        "description": "Call-to-action is specific and low-friction",
    },
    "professionalism": {
        "weight": 0.10,
        "description": "Professional tone, no AI artifacts",
    },
    "specificity": {
        "weight": 0.10,
        "description": "Industry-specific language and examples",
    },
}

CONTENT_RUBRIC: Dict[str, Dict[str, Any]] = {
    "hook": {
        "weight": 0.30,
        "description": "Opening line grabs attention",
    },
    "value": {
        "weight": 0.25,
        "description": "Provides actionable insight",
    },
    "authenticity": {
        "weight": 0.20,
        "description": "Sounds like a founder, not AI",
    },
    "cta": {
        "weight": 0.15,
        "description": "Ends with clear call-to-action",
    },
    "length": {
        "weight": 0.10,
        "description": "Appropriate length for platform",
    },
}

# Default pass thresholds
PROPOSAL_PASS_THRESHOLD = 50.0
CONTENT_PASS_THRESHOLD = 50.0


# ===========================================
# AgentEvaluator
# ===========================================

class AgentEvaluator:
    """
    Evaluates quality of agent outputs using rubrics and Claude Haiku.

    Usage:
        evaluator = AgentEvaluator()
        result = evaluator.evaluate_proposal(proposal_text, context)
        if result.pass_threshold:
            # good to send
    """

    def __init__(
        self,
        supabase_url: Optional[str] = None,
        supabase_key: Optional[str] = None,
        anthropic_key: Optional[str] = None,
    ):
        """
        Initialize evaluator.

        Args:
            supabase_url: Supabase project URL.
            supabase_key: Supabase anon key.
            anthropic_key: Anthropic API key.
        """
        self.supabase_url = supabase_url or os.getenv('SUPABASE_URL')
        self.supabase_key = supabase_key or os.getenv('SUPABASE_ANON_KEY')

        if not self.supabase_url or not self.supabase_key:
            raise ValueError(
                "SUPABASE_URL and SUPABASE_ANON_KEY required"
            )

        self.supabase: Client = create_client(
            self.supabase_url, self.supabase_key
        )

        self.anthropic_key = anthropic_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.anthropic_key:
            raise ValueError("ANTHROPIC_API_KEY required")
        self.client = anthropic.Anthropic(api_key=self.anthropic_key)

        logger.info("EVALUATOR initialized")

    # ===========================================
    # Proposal Evaluation
    # ===========================================

    def evaluate_proposal(
        self,
        proposal_text: str,
        context: Dict[str, Any],
        threshold: float = PROPOSAL_PASS_THRESHOLD,
    ) -> EvalResult:
        """
        Score a proposal against the proposal rubric using Claude Haiku.

        Args:
            proposal_text: The proposal content (JSON or plain text).
            context: Dict with vertical, pain_point, deal_value, business_size.
            threshold: Minimum passing score (0-100).

        Returns:
            EvalResult with composite score, dimension scores, and feedback.
        """
        rubric_text = self._format_rubric(PROPOSAL_RUBRIC)

        prompt = f"""You are a proposal quality evaluator. Score this proposal on each dimension.

PROPOSAL:
{proposal_text[:3000]}

CLIENT CONTEXT:
- Vertical: {context.get('vertical', 'unknown')}
- Pain Point: {context.get('pain_point', 'unknown')}
- Deal Value: ${context.get('deal_value', 0)} AUD
- Business Size: {context.get('business_size', 'unknown')}

SCORING RUBRIC (score each 0-10):
{rubric_text}

Respond in this exact JSON format:
{{
  "personalization": 7,
  "clarity": 8,
  "pricing_fit": 6,
  "cta_strength": 7,
  "professionalism": 8,
  "specificity": 5,
  "feedback": "One sentence summary of strengths and weaknesses"
}}"""

        return self._run_eval(
            prompt=prompt,
            rubric=PROPOSAL_RUBRIC,
            threshold=threshold,
            eval_type='proposal',
        )

    # ===========================================
    # Content Evaluation
    # ===========================================

    def evaluate_content(
        self,
        content_text: str,
        platform: str,
        threshold: float = CONTENT_PASS_THRESHOLD,
    ) -> EvalResult:
        """
        Score social media content against the content rubric.

        Args:
            content_text: The content body text.
            platform: Target platform (linkedin, instagram, both).
            threshold: Minimum passing score (0-100).

        Returns:
            EvalResult with composite score and feedback.
        """
        rubric_text = self._format_rubric(CONTENT_RUBRIC)

        platform_guidance = {
            "linkedin": "LinkedIn posts should be 150-300 words, professional tone, thought-leadership angle.",
            "instagram": "Instagram captions should be 50-150 words, conversational, with emoji-friendly formatting.",
            "both": "Content should work on both LinkedIn and Instagram -- professional but approachable.",
        }

        prompt = f"""You are a social media content evaluator. Score this content on each dimension.

CONTENT:
{content_text[:2000]}

PLATFORM: {platform}
PLATFORM GUIDANCE: {platform_guidance.get(platform, platform_guidance['both'])}

SCORING RUBRIC (score each 0-10):
{rubric_text}

Respond in this exact JSON format:
{{
  "hook": 7,
  "value": 8,
  "authenticity": 6,
  "cta": 7,
  "length": 8,
  "feedback": "One sentence summary of strengths and weaknesses"
}}"""

        return self._run_eval(
            prompt=prompt,
            rubric=CONTENT_RUBRIC,
            threshold=threshold,
            eval_type='content',
        )

    # ===========================================
    # Conversion Metrics
    # ===========================================

    def get_conversion_metrics(self) -> Dict[str, Any]:
        """
        Pull conversion metrics from Supabase.

        Queries atlas_pipeline and atlas_proposals to calculate:
        - Proposals sent vs responses vs closed
        - Conversion rate by stage
        - Average quality score by vertical

        Returns:
            Dict with conversion metrics.
        """
        try:
            # Stage counts
            pipeline = self.supabase.table('atlas_pipeline').select(
                'id, stage, deal_value'
            ).execute()

            entries = pipeline.data or []
            stage_counts: Dict[str, int] = {}
            stage_value: Dict[str, float] = {}

            for entry in entries:
                stage = entry.get('stage', 'discovered')
                stage_counts[stage] = stage_counts.get(stage, 0) + 1
                val = float(entry.get('deal_value', 0) or 0)
                stage_value[stage] = stage_value.get(stage, 0.0) + val

            total = len(entries)
            proposed = stage_counts.get('proposed', 0)
            responded = stage_counts.get('responded', 0)
            won = stage_counts.get('closed_won', 0)

            # Proposal quality scores
            proposals = self.supabase.table('atlas_proposals').select(
                'quality_score, eval_score'
            ).execute()

            quality_scores = [
                p['quality_score'] for p in (proposals.data or [])
                if p.get('quality_score') is not None
            ]
            eval_scores = [
                p['eval_score'] for p in (proposals.data or [])
                if p.get('eval_score') is not None
            ]

            avg_quality = (
                sum(quality_scores) / len(quality_scores)
                if quality_scores else None
            )
            avg_eval = (
                sum(eval_scores) / len(eval_scores)
                if eval_scores else None
            )

            return {
                'total_pipeline': total,
                'stage_counts': stage_counts,
                'stage_value': stage_value,
                'proposed_count': proposed,
                'responded_count': responded,
                'closed_won_count': won,
                'proposal_to_response_rate': (
                    responded / proposed if proposed > 0 else 0.0
                ),
                'response_to_close_rate': (
                    won / responded if responded > 0 else 0.0
                ),
                'overall_close_rate': (
                    won / total if total > 0 else 0.0
                ),
                'avg_quality_score': avg_quality,
                'avg_eval_score': avg_eval,
                'total_proposals_scored': len(quality_scores),
            }

        except Exception as e:
            logger.error(f"EVALUATOR: Conversion metrics failed: {e}")
            return {'error': str(e)}

    # ===========================================
    # Internal Helpers
    # ===========================================

    def _run_eval(
        self,
        prompt: str,
        rubric: Dict[str, Dict[str, Any]],
        threshold: float,
        eval_type: str,
    ) -> EvalResult:
        """
        Run an evaluation prompt through Haiku and compute scores.

        Args:
            prompt: The evaluation prompt.
            rubric: The rubric dict with weights.
            threshold: Pass/fail threshold (0-100).
            eval_type: 'proposal' or 'content' for logging.

        Returns:
            EvalResult with composite score.
        """
        try:
            message = self.client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )

            response_text = message.content[0].text.strip()

            # Log the API call
            self._log_api_call(
                action=f'evaluate_{eval_type}',
                model='claude-haiku-4-5-20251001',
                input_tokens=message.usage.input_tokens,
                output_tokens=message.usage.output_tokens,
            )

            # Parse response
            try:
                if response_text.startswith('```'):
                    response_text = response_text.split('```')[1]
                    if response_text.startswith('json'):
                        response_text = response_text[4:]
                scores_data = json.loads(response_text.strip())
            except json.JSONDecodeError:
                logger.warning(
                    f"EVALUATOR: Failed to parse {eval_type} eval JSON"
                )
                return EvalResult(
                    score=0.0,
                    dimensions={},
                    feedback="Evaluation parse failed",
                    pass_threshold=False,
                )

            # Extract dimension scores and compute weighted composite
            dimensions: Dict[str, float] = {}
            weighted_sum = 0.0

            for dim_name, dim_config in rubric.items():
                raw_score = float(scores_data.get(dim_name, 5))
                # Clamp to 0-10
                raw_score = max(0.0, min(10.0, raw_score))
                dimensions[dim_name] = raw_score
                weighted_sum += raw_score * dim_config['weight']

            # Normalize to 0-100
            composite = weighted_sum * 10.0

            feedback = scores_data.get('feedback', '')

            logger.info(
                f"EVALUATOR: {eval_type} scored {composite:.1f}/100 "
                f"(threshold: {threshold})"
            )

            return EvalResult(
                score=round(composite, 1),
                dimensions=dimensions,
                feedback=feedback,
                pass_threshold=composite > threshold,
            )

        except Exception as e:
            logger.error(f"EVALUATOR: {eval_type} eval failed: {e}")
            return EvalResult(
                score=0.0,
                dimensions={},
                feedback=f"Evaluation error: {str(e)}",
                pass_threshold=False,
            )

    def _format_rubric(
        self,
        rubric: Dict[str, Dict[str, Any]],
    ) -> str:
        """Format a rubric dict into a prompt-friendly string."""
        lines = []
        for dim_name, dim_config in rubric.items():
            weight_pct = int(dim_config['weight'] * 100)
            lines.append(
                f"- {dim_name} ({weight_pct}%): {dim_config['description']}"
            )
        return "\n".join(lines)

    def _log_api_call(
        self,
        action: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
    ) -> None:
        """Log API call to atlas_agent_logs."""
        try:
            cost = (
                input_tokens * 0.00025 + output_tokens * 0.00125
            ) / 1000

            self.supabase.table('atlas_agent_logs').insert({
                'agent': 'evaluator',
                'action': action,
                'model_used': model,
                'tokens_in': input_tokens,
                'tokens_out': output_tokens,
                'cost_usd': cost,
                'status': 'success',
            }).execute()

        except Exception as e:
            logger.error(f"EVALUATOR: Failed to log API call: {e}")


# ===========================================
# Standalone Testing
# ===========================================

def main() -> None:
    """Test evaluator functionality."""
    print("=" * 60)
    print(" EVALUATOR - Agent Output Quality Scorer")
    print("=" * 60)

    evaluator = AgentEvaluator()

    # Test conversion metrics
    print("\n1. Conversion Metrics:")
    metrics = evaluator.get_conversion_metrics()
    if 'error' not in metrics:
        print(f"   Total Pipeline: {metrics['total_pipeline']}")
        print(f"   Stage Counts: {metrics['stage_counts']}")
        print(f"   Close Rate: {metrics['overall_close_rate']:.1%}")
        print(f"   Avg Quality Score: {metrics['avg_quality_score']}")
        print(f"   Avg Eval Score: {metrics['avg_eval_score']}")
    else:
        print(f"   Error: {metrics['error']}")

    # Test proposal evaluation with sample
    print("\n2. Sample Proposal Evaluation:")
    sample_proposal = json.dumps({
        "executive_summary": "Your manual onboarding process is costing 10+ hours weekly.",
        "problem_statement": "New customers wait 3-5 days for setup.",
        "proposed_solution": "Automated onboarding workflow connecting your CRM to Slack.",
        "pricing_recommendation": "pro",
        "roi_estimate": {"monthly_savings_aud": 2000},
        "next_steps": "Book a 15-minute call this week.",
    })
    result = evaluator.evaluate_proposal(
        proposal_text=sample_proposal,
        context={
            'vertical': 'SaaS',
            'pain_point': 'Manual onboarding takes 10 hours/week',
            'deal_value': 2497,
            'business_size': 'small',
        },
    )
    print(f"   Score: {result.score}/100")
    print(f"   Pass: {result.pass_threshold}")
    print(f"   Dimensions: {result.dimensions}")
    print(f"   Feedback: {result.feedback}")

    print("\n" + "=" * 60)
    print(" EVALUATOR ready for ATLAS integration")
    print("=" * 60)


if __name__ == "__main__":
    main()
