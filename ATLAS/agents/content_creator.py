#!/usr/bin/env python3
"""
CONTENT CREATOR Agent - Social Media Content for ForgeVoice Studio
Generates daily LinkedIn + Instagram content on a 4-pillar rotation.

Schedule: Daily at 8:00 PM AEST (generate next day's content)
Model: Claude Haiku (~$0.01/post)
Pillars: industry, behind_scenes, value_bomb, social_proof
"""

import os
import json
import logging
from datetime import date, datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from supabase import create_client, Client
import anthropic

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("CONTENT_CREATOR")


# ===========================================
# Data Models
# ===========================================

@dataclass
class ContentPiece:
    """A single piece of generated content."""
    pillar: str
    platform: str
    topic: str
    headline: str
    body: str
    hashtags: str
    carousel_slides: List[Dict[str, str]]
    scheduled_for: str  # ISO date string
    status: str = "draft"


# ===========================================
# Topic Banks
# ===========================================

INDUSTRY_TOPICS: List[str] = [
    "Why local businesses lose $50K/year with bad websites",
    "The accounting firm website formula that generates 3 leads/week",
    "E-commerce landing pages: the layout that converts at 8%",
    "SaaS founders: your $20K website could be $2K. Here's proof.",
    "Real estate agents: your listings page is costing you commissions",
    "Health & wellness practitioners: online booking = 40% more clients",
    "Agencies: stop building client websites manually",
    "Education creators: your course page is losing students",
    "Why 73% of small businesses still don't have a mobile-friendly site",
    "The restaurant website mistake that's costing you reservations",
    "Law firms: your website is your first impression. Most fail.",
    "Tradies losing $30K/year by not having a simple landing page",
    "Fitness studios: the online booking page that fills classes",
    "Dentists: the patient intake form that saves 2 hours/day",
    "Consultants: the one-page site that books 5 calls/week",
]

BEHIND_SCENES_TOPICS: List[str] = [
    "How AI analyzes 125+ business opportunities while you sleep",
    "We built a complete website in 4 hours. Here's the process.",
    "Inside ATLAS: the 5 AI agents running my business",
    "From Reddit post to client proposal in 72 hours",
    "I spent $30 on AI this month. It found $50K in deals.",
    "What happens when AI writes your sales emails",
    "The dashboard that shows me everything my AI is doing",
    "How we deploy a production website without touching code",
    "Our AI read 500 Reddit posts this week. Here's what it found.",
    "The budget guardian: how AI keeps itself under $250/month",
    "5 AI agents, zero employees, one founder. Inside my stack.",
    "How I automated client proposals with Claude + Supabase",
    "The 3 AM discovery: when AI finds leads while you sleep",
    "Building in public: our AI system's first 30 days",
    "How one Python script replaced a $5K/month marketing agency",
]

VALUE_BOMB_TOPICS: List[str] = [
    "5 things your landing page is missing right now",
    "The 3-second rule: why visitors leave your site",
    "Dark mode websites convert 23% better. Here's why.",
    "The email capture strategy that gets 15% opt-in rates",
    "Stop using stock photos. Here's what to use instead.",
    "Your CTA button color matters more than you think",
    "The hero section formula: headline + subhead + CTA + trust",
    "Speed kills: every second of load time costs you 7% conversion",
    "The 5-page website framework that works for any business",
    "Why your contact form is killing your leads",
    "The pricing page layout that increases conversions by 35%",
    "Mobile-first design: 3 changes that double your mobile leads",
    "The testimonial placement trick that boosts trust by 40%",
    "Why your about page is your secret weapon (and how to fix it)",
    "The follow-up email template that gets 42% open rates",
]

SOCIAL_PROOF_TOPICS: List[str] = [
    "Here's what a $997 AI-built landing page looks like",
    "Our AI found 34 businesses needing help this week",
    "5 demo pages, 5 industries, all built by AI this week",
    "From idea to live website: a visual timeline",
    "The numbers after 30 days of running AI agents",
    "What our clients see in their real-time dashboard",
    "Before vs after: a local business website transformation",
    "3 landing pages built in one afternoon. Here's the result.",
    "The pipeline: from Reddit pain point to paying client",
    "Demo day: real estate agent landing page walkthrough",
    "Client spotlight: how a dentist got 40% more bookings",
    "The proposal that closed in 48 hours (and what made it work)",
]

