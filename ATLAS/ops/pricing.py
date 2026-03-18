"""
Pricing Engine for ForgeVoice Studio
Defines pricing tiers per service type and helper functions
for generating proposals and quotes.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class PricingTier:
    """Single pricing tier for a service."""

    name: str
    price_aud: int
    includes: List[str]
    delivery_days: int
    revisions: int
    support_days: int


@dataclass
class ServicePricing:
    """All tiers for a single service type."""

    service_name: str
    description: str
    tiers: Dict[str, PricingTier]


# =============================================
# Landing Page Pricing
# =============================================

LANDING_PAGE_PRICING = ServicePricing(
    service_name="Landing Page",
    description="High-converting landing pages built with AI, deployed in days.",
    tiers={
        "basic": PricingTier(
            name="Starter",
            price_aud=997,
            delivery_days=3,
            revisions=2,
            support_days=14,
            includes=[
                "Single-page responsive landing page",
                "Mobile-optimized design",
                "Contact form with email notifications",
                "SEO meta tags and Open Graph setup",
                "Google Analytics integration",
                "Custom domain setup",
                "2 rounds of revisions",
                "14-day post-launch support",
            ],
        ),
        "pro": PricingTier(
            name="Professional",
            price_aud=2497,
            delivery_days=5,
            revisions=3,
            support_days=30,
            includes=[
                "Multi-page site (up to 5 pages)",
                "CRM integration (HubSpot, Pipedrive, or similar)",
                "Analytics dashboard with conversion tracking",
                "A/B testing setup for hero section",
                "Email capture with automated welcome sequence",
                "Live chat widget integration",
                "Speed optimization (90+ Lighthouse score)",
                "3 rounds of revisions",
                "30-day post-launch support",
            ],
        ),
        "enterprise": PricingTier(
            name="Enterprise",
            price_aud=4997,
            delivery_days=10,
            revisions=5,
            support_days=90,
            includes=[
                "Full marketing site (up to 12 pages)",
                "Custom automation workflows (up to 3)",
                "API integrations with existing tools",
                "Advanced analytics and reporting dashboard",
                "Multi-variant A/B testing",
                "Ongoing conversion rate optimization (30 days)",
                "Priority Slack/email support",
                "Monthly performance report",
                "5 rounds of revisions",
                "90-day post-launch support",
            ],
        ),
    },
)

# =============================================
# Automation Workflow Pricing
# =============================================

AUTOMATION_WORKFLOW_PRICING = ServicePricing(
    service_name="Automation Workflow",
    description="Custom business automation that eliminates manual work.",
    tiers={
        "basic": PricingTier(
            name="Single Flow",
            price_aud=1497,
            delivery_days=5,
            revisions=2,
            support_days=14,
            includes=[
                "1 automated workflow (up to 5 steps)",
                "Integration with 2 apps (e.g., Gmail + Sheets)",
                "Error handling and retry logic",
                "Documentation and handover guide",
                "2 rounds of revisions",
                "14-day monitoring and support",
            ],
        ),
        "pro": PricingTier(
            name="Workflow Suite",
            price_aud=3497,
            delivery_days=10,
            revisions=3,
            support_days=30,
            includes=[
                "Up to 3 connected workflows",
                "Integration with up to 5 apps",
                "Conditional logic and branching",
                "Scheduled triggers and webhooks",
                "Data transformation and formatting",
                "Error alerting via Slack or email",
                "Performance monitoring dashboard",
                "3 rounds of revisions",
                "30-day monitoring and support",
            ],
        ),
        "enterprise": PricingTier(
            name="Full Automation",
            price_aud=6997,
            delivery_days=15,
            revisions=5,
            support_days=90,
            includes=[
                "Unlimited workflows for 1 business process",
                "Integration with all required systems",
                "Custom API development if needed",
                "AI-powered decision steps (e.g., classification)",
                "Full audit trail and logging",
                "Failover and backup workflows",
                "Staff training session (1 hour)",
                "Monthly optimization review",
                "5 rounds of revisions",
                "90-day monitoring and support",
            ],
        ),
    },
)

# =============================================
# Full Digital Presence Pricing
# =============================================

FULL_DIGITAL_PRESENCE_PRICING = ServicePricing(
    service_name="Full Digital Presence",
    description="Landing page + automation + ongoing optimization, all-in-one.",
    tiers={
        "basic": PricingTier(
            name="Launchpad",
            price_aud=2997,
            delivery_days=7,
            revisions=3,
            support_days=30,
            includes=[
                "Professional landing page (single page)",
                "1 automation workflow",
                "Email capture with welcome sequence",
                "CRM integration",
                "Google Analytics and conversion tracking",
                "Custom domain and SSL setup",
                "3 rounds of revisions",
                "30-day post-launch support",
            ],
        ),
        "pro": PricingTier(
            name="Growth",
            price_aud=5997,
            delivery_days=14,
            revisions=4,
            support_days=60,
            includes=[
                "Multi-page site (up to 5 pages)",
                "3 automation workflows",
                "Email marketing setup (sequences + templates)",
                "CRM integration with lead scoring",
                "A/B testing on landing pages",
                "Social media auto-posting workflow",
                "Monthly analytics report",
                "4 rounds of revisions",
                "60-day post-launch support",
            ],
        ),
        "enterprise": PricingTier(
            name="Dominate",
            price_aud=9997,
            delivery_days=21,
            revisions=6,
            support_days=90,
            includes=[
                "Full marketing site (up to 12 pages)",
                "Unlimited automation workflows",
                "AI-powered lead qualification",
                "Custom reporting dashboard",
                "Multi-channel outreach automation",
                "Booking system integration",
                "Staff training (2 hours)",
                "Bi-weekly optimization calls",
                "6 rounds of revisions",
                "90-day dedicated support",
            ],
        ),
    },
)

# =============================================
# All services indexed for lookup
# =============================================

ALL_SERVICES: Dict[str, ServicePricing] = {
    "landing_page": LANDING_PAGE_PRICING,
    "automation_workflow": AUTOMATION_WORKFLOW_PRICING,
    "full_digital_presence": FULL_DIGITAL_PRESENCE_PRICING,
}


# =============================================
# Helper Functions
# =============================================


def get_pricing(
    service_type: str,
    tier: Optional[str] = None,
) -> ServicePricing | PricingTier | None:
    """
    Get pricing for a service type, optionally filtered to a tier.

    Args:
        service_type: One of landing_page, automation_workflow,
                      full_digital_presence
        tier: Optional tier name (basic, pro, enterprise)

    Returns:
        ServicePricing if no tier specified, PricingTier if tier given,
        None if not found.
    """
    service = ALL_SERVICES.get(service_type)
    if service is None:
        return None
    if tier is None:
        return service
    return service.tiers.get(tier)


def format_pricing_table(service_type: str) -> str:
    """
    Generate a human-readable pricing table for proposals/emails.

    Args:
        service_type: One of landing_page, automation_workflow,
                      full_digital_presence

    Returns:
        Formatted string with pricing breakdown.
    """
    service = ALL_SERVICES.get(service_type)
    if service is None:
        return f"Unknown service type: {service_type}"

    lines = [
        f"=== {service.service_name} ===",
        service.description,
        "",
    ]

    for tier_key, tier in service.tiers.items():
        lines.append(f"--- {tier.name} (${tier.price_aud:,} AUD) ---")
        lines.append(f"  Delivery: {tier.delivery_days} business days")
        lines.append(f"  Revisions: {tier.revisions}")
        lines.append(f"  Support: {tier.support_days} days post-launch")
        lines.append("  Includes:")
        for item in tier.includes:
            lines.append(f"    - {item}")
        lines.append("")

    return "\n".join(lines)


def get_recommended_tier(
    budget_aud: float,
    service_type: str,
) -> Optional[PricingTier]:
    """
    Return the best tier that fits within a client's budget.

    Args:
        budget_aud: Client's stated budget in AUD
        service_type: Service type key

    Returns:
        The highest-value tier within budget, or None.
    """
    service = ALL_SERVICES.get(service_type)
    if service is None:
        return None

    best_fit: Optional[PricingTier] = None
    for tier in service.tiers.values():
        if tier.price_aud <= budget_aud:
            if best_fit is None or tier.price_aud > best_fit.price_aud:
                best_fit = tier

    return best_fit
