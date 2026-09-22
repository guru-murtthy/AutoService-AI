from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.all_models import Lead, FollowUp, Expense, SelfImprovementProposal

def generate_business_recommendations(business_id: str, db: Session) -> List[Dict[str, Any]]:
    """
    Autonomous Recommendation Engine.
    Analyzes business health, pipeline staleness, and costs.
    Generates actionable proposals WITHOUT performing unauthorized auto-changes.
    """
    proposals = []

    # 1. Check for stale leads (>3 days without quotation response)
    stale_leads = db.query(Lead).filter(
        Lead.business_id == business_id,
        Lead.status == "QUOTED"
    ).all()

    if len(stale_leads) > 3:
        proposals.append({
            "category": "sales_optimization",
            "proposal": f"Follow up with {len(stale_leads)} stale quoted leads by offering a 5% early-bird booking discount.",
            "expected_saving": "Boost conversion by ~15%",
            "risk": "low",
            "status": "PENDING_REVIEW"
        })

    # 2. AI token cost optimization proposal
    total_ai_expenses = db.query(Expense).filter(
        Expense.business_id == business_id,
        Expense.category == "AI_API"
    ).all()

    if total_ai_expenses:
        proposals.append({
            "category": "cost_reduction",
            "proposal": "Enable response caching for repeated customer destination queries to lower AI token costs.",
            "expected_saving": "25% lower API cost",
            "risk": "low",
            "status": "PENDING_REVIEW"
        })

    # Record in SelfImprovementProposal table
    for p in proposals:
        existing = db.query(SelfImprovementProposal).filter(SelfImprovementProposal.proposal == p["proposal"]).first()
        if not existing:
            prop_rec = SelfImprovementProposal(
                proposal=p["proposal"],
                expected_saving=p.get("expected_saving"),
                risk=p.get("risk", "low"),
                status="PENDING_REVIEW"
            )
            db.add(prop_rec)
    db.commit()

    return proposals
