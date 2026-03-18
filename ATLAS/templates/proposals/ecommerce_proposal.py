"""
E-commerce Proposal Template - For online stores and retail businesses.
"""

ECOMMERCE_PROPOSAL = {
    "vertical": "ecommerce",
    "template": {
        "executive_summary": (
            "{company_name} is spending too much time on {pain_point} when that "
            "effort should go toward growing revenue and improving customer experience. "
            "We automate the repetitive backend operations so your team can focus on "
            "selling and scaling."
        ),
        "problem_statement": (
            "Common pain points we see in e-commerce operations like yours:\n"
            "- {hours_lost} hours/week on {process_name}\n"
            "- Order processing delays during peak periods\n"
            "- Inventory sync errors across channels\n"
            "- Manual customer communication eating up support time\n"
            "- Revenue lost to slow fulfillment and shipping updates"
        ),
        "proposed_solution": (
            "We connect your e-commerce stack ({tools_used}) into a single automated "
            "pipeline. Orders flow from storefront to fulfillment without manual "
            "touchpoints. Customer communications trigger automatically. Inventory "
            "stays synced in real time.\n\n"
            "Key components:\n"
            "- Shopify/WooCommerce order automation\n"
            "- Multi-channel inventory sync\n"
            "- Automated shipping notifications and tracking\n"
            "- Returns and refund workflow\n"
            "- Customer review request sequences"
        ),
        "pricing": {
            "basic": {
                "price": 997,
                "name": "Store Essentials",
                "features": [
                    "Single channel order automation",
                    "Basic inventory sync",
                    "Shipping notification emails",
                    "Email support",
                    "30-day warranty",
                ],
            },
            "pro": {
                "price": 2497,
                "name": "Multi-Channel Pro",
                "features": [
                    "Multi-channel order automation",
                    "Real-time inventory sync (up to 3 channels)",
                    "Automated review requests",
                    "Returns workflow",
                    "Priority support",
                    "90-day warranty",
                ],
            },
            "enterprise": {
                "price": 4997,
                "name": "Commerce Engine",
                "features": [
                    "Unlimited channels and marketplaces",
                    "Advanced inventory forecasting",
                    "Custom reporting dashboard",
                    "ERP integration",
                    "Dedicated account manager",
                    "Quarterly optimization",
                    "12-month warranty",
                ],
            },
        },
        "timeline": (
            "- Week 1: Audit your current stack and order flow\n"
            "- Week 2: Build integrations and automation rules\n"
            "- Week 3: Test with live orders (parallel run)\n"
            "- Week 4: Full cutover and monitoring"
        ),
        "roi_projection": (
            "Based on {hours_lost} hours/week at ${hourly_rate}/hour:\n"
            "- Monthly time savings: ${monthly_savings}\n"
            "- Reduced errors saving an estimated ${error_savings}/month\n"
            "- Annual total savings: ${annual_savings}\n"
            "- Payback period: {payback_weeks} weeks"
        ),
        "next_steps": (
            "1. Reply or book a call: https://calendly.com/ashishtaneja\n"
            "2. Free 30-minute store audit\n"
            "3. Pick your tier\n"
            "4. Live within {delivery_weeks} weeks"
        ),
    },
}
