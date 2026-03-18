"""
Proposal Email Template - Sent alongside a formal proposal.
Delivers the proposal link and summarizes the key value points.
"""

PROPOSAL_EMAIL = {
    "type": "proposal",
    "subject": "Your automation proposal for {company_name}",
    "body": """Hi {contact_name},

Great chatting earlier. As promised, here is the proposal tailored for {company_name}.

The short version: we can automate {pain_point} and save your team approximately {hours_saved} hours per week. Based on your current costs, that translates to roughly {roi_estimate} in annual savings.

I have outlined three options:

- Basic ({basic_price} AUD): {basic_summary}
- Pro ({pro_price} AUD): {pro_summary}
- Enterprise ({enterprise_price} AUD): {enterprise_summary}

Most {vertical} businesses in your position go with the Pro tier because it covers {pro_reason}.

Full proposal is attached. Happy to walk through it whenever suits you -- just reply to this email or grab a time here: https://calendly.com/ashishtaneja

Talk soon,
Ashish Taneja
ForgeVoice Studio
ashish@forgevoice.studio""",
}
