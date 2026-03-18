"""
Close Email Template - Sent when a deal is agreed upon.
Confirms next steps and kicks off delivery.
"""

CLOSE_EMAIL = {
    "type": "close",
    "subject": "Welcome aboard, {company_name} -- next steps",
    "body": """Hi {contact_name},

Thrilled to have {company_name} on board. Here is what happens next:

1. You will receive an invoice for {deal_value} AUD within the hour.
2. Once payment clears, we kick off your {solution_type} setup.
3. I will send a short intake form (5 minutes) to gather your system details.
4. Your automation goes live within {delivery_days} business days.

Throughout the process, I am your direct point of contact. Reply here anytime or book a call if something comes up: https://calendly.com/ashishtaneja

Looking forward to saving your team {hours_saved} hours a week.

Ashish Taneja
ForgeVoice Studio
ashish@forgevoice.studio""",
}
