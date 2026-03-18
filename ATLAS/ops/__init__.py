"""
ATLAS Operations Module
Complete operational framework for ForgeVoice Studio's ATLAS engine.

Modules:
    brand       — Business identity for all client communications
    pricing     — Pricing engine per service type and tier
    playbook    — Per-vertical strategy (persona, pain points, pricing)
    onboarding  — Client onboarding state machine
    email_sequences — Outreach, nurture, and post-sale email flows
    landing_page_playbook — FORGE build specs per vertical
    reporting   — Metrics, alerts, and report configurations

Usage:
    from ATLAS.ops import BRAND, get_playbook_for_vertical, get_pricing
    from ATLAS.ops import get_sequence, get_landing_page_spec
"""

from .brand import (
    BRAND,
    SOCIAL_LINKS,
    PAYMENT_METHODS,
    LEGAL,
    get_email_signature,
    get_email_from,
)
from .pricing import (
    get_pricing,
    format_pricing_table,
    get_recommended_tier,
    ALL_SERVICES,
    PricingTier,
    ServicePricing,
)
from .playbook import (
    get_playbook_for_vertical,
    get_all_playbooks,
    list_verticals,
    VerticalPlaybook,
)
from .onboarding import (
    get_onboarding_steps,
    get_step_by_name,
    get_next_step,
    get_step_by_trigger,
    format_onboarding_timeline,
    OnboardingStep,
    OnboardingStatus,
)
from .email_sequences import (
    get_sequence,
    get_sequence_for_stage,
    list_sequences,
    get_email_at_step,
    EmailSequence,
    EmailStep,
)
from .landing_page_playbook import (
    get_landing_page_spec,
    list_available_specs,
    get_forge_prompt_context,
    LandingPageSpec,
)
from .reporting import (
    get_daily_report_config,
    get_weekly_report_config,
    get_report_config,
    format_report_summary,
    ReportConfig,
)

__all__ = [
    # Brand
    "BRAND",
    "SOCIAL_LINKS",
    "PAYMENT_METHODS",
    "LEGAL",
    "get_email_signature",
    "get_email_from",
    # Pricing
    "get_pricing",
    "format_pricing_table",
    "get_recommended_tier",
    "ALL_SERVICES",
    "PricingTier",
    "ServicePricing",
    # Playbook
    "get_playbook_for_vertical",
    "get_all_playbooks",
    "list_verticals",
    "VerticalPlaybook",
    # Onboarding
    "get_onboarding_steps",
    "get_step_by_name",
    "get_next_step",
    "get_step_by_trigger",
    "format_onboarding_timeline",
    "OnboardingStep",
    "OnboardingStatus",
    # Email Sequences
    "get_sequence",
    "get_sequence_for_stage",
    "list_sequences",
    "get_email_at_step",
    "EmailSequence",
    "EmailStep",
    # Landing Page
    "get_landing_page_spec",
    "list_available_specs",
    "get_forge_prompt_context",
    "LandingPageSpec",
    # Reporting
    "get_daily_report_config",
    "get_weekly_report_config",
    "get_report_config",
    "format_report_summary",
    "ReportConfig",
]
