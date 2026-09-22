import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="owner")  # owner, admin, staff
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    businesses = relationship("Business", back_populates="owner")

class Business(Base):
    __tablename__ = "businesses"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    business_type = Column(String, default="travel_and_tour")
    owner_id = Column(String, ForeignKey("users.id"), nullable=False)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    location = Column(String, nullable=True)
    gst_number = Column(String, nullable=True)
    logo_url = Column(String, nullable=True)
    contact_person = Column(String, nullable=True)
    currency = Column(String, default="INR")
    timezone = Column(String, default="Asia/Kolkata")
    subscription_plan = Column(String, default="STARTER")
    subscription_status = Column(String, default="active")

    # Pilot Metadata
    pilot_business = Column(Boolean, default=True)
    pilot_started_at = Column(DateTime, default=datetime.utcnow)
    pilot_ends_at = Column(DateTime, nullable=True)
    pilot_status = Column(String, default="ACTIVE")  # ONBOARDING, ACTIVE, PAUSED, COMPLETED, CONVERTED, CHURNED

    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="businesses")
    customers = relationship("Customer", back_populates="business")
    leads = relationship("Lead", back_populates="business")
    expenses = relationship("Expense", back_populates="business")
    pricing_configs = relationship("PricingConfig", back_populates="business")

class Customer(Base):
    __tablename__ = "customers"

    id = Column(String, primary_key=True, default=generate_uuid)
    business_id = Column(String, ForeignKey("businesses.id"), nullable=False)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    source = Column(String, default="web_chat")
    is_opted_out = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    business = relationship("Business", back_populates="customers")
    leads = relationship("Lead", back_populates="customer")
    conversations = relationship("Conversation", back_populates="customer")

class Lead(Base):
    __tablename__ = "leads"

    id = Column(String, primary_key=True, default=generate_uuid)
    business_id = Column(String, ForeignKey("businesses.id"), nullable=False)
    customer_id = Column(String, ForeignKey("customers.id"), nullable=False)
    destination = Column(String, nullable=True)
    origin = Column(String, nullable=True)
    duration_days = Column(Integer, nullable=True)
    travel_date = Column(String, nullable=True)
    return_date = Column(String, nullable=True)
    passenger_count = Column(Integer, nullable=True)
    vehicle_type = Column(String, nullable=True)
    budget = Column(Float, nullable=True)
    status = Column(String, default="NEW")  # NEW, QUALIFYING, QUOTED, FOLLOW_UP, BOOKED, LOST, CANCELLED, OPTED_OUT
    lead_score = Column(Integer, default=50)
    assigned_to = Column(String, nullable=True)
    source = Column(String, default="web_chat")
    last_contact_at = Column(DateTime, default=datetime.utcnow)
    next_followup_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    business = relationship("Business", back_populates="leads")
    customer = relationship("Customer", back_populates="leads")
    quotations = relationship("Quotation", back_populates="lead")
    followups = relationship("FollowUp", back_populates="lead")
    bookings = relationship("Booking", back_populates="lead")

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String, primary_key=True, default=generate_uuid)
    business_id = Column(String, ForeignKey("businesses.id"), nullable=False)
    customer_id = Column(String, ForeignKey("customers.id"), nullable=False)
    channel = Column(String, default="web_chat")
    status = Column(String, default="active")  # active, closed, pending_human
    started_at = Column(DateTime, default=datetime.utcnow)
    last_message_at = Column(DateTime, default=datetime.utcnow)

    customer = relationship("Customer", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation")

class Message(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True, default=generate_uuid)
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False)
    sender_type = Column(String, nullable=False)  # customer, ai, human_agent
    message = Column(Text, nullable=False)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    conversation = relationship("Conversation", back_populates="messages")

class Quotation(Base):
    __tablename__ = "quotations"

    id = Column(String, primary_key=True, default=generate_uuid)
    lead_id = Column(String, ForeignKey("leads.id"), nullable=False)
    quotation_number = Column(String, unique=True, nullable=False)
    subtotal = Column(Float, nullable=False)
    tax = Column(Float, nullable=False)
    discount = Column(Float, default=0.0)
    total = Column(Float, nullable=False)
    currency = Column(String, default="INR")
    status = Column(String, default="DRAFT")  # DRAFT, PENDING_APPROVAL, APPROVED, SENT, VIEWED, EXPIRED, BOOKED, LOST, CANCELLED
    valid_until = Column(DateTime, nullable=True)
    approved_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    lead = relationship("Lead", back_populates="quotations")
    items = relationship("QuotationItem", back_populates="quotation", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="quotation")

class QuotationItem(Base):
    __tablename__ = "quotation_items"

    id = Column(String, primary_key=True, default=generate_uuid)
    quotation_id = Column(String, ForeignKey("quotations.id"), nullable=False)
    description = Column(String, nullable=False)
    quantity = Column(Float, default=1.0)
    unit_price = Column(Float, nullable=False)
    total = Column(Float, nullable=False)

    quotation = relationship("Quotation", back_populates="items")

