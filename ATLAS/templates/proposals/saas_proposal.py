"""
SaaS Proposal Template - For SaaS companies and software businesses.
"""

SAAS_PROPOSAL = {
    "vertical": "saas",
    "template": {
        "executive_summary": (
            "Your team at {company_name} is losing valuable engineering and operations "
            "hours to {pain_point}. We propose an automation solution that eliminates "
            "this bottleneck, letting your team focus on product development and customer "
            "growth instead of manual processes."
        ),
        "problem_statement": (
            "Based on our analysis, {company_name} currently faces:\n"
            "- {hours_lost} hours/week spent on {process_name}\n"
            "- Increased error rates from manual handling\n"
            "- Slower customer onboarding and response times\n"
            "- Engineering talent diverted from core product work\n"
            "- Scaling limitations as customer volume grows"
        ),
        "proposed_solution": (
            "We build a fully automated workflow that connects your existing tools "
            "({tools_used}) and eliminates manual steps entirely. The system runs "
            "24/7, handles edge cases, and alerts your team only when human judgment "
            "is genuinely needed.\n\n"
            "Key components:\n"
            "- API integrations with your current stack\n"
            "- Automated data transformation and routing\n"
            "- Error handling with smart retry logic\n"
            "- Real-time monitoring dashboard\n"
            "- Slack/email alerts for exceptions"
        ),
        "pricing": {
            "basic": {
                "price": 997,
                "name": "Starter Automation",
                "features": [
                    "Single workflow automation",
                    "Up to 2 tool integrations",
                    "Basic error handling",
                    "Email support",
                    "30-day warranty",
                ],
            },
            "pro": {
                "price": 2497,
                "name": "Growth Automation",
                "features": [
                    "Up to 3 connected workflows",
                    "Up to 5 tool integrations",
                    "Advanced error handling and retries",
                    "Monitoring dashboard",
                    "Slack/email alerts",
                    "Priority support",
                    "90-day warranty",
                ],
            },
            "enterprise": {
                "price": 4997,
                "name": "Scale Automation",
                "features": [
                    "Unlimited workflows",
                    "Unlimited integrations",
                    "Custom API development",
                    "Dedicated monitoring dashboard",
                    "SLA with 4-hour response time",
                    "Quarterly optimization reviews",
                    "12-month warranty",
                ],
            },
        },
        "timeline": (
            "- Week 1: Discovery and technical audit\n"
            "- Week 2: Build and internal testing\n"
            "- Week 3: Deployment and parallel run\n"
            "- Week 4: Handoff and monitoring setup"
        ),
        "roi_projection": (
            "Based on {hours_lost} hours/week at an estimated ${hourly_rate}/hour:\n"
            "- Monthly savings: ${monthly_savings}\n"
            "- Annual savings: ${annual_savings}\n"
            "- Payback period: {payback_weeks} weeks\n"
            "- 12-month ROI: {roi_percent}%"
        ),
        "next_steps": (
            "1. Reply to this email or book a call: https://calendly.com/ashishtaneja\n"
            "2. We run a 30-minute technical audit (free)\n"
            "3. You pick the tier that fits\n"
            "4. We build and deploy within {delivery_weeks} weeks"
        ),
    },
}
