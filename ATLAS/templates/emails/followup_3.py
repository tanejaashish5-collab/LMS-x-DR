"""
Follow-up 3 Email Template - Sent 14 days after proposal.
Final check-in, graceful close.
"""

FOLLOWUP_3_EMAIL = {
    "type": "followup_3",
    "subject": "Should I close your file?",
    "body": """Hi {contact_name},

I have reached out a few times about automating {pain_point} for {company_name} and have not heard back, so I want to respect your time.

I will close out your file on my end, but the proposal stays valid if things change. If {pain_point} becomes a bigger issue down the road, just reply to this email and we will pick up where we left off.

Wishing you all the best with {company_name}.

Ashish Taneja
ForgeVoice Studio""",
}