class FollowUp(Base):
    __tablename__ = "follow_ups"

    id = Column(String, primary_key=True, default=generate_uuid)
    lead_id = Column(String, ForeignKey("leads.id"), nullable=False)
    scheduled_at = Column(DateTime, nullable=False)
    status = Column(String, default="SCHEDULED")  # SCHEDULED, EXECUTED, CANCELLED, OPTED_OUT
    attempt_number = Column(Integer, default=1)
    message = Column(Text, nullable=True)
    executed_at = Column(DateTime, nullable=True)

    lead = relationship("Lead", back_populates="followups")

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(String, primary_key=True, default=generate_uuid)
    lead_id = Column(String, ForeignKey("leads.id"), nullable=False)
    quotation_id = Column(String, ForeignKey("quotations.id"), nullable=False)
    status = Column(String, default="CONFIRMED")  # CONFIRMED, COMPLETED, CANCELLED
    booking_amount = Column(Float, nullable=False)
    currency = Column(String, default="INR")
    created_at = Column(DateTime, default=datetime.utcnow)

    lead = relationship("Lead", back_populates="bookings")
    quotation = relationship("Quotation", back_populates="bookings")
    payments = relationship("Payment", back_populates="booking")

class Payment(Base):
    __tablename__ = "payments"

    id = Column(String, primary_key=True, default=generate_uuid)
    booking_id = Column(String, ForeignKey("bookings.id"), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="INR")
    status = Column(String, default="SUCCESS")  # PENDING, SUCCESS, FAILED
    provider = Column(String, default="mock")
    transaction_reference = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    booking = relationship("Booking", back_populates="payments")

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(String, primary_key=True, default=generate_uuid)
    business_id = Column(String, ForeignKey("businesses.id"), nullable=False)
    category = Column(String, nullable=False)  # AI_API, HOSTING, MARKETING, OPERATIONAL
    amount = Column(Float, nullable=False)
    currency = Column(String, default="INR")
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    business = relationship("Business", back_populates="expenses")

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(String, primary_key=True, default=generate_uuid)
    business_id = Column(String, ForeignKey("businesses.id"), nullable=False)
    plan = Column(String, default="STARTER")
    amount = Column(Float, default=5000.0)
    billing_cycle = Column(String, default="monthly")
    status = Column(String, default="active")
    next_billing_date = Column(DateTime, nullable=True)

class AgentTask(Base):
    __tablename__ = "agent_tasks"

    id = Column(String, primary_key=True, default=generate_uuid)
    task_type = Column(String, nullable=False)
    status = Column(String, default="PENDING")  # PENDING, IN_PROGRESS, COMPLETED, FAILED
    priority = Column(Integer, default=5)
    input_data = Column(JSON, nullable=True)
    output_data = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

class AgentEvent(Base):
    __tablename__ = "agent_events"

    id = Column(String, primary_key=True, default=generate_uuid)
    agent_name = Column(String, nullable=False)
    event_type = Column(String, nullable=False)
    payload = Column(JSON, nullable=True)
    severity = Column(String, default="INFO")  # INFO, WARNING, ERROR, CRITICAL
    created_at = Column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, default=generate_uuid)
    actor_type = Column(String, nullable=False)  # user, agent, system
    actor_id = Column(String, nullable=True)
    business_id = Column(String, nullable=True)
    action = Column(String, nullable=False)
    resource_type = Column(String, nullable=False)
    resource_id = Column(String, nullable=True)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class SystemHealth(Base):
    __tablename__ = "system_health"

    id = Column(String, primary_key=True, default=generate_uuid)
    component = Column(String, nullable=False)  # backend, database, ai_provider, worker, automaton
    status = Column(String, default="healthy")  # healthy, degraded, unhealthy
    latency = Column(Float, default=0.0)  # ms
    error_rate = Column(Float, default=0.0)
    checked_at = Column(DateTime, default=datetime.utcnow)

class PricingConfig(Base):
    __tablename__ = "pricing_configs"

    id = Column(String, primary_key=True, default=generate_uuid)
    business_id = Column(String, ForeignKey("businesses.id"), nullable=False)
    vehicle_type = Column(String, nullable=False)  # 5-seater, 7-seater, tempo-traveller
    base_price_per_day = Column(Float, nullable=False)
    included_km_per_day = Column(Float, default=250.0)
    rate_per_km = Column(Float, default=14.0)
    driver_allowance_per_day = Column(Float, default=400.0)
    tax_percentage = Column(Float, default=5.0)  # GST 5%
    toll_config = Column(String, default="at_actuals")
    parking_config = Column(String, default="at_actuals")
    cancellation_policy = Column(Text, default="Full refund 48h prior to departure. 50% refund within 24h.")
    validity_days = Column(Integer, default=7)
    terms_and_conditions = Column(Text, default="1. Tolls & parking at actuals. 2. Night driver allowance past 10 PM.")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    business = relationship("Business", back_populates="pricing_configs")

class SelfImprovementProposal(Base):
    __tablename__ = "self_improvement_proposals"

    id = Column(String, primary_key=True, default=generate_uuid)
    proposal = Column(Text, nullable=False)
    expected_saving = Column(String, nullable=True)
    risk = Column(String, default="low")
    status = Column(String, default="PENDING_REVIEW")
    created_at = Column(DateTime, default=datetime.utcnow)

class EmergencyStopConfig(Base):
    __tablename__ = "emergency_stop_config"

    id = Column(String, primary_key=True, default="default_config")
    is_active = Column(Boolean, default=False)
    activated_by = Column(String, nullable=True)
    activated_at = Column(DateTime, nullable=True)
    reason = Column(String, nullable=True)
