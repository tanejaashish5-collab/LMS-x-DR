"""
Local Business Proposal Template - For local service businesses, healthcare, legal, real estate.
"""

LOCAL_BUSINESS_PROPOSAL = {
    "vertical": "local_business",
    "template": {
        "executive_summary": (
            "{company_name} is spending staff time on {pain_point} that could be "
            "handled automatically. We set up simple, reliable automations that "
            "run in the background so your team can focus on serving customers "
            "and growing the business."
        ),
        "problem_statement": (
            "Local businesses like {company_name} commonly deal with:\n"
            "- {hours_lost} hours/week on {process_name}\n"
            "- Missed follow-ups with leads and customers\n"
            "- Manual appointment scheduling and reminders\n"
            "- Slow response times hurting online reviews\n"
            "- Admin tasks pulling staff away from revenue work"
        ),
        "proposed_solution": (
            "We connect your existing tools ({tools_used}) into automated workflows "
            "that handle the admin while you handle the customers.\n\n"
            "Key components:\n"
            "- Automated appointment booking and reminders\n"
            "- Lead capture and instant follow-up\n"
            "- Review request automation (Google, Yelp)\n"
            "- Invoice and payment reminders\n"
            "- Customer communication sequences"
        ),
        "pricing": {
            "basic": {
                "price": 997,
                "name": "Local Starter",
                "features": [
                    "Single automation (booking OR reviews OR invoicing)",
                    "Up to 2 tool connections",
                    "Basic email/SMS templates",
                    "Email support",
                    "30-day warranty",
                ],
            },
            "pro": {
                "price": 2497,
                "name": "Local Growth",
                "features": [
                    "Up to 3 automations",
                    "Up to 5 tool connections",
                    "Lead follow-up sequences",
                    "Review management",
                    "Phone support",
                    "90-day warranty",
                ],
            },
            "enterprise": {
                "price": 4997,
                "name": "Local Dominator",
                "features": [
                    "Unlimited automations",
                    "Full CRM setup and automation",
                    "Multi-location support",
                    "Custom reporting dashboard",
                    "Dedicated account manager",
                    "Quarterly optimization",
                    "12-month warranty",
                ],
            },
        },
        "timeline": (
            "- Day 1-2: Understand your business and current tools\n"
            "- Day 3-5: Build and configure automations\n"
            "- Day 6-7: Test with real scenarios\n"
            "- Day 8: Go live"
        ),
        "roi_projection": (
            "Based on {hours_lost} hours/week at ${hourly_rate}/hour:\n"
            "- Weekly time saved: {hours_lost} hours\n"
            "- Monthly savings: ${monthly_savings}\n"
            "- Annual savings: ${annual_savings}\n"
            "- Payback period: {payback_weeks} weeks"
        ),
        "next_steps": (
            "1. Reply or call: https://calendly.com/ashishtaneja\n"
            "2. Free 20-minute business review\n"
            "3. Pick your plan\n"
            "4. Live within {delivery_weeks} days"
        ),
    },
}
