"""
Client Onboarding Flow for ForgeVoice Studio
Defines the onboarding state machine from deal-close to delivery.
Each step has a trigger, email template, and timing.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class OnboardingStatus(str, Enum):
    """Possible statuses for an onboarding step."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    WAITING_CLIENT = "waiting_client"
    COMPLETED = "completed"
    SKIPPED = "skipped"


@dataclass
class OnboardingStep:
    """Single step in the client onboarding flow."""

    step: int
    name: str
    display_name: str
    trigger: str
    email_template: str
    delay_hours: int
    owner: str  # "us" or "client"
    description: str
    required: bool = True
    auto_send: bool = True


# =============================================
# Onboarding Flow Definition
# =============================================

ONBOARDING_STEPS: List[OnboardingStep] = [
    OnboardingStep(
        step=1,
        name="welcome_email",
        display_name="Welcome Email",
        trigger="deal_closed",
        email_template="onboarding_welcome",
        delay_hours=0,
        owner="us",
        description=(
            "Send welcome email with onboarding overview, timeline, "
            "and link to intake form. Set expectations."
        ),
    ),
    OnboardingStep(
        step=2,
        name="intake_form",
        display_name="Client Intake Form",
        trigger="welcome_sent",
        email_template="intake_questionnaire",
        delay_hours=24,
        owner="client",
        description=(
            "Client fills out intake questionnaire: brand assets, "
            "target audience, competitors, goals, existing tools."
        ),
    ),
    OnboardingStep(
        step=3,
        name="kickoff_call",
        display_name="Kickoff Call",
        trigger="intake_received",
        email_template="kickoff_scheduling",
        delay_hours=0,
        owner="us",
        description=(
            "30-minute call to review intake, clarify requirements, "
            "align on timeline. Send Calendly link."
        ),
    ),
    OnboardingStep(
        step=4,
        name="requirements_doc",
        display_name="Requirements Summary",
        trigger="kickoff_complete",
        email_template="requirements_summary",
        delay_hours=24,
        owner="us",
        description=(
            "Summarise agreed requirements, deliverables, timeline, "
            "and acceptance criteria. Client signs off."
        ),
    ),
    OnboardingStep(
        step=5,
        name="build_start",
        display_name="Build Started",
        trigger="requirements_approved",
        email_template="build_started_notification",
        delay_hours=0,
        owner="us",
        description=(
            "Notify client that build has begun. "
            "Share estimated first-draft date."
        ),
    ),
    OnboardingStep(
        step=6,
        name="first_draft",
        display_name="First Draft Preview",
        trigger="build_50_percent",
        email_template="preview_ready",
        delay_hours=0,
        owner="us",
        description=(
            "Share preview link for first draft. "
            "Request client feedback within 48 hours."
        ),
    ),
    OnboardingStep(
        step=7,
        name="revision",
        display_name="Revision Round",
        trigger="feedback_received",
        email_template="revision_confirmation",
        delay_hours=0,
        owner="us",
        description=(
            "Apply client feedback. Send updated preview. "
            "Repeat if more revision rounds remain."
        ),
    ),
    OnboardingStep(
        step=8,
        name="delivery",
        display_name="Final Delivery",
        trigger="approved",
        email_template="delivery_handoff",
        delay_hours=0,
        owner="us",
        description=(
            "Deliver final assets: live URL, source files, credentials, "
            "documentation, and handover guide."
        ),
    ),
    OnboardingStep(
        step=9,
        name="invoice_final",
        display_name="Final Invoice & Feedback",
        trigger="delivered",
        email_template="invoice_and_feedback",
        delay_hours=24,
        owner="us",
        description=(
            "Send final invoice (remaining 50%). "
            "Request Google review and testimonial."
        ),
    ),
    OnboardingStep(
        step=10,
        name="checkin_7day",
        display_name="7-Day Check-in",
        trigger="delivered",
        email_template="checkin_7day",
        delay_hours=168,  # 7 days
        owner="us",
        description=(
            "Check how things are going. Offer to fix any small issues. "
            "Plant seed for upsell or referral."
        ),
        required=False,
    ),
]


# =============================================
# Helper Functions
# =============================================


def get_onboarding_steps(
    include_optional: bool = True,
) -> List[OnboardingStep]:
    """
    Get the full onboarding flow.

    Args:
        include_optional: Whether to include non-required steps.

    Returns:
        Ordered list of OnboardingStep.
    """
    if include_optional:
        return ONBOARDING_STEPS.copy()
    return [s for s in ONBOARDING_STEPS if s.required]


def get_step_by_name(name: str) -> Optional[OnboardingStep]:
    """Look up a step by its name key."""
    for step in ONBOARDING_STEPS:
        if step.name == name:
            return step
    return None


def get_next_step(current_step_name: str) -> Optional[OnboardingStep]:
    """Get the next step after the given one."""
    for i, step in enumerate(ONBOARDING_STEPS):
        if step.name == current_step_name:
            if i + 1 < len(ONBOARDING_STEPS):
                return ONBOARDING_STEPS[i + 1]
            return None
    return None


def get_step_by_trigger(trigger: str) -> List[OnboardingStep]:
    """Get all steps triggered by a given event."""
    return [s for s in ONBOARDING_STEPS if s.trigger == trigger]


def calculate_total_timeline_hours() -> int:
    """Calculate minimum total hours from deal close to delivery."""
    return sum(s.delay_hours for s in ONBOARDING_STEPS if s.required)


def format_onboarding_timeline() -> str:
    """Generate a human-readable onboarding timeline."""
    lines = ["=== Client Onboarding Timeline ===", ""]
    cumulative_hours = 0

    for step in ONBOARDING_STEPS:
        cumulative_hours += step.delay_hours
        days = cumulative_hours / 24
        marker = "*" if step.required else " "
        lines.append(
            f"  {marker} Step {step.step}: {step.display_name} "
            f"(~Day {days:.0f}, {step.owner})"
        )
        lines.append(f"    {step.description}")
        lines.append("")

    lines.append("* = required step")
    return "\n".join(lines)
