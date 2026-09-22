from typing import Dict, List, Tuple
from app.schemas.all_schemas import ExtractedRequirement

def calculate_lead_score(extracted: ExtractedRequirement, response_count: int = 1) -> Tuple[int, List[str]]:
    """
    Calculates transparent Engagement Score (0-100) for a lead based on:
    - Travel date provided (+20)
    - Destination specified (+20)
    - Vehicle type specified (+15)
    - Duration specified (+15)
    - Budget provided (+15)
    - Passengers count provided (+15)
    """
    score = 10  # Base score for reaching out
    reasons: List[str] = ["Initial enquiry received (+10)"]

    if extracted.destination:
        score += 20
        reasons.append(f"Destination specified: {extracted.destination} (+20)")

    if extracted.travel_date:
        score += 20
        reasons.append(f"Travel date specified: {extracted.travel_date} (+20)")

    if extracted.vehicle_type:
        score += 15
        reasons.append(f"Vehicle type specified: {extracted.vehicle_type} (+15)")

    if extracted.duration_days and extracted.duration_days > 0:
        score += 15
        reasons.append(f"Trip duration specified: {extracted.duration_days} days (+15)")

    if extracted.passenger_count and extracted.passenger_count > 0:
        score += 10
        reasons.append(f"Passenger count specified: {extracted.passenger_count} pax (+10)")

    if extracted.budget and extracted.budget > 0:
        score += 10
        reasons.append(f"Budget estimate provided: ₹{extracted.budget:,.0f} (+10)")

    # Clamp score between 0 and 100
    final_score = max(0, min(100, score))
    return final_score, reasons
