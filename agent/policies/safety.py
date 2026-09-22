from sqlalchemy.orm import Session
from app.core.config import settings
from app.services.emergency_stop import is_emergency_stop_active

class SafetyPolicyViolation(Exception):
    pass

class SafetyPolicyEngine:
    def __init__(self, db: Session):
        self.db = db

    def validate_action(self, action_name: str, action_params: dict, estimated_cost: float = 0.0):
        # 1. Emergency Stop Check
        if is_emergency_stop_active(self.db):
            raise SafetyPolicyViolation("EMERGENCY STOP IS ACTIVE. Agent execution blocked.")

        # 2. Business Validation Mode Guard
        if settings.BUSINESS_VALIDATION_MODE and action_name in ["send_message", "execute_payment", "send_quote_to_customer"]:
            if not action_params.get("human_approved", False):
                raise SafetyPolicyViolation(f"Action '{action_name}' requires human approval in BUSINESS_VALIDATION_MODE.")

        # 3. Financial Spending Limit Check
        if estimated_cost > settings.DAILY_SPENDING_LIMIT:
            raise SafetyPolicyViolation(
                f"Action cost ₹{estimated_cost:.2f} exceeds daily spending limit ₹{settings.DAILY_SPENDING_LIMIT:.2f}."
            )

        # 4. High-value Quote Approval Threshold
        if action_name == "create_quote":
            calc_total = action_params.get("total", 0.0)
            if calc_total > settings.APPROVAL_THRESHOLD and not action_params.get("owner_approved", False):
                # Force status to PENDING_APPROVAL
                action_params["force_pending_approval"] = True

        return True
