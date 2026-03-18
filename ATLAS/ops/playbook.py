"""
Vertical Playbooks for ATLAS Operations
Defines per-vertical strategy: persona, pain points, pricing,
email sequences, and delivery timelines.

Verticals are derived from Scout's categorization:
  automation_service, template_product, software_product
and the target verticals it identifies
  (Real Estate, Legal, E-commerce, Healthcare, etc.)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class VerticalPlaybook:
    """Complete operational playbook for a single vertical."""

    vertical: str
    target_persona: str
    pain_points: List[str]
    solution_type: str
    landing_page_template: str
    pricing: Dict[str, int]  # {basic, pro, enterprise} in AUD
    email_sequence: List[str]  # Sequence names to use
    proposal_template: str
    estimated_close_rate: float  # 0.0 - 1.0
    average_deal_size: float  # AUD
    delivery_timeline: str
    keywords: List[str] = field(default_factory=list)
    subreddits: List[str] = field(default_factory=list)


# =============================================
# Vertical Definitions
# =============================================

VERTICALS: Dict[str, VerticalPlaybook] = {
    "saas": VerticalPlaybook(
        vertical="SaaS",
        target_persona="SaaS founder or Head of Ops, 10-200 employees, Series A-B",
        pain_points=[
            "Manual onboarding eats 3-5 hours per new customer",
            "Churn signals go undetected until cancellation",
            "Support tickets pile up for issues automatable via self-serve",
            "Data lives in 5+ disconnected tools with no single dashboard",
            "Billing and usage reconciliation is a monthly nightmare",
        ],
        solution_type="automation_workflow",
        landing_page_template="saas_automation",
        pricing={"basic": 1497, "pro": 3497, "enterprise": 6997},
        email_sequence=["cold_outreach_saas", "warm_lead", "post_sale"],
        proposal_template="saas_workflow_proposal",
        estimated_close_rate=0.08,
        average_deal_size=3500.0,
        delivery_timeline="5-15 business days",
        keywords=["saas automation", "workflow integration", "onboarding automation"],
        subreddits=["SaaS", "startups", "EntrepreneurRideAlong"],
    ),
    "ecommerce": VerticalPlaybook(
        vertical="E-commerce",
        target_persona="DTC brand owner or ecom manager, $500K-$10M revenue",
        pain_points=[
            "Product pages don't convert — high traffic, low sales",
            "Inventory and order management spread across 3+ platforms",
            "Abandoned cart emails are generic and underperforming",
            "Returns and refund processing takes days of manual work",
            "No unified view of customer journey across channels",
        ],
        solution_type="full_digital_presence",
        landing_page_template="ecommerce_conversion",
        pricing={"basic": 2997, "pro": 5997, "enterprise": 9997},
        email_sequence=["cold_outreach_ecommerce", "warm_lead", "post_sale"],
        proposal_template="ecommerce_growth_proposal",
        estimated_close_rate=0.06,
        average_deal_size=5000.0,
        delivery_timeline="7-21 business days",
        keywords=["ecommerce optimization", "conversion rate", "shopify automation"],
        subreddits=["ecommerce", "shopify", "FulfillmentByAmazon"],
    ),
    "local_business": VerticalPlaybook(
        vertical="Local Business",
        target_persona="Local business owner (trades, retail, food), 1-20 employees",
        pain_points=[
            "No online presence beyond a Facebook page",
            "Losing customers to competitors with better Google presence",
            "Booking and scheduling done via phone and paper",
            "No way to collect reviews or respond to them systematically",
            "Spending money on ads with zero tracking on ROI",
        ],
        solution_type="landing_page",
        landing_page_template="local_business_presence",
        pricing={"basic": 997, "pro": 2497, "enterprise": 4997},
        email_sequence=["cold_outreach_local", "warm_lead", "post_sale"],
        proposal_template="local_business_proposal",
        estimated_close_rate=0.12,
        average_deal_size=1800.0,
        delivery_timeline="3-7 business days",
        keywords=["local business website", "online booking", "google my business"],
        subreddits=["smallbusiness", "Entrepreneur", "sweatystartup"],
    ),
    "agency": VerticalPlaybook(
        vertical="Agency",
        target_persona="Digital/marketing agency owner, 5-50 employees",
        pain_points=[
            "Client reporting takes a full day every month",
            "Onboarding new clients requires 10+ manual setup steps",
            "No white-label solution to resell to their own clients",
            "Project handoffs between teams cause delays and errors",
            "Proposal creation is manual, inconsistent, and slow",
        ],
        solution_type="automation_workflow",
        landing_page_template="agency_whitelabel",
        pricing={"basic": 1497, "pro": 3497, "enterprise": 6997},
        email_sequence=["cold_outreach_agency", "warm_lead", "post_sale"],
        proposal_template="agency_automation_proposal",
        estimated_close_rate=0.10,
        average_deal_size=4000.0,
        delivery_timeline="5-15 business days",
        keywords=["agency automation", "white-label", "client reporting"],
        subreddits=["digital_marketing", "Entrepreneur", "agency"],
    ),
    "real_estate": VerticalPlaybook(
        vertical="Real Estate",
        target_persona="Real estate agent or agency principal, independent or small firm",
        pain_points=[
            "Lead follow-up takes too long — hot leads go cold",
            "Property listings managed manually across 4+ portals",
            "No automated nurture for long-cycle buyers",
            "Open home registrations and follow-ups are all manual",
            "CRM is barely used because data entry is painful",
        ],
        solution_type="full_digital_presence",
        landing_page_template="real_estate_leads",
        pricing={"basic": 2997, "pro": 5997, "enterprise": 9997},
        email_sequence=["cold_outreach_realestate", "warm_lead", "post_sale"],
        proposal_template="real_estate_proposal",
        estimated_close_rate=0.07,
        average_deal_size=5500.0,
        delivery_timeline="7-14 business days",
        keywords=["real estate automation", "property listings", "lead capture"],
        subreddits=["realestateinvesting", "RealEstate", "CommercialRealEstate"],
    ),
    "health_wellness": VerticalPlaybook(
        vertical="Health & Wellness",
        target_persona="Clinic owner, physio, dentist, or wellness practitioner",
        pain_points=[
            "No-shows cost thousands per month with no automated reminders",
            "Patient intake forms are still paper-based",
            "Booking happens via phone — staff spend hours on scheduling",
            "Follow-up care reminders are inconsistent or nonexistent",
            "Online reviews are low despite high patient satisfaction",
        ],
        solution_type="landing_page",
        landing_page_template="health_booking",
        pricing={"basic": 997, "pro": 2497, "enterprise": 4997},
        email_sequence=["cold_outreach_health", "warm_lead", "post_sale"],
        proposal_template="health_wellness_proposal",
        estimated_close_rate=0.10,
        average_deal_size=2200.0,
        delivery_timeline="3-10 business days",
        keywords=["clinic booking", "patient engagement", "healthcare automation"],
        subreddits=["healthcare", "dentistry", "physicaltherapy"],
    ),
    "professional_services": VerticalPlaybook(
        vertical="Professional Services",
        target_persona="Consultant, accountant, or lawyer, solo or small firm",
        pain_points=[
            "Client acquisition depends entirely on referrals — no online funnel",
            "Scheduling back-and-forth eats 30+ minutes per meeting",
            "Invoice creation and follow-up is all manual",
            "Document collection from clients is a chaos of email threads",
            "No differentiation from competitors online",
        ],
        solution_type="landing_page",
        landing_page_template="professional_services_site",
        pricing={"basic": 997, "pro": 2497, "enterprise": 4997},
        email_sequence=["cold_outreach_professional", "warm_lead", "post_sale"],
        proposal_template="professional_services_proposal",
        estimated_close_rate=0.09,
        average_deal_size=2000.0,
        delivery_timeline="3-7 business days",
        keywords=["consulting website", "professional booking", "lead generation"],
        subreddits=["consulting", "Accounting", "freelance"],
    ),
    "education": VerticalPlaybook(
        vertical="Education",
        target_persona="Course creator, tutor, or training company, online or hybrid",
        pain_points=[
            "Course sales pages look amateur and don't convert",
            "Student onboarding is manual email + spreadsheet tracking",
            "No automated drip content or engagement sequences",
            "Certificate generation is a copy-paste nightmare",
            "Can't measure student outcomes or completion rates easily",
        ],
        solution_type="full_digital_presence",
        landing_page_template="education_course",
        pricing={"basic": 2997, "pro": 5997, "enterprise": 9997},
        email_sequence=["cold_outreach_education", "warm_lead", "post_sale"],
        proposal_template="education_platform_proposal",
        estimated_close_rate=0.07,
        average_deal_size=4500.0,
        delivery_timeline="7-21 business days",
        keywords=["course platform", "student engagement", "online education"],
        subreddits=["Entrepreneur", "edtech", "OnlineEducation"],
    ),
}


# =============================================
# Lookup Functions
# =============================================


def get_playbook_for_vertical(vertical: str) -> Optional[VerticalPlaybook]:
    """
    Get the playbook for a vertical.

    Args:
        vertical: Vertical key (saas, ecommerce, local_business, etc.)
                  Also accepts display names like "Real Estate" or
                  Scout category strings like "Legal Services".

    Returns:
        VerticalPlaybook or None if not found.
    """
    # Direct key lookup
    key = vertical.lower().replace(" ", "_").replace("&", "").replace("/", "_")
    if key in VERTICALS:
        return VERTICALS[key]

    # Fuzzy match on display name
    vertical_lower = vertical.lower()
    for vkey, playbook in VERTICALS.items():
        if vertical_lower in playbook.vertical.lower():
            return playbook

    # Map common Scout vertical labels to our keys
    scout_mapping: Dict[str, str] = {
        "legal services": "professional_services",
        "legal": "professional_services",
        "accounting": "professional_services",
        "finance": "professional_services",
        "healthcare": "health_wellness",
        "fitness": "health_wellness",
        "medical": "health_wellness",
        "dental": "health_wellness",
        "retail": "ecommerce",
        "shopify": "ecommerce",
        "amazon": "ecommerce",
        "dtc": "ecommerce",
        "property": "real_estate",
        "real estate": "real_estate",
        "mortgage": "real_estate",
        "marketing agency": "agency",
        "digital marketing": "agency",
        "web agency": "agency",
        "restaurant": "local_business",
        "trades": "local_business",
        "plumbing": "local_business",
        "cleaning": "local_business",
        "coaching": "education",
        "training": "education",
        "tutoring": "education",
        "online course": "education",
        "software": "saas",
        "b2b saas": "saas",
        "startup": "saas",
    }

    for label, target_key in scout_mapping.items():
        if label in vertical_lower:
            return VERTICALS.get(target_key)

    return None


def list_verticals() -> List[str]:
    """Return all supported vertical keys."""
    return list(VERTICALS.keys())


def get_all_playbooks() -> Dict[str, VerticalPlaybook]:
    """Return all playbooks."""
    return VERTICALS.copy()
