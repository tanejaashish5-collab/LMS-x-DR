"""
Follow-up 1 Email Template - Sent 3 days after proposal.
Light touch, adds new value.
"""

FOLLOWUP_1_EMAIL = {
    "type": "followup_1",
    "subject": "Re: Your automation proposal for {company_name}",
    "body": """Hi {contact_name},

Just checking in on the proposal I sent over. I know things get busy.

I wanted to share something relevant -- we just helped another {vertical} business automate their {process_name} and they cut processing time by 80% in the first week. Thought that might resonate given what you described.

If you have any questions about the proposal or want to adjust the scope, just reply here. No pressure at all.

Best,
Ashish""",
}
