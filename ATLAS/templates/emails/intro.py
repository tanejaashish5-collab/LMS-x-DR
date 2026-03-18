"""
Intro Email Template - First contact with a potential lead.
Sent when a qualified opportunity is first contacted.
"""

INTRO_EMAIL = {
    "type": "intro",
    "subject": "Quick question about {pain_point}",
    "body": """Hi {contact_name},

I came across your post about {pain_point} and it caught my attention -- we solve exactly this problem for {vertical} businesses.

Most of our clients in your space were losing {hours_lost} hours a week on manual {process_name} before switching to an automated workflow. Now it runs itself and they focus on what actually makes them money.

We built a system specifically for {vertical} that handles {solution_summary}. No custom software, no six-month implementation. Most clients are live within a week.

Would it make sense to jump on a 15-minute call this week? I can show you what we built for a similar {vertical} company.

Best,
Ashish Taneja
ForgeVoice Studio
hello@forgevoicestudio.com""",
}
