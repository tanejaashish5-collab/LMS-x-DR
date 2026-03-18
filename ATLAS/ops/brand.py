"""
Brand Identity Configuration for ForgeVoice Studio
All client-facing communications use this identity.
ATLAS is the internal AI engine — never mentioned to clients.
"""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass(frozen=True)
class BrandIdentity:
    """Immutable brand identity for all outreach and client comms."""

    company_name: str = "ForgeVoice Studio"
    website: str = "https://forgevoice.studio"
    domain: str = "forgevoice.studio"

    # Email addresses
    email_primary: str = "ashish@forgevoice.studio"
    email_sales: str = "sales@forgevoice.studio"
    email_support: str = "support@forgevoice.studio"
    email_billing: str = "billing@forgevoice.studio"

    # Founder info
    founder: str = "Ashish Taneja"
    founder_title: str = "Founder & CEO"
    founder_email: str = "ashish@forgevoice.studio"
    founder_calendly: str = "https://calendly.com/ashishtaneja"

    # Location
    location: str = "Canberra, ACT, Australia"
    timezone: str = "AEST (UTC+10)"
    country_code: str = "AU"

    # Messaging
    tagline: str = (
        "AI-Powered Digital Solutions for Growing Businesses"
    )
    value_prop: str = (
        "We build high-converting landing pages and automation workflows "
        "powered by AI — delivered in days, not months."
    )
    one_liner: str = (
        "From idea to live site in 72 hours. "
        "AI does the heavy lifting, you get the results."
    )

    # Financial
    currency: str = "AUD"
    abn: str = ""  # To be filled when registered

    # Business hours (AEST)
    business_hours: str = "Mon-Fri 9:00 AM - 6:00 PM AEST"
    response_sla_hours: int = 24


BRAND = BrandIdentity()

# Social links — separate dict to keep the frozen dataclass clean
SOCIAL_LINKS: Dict[str, str] = {
    "linkedin": "https://linkedin.com/company/forgevoice-studio",
    "twitter": "https://twitter.com/forgevoicestudio",
    "github": "https://github.com/forgevoice-studio",
}

# Payment methods accepted
PAYMENT_METHODS: List[str] = [
    "Stripe (Credit/Debit Card)",
    "Bank Transfer (AU domestic)",
    "PayTo (Australian instant payment)",
]

# Legal boilerplate
LEGAL = {
    "terms_url": "https://forgevoice.studio/terms",
    "privacy_url": "https://forgevoice.studio/privacy",
    "refund_policy": (
        "Full refund within 7 days if we haven't started building. "
        "50% refund if first draft has been delivered but doesn't meet "
        "the agreed requirements. No refund after final approval."
    ),
    "payment_terms": "50% upfront, 50% on delivery. Enterprise: NET 14.",
}


def get_email_signature(sender_name: str = "") -> str:
    """Generate a professional email signature."""
    name = sender_name or BRAND.founder
    return (
        f"\n---\n"
        f"{name}\n"
        f"{BRAND.company_name}\n"
        f"{BRAND.website}\n"
        f"{BRAND.email_primary}\n"
        f"{BRAND.location}\n"
    )


def get_email_from(email_type: str = "sales") -> str:
    """Return the correct from-address for a given email type."""
    email_map = {
        "sales": BRAND.email_sales,
        "support": BRAND.email_support,
        "billing": BRAND.email_billing,
        "founder": BRAND.founder_email,
        "primary": BRAND.email_primary,
    }
    return email_map.get(email_type, BRAND.email_primary)
