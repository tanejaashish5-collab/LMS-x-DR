"""
Generic Proposal Template - Fallback for verticals without a dedicated template.
"""

GENERIC_PROPOSAL = {
    "vertical": "generic",
    "template": {
        "executive_summary": (
            "{company_name} is losing productive hours to {pain_point}. We build "
            "custom automation solutions that eliminate manual work, reduce errors, "
            "and let your team focus on high-value activities."
        ),
        "problem_statement": (
            "Based on our analysis of your situation:\n"
            "- {hours_lost} hours/week spent on {process_name}\n"
            "- Manual processes creating bottlenecks and errors\n"
            "- Staff time consumed by repetitive tasks\n"
            "- Growth limited by operational capacity\n"
            "- Inconsistent quality when things are done by hand"
        ),
        "proposed_solution": (
            "We design and build an automated workflow that connects your existing "
            "tools ({tools_used}) and removes the manual steps.\n\n"
            "Key components:\n"
            "- Process mapping and optimization\n"
            "- Tool integrations and data flow automation\n"
            "- Error handling and exception management\n"
            "- Monitoring and alerting\n"
            "- Documentation and training"
        ),
        "pricing": {
            "basic": {
                "price": 997,
                "name": "Essentials",
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
                "name": "Professional",
                "features": [
                    "Up to 3 workflows",
                    "Up to 5 tool integrations",
                    "Advanced error handling",
                    "Monitoring dashboard",
                    "Priority support",
                    "90-day warranty",
                ],
            },
            "enterprise": {
                "price": 4997,
                "name": "Enterprise",
                "features": [
                    "Unlimited workflows",
                    "Unlimited integrations",
                    "Custom development",
                    "Dedicated support",
                    "SLA guarantee",
                    "Quarterly reviews",
                    "12-month warranty",
                ],
            },
        },
        "timeline": (
            "- Week 1: Discovery and process mapping\n"
            "- Week 2: Build and configure\n"
            "- Week 3: Test and iterate\n"
            "- Week 4: Deploy and monitor"
        ),
        "roi_projection": (
            "Based on {hours_lost} hours/week at ${hourly_rate}/hour:\n"
            "- Monthly savings: ${monthly_savings}\n"
            "- Annual savings: ${annual_savings}\n"
            "- Payback period: {payback_weeks} weeks\n"
            "- 12-month ROI: {roi_percent}%"
        ),
        "next_steps": (
            "1. Reply or book a call: https://calendly.com/ashishtaneja\n"
            "2. Free 30-minute discovery call\n"
            "3. Pick your tier\n"
            "4. Live within {delivery_weeks} weeks"
        ),
    },
}
