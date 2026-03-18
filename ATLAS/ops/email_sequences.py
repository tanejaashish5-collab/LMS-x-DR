"""
Email Sequence Engine for ForgeVoice Studio
Defines structured outreach, nurture, and post-sale email sequences.
Each email has a delay, subject template, body template, and trigger.

Templates use {variable} placeholders for personalisation.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class EmailStep:
    """Single email in a sequence."""

    step: int
    name: str
    delay_hours: int
    subject: str
    body: str
    trigger: str
    from_email_type: str = "sales"  # maps to brand.get_email_from()
    reply_to: str = ""  # empty = same as from


@dataclass
class EmailSequence:
    """Complete email sequence with metadata."""

    sequence_id: str
    name: str
    description: str
    target: str  # who this sequence is for
    emails: List[EmailStep]


# =============================================
# Cold Outreach Sequence (Scout-discovered)
# =============================================

COLD_OUTREACH = EmailSequence(
    sequence_id="cold_outreach",
    name="Cold Outreach",
    description="4-touch sequence for Scout-discovered opportunities",
    target="Business owners discovered via Reddit/web scanning",
    emails=[
        EmailStep(
            step=1,
            name="intro",
            delay_hours=0,
            trigger="opportunity_qualified",
            subject="Quick question about {pain_point_short}",
            from_email_type="founder",
            body=(
                "Hi {first_name},\n\n"
                "I came across your post about {pain_point_context} and it "
                "resonated — I've helped several {vertical} businesses solve "
                "exactly this.\n\n"
                "We recently helped a {similar_business} cut their "
                "{pain_metric} by {result_percentage}% in under 2 weeks.\n\n"
                "Would a quick 15-minute chat be useful? No pitch, just "
                "curious if what worked for them could apply to you.\n\n"
                "Cheers,\n"
                "{sender_name}\n"
                "ForgeVoice Studio\n"
                "{calendly_link}"
            ),
        ),
        EmailStep(
            step=2,
            name="value_add",
            delay_hours=72,  # Day 3
            trigger="no_reply_step_1",
            subject="Re: {pain_point_short} — thought this might help",
            from_email_type="founder",
            body=(
                "Hi {first_name},\n\n"
                "Following up on my earlier note. I put together a short "
                "breakdown of how {vertical} businesses are automating "
                "{pain_point_short}.\n\n"
                "Here are 3 patterns that save the most time:\n\n"
                "1. {insight_1}\n"
                "2. {insight_2}\n"
                "3. {insight_3}\n\n"
                "Happy to walk you through how any of these would work for "
                "{company_name}. No commitment needed.\n\n"
                "Best,\n"
                "{sender_name}"
            ),
        ),
        EmailStep(
            step=3,
            name="solution_preview",
            delay_hours=168,  # Day 7
            trigger="no_reply_step_2",
            subject="Built something for {vertical} businesses like yours",
            from_email_type="sales",
            body=(
                "Hi {first_name},\n\n"
                "I built a sample landing page for {vertical} businesses "
                "that shows what a modern online presence looks like:\n\n"
                "{sample_page_url}\n\n"
                "This is the kind of thing we deliver in 3-5 days. "
                "Pricing starts at ${basic_price} AUD.\n\n"
                "Worth a quick look? If it sparks any ideas, I'm happy to "
                "chat about what would work specifically for you.\n\n"
                "{sender_name}\n"
                "ForgeVoice Studio"
            ),
        ),
        EmailStep(
            step=4,
            name="final_nudge",
            delay_hours=336,  # Day 14
            trigger="no_reply_step_3",
            subject="Last note from me, {first_name}",
            from_email_type="founder",
            body=(
                "Hi {first_name},\n\n"
                "Last email from me on this — no hard feelings either way.\n\n"
                "If {pain_point_short} is still a headache, we're running a "
                "limited offer this month: {offer_description}.\n\n"
                "3 businesses in {vertical} have already taken us up on it.\n\n"
                "If the timing isn't right, no worries at all. I'll be here "
                "when it is.\n\n"
                "All the best,\n"
                "{sender_name}"
            ),
        ),
    ],
)


# =============================================
# Warm Lead Sequence (responded to outreach)
# =============================================

WARM_LEAD = EmailSequence(
    sequence_id="warm_lead",
    name="Warm Lead Nurture",
    description="4-touch sequence for leads who responded positively",
    target="Prospects who replied to cold outreach or booked a call",
    emails=[
        EmailStep(
            step=1,
            name="thank_you",
            delay_hours=0,
            trigger="lead_responded",
            subject="Great chatting, {first_name} — next steps",
            from_email_type="founder",
            body=(
                "Hi {first_name},\n\n"
                "Thanks for taking the time to chat. Here's a quick "
                "summary of what we discussed:\n\n"
                "- Problem: {pain_point_summary}\n"
                "- Solution: {proposed_solution}\n"
                "- Timeline: {timeline}\n"
                "- Investment: {price_range}\n\n"
                "I'll have a detailed proposal over to you by "
                "{proposal_date}.\n\n"
                "In the meantime, feel free to reply with any questions.\n\n"
                "Cheers,\n"
                "{sender_name}"
            ),
        ),
        EmailStep(
            step=2,
            name="proposal",
            delay_hours=24,  # Day 1
            trigger="thank_you_sent",
            subject="Your proposal from ForgeVoice Studio",
            from_email_type="sales",
            body=(
                "Hi {first_name},\n\n"
                "As promised, here's your proposal:\n\n"
                "{proposal_link}\n\n"
                "Key highlights:\n"
                "- {highlight_1}\n"
                "- {highlight_2}\n"
                "- {highlight_3}\n\n"
                "To get started, just reply 'go' and I'll send the "
                "invoice for the first 50%.\n\n"
                "Happy to jump on a quick call if you want to talk "
                "through anything.\n\n"
                "{sender_name}\n"
                "ForgeVoice Studio"
            ),
        ),
        EmailStep(
            step=3,
            name="roi_breakdown",
            delay_hours=72,  # Day 3
            trigger="no_reply_proposal",
            subject="The numbers behind your {vertical} automation",
            from_email_type="founder",
            body=(
                "Hi {first_name},\n\n"
                "Wanted to share a quick ROI snapshot for what we "
                "discussed:\n\n"
                "Current cost of {pain_point_short}:\n"
                "  {hours_per_week} hours/week x ${hourly_rate}/hr = "
                "${weekly_cost}/week\n\n"
                "Annual cost: ${annual_cost}\n"
                "Our solution: ${solution_price} (one-time)\n"
                "Payback period: {payback_weeks} weeks\n\n"
                "After that, it's pure time and money back in your "
                "pocket.\n\n"
                "Shall I lock in your spot this week?\n\n"
                "{sender_name}"
            ),
        ),
        EmailStep(
            step=4,
            name="decision_support",
            delay_hours=168,  # Day 7
            trigger="no_reply_roi",
            subject="Any questions on the proposal, {first_name}?",
            from_email_type="founder",
            body=(
                "Hi {first_name},\n\n"
                "Just checking in — any questions about the proposal?\n\n"
                "Common things clients ask at this stage:\n"
                "- 'What if I don't like it?' — Full refund within 7 days "
                "if we haven't started building.\n"
                "- 'How long does it really take?' — {delivery_days} "
                "business days for your scope.\n"
                "- 'What do I need to provide?' — Just 30 minutes of your "
                "time for the kickoff call.\n\n"
                "If now isn't the right time, totally understand. "
                "The proposal stays valid for 30 days.\n\n"
                "Cheers,\n"
                "{sender_name}"
            ),
        ),
    ],
)


# =============================================
# Post-Sale Sequence
# =============================================

POST_SALE = EmailSequence(
    sequence_id="post_sale",
    name="Post-Sale Nurture",
    description="Ongoing relationship building after delivery",
    target="Clients who have received their deliverables",
    emails=[
        EmailStep(
            step=1,
            name="welcome_onboarding",
            delay_hours=0,
            trigger="deal_closed",
            subject="Welcome to ForgeVoice Studio, {first_name}!",
            from_email_type="founder",
            body=(
                "Hi {first_name},\n\n"
                "Welcome aboard! We're excited to build {project_name} "
                "for you.\n\n"
                "Here's what happens next:\n"
                "1. You'll receive an intake form within 24 hours\n"
                "2. We'll schedule a 30-min kickoff call\n"
                "3. Build starts immediately after kickoff\n"
                "4. First draft in {first_draft_days} days\n\n"
                "Your dedicated point of contact is me — reply to this "
                "email anytime.\n\n"
                "Let's build something great.\n\n"
                "Ashish Taneja\n"
                "Founder, ForgeVoice Studio"
            ),
        ),
        EmailStep(
            step=2,
            name="checkin_7day",
            delay_hours=168,  # Day 7
            trigger="delivered",
            subject="How's everything going with {project_name}?",
            from_email_type="founder",
            body=(
                "Hi {first_name},\n\n"
                "It's been a week since we delivered {project_name}. "
                "How's everything working?\n\n"
                "A few things to check:\n"
                "- Is the site loading fast on mobile?\n"
                "- Are you receiving form submissions?\n"
                "- Any small tweaks needed?\n\n"
                "We're still within your {support_days}-day support "
                "window, so don't hesitate to reach out.\n\n"
                "{sender_name}"
            ),
        ),
        EmailStep(
            step=3,
            name="satisfaction_survey",
            delay_hours=720,  # Day 30
            trigger="delivered",
            subject="Quick favour, {first_name}? (30 seconds)",
            from_email_type="primary",
            body=(
                "Hi {first_name},\n\n"
                "Hope {project_name} is serving you well!\n\n"
                "Would you mind leaving a quick Google review? "
                "It takes 30 seconds and helps us reach more businesses "
                "like yours.\n\n"
                "{review_link}\n\n"
                "If you'd also be open to a short testimonial I can "
                "feature on our site, just reply and I'll send a few "
                "easy questions.\n\n"
                "Thanks for being a great client.\n\n"
                "{sender_name}"
            ),
        ),
        EmailStep(
            step=4,
            name="upsell_referral",
            delay_hours=1440,  # Day 60
            trigger="delivered",
            subject="{first_name}, ready for the next level?",
            from_email_type="sales",
            body=(
                "Hi {first_name},\n\n"
                "It's been 2 months since we launched {project_name}. "
                "I hope the results are coming through.\n\n"
                "Two things I wanted to share:\n\n"
                "1. **Upgrade offer**: We now have {upsell_service} "
                "starting at ${upsell_price} AUD that pairs perfectly "
                "with what you already have.\n\n"
                "2. **Referral bonus**: Know someone who needs what you "
                "got? Refer them and you'll both get $200 off your next "
                "project.\n\n"
                "Either way, it was great working with you.\n\n"
                "{sender_name}\n"
                "ForgeVoice Studio"
            ),
        ),
    ],
)


# =============================================
# All Sequences Indexed
# =============================================

ALL_SEQUENCES: Dict[str, EmailSequence] = {
    "cold_outreach": COLD_OUTREACH,
    "warm_lead": WARM_LEAD,
    "post_sale": POST_SALE,
}


# =============================================
# Helper Functions
# =============================================


def get_sequence(sequence_id: str) -> Optional[EmailSequence]:
    """
    Get an email sequence by ID.

    Args:
        sequence_id: One of cold_outreach, warm_lead, post_sale

    Returns:
        EmailSequence or None.
    """
    return ALL_SEQUENCES.get(sequence_id)


def get_sequence_for_stage(pipeline_stage: str) -> Optional[EmailSequence]:
    """
    Map a pipeline stage to the appropriate email sequence.

    Args:
        pipeline_stage: E.g., 'qualified', 'responded', 'closed'

    Returns:
        Appropriate EmailSequence or None.
    """
    stage_map: Dict[str, str] = {
        "qualified": "cold_outreach",
        "discovered": "cold_outreach",
        "outreach": "cold_outreach",
        "responded": "warm_lead",
        "proposal_sent": "warm_lead",
        "negotiation": "warm_lead",
        "closed": "post_sale",
        "delivered": "post_sale",
        "active_client": "post_sale",
    }
    seq_id = stage_map.get(pipeline_stage.lower())
    if seq_id:
        return ALL_SEQUENCES.get(seq_id)
    return None


def list_sequences() -> List[str]:
    """Return all sequence IDs."""
    return list(ALL_SEQUENCES.keys())


def get_email_at_step(
    sequence_id: str,
    step: int,
) -> Optional[EmailStep]:
    """
    Get a specific email from a sequence by step number.

    Args:
        sequence_id: Sequence key
        step: Step number (1-indexed)

    Returns:
        EmailStep or None.
    """
    seq = ALL_SEQUENCES.get(sequence_id)
    if seq is None:
        return None
    for email in seq.emails:
        if email.step == step:
            return email
    return None
