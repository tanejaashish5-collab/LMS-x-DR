"""
ATLAS Agents Module

Autonomous agents that power the ATLAS system:
- VAULT: Budget guardian
- SCOUT: Opportunity discovery
- FORGE: Landing page builder
- MERCURY: Outreach automation
- ARGUS: Metrics tracker
- ATLAS: Main orchestrator
"""

from .vault import VAULTAgent, BudgetRequest, BudgetLimits
from .scout import SCOUTAgent, Opportunity, FilterResult, ScoreResult
from .forge import FORGEAgent, LandingPageRequest, LandingPageResult
from .mercury import MERCURYAgent, DistributionRequest, DistributionResult, ChannelCopy

__all__ = [
    'VAULTAgent',
    'BudgetRequest',
    'BudgetLimits',
    'SCOUTAgent',
    'Opportunity',
    'FilterResult',
    'ScoreResult',
    'FORGEAgent',
    'LandingPageRequest',
    'LandingPageResult',
    'MERCURYAgent',
    'DistributionRequest',
    'DistributionResult',
    'ChannelCopy',
]