TOPIC_BANKS: Dict[str, List[str]] = {
    "industry": INDUSTRY_TOPICS,
    "behind_scenes": BEHIND_SCENES_TOPICS,
    "value_bomb": VALUE_BOMB_TOPICS,
    "social_proof": SOCIAL_PROOF_TOPICS,
}

# Pillar rotation by day-of-week (Monday=0, Sunday=6)
PILLAR_ROTATION: Dict[int, str] = {
    0: "industry",       # Monday
    1: "behind_scenes",  # Tuesday
    2: "value_bomb",     # Wednesday
    3: "industry",       # Thursday
    4: "behind_scenes",  # Friday
    5: "value_bomb",     # Saturday
    6: "social_proof",   # Sunday
}


# ===========================================
# Content Creator Agent Class
# ===========================================

class ContentCreatorAgent:
    """
    Content generation agent for ForgeVoice Studio social media.

    Responsibilities:
    - Generate daily LinkedIn + Instagram content
    - Follow 4-pillar rotation schedule
    - Store drafts in atlas_content table
    - Track generation costs via agent logs
    """

    def __init__(
        self,
        supabase_url: Optional[str] = None,
        supabase_key: Optional[str] = None,
        anthropic_key: Optional[str] = None,
        vault_agent: Optional[Any] = None,
    ):
        """
        Initialize Content Creator agent.

        Args:
            supabase_url: Supabase project URL
            supabase_key: Supabase anon key
            anthropic_key: Anthropic API key
            vault_agent: VAULT agent for budget checks
        """
        self.supabase_url = supabase_url or os.getenv("SUPABASE_URL")
        self.supabase_key = supabase_key or os.getenv("SUPABASE_ANON_KEY")

        if not self.supabase_url or not self.supabase_key:
            raise ValueError(
                "SUPABASE_URL and SUPABASE_ANON_KEY environment variables required"
            )

        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)

        self.anthropic_key = anthropic_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.anthropic_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable required")
        self.client = anthropic.Anthropic(api_key=self.anthropic_key)

        self.vault = vault_agent
        logger.info("CONTENT_CREATOR initialized - Ready to generate content")

    # ===========================================
    # Public Methods
    # ===========================================

    async def generate_daily_content(self, target_date: date) -> Dict[str, Any]:
        """
        Generate content for a specific date based on pillar rotation.

        Args:
            target_date: The date to generate content for.

        Returns:
            Dict with generated content details or error.
        """
        pillar = self._get_pillar_for_date(target_date)
        topic = self._get_topic_for_pillar(pillar, target_date)

        logger.info(
            f"Generating {pillar} content for {target_date.isoformat()}: {topic}"
        )

        # Budget check via VAULT if available
        if self.vault:
            from agents.vault import BudgetRequest

            budget_req = BudgetRequest(
                amount=0.02,
                agent="content_creator",
                description=f"Content generation: {pillar} for {target_date}",
            )
            budget_result = self.vault.check_budget(budget_req)
            if not budget_result["approved"]:
                logger.warning(f"Budget blocked: {budget_result['reason']}")
                return {"status": "blocked", "reason": budget_result["reason"]}

        # Generate LinkedIn post
        linkedin_result = self._generate_linkedin_post(pillar, topic, target_date)

        # Generate Instagram carousel
        carousel_result = self._generate_instagram_carousel(pillar, topic)

        # Save to database
        content_piece = ContentPiece(
            pillar=pillar,
            platform="both",
            topic=topic,
            headline=linkedin_result["headline"],
            body=linkedin_result["body"],
            hashtags=linkedin_result["hashtags"],
            carousel_slides=carousel_result["slides"],
            scheduled_for=target_date.isoformat(),
        )

        saved = self._save_content(content_piece)

        return {
            "status": "generated" if saved else "error",
            "date": target_date.isoformat(),
            "pillar": pillar,
            "topic": topic,
            "headline": linkedin_result["headline"],
            "word_count": len(linkedin_result["body"].split()),
            "carousel_slides": len(carousel_result["slides"]),
        }

    async def generate_batch(
        self, start_date: date, days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Generate a batch of content for multiple days.

        Args:
            start_date: First date in the batch.
            days: Number of days to generate (default 30).

        Returns:
            List of generation results.
        """
        results: List[Dict[str, Any]] = []
        for i in range(days):
            target_date = start_date + timedelta(days=i)
            result = await self.generate_daily_content(target_date)
            results.append(result)
            logger.info(
                f"Batch progress: {i + 1}/{days} - "
                f"{result.get('pillar', '?')}: {result.get('status', '?')}"
            )

        generated = sum(1 for r in results if r.get("status") == "generated")
        logger.info(f"Batch complete: {generated}/{days} pieces generated")

        # Log batch run
        self._log_agent_action(
            action="batch_generate",
            details=f"Generated {generated}/{days} content pieces starting {start_date}",
        )

        return results

    async def get_pending_content(self) -> List[Dict[str, Any]]:
        """
        Get all draft content awaiting review.

        Returns:
            List of draft content entries.
        """
        try:
            result = (
                self.supabase.table("atlas_content")
                .select("*")
                .eq("status", "draft")
                .order("scheduled_for")
                .execute()
            )
            return result.data or []
        except Exception as e:
            logger.error(f"Failed to get pending content: {e}")
            return []

    async def get_content_stats(self) -> Dict[str, Any]:
        """Get content generation statistics."""
        try:
            total = (
                self.supabase.table("atlas_content")
                .select("id", count="exact")
                .execute()
            )
            drafts = (
                self.supabase.table("atlas_content")
                .select("id", count="exact")
                .eq("status", "draft")
                .execute()
            )
            posted = (
                self.supabase.table("atlas_content")
                .select("id", count="exact")
                .eq("status", "posted")
                .execute()
            )

            # Upcoming schedule
            upcoming = (
                self.supabase.table("atlas_content")
                .select("scheduled_for, pillar, topic, headline")
                .eq("status", "draft")
                .gte("scheduled_for", date.today().isoformat())
                .order("scheduled_for")
                .limit(7)
                .execute()
            )

            return {
                "total_content": total.count or 0,
                "drafts": drafts.count or 0,
                "posted": posted.count or 0,
                "upcoming_week": upcoming.data or [],
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Failed to get content stats: {e}")
            return {"error": str(e)}

    # ===========================================
    # Pillar & Topic Selection
    # ===========================================

    def _get_pillar_for_date(self, target_date: date) -> str:
        """
        Determine content pillar based on day of week.

        Monday/Thursday: industry
        Tuesday/Friday: behind_scenes
        Wednesday/Saturday: value_bomb
        Sunday: social_proof
        """
        weekday = target_date.weekday()  # 0=Mon, 6=Sun
        return PILLAR_ROTATION[weekday]

    def _get_topic_for_pillar(self, pillar: str, target_date: date) -> str:
        """
        Select a topic for the given pillar.
        Uses date-based indexing to cycle through topics without repetition.
        """
        topics = TOPIC_BANKS.get(pillar, INDUSTRY_TOPICS)
        # Use day-of-year to cycle through topics deterministically
        day_index = target_date.timetuple().tm_yday
        return topics[day_index % len(topics)]

    # ===========================================
    # LinkedIn Generation
    # ===========================================

    def _generate_linkedin_post(
        self, pillar: str, topic: str, target_date: date
    ) -> Dict[str, str]:
        """
        Generate a full LinkedIn post using Claude Haiku.

        Returns:
            Dict with 'headline', 'body', and 'hashtags'.
        """
        pillar_instructions = {
            "industry": (
                "Write a deep-dive LinkedIn post about a specific business vertical. "
                "Include real numbers, specific pain points, and actionable solutions. "
                "Position ForgeVoice Studio as the expert that solves this exact problem. "
                "Reference specific tools, metrics, and industry benchmarks."
            ),
            "behind_scenes": (
                "Write a behind-the-scenes LinkedIn post about building with AI. "
                "Share specific numbers (costs, time saved, opportunities found). "
                "Make the reader feel like they're getting insider access to something "
                "cutting-edge. Be transparent about the process, tools, and results."
            ),
            "value_bomb": (
                "Write an actionable LinkedIn post that gives immediate value. "
                "The reader should be able to implement at least one thing today. "
                "Use specific examples, percentages, and before/after comparisons. "
                "Make it practical, not theoretical."
            ),
            "social_proof": (
                "Write a LinkedIn post that showcases results and builds credibility. "
                "Use specific numbers, timelines, and visual descriptions. "
                "Make the reader think 'I want that for my business.' "
                "Include a clear path to working with ForgeVoice Studio."
            ),
        }

        prompt = f"""You are Ashish Taneja, founder of ForgeVoice Studio. Write a LinkedIn post.

VOICE RULES (non-negotiable):
- Direct, confident, founder-tone. NOT corporate. NOT AI-sounding.
- Like talking to a smart friend who knows business.
- Use numbers, real examples, specific details.
- Short paragraphs (1-3 sentences max).
- Start with a hook line that stops the scroll.
- No fluff. No filler. Every sentence earns its place.
- Australian founder based in Canberra building with AI.

BRAND:
- Company: ForgeVoice Studio
- What we do: AI-powered landing pages and digital solutions, delivered in 72 hours
- Website: https://forgevoice.studio
- AI engine: ATLAS (5 autonomous agents) - can mention when relevant
- Pricing: Starting at $997 AUD for landing pages

PILLAR: {pillar}
TOPIC: {topic}
DATE: {target_date.isoformat()} ({target_date.strftime('%A')})

{pillar_instructions.get(pillar, '')}

FORMAT:
1. Hook line (attention-grabbing first line, separated by line break)
2. 2-3 paragraphs of real value (total 700-1200 words)
3. Actionable takeaway the reader can use today
4. CTA: "Follow for daily AI + business insights. DM me 'BUILD' for a free assessment."
5. 5-7 hashtags on the last line

Respond in this exact format:
HEADLINE: [compelling headline, max 100 chars]
---
[full post body, 700-1200 words]
---
HASHTAGS: [5-7 hashtags separated by spaces]"""

        try:
            message = self.client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}],
            )

            response = message.content[0].text.strip()

            # Parse response
            headline = ""
            body = ""
            hashtags = ""

            sections = response.split("---")

            if len(sections) >= 1:
                first_section = sections[0].strip()
                if first_section.startswith("HEADLINE:"):
                    headline = first_section.replace("HEADLINE:", "").strip()

            if len(sections) >= 2:
                body = sections[1].strip()

            if len(sections) >= 3:
                last_section = sections[-1].strip()
                if "HASHTAGS:" in last_section:
                    hashtags = last_section.replace("HASHTAGS:", "").strip()
                else:
                    hashtags = last_section.strip()

            # Fallback parsing if --- split didn't work
            if not body:
                lines = response.split("\n")
                body_lines: List[str] = []
                for line in lines:
                    if line.startswith("HEADLINE:"):
                        headline = line.replace("HEADLINE:", "").strip()
                    elif line.startswith("HASHTAGS:"):
                        hashtags = line.replace("HASHTAGS:", "").strip()
                    else:
                        body_lines.append(line)
                body = "\n".join(body_lines).strip()

            # Log API call
            self._log_api_call(
                action="linkedin_generate",
                model="claude-haiku-4-5-20251001",
                input_tokens=message.usage.input_tokens,
                output_tokens=message.usage.output_tokens,
                status="success",
            )

            return {"headline": headline, "body": body, "hashtags": hashtags}

        except Exception as e:
            logger.error(f"LinkedIn generation failed: {e}")
            return {
                "headline": f"[GENERATION FAILED] {topic}",
                "body": f"Generation error for topic: {topic}\nError: {str(e)}",
                "hashtags": "#ForgeVoiceStudio #AI",
            }

    # ===========================================
    # Instagram Carousel Generation
    # ===========================================

    def _generate_instagram_carousel(
        self, pillar: str, topic: str
    ) -> Dict[str, Any]:
        """
        Generate Instagram carousel slides using Claude Haiku.

        Returns:
            Dict with 'slides' list of {slide, text} dicts.
        """
        prompt = f"""Create an Instagram carousel for ForgeVoice Studio.

TOPIC: {topic}
PILLAR: {pillar}

RULES:
- 6 slides total
- Slide 1: Bold hook headline (max 8 words, attention-grabbing)
- Slides 2-5: Key points with short text (max 20 words per slide)
- Slide 6: CTA with @forgevoicestudio
- Use numbers and specifics where possible
- Each slide should standalone but flow as a story

Respond in this exact JSON format (no other text):
[
  {{"slide": 1, "text": "Bold Hook Here"}},
  {{"slide": 2, "text": "Key point with number"}},
  {{"slide": 3, "text": "Another insight"}},
  {{"slide": 4, "text": "Actionable tip"}},
  {{"slide": 5, "text": "Supporting data point"}},
  {{"slide": 6, "text": "DM us BUILD for a free assessment @forgevoicestudio"}}
]"""

        try:
            message = self.client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}],
            )

            response = message.content[0].text.strip()

            # Extract JSON from response
            start = response.find("[")
            end = response.rfind("]") + 1
            if start != -1 and end > start:
                slides = json.loads(response[start:end])
            else:
                slides = [
                    {"slide": 1, "text": topic},
                    {"slide": 2, "text": "AI-powered solutions"},
                    {"slide": 3, "text": "72-hour delivery"},
                    {"slide": 4, "text": "Starting at $997 AUD"},
                    {"slide": 5, "text": "5 AI agents working for you"},
                    {"slide": 6, "text": "DM BUILD @forgevoicestudio"},
                ]

            self._log_api_call(
                action="carousel_generate",
                model="claude-haiku-4-5-20251001",
                input_tokens=message.usage.input_tokens,
                output_tokens=message.usage.output_tokens,
                status="success",
            )

            return {"slides": slides}

        except Exception as e:
            logger.error(f"Carousel generation failed: {e}")
            return {
                "slides": [
                    {"slide": 1, "text": topic},
                    {"slide": 2, "text": "AI-powered digital solutions"},
                    {"slide": 3, "text": "Delivered in 72 hours"},
                    {"slide": 4, "text": "Starting at $997 AUD"},
                    {"slide": 5, "text": "5 AI agents, zero delays"},
                    {"slide": 6, "text": "DM BUILD @forgevoicestudio"},
                ]
            }

    # ===========================================
    # Database Operations
    # ===========================================

    def _save_content(self, content: ContentPiece) -> bool:
        """Save generated content to atlas_content table."""
        try:
            # Check for duplicate (same date + pillar)
            existing = (
                self.supabase.table("atlas_content")
                .select("id")
                .eq("scheduled_for", content.scheduled_for)
                .eq("pillar", content.pillar)
                .execute()
            )

            if existing.data:
                logger.warning(
                    f"Content already exists for {content.scheduled_for} "
                    f"({content.pillar}) - skipping"
                )
                return False

            data = {
                "pillar": content.pillar,
                "platform": content.platform,
                "topic": content.topic,
                "headline": content.headline,
                "body": content.body,
                "hashtags": content.hashtags,
                "carousel_slides": json.dumps(content.carousel_slides),
                "status": content.status,
                "scheduled_for": content.scheduled_for,
            }

            result = self.supabase.table("atlas_content").insert(data).execute()

            if result.data:
                logger.info(
                    f"Saved content: {content.pillar} for {content.scheduled_for}"
                )
                return True

            return False

        except Exception as e:
            logger.error(f"Failed to save content: {e}")
            return False

    # ===========================================
    # Logging
    # ===========================================

    def _log_api_call(
        self,
        action: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        status: str,
    ) -> None:
        """Log API call to agent logs table."""
        try:
            if "haiku" in model:
                cost = (input_tokens * 0.00025 + output_tokens * 0.00125) / 1000
            else:
                cost = (input_tokens * 0.003 + output_tokens * 0.015) / 1000

            self.supabase.table("atlas_agent_logs").insert(
                {
                    "agent": "content_creator",
                    "action": action,
                    "model_used": model,
                    "tokens_in": input_tokens,
                    "tokens_out": output_tokens,
                    "cost_usd": cost,
                    "status": status,
                }
            ).execute()
        except Exception as e:
            logger.error(f"Failed to log API call: {e}")

    def _log_agent_action(self, action: str, details: str) -> None:
        """Log a general agent action."""
        try:
            self.supabase.table("atlas_agent_logs").insert(
                {
                    "agent": "content_creator",
                    "action": action,
                    "input": details,
                    "status": "success",
                }
            ).execute()
        except Exception as e:
            logger.error(f"Failed to log action: {e}")


# ===========================================
# Standalone Testing
# ===========================================

def main() -> None:
    """Test Content Creator agent functionality."""
    import asyncio

    print("=" * 60)
    print(" CONTENT CREATOR Agent - Social Media Content")
    print("=" * 60)

    creator = ContentCreatorAgent()

    # Test: generate content for tomorrow
    tomorrow = date.today() + timedelta(days=1)
    print(f"\nGenerating content for {tomorrow.isoformat()}...")

    result = asyncio.run(creator.generate_daily_content(tomorrow))
    print(f"Status: {result.get('status')}")
    print(f"Pillar: {result.get('pillar')}")
    print(f"Topic: {result.get('topic')}")
    print(f"Headline: {result.get('headline')}")
    print(f"Word count: {result.get('word_count')}")
    print(f"Carousel slides: {result.get('carousel_slides')}")

    print("\n" + "=" * 60)
    print(" CONTENT_CREATOR agent ready for ATLAS orchestrator")
    print("=" * 60)


if __name__ == "__main__":
    main()
