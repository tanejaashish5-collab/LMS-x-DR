"""
Agency Proposal Template - For marketing agencies, consulting firms, and service businesses.
"""

AGENCY_PROPOSAL = {
    "vertical": "agency",
    "template": {
        "executive_summary": (
            "{company_name} is handling {pain_point} manually, which eats into "
            "billable hours and limits how many clients you can serve. We automate "
            "the operational overhead so your team delivers more client value with "
            "less grunt work."
        ),
        "problem_statement": (
            "Agencies like {company_name} typically struggle with:\n"
            "- {hours_lost} hours/week on {process_name} across clients\n"
            "- Client reporting consuming senior staff time\n"
            "- Onboarding bottlenecks slowing new client ramp-up\n"
            "- Inconsistent delivery when processes are manual\n"
            "- Margin compression as team grows but ops stay manual"
        ),
        "proposed_solution": (
            "We build automated workflows that handle your operational backend "
            "({tools_used}), freeing your team to focus on strategy and client "
            "relationships.\n\n"
            "Key components:\n"
            "- Client onboarding automation (forms, access, kickoff)\n"
            "- Automated reporting from data sources to client dashboards\n"
            "- Task creation and assignment workflows\n"
            "- Time tracking and invoicing automation\n"
            "- Client communication sequences"
        ),
        "pricing": {
            "basic": {
                "price": 997,
                "name": "Agency Starter",
                "features": [
                    "Single workflow (reporting OR onboarding)",
                    "Up to 2 tool integrations",
                    "Template for 1 client type",
                    "Email support",
                    "30-day warranty",
                ],
            },
            "pro": {
                "price": 2497,
                "name": "Agency Growth",
                "features": [
                    "Up to 3 workflows",
                    "Up to 5 tool integrations",
                    "Multi-client templating",
                    "Automated client reporting",
                    "Priority support",
                    "90-day warranty",
                ],
            },
            "enterprise": {
                "price": 4997,
                "name": "Agency Scale",
                "features": [
                    "Unlimited workflows",
                    "White-label client portal",
                    "Custom integrations",
                    "SOPs documented and automated",
                    "Dedicated support",
                    "Quarterly reviews",
                    "12-month warranty",
                ],
            },
        },
        "timeline": (
            "- Week 1: Map current processes and identify quick wins\n"
            "- Week 2: Build core automations\n"
            "- Week 3: Test with one live client\n"
            "- Week 4: Roll out to remaining clients"
        ),
        "roi_projection": (
            "Based on {hours_lost} hours/week at ${hourly_rate}/hour billable rate:\n"
            "- Recovered billable hours: {hours_lost}h/week\n"
            "- Monthly revenue recovery: ${monthly_savings}\n"
            "- Annual impact: ${annual_savings}\n"
            "- Payback period: {payback_weeks} weeks"
        ),
        "next_steps": (
            "1. Reply or book a call: https://calendly.com/ashishtaneja\n"
            "2. Free 30-minute process audit\n"
            "3. Select your tier\n"
            "4. First automation live within {delivery_weeks} weeks"
        ),
    },
}
