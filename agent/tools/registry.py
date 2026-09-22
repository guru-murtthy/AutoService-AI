from typing import Dict, Any, Callable
from sqlalchemy.orm import Session

from app.models.all_models import Lead, Customer, Conversation, Message, Quotation, FollowUp, AgentTask, SystemHealth
from app.schemas.all_schemas import QuoteCalculationRequest
from app.pricing.engine import calculate_deterministic_quote
from app.services.analytics_service import generate_daily_report
from app.services.revenue_service import calculate_revenue_metrics

class AgentToolRegistry:
    def __init__(self, db: Session):
        self.db = db
        self.tools: Dict[str, Callable] = {
            "search_leads": self.search_leads,
            "get_customer": self.get_customer,
            "get_conversation": self.get_conversation,
            "create_lead": self.create_lead,
            "update_lead": self.update_lead,
            "calculate_quote": self.calculate_quote,
            "create_quote": self.create_quote,
            "send_message": self.send_message,
            "schedule_followup": self.schedule_followup,
            "cancel_followup": self.cancel_followup,
            "generate_report": self.generate_report,
            "get_business_metrics": self.get_business_metrics,
            "get_system_health": self.get_system_health
        }

    def execute_tool(self, name: str, params: dict) -> dict:
        if name not in self.tools:
            return {"error": f"Unknown tool: {name}"}
        return self.tools[name](params)

    # 1. search_leads
    def search_leads(self, params: dict) -> dict:
        b_id = params.get("business_id")
        status = params.get("status")
        query = self.db.query(Lead).filter(Lead.business_id == b_id)
        if status:
            query = query.filter(Lead.status == status)
        leads = query.all()
        return {"leads": [{"id": l.id, "customer_id": l.customer_id, "destination": l.destination, "status": l.status, "score": l.lead_score} for l in leads]}

    # 2. get_customer
    def get_customer(self, params: dict) -> dict:
        c_id = params.get("customer_id")
        cust = self.db.query(Customer).filter(Customer.id == c_id).first()
        if not cust:
            return {"error": "Customer not found"}
        return {"id": cust.id, "name": cust.name, "phone": cust.phone, "email": cust.email}

    # 3. get_conversation
    def get_conversation(self, params: dict) -> dict:
        conv_id = params.get("conversation_id")
        msgs = self.db.query(Message).filter(Message.conversation_id == conv_id).order_by(Message.created_at.asc()).all()
        return {"messages": [{"sender": m.sender_type, "message": m.message, "time": m.created_at.isoformat()} for m in msgs]}

    # 4. create_lead
    def create_lead(self, params: dict) -> dict:
        lead = Lead(
            business_id=params["business_id"],
            customer_id=params["customer_id"],
            destination=params.get("destination"),
            origin=params.get("origin"),
            travel_date=params.get("travel_date"),
            vehicle_type=params.get("vehicle_type"),
            passenger_count=params.get("passenger_count"),
            status="QUALIFIED"
        )
        self.db.add(lead)
        self.db.commit()
        self.db.refresh(lead)
        return {"lead_id": lead.id, "status": lead.status}

    # 5. update_lead
    def update_lead(self, params: dict) -> dict:
        lead = self.db.query(Lead).filter(Lead.id == params["lead_id"]).first()
        if not lead: return {"error": "Lead not found"}
        if "status" in params: lead.status = params["status"]
        if "lead_score" in params: lead.lead_score = params["lead_score"]
        self.db.commit()
        return {"lead_id": lead.id, "status": lead.status, "score": lead.lead_score}

    # 6. calculate_quote
    def calculate_quote(self, params: dict) -> dict:
        req = QuoteCalculationRequest(
            business_id=params["business_id"],
            vehicle_type=params["vehicle_type"],
            duration_days=params.get("duration_days", 1),
            estimated_km=params.get("estimated_km"),
            discount_amount=params.get("discount_amount", 0.0)
        )
        res = calculate_deterministic_quote(req, self.db)
        return res.model_dump()

    # 7. create_quote
    def create_quote(self, params: dict) -> dict:
        import uuid
        from datetime import datetime, timedelta
        q_num = f"QT-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:4].upper()}"
        q = Quotation(
            lead_id=params["lead_id"],
            quotation_number=q_num,
            subtotal=params["subtotal"],
            tax=params["tax"],
            discount=params.get("discount", 0.0),
            total=params["total"],
            status="PENDING_APPROVAL",
            valid_until=datetime.utcnow() + timedelta(days=7)
        )
        self.db.add(q)
        self.db.commit()
        return {"quotation_id": q.id, "number": q_num, "status": q.status}

    # 8. send_message
    def send_message(self, params: dict) -> dict:
        # In mock mode, records sending intent
        return {"status": "sent", "channel": "whatsapp", "recipient": params.get("phone")}

    # 9. schedule_followup
    def schedule_followup(self, params: dict) -> dict:
        from app.services.followup_service import schedule_default_followups
        followups = schedule_default_followups(params["lead_id"], self.db)
        return {"status": "scheduled", "count": len(followups)}

    # 10. cancel_followup
    def cancel_followup(self, params: dict) -> dict:
        f = self.db.query(FollowUp).filter(FollowUp.lead_id == params["lead_id"], FollowUp.status == "SCHEDULED").all()
        for item in f: item.status = "CANCELLED"
        self.db.commit()
        return {"cancelled_count": len(f)}

    # 11. generate_report
    def generate_report(self, params: dict) -> dict:
        from datetime import date
        rep = generate_daily_report(params["business_id"], date.today(), self.db)
        return rep.model_dump()

    # 12. get_business_metrics
    def get_business_metrics(self, params: dict) -> dict:
        return calculate_revenue_metrics(params["business_id"], self.db)

    # 13. get_system_health
    def get_system_health(self, params: dict) -> dict:
        return {"status": "healthy", "database": "connected", "worker": "active"}
