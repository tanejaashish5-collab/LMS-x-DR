"""
ATLAS Email Templates
Used by CLOSER agent for outreach sequences.
"""

from .intro import INTRO_EMAIL
from .proposal import PROPOSAL_EMAIL
from .followup_1 import FOLLOWUP_1_EMAIL
from .followup_2 import FOLLOWUP_2_EMAIL
from .followup_3 import FOLLOWUP_3_EMAIL
from .close import CLOSE_EMAIL

__all__ = [
    'INTRO_EMAIL',
    'PROPOSAL_EMAIL',
    'FOLLOWUP_1_EMAIL',
    'FOLLOWUP_2_EMAIL',
    'FOLLOWUP_3_EMAIL',
    'CLOSE_EMAIL',
]
