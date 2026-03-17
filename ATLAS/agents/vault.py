#!/usr/bin/env python3
"""
VAULT Agent - Budget Guardian for ATLAS
Controls all spending, tracks budgets, enforces limits

Monthly budget: $250
Per-experiment limit: $50
Conservation mode at 80% spend
"""

import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass
from supabase import create_client, Client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('VAULT')


# ===========================================
# Data Models
# ===========================================

@dataclass
class BudgetRequest:
    """Budget request from any ATLAS agent"""
    amount: float
    experiment_id: Optional[str] = None
    agent: str = "unknown"
    description: str = "Budget request"
    type: str = "api_call"


@dataclass
class BudgetLimits:
    """Budget configuration limits"""
    monthly_limit: float = 250.00
    experiment_limit: float = 50.00
    conservation_threshold: float = 0.8  # 80% of monthly budget
    minimum_balance: float = 10.00  # Always keep $10 reserve


# ===========================================
# VAULT Agent Class
# ===========================================

class VAULTAgent:
    """
    Budget guardian that controls all spending in ATLAS system

    Responsibilities:
    - Check budget requests against limits
    - Track spending in Supabase database
    - Enforce monthly and per-experiment limits
    - Activate conservation mode when needed
    - Log all decisions for audit trail
    """

    def __init__(
        self,
        supabase_url: str = None,
        supabase_key: str = None,
        limits: BudgetLimits = None
    ):
        """
        Initialize VAULT agent

        Args:
            supabase_url: Supabase project URL (defaults to env var)
            supabase_key: Supabase anon key (defaults to env var)
            limits: Custom budget limits (defaults to standard limits)
        """
        # Initialize Supabase client
        self.supabase_url = supabase_url or os.getenv('SUPABASE_URL')
        self.supabase_key = supabase_key or os.getenv('SUPABASE_ANON_KEY')

        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY environment variables are required")

        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)

        # Set budget limits
        self.limits = limits or BudgetLimits()

        logger.info(
            f"VAULT initialized - Monthly: ${self.limits.monthly_limit}, "
            f"Per-experiment: ${self.limits.experiment_limit}"
        )

    # ===========================================
    # Main Budget Check Logic
    # ===========================================

    def check_budget(self, request: BudgetRequest) -> Dict[str, Any]:
        """
        Check if budget request should be approved

        Args:
            request: BudgetRequest with amount, experiment_id, agent, description

        Returns:
            Dict with approval status, new balance, message, timestamp
        """
        try:
            # Input validation
            if request.amount <= 0:
                return self._block_request(request, "Invalid amount: must be > 0")

            if request.amount > self.limits.experiment_limit:
                return self._block_request(
                    request,
                    f"Single request exceeds experiment limit: ${request.amount:.2f} > ${self.limits.experiment_limit:.2f}"
                )

            # Get current month budget
            month_key = datetime.now().strftime("%Y-%m")
            budget = self._get_or_create_budget(month_key)

            current_balance = float(budget.get('current_balance', 0))
            total_spent = float(budget.get('total_spent', 0))

            # Check 1: Sufficient balance
            if current_balance < request.amount:
                return self._block_request(
                    request,
                    f"Insufficient balance: ${current_balance:.2f} < ${request.amount:.2f}"
                )

            # Check 2: Minimum reserve
            if (current_balance - request.amount) < self.limits.minimum_balance:
                return self._block_request(
                    request,
                    f"Would breach minimum reserve: ${self.limits.minimum_balance:.2f}"
                )

            # Check 3: Experiment limit
            if request.experiment_id:
                exp_check = self._check_experiment_limit(request)
                if not exp_check['approved']:
                    return exp_check

            # Check 4: Conservation mode
            conservation_limit = self.limits.monthly_limit * self.limits.conservation_threshold
            if total_spent >= conservation_limit:
                conservation_check = self._check_conservation_mode(request, total_spent)
                if not conservation_check['approved']:
                    return conservation_check

            # All checks passed - approve request
            return self._approve_request(request, budget, current_balance)

        except Exception as e:
            logger.error(f"Budget check error: {e}", exc_info=True)
            return self._block_request(request, f"System error: {str(e)}")

    # ===========================================
    # Budget Approval & Tracking
    # ===========================================

    def _approve_request(
        self,
        request: BudgetRequest,
        budget: Dict,
        current_balance: float
    ) -> Dict[str, Any]:
        """
        Approve budget request and update all tracking tables

        Updates:
        1. atlas_budget_ledger - transaction log (budget_summary is a VIEW, updated automatically)
        2. atlas_experiments - experiment spending
        3. atlas_agent_logs - approval log

        Note: atlas_budget_summary is a VIEW and cannot be updated directly.
        It's calculated from atlas_budget_ledger automatically.
        """
        new_balance = current_balance - request.amount
        month_key = budget['month_key']

        try:
            # Update 1: Ledger entry (this will update the budget_summary VIEW automatically)
            self.supabase.table('atlas_budget_ledger').insert({
                'type': 'spend',
                'amount': request.amount,
                'experiment_id': request.experiment_id,
                'agent': request.agent.lower(),  # Agent enum values are lowercase
                'description': request.description,
                'balance_after': new_balance,
                'month_key': month_key,
                'created_at': datetime.now().isoformat()
            }).execute()

            # Update 2: Experiment spending
            if request.experiment_id:
                self._update_experiment_spend(request)

            # Update 3: Agent log
            self.supabase.table('atlas_agent_logs').insert({
                'agent': 'vault',
                'action': 'budget_approved',
                'input': f"Amount: ${request.amount:.2f}, Agent: {request.agent}, Experiment: {request.experiment_id}",
                'output': f"Approved - New balance: ${new_balance:.2f}",
                'status': 'success'
            }).execute()

            logger.info(
                f"Approved ${request.amount:.2f} for {request.agent} - "
                f"Balance: ${new_balance:.2f}"
            )

            return {
                "approved": True,
                "amount": request.amount,
                "new_balance": new_balance,
                "previous_balance": current_balance,
                "message": f"Approved ${request.amount:.2f}",
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to approve request: {e}", exc_info=True)
            return self._block_request(request, f"Approval failed: {str(e)}")

    def _block_request(self, request: BudgetRequest, reason: str) -> Dict[str, Any]:
        """
        Block budget request and log rejection
        """
        try:
            # Log rejection
            self.supabase.table('atlas_agent_logs').insert({
                'agent': 'vault',
                'action': 'budget_blocked',
                'input': f"Amount: ${request.amount:.2f}, Agent: {request.agent}, Experiment: {request.experiment_id}",
                'output': f"Blocked: {reason}",
                'status': 'blocked'
            }).execute()

            logger.warning(f"Blocked ${request.amount:.2f} for {request.agent}: {reason}")

        except Exception as e:
            logger.error(f"Failed to log block: {e}")

        return {
            "approved": False,
            "amount": request.amount,
            "reason": reason,
            "message": f"Blocked: {reason}",
            "timestamp": datetime.now().isoformat()
        }

    # ===========================================
    # Budget Checks & Validations
    # ===========================================

    def _check_experiment_limit(self, request: BudgetRequest) -> Dict[str, Any]:
        """Check if experiment would exceed per-experiment limit"""
        try:
            # Use 'id' column instead of 'experiment_id'
            exp_result = self.supabase.table('atlas_experiments').select(
                "budget_spent"
            ).eq('id', request.experiment_id).execute()

            if exp_result.data:
                experiment_spent = float(exp_result.data[0].get('budget_spent', 0))
                new_total = experiment_spent + request.amount

                if new_total > self.limits.experiment_limit:
                    return {
                        "approved": False,
                        "reason": (
                            f"Experiment limit exceeded: "
                            f"${experiment_spent:.2f} + ${request.amount:.2f} = ${new_total:.2f} "
                            f"> ${self.limits.experiment_limit:.2f}"
                        )
                    }

            return {"approved": True}

        except Exception as e:
            logger.error(f"Experiment check error: {e}")
            return {"approved": False, "reason": f"Experiment check failed: {str(e)}"}

    def _check_conservation_mode(
        self,
        request: BudgetRequest,
        total_spent: float
    ) -> Dict[str, Any]:
        """
        Check if spending is allowed in conservation mode

        Conservation mode activates at 80% of monthly budget
        Only high-priority agents (SONNET, ATLAS) can spend
        """
        conservation_limit = self.limits.monthly_limit * self.limits.conservation_threshold

        logger.warning(
            f"Conservation mode active: ${total_spent:.2f} > ${conservation_limit:.2f}"
        )

        # High-priority agents can spend in conservation mode
        high_priority_agents = ['SONNET', 'ATLAS', 'VAULT']

        if request.agent in high_priority_agents:
            logger.info(f"High-priority agent {request.agent} allowed in conservation mode")
            return {"approved": True}

        return {
            "approved": False,
            "reason": (
                f"Conservation mode active - only {', '.join(high_priority_agents)} "
                f"agents can spend (${total_spent:.2f} / ${self.limits.monthly_limit:.2f})"
            )
        }

    # ===========================================
    # Database Helpers
    # ===========================================

    def _get_or_create_budget(self, month_key: str) -> Dict:
        """Get budget for month, create if doesn't exist"""
        try:
            result = self.supabase.table('atlas_budget_summary').select(
                "*"
            ).eq('month_key', month_key).execute()

            if result.data:
                return result.data[0]

            # Initialize new month budget
            return self._initialize_budget(month_key)

        except Exception as e:
            logger.error(f"Failed to get budget: {e}")
            raise

    def _initialize_budget(self, month_key: str) -> Dict:
        """Initialize budget for new month"""
        budget_data = {
            "month_key": month_key,
            "total_deposited": self.limits.monthly_limit,
            "total_spent": 0,
            "total_revenue": 0,
            "current_balance": self.limits.monthly_limit,
            "transaction_count": 0
        }

        result = self.supabase.table('atlas_budget_summary').insert(
            budget_data
        ).execute()

        logger.info(f"Initialized budget for {month_key}: ${self.limits.monthly_limit}")

        return result.data[0] if result.data else budget_data

    def _update_experiment_spend(self, request: BudgetRequest):
        """Update experiment budget_spent field"""
        try:
            # Use 'id' column instead of 'experiment_id'
            exp_result = self.supabase.table('atlas_experiments').select(
                "budget_spent"
            ).eq('id', request.experiment_id).execute()

            if exp_result.data:
                current_spend = float(exp_result.data[0].get('budget_spent', 0))
                new_spend = current_spend + request.amount

                self.supabase.table('atlas_experiments').update({
                    'budget_spent': new_spend
                }).eq('id', request.experiment_id).execute()

                logger.info(
                    f"Updated experiment {request.experiment_id}: "
                    f"${current_spend:.2f} -> ${new_spend:.2f}"
                )

        except Exception as e:
            logger.error(f"Failed to update experiment spend: {e}")

    # ===========================================
    # Reporting & Analytics
    # ===========================================

    def get_budget_status(self) -> Dict[str, Any]:
        """Get current budget status for reporting"""
        try:
            month_key = datetime.now().strftime("%Y-%m")
            budget = self._get_or_create_budget(month_key)

            total_spent = float(budget.get('total_spent', 0))
            current_balance = float(budget.get('current_balance', 0))

            return {
                "month": month_key,
                "monthly_limit": self.limits.monthly_limit,
                "current_balance": current_balance,
                "total_spent": total_spent,
                "percent_spent": (total_spent / self.limits.monthly_limit) * 100,
                "conservation_mode": total_spent >= (self.limits.monthly_limit * self.limits.conservation_threshold),
                "transaction_count": budget.get('transaction_count', 0),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to get budget status: {e}")
            return {"error": str(e)}

    def get_experiment_spend(self, experiment_id: str) -> Dict[str, Any]:
        """Get spending summary for specific experiment"""
        try:
            # Get experiment data using 'id' column
            exp_result = self.supabase.table('atlas_experiments').select(
                "id, name, budget_spent"
            ).eq('id', experiment_id).execute()

            if not exp_result.data:
                return {"error": "Experiment not found"}

            experiment = exp_result.data[0]
            budget_spent = float(experiment.get('budget_spent', 0))

            # Get transaction history
            ledger_result = self.supabase.table('atlas_budget_ledger').select(
                "*"
            ).eq('experiment_id', experiment_id).order(
                'created_at', desc=True
            ).execute()

            return {
                "experiment_id": experiment_id,
                "name": experiment.get('name'),
                "budget_spent": budget_spent,
                "budget_limit": self.limits.experiment_limit,
                "percent_used": (budget_spent / self.limits.experiment_limit) * 100,
                "remaining": self.limits.experiment_limit - budget_spent,
                "transaction_count": len(ledger_result.data) if ledger_result.data else 0,
                "transactions": ledger_result.data or [],
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to get experiment spend: {e}")
            return {"error": str(e)}


# ===========================================
# Standalone Testing
# ===========================================

def main():
    """Test VAULT agent functionality"""
    print("=" * 60)
    print(" VAULT Agent - Budget Guardian")
    print("=" * 60)

    # Initialize agent
    vault = VAULTAgent()

    # Get budget status
    print("\n1. Current Budget Status:")
    status = vault.get_budget_status()
    if 'error' not in status:
        print(f"   Balance: ${status['current_balance']:.2f}")
        print(f"   Spent: ${status['total_spent']:.2f} ({status['percent_spent']:.1f}%)")
        print(f"   Conservation: {status['conservation_mode']}")
    else:
        print(f"   Error: {status['error']}")

    # Test budget request without experiment ID
    print("\n2. Testing Budget Request (no experiment):")
    test_request = BudgetRequest(
        amount=5.00,
        experiment_id=None,
        agent="SCOUT",
        description="Test API call"
    )

    result = vault.check_budget(test_request)
    print(f"   Approved: {result['approved']}")
    print(f"   Message: {result.get('message', result.get('reason', 'No message'))}")
    if result['approved']:
        print(f"   New Balance: ${result['new_balance']:.2f}")

    # Test conservation mode trigger
    print("\n3. Testing High-Spend Request (conservation mode check):")
    conservation_request = BudgetRequest(
        amount=50.00,
        experiment_id=None,
        agent="FORGE",
        description="Build landing page"
    )

    result2 = vault.check_budget(conservation_request)
    print(f"   Approved: {result2['approved']}")
    print(f"   Message: {result2.get('message', result2.get('reason', 'No message'))}")
    if result2['approved']:
        print(f"   New Balance: ${result2['new_balance']:.2f}")

    print("\n" + "=" * 60)
    print(" VAULT agent ready for ATLAS orchestrator")
    print("=" * 60)


if __name__ == "__main__":
    main()
