from datetime import datetime
from typing import List, Tuple
from sqlalchemy.orm import Session

from app.models.all_models import Customer, Conversation, Message, Lead, AuditLog
from app.schemas.all_schemas import EnquiryRequest, EnquiryResponse, ExtractedRequirement
from app.ai.provider import ai_provider
from app.services.lead_scoring import calculate_lead_score
from app.services.followup_service import check_customer_opt_out, handle_customer_opt_out

REQUIRED_FIELDS = ["destination", "vehicle_type", "duration_days", "travel_date", "passenger_count"]

async def process_customer_enquiry(req: EnquiryRequest, db: Session) -> EnquiryResponse:
    # 1. Get or create Customer
    customer = db.query(Customer).filter(
        Customer.business_id == req.business_id,
        (Customer.phone == req.phone) | (Customer.email == req.email) if (req.phone or req.email) else (Customer.name == req.customer_name)
    ).first()

    if not customer:
        customer = Customer(
            business_id=req.business_id,
            name=req.customer_name,
            phone=req.phone,
            email=req.email,
            source="web_chat"
        )
        db.add(customer)
        db.commit()
        db.refresh(customer)

    # 2. Get or create Conversation
    conversation = db.query(Conversation).filter(
        Conversation.business_id == req.business_id,
        Conversation.customer_id == customer.id,
        Conversation.status == "active"
    ).first()

    if not conversation:
        conversation = Conversation(
            business_id=req.business_id,
            customer_id=customer.id,
            channel="web_chat",
            status="active"
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    # 3. Add customer message to conversation
    cust_msg = Message(
        conversation_id=conversation.id,
        sender_type="customer",
        message=req.message
    )
    db.add(cust_msg)
    conversation.last_message_at = datetime.utcnow()
    db.commit()

    # 4. Check for Customer Opt-Out Keyword ("STOP", "Unsubscribe", "do not contact")
    is_optout = check_customer_opt_out(req.message)

    # 5. Fetch prior messages for conversation memory context
    prior_messages = db.query(Message).filter(Message.conversation_id == conversation.id).order_by(Message.created_at.asc()).all()
    history_list = [{"sender_type": m.sender_type, "message": m.message} for m in prior_messages]

    # 6. Extract requirement using AI abstraction (or fallback)
    raw_extraction = await ai_provider.extract_requirements(req.message, history_list)
    extracted = ExtractedRequirement(**raw_extraction)

    # 7. Get or create Lead
    lead = db.query(Lead).filter(
        Lead.business_id == req.business_id,
        Lead.customer_id == customer.id,
        Lead.status != "BOOKED",
        Lead.status != "LOST"
    ).first()

    if not lead:
        lead = Lead(
            business_id=req.business_id,
            customer_id=customer.id,
            origin=extracted.origin,
            destination=extracted.destination,
            vehicle_type=extracted.vehicle_type,
            duration_days=extracted.duration_days,
            travel_date=extracted.travel_date,
            passenger_count=extracted.passenger_count,
            budget=extracted.budget,
            status="NEW",
            lead_score=50
        )
        db.add(lead)
        db.commit()
        db.refresh(lead)

    if is_optout:
        handle_customer_opt_out(lead.id, db)
        reply_message = f"You have been unsubscribed from automated check-ins. Thank you {customer.name}!"
        ai_msg = Message(
            conversation_id=conversation.id,
            sender_type="ai",
            message=reply_message
        )
        db.add(ai_msg)
        db.commit()

        return EnquiryResponse(
            lead_id=lead.id,
            customer_id=customer.id,
            extracted=extracted,
            missing_fields=[],
            reply_message=reply_message,
            lead_score=0
        )

    # 8. Detect missing required fields
    missing_fields = []
    if not extracted.destination:
        missing_fields.append("destination")
    if not extracted.vehicle_type:
        missing_fields.append("vehicle_type")
    if not extracted.duration_days:
        missing_fields.append("duration_days")
    if not extracted.travel_date:
        missing_fields.append("travel_date")
    if not extracted.passenger_count:
        missing_fields.append("passenger_count")

    # 9. Generate targeted response asking ONLY for missing fields
    if missing_fields:
        missing_readable = []
        if "destination" in missing_fields:
            missing_readable.append("destination city")
        if "vehicle_type" in missing_fields:
            missing_readable.append("preferred vehicle type (e.g. 5-seater sedan or 7-seater SUV)")
        if "duration_days" in missing_fields:
            missing_readable.append("number of days for your trip")
        if "travel_date" in missing_fields:
            missing_readable.append("start date of travel")
        if "passenger_count" in missing_fields:
            missing_readable.append("number of passengers")

        missing_str = ", ".join(missing_readable)
        reply_message = f"Thank you {customer.name}! To provide an exact quotation for your trip, could you please specify: {missing_str}?"
    else:
        reply_message = f"Thank you {customer.name}! We have all the details for your trip to {extracted.destination} ({extracted.duration_days} days starting {extracted.travel_date} in a {extracted.vehicle_type}). Preparing your instant quotation now!"

    ai_msg = Message(
        conversation_id=conversation.id,
        sender_type="ai",
        message=reply_message,
        metadata_json=extracted.model_dump()
    )
    db.add(ai_msg)

    # 10. Update Lead
    lead_score, reasons = calculate_lead_score(extracted, len(prior_messages))
    if extracted.origin: lead.origin = extracted.origin
    if extracted.destination: lead.destination = extracted.destination
    if extracted.vehicle_type: lead.vehicle_type = extracted.vehicle_type
    if extracted.duration_days: lead.duration_days = extracted.duration_days
    if extracted.travel_date: lead.travel_date = extracted.travel_date
    if extracted.passenger_count: lead.passenger_count = extracted.passenger_count
    if extracted.budget: lead.budget = extracted.budget
    lead.lead_score = lead_score
    if not missing_fields:
        lead.status = "QUALIFYING"

    db.commit()
    db.refresh(lead)

    audit = AuditLog(
        actor_type="ai",
        business_id=req.business_id,
        action="ENQUIRY_PROCESSED",
        resource_type="lead",
        resource_id=lead.id,
        metadata_json={"customer_name": customer.name, "missing": missing_fields, "score": lead_score}
    )
    db.add(audit)
    db.commit()

    return EnquiryResponse(
        lead_id=lead.id,
        customer_id=customer.id,
        extracted=extracted,
        missing_fields=missing_fields,
        reply_message=reply_message,
        lead_score=lead_score
    )
