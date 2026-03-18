"""
Landing Page Playbook for ATLAS FORGE Agent
Defines per-vertical landing page specifications:
hero copy, sections, social proof, CTA, color scheme.

FORGE uses these specs to generate targeted landing pages
instead of generic one-size-fits-all pages.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class LandingPageSection:
    """A section block on the landing page."""

    name: str
    heading: str
    subheading: str
    content_type: str  # text, features, testimonials, stats, faq, pricing
    items: List[str] = field(default_factory=list)


@dataclass
class LandingPageSpec:
    """Complete specification for a vertical-specific landing page."""

    vertical: str
    hero_headline: str
    hero_subheadline: str
    hero_cta_text: str
    hero_cta_action: str  # book_call, get_quote, start_trial, contact_form
    sections: List[LandingPageSection]
    social_proof_type: str  # testimonials, case_studies, stats, logos
    color_primary: str  # hex
    color_accent: str  # hex
    color_bg: str  # hex
    usps: List[str]  # unique selling points
    trust_badges: List[str]
    meta_title: str
    meta_description: str


# =============================================
# Default CTA actions
# =============================================

CTA_ACTIONS = {
    "book_call": "https://calendly.com/ashishtaneja",
    "get_quote": "#contact-form",
    "start_trial": "#signup",
    "contact_form": "#contact-form",
}


# =============================================
# Per-Vertical Landing Page Specs
# =============================================

LANDING_PAGE_SPECS: Dict[str, LandingPageSpec] = {
    "saas": LandingPageSpec(
        vertical="SaaS",
        hero_headline="Stop Losing Customers to Manual Onboarding",
        hero_subheadline=(
            "We build custom automation workflows that cut onboarding "
            "time by 80% and reduce churn — delivered in under 2 weeks."
        ),
        hero_cta_text="Book a Free Strategy Call",
        hero_cta_action="book_call",
        sections=[
            LandingPageSection(
                name="pain",
                heading="Sound Familiar?",
                subheading="These problems cost SaaS companies thousands every month",
                content_type="features",
                items=[
                    "New users drop off because onboarding takes too many manual steps",
                    "Your team spends hours every week on tasks that should be automated",
                    "Churn signals go unnoticed until it's too late to save the customer",
                    "Data lives in 5+ tools with no unified view of customer health",
                ],
            ),
            LandingPageSection(
                name="solution",
                heading="What We Build For You",
                subheading="Custom automation, not off-the-shelf templates",
                content_type="features",
                items=[
                    "Automated onboarding flows that guide users to their 'aha' moment",
                    "Churn prediction alerts with automated win-back sequences",
                    "Cross-platform data sync eliminating manual data entry",
                    "Custom dashboards showing metrics that actually matter",
                ],
            ),
            LandingPageSection(
                name="proof",
                heading="Results That Speak",
                subheading="",
                content_type="stats",
                items=[
                    "80% reduction in manual onboarding time",
                    "35% decrease in first-month churn",
                    "15+ hours saved per team member per week",
                    "Delivered in 5-15 business days",
                ],
            ),
            LandingPageSection(
                name="pricing",
                heading="Simple, Transparent Pricing",
                subheading="One-time investment, no monthly fees",
                content_type="pricing",
                items=[
                    "Single Flow: $1,497 AUD — 1 workflow, 2 integrations",
                    "Workflow Suite: $3,497 AUD — 3 workflows, 5 integrations",
                    "Full Automation: $6,997 AUD — Unlimited workflows, AI steps",
                ],
            ),
            LandingPageSection(
                name="faq",
                heading="Common Questions",
                subheading="",
                content_type="faq",
                items=[
                    "How long does it take? 5-15 business days depending on scope.",
                    "What tools do you integrate? Any tool with an API — Stripe, HubSpot, Slack, etc.",
                    "What if it breaks? 90-day support and monitoring included.",
                    "Do I need to be technical? No. We handle everything.",
                ],
            ),
        ],
        social_proof_type="stats",
        color_primary="#6366F1",  # Indigo
        color_accent="#818CF8",
        color_bg="#0F172A",  # Dark slate
        usps=[
            "AI-powered build — 10x faster than agencies",
            "Flat pricing — no hourly surprises",
            "90-day monitoring included",
        ],
        trust_badges=[
            "Australian-owned business",
            "10+ SaaS clients served",
            "7-day money-back guarantee",
        ],
        meta_title="SaaS Automation Workflows | ForgeVoice Studio",
        meta_description=(
            "Custom automation workflows for SaaS companies. "
            "Cut onboarding time 80%, reduce churn, eliminate manual work. "
            "Delivered in days, not months."
        ),
    ),
    "ecommerce": LandingPageSpec(
        vertical="E-commerce",
        hero_headline="Turn Browsers Into Buyers With Pages That Convert",
        hero_subheadline=(
            "AI-built product pages and automation workflows that boost "
            "your conversion rate — live in 5 days."
        ),
        hero_cta_text="Get Your Free Conversion Audit",
        hero_cta_action="book_call",
        sections=[
            LandingPageSection(
                name="pain",
                heading="Traffic Without Sales Hurts",
                subheading="You're spending on ads but the conversions aren't there",
                content_type="features",
                items=[
                    "Product pages look generic and fail to differentiate your brand",
                    "Abandoned carts bleed revenue with no recovery system",
                    "Order management is spread across platforms with no single view",
                    "You're guessing what works because there's no proper A/B testing",
                ],
            ),
            LandingPageSection(
                name="solution",
                heading="What You Get",
                subheading="Built for conversion, not just aesthetics",
                content_type="features",
                items=[
                    "High-converting product pages with proven copy frameworks",
                    "Automated abandoned cart recovery sequences",
                    "Unified order dashboard across all sales channels",
                    "A/B testing setup so you know exactly what works",
                ],
            ),
            LandingPageSection(
                name="proof",
                heading="Real Numbers",
                subheading="",
                content_type="stats",
                items=[
                    "2.5x average increase in page conversion rate",
                    "40% of abandoned carts recovered automatically",
                    "5 hours/week saved on order management",
                    "Live in 5-7 business days",
                ],
            ),
            LandingPageSection(
                name="pricing",
                heading="Investment",
                subheading="Pays for itself within the first month",
                content_type="pricing",
                items=[
                    "Launchpad: $2,997 AUD — Landing page + 1 automation",
                    "Growth: $5,997 AUD — Multi-page + 3 automations + email",
                    "Dominate: $9,997 AUD — Full site + unlimited automations",
                ],
            ),
        ],
        social_proof_type="case_studies",
        color_primary="#F59E0B",  # Amber
        color_accent="#FBBF24",
        color_bg="#111827",
        usps=[
            "Conversion-first design methodology",
            "AI-powered copy that sells",
            "Full funnel — page + email + automation",
        ],
        trust_badges=[
            "Shopify and WooCommerce experts",
            "Average 2.5x conversion lift",
            "7-day money-back guarantee",
        ],
        meta_title="E-commerce Conversion Optimization | ForgeVoice Studio",
        meta_description=(
            "AI-built product pages and automation workflows for e-commerce. "
            "Boost conversions, recover abandoned carts, unify operations."
        ),
    ),
    "local_business": LandingPageSpec(
        vertical="Local Business",
        hero_headline="Get Found Online. Get Booked. Get Paid.",
        hero_subheadline=(
            "A professional website with online booking — live in 72 hours. "
            "No tech skills needed."
        ),
        hero_cta_text="Get Your Free Website Mockup",
        hero_cta_action="book_call",
        sections=[
            LandingPageSection(
                name="pain",
                heading="Your Competitors Are Online. Are You?",
                subheading="",
                content_type="features",
                items=[
                    "Customers search Google first — and find your competitor",
                    "You're losing bookings to businesses with online scheduling",
                    "Your Facebook page isn't a real website and Google knows it",
                    "You have no idea which marketing is actually working",
                ],
            ),
            LandingPageSection(
                name="solution",
                heading="Everything You Need, Nothing You Don't",
                subheading="Simple, fast, professional",
                content_type="features",
                items=[
                    "Professional website that loads fast on any device",
                    "Online booking system — customers schedule themselves",
                    "Google-optimized so you show up in local searches",
                    "Review collection on autopilot to build trust",
                ],
            ),
            LandingPageSection(
                name="proof",
                heading="What Our Clients Say",
                subheading="",
                content_type="testimonials",
                items=[
                    "'Bookings went up 40% in the first month' — Plumber, Sydney",
                    "'Best investment I've made for my clinic' — Physio, Melbourne",
                    "'Finally I look professional online' — Electrician, Brisbane",
                ],
            ),
            LandingPageSection(
                name="pricing",
                heading="Affordable. Transparent. No Monthly Fees.",
                subheading="One-time payment, yours forever",
                content_type="pricing",
                items=[
                    "Starter: $997 AUD — Single page + contact form",
                    "Professional: $2,497 AUD — Multi-page + booking + analytics",
                    "Enterprise: $4,997 AUD — Full site + automation + ongoing support",
                ],
            ),
        ],
        social_proof_type="testimonials",
        color_primary="#10B981",  # Emerald
        color_accent="#34D399",
        color_bg="#0F172A",
        usps=[
            "Live in 72 hours, not 72 days",
            "No monthly fees or hidden costs",
            "We handle everything — zero tech needed from you",
        ],
        trust_badges=[
            "Australian-owned and operated",
            "50+ local businesses served",
            "7-day money-back guarantee",
        ],
        meta_title="Websites for Local Businesses | ForgeVoice Studio",
        meta_description=(
            "Professional websites with online booking for local businesses. "
            "Live in 72 hours. No monthly fees. Get found, get booked, get paid."
        ),
    ),
    "agency": LandingPageSpec(
        vertical="Agency",
        hero_headline="White-Label Automation Your Clients Will Love",
        hero_subheadline=(
            "Offer automation services to your clients without hiring developers. "
            "We build, you rebrand and resell."
        ),
        hero_cta_text="See the White-Label Demo",
        hero_cta_action="book_call",
        sections=[
            LandingPageSection(
                name="pain",
                heading="Scaling Hurts When Everything Is Manual",
                subheading="",
                content_type="features",
                items=[
                    "Client reporting takes a full day every single month",
                    "Onboarding new clients requires 10+ manual setup steps",
                    "You want to sell automation but don't have the dev team",
                    "Proposal creation is inconsistent and eats billable hours",
                ],
            ),
            LandingPageSection(
                name="solution",
                heading="Your Secret Weapon",
                subheading="We build it, you sell it under your brand",
                content_type="features",
                items=[
                    "White-label automation workflows ready to resell",
                    "Automated client reporting — one click, done",
                    "Templated onboarding that runs without your input",
                    "Proposal builder with your branding and pricing",
                ],
            ),
            LandingPageSection(
                name="proof",
                heading="Agency Results",
                subheading="",
                content_type="stats",
                items=[
                    "3x margin on resold automation services",
                    "20 hours/month saved on client reporting",
                    "New revenue stream launched in under 2 weeks",
                ],
            ),
            LandingPageSection(
                name="pricing",
                heading="Partnership Pricing",
                subheading="Built to give you healthy margins",
                content_type="pricing",
                items=[
                    "Single Flow: $1,497 AUD — You sell for $3-5K",
                    "Workflow Suite: $3,497 AUD — You sell for $7-10K",
                    "Full Automation: $6,997 AUD — You sell for $15-20K",
                ],
            ),
        ],
        social_proof_type="case_studies",
        color_primary="#8B5CF6",  # Violet
        color_accent="#A78BFA",
        color_bg="#1E1B4B",
        usps=[
            "White-label ready — your brand, our build",
            "3x markup potential on every project",
            "No developers needed on your side",
        ],
        trust_badges=[
            "Trusted by 10+ agencies",
            "NDA and white-label agreement included",
            "Volume discounts available",
        ],
        meta_title="White-Label Automation for Agencies | ForgeVoice Studio",
        meta_description=(
            "White-label automation workflows for digital agencies. "
            "Resell under your brand with 3x margins. No developers needed."
        ),
    ),
    "real_estate": LandingPageSpec(
        vertical="Real Estate",
        hero_headline="Never Lose a Lead to Slow Follow-Up Again",
        hero_subheadline=(
            "Automated lead capture and nurture for real estate agents — "
            "so hot leads never go cold."
        ),
        hero_cta_text="See It In Action",
        hero_cta_action="book_call",
        sections=[
            LandingPageSection(
                name="pain",
                heading="Every Hour You Wait, a Lead Goes Cold",
                subheading="",
                content_type="features",
                items=[
                    "Leads from portals sit in your inbox for hours before follow-up",
                    "Property listings managed manually across multiple platforms",
                    "Open home follow-ups fall through the cracks",
                    "Your CRM is empty because entering data takes too long",
                ],
            ),
            LandingPageSection(
                name="solution",
                heading="Your 24/7 Sales Machine",
                subheading="",
                content_type="features",
                items=[
                    "Instant lead capture from every channel — portal, web, social",
                    "Automated follow-up sequences that nurture for months",
                    "Open home registration and post-event follow-up on autopilot",
                    "CRM auto-populated — every interaction logged automatically",
                ],
            ),
            LandingPageSection(
                name="proof",
                heading="Agent Results",
                subheading="",
                content_type="stats",
                items=[
                    "60% faster lead response time",
                    "3x more leads converted to appraisals",
                    "10+ hours/week saved on admin",
                ],
            ),
            LandingPageSection(
                name="pricing",
                heading="Investment",
                subheading="",
                content_type="pricing",
                items=[
                    "Launchpad: $2,997 AUD — Lead capture page + follow-up",
                    "Growth: $5,997 AUD — Full site + nurture + CRM",
                    "Dominate: $9,997 AUD — Everything + AI lead scoring",
                ],
            ),
        ],
        social_proof_type="testimonials",
        color_primary="#0EA5E9",  # Sky blue
        color_accent="#38BDF8",
        color_bg="#0C1222",
        usps=[
            "Respond to leads in under 60 seconds, automatically",
            "Built for Australian real estate workflows",
            "Integrates with REA, Domain, and major CRMs",
        ],
        trust_badges=[
            "Built for Australian real estate",
            "REA and Domain compatible",
            "7-day money-back guarantee",
        ],
        meta_title="Real Estate Lead Automation | ForgeVoice Studio",
        meta_description=(
            "Automated lead capture and nurture for real estate agents. "
            "Respond in seconds, nurture for months, close more deals."
        ),
    ),
    "health_wellness": LandingPageSpec(
        vertical="Health & Wellness",
        hero_headline="Fill Your Appointment Book on Autopilot",
        hero_subheadline=(
            "Online booking, automated reminders, and review collection — "
            "so you can focus on patients, not admin."
        ),
        hero_cta_text="Book a Free Demo",
        hero_cta_action="book_call",
        sections=[
            LandingPageSection(
                name="pain",
                heading="Admin Shouldn't Take Half Your Day",
                subheading="",
                content_type="features",
                items=[
                    "Phone scheduling wastes hours of staff time every day",
                    "No-shows cost you thousands with no automated reminders",
                    "Patient intake is still paper forms and manual data entry",
                    "Happy patients never leave reviews because nobody asks",
                ],
            ),
            LandingPageSection(
                name="solution",
                heading="Modern Practice, Happy Patients",
                subheading="",
                content_type="features",
                items=[
                    "24/7 online booking — patients schedule at their convenience",
                    "SMS and email reminders that slash no-show rates by 50%",
                    "Digital intake forms that flow straight into your system",
                    "Automated review requests sent after every visit",
                ],
            ),
            LandingPageSection(
                name="proof",
                heading="Practice Results",
                subheading="",
                content_type="stats",
                items=[
                    "50% reduction in no-shows",
                    "3 hours/day saved on phone scheduling",
                    "4.8 average Google rating with automated reviews",
                ],
            ),
            LandingPageSection(
                name="pricing",
                heading="Simple Pricing",
                subheading="",
                content_type="pricing",
                items=[
                    "Starter: $997 AUD — Website + contact form",
                    "Professional: $2,497 AUD — Website + booking + reminders",
                    "Enterprise: $4,997 AUD — Full system + automations + support",
                ],
            ),
        ],
        social_proof_type="testimonials",
        color_primary="#14B8A6",  # Teal
        color_accent="#2DD4BF",
        color_bg="#0F172A",
        usps=[
            "Patients book when it suits them, 24/7",
            "No-shows drop by 50% with automated reminders",
            "Google reviews grow on autopilot",
        ],
        trust_badges=[
            "HIPAA-conscious design principles",
            "Trusted by 20+ clinics",
            "7-day money-back guarantee",
        ],
        meta_title="Websites & Booking for Clinics | ForgeVoice Studio",
        meta_description=(
            "Online booking, automated reminders, and review collection "
            "for health and wellness practices. Less admin, more patients."
        ),
    ),
    "professional_services": LandingPageSpec(
        vertical="Professional Services",
        hero_headline="Win Clients Online, Not Just From Referrals",
        hero_subheadline=(
            "A professional website with scheduling and lead capture — "
            "so new clients find you, not just old contacts."
        ),
        hero_cta_text="Get Your Free Site Mockup",
        hero_cta_action="book_call",
        sections=[
            LandingPageSection(
                name="pain",
                heading="Referrals Are Great. But They're Not Enough.",
                subheading="",
                content_type="features",
                items=[
                    "Potential clients Google you and find nothing credible",
                    "Scheduling a meeting takes 5+ emails back and forth",
                    "You look the same as every other consultant online",
                    "No system to capture and follow up with website visitors",
                ],
            ),
            LandingPageSection(
                name="solution",
                heading="Your Digital Handshake",
                subheading="",
                content_type="features",
                items=[
                    "Professional site that builds trust in 5 seconds",
                    "One-click scheduling — no more email tennis",
                    "Lead capture that automatically follows up",
                    "SEO that puts you in front of people searching for help",
                ],
            ),
            LandingPageSection(
                name="proof",
                heading="Client Results",
                subheading="",
                content_type="testimonials",
                items=[
                    "'Went from 0 to 5 inbound leads per month' — Consultant",
                    "'Scheduling time dropped from 30 min to 30 seconds' — Accountant",
                    "'Best ROI on any business expense this year' — Lawyer",
                ],
            ),
            LandingPageSection(
                name="pricing",
                heading="Pricing",
                subheading="",
                content_type="pricing",
                items=[
                    "Starter: $997 AUD — Single page + scheduling",
                    "Professional: $2,497 AUD — Multi-page + CRM + email",
                    "Enterprise: $4,997 AUD — Full site + automation + support",
                ],
            ),
        ],
        social_proof_type="testimonials",
        color_primary="#3B82F6",  # Blue
        color_accent="#60A5FA",
        color_bg="#0F172A",
        usps=[
            "Look credible online in 72 hours",
            "One-click scheduling kills email back-and-forth",
            "Inbound leads on autopilot",
        ],
        trust_badges=[
            "Trusted by accountants, lawyers, and consultants",
            "Australian-owned business",
            "7-day money-back guarantee",
        ],
        meta_title="Websites for Consultants & Professionals | ForgeVoice Studio",
        meta_description=(
            "Professional websites with scheduling and lead capture for "
            "consultants, accountants, and lawyers. Live in 72 hours."
        ),
    ),
    "education": LandingPageSpec(
        vertical="Education",
        hero_headline="Sell More Courses With Pages That Convert",
        hero_subheadline=(
            "AI-built course sales pages and student engagement automation — "
            "so you teach, and the tech handles the rest."
        ),
        hero_cta_text="See a Sample Course Page",
        hero_cta_action="book_call",
        sections=[
            LandingPageSection(
                name="pain",
                heading="Great Content, Poor Sales Page",
                subheading="",
                content_type="features",
                items=[
                    "Your course is excellent but the sales page doesn't show it",
                    "Student onboarding is a mess of manual emails and spreadsheets",
                    "Completion rates are low because there's no engagement system",
                    "Certificate generation is a painful manual process",
                ],
            ),
            LandingPageSection(
                name="solution",
                heading="From Enrol to Complete, Automated",
                subheading="",
                content_type="features",
                items=[
                    "High-converting course sales page with proven frameworks",
                    "Automated student onboarding and drip content delivery",
                    "Engagement nudges that boost completion rates",
                    "Automatic certificate generation on course completion",
                ],
            ),
            LandingPageSection(
                name="proof",
                heading="Educator Results",
                subheading="",
                content_type="stats",
                items=[
                    "3x increase in course enrolments",
                    "65% course completion rate (industry avg: 15%)",
                    "Zero manual work on student onboarding",
                ],
            ),
            LandingPageSection(
                name="pricing",
                heading="Investment",
                subheading="",
                content_type="pricing",
                items=[
                    "Launchpad: $2,997 AUD — Sales page + onboarding",
                    "Growth: $5,997 AUD — Multi-page + engagement + email",
                    "Dominate: $9,997 AUD — Full platform + AI + certificates",
                ],
            ),
        ],
        social_proof_type="stats",
        color_primary="#EC4899",  # Pink
        color_accent="#F472B6",
        color_bg="#1A1025",
        usps=[
            "Sales pages built with proven conversion frameworks",
            "Student engagement on autopilot",
            "From enrol to certificate, fully automated",
        ],
        trust_badges=[
            "Trusted by course creators worldwide",
            "Average 3x enrolment increase",
            "7-day money-back guarantee",
        ],
        meta_title="Course Sales Pages & Automation | ForgeVoice Studio",
        meta_description=(
            "AI-built course sales pages and student engagement automation. "
            "Sell more courses, boost completion rates, automate onboarding."
        ),
    ),
}


# =============================================
# Helper Functions
# =============================================


def get_landing_page_spec(vertical: str) -> Optional[LandingPageSpec]:
    """
    Get the landing page specification for a vertical.

    Args:
        vertical: Vertical key (saas, ecommerce, local_business, etc.)
                  Also accepts display names.

    Returns:
        LandingPageSpec or None.
    """
    key = vertical.lower().replace(" ", "_").replace("&", "").replace("/", "_")
    if key in LANDING_PAGE_SPECS:
        return LANDING_PAGE_SPECS[key]

    # Fuzzy match on display name
    for spec_key, spec in LANDING_PAGE_SPECS.items():
        if vertical.lower() in spec.vertical.lower():
            return spec

    return None


def list_available_specs() -> List[str]:
    """Return all available vertical spec keys."""
    return list(LANDING_PAGE_SPECS.keys())


def get_forge_prompt_context(vertical: str) -> Optional[str]:
    """
    Generate a context block that FORGE can inject into its
    Sonnet prompt for vertical-specific page generation.

    Args:
        vertical: Vertical key

    Returns:
        Formatted string for inclusion in FORGE prompt, or None.
    """
    spec = get_landing_page_spec(vertical)
    if spec is None:
        return None

    sections_text = ""
    for section in spec.sections:
        items_formatted = "\n".join(f"  - {item}" for item in section.items)
        sections_text += (
            f"\n[{section.name.upper()}]\n"
            f"Heading: {section.heading}\n"
            f"Sub: {section.subheading}\n"
            f"Type: {section.content_type}\n"
            f"{items_formatted}\n"
        )

    return (
        f"VERTICAL-SPECIFIC DESIGN BRIEF:\n"
        f"Vertical: {spec.vertical}\n"
        f"Hero Headline: {spec.hero_headline}\n"
        f"Hero Sub: {spec.hero_subheadline}\n"
        f"CTA: {spec.hero_cta_text}\n"
        f"Color Primary: {spec.color_primary}\n"
        f"Color Accent: {spec.color_accent}\n"
        f"Background: {spec.color_bg}\n"
        f"Social Proof: {spec.social_proof_type}\n"
        f"USPs: {', '.join(spec.usps)}\n"
        f"Trust: {', '.join(spec.trust_badges)}\n"
        f"Meta Title: {spec.meta_title}\n"
        f"Meta Desc: {spec.meta_description}\n"
        f"\nSECTIONS:{sections_text}"
    )
