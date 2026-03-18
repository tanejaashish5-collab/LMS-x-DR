"""
ATLAS Proposal Templates
Used by CLOSER agent to generate tailored proposals per vertical.
"""

from .saas_proposal import SAAS_PROPOSAL
from .ecommerce_proposal import ECOMMERCE_PROPOSAL
from .agency_proposal import AGENCY_PROPOSAL
from .local_business_proposal import LOCAL_BUSINESS_PROPOSAL
from .generic_proposal import GENERIC_PROPOSAL

VERTICAL_TEMPLATES = {
    'saas': SAAS_PROPOSAL,
    'software': SAAS_PROPOSAL,
    'ecommerce': ECOMMERCE_PROPOSAL,
    'e-commerce': ECOMMERCE_PROPOSAL,
    'retail': ECOMMERCE_PROPOSAL,
    'agency': AGENCY_PROPOSAL,
    'marketing': AGENCY_PROPOSAL,
    'consulting': AGENCY_PROPOSAL,
    'local': LOCAL_BUSINESS_PROPOSAL,
    'restaurant': LOCAL_BUSINESS_PROPOSAL,
    'healthcare': LOCAL_BUSINESS_PROPOSAL,
    'legal': LOCAL_BUSINESS_PROPOSAL,
    'real estate': LOCAL_BUSINESS_PROPOSAL,
}

__all__ = [
    'SAAS_PROPOSAL',
    'ECOMMERCE_PROPOSAL',
    'AGENCY_PROPOSAL',
    'LOCAL_BUSINESS_PROPOSAL',
    'GENERIC_PROPOSAL',
    'VERTICAL_TEMPLATES',
]
